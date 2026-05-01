"""Flora Collector — Config"""
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

DATA_DIR = PROJECT_ROOT / "data"
IMAGES_DIR = DATA_DIR / "images"
for d in [DATA_DIR, IMAGES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

PLANTNET_API_KEY = os.getenv("PLANTNET_API_KEY", "")
PLANTNET_API_URL = "https://my-api.plantnet.org/v2/identify/all"
INATURALIST_API_URL = "https://api.inaturalist.org/v1"
DATABASE_URL = f"sqlite:///{PROJECT_ROOT}/data/flora.db"
