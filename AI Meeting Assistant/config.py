import os

DOCS_DIR = r"Meeting_to_pdf\rag_knowledge_base"
MARKDOWN_DIR = "markdown"
PARENT_STORE_PATH = "parent_store"
CHILD_COLLECTION = "document_child_chunks"

os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(MARKDOWN_DIR, exist_ok=True)
os.makedirs(PARENT_STORE_PATH, exist_ok=True)
