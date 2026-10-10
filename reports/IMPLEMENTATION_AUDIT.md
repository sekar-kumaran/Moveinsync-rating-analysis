# Implementation Audit

## 1. Actual Repository Structure
- `data/raw/`: Contains `google_play_reviews.csv`
- `data/processed/`: Contains reproducible outputs `metrics.json` and `google_play_reviews_clean.csv`.
- `models/`: Contains the fitted model `low_star_classifier.pkl` and strictly corresponding `model_metadata.json`.
- `src/`: The `generate_metrics.py` orchestrator script, calling shared logic inside the `moveinsync/` module.
- `app/`: Multi-page Streamlit application reading dynamically from processed data.
- `archive/`: Old notebooks and utility scripts that have been deprecated to prevent confusion.
- `tests/`: Automated test suite in `test_moveinsync.py`.
- `reports/` and `deliverables/`: Generated presentation decks and markdown documentation.

## 2. Main Execution Paths
The pipeline operates strictly unidirectionally to guarantee reproducibility:
1. `python src/generate_metrics.py` reads raw data, processes it via `moveinsync.preprocessing`, isolates duplicates, trains the classifier, and outputs canonical CSV, JSON, and Pickle files.
2. `streamlit run app/streamlit_app.py` boots the dashboard and reads strictly from `data/processed/metrics.json` and `models/model_metadata.json`.
3. `pytest tests/test_moveinsync.py` guarantees the schema logic and inference consistency.

## 3. Data Dependencies for Each Dashboard Page
- **Executive Summary:** `data/processed/metrics.json` (Dataset block)
- **Deep Dive / Trends / Explorer:** `data/processed/google_play_reviews_clean.csv` (Uses strict schema validation)
- **ML Model:** `models/low_star_classifier.pkl` and `models/model_metadata.json` (Model specific block)
- **Action Plan:** `google_play_reviews_clean.csv`

## 4. Model Training, Evaluation, and Inference Paths
- **Training/Eval:** Exclusively handled by `src/generate_metrics.py`. Duplicates dropped prior to split.
- **Inference:** Handled globally by `src.moveinsync.inference.predict_low_star()`. Used directly by the Streamlit application to ensure text normalization rules are identical to training.

## 5. Existing Inconsistencies Discovered and Fixed
- `google_play_reviews_clean.csv` lacked category columns (GPS, crashes, etc.). The dashboard was failing to extract category statistics.
- Category statistic calculations were using arbitrary denominators for share calculations.
- `metrics.json` contained merged properties from the dataset generation and the ML generation, leading to cross-contamination of metadata.
- Deep dive charts did not respond to global date filters.
- Action plan pages cited unsupported engineering fixes (150m geofence, 5-sec ping) instead of hypotheses requiring telemetry.
- Dashboard inference manually reimplemented a text cleaning function rather than importing the core module.

## 6. Changes Required
All inconsistencies discovered above have been resolved and implemented in this current run.

## 7. Tests That Establish Correctness
- `test_metrics_json_schema`: Ensures the nested schema prevents namespace clashing.
- `test_duplicate_text_handling`: Ensures text duplicates are purged before ML modeling.
- `test_inference_returns_dict`: Ensures the external inference function loads the correct artifact and successfully vectorizes raw strings.
