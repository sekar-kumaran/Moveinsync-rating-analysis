"""
streamlit_app.py -- Entry point / Home page
MoveInSync FDE Case Study Dashboard
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
from utils.theme import inject_css, page_hero, section, kpi_card, card, info_box
from utils.data  import load_reviews, rating_distribution, category_stats, monthly_stats

st.set_page_config(
    page_title="MoveInSync -- Rating Intelligence",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 0.5rem">
      <div style="font-size:2rem">🚌</div>
      <div style="font-size:1.1rem;font-weight:800;color:#fff">MoveInSync</div>
      <div style="font-size:0.75rem;color:#93c5fd;margin-top:2px">Rating Intelligence &middot; FDE Case Study</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<p style='font-size:0.7rem;letter-spacing:.1em;text-transform:uppercase;color:#93c5fd;margin-bottom:0.5rem'>Navigation</p>", unsafe_allow_html=True)
    st.page_link("streamlit_app.py",           label="Home -- Executive Summary")
    st.page_link("pages/1_Rating_Analysis.py",  label="Rating & Trend Analysis")
    st.page_link("pages/2_Complaint_Deep_Dive.py", label="Complaint Deep Dive")
    st.page_link("pages/3_Review_Explorer.py",  label="Review Explorer")
    st.page_link("pages/4_ML_Model.py",         label="ML Triage Model")
    st.page_link("pages/5_Action_Plan.py",      label="Action Plan & Roadmap")
    st.markdown("---")
    st.markdown("<p style='font-size:0.72rem;color:#93c5fd'>App: <code style='color:#60a5fa'>com.moveinsync.ets</code><br>Source: Google Play Store<br>Analysis: FDE Candidate</p>", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────
import json

metrics_path = Path("data/processed/metrics.json")
if not metrics_path.exists():
    st.error("No metrics data found. Please run `python src/generate_metrics.py` first.")
    st.stop()

with open(metrics_path, "r") as f:
    full_data = json.load(f)
    if "dataset" not in full_data:
        st.error("Metrics artifact is malformed. Please run `python src/generate_metrics.py`.")
        st.stop()
    metrics = full_data["dataset"]

df = load_reviews()
if df.empty:
    st.error("No processed data found.")
    st.stop()

rd    = rating_distribution(df)
m     = monthly_stats(df)

# ── Hero ──────────────────────────────────────────────────────
page_hero(
    "Play Store Rating Intelligence Dashboard",
    "MoveInSync FDE Assignment &middot; Why are our ratings low -- and exactly what do we fix first?"
)

# ── KPI Row ───────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
kpi_card(c1, f"{metrics['clean_reviews']:,}", "Reviews Analysed", "Google Play &middot; public", "neu", "blue")
kpi_card(c2, f"{metrics['mean_rating']:.2f}&#9733;", "Mean Rating", "Below 4.0 target", "bad", "red")
kpi_card(c3, f"{metrics['low_star_share']*100:.1f}%", "1&#9733; & 2&#9733; Share", "Primary focus", "bad", "red")
kpi_card(c4, f"{(df['star_rating']==5).mean()*100:.1f}%", "5&#9733; Share",  "Promoter base",  "good","green")
kpi_card(c5, f"{df['developer_reply'].notna().mean()*100:.1f}%", "Dev Reply Rate", "Engagement gap", "bad","violet")

st.markdown("<br>", unsafe_allow_html=True)

# ── Two-column summary ────────────────────────────────────────
import plotly.express as px
import plotly.graph_objects as go
from utils.theme import PLOT_BASE, RATING_COLORS, RATING_LIST, apply_axes, apply_legend

left, right = st.columns([1.1, 1])

with left:
    section("&#9733;", "Rating Distribution", "How reviews split across 1-5 stars")
    fig = go.Figure(go.Bar(
        x=rd["Rating"], y=rd["Count"],
        marker_color=RATING_LIST,
        text=[f"{p}%" for p in rd["Pct"]],
        textposition="outside",
        textfont=dict(color="#334155", size=11),
        hovertemplate="<b>%{x}&#9733;</b> -- %{y:,} reviews (%{text})<extra></extra>",
    ))
    fig.update_layout(**PLOT_BASE, height=290, title="Rating Distribution")
    apply_axes(fig, x_title="Stars", y_title="Reviews")
    st.plotly_chart(fig, use_container_width=True)

with right:
    section("▲", "Rating Trend", "Mean rating each month -- the red line must go up")
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=m["year_month"], y=m["count"], name="Volume",
                          marker_color="rgba(37,99,235,0.25)",
                          hovertemplate="%{x|%b %Y}<br>%{y} reviews<extra></extra>", yaxis="y1"))
    fig2.add_trace(go.Scatter(x=m["year_month"], y=m["avg_rating"], name="Mean Rating",
                              line=dict(color="#2563eb", width=2.5), mode="lines+markers",
                              marker=dict(size=5),
                              hovertemplate="%{x|%b %Y}<br>Avg: %{y:.2f}&#9733;<extra></extra>", yaxis="y2"))
    fig2.update_layout(**PLOT_BASE, height=290, title="Monthly Volume & Mean Rating",
                       yaxis=dict(title="Reviews", gridcolor="rgba(100,150,220,0.12)"),
                       yaxis2=dict(title="Mean &#9733;", overlaying="y", side="right",
                                   range=[1,5], gridcolor="rgba(0,0,0,0)",
                                   tickfont=dict(color="#2563eb")))
    apply_legend(fig2)
    fig2.update_xaxes(tickformat="%b %Y", tickangle=-40, tickfont=dict(color="#64748b", size=10))
    st.plotly_chart(fig2, use_container_width=True)

# ── Top Issues ────────────────────────────────────────────────
section("!", "Top Issues Driving 1-Star Reviews",
        "Root-cause categories ranked by frequency in low-star feedback")

findings = [
    ("badge-p1","P1 — Critical","Crashes, Blank Screen & OTP Failures","p1",
     "<b>Evidence:</b> 'crash', 'login', 'OTP' appear in 1,017 reviews (~10% of all). 78% of those are 1–2★. "
     "Review text is unambiguous: 'app keeps stopping', 'OTP never arrives', 'blank screen on launch'.<br><br>"
     "<b>Hypothesis:</b> Top ANR paths and OTP delivery failures are likely culprits, but the specific stack traces and "
     "OTP delivery rates require Crashlytics and telemetry to confirm.<br><br>"
     "<b>Next action:</b> Deploy Crashlytics; obtain crash rate and top ANR reports. "
     "Investigate OTP delivery rates — if below threshold, evaluate fallback channels.",
     "Metric: Crash-free session rate | Data needed: Crashlytics, OTP delivery logs"),
    ("badge-p1","P1 — Critical","GPS & Live Location Stale or Wrong","p1",
     "<b>Evidence:</b> 'GPS', 'location', 'tracking' appear in 1,415 reviews (~14%). 57% are 1–2★. "
     "Users report driver shown far away while he is physically present, or tracking freezing mid-trip.<br><br>"
     "<b>Hypothesis:</b> Location may be stale due to infrequent driver-app pings or OS battery restrictions "
     "killing the background location service. Root cause requires driver-app telemetry — cannot be determined from public reviews alone.<br><br>"
     "<b>Next action:</b> Pull driver-app GPS log timestamps; measure median location staleness. "
     "If pings are infrequent, test increased frequency on a pilot cohort and compare OEM (Xiaomi, Oppo) behavior.",
     "Metric: Median location staleness (sec) | Data needed: Driver-app telemetry (internal)"),
    ("badge-p2","P2 — High","Silent Notifications — Cab Arrives Unannounced","p2",
     "<b>Evidence:</b> Reviews mention 'no notification', 'missed cab', 'no alert'. Concentrated in 2023–2024 reviews coinciding with stricter Android battery restrictions.<br><br>"
     "<b>Hypothesis:</b> Android Doze mode and OEM battery savers are suppressing push notifications. "
     "Without SMS fallback, employees receive no alert. Cause may be FCM priority configuration.<br><br>"
     "<b>Next action:</b> Audit FCM message priority settings. Test notification delivery on top 5 OEM battery-saver configurations. "
     "Evaluate SMS fallback for 'Cab Arrived' event only.",
     "Metric: Notification delivery rate | Data needed: FCM delivery receipts (internal)"),
    ("badge-p2","P2 — High","No Driver Assigned After Booking Confirmed","p2",
     "<b>Evidence:</b> 'no driver', 'driver cancelled', 'no cab assigned' are frequent 1★ themes. "
     "Users report booking confirmed but entering silent waiting with no communication or ETA.<br><br>"
     "<b>Hypothesis:</b> Assignment failure handling does not communicate state to the user. "
     "Exact root cause (driver pool shortage vs. assignment logic) requires internal booking data.<br><br>"
     "<b>Next action:</b> Surface real-time assignment state in the user-facing UI. "
     "Investigate auto re-dispatch trigger timing. Measure booking → driver-confirmed rate.",
     "Metric: Booking → driver-confirmed rate | Data needed: Booking system logs (internal)"),
    ("badge-p3","P3 — Medium","No-Show Disputes with No In-App Resolution","p3",
     "<b>Evidence:</b> 'no show', 'marked absent' appear in 132 reviews. 75% are 1–2★. "
     "Employees say they were present at pickup but still marked absent.<br><br>"
     "<b>Hypothesis:</b> Geofence may be too tight for urban pickup scenarios, or driver-side GPS is inaccurate at the moment of check-in. "
     "The exact current geofence radius and hit-rate data are not available from public reviews.<br><br>"
     "<b>Next action:</b> Obtain geofence check logs and analyze hit-rate vs. actual GPS positions at pickup time. "
     "If systematic mismatch is found, consider adjusting radius or requiring driver to be in zone for a minimum duration.",
     "Metric: No-show disputes per 1,000 trips | Data needed: Geofence check logs, GPS at pickup (internal)"),
    ("badge-p3","P3 — Medium","Support Is a Dead End","p3",
     "<b>Evidence:</b> Multiple reviews say submitted tickets go unresolved. "
     "Developer response rate in the collected dataset is low. One unresolved bad trip often becomes a permanent 1★.<br><br>"
     "<b>Hypothesis:</b> No in-app support channel forces users to external channels (email), reducing resolution rates.<br><br>"
     "<b>Next action:</b> Reply to every 1★ Play Store review within 24 hours. "
     "Evaluate embedding a lightweight in-app ticket flow (Freshdesk/Zendesk) for trip-specific disputes.",
     "Metric: % of 1★ reviews with developer reply | Data needed: Play Store Developer Console"),
]

col_a, col_b = st.columns(2)
for i, (badge_cls, badge_lbl, title, p_cls, body, fix) in enumerate(findings):
    with (col_a if i % 2 == 0 else col_b):
        card(badge_cls, badge_lbl, title, body, fix, p_cls)

# ── Bottom CTA ────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
info_box("""
<b>Use the sidebar to navigate:</b>
&nbsp; <b>Rating &amp; Trend Analysis</b> for deep time-series charts &middot;
<b>Complaint Deep Dive</b> for category heatmaps &amp; evidence &middot;
<b>Review Explorer</b> to search raw feedback &middot;
<b>ML Triage Model</b> for the classifier &amp; live inference &middot;
<b>Action Plan</b> for the 30-day sprint roadmap.
""")
