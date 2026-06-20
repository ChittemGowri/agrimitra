"""
scripts/build_vector_store.py
Run this ONCE (and again whenever you edit data/knowledge_base/*.txt)
to embed all knowledge base documents and save the vector index to
data/vector_store.json.

Usage:
    python scripts/build_vector_store.py
"""

import sys
from pathlib import Path

# Allow running this script directly from the scripts/ folder
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.retrieval_tool import SimpleVectorStore
from config import KB_DIR, GEMINI_API_KEY


def main():
    if not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY is not set. Add it to your .env file first.")
        sys.exit(1)

    txt_files = list(KB_DIR.glob("*.txt"))
    if not txt_files:
        print(f"ERROR: No .txt files found in {KB_DIR}")
        sys.exit(1)

    print(f"Found {len(txt_files)} knowledge base file(s) in {KB_DIR}")
    print("Embedding and building vector store... (this calls the Gemini API)")

    store = SimpleVectorStore()
    store.build_from_directory(KB_DIR)

    print(f"Done. Indexed {len(store.chunks)} chunks.")
    print(f"Saved to: {store.store_path}")


if __name__ == "__main__":
    main()
