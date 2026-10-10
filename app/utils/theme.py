"""Shared theme: CSS injection, helper HTML builders, Plotly layout defaults."""
import streamlit as st

# ── Plotly chart base layout (light theme) ───────────────────
PLOT_BG   = "rgba(255,255,255,0)"
GRID_COL  = "rgba(100,150,220,0.12)"
AXIS_COL  = "rgba(100,150,220,0.25)"
TEXT_COL  = "#334155"
TITLE_COL = "#1e3a5f"

PLOT_BASE = dict(
    paper_bgcolor=PLOT_BG,
    plot_bgcolor="rgba(255,255,255,0.7)",
    font=dict(family="Inter, sans-serif", color=TEXT_COL, size=12),
    title_font=dict(family="Inter, sans-serif", color=TITLE_COL, size=15, ),
    margin=dict(t=48, b=32, l=16, r=16),
)

def apply_axes(fig, x_title="", y_title="", x_range=None, y_range=None, tickangle=0):
    kw_x = dict(gridcolor=GRID_COL, linecolor=AXIS_COL, tickfont=dict(color="#64748b"), title=x_title, tickangle=tickangle)
    kw_y = dict(gridcolor=GRID_COL, linecolor=AXIS_COL, tickfont=dict(color="#64748b"), title=y_title)
    if x_range: kw_x["range"] = x_range
    if y_range: kw_y["range"] = y_range
    fig.update_xaxes(**kw_x)
    fig.update_yaxes(**kw_y)
    return fig

def apply_legend(fig, orientation="h", y=-0.18, x=0.5, xanchor="center"):
    fig.update_layout(legend=dict(
        bgcolor="rgba(255,255,255,0.6)",
        bordercolor=AXIS_COL,
        borderwidth=1,
        font=dict(color=TEXT_COL),
        orientation=orientation, y=y, x=x, xanchor=xanchor,
    ))
    return fig

# ── Color palettes ────────────────────────────────────────────
RATING_COLORS = {1: "#ef4444", 2: "#f97316", 3: "#f59e0b", 4: "#22c55e", 5: "#10b981"}
RATING_LIST   = ["#ef4444", "#f97316", "#f59e0b", "#22c55e", "#10b981"]
BLUE_SEQ      = ["#dbeafe", "#93c5fd", "#3b82f6", "#1d4ed8", "#1e3a8a"]
TEAL_SEQ      = ["#ccfbf1", "#5eead4", "#14b8a6", "#0d9488", "#0f766e"]
MULTI_CAT     = ["#2563eb", "#0891b2", "#7c3aed", "#db2777", "#ea580c"]

# ── Shared CSS ────────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Background ─────────────────────── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
.stApp {
    font-family: 'Inter', sans-serif !important;
    background: linear-gradient(160deg,
        #ffffff 0%,
        #dbeafe 35%,
        #e0f2fe 65%,
        #f0fdf4 100%) !important;
}
[data-testid="stAppViewContainer"] > .main > div > div {
    background: transparent !important;
}

/* ── Sidebar ─────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e3a8a 0%, #1e40af 45%, #0e7490 100%) !important;
    border-right: none !important;
}

/* Force ALL sidebar text to white — beats config.toml textColor */
[data-testid="stSidebar"],
[data-testid="stSidebar"] *,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] a,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] * {
    color: #e2eeff !important;
}

/* Headings in sidebar — brighter white */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] strong {
    color: #ffffff !important;
}

/* HR divider */
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.18) !important;
}

/* ── Hide Streamlit's auto-generated nav ── */
[data-testid="stSidebarNav"],
[data-testid="stSidebarNavItems"],
[data-testid="stSidebarNavSeparator"] {
    display: none !important;
}

/* ── Page link items in sidebar ── */
[data-testid="stSidebar"] [data-testid="stPageLink"],
[data-testid="stSidebar"] [data-testid="stPageLink"] *,
[data-testid="stSidebar"] [data-testid="stPageLink"] p,
[data-testid="stSidebar"] [data-testid="stPageLink"] span,
[data-testid="stSidebar"] [data-testid="stPageLink"] div {
    color: #c7d9fb !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    text-decoration: none !important;
    transition: all 0.15s !important;
}

/* Active / current page link */
[data-testid="stSidebar"] [data-testid="stPageLink"][aria-current="page"],
[data-testid="stSidebar"] [data-testid="stPageLink"][aria-current="page"] *,
[data-testid="stSidebar"] [data-testid="stPageLink"][aria-current="page"] p,
[data-testid="stSidebar"] [data-testid="stPageLink"][aria-current="page"] span {
    color: #ffffff !important;
    font-weight: 700 !important;
    background: rgba(255,255,255,0.15) !important;
    border-radius: 8px !important;
}

/* Hover */
[data-testid="stSidebar"] [data-testid="stPageLink"]:hover,
[data-testid="stSidebar"] [data-testid="stPageLink"]:hover * {
    color: #ffffff !important;
    background: rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
}

/* ── Remove chrome ───────────────────── */
#MainMenu, footer, header { visibility: hidden; }

/* ═══════════════════════════════════════════════════
   GLOBAL TEXT COLOR — overrides all white-on-white
   ═══════════════════════════════════════════════════ */

/* Base text in the main area */
.main, .main *,
[data-testid="stMainBlockContainer"], [data-testid="stMainBlockContainer"] *,
[data-testid="block-container"], [data-testid="block-container"] * {
    color: #1e3a5f;
}

/* Paragraphs, spans, divs */
.main p, .main span, .main div,
.main label, .main li, .main td, .main th {
    color: #334155 !important;
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
    color: #1e3a5f !important;
    font-family: 'Inter', sans-serif !important;
}

/* Streamlit-specific text elements */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] strong,
[data-testid="stMarkdownContainer"] em,
[data-testid="stMarkdownContainer"] a {
    color: #334155 !important;
}

/* st.caption */
[data-testid="stCaptionContainer"] p,
.stCaption, small {
    color: #64748b !important;
}

/* st.metric */
[data-testid="stMetricLabel"] p,
[data-testid="stMetricLabel"] {
    color: #475569 !important;
    font-size: 0.82rem !important;
}
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] * {
    color: #1e3a5f !important;
    font-weight: 800 !important;
}
[data-testid="stMetricDelta"] {
    color: #64748b !important;
}

/* Expander title & content */
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span {
    color: #1e3a5f !important;
    font-weight: 600 !important;
}
[data-testid="stExpander"] [data-testid="stMarkdownContainer"] p {
    color: #334155 !important;
}

/* st.selectbox / multiselect / text_input labels */
label, .stSelectbox label, .stMultiSelect label,
.stTextInput label, .stTextArea label,
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] {
    color: #1e3a5f !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}

/* Select box & input text */
[data-baseweb="select"] div,
[data-baseweb="input"] input {
    color: #1e3a5f !important;
    background: #ffffff !important;
}
textarea { color: #1e3a5f !important; }

/* Multiselect tags */
[data-baseweb="tag"] span { color: #1e40af !important; }

/* Table / dataframe */
[data-testid="stDataFrame"] * { color: #1e3a5f !important; }

/* st.number_input */
[data-testid="stNumberInput"] input { color: #1e3a5f !important; }

/* Download button */
[data-testid="stDownloadButton"] button {
    color: #ffffff !important;
    background: linear-gradient(135deg, #2563eb, #0891b2) !important;
    border: none !important;
    font-weight: 600 !important;
}

/* Primary button */
[data-testid="stButton"] button[kind="primary"] {
    color: #ffffff !important;
    background: linear-gradient(135deg, #2563eb, #0891b2) !important;
    border: none !important;
    font-weight: 600 !important;
}
[data-testid="stButton"] button[kind="secondary"] {
    color: #1e3a5f !important;
    border-color: rgba(37,99,235,0.3) !important;
}

/* Warning / info / error boxes */
[data-testid="stAlert"] p { color: #1e3a5f !important; }

/* ── Typography ──────────────────────── */

/* ── Page title ──────────────────────── */
.page-hero {
    background: linear-gradient(135deg, #1e40af 0%, #0e7490 100%);
    border-radius: 16px;
    padding: 2rem 2.4rem;
    margin-bottom: 1.8rem;
    color: white !important;
    position: relative;
    overflow: hidden;
}
.page-hero::after {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 160px; height: 160px;
    border-radius: 50%;
    background: rgba(255,255,255,0.08);
}
.page-hero h1 { color: white !important; font-size: 1.9rem; font-weight: 800; margin: 0 0 0.3rem; }
.page-hero p  { color: rgba(255,255,255,0.82) !important; margin: 0; font-size: 0.92rem; }

/* ── KPI cards ───────────────────────── */
.kpi-card {
    background: #ffffff;
    border: 1px solid rgba(37,99,235,0.18);
    border-radius: 14px;
    padding: 1.3rem 1rem;
    text-align: center;
    box-shadow: 0 4px 24px rgba(30,58,138,0.09);
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
}
.kpi-card.blue::before   { background: linear-gradient(90deg,#2563eb,#60a5fa); }
.kpi-card.teal::before   { background: linear-gradient(90deg,#0891b2,#22d3ee); }
.kpi-card.red::before    { background: linear-gradient(90deg,#ef4444,#f97316); }
.kpi-card.green::before  { background: linear-gradient(90deg,#10b981,#34d399); }
.kpi-card.violet::before { background: linear-gradient(90deg,#7c3aed,#a78bfa); }
.kpi-val   { font-size: 2.2rem; font-weight: 800; color: #1e3a5f !important; line-height: 1; }
.kpi-label { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.07em; color: #475569 !important; font-weight: 600; margin: 0.4rem 0 0.2rem; }
.kpi-delta { font-size: 0.78rem; font-weight: 500; }
.kpi-delta.bad  { color: #ef4444 !important; }
.kpi-delta.good { color: #10b981 !important; }
.kpi-delta.neu  { color: #64748b !important; }

/* ── Section header ──────────────────── */
.sec-hdr {
    display: flex; align-items: flex-start; gap: 0.75rem;
    margin: 2rem 0 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 2px solid rgba(37,99,235,0.1);
}
.sec-icon {
    width: 36px; height: 36px; flex-shrink: 0;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; font-weight: 700;
    background: linear-gradient(135deg, #2563eb, #0891b2);
    color: white;
}
.sec-title { font-size: 1.15rem; font-weight: 700; color: #1e3a5f; margin: 0 0 0.15rem; }
.sec-desc  { font-size: 0.8rem; color: #64748b; margin: 0; }

/* ── Content cards ───────────────────── */
.card {
    background: rgba(255,255,255,0.9);
    border: 1px solid rgba(37,99,235,0.12);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 2px 12px rgba(30,58,138,0.05);
    margin-bottom: 0.9rem;
}
.card-title { font-size: 0.95rem; font-weight: 700; color: #1e3a5f; margin: 0 0 0.4rem; }
.card-body  { font-size: 0.84rem; color: #475569; line-height: 1.65; margin: 0; }
.card-fix   { font-size: 0.82rem; color: #2563eb; margin: 0.5rem 0 0; font-weight: 500; }

/* Priority badges */
.badge { display:inline-block; padding:2px 10px; border-radius:20px; font-size:0.7rem; font-weight:700; letter-spacing:.06em; text-transform:uppercase; margin-bottom:0.4rem; }
.badge-p1 { background:#fee2e2; color:#dc2626; border:1px solid #fca5a5; }
.badge-p2 { background:#fef3c7; color:#b45309; border:1px solid #fcd34d; }
.badge-p3 { background:#dcfce7; color:#15803d; border:1px solid #86efac; }
.badge-p4 { background:#dbeafe; color:#1d4ed8; border:1px solid #93c5fd; }

/* Card left-border by priority */
.card.p1 { border-left: 4px solid #ef4444; }
.card.p2 { border-left: 4px solid #f59e0b; }
.card.p3 { border-left: 4px solid #10b981; }

/* ── Review excerpt card ─────────────── */
.review-card {
    background: rgba(255,255,255,0.85);
    border: 1px solid rgba(37,99,235,0.1);
    border-left: 4px solid #2563eb;
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.6rem;
    font-size: 0.85rem;
    color: #334155;
    line-height: 1.65;
}
.review-meta { font-size:0.73rem; color:#94a3b8; margin-top:0.5rem; }

/* ── Action row ──────────────────────── */
.action-row {
    display: grid;
    grid-template-columns: 90px 1fr auto;
    gap: 1rem;
    background: rgba(255,255,255,0.88);
    border: 1px solid rgba(37,99,235,0.12);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
    align-items: start;
}
.action-week { font-size:0.73rem; font-weight:700; color:#2563eb; text-transform:uppercase; letter-spacing:.06em; }
.action-text { font-size:0.86rem; color:#334155; line-height:1.55; }
.action-team { font-size:0.75rem; color:#64748b; text-align:right; white-space:nowrap; }

/* ── Info box ────────────────────────── */
.info-box {
    background: rgba(219,234,254,0.5);
    border: 1px solid rgba(37,99,235,0.2);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    font-size: 0.84rem;
    color: #1e3a5f;
    line-height: 1.65;
}

/* ── ML predict result ───────────────── */
.predict-low   { background:#fee2e2; border:1px solid #fca5a5; border-radius:12px; padding:1.2rem; text-align:center; }
.predict-high  { background:#dcfce7; border:1px solid #86efac; border-radius:12px; padding:1.2rem; text-align:center; }
.predict-label { font-size:1.4rem; font-weight:800; }
.predict-sub   { font-size:0.85rem; margin-top:0.3rem; }

/* ── Metric delta override ───────────── */
[data-testid="stMetricDelta"] { font-size: 0.78rem !important; }

/* ── Tab bar ─────────────────────────── */
[data-baseweb="tab-list"] { gap: 0.3rem; }
[data-baseweb="tab"] {
    background: rgba(255,255,255,0.7) !important;
    border: 1px solid rgba(37,99,235,0.15) !important;
    border-radius: 8px !important;
    color: #334155 !important;
    font-size: 0.83rem !important;
    font-weight: 500 !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    background: linear-gradient(135deg,#2563eb,#0891b2) !important;
    color: white !important;
    border-color: transparent !important;
}
[data-baseweb="tab-border"], [data-baseweb="tab-highlight"] { display: none !important; }

/* ── Input / select ──────────────────── */
[data-baseweb="input"] input { background: rgba(255,255,255,0.9) !important; border-color: rgba(37,99,235,0.2) !important; }
textarea { background: rgba(255,255,255,0.9) !important; border-color: rgba(37,99,235,0.2) !important; }

/* ── Scrollbar ───────────────────────── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #f1f5f9; }
::-webkit-scrollbar-thumb { background: #93c5fd; border-radius: 3px; }

/* ── Dataframe ───────────────────────── */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(30,58,138,0.07); }
</style>
"""

def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)

def page_hero(title: str, subtitle: str):
    st.markdown(f"""
    <div class="page-hero">
      <h1>{title}</h1>
      <p>{subtitle}</p>
    </div>""", unsafe_allow_html=True)

def section(icon: str, title: str, desc: str = ""):
    st.markdown(f"""
    <div class="sec-hdr">
      <div class="sec-icon">{icon}</div>
      <div>
        <p class="sec-title">{title}</p>
        {"" if not desc else f'<p class="sec-desc">{desc}</p>'}
      </div>
    </div>""", unsafe_allow_html=True)

def kpi_card(col, val, label, delta="", dtype="neu", color="blue"):
    col.markdown(f"""
    <div class="kpi-card {color}">
      <div class="kpi-val">{val}</div>
      <div class="kpi-label">{label}</div>
      {"" if not delta else f'<div class="kpi-delta {dtype}">{delta}</div>'}
    </div>""", unsafe_allow_html=True)

def card(badge_cls, badge_text, title, body, fix="", priority_cls=""):
    fix_html = f'<p class="card-fix">&#9658; Fix: {fix}</p>' if fix else ""
    st.markdown(f"""
    <div class="card {priority_cls}">
      <span class="badge {badge_cls}">{badge_text}</span>
      <p class="card-title">{title}</p>
      <p class="card-body">{body}</p>
      {fix_html}
    </div>""", unsafe_allow_html=True)

def info_box(html: str):
    st.markdown(f'<div class="info-box">{html}</div>', unsafe_allow_html=True)
