"""Page 4 - ML Triage Classifier: metrics, feature importance, live inference."""
import sys, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

from utils.theme import inject_css, page_hero, section, info_box, kpi_card, PLOT_BASE
from utils.data  import load_reviews, load_model

st.set_page_config(page_title="ML Model - MoveInSync", layout="wide")
inject_css()

with st.sidebar:
    st.markdown(
        "<div style='text-align:center;padding:.8rem 0 0.5rem'>"
        "<div style='font-weight:800;color:#fff;font-size:1.15rem'>MoveInSync</div>"
        "<div style='color:#93c5fd;font-size:0.72rem;margin-top:2px'>FDE Case Study</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.page_link("streamlit_app.py",               label="Home - Executive Summary")
    st.page_link("pages/1_Rating_Analysis.py",     label="Rating and Trend Analysis")
    st.page_link("pages/2_Complaint_Deep_Dive.py", label="Complaint Deep Dive")
    st.page_link("pages/3_Review_Explorer.py",     label="Review Explorer")
    st.page_link("pages/4_ML_Model.py",            label="ML Triage Model")
    st.page_link("pages/5_Action_Plan.py",         label="Action Plan and Roadmap")

df             = load_reviews()
pipeline, meta = load_model()

page_hero("ML Triage Classifier",
          "TF-IDF + Logistic Regression trained to predict low-star reviews from free-text -- enabling automatic severity triage of support tickets")

if pipeline is None:
    st.warning("Model not found. Run python src/generate_metrics.py first.")
    st.stop()

# Metric KPIs
section("M", "Model Performance Metrics", "Evaluated on held-out test set -- never seen during training")
c1, c2, c3, c4 = st.columns(4)
kpi_card(c1, f"{meta.get('roc_auc', 0):.3f}",  "ROC-AUC Score",     "1.0 = perfect",     "good", "blue")
kpi_card(c2, f"{meta.get('f1_macro', 0):.3f}", "F1-Macro",          "Balanced accuracy metric", "good", "teal")
kpi_card(c3, f"{meta.get('ml_test_size', 0):,}",  "Test Set Size",     "Samples evaluated on", "neu",  "violet")
kpi_card(c4, meta.get("split_strategy", "Random"), "Split Strategy", "To prevent text leakage", "neu",  "green")
st.markdown("<br>", unsafe_allow_html=True)

info_box("""
<b>What the model does:</b> Given any free-text (review, support ticket, feedback form),
it predicts whether that text implies a 1-star or 2-star experience.<br><br>
<b>Why it matters:</b> Employees sometimes submit internal HR feedback without a star rating.
This classifier can <b>auto-flag severe negative experiences</b> for immediate ops triage --
before they become a Play Store 1-star review.
""")

# Feature importance
section("F", "Most Influential Words",
        "Top TF-IDF features by Logistic Regression coefficient -- what language predicts bad vs good")
try:
    clf        = pipeline.named_steps["clf"]
    tfidf      = pipeline.named_steps["tfidf"]
    feat_names = np.array(tfidf.get_feature_names_out())
    coefs      = clf.coef_[0]
    n = 18

    top_neg = np.argsort(coefs)[-n:]   # high coef = predicts LOW-STAR
    top_pos = np.argsort(coefs)[:n]    # low coef  = predicts HIGH-STAR

    col_a, col_b = st.columns(2)
    with col_a:
        max_c = max(abs(coefs))
        alphas = [min(1, 0.4 + abs(v) / max_c * 0.6) for v in coefs[top_neg]]
        fig = go.Figure(go.Bar(
            x=coefs[top_neg], y=feat_names[top_neg], orientation="h",
            marker_color=[f"rgba(239,68,68,{a:.2f})" for a in alphas],
            hovertemplate="<b>%{y}</b><br>Coefficient: %{x:.3f}<extra></extra>"))
        fig.update_layout(**PLOT_BASE, height=480, title="Words Predicting LOW-STAR Review")
        fig.update_xaxes(title="LR Coefficient", gridcolor="rgba(100,150,220,0.12)")
        fig.update_yaxes(tickfont=dict(color="#334155", size=11))
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        alphas2 = [min(1, 0.4 + abs(v) / max_c * 0.6) for v in coefs[top_pos][::-1]]
        fig2 = go.Figure(go.Bar(
            x=coefs[top_pos][::-1], y=feat_names[top_pos][::-1], orientation="h",
            marker_color=[f"rgba(16,185,129,{a:.2f})" for a in alphas2],
            hovertemplate="<b>%{y}</b><br>Coefficient: %{x:.3f}<extra></extra>"))
        fig2.update_layout(**PLOT_BASE, height=480, title="Words Predicting HIGH-STAR Review")
        fig2.update_xaxes(title="LR Coefficient", gridcolor="rgba(100,150,220,0.12)")
        fig2.update_yaxes(tickfont=dict(color="#334155", size=11))
        st.plotly_chart(fig2, use_container_width=True)

except Exception as e:
    st.warning(f"Could not extract feature importance: {e}")

# Confidence distribution
section("C", "Prediction Confidence Distribution",
        "How confident is the model on a 500-review sample -- well-calibrated models peak near 0 and 1")
if not df.empty:
    try:
        sample = df.dropna(subset=["clean_text"]).sample(min(500, len(df)), random_state=42)
        probs  = pipeline.predict_proba(sample["clean_text"])[:, 1]
        labels = sample["is_low_star"].values
        fig3 = go.Figure()
        fig3.add_trace(go.Histogram(x=probs[labels == 1], name="Actual Low-Star",
                                    marker_color="rgba(239,68,68,0.65)", nbinsx=30,
                                    hovertemplate="P=%{x:.2f}<br>Count=%{y}<extra></extra>"))
        fig3.add_trace(go.Histogram(x=probs[labels == 0], name="Actual High-Star",
                                    marker_color="rgba(16,185,129,0.55)", nbinsx=30,
                                    hovertemplate="P=%{x:.2f}<br>Count=%{y}<extra></extra>"))
        fig3.update_layout(**PLOT_BASE, barmode="overlay", height=300,
                           title="Predicted P(Low-Star) -- 500 review sample")
        fig3.update_xaxes(title="P(low-star)", range=[0, 1], gridcolor="rgba(100,150,220,0.12)")
        fig3.update_yaxes(title="Count", gridcolor="rgba(100,150,220,0.12)")
        fig3.update_layout(legend=dict(bgcolor="rgba(255,255,255,0.8)", borderwidth=1,
                                       bordercolor="rgba(100,150,220,0.2)"))
        st.plotly_chart(fig3, use_container_width=True)
    except Exception:
        pass

# Live Inference
section("L", "Live Inference -- Try It Yourself",
        "Type any feedback or support ticket text and the model predicts severity")

examples = [
    "Select an example...",
    "The app keeps crashing whenever I try to book a cab. OTP never arrives and I'm always late.",
    "GPS shows my driver 5 km away but he was already at my gate. I missed the cab.",
    "Excellent experience, the cab was on time and driver was very polite!",
    "I booked successfully but no driver was ever assigned. Waited 45 minutes.",
]
chosen = st.selectbox("Quick examples (or type your own below)", examples)

review_input = st.text_area(
    "Paste review / feedback / support ticket text here:",
    value="" if chosen == "Select an example..." else chosen,
    height=120,
    placeholder="e.g. App crashed during OTP entry, missed my cab to work. This has happened 3 times."
)

if st.button("Predict Severity", type="primary"):
    if not review_input.strip():
        st.warning("Please enter some text.")
    else:
        with st.spinner("Running inference..."):
            from moveinsync.inference import predict_low_star
            result = predict_low_star(review_input)
            
        if result["error"]:
            st.error(result["error"])
        else:
            is_low = result["is_low_star"]
            low_prob = result["confidence"] if is_low else 1 - result["confidence"]
            
            col_res, col_detail = st.columns([1, 2])
            with col_res:
                if is_low:
                    st.markdown(
                        f"<div class='predict-low'>"
                        f"<div class='predict-label' style='color:#dc2626'>LOW-STAR SIGNAL</div>"
                        f"<div class='predict-sub' style='color:#7f1d1d'>Predicts a 1 or 2 star experience"
                        f"<br><b>{low_prob*100:.1f}% confidence</b></div></div>",
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        f"<div class='predict-high'>"
                        f"<div class='predict-label' style='color:#15803d'>POSITIVE SIGNAL</div>"
                        f"<div class='predict-sub' style='color:#14532d'>Predicts a 3-5 star experience"
                        f"<br><b>{(1-low_prob)*100:.1f}% confidence</b></div></div>",
                        unsafe_allow_html=True)

        with col_detail:
            st.markdown("<br>", unsafe_allow_html=True)
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=low_prob * 100,
                number=dict(suffix="%", font=dict(size=28, color="#1e3a5f")),
                gauge=dict(
                    axis=dict(range=[0, 100], tickwidth=1, tickcolor="#64748b"),
                    bar=dict(color="#ef4444" if is_low else "#10b981"),
                    bgcolor="rgba(241,245,249,0.8)",
                    steps=[
                        dict(range=[0, 40], color="rgba(16,185,129,0.12)"),
                        dict(range=[40, 60], color="rgba(245,158,11,0.12)"),
                        dict(range=[60, 100], color="rgba(239,68,68,0.12)"),
                    ],
                    threshold=dict(line=dict(color="#ef4444", width=2),
                                   thickness=0.75, value=60),
                ),
                title=dict(text="P(Low-Star)", font=dict(color="#1e3a5f")),
            ))
            fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                                    height=220, margin=dict(t=30, b=10, l=10, r=10))
            st.plotly_chart(fig_gauge, use_container_width=True)
