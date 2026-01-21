import os
import numpy as np
import torch
import torchaudio

from config import DB_PATH, ENROLL_DIR, DEVICE
from preprocessing import preprocess_audio
from models import speaker_verification

# =========================
# LOAD / INIT SPEAKER DB
# =========================
if os.path.exists(DB_PATH):
    speaker_db = np.load(DB_PATH, allow_pickle=True).item()
else:
    speaker_db = {}

# =========================
# EMBEDDING EXTRACTION
# =========================
def extract_embedding(wav_path):
    waveform, sr = torchaudio.load(wav_path)

    # Convert to mono
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)

    # Resample if needed
    if sr != 16000:
        waveform = torchaudio.functional.resample(
            waveform, sr, 16000
        )

    with torch.no_grad():
        emb = speaker_verification.encode_batch(
            waveform.to(DEVICE)
        )

    return emb.squeeze().cpu().numpy()

# =========================
# ADD SPEAKER (UNCHANGED)
# =========================
def add_speaker(audio_path, custom_name=None):
    """
    Original behavior:
    - Speaker name = filename
    - Preprocess internally
    - Extract embedding
    - Save to speaker_database.npy
    """
    global speaker_db

    speaker_name = custom_name if custom_name else os.path.splitext(
        os.path.basename(audio_path)
    )[0]

    processed_path = preprocess_audio(
        input_wav=audio_path,
        output_dir=ENROLL_DIR,
        suffix="_Record",
        override_name=speaker_name
    )

    embedding = extract_embedding(processed_path)

    speaker_db[speaker_name] = embedding
    np.save(DB_PATH, speaker_db)

    print(f"[✓] Speaker '{speaker_name}' added")

    return speaker_name

def remove_speaker(speaker_name):
    """
    Removes the speaker's embedding from the global dictionary 
    and updates the .npy file on disk.
    """
    global speaker_db

    if speaker_name in speaker_db:
        # 1. Remove from the active dictionary in memory
        del speaker_db[speaker_name]
        
        # 2. Save the updated dictionary back to the .npy file
        np.save(DB_PATH, speaker_db)
        print(f"[x] Speaker '{speaker_name}' removed from AI database")
        return True
    
    print(f"[!] Speaker '{speaker_name}' not found in AI database")
    return False

