import joblib
import json
import logging
from typing import Tuple, Dict, Any, Optional

from . import config

logger = logging.getLogger(__name__)
_cached_model = None
_cached_metadata = None

def get_model_and_metadata() -> Tuple[Optional[Any], Optional[Dict]]:
    """Loads the ML pipeline and metadata, using an in-memory cache to avoid reloading."""
    global _cached_model, _cached_metadata
    
    if _cached_model is not None and _cached_metadata is not None:
        return _cached_model, _cached_metadata
        
    if not config.CLASSIFIER_MODEL_PATH.exists() or not config.MODEL_METADATA_PATH.exists():
        logger.warning(f"Model or metadata not found in {config.MODELS_DIR}. Inference will fallback.")
        return None, None
        
    try:
        _cached_model = joblib.load(config.CLASSIFIER_MODEL_PATH)
        with open(config.MODEL_METADATA_PATH, "r") as f:
            _cached_metadata = json.load(f)
        return _cached_model, _cached_metadata
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return None, None
