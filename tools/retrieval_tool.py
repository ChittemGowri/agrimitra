"""
tools/retrieval_tool.py
RAG retrieval: embed the query using NVIDIA's embedding model,
then find the most relevant chunks from the pre-built vector store.

Vector store is built once by scripts/build_vector_store.py
and saved to data/vector_store.json.
"""

import json
import math
from pathlib import Path
from typing import List, Tuple

from openai import OpenAI

from config import (
    NVIDIA_API_KEY,
    NVIDIA_BASE_URL,
    EMBEDDING_MODEL,
    VECTOR_STORE_PATH,
    KB_DIR,
)


# ---------------------------------------------------------------------------
# Embedding helper
# ---------------------------------------------------------------------------

def _get_embedding(text: str) -> List[float]:
    """Call NVIDIA NIM embedding endpoint and return the vector."""
    client = OpenAI(base_url=NVIDIA_BASE_URL, api_key=NVIDIA_API_KEY)
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
        encoding_format="float",
    )
    return response.data[0].embedding


def _cosine(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


# ---------------------------------------------------------------------------
# Vector store loading
# ---------------------------------------------------------------------------

_STORE: List[dict] | None = None   # cached in-process


def _load_store() -> List[dict]:
    global _STORE
    if _STORE is not None:
        return _STORE
    if not VECTOR_STORE_PATH.exists():
        return []
    _STORE = json.loads(VECTOR_STORE_PATH.read_text())
    return _STORE


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def retrieve(query: str, top_k: int = 4) -> List[str]:
    """
    Return the top_k most relevant text chunks for the given query.
    Falls back to a simple keyword search if the vector store is empty
    (so the app works even before build_vector_store.py is run).
    """
    if not NVIDIA_API_KEY:
        return ["[RAG] NVIDIA_API_KEY not set — cannot retrieve documents."]

    store = _load_store()

    if not store:
        # Fallback: keyword scan of raw .txt files in the knowledge base
        return _keyword_fallback(query, top_k)

    query_vec = _get_embedding(query)
    scored: List[Tuple[float, str]] = []
    for item in store:
        score = _cosine(query_vec, item["embedding"])
        scored.append((score, item["text"]))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [text for _, text in scored[:top_k]]


def _keyword_fallback(query: str, top_k: int) -> List[str]:
    """Simple word-overlap search when no vector store exists yet."""
    keywords = set(query.lower().split())
    chunks: List[Tuple[int, str]] = []
    for txt_file in KB_DIR.glob("*.txt"):
        content = txt_file.read_text(errors="replace")
        paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 80]
        for para in paragraphs:
            hits = sum(1 for kw in keywords if kw in para.lower())
            if hits:
                chunks.append((hits, para))
    chunks.sort(key=lambda x: x[0], reverse=True)
    return [text for _, text in chunks[:top_k]] if chunks else [
        "No knowledge-base documents found. Run scripts/build_vector_store.py "
        "or add .txt files to data/knowledge_base/."
    ]
