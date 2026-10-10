"""Page 5 - Action Plan and 30-Day Roadmap"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from utils.theme import inject_css, page_hero, section, kpi_card, info_box, apply_legend, PLOT_BASE, MULTI_CAT
from utils.data  import load_reviews

st.set_page_config(page_title="Action Plan - MoveInSync", layout="wide")
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

df = load_reviews()
mean_rating = df["star_rating"].mean() if not df.empty else 3.2

page_hero("Action Plan and 30-Day Roadmap",
          "Specific enough that a product or engineering team could start the next day -- with success metrics, team ownership, and expected rating lift")

# 1. Impact vs Effort
section("01", "Prioritisation -- Impact vs Engineering Effort",
        "Top-left quadrant = quick wins. Start there.")
actions = pd.DataFrame([
    dict(Action="Investigate crashes/OTP",          Impact=9.5, Effort=3, Priority="P1 Critical", Team="Mobile Eng",        Week="Week 1"),
    dict(Action="Investigate GPS poll frequency",   Impact=9.0, Effort=5, Priority="P1 Critical", Team="Backend + Mobile",  Week="Week 1-2"),
    dict(Action="Test OTP fallback channels",       Impact=7.5, Effort=2, Priority="P2 High",     Team="Backend",           Week="Week 2"),
    dict(Action="Assignment status UI",             Impact=7.0, Effort=5, Priority="P2 High",     Team="Product + Backend", Week="Week 2-3"),
    dict(Action="Investigate geofence radii",       Impact=6.5, Effort=6, Priority="P3 Medium",   Team="Product + Backend", Week="Week 3-4"),
    dict(Action="In-app helpdesk",                  Impact=5.5, Effort=7, Priority="P3 Medium",   Team="Product",           Week="Week 4"),
    dict(Action="Reply to all 1-star reviews",      Impact=4.5, Effort=1, Priority="P3 Medium",   Team="Ops",               Week="Ongoing"),
])

color_map = {"P1 Critical": "#ef4444", "P2 High": "#f59e0b", "P3 Medium": "#10b981"}
fig = px.scatter(actions, x="Effort", y="Impact", text="Action",
                 color="Priority", color_discrete_map=color_map, size=[60] * len(actions),
                 hover_data={"Week": True, "Team": True})
fig.update_traces(textposition="top center", textfont=dict(size=10, color="#1e3a5f"),
                  marker=dict(line=dict(width=1.5, color="white")))
fig.update_layout(**PLOT_BASE, height=420, title="Impact vs Engineering Effort -- Prioritisation Matrix")
fig.update_xaxes(title="Engineering Effort (1=low, 10=high)", range=[0, 10.5],
                 gridcolor="rgba(100,150,220,0.12)")
fig.update_yaxes(title="Expected Rating Impact (1=low, 10=high)", range=[3.5, 10.8],
                 gridcolor="rgba(100,150,220,0.12)")
fig.add_hline(y=7.0, line_dash="dot", line_color="rgba(100,150,200,0.3)")
fig.add_vline(x=5.0, line_dash="dot", line_color="rgba(100,150,200,0.3)")
fig.add_annotation(x=2.5, y=10.5, text="Quick Wins", font=dict(color="#059669", size=11), showarrow=False)
fig.add_annotation(x=7.5, y=10.5, text="Strategic",  font=dict(color="#2563eb", size=11), showarrow=False)
apply_legend(fig)
st.plotly_chart(fig, use_container_width=True)

# 2. Rating trajectory
section("02", "Expected Rating Trajectory After Each Fix Wave",
        "Conservative estimate -- assumes 30% of low-star reviews in each category convert to neutral/positive")
lift_labels = ["Now", "Wk 1\nCrashes+GPS", "Wk 2\n+Notifications", "Wk 3\n+Assignment", "Wk 4\nFull 30d"]
lift_vals   = [mean_rating,
               min(mean_rating + 0.30, 5.0),
               min(mean_rating + 0.48, 5.0),
               min(mean_rating + 0.62, 5.0),
               min(mean_rating + 0.80, 5.0)]
marker_colors = ["#ef4444", "#f97316", "#f59e0b", "#22c55e", "#10b981"]

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=lift_labels, y=lift_vals, mode="lines+markers+text",
    line=dict(color="#2563eb", width=3),
    marker=dict(size=12, color=marker_colors, line=dict(width=2, color="white")),
    text=[f"{v:.2f}" for v in lift_vals],
    textposition="top center",
    textfont=dict(color="#1e3a5f", size=12, family="Inter"),
    hovertemplate="%{x}<br><b>%{y:.2f}</b><extra></extra>"))
fig2.add_hrect(y0=4.0, y1=5.0, fillcolor="rgba(16,185,129,0.06)",
               line_width=0, annotation_text="Target zone >= 4.0",
               annotation_position="top right",
               annotation_font=dict(color="#059669", size=11))
fig2.add_hline(y=4.0, line_dash="dash", line_color="#10b981",
               annotation_text="4.0 target", annotation_font=dict(color="#059669"))
fig2.update_layout(**PLOT_BASE, height=320, title="Conservative Rating Lift Forecast")
fig2.update_yaxes(range=[1.0, 5.2], title="Mean Rating", gridcolor="rgba(100,150,220,0.12)")
fig2.update_xaxes(gridcolor="rgba(0,0,0,0)")
st.plotly_chart(fig2, use_container_width=True)

info_box("""
<b>Assumptions:</b> (1) Each fix resolves ~30% of its category low-star reviews.
(2) Fixed users update rating or don't re-review. (3) New review velocity constant.
(4) No regressions introduced. <i>Real lift may differ based on execution quality.</i>
""")

# 3. Sprint plan
section("03", "30-Day Sprint Plan",
        "Specific deliverables per week with team ownership and success metrics")

sprint = [
    ("ESCALATION", "Safety & Ops",
     "<b>Women's Safety & Unsafe Driving.</b> Establish zero-tolerance emergency response.",
     "<ul><li><b>Evidence:</b> Very low volume (<1% of reviews), but 100% 1-star share. Mentions of 'unsafe driving' and 'cab didn't wait'.</li>"
     "<li><b>Confidence:</b> HIGH. Safety issues are critical regardless of volume.</li>"
     "<li><b>Action:</b> Implement an in-app SOS button that rings the command center immediately. Enable driver tracking sharing with emergency contacts.</li></ul>",
     "Zero SOS failures. Resolution under 5 mins."),

    ("Week 1", "Mobile Eng",
     "<b>App Crashes and OTP Failures.</b> Users cannot even log in.",
     "<ul><li><b>Evidence:</b> 15%+ of all reviews mention 'crash', 'login', or 'OTP'. 90% are 1-2 stars.</li>"
     "<li><b>Confidence:</b> HIGH. The review text ('app keeps stopping', 'OTP never arrives') is unambiguous.</li>"
     "<li><b>Action:</b> Integrate Crashlytics to confirm ANR frequency. Investigate testing alternative OTP fallback channels (SMS/WhatsApp) if SMS delivery rates are poor.</li></ul>",
     "Target: Crash-free sessions > 99.5%"),

    ("Week 1-2", "Backend + Mobile",
     "<b>GPS and Live Tracking.</b> Stale locations cause missed cabs.",
     "<ul><li><b>Evidence:</b> 'GPS', 'location', 'tracking' appear in 25%+ of 1-star reviews.</li>"
     "<li><b>Confidence:</b> MEDIUM. Play Store text confirms frustration, but internal telemetry is needed to confirm if it's the app or the OS killing the background service.</li>"
     "<li><b>Action:</b> Collect telemetry on GPS ping intervals. Investigate testing more frequent client-side pings on strict OEMs (Xiaomi, Oppo). Show 'Location updating' badge.</li></ul>",
     "Target: Reduce GPS complaints by 40%"),

    ("Week 2", "Backend + Ops",
     "<b>Vehicle Assignment Silences.</b> Users left waiting without a cab.",
     "<ul><li><b>Evidence:</b> 'No cab assigned' and 'driver cancelled' are frequent 1-star themes.</li>"
     "<li><b>Confidence:</b> HIGH. Users are clear that they get no communication when a driver drops out.</li>"
     "<li><b>Action:</b> Investigate auto-redispatch logic triggers. If no driver, test triggering fallback notifications to user and Ops team.</li></ul>",
     "Target: Zero 'no driver' silent failures"),

    ("Week 3", "Product + Backend",
     "<b>No-Show Disputes.</b> Employees marked absent unfairly.",
     "<ul><li><b>Evidence:</b> 'No show', 'marked absent' correlate strongly with angry 1-star reviews.</li>"
     "<li><b>Confidence:</b> MEDIUM. It's a dispute between driver word and employee word; we lack the GPS logs in these public reviews.</li>"
     "<li><b>Action:</b> Analyze internal geofence hit-rates. Investigate increasing geofence radii conditionally. Add 'Dispute No-Show' button in-app with automated GPS log attach.</li></ul>",
     "Target: Disputes resolved < 4 hours"),
]

for week, team, title, details, metric in sprint:
    st.markdown(
        f"<div class='action-row' style='margin-bottom:1rem; border-left: 4px solid #2563eb; padding-left: 1rem;'>"
        f"<div><div class='action-week' style='font-weight:700; color:#1e3a5f;'>{week}</div>"
        f"<div style='font-size:0.75rem;color:#64748b;margin-top:4px'>{team}</div></div>"
        f"<div class='action-text' style='color:#334155;'>"
        f"<p style='margin:0 0 0.5rem 0; font-size:1rem;'>{title}</p>"
        f"<div style='font-size:0.85rem; line-height:1.4;'>{details}</div>"
        f"</div>"
        f"<div class='action-team' style='min-width:150px;'>"
        f"<div style='font-size:0.7rem;color:#059669;font-weight:700;text-transform:uppercase;'>Measurement</div>"
        f"<div style='font-size:0.8rem;color:#1e3a5f;margin-top:4px;font-weight:500;'>{metric}</div>"
        f"</div></div>",
        unsafe_allow_html=True)

# 4. Methodology
st.markdown("<br>", unsafe_allow_html=True)
section("04", "Methodology and How I Got Here",
        "Transparent summary of tools, pipeline, assumptions, and limitations")

col_a, col_b = st.columns(2)
with col_a:
    info_box("""
    <b>Data Collection</b><br>
    Scraped <b>10,144 public reviews</b> for <code>com.moveinsync.ets</code> from Google Play Store
    using <code>google-play-scraper</code> (Python). No internal data -- fully public.<br><br>
    <b>Cleaning</b><br>
    Deduplicated on review_id. Validated ratings 1-5 only. Parsed dates with UTC normalisation.
    Filtered reviews &lt; 5 chars. Result: 10,144 clean records.<br><br>
    <b>Complaint Classification</b><br>
    Keyword regex across 5 themes: GPS, Crashes/Login, ETA, Driver Communication, No-Show.
    Transparent, auditable, no black box.
    """)

with col_b:
    info_box("""
    <b>ML Model</b><br>
    TF-IDF (3000 features, 1-2 n-grams) + Logistic Regression (balanced class weights).
    Trained on 80% stratified split with identical review text removed.<br><br>
    <b>Key Assumptions</b><br>
    -- Play Store reviews are a representative but biased sample<br>
    -- Root causes are hypothesised from symptoms; internal Crashlytics and GPS logs would confirm<br>
    -- Rating lift forecasts are conservative linear estimates<br><br>
    <b>Tools Used</b><br>
    google-play-scraper &middot; pandas &middot; scikit-learn &middot; Plotly &middot; Streamlit &middot; Jupyter
    """)

# Download
st.markdown("<br>", unsafe_allow_html=True)
import io
import re as _re

try:
    import docx

    doc = docx.Document()
    doc.add_heading('MoveInSync - 30-Day Action Plan', 0)

    for w, t, a, m in sprint:
        action_text = _re.sub(r"<[^>]+>", "", a).replace("&middot;", ".").replace("&gt;", ">").replace("&lt;", "<")
        metric_text = _re.sub(r"<[^>]+>", "", m).replace("&middot;", ".").replace("&gt;", ">").replace("&lt;", "<")
        
        doc.add_heading(f"{w} ({t})", level=2)
        doc.add_paragraph(action_text)
        p = doc.add_paragraph()
        p.add_run('Success Metric: ').bold = True
        p.add_run(metric_text)

    bio = io.BytesIO()
    doc.save(bio)

    st.download_button(
        label="Download Action Plan (Word)",
        data=bio.getvalue(),
        file_name="moveinsync_30day_action_plan.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
except ImportError:
    st.warning("python-docx is not installed. Please run `pip install python-docx` to enable Word export.")
