"""Page 3 - Review Explorer: search, filter, paginate, export."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
from utils.theme import inject_css, page_hero, section
from utils.data  import load_reviews, CAT_LABELS

st.set_page_config(page_title="Review Explorer - MoveInSync", layout="wide")
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
if df.empty:
    st.error("No data found."); st.stop()

page_hero("Review Explorer",
          "Search 10,000+ raw Play Store reviews by keyword, rating, category, and date. Validate any hypothesis directly.")

# Filters
section("F", "Filters", "Narrow down the review set")
f1, f2, f3, f4 = st.columns([2, 1, 1, 1])
with f1:
    search = st.text_input("Search review text", placeholder="e.g. gps, crash, otp, driver, no show...")
with f2:
    sel_ratings = st.multiselect("Star ratings", [1, 2, 3, 4, 5], default=[1, 2])
with f3:
    cat_options = ["All"] + list(CAT_LABELS.values())
    sel_cat = st.selectbox("Issue category", cat_options)
with f4:
    sort_by = st.selectbox("Sort by", ["Latest first", "Oldest first",
                                        "Rating: Low to High", "Rating: High to Low"])

# Apply filters
filtered = df.copy()
if sel_ratings:
    filtered = filtered[filtered["star_rating"].isin(sel_ratings)]
if search:
    filtered = filtered[filtered["review_text"].fillna("").str.lower().str.contains(
        search.lower(), regex=False)]
if sel_cat != "All":
    cat_col = {v: k for k, v in CAT_LABELS.items()}.get(sel_cat)
    if cat_col and cat_col in filtered.columns:
        filtered = filtered[filtered[cat_col] == 1]

sort_map = {
    "Latest first":       ("review_date", False),
    "Oldest first":       ("review_date", True),
    "Rating: Low to High":("star_rating", True),
    "Rating: High to Low":("star_rating", False),
}
sc, sa = sort_map[sort_by]
if sc in filtered.columns:
    filtered = filtered.sort_values(sc, ascending=sa)

st.markdown(
    f"<p style='color:#475569;font-size:0.85rem;margin:0.3rem 0 1rem'>Found "
    f"<b>{len(filtered):,}</b> reviews matching your filters</p>",
    unsafe_allow_html=True,
)

# Summary metrics
if not filtered.empty:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Reviews", f"{len(filtered):,}")
    m2.metric("Mean Rating", f"{filtered['star_rating'].mean():.2f}")
    m3.metric("Low-Star %", f"{(filtered['star_rating'] <= 2).mean() * 100:.1f}%")
    with_reply = (filtered["developer_reply"].notna().sum()
                  if "developer_reply" in filtered.columns else 0)
    m4.metric("Dev Replies", f"{with_reply:,}")
    st.markdown("<br>", unsafe_allow_html=True)

# Review cards
section("R", "Reviews", "Expand each card to read the full review and any developer reply")
PAGE_SIZE = 10
total_pages = max(1, (len(filtered) - 1) // PAGE_SIZE + 1)
page_num = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)
page_data = filtered.iloc[(page_num - 1) * PAGE_SIZE: page_num * PAGE_SIZE]

STAR_FILLED = "&#9733;"
STAR_EMPTY  = "&#9734;"

for _, row in page_data.iterrows():
    rating = int(row.get("star_rating", 0))
    star_html = STAR_FILLED * rating + STAR_EMPTY * (5 - rating)
    date   = str(row.get("review_date", ""))[:10]
    ver    = str(row.get("app_version", "?"))
    text   = str(row.get("review_text", ""))
    reply  = row.get("developer_reply", "")

    label = f"[{rating}/5]  {date}  v{ver}  --  {text[:85]}"

    with st.expander(label):
        st.markdown(
            f"<div style='font-size:0.88rem;color:#334155;line-height:1.7'>"
            f"{star_html} &nbsp; v{ver} &nbsp; {date}"
            f"<hr style='margin:0.5rem 0;border-color:rgba(37,99,235,0.1)'>"
            f"{text}</div>",
            unsafe_allow_html=True,
        )
        if reply and pd.notna(reply):
            st.markdown(
                f"<div style='background:#eff6ff;border-left:3px solid #2563eb;"
                f"border-radius:6px;padding:0.7rem 1rem;margin-top:0.6rem;"
                f"font-size:0.82rem;color:#1e40af'>"
                f"<b>Developer Reply:</b><br>{str(reply)[:400]}</div>",
                unsafe_allow_html=True,
            )

st.caption(f"Page {page_num} of {total_pages}")

# Download
st.markdown("<br>", unsafe_allow_html=True)
disp_cols = ["star_rating", "review_date", "app_version", "review_text", "developer_reply"]
disp_cols = [c for c in disp_cols if c in filtered.columns]
st.download_button(
    "Download filtered reviews (CSV)",
    data=filtered[disp_cols].to_csv(index=False).encode("utf-8"),
    file_name="moveinsync_filtered_reviews.csv",
    mime="text/csv",
)
