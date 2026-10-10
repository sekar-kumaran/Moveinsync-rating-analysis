"""Shared data loading -- cached at the process level."""
import sys
import json
from pathlib import Path

import pandas as pd
import numpy as np
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / "src"))

CAT_COLS = ["cat_gps_location", "cat_crashes_login", "cat_eta_pickup",
            "cat_driver_comms", "cat_noshow_checkin"]
CAT_LABELS = {
    "cat_gps_location":   "GPS & Live Location",
    "cat_crashes_login":  "Crashes & Login / OTP",
    "cat_eta_pickup":     "ETA & Late Pickup",
    "cat_driver_comms":   "Driver Communication",
    "cat_noshow_checkin": "No-Show & Check-in",
}


@st.cache_data(show_spinner="Loading review data...")
def load_reviews() -> pd.DataFrame:
    path = BASE_DIR / "data" / "processed" / "google_play_reviews_clean.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    df["star_rating"]  = pd.to_numeric(df["star_rating"], errors="coerce")
    df = df.dropna(subset=["star_rating"])
    df["star_rating"]  = df["star_rating"].astype(int)
    df["review_date"]  = pd.to_datetime(df["review_date"], utc=True, errors="coerce")
    df["year_month"]   = df["review_date"].dt.to_period("M").dt.to_timestamp()
    df["year"]         = df["review_date"].dt.year
    df["month"]        = df["review_date"].dt.month
    df["day_of_week"]  = df["review_date"].dt.day_name()
    df["is_low_star"]  = (df["star_rating"] <= 2).astype(int)
    # clean_text fallback
    if "clean_text" not in df.columns:
        import re
        def _clean(t):
            t = str(t).lower()
            t = re.sub(r"http\S+", " ", t)
            t = re.sub(r"[^a-z\s]", " ", t)
            return re.sub(r"\s+", " ", t).strip()
        df["clean_text"] = df["review_text"].apply(_clean)
    return df


@st.cache_data(show_spinner=False)
def monthly_stats(df: pd.DataFrame) -> pd.DataFrame:
    m = (df.groupby("year_month")
           .agg(count=("star_rating","count"),
                avg_rating=("star_rating","mean"),
                low_pct=("is_low_star","mean"),
                five_star_pct=("star_rating", lambda x:(x==5).mean()))
           .reset_index())
    m = m[m["count"] >= 8].copy()
    m["low_pct"]        *= 100
    m["five_star_pct"]  *= 100
    return m


@st.cache_data(show_spinner=False)
def yearly_stats(df: pd.DataFrame) -> pd.DataFrame:
    return (df.groupby("year")
              .agg(count=("star_rating","count"),
                   avg_rating=("star_rating","mean"),
                   low_pct=("is_low_star","mean"))
              .reset_index()
              .assign(low_pct=lambda x: x["low_pct"]*100))


@st.cache_data(show_spinner=False)
def rating_distribution(df: pd.DataFrame) -> pd.DataFrame:
    rd = df["star_rating"].value_counts().sort_index().reset_index()
    rd.columns = ["Rating","Count"]
    rd["Pct"] = (rd["Count"] / len(df) * 100).round(1)
    return rd


@st.cache_data(show_spinner=False)
def category_stats(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in CAT_COLS:
        if col not in df.columns:
            continue
        label = CAT_LABELS[col]
        total      = int(df[col].sum())
        low_total  = int(df[df["star_rating"] <= 2][col].sum())
        pct_of_low = round(low_total / max((df["star_rating"] <= 2).sum(), 1) * 100, 1)
        rows.append(dict(col=col, label=label, total=total,
                         low_total=low_total, pct_of_low=pct_of_low))
    return pd.DataFrame(rows).sort_values("low_total", ascending=False)


@st.cache_resource(show_spinner=False)
def load_model():
    """Returns (pipeline, metadata) or (None, None)."""
    import joblib
    model_path = BASE_DIR / "models" / "low_star_classifier.pkl"
    meta_path  = BASE_DIR / "models" / "model_metadata.json"
    if not model_path.exists():
        return None, None
    try:
        pipeline = joblib.load(model_path)
        metadata = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        return pipeline, metadata
    except Exception:
        return None, None
