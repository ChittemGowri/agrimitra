import os
from pathlib import Path

# Load .env for local development.
# On Streamlit Cloud dotenv is unnecessary — secrets come via st.secrets.
# We silently skip if the package isn't installed.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    pass

# ---- Paths ----
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
KB_DIR = DATA_DIR / "knowledge_base"
SAMPLE_IMG_DIR = DATA_DIR / "sample_images"
VECTOR_STORE_PATH = DATA_DIR / "vector_store.json"
MEMORY_STORE_PATH = DATA_DIR / "session_memory.json"


# ---- Secret resolution ----
# Priority: Streamlit Secrets (cloud) → os.environ (.env / system)
def _get_secret(key: str) -> str:
    """Read a secret from Streamlit Secrets (cloud) or os.environ (local)."""
    try:
        import streamlit as st
        return st.secrets.get(key, os.getenv(key, ""))
    except Exception:
        return os.getenv(key, "")


# ---- API Keys ----
NVIDIA_API_KEY = _get_secret("NVIDIA_API_KEY")
OPENWEATHER_API_KEY = _get_secret("OPENWEATHER_API_KEY")

# ---- NVIDIA NIM endpoint ----
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"

# ---- Model config ----
TEXT_MODEL = "meta/llama-3.3-70b-instruct"
VISION_MODEL = "nvidia/llama-3.2-90b-vision-instruct"
EMBEDDING_MODEL = "nvidia/llama-3.2-nv-embedqa-1b-v2"

# ---- App constants ----
APP_NAME = "AgriMitra"
DEFAULT_LOCATION = "Madanapalle, Andhra Pradesh"
DEFAULT_LAT = 13.5503
DEFAULT_LON = 78.5026
SUPPORTED_LANGUAGES = ["English", "Telugu"]

TRACKED_CROPS = ["Tomato", "Groundnut", "Mango", "Tamarind", "Ragi"]
