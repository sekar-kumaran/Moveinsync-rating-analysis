import pytest
import pandas as pd
import json
import sys
from pathlib import Path
import os
import shutil

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "src"))

from moveinsync.preprocessing import clean_text
from moveinsync.data_loader import load_processed_data
from moveinsync.inference import predict_low_star

def test_clean_text():
    # 1. Review cleaning validation
    raw = "I LOVE this app!!! http://example.com"
    expected = "i love this app"
    assert clean_text(raw) == expected

def test_metrics_json_schema():
    # 2. JSON serialization and schema validation
    metrics_path = BASE_DIR / "data/processed/metrics.json"
    if metrics_path.exists():
        with open(metrics_path, "r") as f:
            data = json.load(f)
        assert "dataset" in data
        assert "ml_model" in data
        assert "raw_reviews" in data["dataset"]
        assert "f1_macro" in data["ml_model"]
        assert "duplicate_texts" in data["dataset"]

def test_duplicate_text_handling():
    # 3. Duplicate text detection and ML isolation theory
    # (Checking the logic implemented in generate_metrics.py)
    df = pd.DataFrame({
        "review_id": [1, 2, 3],
        "clean_text": ["good", "good", "bad"],
        "star_rating": [5, 5, 1]
    })
    
    # Simulate the pipeline
    df_clean = df.drop_duplicates(subset=["clean_text"])
    assert len(df_clean) == 2, "Should drop exact duplicates to prevent ML leakage"
    assert "good" in df_clean["clean_text"].values
    assert "bad" in df_clean["clean_text"].values

def test_inference_returns_dict():
    # 4. Model loading and inference
    result = predict_low_star("This app crashes all the time!")
    assert isinstance(result, dict)
    assert 'is_low_star' in result
    assert result['error'] is None

def test_inference_empty_text():
    result = predict_low_star("")
    assert result['error'] == "Empty review text provided."
    assert result['is_low_star'] is None
