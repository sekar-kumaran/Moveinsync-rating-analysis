"""Page 1 - Rating and Trend Analysis"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from utils.theme import inject_css, page_hero, section, kpi_card, apply_axes, apply_legend
from utils.theme import PLOT_BASE, RATING_COLORS, RATING_LIST
from utils.data  import load_reviews, monthly_stats, yearly_stats, rating_distribution

st.set_page_config(page_title="Rating Analysis - MoveInSync", layout="wide")
inject_css()

with st.sidebar:
    st.markdown(
        "<div style='text-align:center;padding:.8rem 0 0.5rem'>"
        "<div style='font-weight:800;color:#fff;font-size:1.15rem;letter-spacing:.02em'>MoveInSync</div>"
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
if df.empty:
    st.error("No data. Run the notebook first."); st.stop()

page_hero(
    "Rating and Trend Analysis",
    "Deep time-series breakdown of MoveInSync Play Store ratings -- when did things get worse, by how much, and on which version?",
)

# Filters
with st.expander("Filters", expanded=False):
    fc1, fc2 = st.columns(2)
    min_d = df["review_date"].min().date()
    max_d = df["review_date"].max().date()
    with fc1:
        date_range = st.date_input("Date range", value=(min_d, max_d), min_value=min_d, max_value=max_d)
    with fc2:
        sel_ratings = st.multiselect("Star ratings", [1, 2, 3, 4, 5], default=[1, 2, 3, 4, 5])

dff = df.copy()
if len(date_range) == 2:
    dff = dff[(dff["review_date"].dt.date >= date_range[0]) &
              (dff["review_date"].dt.date <= date_range[1])]
if sel_ratings:
    dff = dff[dff["star_rating"].isin(sel_ratings)]
st.caption(f"Showing **{len(dff):,}** reviews matching filters")

m2 = monthly_stats(dff)
yr = yearly_stats(dff)

# KPIs
c1, c2, c3, c4, c5 = st.columns(5)
kpi_card(c1, f"{len(dff):,}",                                 "Reviews in Range",   "",  "neu",  "blue")
kpi_card(c2, f"{dff['star_rating'].mean():.2f}",              "Mean Rating",        "",  "bad",  "red")
kpi_card(c3, f"{(dff['star_rating']<=2).mean()*100:.1f}%",   "Low-Star Share",     "",  "bad",  "red")
kpi_card(c4, f"{(dff['star_rating']==5).mean()*100:.1f}%",   "5-Star Share",       "",  "good", "green")
kpi_card(c5, f"{(dff['star_rating']==1).mean()*100:.1f}%",   "1-Star Share",       "",  "bad",  "violet")
st.markdown("<br>", unsafe_allow_html=True)

# ── 01. Monthly Volume + Mean Rating ──────────────────────────
section("01", "Monthly Review Volume and Mean Rating",
        "Dual-axis: bars = review volume, blue line = mean rating per month")
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Bar(x=m2["year_month"], y=m2["count"], name="Review Volume",
                     marker_color="rgba(37,99,235,0.28)",
                     hovertemplate="%{x|%b %Y}<br>%{y} reviews<extra></extra>"), secondary_y=False)
fig.add_trace(go.Scatter(x=m2["year_month"], y=m2["avg_rating"], name="Mean Rating",
                         line=dict(color="#2563eb", width=2.5), mode="lines+markers",
                         marker=dict(size=5),
                         hovertemplate="%{x|%b %Y}<br>Avg: %{y:.2f}<extra></extra>"), secondary_y=True)
fig.add_hline(y=4.0, line_dash="dot", line_color="#10b981",
              annotation_text="Target 4.0", annotation_font=dict(color="#059669"), secondary_y=True)
fig.update_layout(**PLOT_BASE, height=380, title="Monthly Review Volume vs Mean Rating")
fig.update_yaxes(title_text="Reviews", secondary_y=False, gridcolor="rgba(100,150,220,0.12)")
fig.update_yaxes(title_text="Mean Rating", secondary_y=True, range=[1, 5],
                 gridcolor="rgba(0,0,0,0)", tickfont=dict(color="#2563eb"))
fig.update_xaxes(tickformat="%b %Y", tickangle=-45, tickfont=dict(color="#64748b", size=10))
apply_legend(fig)
st.plotly_chart(fig, use_container_width=True)
st.markdown(
    "<p style='font-size:0.82rem;color:#475569;margin:-0.5rem 0 1.2rem 0.3rem'>"
    "<b>Reading:</b> The volume of reviews surged in recent months, but the mean rating "
    "(blue line) has stayed below the 4.0 target (green dashes). This indicates a growing, "
    "unhappy user base -- more people are writing reviews, and more of them are negative."
    "</p>",
    unsafe_allow_html=True,
)

# ── 02. Low-star and 5-star share over time ───────────────────
section("02", "Low-Star vs 5-Star Share Over Time",
        "Area chart: fraction of 1-2 star (red) and 5-star (green) reviews each month")
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=m2["year_month"], y=m2["low_pct"],
                          name="1+2 Star Share", fill="tozeroy",
                          fillcolor="rgba(239,68,68,0.15)",
                          line=dict(color="#ef4444", width=2),
                          hovertemplate="%{x|%b %Y}<br>Low-star: %{y:.1f}%<extra></extra>"))
fig2.add_trace(go.Scatter(x=m2["year_month"], y=m2["five_star_pct"],
                          name="5-Star Share", fill="tozeroy",
                          fillcolor="rgba(16,185,129,0.12)",
                          line=dict(color="#10b981", width=2),
                          hovertemplate="%{x|%b %Y}<br>5-star: %{y:.1f}%<extra></extra>"))
fig2.update_layout(**PLOT_BASE, height=300, title="Low-Star (1+2) vs 5-Star Share (%)")
fig2.update_yaxes(title="% of reviews that month", ticksuffix="%",
                  gridcolor="rgba(100,150,220,0.12)", range=[0, 100])
fig2.update_xaxes(tickformat="%b %Y", tickangle=-45, tickfont=dict(color="#64748b", size=10))
apply_legend(fig2)
st.plotly_chart(fig2, use_container_width=True)
st.markdown(
    "<p style='font-size:0.82rem;color:#475569;margin:-0.5rem 0 1.2rem 0.3rem'>"
    "<b>Reading:</b> When the red area (low-star share) rises above the green area (5-star share), "
    "negative sentiment dominates. The crossing points indicate critical release events or "
    "operational failures -- investigate those months for root causes."
    "</p>",
    unsafe_allow_html=True,
)

# ── 03 + 04. Year-over-year + Donut ──────────────────────────
col_a, col_b = st.columns(2)
with col_a:
    section("03", "Year-over-Year Comparison", "How ratings have shifted by calendar year")
    fig3 = go.Figure(go.Bar(
        x=yr["year"].astype(str), y=yr["avg_rating"],
        marker_color=["#2563eb", "#0891b2", "#7c3aed", "#db2777", "#ea580c"][:len(yr)],
        text=[f"{v:.2f}" for v in yr["avg_rating"]],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Avg: %{y:.2f}<extra></extra>"))
    fig3.update_layout(**PLOT_BASE, height=300, title="Average Rating by Year")
    fig3.update_yaxes(range=[1, 5], title="Avg Rating", gridcolor="rgba(100,150,220,0.12)")
    fig3.update_xaxes(title="Year", tickfont=dict(color="#64748b"))
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown(
        "<p style='font-size:0.82rem;color:#475569;margin:-0.5rem 0 1rem 0.3rem'>"
        "<b>Reading:</b> Each bar shows the mean rating for that calendar year. "
        "A declining trend year-over-year confirms the problem is worsening, not improving."
        "</p>",
        unsafe_allow_html=True,
    )

with col_b:
    section("04", "Current Rating Distribution", "Share of each star level in the filtered dataset")
    rd2 = dff["star_rating"].value_counts().sort_index().reset_index()
    rd2.columns = ["Rating", "Count"]
    rd2["Pct"] = (rd2["Count"] / len(dff) * 100).round(1)
    fig4 = go.Figure(go.Pie(
        labels=[f"{r} Star" for r in rd2["Rating"]],
        values=rd2["Count"],
        marker_colors=RATING_LIST,
        hole=0.52,
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>%{value:,} reviews<extra></extra>"))
    fig4.add_annotation(
        text=f"{dff['star_rating'].mean():.2f}<br><span style='font-size:9px'>mean</span>",
        x=0.5, y=0.5, font=dict(size=20, color="#1e3a5f"), showarrow=False)
    fig4.update_layout(**PLOT_BASE, height=300, title="Rating Share")
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown(
        "<p style='font-size:0.82rem;color:#475569;margin:-0.5rem 0 1rem 0.3rem'>"
        "<b>Reading:</b> The donut shows a bimodal pattern -- high 1-star AND high 5-star counts "
        "with a hollow middle. This is typical of a product with passionate fans and frustrated users, "
        "with few neutral experiences."
        "</p>",
        unsafe_allow_html=True,
    )

# ── 05. Day-of-week ───────────────────────────────────────────
section("05", "Review Volume and Mean Rating by Day of Week",
        "Detects whether certain days -- e.g. Monday morning commute -- generate more complaints")
col_c, col_d = st.columns(2)
dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
with col_c:
    dow_vol = dff.groupby("day_of_week").size().reindex(dow_order).reset_index()
    dow_vol.columns = ["Day", "Count"]
    fig5 = go.Figure(go.Bar(x=dow_vol["Day"], y=dow_vol["Count"],
                            marker_color="rgba(37,99,235,0.6)",
                            hovertemplate="<b>%{x}</b><br>%{y} reviews<extra></extra>"))
    fig5.update_layout(**PLOT_BASE, height=270, title="Review Volume by Day of Week")
    apply_axes(fig5, y_title="Reviews", tickangle=-30)
    st.plotly_chart(fig5, use_container_width=True)
    st.markdown(
        "<p style='font-size:0.82rem;color:#475569;margin:-0.5rem 0 1rem 0.3rem'>"
        "<b>Reading:</b> Weekday peaks (especially Mon-Wed) align with the morning commute rush -- "
        "when GPS failures and cab no-shows have the highest emotional impact on users."
        "</p>",
        unsafe_allow_html=True,
    )

with col_d:
    dow_rat = (dff.groupby("day_of_week")["star_rating"].mean()
                  .reindex(dow_order).reset_index())
    dow_rat.columns = ["Day", "Avg Rating"]
    colors = ["#ef4444" if v < 3 else "#f59e0b" if v < 4 else "#10b981"
              for v in dow_rat["Avg Rating"]]
    fig6 = go.Figure(go.Bar(x=dow_rat["Day"], y=dow_rat["Avg Rating"],
                            marker_color=colors,
                            text=[f"{v:.2f}" for v in dow_rat["Avg Rating"]],
                            textposition="outside",
                            hovertemplate="<b>%{x}</b><br>Avg: %{y:.2f}<extra></extra>"))
    fig6.update_layout(**PLOT_BASE, height=270, title="Mean Rating by Day of Week")
    apply_axes(fig6, y_title="Avg Rating", y_range=[1, 5.5], tickangle=-30)
    st.plotly_chart(fig6, use_container_width=True)
    st.markdown(
        "<p style='font-size:0.82rem;color:#475569;margin:-0.5rem 0 1rem 0.3rem'>"
        "<b>Reading:</b> Sunday ratings drop sharply (red bar) -- likely because infrequent users "
        "or weekend-only trips encounter unfamiliar issues. Target weekend reliability in ops alerts."
        "</p>",
        unsafe_allow_html=True,
    )

# ── 06. App version (v11+) ────────────────────────────────────
if "app_version" in dff.columns:
    section("06", "Rating by App Version (v11 and above)",
            "Shows mean rating per version -- pinpoints exactly which release caused a rating crash")

    def _major_ver(v):
        try:
            return float(str(v).split(".")[0])
        except Exception:
            return 0.0

    v_all = (dff.dropna(subset=["app_version"])
               .groupby("app_version")
               .agg(count=("star_rating", "count"), avg=("star_rating", "mean"),
                    low_pct=("is_low_star", "mean"))
               .reset_index())
    v_all["major"] = v_all["app_version"].apply(_major_ver)
    # Filter to v11+ only, top 14 by volume
    v_stats = (v_all[v_all["major"] >= 11]
               .sort_values("count", ascending=False)
               .head(14)
               .sort_values("avg"))
    v_stats["low_pct"] = (v_stats["low_pct"] * 100).round(1)

    if v_stats.empty:
        st.info("No v11+ versions found -- check the app_version column values.")
    else:
        fig7 = go.Figure(go.Bar(
            x=v_stats["avg"],
            y=v_stats["app_version"],
            orientation="h",
            marker_color=[RATING_COLORS.get(round(v), "#94a3b8") for v in v_stats["avg"]],
            text=[f"{v:.2f}  ({n:,} reviews, {lp}% low-star)"
                  for v, n, lp in zip(v_stats["avg"], v_stats["count"], v_stats["low_pct"])],
            textposition="outside",
            hovertemplate="<b>v%{y}</b><br>Avg: %{x:.2f}<extra></extra>"))
        fig7.update_layout(**PLOT_BASE, height=max(340, len(v_stats) * 35),
                           title="Mean Rating by App Version (v11+, top 14 by volume)")
        fig7.update_xaxes(range=[1, 6.8], title="Mean Rating", gridcolor="rgba(100,150,220,0.12)")
        fig7.update_yaxes(title="App Version", tickfont=dict(color="#334155", size=11))
        st.plotly_chart(fig7, use_container_width=True)
        st.markdown(
            "<p style='font-size:0.82rem;color:#475569;margin:-0.5rem 0 1rem 0.3rem'>"
            "<b>Reading:</b> Red bars (rating &lt; 3) mark releases that immediately triggered "
            "negative feedback -- typically caused by a regression in GPS accuracy, OTP delivery, "
            "or app stability. Cross-reference with the release changelog to identify the culprit commit."
            "</p>",
            unsafe_allow_html=True,
        )
