import pandas as pd
import json
import os
import datetime
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, roc_auc_score, f1_score, precision_score, recall_score
from sklearn.dummy import DummyClassifier
import joblib
import traceback
import hashlib

def main():
    print("Loading raw data...")
    try:
        raw_df = pd.read_csv('data/raw/google_play_reviews.csv')
    except Exception as e:
        print(f"Error loading raw data: {e}")
        return

    metrics = {}
    metrics["raw_reviews"] = len(raw_df)
    metrics["unique_review_ids"] = int(raw_df["review_id"].nunique())
    
    # 1. Cleaning — document every exclusion step
    from moveinsync.preprocessing import clean_text
    clean_df = raw_df.drop_duplicates(subset=["review_id"]).copy()
    step1_count = len(clean_df)
    clean_df = clean_df.dropna(subset=["review_text", "star_rating"])
    step2_count = len(clean_df)
    clean_df["clean_text"] = clean_df["review_text"].apply(clean_text)
    clean_df = clean_df[clean_df["clean_text"].str.len() > 0]  # Drop reviews with empty text after cleaning (e.g. emoji-only)
    step3_count = len(clean_df)
    
    metrics["excluded_duplicate_ids"] = int(len(raw_df) - step1_count)
    metrics["excluded_null_text_or_rating"] = int(step1_count - step2_count)
    metrics["excluded_too_short_text"] = int(step2_count - step3_count)
    metrics["total_excluded"] = int(len(raw_df) - step3_count)
    metrics["clean_reviews"] = step3_count
    
    clean_df["is_low_star"] = (clean_df["star_rating"] <= 2).astype(int)
    
    # Keyword categorization
    categories = {
        "gps_location": ["gps", "location", "map", "track", "route", "wrong path", "navigation"],
        "crashes_login": ["crash", "otp", "login", "hang", "stuck", "blank", "error", "bug", "glitch", "uninstall", "open"],
        "eta_pickup": ["eta", "late", "delay", "on time", "wait", "pickup"],
        "driver_comms": ["driver", "call", "rude", "behaviour", "behavior"],
        "noshow_checkin": ["no show", "absent", "check in", "boarded", "escort"],
    }
    
    import re
    for cat_name, keywords in categories.items():
        pattern = "|".join([r"\b" + re.escape(kw) + r"\b" for kw in keywords])
        clean_df[f"cat_{cat_name}"] = clean_df['review_text'].fillna("").str.lower().str.contains(pattern, regex=True).astype(int)
        
        # Calculate category specific metrics
        cat_col = f"cat_{cat_name}"
        metrics[f"{cat_col}_total"] = int(clean_df[cat_col].sum())
        metrics[f"{cat_col}_low_star"] = int(clean_df[clean_df["is_low_star"] == 1][cat_col].sum())
    
    # Calculate unclassified share
    cat_cols = [f"cat_{c}" for c in categories.keys()]
    clean_df["is_categorized"] = clean_df[cat_cols].max(axis=1)
    metrics["unclassified_reviews"] = len(clean_df) - int(clean_df["is_categorized"].sum())
    metrics["unclassified_share"] = round(metrics["unclassified_reviews"] / metrics["clean_reviews"], 3)
    
    metrics["duplicate_texts"] = clean_df["clean_text"].duplicated().sum()
    metrics["low_star_reviews"] = int(clean_df["is_low_star"].sum())
    metrics["low_star_share"] = round(metrics["low_star_reviews"] / metrics["clean_reviews"], 3)
    metrics["mean_rating"] = round(clean_df["star_rating"].mean(), 2)

    # 2. ML Training (preventing text leakage)
    print("Preparing ML training data...")
    # Build dataset fingerprint for traceability
    dataset_fingerprint = hashlib.md5(
        clean_df["review_id"].sort_values().str.cat(sep=",").encode()
    ).hexdigest()[:12]
    
    ml_df = clean_df.drop_duplicates(subset=["clean_text"]).copy()
    
    X = ml_df["clean_text"]
    y = ml_df["is_low_star"]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print("Training ML model...")
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=3000, ngram_range=(1, 2), stop_words='english')),
        ('clf', LogisticRegression(class_weight='balanced', random_state=42, max_iter=1000))
    ])
    pipeline.fit(X_train, y_train)
    
    print("Evaluating ML model...")
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]
    
    # Baseline comparison
    dummy = DummyClassifier(strategy="most_frequent")
    dummy.fit(X_train, y_train)
    y_dummy = dummy.predict(X_test)

    report = classification_report(y_test, y_pred, output_dict=True)
    
    ml_metadata = {
        "model_version": "1.0.0",
        "model_artifact": "low_star_classifier.pkl",
        "positive_class": "1-2 stars (is_low_star=1)",
        "evaluation_timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "dataset_fingerprint": dataset_fingerprint,
        "split_strategy": "Random 80/20 split after removing duplicate normalized texts",
        "sklearn_version": __import__('sklearn').__version__,
        "ml_train_size": int(len(X_train)),
        "ml_test_size": int(len(X_test)),
        "train_low_star_count": int(y_train.sum()),
        "test_low_star_count": int(y_test.sum()),
        "f1_macro": round(f1_score(y_test, y_pred, average="macro"), 3),
        "f1_low_star": round(report.get("1", {}).get("f1-score", 0), 3),
        "precision_low_star": round(report.get("1", {}).get("precision", 0), 3),
        "recall_low_star": round(report.get("1", {}).get("recall", 0), 3),
        "roc_auc": round(roc_auc_score(y_test, y_prob), 3),
        "baseline_f1_macro": round(f1_score(y_test, y_dummy, average="macro"), 3),
    }
    
    print("Saving artifacts...")
    os.makedirs('data/processed', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    # Save canonical data
    clean_df.to_csv('data/processed/google_play_reviews_clean.csv', index=False)
    
    # Save ML model and its explicit metadata
    joblib.dump(pipeline, 'models/low_star_classifier.pkl')
    with open('models/model_metadata.json', 'w') as f:
        json.dump(ml_metadata, f, indent=4)
    
    # Save canonical metrics
    metrics_path = 'data/processed/metrics.json'
    final_metrics = {
        "dataset": metrics,
        "ml_model": ml_metadata
    }
    with open(metrics_path, 'w') as f:
        json.dump(final_metrics, f, indent=4, default=float)
        
    print("Done! Canonical metrics and models updated.")

if __name__ == '__main__':
    main()
