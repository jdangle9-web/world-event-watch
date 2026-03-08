import streamlit as st

from services.storage import init_db, get_watchlist_terms, save_watchlist_term, delete_watchlist_term
from utils.seed import seed_watchlist

st.set_page_config(page_title="World Event Watch", layout="wide")

init_db()
seed_watchlist()

st.title("World Event Watch")
st.caption("Afternoon MVP: Streamlit + SQLite + GDELT")

st.write(
    "Use the sidebar pages to view the live feed, grouped events, and a simple briefing view."
)

with st.expander("Manage watchlist"):
    current_terms = get_watchlist_terms()
    st.write("Current terms:", ", ".join(current_terms) if current_terms else "None yet")

    with st.form("add_term_form", clear_on_submit=True):
        new_term = st.text_input("Add a watch term")
        submitted = st.form_submit_button("Add")
        if submitted:
            if save_watchlist_term(new_term):
                st.success(f"Added: {new_term}")
                st.rerun()
            else:
                st.warning("That term is blank or already exists.")

    term_to_delete = st.selectbox("Delete a watch term", options=[""] + current_terms)
    if st.button("Delete selected term", disabled=not term_to_delete):
        delete_watchlist_term(term_to_delete)
        st.success(f"Deleted: {term_to_delete}")
        st.rerun()

st.info("Next: open the Live Feed page and fetch recent GDELT articles.")
