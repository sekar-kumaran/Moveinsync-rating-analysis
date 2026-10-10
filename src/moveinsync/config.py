import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "google_play_reviews.csv"
PROCESSED_DATA_PATH = DATA_DIR / "processed" / "google_play_reviews_clean.csv"

MODELS_DIR = BASE_DIR / "models"
CLASSIFIER_MODEL_PATH = MODELS_DIR / "low_star_classifier.pkl"
MODEL_METADATA_PATH = MODELS_DIR / "model_metadata.json"

# Feature configuration
MAX_REVIEW_LENGTH = 1000

# Categories setup in notebook
CATEGORY_RULES = {
    "booking_date": "Booking & Date",
    "vehicle_assignment": "Vehicle Assignment",
    "gps_location": "GPS / Location",
    "eta_pickup": "ETA & Pickup",
    "crashes_login": "Crash/Perf/Login",
    "driver_comms": "Driver Comms",
    "noshow_checkin": "Check-in/No-show",
    "support": "Support",
}
