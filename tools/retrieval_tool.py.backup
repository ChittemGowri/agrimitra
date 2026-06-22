"""
tools/retrieval_tool.py
A small but REAL Retrieval-Augmented Generation (RAG) pipeline.

Why not a "real" vector DB (FAISS/Chroma/Pinecone)?
For a 5-10 document knowledge base, a plain Python list of embeddings
+ cosine similarity is just as correct and removes a heavy dependency
that often breaks deployment on free hosting tiers. The retrieval
LOGIC is the same one you'd use at any scale -- swap `SimpleVectorStore`
for a real vector DB later without touching the agent layer.

Build the index once with: python scripts/build_vector_store.py
"""

import json
import math
from pathlib import Path

from google import genai

from config import GEMINI_API_KEY, EMBEDDING_MODEL, KB_DIR, VECTOR_STORE_PATH

_client = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def _embed_text(text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
    client = _get_client()
    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config={"task_type": task_type},
    )
    return result.embeddings[0].values


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class SimpleVectorStore:
    def __init__(self, store_path: Path = VECTOR_STORE_PATH):
        self.store_path = store_path
        self.chunks: list[dict] = []

    def build_from_directory(self, kb_dir: Path = KB_DIR, chunk_size: int = 600) -> None:
        """Read every .txt file in kb_dir, chunk it, embed each chunk, save to disk."""
        self.chunks = []
        for file_path in sorted(kb_dir.glob("*.txt")):
            text = file_path.read_text(encoding="utf-8")
            for i in range(0, len(text), chunk_size):
                chunk_text = text[i:i + chunk_size].strip()
                if len(chunk_text) < 30:
                    continue
                embedding = _embed_text(chunk_text)
                self.chunks.append({
                    "source": file_path.name,
                    "text": chunk_text,
                    "embedding": embedding,
                })
        self.save()

    def save(self) -> None:
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        self.store_path.write_text(json.dumps(self.chunks))

    def load(self) -> bool:
        if not self.store_path.exists():
            return False
        self.chunks = json.loads(self.store_path.read_text())
        return True

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        if not self.chunks:
            loaded = self.load()
            if not loaded:
                return []
        query_embedding = _embed_text(query, task_type="RETRIEVAL_QUERY")
        scored = [
            {**chunk, "score": _cosine_similarity(query_embedding, chunk["embedding"])}
            for chunk in self.chunks
        ]
        scored.sort(key=lambda c: c["score"], reverse=True)
        return scored[:top_k]


_store = SimpleVectorStore()


def retrieve_agri_knowledge(query: str) -> dict:
    """
    Search the local agricultural knowledge base (disease management
    guides, IPM principles) for passages relevant to a farmer's question.

    Args:
        query: A natural-language question or topic, e.g.
               "how to treat tomato leaf curl virus".

    Returns:
        dict with the most relevant knowledge base passages and sources.
    """
    results = _store.search(query, top_k=3)
    if not results:
        return {
            "status": "error",
            "message": "Knowledge base not built yet. Run "
                       "'python scripts/build_vector_store.py' first.",
        }
    return {
        "status": "success",
        "results": [
            {"source": r["source"], "text": r["text"], "relevance": round(r["score"], 3)}
            for r in results
        ],
    }
