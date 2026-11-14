import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "").strip()
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "").strip()
VOICE_LANGUAGE = os.getenv("VOICE_LANGUAGE", "pt").strip()
TARGET_LUFS = int(os.getenv("TARGET_LUFS", "-14"))

BROLL_CACHE_DIR = BASE_DIR / "assets" / "broll_cache"
OUTPUT_DIR = BASE_DIR / "output"
VOICE_REF_DIR = BASE_DIR / "config" / "voice_ref"
