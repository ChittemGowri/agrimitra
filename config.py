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
# Get a free Gemini key at https://aistudio.google.com/app/apikey
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Optional: OpenWeatherMap free tier key (https://openweathermap.org/api)
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

# ---- Model config ----
# gemini-2.5-flash: fast, cheap, multimodal (vision + text), good for an agent loop
TEXT_MODEL = "gemini-2.5-flash"
VISION_MODEL = "gemini-2.5-flash"
EMBEDDING_MODEL = "text-embedding-004"

# ---- App constants ----
APP_NAME = "AgriMitra"
DEFAULT_LOCATION = "Madanapalle, Andhra Pradesh"
DEFAULT_LAT = 13.5503
DEFAULT_LON = 78.5026
SUPPORTED_LANGUAGES = ["English", "Telugu"]

# Crops the Market Agent knows about (extend as you like)
TRACKED_CROPS = ["Tomato", "Groundnut", "Mango", "Tamarind", "Ragi"]
