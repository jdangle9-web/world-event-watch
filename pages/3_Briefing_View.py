import pandas as pd
import streamlit as st

from services.storage import get_raw_items
from utils.grouping import build_event_groups

st.title("Briefing View")

selected_query = st.session_state.get("selected_event_query")

rows = get_raw_items(limit=1000)
if not rows:
    st.info("No articles available yet.")
    st.stop()

events = build_event_groups(rows)
queries = [e["query"] for e in events]

if not queries:
    st.info("No grouped events available yet.")
    st.stop()

selected_query = st.selectbox(
    "Choose an event",
    options=queries,
    index=queries.index(selected_query) if selected_query in queries else 0
)

event = next(e for e in events if e["query"] == selected_query)

st.subheader(event["headline"])
st.write(f"**Topic:** {event['query']}")
st.write(f"**Confidence:** {event['confidence']}")
st.write(f"**Articles found:** {event['article_count']}")
st.write(f"**Unique domains:** {event['domain_count']}")
st.write(f"**Countries represented:** {event['country_count']}")
st.write(f"**Earliest seen:** {event['earliest_seen']}")
st.write(f"**Latest seen:** {event['latest_seen']}")

st.markdown("### Why it matters")
st.write(
    f"This topic is showing up across {event['domain_count']} source domains "
    f"with {event['article_count']} matching articles in the current dataset."
)

st.markdown("### Analyst takeaway")
if event["confidence"] == "High":
    st.write("This looks broadly reported and is worth stakeholder attention.")
elif event["confidence"] == "Medium":
    st.write("This appears to be developing and should stay on the watchlist.")
else:
    st.write("This is still a weak signal and may need more confirmation.")

st.markdown("### Supporting coverage")
df = pd.DataFrame(event["items"])
st.dataframe(
    df[["seendate", "title", "domain", "sourcecountry", "url"]],
    use_container_width=True,
    hide_index=True,
)

st.markdown("### Notes for stakeholders")
default_note = (
    f"Observed increasing coverage on '{event['query']}' across {event['domain_count']} domains. "
    f"Latest tracked headline: {event['headline']}"
)
notes = st.text_area("Edit this summary", value=default_note, height=140)
st.download_button(
    "Download summary as text",
    data=notes,
    file_name=f"{event['query'].replace(' ', '_')}_brief.txt",
    mime="text/plain",
)
