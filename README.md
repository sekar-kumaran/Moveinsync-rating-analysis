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

# Launch the dashboard
streamlit run app/streamlit_app.py
```

Or using Make (Linux/Mac):
```bash
make install
make dashboard
```

---

## Repository Structure

```
moveinsync-fde-case-study/
├── README.md
├── requirements.txt
├── Makefile
├── data/
│   ├── raw/                          # Raw collected reviews (do not modify)
│   │   ├── google_play_reviews.csv
│   │   ├── collection_metadata.json
│   │   └── collection_errors.log
│   ├── processed/                    # Cleaned and classified data
│   │   ├── google_play_reviews_clean.csv
│   │   ├── google_play_reviews_classified.csv
│   │   ├── analysis_summary.json
│   │   └── dashboard_*.json
│   └── sample/                       # Anonymized sample for redistribution
│       └── google_play_reviews_sample.csv
├── notebooks/
│   └── 01_exploratory_data_analysis.ipynb
├── src/
│   ├── collect_reviews.py            # Data collection pipeline
│   ├── clean_reviews.py              # Data cleaning & validation
│   ├── classify_reviews.py           # Review classification
│   ├── analyze_reviews.py            # EDA & chart generation
│   └── build_dashboard_data.py       # Dashboard data prep
├── app/
│   └── streamlit_app.py              # Interactive dashboard (4 pages)
├── reports/
│   ├── data_quality_report.md
│   └── figures/                      # All generated charts (PNG)
├── deliverables/
│   ├── MoveInSync_FDE_Case_Study.pptx
│   ├── MoveInSync_FDE_Case_Study_Report.pdf
│   └── MoveInSync_FDE_Case_Study_Report.docx
└── tests/
    └── test_pipeline.py
```

---

## Pipeline Steps

| Step | Script | Input | Output |
|------|--------|-------|--------|
| 1. Collect | `scripts/collect_reviews.py` | Google Play API | `data/raw/google_play_reviews.csv` |
| 2. Generate Metrics & ML | `src/generate_metrics.py` | raw CSV | `data/processed/metrics.json`, `clean.csv`, `models/*.pkl` |
| 3. Dashboard | `app/streamlit_app.py` | processed data | Interactive web app |

---

## Dashboard

```bash
streamlit run app/streamlit_app.py --server.port 8501
```

Open http://localhost:8501

**Pages:**
- Executive Overview — KPIs, key findings
- Ratings & Trends — Rating distribution, monthly trends
- Complaint Analysis — Category frequency, heatmap, searchable excerpts
- Product Action Tracker — Prioritized backlog, 30-day roadmap

---

## Key Findings

1. **GPS / Live Location** — Most frequently mentioned in 1★ reviews. Stale or wrong location prevents employees from coordinating pickup.
2. **App Crashes & Login** — Crashes, ANRs, and OTP failures prevent access entirely.
3. **Push Notifications** — Missed cab arrival alerts; no SMS fallback.
4. **Vehicle Assignment** — Silent failures when no driver is available.
5. **No-show Disputes** — Employees marked absent with no in-app recourse.

---

## Methodology

- **Collection**: `google-play-scraper` (Python), paginated, NEWEST + MOST_RELEVANT sorts, deduplicated
- **Classification**: Transparent keyword rule engine (multi-label, auditable)
- **EDA**: Pandas, Matplotlib, Seaborn, Plotly
- **Dashboard**: Streamlit + Plotly
- **Prioritization**: Severity × Frequency × Confidence model, adjusted for effort

---

## Limitations

- `google-play-scraper` provides access to a rolling window of publicly visible reviews. The complete historical dataset may not be accessible.
- Review counts may not represent the full population (sampling bias toward recent/relevant reviews).
- Keyword-based classification has recall/precision tradeoffs; validated on a manual subset.
- No access to internal telemetry, crash logs, or operational data — root causes are hypotheses requiring internal validation.
- Android and iOS data are kept separate. This project covers Android only.

---

## Deliverables

| File | Description |
|------|-------------|
| `deliverables/MoveInSync_FDE_Case_Study.pptx` | 12-slide presentation |
| `deliverables/MoveInSync_FDE_Case_Study_Report.pdf` | Full report (PDF) |
| `deliverables/MoveInSync_FDE_Case_Study_Report.docx` | Editable report (DOCX) |
| `reports/data_quality_report.md` | Data quality assessment |
| `reports/figures/` | All EDA charts |
| `app/streamlit_app.py` | Interactive dashboard |

---

## Regenerating Data

If raw review text cannot be redistributed, run the collection pipeline to regenerate:

```bash
python src/collect_reviews.py --app-id com.moveinsync.ets
```

The pipeline is idempotent and deduplicates by review ID.

---

*Built for the MoveInSync Forward Deployed Engineer candidate assignment.*
