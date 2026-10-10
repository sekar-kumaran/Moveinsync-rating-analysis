import pytest
import pandas as pd
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "src"))

from moveinsync.preprocessing import clean_text
from moveinsync.data_loader import load_processed_data
from moveinsync.inference import predict_low_star

def test_clean_text():
    raw = "I LOVE this app!!! http://example.com"
    expected = "i love this app"
    assert clean_text(raw) == expected

def test_data_loader_returns_dataframe():
    df = load_processed_data()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'star_rating' in df.columns

def test_inference_returns_dict():
    result = predict_low_star("This app crashes all the time!")
    assert isinstance(result, dict)
    assert 'is_low_star' in result
    assert result['error'] is None

def test_inference_empty_text():
    result = predict_low_star("")
    assert result['error'] == "Empty review text provided."
    assert result['is_low_star'] is None
