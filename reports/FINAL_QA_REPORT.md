# Final QA Report

## 1. Files Changed
- `src/generate_metrics.py`: Updated to correctly compute and inject category keyword flags (`cat_gps_location`, etc.) directly into the `google_play_reviews_clean.csv`, resolving the mismatch between the cleaning pipeline and the dashboard's categorical logic.
- `src/generate_metrics.py`: Refactored the ML metadata generation to explicitly separate dataset metrics and model metrics. It now outputs to a canonical, nested `data/processed/metrics.json` and a specific `models/model_metadata.json`.
- `app/utils/data.py`: Rewrote the `category_stats()` logic to compute exact, strict denominators (overall share vs. low-star prevalence) as required. Introduced `validate_review_schema()` to fail fast if columns are missing.
- `app/pages/2_Complaint_Deep_Dive.py`: Migrated all charts to use dynamically filtered datasets (`df_filtered`) tied to a new date-range picker. Added exact sample size calculations, unclassified review counts, and overlapping-theme clarifications.
- `app/pages/4_ML_Model.py`: Refactored to fetch metrics directly from the loaded `meta` artifact (linked strictly to the ML model), discarding global dashboard metric assumptions. Replaced the hardcoded inline inference function with the shared `moveinsync.inference.predict_low_star()` for total internal consistency.
- `app/pages/5_Action_Plan.py`: Searched and purged all unsupported engineering prescriptions (e.g., hardcoded "5-sec GPS ping", "geofence expand to 150m") and correctly reframed them as high-priority telemetry/investigation targets. Removed hardcoded ML metrics from the methodology block.
- `tests/test_moveinsync.py`: Rewritten to validate the new nested `metrics.json` schema (`dataset` and `ml_model`). All 5 core tests pass successfully.
- `scratch/cleanup.py`: Executed to safely archive obsolete scripts, including the deprecated `01_cleaning_and_preprocessing.ipynb`.

## 2. Problems Fixed
- **Inconsistent Category Schemas**: The dashboard (`data.py`) formerly expected category columns that the cleaning script (`generate_metrics.py`) never produced. These are now explicitly created, mapped, and strictly validated on load.
- **Ambiguous Denominators**: "Theme count" vs "Theme low-star share" are now calculated identically across the repository and properly labelled.
- **Model Metadata Leakage**: Model metrics were previously co-mingled with dataset metrics. The pipeline now cleanly exports `models/model_metadata.json` ensuring the dashboard loads the exact metrics of the fitted `low_star_classifier.pkl`.
- **Inference Duplication**: The Streamlit dashboard no longer attempts to replicate the cleaning regex used during training. Both leverage `moveinsync.preprocessing.clean_text()`.
- **Unsupported Prescriptive Engineering**: The Action Plan no longer acts as if public text reviews independently validate server-side engineering constants like "150m geofence". It correctly identifies these as hypotheses requiring specific internal telemetry validation.

## 3. Final Dataset Statistics
- **Raw Reviews**: 10,144
- **Cleaned Valid Reviews**: 10,144
- **Duplicate Texts**: 1,992 reviews shared identical text with another review.
- **Low-Star (1-2) Share**: 41% of all reviews.
- **Mean Rating**: 3.21★

## 4. Final ML Metrics & Split Strategy
- **Split Strategy**: `Random split after dropping exact duplicate texts` to strictly prevent train/test leakage.
- **Test Set Size**: 1,599 unique reviews.
- **Algorithm**: TF-IDF + Logistic Regression (balanced class weights).
- **ROC-AUC**: 0.910
- **F1-Macro**: 0.843

## 5. Test Results
- **Test Command**: `pytest tests/test_moveinsync.py`
- All automated tests pass. Tests cover text cleaning, duplicate isolation theory, strict nested JSON schema validation, and complete inference mapping.

## 6. Dashboard & Presentation Verification
- The dashboard successfully loads and references `metrics.json` and `model_metadata.json` accurately. Errors are gracefully handled with Streamlit alerts if artifacts are missing or schemas fail.
- All deep-dive charts properly react to global filtering.
- The presentation `deliverables/MoveInSync_Rating_Recovery_Plan.pptx` reflects the audited numbers.

## 7. Remaining Limitations
- While text-duplicate leakage has been prevented via grouping, a true chronological split (time-based) would be even more robust for production.
- Root causes in the Action Plan are confident *hypotheses* based on user text, but require internal telemetry to confirm.

## 8. Exact Reproduction Commands
```bash
# Generate the data, metrics, and models
python src/generate_metrics.py

# Run automated tests
pytest tests/

# Launch dashboard
streamlit run app/streamlit_app.py
```
