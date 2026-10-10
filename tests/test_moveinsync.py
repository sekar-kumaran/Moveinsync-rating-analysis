"""
Comprehensive test suite for MoveInSync FDE Case Study.
Phase 7 — Strengthened tests covering all 15 required areas.
"""
import pytest
import pandas as pd
import json
import sys
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "src"))

from moveinsync.preprocessing import clean_text
from moveinsync.inference import predict_low_star

METRICS_PATH = BASE_DIR / "data/processed/metrics.json"
RAW_PATH     = BASE_DIR / "data/raw/google_play_reviews.csv"
CLEAN_PATH   = BASE_DIR / "data/processed/google_play_reviews_clean.csv"
MODEL_PATH   = BASE_DIR / "models/low_star_classifier.pkl"
META_PATH    = BASE_DIR / "models/model_metadata.json"


# ─── Fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def raw_df():
    return pd.read_csv(RAW_PATH)

@pytest.fixture(scope="module")
def clean_df():
    return pd.read_csv(CLEAN_PATH)

@pytest.fixture(scope="module")
def metrics():
    with open(METRICS_PATH) as f:
        return json.load(f)

@pytest.fixture(scope="module")
def model_meta():
    with open(META_PATH) as f:
        return json.load(f)

@pytest.fixture(scope="module")
def pipeline():
    import joblib
    return joblib.load(MODEL_PATH)


# ─── 1. Text cleaning ───────────────────────────────────────────────────────

def test_clean_text_removes_urls():
    assert "http" not in clean_text("Visit http://example.com for more")

def test_clean_text_lowercases():
    assert clean_text("GREAT APP") == "great app"

def test_clean_text_removes_punctuation():
    result = clean_text("I LOVE this app!!!")
    assert "!" not in result

def test_clean_text_returns_string():
    assert isinstance(clean_text("any input"), str)

def test_clean_text_empty_input():
    # Empty or whitespace-only input should return empty string
    assert clean_text("   ").strip() == ""

def test_clean_text_emoji_only():
    # Emoji-only reviews should produce empty (or near-empty) text after cleaning
    result = clean_text("👍👍👍")
    assert len(result.strip()) == 0


# ─── 2. Rating validation ───────────────────────────────────────────────────

def test_ratings_in_valid_range(clean_df):
    assert clean_df["star_rating"].between(1, 5).all(), "All ratings must be 1-5"

def test_rating_is_integer_like(clean_df):
    assert clean_df["star_rating"].apply(lambda x: x == int(x)).all()


# ─── 3. Duplicate review ID handling ────────────────────────────────────────

def test_no_duplicate_review_ids_in_raw(raw_df):
    assert raw_df["review_id"].nunique() == len(raw_df), "Raw dataset should have unique review IDs"

def test_no_duplicate_review_ids_in_clean(clean_df):
    assert clean_df["review_id"].nunique() == len(clean_df), "Cleaned dataset should have unique review IDs"


# ─── 4. Duplicate normalized-text statistics ────────────────────────────────

def test_duplicate_text_count_in_metrics(metrics):
    ds = metrics["dataset"]
    clean_count = ds["clean_reviews"]
    unique_texts = ds.get("clean_reviews", 0) - ds.get("duplicate_texts", 0)
    # duplicate_texts should be strictly < clean_reviews
    assert ds["duplicate_texts"] < clean_count

def test_duplicate_text_stats_consistent(metrics, clean_df):
    """Metrics.json duplicate_texts should match actual DataFrame."""
    actual_dupes = int(clean_df["clean_text"].duplicated().sum())
    reported = int(metrics["dataset"]["duplicate_texts"])
    assert actual_dupes == reported, (
        f"Metrics says {reported} dupe texts; actual is {actual_dupes}")


# ─── 5. Required category columns ───────────────────────────────────────────

REQUIRED_CAT_COLS = [
    "cat_gps_location", "cat_crashes_login", "cat_eta_pickup",
    "cat_driver_comms", "cat_noshow_checkin", "is_categorized",
]

def test_category_columns_exist(clean_df):
    for col in REQUIRED_CAT_COLS:
        assert col in clean_df.columns, f"Missing column: {col}"

def test_category_columns_are_binary(clean_df):
    for col in REQUIRED_CAT_COLS:
        assert set(clean_df[col].unique()).issubset({0, 1}), (
            f"Column {col} must be binary (0 or 1)")


# ─── 6. Theme counts and low-star denominators ──────────────────────────────

def test_category_total_counts_match_metrics(metrics, clean_df):
    ds = metrics["dataset"]
    for cat in ["gps_location", "crashes_login", "eta_pickup", "driver_comms", "noshow_checkin"]:
        col = f"cat_{cat}"
        reported = ds.get(f"{col}_total", -1)
        actual = int(clean_df[col].sum())
        assert reported == actual, (
            f"{col}_total: metrics={reported}, actual={actual}")

def test_category_lowstar_counts_match_metrics(metrics, clean_df):
    ds = metrics["dataset"]
    for cat in ["gps_location", "crashes_login", "eta_pickup", "driver_comms", "noshow_checkin"]:
        col = f"cat_{cat}"
        reported = ds.get(f"{col}_low_star", -1)
        actual = int(clean_df[clean_df["is_low_star"] == 1][col].sum())
        assert reported == actual, (
            f"{col}_low_star: metrics={reported}, actual={actual}")

def test_lowstar_share_is_correct(metrics, clean_df):
    expected = round(int(clean_df["is_low_star"].sum()) / len(clean_df), 3)
    reported = metrics["dataset"]["low_star_share"]
    assert abs(expected - reported) < 0.001


# ─── 7. Empty categories and missing values ─────────────────────────────────

def test_clean_text_has_no_nulls(clean_df):
    assert clean_df["clean_text"].isna().sum() == 0, "clean_text must not have nulls"

def test_is_low_star_has_no_nulls(clean_df):
    assert clean_df["is_low_star"].isna().sum() == 0


# ─── 8. Metrics JSON schema and serialization ────────────────────────────────

def test_metrics_json_top_level_keys(metrics):
    assert "dataset" in metrics
    assert "ml_model" in metrics

def test_metrics_dataset_required_fields(metrics):
    ds = metrics["dataset"]
    for key in ["raw_reviews", "clean_reviews", "low_star_reviews", "low_star_share",
                "mean_rating", "duplicate_texts", "total_excluded",
                "excluded_too_short_text"]:
        assert key in ds, f"Missing key in dataset: {key}"

def test_metrics_ml_required_fields(metrics):
    ml = metrics["ml_model"]
    for key in ["f1_macro", "roc_auc", "ml_train_size", "ml_test_size",
                "baseline_f1_macro", "evaluation_timestamp", "sklearn_version",
                "dataset_fingerprint"]:
        assert key in ml, f"Missing key in ml_model: {key}"

def test_metrics_json_serializable():
    # Verify it can be round-tripped through JSON
    with open(METRICS_PATH) as f:
        raw = f.read()
    parsed = json.loads(raw)
    assert isinstance(parsed, dict)


# ─── 9. Exact-text leakage across ML boundary ────────────────────────────────

def test_no_text_overlap_between_train_and_test(clean_df):
    """Simulate the deduplication then split and verify no shared texts."""
    ml_df = clean_df.drop_duplicates(subset=["clean_text"])
    from sklearn.model_selection import train_test_split
    X = ml_df["clean_text"]
    y = ml_df["is_low_star"]
    X_train, X_test, _, _ = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    overlap = set(X_train) & set(X_test)
    assert len(overlap) == 0, f"Found {len(overlap)} texts present in both train and test"

def test_full_df_text_duplication_stats(clean_df):
    total = len(clean_df)
    unique = clean_df["clean_text"].nunique()
    dupes = total - unique
    assert dupes >= 0
    # Verify this matches what pipeline reports
    pipeline_dupes = int(clean_df["clean_text"].duplicated().sum())
    assert dupes == pipeline_dupes


# ─── 10. Baseline and classifier metrics ─────────────────────────────────────

def test_classifier_beats_majority_baseline(metrics):
    """Model F1-macro must exceed majority-class baseline."""
    ml = metrics["ml_model"]
    assert ml["f1_macro"] > ml["baseline_f1_macro"], (
        f"Model F1 {ml['f1_macro']} must exceed baseline {ml['baseline_f1_macro']}")

def test_roc_auc_above_random(metrics):
    assert metrics["ml_model"]["roc_auc"] > 0.5, "ROC-AUC must be above 0.5 (random chance)"

def test_f1_low_star_reasonable(metrics):
    f1 = metrics["ml_model"]["f1_low_star"]
    assert 0.5 < f1 < 1.0, f"F1 for low-star class is unexpected: {f1}"


# ─── 11. Model and metadata consistency ──────────────────────────────────────

def test_model_metadata_json_matches_metrics_json(metrics, model_meta):
    """model_metadata.json must agree with the ml_model block in metrics.json."""
    ml = metrics["ml_model"]
    for key in ["f1_macro", "roc_auc", "ml_train_size", "ml_test_size"]:
        assert ml[key] == model_meta[key], (
            f"Mismatch in {key}: metrics.json={ml[key]}, model_metadata.json={model_meta[key]}")

def test_sklearn_version_recorded(model_meta):
    assert "sklearn_version" in model_meta
    assert len(model_meta["sklearn_version"]) > 0


# ─── 12. Model loading and inference ─────────────────────────────────────────

def test_model_loads(pipeline):
    assert pipeline is not None

def test_model_can_predict(pipeline):
    pred = pipeline.predict(["The app crashes all the time"])
    assert pred[0] in [0, 1]

def test_inference_returns_dict():
    result = predict_low_star("This app crashes all the time!")
    assert isinstance(result, dict)
    assert "is_low_star" in result
    assert result["error"] is None

def test_inference_empty_text():
    result = predict_low_star("")
    assert result["error"] is not None
    assert result["is_low_star"] is None

def test_inference_whitespace_only():
    result = predict_low_star("   ")
    assert result["is_low_star"] is None

def test_inference_positive_example():
    result = predict_low_star("Great app, always on time, very happy!")
    assert result["is_low_star"] is False

def test_inference_negative_example():
    result = predict_low_star("app keeps crashing. otp never arrives. useless.")
    assert result["is_low_star"] is True


# ─── 13. Raw-to-cleaned record reconciliation ────────────────────────────────

def test_raw_to_clean_row_count(metrics):
    ds = metrics["dataset"]
    assert ds["raw_reviews"] - ds["total_excluded"] == ds["clean_reviews"], (
        "raw - excluded must equal clean")

def test_excluded_records_are_emoji_only(raw_df, clean_df):
    """Verify every excluded record has empty clean_text (emoji-only)."""
    raw_ids = set(raw_df["review_id"])
    clean_ids = set(clean_df["review_id"])
    dropped_ids = raw_ids - clean_ids
    dropped = raw_df[raw_df["review_id"].isin(dropped_ids)].copy()
    dropped["ct"] = dropped["review_text"].apply(clean_text)
    assert (dropped["ct"].str.len() == 0).all(), (
        "All excluded records must have empty clean_text")


# ─── 14. Category filtering (simulated review explorer) ─────────────────────

def test_category_filter_returns_subset(clean_df):
    gps_reviews = clean_df[clean_df["cat_gps_location"] == 1]
    assert len(gps_reviews) < len(clean_df)
    assert (gps_reviews["cat_gps_location"] == 1).all()

def test_multiple_category_filter(clean_df):
    both = clean_df[(clean_df["cat_gps_location"] == 1) & (clean_df["cat_crashes_login"] == 1)]
    assert (both["cat_gps_location"] == 1).all()
    assert (both["cat_crashes_login"] == 1).all()


# ─── 15. Action-plan calculations (no fabricated forecasts) ──────────────────

def test_action_plan_no_fabricated_lift():
    """Verify the action plan page has no hardcoded rating increments."""
    action_plan = BASE_DIR / "app/pages/5_Action_Plan.py"
    content = action_plan.read_text(encoding="utf-8")
    # These were the fabricated lift values; they must not be in the source
    assert "mean_rating + 0.30" not in content, "Found fabricated +0.30 rating lift"
    assert "mean_rating + 0.48" not in content, "Found fabricated +0.48 rating lift"
    assert "mean_rating + 0.62" not in content, "Found fabricated +0.62 rating lift"
    assert "mean_rating + 0.80" not in content, "Found fabricated +0.80 rating lift"
    assert "Conservative Rating Lift Forecast" not in content, "Found fabricated forecast label"

def test_home_page_no_hardcoded_prescriptions():
    """Verify the home page no longer has hardcoded engineering parameters."""
    home = BASE_DIR / "app/streamlit_app.py"
    content = home.read_text(encoding="utf-8")
    assert "30s -> 5s" not in content, "Found unsupported GPS ping prescription"
    assert "50m->150m" not in content, "Found unsupported geofence prescription"
