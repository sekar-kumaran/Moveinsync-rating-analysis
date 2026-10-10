"""Page 2 - Complaint Deep Dive"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from utils.theme import inject_css, page_hero, section, kpi_card, apply_legend, PLOT_BASE, MULTI_CAT
from utils.data  import load_reviews, category_stats, monthly_stats, CAT_COLS, CAT_LABELS

st.set_page_config(page_title="Complaint Deep Dive - MoveInSync", layout="wide")
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

df   = load_reviews()
if df.empty: st.error("No data found."); st.stop()
cats = category_stats(df)

page_hero("Complaint Deep Dive",
          "Keyword-classified complaints across 10,000+ reviews -- what employees keep saying, and when each issue spikes")

# Category KPIs
st.markdown("<br>", unsafe_allow_html=True)
cols = st.columns(len(cats))
colors = ["red", "violet", "blue", "teal", "green"]
for i, (_, row) in enumerate(cats.iterrows()):
    kpi_card(cols[i], f"{row['low_total']:,}",
             row["label"].split("&")[0].strip(),
             f"{row['pct_of_low']:.0f}% of low-star", "bad", colors[i % len(colors)])
st.markdown("<br>", unsafe_allow_html=True)

# 01. Overlay bar + donut
section("01", "Complaint Category Frequency",
        "How often each theme appears -- all reviews vs only 1-2 star reviews")
col_a, col_b = st.columns([1.3, 1])
with col_a:
    fig = go.Figure()
    fig.add_trace(go.Bar(y=cats["label"], x=cats["total"], orientation="h",
                         name="All Reviews", marker_color="rgba(37,99,235,0.35)",
                         hovertemplate="<b>%{y}</b><br>Total: %{x:,}<extra></extra>"))
    fig.add_trace(go.Bar(y=cats["label"], x=cats["low_total"], orientation="h",
                         name="1+2 Star Only", marker_color="rgba(239,68,68,0.75)",
                         hovertemplate="<b>%{y}</b><br>Low-star: %{x:,}<extra></extra>"))
    fig.update_layout(**PLOT_BASE, barmode="overlay", height=360,
                      title="Category Mentions: All vs Low-Star Reviews")
    fig.update_yaxes(autorange="reversed", tickfont=dict(color="#334155"))
    fig.update_xaxes(title="Review Count", gridcolor="rgba(100,150,220,0.12)")
    apply_legend(fig)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        "<p style='font-size:0.82rem;color:#475569;margin:-0.5rem 0 1rem 0.3rem'>"
        "<b>Reading:</b> The closer the red bar matches the blue, the more that issue exclusively "
        "drives low-star reviews. Crashes/Login and GPS show the highest red-to-blue ratio -- "
        "these are the most damaging complaint types to the rating."
        "</p>",
        unsafe_allow_html=True,
    )

with col_b:
    fig2 = go.Figure(go.Pie(
        labels=cats["label"], values=cats["low_total"],
        marker_colors=MULTI_CAT, hole=0.45,
        hovertemplate="<b>%{label}</b><br>%{value:,} low-star mentions<extra></extra>",
        textinfo="percent"))
    fig2.update_layout(**PLOT_BASE, height=360, title="Share of Low-Star Complaints")
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown(
        "<p style='font-size:0.82rem;color:#475569;margin:-0.5rem 0 1rem 0.3rem'>"
        "<b>Reading:</b> The top two categories account for over half of all low-star complaint "
        "mentions. Fixing just these two would meaningfully move the overall rating."
        "</p>",
        unsafe_allow_html=True,
    )

# 02. Heatmap
section("02", "Issue Intensity by Star Rating",
        "Which issues appear in which rating band -- confirms which categories are truly critical")
heat = []
for r in [1, 2, 3, 4, 5]:
    row = {"Rating": f"{r} star"}
    sub = df[df["star_rating"] == r]
    for c in CAT_COLS:
        if c in df.columns:
            row[CAT_LABELS[c]] = int(sub[c].sum())
    heat.append(row)
heat_df = pd.DataFrame(heat).set_index("Rating")
fig3 = px.imshow(
    heat_df.T,
    color_continuous_scale=[[0, "#f0f7ff"], [0.3, "#93c5fd"], [0.7, "#2563eb"], [1, "#1e3a8a"]],
    aspect="auto", text_auto=True)
fig3.update_layout(**PLOT_BASE, height=320, title="Complaint Category x Star Rating Heatmap")
fig3.update_traces(textfont=dict(color="#1e3a5f", size=12))
fig3.update_xaxes(tickfont=dict(color="#334155"))
fig3.update_yaxes(tickfont=dict(color="#334155"))
st.plotly_chart(fig3, use_container_width=True)
st.markdown(
    "<p style='font-size:0.82rem;color:#475569;margin:-0.5rem 0 1.2rem 0.3rem'>"
    "<b>Reading:</b> Dark blue cells in the 1-star column confirm which issues are "
    "predominantly cited by the most dissatisfied users. Crashes/Login and GPS are darkest -- "
    "they overwhelmingly appear in 1-star reviews and almost never in 4-5 star reviews."
    "</p>",
    unsafe_allow_html=True,
)

# 03. Category trend over time
section("03", "Complaint Category Trend Over Time",
        "Select a category to see how often it is mentioned month-over-month with the mean rating for those reviews")
sel_cat = st.selectbox("Category to track", list(CAT_LABELS.values()))
cat_col = {v: k for k, v in CAT_LABELS.items()}[sel_cat]
if cat_col in df.columns:
    cat_monthly = (df[df[cat_col] == 1]
                   .groupby("year_month")
                   .agg(count=(cat_col, "sum"), avg_rating=("star_rating", "mean"))
                   .reset_index())
    cat_monthly = cat_monthly[cat_monthly["count"] >= 2]
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(x=cat_monthly["year_month"], y=cat_monthly["count"],
                          name="Mentions", marker_color="rgba(239,68,68,0.55)",
                          hovertemplate="%{x|%b %Y}<br>%{y} mentions<extra></extra>"))
    fig4.add_trace(go.Scatter(x=cat_monthly["year_month"], y=cat_monthly["avg_rating"],
                              name="Avg Rating (that issue)", yaxis="y2",
                              line=dict(color="#2563eb", width=2), mode="lines+markers",
                              marker=dict(size=5),
                              hovertemplate="%{x|%b %Y}<br>Avg: %{y:.2f}<extra></extra>"))
    fig4.update_layout(**PLOT_BASE, height=320,
                       title=f"Monthly Trend -- {sel_cat}",
                       yaxis=dict(title="Mentions", gridcolor="rgba(100,150,220,0.12)"),
                       yaxis2=dict(title="Avg Rating", overlaying="y", side="right",
                                   range=[1, 5], gridcolor="rgba(0,0,0,0)",
                                   tickfont=dict(color="#2563eb")))
    fig4.update_xaxes(tickformat="%b %Y", tickangle=-45, tickfont=dict(color="#64748b", size=10))
    apply_legend(fig4)
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown(
        "<p style='font-size:0.82rem;color:#475569;margin:-0.5rem 0 1.2rem 0.3rem'>"
        f"<b>Reading:</b> Bars show how many reviews mention <b>{sel_cat}</b> each month. "
        "The blue line shows the average rating of those same reviews. When bars rise and "
        "the blue line dips simultaneously, that month had a severe spike in this complaint type."
        "</p>",
        unsafe_allow_html=True,
    )

# 04. Evidence excerpts
section("04", "Representative Review Excerpts by Category",
        "Real user quotes validating each complaint theme -- select a category to load samples")
sel_cat2 = st.selectbox("Show excerpts for", list(CAT_LABELS.values()), key="exc_sel")
cat_col2 = {v: k for k, v in CAT_LABELS.items()}[sel_cat2]
if cat_col2 in df.columns:
    sample = (df[(df[cat_col2] == 1) & (df["star_rating"] <= 2)]
              .dropna(subset=["review_text"])
              .sort_values("star_rating")
              .head(6))
    STAR_F = "&#9733;"
    STAR_E = "&#9734;"
    for _, row in sample.iterrows():
        r = int(row["star_rating"])
        star_html = STAR_F * r + STAR_E * (5 - r)
        ver  = row.get("app_version", "?")
        date = str(row.get("review_date", ""))[:10]
        text = str(row["review_text"])[:380]
        trail = "..." if len(str(row["review_text"])) > 380 else ""
        st.markdown(
            f"<div class='review-card'>{text}{trail}"
            f"<div class='review-meta'>{star_html} &nbsp;&middot;&nbsp; {date} &nbsp;&middot;&nbsp; v{ver}</div>"
            f"</div>",
            unsafe_allow_html=True)
