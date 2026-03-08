import sqlite3
from pathlib import Path
from typing import Iterable, Optional

DB_PATH = Path("events.db")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS raw_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT NOT NULL,
        query TEXT NOT NULL,
        title TEXT NOT NULL,
        url TEXT NOT NULL UNIQUE,
        domain TEXT,
        seendate TEXT,
        language TEXT,
        sourcecountry TEXT,
        tone REAL,
        inserted_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS watchlist_terms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        term TEXT NOT NULL UNIQUE
    )
    """)

    conn.commit()
    conn.close()


def save_watchlist_term(term: str) -> bool:
    term = term.strip()
    if not term:
        return False

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("INSERT OR IGNORE INTO watchlist_terms(term) VALUES (?)", (term,))
        conn.commit()
        inserted = cur.rowcount > 0
    finally:
        conn.close()
    return inserted


def delete_watchlist_term(term: str) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM watchlist_terms WHERE term = ?", (term,))
    conn.commit()
    conn.close()


def get_watchlist_terms() -> list[str]:
    conn = get_conn()
    cur = conn.cursor()
    rows = cur.execute("SELECT term FROM watchlist_terms ORDER BY term COLLATE NOCASE").fetchall()
    conn.close()
    return [row["term"] for row in rows]


def insert_raw_items(items: Iterable[dict]) -> int:
    conn = get_conn()
    cur = conn.cursor()
    inserted = 0

    for item in items:
        cur.execute("""
        INSERT OR IGNORE INTO raw_items
        (platform, query, title, url, domain, seendate, language, sourcecountry, tone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item.get("platform", "gdelt"),
            item.get("query", ""),
            item.get("title", ""),
            item.get("url", ""),
            item.get("domain", ""),
            item.get("seendate", ""),
            item.get("language", ""),
            item.get("sourcecountry", ""),
            item.get("tone"),
        ))
        inserted += cur.rowcount

    conn.commit()
    conn.close()
    return inserted


def get_raw_items(limit: int = 500, query_filter: Optional[str] = None) -> list[sqlite3.Row]:
    conn = get_conn()
    cur = conn.cursor()

    if query_filter:
        rows = cur.execute("""
            SELECT *
            FROM raw_items
            WHERE query = ?
            ORDER BY seendate DESC, id DESC
            LIMIT ?
        """, (query_filter, limit)).fetchall()
    else:
        rows = cur.execute("""
            SELECT *
            FROM raw_items
            ORDER BY seendate DESC, id DESC
            LIMIT ?
        """, (limit,)).fetchall()

    conn.close()
    return rows


def get_item_by_url(url: str):
    conn = get_conn()
    cur = conn.cursor()
    row = cur.execute("SELECT * FROM raw_items WHERE url = ?", (url,)).fetchone()
    conn.close()
    return row
