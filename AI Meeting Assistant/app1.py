import uuid
import os
import threading
import time
import traceback
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from fastapi.middleware.cors import CORSMiddleware
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from config import DOCS_DIR

# Import your custom RAG logic
from bootstrap import bootstrap_incremental
from graph import agent_graph

RAG_WATCH_PATH = DOCS_DIR

# =========================
# FASTAPI APP
# =========================
app = FastAPI(title="RAG API")

# CORS settings for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# BACKGROUND FILE WATCHER
# =========================
class RagUpdateHandler(FileSystemEventHandler):
    """Monitors folder for new PDFs and triggers re-indexing."""
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".pdf"):
            print(f"\n[EVENT] New meeting report detected: {os.path.basename(event.src_path)}")
            try:
                print("Updating knowledge base (indexing & chunking)...")
                bootstrap_incremental()
                print("[SUCCESS] RAG knowledge base updated.\n")
            except Exception as e:
                print(f"[ERROR] Auto-indexing failed: {e}")

def run_watcher():
    if not os.path.exists(RAG_WATCH_PATH):
        os.makedirs(RAG_WATCH_PATH, exist_ok=True)
        
    event_handler = RagUpdateHandler()
    observer = Observer()
    observer.schedule(event_handler, RAG_WATCH_PATH, recursive=False)
    observer.start()
    print(f"[*] Watcher started: Monitoring {RAG_WATCH_PATH}")
    try:
        while True:
            time.sleep(5) # Keep the thread alive
    except Exception as e:
        observer.stop()
    observer.join()

# Start the folder watcher in a background thread so it doesn't block FastAPI
watcher_thread = threading.Thread(target=run_watcher, daemon=True)
watcher_thread.start()

# =========================
# BOOTSTRAP RAG
# =========================
print("Starting bootstrap...")
bootstrap_incremental()
print("Bootstrap finished.")

# =========================
# THREAD HANDLING
# =========================
def create_thread_id():
    return {"configurable": {"thread_id": str(uuid.uuid4())}}

# Simple single-thread config
config = create_thread_id()

# =========================
# REQUEST / RESPONSE SCHEMA
# =========================
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str

# =========================
# API ENDPOINT
# =========================
@app.post("/rag/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    try:
        message = request.message.strip()
        if not message:
            return {"answer": "Please provide a message."}

        result = agent_graph.invoke({"messages": [HumanMessage(content=message)]}, config)

        answer = "No answer returned."
        msgs = result.get("messages", [])

        if msgs:
            last_msg = msgs[-1]
            
            # 1. Check if it's a standard LangChain Message object (AIMessage)
            if hasattr(last_msg, 'content'):
                content = last_msg.content
                # If content is a list (like in your example output)
                if isinstance(content, list) and len(content) > 0:
                    answer = content[0].get("text", str(content))
                else:
                    answer = content
            
            # 2. If it's a raw list of dictionaries (as seen in your snippet)
            elif isinstance(last_msg, list) and len(last_msg) > 0:
                answer = last_msg[0].get("text", str(last_msg))
                
            # 3. If it's a dictionary
            elif isinstance(last_msg, dict):
                answer = last_msg.get("text", str(last_msg))
            
            # 4. Fallback
            else:
                answer = str(last_msg)

        return {"answer": answer}

    except Exception as e:
        print("Error in /rag/chat:", e)
        traceback.print_exc() # Useful for debugging
        return {"answer": "Error: failed to generate a response from RAG."}



# =========================
# OPTIONAL: Health check
# =========================
@app.get("/health")
def health_check():
    return {
        "status": "ok", 
        "watching_directory": RAG_WATCH_PATH
    }
