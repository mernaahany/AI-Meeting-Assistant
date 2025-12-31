from pathlib import Path
from pdf_to_markdown import pdf_to_markdown
from indexing import index_documents
from config import DOCS_DIR, MARKDOWN_DIR, PARENT_STORE_PATH

def bootstrap_incremental():
    Path(MARKDOWN_DIR).mkdir(exist_ok=True)

    # Convert PDFs to Markdown incrementally
    for pdf_path in Path(DOCS_DIR).glob("*.pdf"):
        md_path = Path(MARKDOWN_DIR) / f"{pdf_path.stem}.md"
        if not md_path.exists():  # only convert new PDFs
            print(f"📄 Converting new PDF: {pdf_path.name}")
            pdf_to_markdown(str(pdf_path), MARKDOWN_DIR)
        else:
            print(f"✓ Markdown already exists: {md_path.name}")

    # Index documents after conversion (re-index all children)
    print("📚 Indexing documents into Qdrant...")
    index_documents()
