"""
utils/memory.py
Persistent, file-backed memory store for farmer profiles and conversation history.
Each session_id gets its own slot in a JSON file.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from config import MEMORY_STORE_PATH


def _load_store() -> Dict[str, Any]:
    if MEMORY_STORE_PATH.exists():
        try:
            return json.loads(MEMORY_STORE_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_store(store: Dict[str, Any]) -> None:
    MEMORY_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_STORE_PATH.write_text(json.dumps(store, indent=2, ensure_ascii=False))


def get_memory(session_id: str) -> Dict[str, Any]:
    """Return the memory dict for a session (creates empty profile if new)."""
    store = _load_store()
    return store.get(session_id, {
        "crop": None,
        "location": None,
        "history": [],          # list of {"role": str, "content": str}
        "last_diagnosis": None,
    })


def save_memory(session_id: str, memory: Dict[str, Any]) -> None:
    """Persist the memory dict for a session."""
    store = _load_store()
    store[session_id] = memory
    _save_store(store)


def append_turn(session_id: str, role: str, content: str) -> None:
    """Append one conversation turn and re-persist."""
    mem = get_memory(session_id)
    mem["history"].append({"role": role, "content": content})
    # Keep only the last 10 turns to avoid prompt bloat
    mem["history"] = mem["history"][-10:]
    save_memory(session_id, mem)


def get_history_text(session_id: str) -> str:
    """Return the last few turns as a readable string for prompt injection."""
    mem = get_memory(session_id)
    lines: List[str] = []
    for turn in mem["history"][-6:]:
        prefix = "Farmer" if turn["role"] == "user" else "AgriMitra"
        lines.append(f"{prefix}: {turn['content']}")
    return "\n".join(lines) if lines else "(no previous conversation)"
