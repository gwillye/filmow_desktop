"""Local movie watch-history store — JSON-backed, no dependencies.

The core of a personal, offline "Filmow-style" tracker: keep your watched
films, ratings, tags and notes locally (no account, no bot-blocked login).
A TMDB client can later enrich entries with metadata, but the store works
fully offline and is the source of truth.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Optional


@dataclass
class Movie:
    title: str
    year: Optional[int] = None
    tmdb_id: Optional[int] = None
    watched: bool = True
    rating: Optional[float] = None        # 0–5
    watched_date: Optional[str] = None    # ISO 'YYYY-MM-DD'
    tags: list[str] = field(default_factory=list)
    notes: str = ""
    lists: list[str] = field(default_factory=list)   # watched / watchlist / rewatch / favorite

    def key(self) -> str:
        return f"{self.title.strip().lower()}|{self.year or ''}"


# Gabriel's four lists (filmow-style): seen / want-to-see / want-to-rewatch / favorites
LISTS = ("watched", "watchlist", "rewatch", "favorite")
LIST_LABELS = {
    "watched": "Já vi",
    "watchlist": "Quero ver",
    "rewatch": "Quero rever",
    "favorite": "Favoritos",
}


class MovieStore:
    def __init__(self, path: str | Path = "movies.json") -> None:
        self.path = Path(path)
        self._movies: dict[str, Movie] = {}
        self.load()

    # ---- persistence ----
    def load(self) -> None:
        if self.path.exists():
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self._movies = {m["title"].strip().lower() + "|" + str(m.get("year") or ""):
                            Movie(**m) for m in data}

    def save(self) -> None:
        self.path.write_text(
            json.dumps([asdict(m) for m in self._movies.values()],
                       ensure_ascii=False, indent=2),
            encoding="utf-8")

    # ---- CRUD ----
    def add(self, movie: Movie) -> Movie:
        self._movies[movie.key()] = movie
        self.save()
        return movie

    def rate(self, title: str, rating: float, year: Optional[int] = None) -> bool:
        m = self._movies.get(f"{title.strip().lower()}|{year or ''}")
        if not m:
            return False
        if not 0 <= rating <= 5:
            raise ValueError("rating must be 0–5")
        m.rating = rating
        m.watched = True
        self.save()
        return True

    def add_to_list(self, title: str, category: str, year: Optional[int] = None) -> bool:
        if category not in LISTS:
            raise ValueError(f"unknown list '{category}' (use {LISTS})")
        m = self._movies.get(f"{title.strip().lower()}|{year or ''}")
        if not m:
            m = self.add(Movie(title=title, year=year, watched=(category != "watchlist")))
        if category not in m.lists:
            m.lists.append(category)
        if category == "watched":
            m.watched = True
        self.save()
        return True

    def remove_from_list(self, title: str, category: str, year: Optional[int] = None) -> bool:
        m = self._movies.get(f"{title.strip().lower()}|{year or ''}")
        if not m or category not in m.lists:
            return False
        m.lists.remove(category)
        self.save()
        return True

    def in_list(self, category: str) -> list["Movie"]:
        return [m for m in self._movies.values() if category in m.lists]

    def remove(self, title: str, year: Optional[int] = None) -> bool:
        ok = self._movies.pop(f"{title.strip().lower()}|{year or ''}", None) is not None
        if ok:
            self.save()
        return ok

    # ---- queries ----
    def all(self) -> list[Movie]:
        return list(self._movies.values())

    def search(self, term: str) -> list[Movie]:
        t = term.strip().lower()
        return [m for m in self._movies.values() if t in m.title.lower()]

    def filter(self, *, watched: Optional[bool] = None,
               min_rating: Optional[float] = None,
               tag: Optional[str] = None) -> list[Movie]:
        out = self.all()
        if watched is not None:
            out = [m for m in out if m.watched == watched]
        if min_rating is not None:
            out = [m for m in out if (m.rating or -1) >= min_rating]
        if tag is not None:
            out = [m for m in out if tag in m.tags]
        return out

    def stats(self) -> dict:
        rated = [m.rating for m in self._movies.values() if m.rating is not None]
        watched = [m for m in self._movies.values() if m.watched]
        return {
            "total": len(self._movies),
            "watched": len(watched),
            "rated": len(rated),
            "avg_rating": round(sum(rated) / len(rated), 2) if rated else None,
        }
