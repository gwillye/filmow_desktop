"""Self-check for the lists + the Flask local site (no server needed)."""
import tempfile
from pathlib import Path
from moviehistory.store import MovieStore, LISTS
from moviehistory.app import create_app

tmp = Path(tempfile.gettempdir()) / "filmow_verify.json"
if tmp.exists():
    tmp.unlink()

# ---- store: four lists ----
s = MovieStore(tmp)
s.add_to_list("Parasite", "watched", 2019)
s.add_to_list("Parasite", "favorite", 2019)      # a movie can be in several lists
s.add_to_list("Dune", "watchlist", 2021)
s.add_to_list("Interstellar", "rewatch", 2014)
assert {m.title for m in s.in_list("watched")} == {"Parasite"}
assert {m.title for m in s.in_list("favorite")} == {"Parasite"}
assert {m.title for m in s.in_list("watchlist")} == {"Dune"}
assert {m.title for m in s.in_list("rewatch")} == {"Interstellar"}
assert set(LISTS) == {"watched", "watchlist", "rewatch", "favorite"}
print("store lists: OK (4 lists; multi-list membership)")

# ---- Flask app via test client ----
app = create_app(str(tmp))
c = app.test_client()
assert c.get("/").status_code == 200
assert b"Meu cat" in c.get("/").data            # page renders
r = c.post("/add", data={"title": "Whiplash", "year": "2014", "category": "favorite"})
assert r.status_code in (302, 303)              # redirect after add
assert any(m.title == "Whiplash" for m in MovieStore(str(tmp)).in_list("favorite"))
assert c.get("/search?q=paras").status_code == 200   # local fallback search
print("flask app: OK (home renders, add works, search responds)")

tmp.unlink()
print("\nverify_app: ALL OK")
