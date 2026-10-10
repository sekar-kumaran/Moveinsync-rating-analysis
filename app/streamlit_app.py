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
    ("badge-p1","P1 -- Critical","Crashes, Blank Screen & OTP Failures","p1",
     "The biggest driver of 1-star reviews. Users can't open the app or complete login -- OTP doesn't arrive, the splash screen freezes, or the app hits an ANR.",
     "Deploy Crashlytics now. Fix top 3 ANR paths. Add SMS/WhatsApp OTP fallback. Target: >99.5% crash-free sessions."),
    ("badge-p1","P1 -- Critical","GPS & Live Location Stale or Wrong","p1",
     "Users see the driver shown 2 km away while he's at the gate. Every missed pickup generates a 1-star review immediately.",
     "Reduce driver ping from 30s -> 5s. Add 'Location updating...' indicator. Use client-side dead-reckoning between pings."),
    ("badge-p2","P2 -- High","Silent Notifications -- Cab Arrives Unannounced","p2",
     "Android Doze and OEM battery savers silently kill push delivery. No SMS fallback = no safety net. Employee misses cab, writes 1-star.",
     "Add SMS fallback for 'Cab Arrived'. Use FCM high-priority channel. Test on top 5 OEM battery-saver configs."),
    ("badge-p2","P2 -- High","No Driver Assigned After Booking Confirmed","p2",
     "Booking shows success, then infinite 'no driver available' limbo with zero communication or ETA.",
     "Show live assignment state in UI. Auto re-dispatch if no driver 20 min before shift + push notification."),
    ("badge-p3","P3 -- Medium","No-Show Disputes with No In-App Resolution","p3",
     "Employees marked absent at the gate. Geofence is too tight. No way to dispute inside the app.",
     "Expand geofence 50m->150m. Require 2 min in zone before marking absent. Add in-app 'Dispute' button."),
    ("badge-p3","P3 -- Medium","Support Is a Dead End","p3",
     "Multiple reviews say tickets go unresolved. One bad trip becomes a permanent 1-star with no repair path.",
     "Integrate Freshdesk/Zendesk in-app. Show ticket status. Reply every 1-star Play Store review within 24h."),
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
