"""Minimal client for TMDB — a free public movie API (themoviedb.org).

Optional: set the TMDB_API_KEY env var (free signup) to enable online search.
Without a key the app still works fully offline against the local catalog —
`search()` just returns [] and the UI falls back to local search.
"""
from __future__ import annotations
import os
import json
import urllib.parse
import urllib.request

BASE = "https://api.themoviedb.org/3"


def _key() -> str | None:
    return os.getenv("TMDB_API_KEY")


def available() -> bool:
    return bool(_key())


def search(query: str, limit: int = 12) -> list[dict]:
    key = _key()
    if not key or not query.strip():
        return []
    url = f"{BASE}/search/movie?" + urllib.parse.urlencode(
        {"api_key": key, "query": query, "include_adult": "false"})
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.load(r)
    except Exception:
        return []
    out = []
    for m in data.get("results", [])[:limit]:
        out.append({
            "tmdb_id": m.get("id"),
            "title": m.get("title", ""),
            "year": (m.get("release_date") or "")[:4],
            "overview": m.get("overview", ""),
        })
    return out
