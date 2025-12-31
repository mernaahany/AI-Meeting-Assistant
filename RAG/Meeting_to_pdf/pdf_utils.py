import os
import re
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import inch
from config import PDF_DIR
import shutil 

def extract_summary_content(report_text):
    """
    Parses the AI-generated report to find the text between 
    'Summary:' and the next section header.
    """
    # Regex looks for "Summary:" and captures everything until it hits 
    # the next header "Key Discussion Points:"
    match = re.search(r"Summary:(.*?)(?=Key Discussion Points:)", report_text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return "No summary available."


def extract_meeting_title(text, fallback="Meeting_Report"):
    match = re.search(r"Meeting Title:\s*(.+)", text)
    if not match:
        return fallback

    title = re.sub(r'[\\/*?:"<>|]', "", match.group(1))
    return re.sub(r"\s+", "_", title)


RAG_PDF_STORAGE = "rag_knowledge_base"

def save_pdf(report_text, file_date=None):
    # 1. Extract and Clean Title

    for folder in [PDF_DIR, RAG_PDF_STORAGE]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    title = extract_meeting_title(report_text)
    
    # 1. Sanitize the date (Replace colons with dashes)
    clean_date = ""
    if file_date:
        clean_date = file_date.replace(":", "-").replace(" ", "_")
    
    # 2. Sanitize the title
    # Remove any character that isn't a letter, number, space, or dash
    safe_title = re.sub(r'[^\w\s-]', '', title).strip()
    safe_title = safe_title.replace(" ", "_")

    # 2. Construct Filename - FORCING the extension
    if file_date:
        filename = f"{clean_date}_{safe_title}.pdf"
    else:
        filename = f"{safe_title}.pdf"

    # 3. Ensure the Directory Exists
    if not os.path.exists(PDF_DIR):
        os.makedirs(PDF_DIR)

    path = os.path.join(PDF_DIR, filename)
    rag_path = os.path.join(RAG_PDF_STORAGE, filename)

    try:
        actual_summary = extract_summary_content(report_text)
        summary_path = path.replace(".pdf", ".txt")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(actual_summary)
    except Exception as e:
        print(f"Warning: Could not save summary text file: {e}")

    # 4. Initialize Document
    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    header_style = ParagraphStyle(
        "Header",
        parent=styles["Normal"],
        fontSize=12,
        fontName="Helvetica-Bold",
        spaceBefore=16,
        spaceAfter=8,
        alignment=TA_LEFT
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        spaceAfter=10,
        leading=14
    )

    story = []
    lines = report_text.split("\n")
    bullet_buffer = []

    def flush_bullets():
        if bullet_buffer:
            story.append(
                ListFlowable(
                    [ListItem(Paragraph(item, body_style), leftIndent=18) for item in bullet_buffer],
                    bulletType="bullet"
                )
            )
            bullet_buffer.clear() # Use clear() instead of reassignment to avoid nonlocal issues

    # 5. Build the Story
    for line in lines:
        line = line.strip()
        if not line:
            flush_bullets()
            story.append(Spacer(1, 0.15 * inch))
            continue

        if re.match(r"^(Meeting Title|Date|Participants|Summary|Key Discussion Points|Decisions Made|Action Items|Risks & Concerns|Next Meeting):", line):
            flush_bullets()
            header = line.replace(":", "")
            story.append(Paragraph(header, header_style))
            continue

        if line.startswith("-"):
            bullet_buffer.append(line[1:].strip())
            continue

        flush_bullets()
        story.append(Paragraph(line, body_style))

    flush_bullets()

    # 6. Build the PDF and Verify
    try:
        doc.build(story)
        if os.path.exists(path) and os.path.getsize(path) > 0:
            shutil.copy2(path, rag_path)
            print(f"[RAG] PDF saved to knowledge base: {rag_path}")
            return path
        else:
            print(f"Error: File {path} was created but is empty.")
            return None
    except Exception as e:
        print(f"Error building PDF: {str(e)}")
        return None