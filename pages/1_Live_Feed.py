import pandas as pd
import streamlit as st

from services.gdelt_client import search_gdelt
from services.storage import get_raw_items, get_watchlist_terms, insert_raw_items

st.title("Live Feed")

terms = get_watchlist_terms()
if not terms:
    st.warning("Add at least one watch term on the home page.")
    st.stop()

col1, col2 = st.columns([2, 1])

with col1:
    selected_terms = st.multiselect(
        "Watch terms to fetch",
        options=terms,
        default=terms[:3]
    )

with col2:
    timespan = st.selectbox("Timespan", ["1h", "6h", "12h", "24h", "3d"], index=3)

if st.button("Fetch latest GDELT stories", type="primary"):
    total_inserted = 0
    with st.spinner("Fetching from GDELT..."):
        for term in selected_terms:
            items = search_gdelt(term, max_records=25, timespan=timespan)
            total_inserted += insert_raw_items(items)
    st.success(f"Done. Inserted {total_inserted} new articles.")
    st.rerun()

all_rows = get_raw_items(limit=500)

if not all_rows:
    st.info("No articles stored yet. Click the fetch button.")
    st.stop()

df = pd.DataFrame([dict(r) for r in all_rows])

filter_term = st.selectbox("Filter by query", ["All"] + sorted(df["query"].dropna().unique().tolist()))
if filter_term != "All":
    df = df[df["query"] == filter_term]

st.subheader("Stored articles")
st.dataframe(
    df[["seendate", "query", "title", "domain", "sourcecountry", "language", "tone", "url"]],
    use_container_width=True,
    hide_index=True,
)

st.caption(f"{len(df)} rows shown")
