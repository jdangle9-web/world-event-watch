from __future__ import annotations

from collections import defaultdict


def build_event_groups(rows: list[dict]) -> list[dict]:
    """
    Very simple grouping:
    - one event per watchlist query
    - counts supporting articles and domains
    """
    grouped: dict[str, list[dict]] = defaultdict(list)

    for row in rows:
        grouped[row["query"]].append(dict(row))

    events = []
    for query, items in grouped.items():
        items.sort(key=lambda x: x.get("seendate", ""), reverse=True)
        domains = sorted({x.get("domain", "") for x in items if x.get("domain")})
        countries = sorted({x.get("sourcecountry", "") for x in items if x.get("sourcecountry")})

        events.append({
            "event_id": query,
            "query": query,
            "headline": items[0]["title"] if items else query,
            "article_count": len(items),
            "domain_count": len(domains),
            "country_count": len(countries),
            "latest_seen": items[0].get("seendate", "") if items else "",
            "earliest_seen": items[-1].get("seendate", "") if items else "",
            "top_domains": ", ".join(domains[:5]),
            "items": items,
            "confidence": score_confidence(len(items), len(domains)),
        })

    events.sort(key=lambda e: (e["article_count"], e["domain_count"], e["latest_seen"]), reverse=True)
    return events


def score_confidence(article_count: int, domain_count: int) -> str:
    if article_count >= 10 and domain_count >= 5:
        return "High"
    if article_count >= 4 and domain_count >= 2:
        return "Medium"
    return "Low"
