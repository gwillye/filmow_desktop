"""Runnable demo + self-check for the local movie watch-history store."""
import tempfile
from pathlib import Path
from moviehistory.store import Movie, MovieStore


def main() -> None:
    tmp = Path(tempfile.gettempdir()) / "moviehistory_demo.json"
    if tmp.exists():
        tmp.unlink()
    store = MovieStore(tmp)

    store.add(Movie("Blade Runner 2049", 2017, rating=5.0, tags=["sci-fi", "favorite"]))
    store.add(Movie("Parasite", 2019, rating=4.5, tags=["thriller"]))
    store.add(Movie("The Room", 2003, rating=1.0, tags=["so-bad-its-good"]))
    store.add(Movie("Dune", 2021, watched=False, tags=["sci-fi"]))  # watchlist

    store.rate("Dune", 4.5, year=2021)  # watched it now

    print("All movies:")
    for m in store.all():
        print(f"  {m.title} ({m.year}) rating={m.rating} watched={m.watched}")

    print("\nFavorites (rating >= 4.5):")
    for m in store.filter(min_rating=4.5):
        print(f"  {m.title}")

    print("\nStats:", store.stats())

    # ---- self-check: persistence + queries ----
    store2 = MovieStore(tmp)                      # reload from disk
    assert len(store2.all()) == 4, "persistence failed"
    assert store2.search("blade")[0].year == 2017
    assert all(m.watched for m in store2.all()), "Dune should be watched after rate()"
    assert store2.stats()["avg_rating"] == round((5.0 + 4.5 + 1.0 + 4.5) / 4, 2)
    assert {m.title for m in store2.filter(min_rating=4.5)} == {
        "Blade Runner 2049", "Parasite", "Dune"}
    tmp.unlink()
    print("\nself-check: OK (persistence, search, rate, filter, stats)")


if __name__ == "__main__":
    main()
