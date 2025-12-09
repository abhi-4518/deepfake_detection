import os
from pathlib import Path

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Primary Model Config
PRIMARY_WEIGHTS_DIR = os.getenv("PRIMARY_WEIGHTS_DIR", str(BASE_DIR / "vendor" / "clipbased" / "weights"))
PRIMARY_MODEL_NAME = os.getenv("PRIMARY_MODEL_NAME", "clipdet_latent10k_plus")
PRIMARY_CONFIDENCE_THRESHOLD = float(os.getenv("PRIMARY_CONFIDENCE_THRESHOLD", "0.65"))
DEVICE = os.getenv("DEVICE", "cpu")

# Fallback Model Config
FALLBACK_MODEL_PATH = os.getenv("FALLBACK_MODEL_PATH", str(BASE_DIR / "V3_103.h5"))

# API Config
PORT = int(os.getenv("PORT", "8000"))
