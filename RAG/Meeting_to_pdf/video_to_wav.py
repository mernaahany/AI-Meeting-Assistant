import subprocess
from datetime import datetime, timezone
import os
from pathlib import Path
from pymediainfo import MediaInfo

def get_file_date(file_path: str) -> str:
    media_info = MediaInfo.parse(file_path)
    for track in media_info.tracks:
        if track.track_type == "General":
            # 1. Get the raw date string from metadata
            raw_date = track.encoded_date or track.tagged_date or track.file_last_modification_date
            
            if raw_date:
                # 2. Clean the string (remove 'UTC ' if present)
                clean_date = str(raw_date).replace("UTC ", "").strip()
                
                try:
                    # 3. Parse the string into a naive datetime object
                    # Typical format: 2023-10-24 18:56:00
                    utc_dt = datetime.strptime(clean_date[:19], "%Y-%m-%d %H:%M:%S")
                    
                    # 4. Explicitly set it to UTC, then convert to Local Time
                    local_dt = utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)
                    
                    return local_dt.strftime("%Y-%m-%d %H:%M")
                except Exception as e:
                    print(f"Parsing error: {e}")
                    # If parsing fails, return the raw cleaned date as a fallback
                    return clean_date[:16]
    
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def convert_to_wav(input_path: str) -> str:
    base, _ = os.path.splitext(input_path)
    wav_path = f"{base}.wav"

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i", input_path,
            "-ac", "1",
            "-ar", "16000",
            "-vn",
            wav_path
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )

    return wav_path


