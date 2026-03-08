from services.storage import get_watchlist_terms, save_watchlist_term


DEFAULT_TERMS = [
    "protest",
    "sanctions",
    "cyberattack",
    "port disruption",
    "rare earths",
]


def seed_watchlist() -> None:
    existing = set(get_watchlist_terms())
    for term in DEFAULT_TERMS:
        if term not in existing:
            save_watchlist_term(term)
