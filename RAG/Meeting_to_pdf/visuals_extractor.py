from models import vision_model
import requests
import preprocessing
from config import API_KEY
def explain_frame_from_filtered(frame: dict) -> dict:
    """
    frame: one element from filtered_frames
    returns explanation + timestamp
    """

    b64 = frame["image"]  # already base64 encoded

    prompt = (
        """You are analyzing an image from a meeting video.

If the image shows a presentation slide, even if it is mostly visual,
describe its purpose and what it represents.

Visual slides used for introductions, branding, or context
ARE considered important content.

Explain the slide in 2–4 sentences.

"""
    )

    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": vision_model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64}"
                            },
                        },
                    ],
                }
            ],
            "max_tokens": 400,
            "temperature": 0.2,
        },
        timeout=120,
    )

    if r.status_code != 200:
        raise RuntimeError(f"{r.status_code} {r.text}")

    return {
        "timestamp": frame["timestamp"],
        "explanation": r.json()["choices"][0]["message"]["content"]
    }

def excution(meeting):
    summarization = []
    total_attendance = set()
    extracted_frames = preprocessing.extract_keyframes(meeting)
    filtered_frames = preprocessing.filter_similar_frames_multihash(extracted_frames, threshold=27)
    for frame in filtered_frames:
        vision_insight = explain_frame_from_filtered(frame)
        summarization.append(vision_insight["explanation"])
    return total_attendance, summarization  