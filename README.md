# 🎬 Local Movie Catalog (Filmow-style, runs on your machine)

A personal movie catalog that **runs locally**, calls a **free public movie API** (TMDB) to find films, and organizes them into four lists — **Já vi / Quero ver / Quero rever / Favoritos** (seen / want-to-see / want-to-rewatch / favorites). Built because [filmow.com](https://filmow.com/@gwillye) became unusable (login hangs behind anti-bot protection), and a movie history shouldn't be locked away in an account you can't reach.

## ✨ Features
- **Local web app** (Flask) — open it in the browser at `127.0.0.1:5000`, no account.
- **Four lists** (filmow-style): seen, want-to-see, want-to-rewatch, favorites — a film can be in several.
- **Search a free public API** (TMDB) when `TMDB_API_KEY` is set; **falls back to local search** offline.
- **JSON-backed store** you own (CRUD, ratings 0–5, tags, notes, stats) + a CLI.

## ▶️ Run it
```bash
pip install -r requirements.txt

# the local web app:
python -m moviehistory.app          # → http://127.0.0.1:5000
# (optional) online search:
#   set TMDB_API_KEY=...   (free key from themoviedb.org)  — works offline without it

# or the CLI:
python -m moviehistory.cli --db movies.json add "Parasite" --year 2019 --rating 4.5 --tag thriller
python -m moviehistory.cli --db movies.json stats
```

## 🗂️ Structure
```
filmow-desktop/
├── moviehistory/
│   ├── store.py    # JSON store: movies, ratings, the 4 lists, search/filter/stats
│   ├── tmdb.py     # free public movie API client (optional, graceful offline)
│   ├── cli.py      # command-line interface
│   └── app.py      # local Flask web app (the catalog UI)
├── demo.py         # store demo + self-check
└── verify_app.py   # self-check for the lists + the web app (no server needed)
```

## 🧪 Verified
Both `python demo.py` and `python verify_app.py` run green:
- `self-check: OK` (persistence, search, rate, filter, stats),
- `flask app: OK` (home renders, add works, search responds).

## 📌 Roadmap
- Show **posters/synopsis** from TMDB on the cards; one-click "mark as watched / rewatch".
- **Import** a Filmow/Letterboxd CSV export to migrate an existing history.
- Package as a one-click desktop launcher.

## 🛠️ Stack
Python · Flask · TMDB API (optional) · standard-library JSON store
