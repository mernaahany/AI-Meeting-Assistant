from models import llm_client
from preprocessing import build_transcription

# def generate_report(points):
#     prompt = f"""
# You are a meeting report generator AI.

# Using the following extracted points:

# {points}

# Create a professional structured meeting report using this format:

# Meeting Title:
# Date:
# Participants:

# Summary:

# Key Discussion Points:
# - …

# Decisions Made:
# - …

# Action Items:
# - Person:
#   Task:
#   Deadline:

# Risks & Concerns:
# - …

# Next Meeting:
# - Date:
# """

#     response = llm_client.chat.completions.create(
#         messages=[{"role": "user", "content": prompt}],
#         max_tokens=600,
#         temperature=0.3
#     )

#     return response.choices[0].message["content"]

def generate_report(transcript, attendance, explanations):
    full_transcription = build_transcription(
        transcript=transcript,
        attendance=attendance,
        explanations=explanations
    )
    prompt = f"""
You are a meeting report generator AI.

The following text is the complete meeting record.
It may include:
- Participants
- Spoken transcript
- Visual explanations extracted from shared-screen frames (e.g., slide text, logos, titles, images)

Use ONLY the information explicitly present in the provided content.
Do NOT guess, infer, or invent any names, organizations, dates, locations, or topics.
If information is missing, leave the field empty or write "Not specified".

{full_transcription}

Generate a professional, structured meeting report using the exact format below.

Meeting Title:
Date:
Participants:

Summary:

Visual Insights from Frames:
- Clearly list only the information that was visible in shared screens or frames.
- Include slide titles, organization names, logos, locations, themes, or visual evidence.
- Do NOT repeat spoken content unless it was also visible in the frames.
- If no visual information is present, write "No visual insights identified".

Key Discussion Points:
- …

Decisions Made:
- …

Action Items:
- Person:
  Task:
  Deadline:

Risks & Concerns:
- …

Next Meeting:
- Date:
"""

    response = llm_client.chat.completions.create(
        #model="mistralai/Mistral-7B-Instruct-v0.2:featherless-ai",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600,
        temperature=0.3
    )

    return response.choices[0].message["content"]


