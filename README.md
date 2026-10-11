# Moveinsync-rating-analysis

> **"Why does MoveInSync's employee transport app receive its current Play Store ratings — and what should Product & Engineering fix first?"**

A complete, reproducible, evidence-backed product analytics project built for the MoveInSync Forward Deployed Engineer candidate assignment.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Quick Start](#quick-start)
3. [Repository Structure](#repository-structure)
4. [Pipeline Steps](#pipeline-steps)
5. [Dashboard](#dashboard)
6. [Key Findings](#key-findings)
7. [Methodology](#methodology)
8. [Limitations](#limitations)
9. [Deliverables](#deliverables)

---

## Project Overview & Goal

### About MoveInSync & The Problem
MoveInSync helps companies run the daily journey of their employees to and from work. Over 1.5 million employees rely on it every working day across 430+ enterprise customers. The core of this experience is the **employee app** (`com.moveinsync.ets`), where users book rides, track cabs live, perform safety checks (OTP), and manage their shifts.

When the app fails—whether due to a late cab, a wrong route, a broken OTP, or a GPS glitch—it directly impacts an employee's ability to get to work on time. Frustrated users often turn to the Google Play Store to voice these critical issues.

### The Goal
The primary goal of this project is to answer a critical business question: **"Why does the MoveInSync employee app receive its current ratings, and what exactly needs to be fixed to improve them?"**

This repository serves as a comprehensive **Forward Deployed Engineer (FDE) Case Study**. It goes beyond simple data scraping to provide a full-stack product analytics solution:
1. **Data Collection & Cleaning**: Mining 10,000+ raw public reviews from the Play Store.
2. **Signal Extraction (ML & NLP)**: Using TF-IDF, Logistic Regression, and keyword categorization to extract actionable themes (GPS issues, crashes, no-shows) from unstructured text.
3. **Interactive Dashboard**: A multi-page Streamlit application that visualizes trends, isolates problematic app versions, and provides a live severity triage model.
4. **Actionable Roadmap**: Translating data into a prioritized, 30-day sprint plan for Mobile Engineering, Backend, and Product teams.

By bridging the gap between raw user feedback and engineering execution, this project demonstrates how data can directly drive product reliability and user satisfaction.

**Scope:**
- Target: Android employee app (`com.moveinsync.ets`)
- Data Source: Google Play Store public reviews (10,000+ records)
- Output: Interactive Dashboard, ML Triage Model, and Engineering Action Plan

---

## Quick Start

### Prerequisites
- Python 3.10+
- pip

### Setup

```bash
# Clone / navigate to project
cd moveinsync-fde-case-study

# Install dependencies
pip install -r requirements.txt

# Run the reproducible data pipeline & metrics generation
python src/generate_metrics.py

# Run the test suite
pytest tests/

# Launch the dashboard
streamlit run app/streamlit_app.py
```

---

## Repository Structure

```
moveinsync-fde-case-study/
├── README.md
├── requirements.txt
├── Makefile
├── data/
│   ├── raw/
│   │   ├── google_play_reviews.csv       # 10,144 raw reviews collected
│   │   ├── collection_metadata.json
│   │   └── collection_errors.log
│   └── processed/
│       ├── google_play_reviews_clean.csv # 10,106 cleaned & categorized reviews
│       └── metrics.json                  # Canonical dataset & evaluation metrics
├── models/
│   ├── low_star_classifier.pkl           # Scikit-learn ML pipeline
│   └── model_metadata.json               # Model parameters, fingerprint & metrics
├── notebooks/
│   └── 01_moveinsync_eda_and_ml.ipynb    # Unified EDA and exploration workspace
├── src/
│   ├── generate_metrics.py               # Canonical pipeline for data & ML training
│   └── moveinsync/                       # Reusable package (preprocessing, inference, loader)
├── app/
│   ├── streamlit_app.py                  # Streamlit entry point (Executive overview)
│   ├── utils/data.py                     # Data loaders and caching
│   └── pages/
│       ├── 1_Rating_Analysis.py          # Ratings distribution & monthly trends
│       ├── 2_Complaint_Deep_Dive.py      # Category breakdowns & version trends
│       ├── 3_Review_Explorer.py          # Interactive search & filter tool
│       ├── 4_ML_Model.py                 # Live ML review triage & feature coefficients
│       └── 5_Action_Plan.py              # Prioritized measurement framework & roadmap
├── tests/
│   └── test_moveinsync.py                # 15-area comprehensive test suite (pytest)
├── reports/
│   ├── FINAL_QA_REPORT.md                # Comprehensive verification & QA report
│   ├── final_completion_report.md        # Pipeline completion & audit report
│   ├── ml_model_details.md               # Model methodology, metrics, and limitations
│   └── data_quality_report.md            # Raw data quality audit
└── deliverables/
    ├── MoveInSync_Rating_Recovery_Plan.pptx # Executive presentation
    └── MoveInSync_FDE_Case_Study_Report.docx # Comprehensive report
```

---

## Pipeline Steps

| Step | Script | Input | Output |
|------|--------|-------|--------|
| 1. Collect | `scripts/collect_reviews.py` | Google Play API | `data/raw/google_play_reviews.csv` |
| 2. Canonical Pipeline & ML | `src/generate_metrics.py` | raw CSV | `data/processed/google_play_reviews_clean.csv`, `metrics.json`, `models/*.pkl` |
| 3. Test Suite | `pytest tests/` | processed data & models | 43 test assertions (100% pass) |
| 4. Interactive Dashboard | `streamlit run app/streamlit_app.py` | processed data | Multi-page Streamlit application |

---

## Dashboard

```bash
streamlit run app/streamlit_app.py --server.port 8501
```

Open http://localhost:8501

**Pages:**
1. **Executive Overview** — KPI cards, evidence-based issue hypotheses, and architecture summary.
2. **Rating Analysis** — Rating distribution (1★ to 5★), monthly averages, and volume timeline.
3. **Complaint Deep Dive** — 5-theme breakdown (GPS, Crashes/Login, ETA, Driver Comms, No-Show) and version matrix.
4. **Review Explorer** — Filterable, searchable review table with instant multi-label category filters.
5. **ML Triage Model** — Real-time review text classification with feature coefficients and score gauge.
6. **Action Plan & Roadmap** — 30-day operational sprint with leading indicators and internal data requirements.

---

## Key Findings

1. **GPS / Live Location (1,415 reviews, 57.2% low-star)** — Stale or inaccurate driver location prevents employees from coordinating pickup.
2. **App Crashes & Login/OTP (1,017 reviews, 78.0% low-star)** — Crashes, ANRs, and OTP delivery failures block application access entirely.
3. **Driver Communication (798 reviews, 61.4% low-star)** — Driver call disconnects, rude behavior, or refusal to follow corporate routing.
4. **ETA & Late Pickup (597 reviews, 64.0% low-star)** — Delays causing missed office shifts.
5. **No-Show & Check-in Disputes (132 reviews, 75.0% low-star)** — Employees unjustly marked absent at the gate with no in-app recourse.

---

## Methodology & Verification

- **Collection**: `google-play-scraper` (Python), paginated, NEWEST + MOST_RELEVANT sorts (10,144 unique reviews).
- **Cleaning**: 38 non-informative reviews excluded (text became empty after emoji/punctuation normalization), leaving 10,106 clean records. 2,115 duplicate normalized-text occurrences beyond the first copy were retained for genuine volume analysis but deduplicated prior to ML splitting.
- **Classification**: Transparent multi-label keyword regex engine across 5 operational themes.
- **ML Classifier**: TF-IDF (3,000 features, 1-2 n-grams) + Logistic Regression (`class_weight='balanced'`). Macro F1: 0.843, ROC-AUC: 0.909 (beats baseline Macro F1 of 0.335).
- **Prioritization Framework**: Evidence-based measurement framework replacing speculative rating lift forecasts with leading telemetry indicators.

---

## Limitations

- Public Google Play reviews reflect user-perceived symptoms; internal Crashlytics stack traces, driver-app GPS ping intervals, and FCM delivery receipts are required to confirm root causes.
- The ML classifier was trained exclusively on Play Store reviews for `com.moveinsync.ets`; performance on internal enterprise support tickets or HR surveys has not been validated.
- Model scores are raw logistic regression sigmoid scores and are not calibrated probabilities.

---

## Deliverables

| File | Description |
|------|-------------|
| `deliverables/MoveInSync_Rating_Recovery_Plan.pptx` | Executive presentation |
| `deliverables/MoveInSync_FDE_Case_Study_Report.docx` | Editable comprehensive report |
| `reports/FINAL_QA_REPORT.md` | Verification & QA report |
| `reports/ml_model_details.md` | Model methodology & metrics |
| `reports/data_quality_report.md` | Data quality assessment |
| `app/streamlit_app.py` | Interactive multi-page dashboard |

---

## Regenerating Data & Pipeline

To run the canonical data pipeline and verify model generation:

```bash
python src/generate_metrics.py
```

To run the full test suite:

```bash
pytest tests/
```
