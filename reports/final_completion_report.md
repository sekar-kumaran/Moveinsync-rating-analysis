# Final Completion Report

## 1. Repository Architecture & Pipeline
- **Raw Data Source**: `data/raw/google_play_reviews.csv` (10,144 records collected via `google-play-scraper`).
- **Canonical Pipeline**: `src/generate_metrics.py` is the single source of truth for cleaning, text normalization, dataset metrics, and ML model training.
- **Modular Package**: `src/moveinsync/` provides shared modules: `preprocessing.py`, `model_loader.py`, and `inference.py`.
- **Interactive Workspace**: `notebooks/01_moveinsync_eda_and_ml.ipynb` performs exploratory data analysis and delegates model generation to the canonical pipeline to prevent competing artifact drift.
- **Multi-Page Dashboard**: Built with Streamlit (`app/streamlit_app.py` entry point with pages in `app/pages/`: `1_Rating_Analysis.py`, `2_Complaint_Deep_Dive.py`, `3_Review_Explorer.py`, `4_ML_Model.py`, `5_Action_Plan.py`) backed by `app/utils/data.py`.
- **Test Suite**: `tests/test_moveinsync.py` providing 15-area test coverage via `pytest`.

## 2. Dataset & Quality Metrics
- **Raw Reviews Collected**: 10,144 (all review IDs are unique).
- **Cleaning & Filtering**: Exactly 38 records were excluded because their text was non-alphanumeric (emojis/punctuation only) and became empty (`len == 0`) after standard text normalization. All legitimate short reviews (such as "good", "nice") were preserved.
- **Cleaned Reviews Retained**: 10,106 valid records (mean rating 3.21★, 41.1% low-star share).
- **Duplicate Normalized Texts**: 2,115 duplicate normalized-text occurrences beyond the first copy (`clean_df['clean_text'].duplicated().sum()`). These are retained in the EDA dataset to reflect genuine feedback frequency, but deduplicated prior to ML train/test splitting to prevent text leakage.

## 3. Machine Learning Classification
- **Task**: Predict whether review text indicates a **low-star experience (1–2 stars)** vs. 3–5 stars.
- **Architecture**: TF-IDF (3,000 max features, unigrams + bigrams) + Logistic Regression (`class_weight='balanced'`).
- **Data Split**: Text-deduplicated 80/20 stratified split (6,392 train / 1,599 test).
- **Evaluation (Held-Out Test Set)**:
  - ROC-AUC: 0.909
  - Macro F1: 0.843 (substantially beats the majority-class baseline F1 of 0.335)
  - Low-Star F1: 0.850 (Precision: 0.823, Recall: 0.879)
- **Calibration & Terminology**: Model outputs are raw sigmoid scores, not calibrated probabilities.
- **Domain Scope**: Trained and evaluated exclusively on public Google Play reviews. Not validated for internal support tickets, HR complaints, or operational logs.

## 4. Prioritization & Engineering Actions
- **Evidence-Based Measurement Framework**: Removed speculative linear rating-lift projections. Replaced with structured measurement cards defining verified baselines, proposed interventions, leading indicators, required internal data, and confidence boundaries.
- **Top Issue Categories**:
  1. **GPS & Live Location**: 1,415 reviews (57.2% low-star). Requires driver-app telemetry to verify ping intervals.
  2. **App Stability & Login/OTP**: 1,017 reviews (78.0% low-star). Requires Crashlytics stack traces and SMS delivery logs.
  3. **Silent Notifications**: Cab arrives unannounced due to OS Doze mode; requires FCM priority audit.
  4. **Driver Assignment Failure**: Users stuck in limbo; requires dispatch system logs.
  5. **No-Show Disputes**: Mismatch between driver check-in and employee geofence.

## 5. Execution & Verification Commands
- **Install Dependencies**: `pip install -r requirements.txt`
- **Run Pipeline & Generate Artifacts**: `python src/generate_metrics.py`
- **Run Test Suite**: `pytest tests/`
- **Launch Dashboard**: `streamlit run app/streamlit_app.py`

