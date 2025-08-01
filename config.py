import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
CACHE_DIR = MODELS_DIR / "cache"
DATA_DIR = BASE_DIR / "data"

MODELS_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

os.environ["TRANSFORMERS_CACHE"] = str(CACHE_DIR)
os.environ["HF_HOME"] = str(CACHE_DIR)
os.environ["TORCH_HOME"] = str(CACHE_DIR)

AI_CONFIG = {
    "model_name": "microsoft/DialoGPT-small",  # Smaller model for faster loading
    "max_length": 1000,
    "temperature": 0.7,
    "top_p": 0.9,
    "device": "cpu"
}

print(f"📁 Models will be saved to: {CACHE_DIR}")
print(f"🔧 Using device: {AI_CONFIG['device']}")