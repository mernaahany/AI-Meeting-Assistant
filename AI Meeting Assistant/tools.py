from langchain_core.tools import tool
from vector_db import child_vector_store
from config import PARENT_STORE_PATH
import json, os, re
from llm_setup import llm
from typing import List



@tool
def search_child_chunks(query: str, k: int = 5) -> List[dict]:
    """
    Search for the top K most relevant child chunks.
    Supports optional file scoping when the user appends:
      - "in FILENAME.pdf", "in FILENAME", "from FILENAME.pdf", etc.
    Example: 'what is self_attention in attention_is_all_you_need pdf'
    """
    try:
        # Helper: extract file names and return cleaned query
        def parse_query_for_sources(q: str) -> (str, List[str]):
            # patterns like: in filename.pdf, in filename pdf, from filename, in "filename.pdf"
            # allow separators: and, comma
            lower_q = q.lower()

            # regex to capture sequences after ' in ' or ' from '
            # capture group: filenames possibly separated by 'and' or comma
            m = re.search(r'(?:\b(in|from)\b)\s+(.+)$', lower_q)
            if not m:
                return q, []

            after = m.group(2).strip()
            # strip trailing question marks or punctuation
            after = re.sub(r'[?.!]+$', '', after).strip()

            # split on " and " or "," or " ; "
            parts = re.split(r'\s+and\s+|,|;', after)
            sources = []
            for p in parts:
                # strip surrounding quotes and whitespace
                p = p.strip().strip('"').strip("'")
                # ensure .pdf extension normalized
                if p and not p.endswith(".pdf"):
                    # allow users to write 'pdf' as word, e.g., 'attention_is_all_you_need pdf'
                    # if last token is just 'pdf', maybe previous token is filename
                    tokens = p.split()
                    if tokens[-1] == "pdf" and len(tokens) >= 2:
                        filename = "_".join(tokens[:-1])
                        sources.append(filename + ".pdf")
                    else:
                        # try simple normalize (replace spaces with underscore)
                        sources.append(p.replace(" ", "_") + (".pdf" if not p.endswith(".pdf") else ""))
                else:
                    sources.append(p)
            # final cleanup: remove empty strings
            sources = [s for s in [src.strip() for src in sources] if s]
            # Build cleaned query: remove the 'in ...' clause from original (preserve case)
            cleaned = re.sub(r'(?i)(?:\bin\b|\bfrom\b)\s+(.+)$', '', query).strip()
            return cleaned, sources

        cleaned_query, requested_sources = parse_query_for_sources(query)

        # If no file requested, just do normal search
        if not requested_sources:
            results = child_vector_store.similarity_search(cleaned_query, k=k, score_threshold=0.7)
            return [
                {
                    "content": doc.page_content,
                    "parent_id": doc.metadata.get("parent_id", ""),
                    "source": doc.metadata.get("source", "")
                } for doc in results
            ]

        # If file(s) requested: perform larger search, then filter by metadata.source
        # Use a higher k to ensure we get enough candidate results to filter from
        search_k = max(k * 5, 20)
        candidates = child_vector_store.similarity_search(cleaned_query, k=search_k, score_threshold=0.0)

        # Normalize requested source names for comparison
        normalize = lambda s: s.lower().strip()
        req_norm = {normalize(s) for s in requested_sources}

        filtered = []
        for doc in candidates:
            src = doc.metadata.get("source", "")
            if not src:
                continue
            # normalize stored source (maybe stored as 'file.pdf' or 'file -> other' from merging)
            # take first token before '->' if merged metadata
            src_primary = src.split("->")[0].strip()
            src_primary_norm = normalize(src_primary)
            # match either exact filename or filename without extension
            if src_primary_norm in req_norm or src_primary_norm.replace(".pdf", "") in {r.replace(".pdf", "") for r in req_norm}:
                filtered.append({
                    "content": doc.page_content,
                    "parent_id": doc.metadata.get("parent_id", ""),
                    "source": src
                })
                # dedup by parent_id
        # deduplicate by parent_id preserving order
        seen = set()
        deduped = []
        for item in filtered:
            pid = item.get("parent_id") or item.get("source") or item["content"][:64]
            if pid not in seen:
                seen.add(pid)
                deduped.append(item)
                if len(deduped) >= k:
                    break

        # If nothing found after filtering, return empty list (agent can handle fallback)
        return deduped

    except Exception as e:
        print(f"Error searching child chunks: {e}")
        return []

    
@tool
def retrieve_parent_chunks(parent_ids: List[str]) -> List[dict]:
    """Retrieve full parent chunks by their IDs.

    Args:
        parent_ids: List of parent chunk IDs to retrieve
    """
    unique_ids = sorted(list(set(parent_ids)))
    results = []

    for parent_id in unique_ids:
        file_path = os.path.join(PARENT_STORE_PATH, parent_id if parent_id.lower().endswith(".json") else f"{parent_id}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    doc_dict = json.load(f)
                    results.append({
                        "content": doc_dict["page_content"],
                        "parent_id": parent_id,
                        "metadata": doc_dict["metadata"]
                    })
            except Exception as e:
                print(f"Error loading parent chunk {parent_id}: {e}")

    return results

# Bind tools to LLM
llm_with_tools = llm.bind_tools([search_child_chunks, retrieve_parent_chunks])