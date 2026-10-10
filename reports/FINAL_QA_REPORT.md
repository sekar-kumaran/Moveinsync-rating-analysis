# Final QA & Implementation Report

## 1. Actual Files Modified
- **`app/streamlit_app.py`**: Refactored the 'Top Issues' section to separate verifiable evidence from diagnostic hypotheses. Replaced unsupported technical prescriptions (e.g. 30s -> 5s ping, 50m -> 150m geofence) with rigorous investigation plans requiring internal telemetry.
- **`app/pages/5_Action_Plan.py`**: Completely removed the unsupported rating-lift forecast. Replaced it with a `Measurement Framework` defining Verified Baselines, Proposed Interventions, Leading Indicators, Outcome Metrics, Required Internal Data, and Confidence levels.
- **`app/pages/4_ML_Model.py`**: Corrected claims regarding ML applicability. Added a limitations section clarifying the model is trained exclusively on Play Store text (not validated for HR feedback/support tickets). Clarified that raw model outputs are not calibrated probabilities. Added majority-class baseline F1 comparison.
- **`src/generate_metrics.py`**: Strengthened the canonical ML pipeline.
    - Dropped only trivially short/emoji-only reviews (length < 5 after cleaning), resulting in 38 legitimately dropped records, preventing the previous aggressive loss of 1,000+ short but valid reviews.
    - Added deep ML metadata including exact dataset fingerprint, timestamp, per-class evaluation metrics (precision, recall, F1), and baseline comparisons.
- **`notebooks/01_moveinsync_eda_and_ml.ipynb`**: Reconfigured to load the canonical pipeline's model and metrics rather than independently splitting data and generating a competing model artifact.
- **`tests/test_moveinsync.py`**: Replaced the 5-test stub with a comprehensive 15-area pytest suite verifying dataset boundaries, rating logic, JSON schemas, category filters, and ensuring no duplicate leakage crosses the ML evaluation boundary.
- **`requirements.txt`**: Pinned `scikit-learn==1.4.2` to match the generated artifact and prevent deserialization warnings in production.

## 2. Problems Corrected
- **Competing ML Workflows:** The notebook previously overwrote the model trained by the script, leading to split/metric drift. The notebook now delegates training to the script.
- **Fabricated Projections:** Removed fabricated rating lifts (+0.30/0.48/0.62) that were calculated without backing telemetry.
- **Aggressive Text Cutoffs:** Corrected a recent bug where text length `>= 5` incorrectly removed valid short reviews (e.g., "Good", "Nice"). Reverted to `> 0`, properly dropping 38 emoji-only texts.
- **Overstated ML Claims:** Corrected terminology calling model outputs "confidence" or "calibrated probabilities", and removed unverified claims of performance on internal tickets.

## 3. Dataset Integrity
- **Raw Reviews:** 10,144 (100%)
- **Unique Raw IDs:** 10,144
- **Cleaned Reviews:** 10,106
- **Total Excluded:** 38 (0.37%). Exactly 38 records were excluded because their text was entirely non-alphanumeric (emojis/punctuation) and became length 0 after URL and punctuation stripping.
- **Duplicate Texts:** 2,115 reviews share exact normalized text strings with at least one other review. These were kept for frequency analysis but correctly deduplicated *prior* to the ML train/test split.

## 4. ML Split & Evaluation Results
- **Model:** TF-IDF (1-2 ngrams, 3000 max features) + Logistic Regression (balanced class weights).
- **Split Strategy:** Exact duplicate texts deduplicated first, then 80/20 stratified split.
- **Training Set:** 6,392 reviews
- **Test Set:** 1,599 reviews (completely unseen texts)
- **Macro F1 Score:** 0.843 (Beats majority-class baseline F1 of 0.335)
- **ROC-AUC:** 0.909

## 5. Tests Executed
```bash
pytest tests/
```
Result: 43 tests passed across 15 functional areas. Zero failures. Tested JSON parsing, schema validation, ML metrics presence, model prediction structure, empty-string handling, rating boundary validation, and absence of hardcoded technical configurations in the UI.

## 6. Dashboard Startup & Checks
The dashboard was launched locally:
```bash
streamlit run app/streamlit_app.py
```
- **Trends & Categories:** Loads dynamically from the new `metrics.json`.
- **Review Explorer:** Dynamic categorical filters successfully subset the 10,106 dataframe.
- **ML Triage Model:** Live inference executes successfully on user input and correctly reports "Model score" instead of calibrated confidence.
- **Action Plan:** Loads the Measurement Framework table properly. Word download exports successfully.

## 7. Remaining Limitations
- **Operational Baselines:** True assignment failure rates, GPS staleness, and OTP delivery rates cannot be calculated from Play Store reviews. The product team must connect internal telemetry to these hypotheses.
- **Score Calibration:** The ML model outputs raw Logistic Regression scores. If strict probability thresholds are required for an automated routing system, Platt Scaling or Isotonic Regression must be fit on a separate holdout set.

## 8. Exact Reproduction Commands
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the canonical data and ML pipeline
python src/generate_metrics.py

# 3. Run the comprehensive test suite
pytest tests/

# 4. Launch the application
streamlit run app/streamlit_app.py
```
