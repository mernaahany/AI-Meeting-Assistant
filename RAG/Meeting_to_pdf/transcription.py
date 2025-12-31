import torchaudio
from config import TARGET_SR
from models import diarization_pipeline, asr_pipeline
from speaker_identification import extract_segment, identify_speaker


def generate_transcription(audio_path, file_date=None):
    waveform, sr = torchaudio.load(audio_path)

    if sr != TARGET_SR:
        waveform = torchaudio.functional.resample(waveform, sr, TARGET_SR)
        sr = TARGET_SR

    diarization = diarization_pipeline({
        "waveform": waveform,
        "sample_rate": sr
    })

    transcript = []

    if file_date:
        transcript.append(f"Recording Date: {file_date}\n")

    for turn, _, _ in diarization.speaker_diarization.itertracks(yield_label=True):
        segment = extract_segment(waveform, turn.start, turn.end, sr)
        speaker, _ = identify_speaker(segment, sr)

        text = asr_pipeline(
            segment[0].cpu().numpy(),
            chunk_length_s=0
        )["text"].strip()

        transcript.append(f"{speaker}:\n{text}\n")

    return "\n".join(transcript)
