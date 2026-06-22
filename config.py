"""
config.py
Central configuration for AgriMitra.
Reads secrets from environment variables (set via .env locally,
or Streamlit Secrets when deployed).
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
# Get a free NVIDIA API key at https://build.nvidia.com/
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")

# Optional: OpenWeatherMap free tier key (https://openweathermap.org/api)
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
# Optional: Base URL for NVIDIA NIM API (if different from default)
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "")

# ---- Model config ----
# Using NVIDIA models via NVIDIA NIM or similar service
# nemotron-3-8b-instruct: capable text model for reasoning
# nemotron-3-8b-vision-alpha: vision model for image understanding (hypothetical name, adjust as needed)
# nv-embed-v1: NVIDIA's embedding model
TEXT_MODEL = "nemotron-3-8b-instruct"
VISION_MODEL = "nemotron-3-8b-vision-alpha"  # Adjust based on actual NVIDIA vision model availability
EMBEDDING_MODEL = "nv-embed-v1"


# ---- App constants ----
APP_NAME = "AgriMitra"
DEFAULT_LOCATION = "Madanapalle, Andhra Pradesh"
DEFAULT_LAT = 13.5503
DEFAULT_LON = 78.5026
SUPPORTED_LANGUAGES = ["English", "Telugu"]

# Crops the Market Agent knows about (extend as you like)
TRACKED_CROPS = ["Tomato", "Groundnut", "Mango", "Tamarind", "Ragi"]
