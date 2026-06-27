"""
scripts/build_vector_store.py
Run ONCE before using the Advisory Agent's RAG feature.

Reads every .txt file in data/knowledge_base/,
splits into ~500-character paragraphs,
embeds each chunk using NVIDIA's embedding model via NIM,
and saves the vector store to data/vector_store.json.

Usage:
    cd agrimitra
    python scripts/build_vector_store.py
"""

import json
import sys
import time
from pathlib import Path

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from openai import OpenAI
from config import NVIDIA_API_KEY, NVIDIA_BASE_URL, EMBEDDING_MODEL, KB_DIR, VECTOR_STORE_PATH


def chunk_text(text: str, max_chars: int = 500) -> list[str]:
    """Split text into overlapping paragraphs of at most max_chars characters."""
    paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 60]
    chunks = []
    for para in paragraphs:
        if len(para) <= max_chars:
            chunks.append(para)
        else:
            # Hard-split long paragraphs
            for i in range(0, len(para), max_chars - 50):
                chunk = para[i:i + max_chars].strip()
                if chunk:
                    chunks.append(chunk)
    return chunks


def embed_chunks(client: OpenAI, chunks: list[str]) -> list[list[float]]:
    """Embed a list of text chunks, returning a list of embedding vectors."""
    embeddings = []
    for i, chunk in enumerate(chunks):
        print(f"  Embedding chunk {i + 1}/{len(chunks)} ({len(chunk)} chars)…", end="\r")
        try:
            response = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=chunk,
                encoding_format="float",
            )
            embeddings.append(response.data[0].embedding)
            time.sleep(0.1)   # polite rate-limit buffer
        except Exception as e:
            print(f"\n  ⚠️  Error embedding chunk {i + 1}: {e}")
            embeddings.append([0.0] * 1024)   # zero vector as placeholder
    print()
    return embeddings


def main() -> None:
    if not NVIDIA_API_KEY:
        print("❌ NVIDIA_API_KEY is not set. Add it to your .env file.")
        sys.exit(1)

    txt_files = list(KB_DIR.glob("*.txt"))
    if not txt_files:
        print(f"❌ No .txt files found in {KB_DIR}. Add agricultural extension guides there first.")
        sys.exit(1)

    print(f"📂 Found {len(txt_files)} knowledge-base file(s) in {KB_DIR}")
    client = OpenAI(base_url=NVIDIA_BASE_URL, api_key=NVIDIA_API_KEY)

    store = []
    for txt_file in sorted(txt_files):
        print(f"\n📄 Processing: {txt_file.name}")
        text = txt_file.read_text(errors="replace")
        chunks = chunk_text(text)
        print(f"  Split into {len(chunks)} chunks")
        vecs = embed_chunks(client, chunks)
        for chunk, vec in zip(chunks, vecs):
            store.append({"source": txt_file.name, "text": chunk, "embedding": vec})

    VECTOR_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    VECTOR_STORE_PATH.write_text(json.dumps(store, ensure_ascii=False))
    print(f"\n✅ Vector store saved → {VECTOR_STORE_PATH}")
    print(f"   Total chunks: {len(store)}")


if __name__ == "__main__":
    main()
