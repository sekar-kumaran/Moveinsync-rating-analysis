# Final Completion Report

## 1. Initial Project Structure and Problems Found
- **Structure**: The initial project used a script-based sequential pipeline (`collect`, `clean`, `classify`, `analyze`, `build_dashboard_data`, `train_model`) rather than an interactive ML notebook as requested. 
- **Dashboard**: The Streamlit dashboard was monolithic (`app/streamlit_app.py`), and reliant on pre-computed JSON files rather than dynamic loading from the dataset.
- **Notebooks**: Notebooks were generated dynamically through `notebooks/generate_notebooks.py` instead of being maintained properly.
- **Models**: The models directory was empty, and inference was not integrated directly into the application.

## 2. File Audit & Actions Taken
- **Retained**: `data/raw/google_play_reviews.csv` (Raw data source), `reports/` (Figures and docs), `deliverables/` (Case study presentation & report docs).
- **Refactored/Created**: 
  - `src/moveinsync/`: Created a clean, reusable Python package with `data_loader.py`, `preprocessing.py`, `model_loader.py`, `inference.py`, `config.py`.
  - `app/`: Refactored into a Multi-Page Streamlit application (`app/streamlit_app.py`, `app/pages/1_Executive_Overview.py`, etc.) powered by `app/services/dashboard_service.py`.
  - `notebooks/01_moveinsync_eda_and_ml.ipynb`: Unified data quality, EDA, feature engineering, and ML model training into a single notebook.
- **Archived**: Moved old `src/*_reviews.py`, `generate_notebooks.py`, and `app/old_streamlit_app.py` into the `archive/` directory to preserve potentially useful logic without polluting the codebase.
- **Removed**: Deleted the hard-coded `tests/test_pipeline.py` and replaced it with `tests/test_moveinsync.py`.

## 3. Dataset & Data Quality Results
- **Collected**: 10,144 raw reviews from the Google Play Store (app `com.moveinsync.ets`).
- **Data Quality**: Identified 1,992 duplicate text reviews.
- **Processed**: The cleaned dataset contains 10,144 valid reviews (duplicates kept for EDA), but exact text duplicates are dropped before ML training to prevent leakage.

## 4. EDA Findings
- **Overall Rating**: The application suffers from a significant volume of 1-star reviews.
- **Key Complaint Themes**:
  1. **GPS/Location Accuracy**: High correlation with 1-star ratings; users cite stale tracking preventing successful pickups.
  2. **App Crashes & Login (OTP) Issues**: Effectively block all application usage.
  3. **No-Show Disputes**: Drivers marking employees absent unjustly due to strict/faulty geofencing.

## 5. ML Classification & Validation
- **Target Task**: Predict whether a review implies a **LOW STAR RATING (1-2 stars)** based solely on the review text. 
- **Methodology**: Keyword-based classification was used for extracting issue themes (e.g., GPS, crashes), while a TF-IDF + Logistic Regression model was trained for the sentiment binary prediction task.
- **Validation**: 
  - TF-IDF + Logistic Regression: F1-Macro ~ 0.839, ROC-AUC > 0.908.
- **Final Model Artifact**: Saved as a complete Scikit-Learn pipeline to `models/low_star_classifier.pkl` and metadata to `data/processed/metrics.json`.

## 6. Dashboard
- **Entry Point**: `app/streamlit_app.py`
- **Run Command**: `streamlit run app/streamlit_app.py`
- **Live Inference**: Integrated on Page 5 (`ML Insights`), allowing real-time evaluation of user feedback text against the trained Logistic Regression model.

## 7. Testing & Reproducibility
- **Test Command**: `pytest tests/test_moveinsync.py -v` (Executed and passed).
- **Notebook Reproduction**: `python scripts/run_notebook.py`
- **Limitations**: Root causes listed in the dashboard are *hypotheses* derived from symptoms in public reviews. Verification requires internal telemetry data (e.g., Crashlytics, driver app GPS ping frequency).
