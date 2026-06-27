"""
config.py
Central configuration for AgriMitra.
Reads secrets from environment variables (set via .env locally,
or Streamlit Secrets when deployed).

Backend: NVIDIA NIM API (OpenAI-compatible endpoint).
Get a free API key at https://build.nvidia.com/
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load variables from .env if present (local dev)
load_dotenv()

# ---- Paths ----
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
KB_DIR = DATA_DIR / "knowledge_base"
SAMPLE_IMG_DIR = DATA_DIR / "sample_images"
VECTOR_STORE_PATH = DATA_DIR / "vector_store.json"
MEMORY_STORE_PATH = DATA_DIR / "session_memory.json"

# ---- API Keys ----
# Get a free NVIDIA NIM API key at https://build.nvidia.com/
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")

# Optional: OpenWeatherMap free tier key (https://openweathermap.org/api)
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

# ---- NVIDIA NIM endpoint ----
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"

# ---- Model config ----
# Text + reasoning model  (supports function/tool calling)
TEXT_MODEL = "meta/llama-3.3-70b-instruct"

# Vision model  (multimodal: text + image)
VISION_MODEL = "nvidia/llama-3.2-90b-vision-instruct"

# Embedding model  (for RAG)
EMBEDDING_MODEL = "nvidia/llama-3.2-nv-embedqa-1b-v2"

# ---- App constants ----
APP_NAME = "AgriMitra"
DEFAULT_LOCATION = "Madanapalle, Andhra Pradesh"
DEFAULT_LAT = 13.5503
DEFAULT_LON = 78.5026
SUPPORTED_LANGUAGES = ["English", "Telugu"]

# Crops the Market Agent knows about (extend as you like)
TRACKED_CROPS = ["Tomato", "Groundnut", "Mango", "Tamarind", "Ragi"]
