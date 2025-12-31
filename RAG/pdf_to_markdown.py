import os, glob
from pathlib import Path
import pymupdf
import pymupdf4llm
from config import MARKDOWN_DIR

os.environ["TOKENIZERS_PARALLELISM"] = "false"

def pdf_to_markdown(pdf_path, output_dir):
    doc = pymupdf.open(pdf_path)
    md = pymupdf4llm.to_markdown(
        doc,
        write_images=False
    )
    md_cleaned = md.encode("utf-8", errors="ignore").decode("utf-8")
    out = Path(output_dir) / f"{Path(doc.name).stem}.md"
    out.write_text(md_cleaned, encoding="utf-8")

def pdfs_to_markdowns():
    Path(MARKDOWN_DIR).mkdir(exist_ok=True)
    for pdf in glob.glob("./docs/*.pdf"):
        pdf_to_markdown(pdf, MARKDOWN_DIR)
