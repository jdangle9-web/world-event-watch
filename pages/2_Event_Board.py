import streamlit as st

from services.storage import get_raw_items
from utils.grouping import build_event_groups

st.title("Event Board")

rows = get_raw_items(limit=1000)
if not rows:
    st.info("No articles available yet. Use the Live Feed page first.")
    st.stop()

events = build_event_groups(rows)

for event in events:
    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.subheader(event["query"])
            st.write(event["headline"])
            st.caption(f"Top domains: {event['top_domains'] or 'N/A'}")

        with col2:
            st.metric("Articles", event["article_count"])
            st.metric("Domains", event["domain_count"])

        with col3:
            st.metric("Countries", event["country_count"])
            st.metric("Confidence", event["confidence"])

        st.write(f"First seen: {event['earliest_seen']}")
        st.write(f"Latest seen: {event['latest_seen']}")

        if st.button(f"Open briefing for {event['query']}", key=f"brief_{event['query']}"):
            st.session_state["selected_event_query"] = event["query"]
            st.switch_page("pages/3_Briefing_View.py")
