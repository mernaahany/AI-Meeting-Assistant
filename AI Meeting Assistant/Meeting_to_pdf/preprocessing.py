import librosa, soundfile as sf, noisereduce as nr
import numpy as np, os, torch
from scipy.signal import butter, lfilter
from config import TARGET_SR
import cv2
import base64
import imagehash
from PIL import Image 
from io import BytesIO
import scenedetect as sd

def bandpass_filter(audio, sr, low=80, high=7500):
    b, a = butter(4, [low/(sr/2), high/(sr/2)], btype="band")
    return lfilter(b, a, audio)

def apply_vad(audio, sr):
    model, utils = torch.hub.load("snakers4/silero-vad", "silero_vad")
    get_speech_timestamps = utils[0]
    speech = []
    for seg in get_speech_timestamps(audio, model, sampling_rate=sr):
        speech.append(audio[seg["start"]:seg["end"]])
    return np.concatenate(speech) if speech else audio

def preprocess_audio(input_wav, output_dir, suffix, override_name=None):
    os.makedirs(output_dir, exist_ok=True)

    # 1. Determine the base name: Use override_name if provided, otherwise use original filename
    if override_name:
        base_name = override_name
    else:
        base_name = os.path.splitext(os.path.basename(input_wav))[0]

    # 2. Construct the final output path with the suffix
    # If suffix is "_Record", filename becomes "John Doe_Record.wav"
    out_filename = f"{base_name}.wav"
    out_path = os.path.join(output_dir, out_filename)

    audio, sr = librosa.load(input_wav, sr=TARGET_SR, mono=True)
    audio = librosa.util.normalize(audio)
    audio = nr.reduce_noise(audio, sr)
    audio = bandpass_filter(audio, sr)
    audio = apply_vad(audio, sr)
    audio = librosa.util.normalize(audio)

    sf.write(out_path, audio, sr)
    return out_path

# helper functions of extract frames

def encode_frame(frame_rgb):
    pil = Image.fromarray(frame_rgb)
    buf = BytesIO()
    pil.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode()

def decode_image(base64_string):
    data = base64.b64decode(base64_string)
    return Image.open(BytesIO(data))

def extract_keyframes(video_path, threshold=15.0):
    video = sd.open_video(video_path)
    manager = sd.SceneManager()
    manager.add_detector(sd.ContentDetector(threshold=threshold))
    manager.detect_scenes(video)

    scenes = manager.get_scene_list()
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    frames = []

    for start, end in scenes:
        mid = (start.frame_num + end.frame_num) // 2
        cap.set(cv2.CAP_PROP_POS_FRAMES, mid)
        ret, frame = cap.read()
        if not ret:
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ts = mid / fps
        m, s = divmod(ts, 60)

        frames.append({
            "timestamp": f"{int(m):02d}:{int(s):02d}",
            "frame_np": frame_rgb,
            "image": encode_frame(frame_rgb)
        })

    cap.release()
    return frames

# Hash similarity for filteration

def multi_hash(frame_np):
    img = Image.fromarray(frame_np)
    return {
        "ph": imagehash.phash(img),
        "dh": imagehash.dhash(img),
        "ah": imagehash.average_hash(img),
    }

def hash_distance(h1, h2):
    return (
        (h1["ph"] - h2["ph"]) * 0.5 +
        (h1["dh"] - h2["dh"]) * 0.3 +
        (h1["ah"] - h2["ah"]) * 0.2
    )

def filter_similar_frames_multihash(frames, threshold=20):
    filtered = []
    last_hash = None

    for f in frames:
        h = multi_hash(f["frame_np"])

        if last_hash is None:
            filtered.append(f)
            last_hash = h
            continue

        dist = hash_distance(h, last_hash)

        if dist > threshold:
            filtered.append(f)
            last_hash = h

    return filtered

def remove_safe(explanations):
    return [
        e for e in explanations
        if isinstance(e, str) and e.strip().lower() != "safe"
    ]

def format_explanations(explanations):
    return "\n".join(f"- {exp}" for exp in explanations)
def format_attendance(attendance):
    return "\n".join(f"- {name}" for name in attendance)

def build_transcription(transcript, attendance, explanations):
    attendance_text = format_attendance(attendance)
    explanations_text = format_explanations(explanations)

    full_transcription = f"""
[ATTENDANCE]
{attendance_text}

[VISUAL EXPLANATIONS FROM FRAMES]
{explanations_text}

[MEETING TRANSCRIPT]
{transcript}
""".strip()

    return full_transcription

