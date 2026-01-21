import torch
from config import DEVICE
from models import speaker_verification
from speaker_db import speaker_db


def extract_segment(waveform, start, end, sr):
    start_sample = int(start * sr)
    end_sample = int(end * sr)
    return waveform[:, start_sample:end_sample]


def identify_speaker(segment, sample_rate):
    min_duration_sec = 0.5
    if segment.shape[1] < int(min_duration_sec * sample_rate):
        return "Unknown", 0.0

    with torch.no_grad():
        emb = speaker_verification.encode_batch(segment.to(DEVICE))
        emb = emb.squeeze()

    best_speaker = "Unknown"
    best_score = 0.0

    for name, ref_emb in speaker_db.items():
        score = torch.nn.functional.cosine_similarity(
            emb, torch.tensor(ref_emb).to(emb.device), dim=0
        )
        if score > best_score:
            best_score = score
            best_speaker = name

    if best_score < 0.3:
        best_speaker = "Unknown"

    return best_speaker, float(best_score)
