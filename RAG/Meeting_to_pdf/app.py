import warnings
warnings.filterwarnings("ignore")
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil, os
from datetime import datetime
import re
from fastapi import UploadFile, File, Form
import json
from visuals_extractor import excution



from speaker_db import add_speaker, remove_speaker
from preprocessing import preprocess_audio
from transcription import generate_transcription
from report_generator import generate_report
from pdf_utils import save_pdf, extract_summary_content
from config import TEST_DIR, ENROLL_DIR, PDF_DIR
from video_to_wav import convert_to_wav, get_file_date
from n8n import upload_to_n8n



app = FastAPI(title="Meeting Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/enroll-speaker/")
async def enroll_speaker(
    file: UploadFile = File(...), 
    speaker_name: str = Form(...),
    department: str = Form(...)
):

    try:
        # 1. Clean ONLY illegal characters (keep spaces)
        safe_name = re.sub(r'[\\/*?:"<>|]', "", speaker_name).strip()
        
        # Ensure enrollment directory exists
        if not os.path.exists(ENROLL_DIR):
            os.makedirs(ENROLL_DIR, exist_ok=True)
            
        # 2. Save the RAW file temporarily for processing
        temp_filename = f"temp_{file.filename}"
        temp_path = os.path.join(ENROLL_DIR, temp_filename)
        
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 3. Process Audio & Extract Embeddings
        # This calls your preprocessing logic and saves the final .wav
        final_speaker_name = add_speaker(temp_path, custom_name=safe_name)

        # 4. SAVE METADATA (The "Sidecar" JSON file)
        # This links the speaker name to their department on disk
        meta_path = os.path.join(ENROLL_DIR, f"{final_speaker_name}.json")
        metadata = {
            "name": final_speaker_name,
            "department": department,
            "enrolled_at": str(os.path.getctime(temp_path)) # Optional: timestamp
        }
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=4)

        # 5. Cleanup the temporary raw upload
        if os.path.exists(temp_path):
            os.remove(temp_path)     

        # 6. Return status 'trained' to satisfy the Frontend UI logic
        return {
            "status": "trained", 
            "speaker": final_speaker_name,
            "department": department
        }

    except Exception as e:
        print(f"Enrollment Error: {str(e)}")
        # If something fails, try to clean up temp file
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-meeting/")
async def process_meeting(file: UploadFile = File(...)):
    temp_path = f"{file.filename}"

    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    file_date = get_file_date(temp_path)


        # Convert video → WAV (if video)
    if temp_path.lower().endswith((".mp4", ".mkv", ".avi", ".mov", ".webm")):
        audio_path = convert_to_wav(temp_path)
    else:
        audio_path = temp_path  # already audio

    processed = preprocess_audio(
        input_wav=temp_path,
        output_dir=TEST_DIR,
        suffix="_meeting"
    )

    transcript = generate_transcription(audio_path=processed, file_date=file_date)
    attendance, explanation = excution(temp_path)
    report = generate_report(transcript,attendance,explanation)

    actual_summary = extract_summary_content(report)


    pdf_path = save_pdf(report, file_date=file_date)

    if os.path.exists(pdf_path):
        upload_to_n8n(pdf_path)
    else:
        print("PDF output file not found. Did the previous steps finish successfully?")
    

    os.remove(temp_path)
    if audio_path != temp_path:
        os.remove(audio_path)

    return {
        "transcript": transcript,
        "report": report,
        "pdf_path": pdf_path,
        "summary": actual_summary,
    }

@app.get("/dashboard-stats")
async def get_dashboard_stats():
    # 1. Count Voice Profiles
    # Filter to only count .wav files so the .json sidecars don't double the count
    voice_profiles_count = 0
    if os.path.exists(ENROLL_DIR):
        voice_profiles_count = len([
            name for name in os.listdir(ENROLL_DIR) 
            if name.endswith(".wav")
        ])

    # 2. Count Total Meetings (files in your TEST_DIR)
    total_meetings = 0
    recent_meetings = []
    if os.path.exists(TEST_DIR):
        # We also filter for audio files here to avoid counting temp files or hidden OS files
        files = [f for f in os.listdir(TEST_DIR) if os.path.isfile(os.path.join(TEST_DIR, f)) and f.endswith((".wav", ".mp3"))]
        total_meetings = len(files)
        
        # 3. Get Recent Meetings (Last 5 files based on modification time)
        files_with_time = [
            {
                "id": f,
                "title": f,
                "status": "completed",
                "date": os.path.getmtime(os.path.join(TEST_DIR, f))
            } for f in files
        ]
        # Sort by date descending
        recent_meetings = sorted(files_with_time, key=lambda x: x['date'], reverse=True)[:5]

    return {
        "totalMeetings": total_meetings,
        "voiceProfiles": voice_profiles_count,
        "hoursSaved": total_meetings * 1,   # Simulated logic (1hr per meeting)
        "recentMeetings": recent_meetings
    }

@app.get("/list-speakers")
async def list_speakers():
    profiles = []
    
    if os.path.exists(ENROLL_DIR):
        # Iterate through the enrollment directory
        for filename in os.listdir(ENROLL_DIR):
            # Only process .wav files
            if filename.endswith(".wav"):
                # "John Doe.wav" -> "John Doe"
                name = filename.replace(".wav", "")
                
                # Default values
                department = "General"
                
                # Look for a sidecar JSON file (e.g., "John Doe.json")
                json_path = os.path.join(ENROLL_DIR, f"{name}.json")
                
                if os.path.exists(json_path):
                    try:
                        with open(json_path, "r") as f:
                            metadata = json.load(f)
                            # Pull the department saved during enrollment
                            department = metadata.get("department", "General")
                    except Exception as e:
                        print(f"Error reading metadata for {name}: {e}")
                
                profiles.append({
                    "id": name,         # Using name as ID
                    "name": name,
                    "department": department,
                    "status": "trained" # Since the .wav exists on disk
                })
                
    return profiles



@app.delete("/delete-speaker/{speaker_name}")
async def delete_speaker(speaker_name: str):
    # 1. Clean the name to match the file system and dictionary keys
    safe_name = re.sub(r'[\\/*?:"<>|]', "", speaker_name).strip()
    
    # Define paths for the files on disk
    wav_path = os.path.join(ENROLL_DIR, f"{safe_name}.wav")
    json_path = os.path.join(ENROLL_DIR, f"{safe_name}.json")
    
    try:
        # 2. Check if the speaker exists on disk
        # We check the wav file as the primary indicator of existence
        if not os.path.exists(wav_path):
            raise HTTPException(
                status_code=404, 
                detail=f"Speaker '{speaker_name}' profile not found on disk."
            )

        # 3. Remove the physical files
        try:
            os.remove(wav_path)
            if os.path.exists(json_path):
                os.remove(json_path)
        except OSError as e:
            # Handle cases where file might be locked or permission denied
            raise HTTPException(
                status_code=500, 
                detail=f"Error deleting files for {safe_name}: {str(e)}"
            )

        # 4. Remove from AI Embedding Database (.npy and global dict)
        # This calls the function you added to your database management file
        db_removed = remove_speaker(safe_name)

        if not db_removed:
            print(f"Warning: Files deleted, but {safe_name} wasn't in the embedding dictionary.")

        return {
            "status": "ok", 
            "message": f"Successfully purged {speaker_name} from files and AI memory."
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Delete Error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal Server Error during deletion: {str(e)}"
        )


# Path where your meeting PDFs are stored
MEETINGS_DIR = PDF_DIR

@app.get("/list-meetings")
async def list_meetings():
    meetings = []
    if not os.path.exists(MEETINGS_DIR):
        os.makedirs(MEETINGS_DIR)
        return []
        
    for filename in os.listdir(MEETINGS_DIR):
        # Only process valid PDF files and ignore those 0 KB "ghost" files
        if filename.endswith(".pdf") and os.path.getsize(os.path.join(MEETINGS_DIR, filename)) > 0:
            file_path = os.path.join(MEETINGS_DIR, filename)
            
            # 1. Split filename to separate the sanitized date from the title
            # Expected format: "2025-12-22_20-56_Meeting_Title.pdf"
            parts = filename.split("_", 1)
            
            # Default fallback using file metadata
            file_stats = os.stat(file_path)
            fallback_date = datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d')
            
            if len(parts) > 1:
                # The first part is the date. We'll show the sanitized version (with dashes)
                # to the frontend to ensure it remains a valid string for Javascript.
                extracted_date = parts[0] 
                # Clean up the title for display
                raw_title = parts[1].replace(".pdf", "").replace("_", " ")
            else:
                extracted_date = fallback_date
                raw_title = filename.replace(".pdf", "").replace("_", " ")


            summary_txt_path = file_path.replace(".pdf", ".txt")
            if os.path.exists(summary_txt_path):
                with open(summary_txt_path, "r", encoding="utf-8") as f:
                    summary_content = f.read()
            else:
                summary_content = f"Download the report to get the meeting details."


            meetings.append({
                "id": filename,
                "title": raw_title,
                "date": extracted_date, 
                "duration": "N/A", 
                "attendees": ["Showed in the report"],
                "status": "completed",
                "summary": summary_content,
                "actionItems": []
            })
                
    # Sort by date descending so the newest meetings appear first
    meetings.sort(key=lambda x: x["date"], reverse=True)
    return meetings


@app.get("/download-pdf/{filename}")
async def download_pdf(filename: str):
    file_path = os.path.join(MEETINGS_DIR, filename)
    
    # Safety check: Ensure the file exists and isn't a 0 KB corrupted file
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return FileResponse(
            file_path, 
            media_type='application/pdf',
            filename=filename # This ensures the browser downloads it with the right name
        )
    
    # Return a proper 404 error instead of just a dictionary
    raise HTTPException(status_code=404, detail="Meeting PDF not found or is corrupted.")