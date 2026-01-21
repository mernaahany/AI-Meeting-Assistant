import warnings
warnings.filterwarnings("ignore")
import torch
from pyannote.audio import Pipeline
from transformers import pipeline as hf_pipeline
from speechbrain.inference import SpeakerRecognition
from speechbrain.utils.fetching import LocalStrategy
from huggingface_hub import InferenceClient
from config import *

print("Loading models...")

diarization_pipeline = Pipeline.from_pretrained(
    DIARIZATION_MODEL,
    token=HF_TOKEN
).to(torch.device(DEVICE))

asr_pipeline = hf_pipeline(
    task="automatic-speech-recognition",
    model=ASR_MODEL,
    ignore_warning=True,
    return_timestamps=True,
    device=0 if DEVICE == "cuda" else -1,
    generate_kwargs={"task": "transcribe", "language": "en"}
)

speaker_verification = SpeakerRecognition.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="pretrained_models/spkrec",
    local_strategy=LocalStrategy.COPY_SKIP_CACHE
)

llm_client = InferenceClient(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    token=HF_TOKEN
)
vision_model = "meta-llama/llama-3.2-11b-vision-instruct" 
print("✓ Models loaded")
