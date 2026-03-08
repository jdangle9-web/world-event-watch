from __future__ import annotations

import requests

BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"


def search_gdelt(query: str, max_records: int = 50, timespan: str = "24h") -> list[dict]:
    """
    Query the GDELT DOC API in ArticleList mode and return normalized article records.
    """
    params = {
        "query": query,
        "mode": "ArtList",
        "maxrecords": max_records,
        "timespan": timespan,
        "format": "json",
        "sort": "datedesc",
    }

    resp = requests.get(BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    articles = data.get("articles", [])
    normalized = []

    for article in articles:
        normalized.append({
            "platform": "gdelt",
            "query": query,
            "title": article.get("title", "").strip(),
            "url": article.get("url", "").strip(),
            "domain": article.get("domain", "").strip(),
            "seendate": article.get("seendate", "").strip(),
            "language": article.get("language", "").strip(),
            "sourcecountry": article.get("sourcecountry", "").strip(),
            "tone": _to_float(article.get("tone")),
        })

    return [x for x in normalized if x["title"] and x["url"]]


def _to_float(value):
    try:
        return float(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None
