import os
import torch

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "speaker_database.npy")
ENROLL_DIR = os.path.join(BASE_DIR, "processed_audio_enrollment")
TEST_DIR = os.path.join(BASE_DIR, "processed_audio_test")
PDF_DIR = os.path.join(BASE_DIR, "docs")

os.makedirs(ENROLL_DIR, exist_ok=True)
os.makedirs(TEST_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

HF_TOKEN = "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"
API_KEY= "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"

DIARIZATION_MODEL = "pyannote/speaker-diarization-3.1"
ASR_MODEL = "openai/whisper-small"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
TARGET_SR = 16000
