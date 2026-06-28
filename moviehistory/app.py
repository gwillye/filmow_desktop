"""Local web app (Flask) for the personal movie catalog — Filmow-style.

Runs on your machine, organizes films into four lists (seen / want-to-see /
want-to-rewatch / favorites) and can search a free public movie API (TMDB)
when TMDB_API_KEY is set, falling back to local search otherwise.

Run:  python -m moviehistory.app      # http://127.0.0.1:5000
"""
from __future__ import annotations
from flask import Flask, request, redirect, url_for, render_template_string
from .store import MovieStore, LISTS, LIST_LABELS
from . import tmdb

PAGE = """
<!doctype html><html lang="pt-br"><head><meta charset="utf-8">
<title>Meu Filmow local</title>
<style>
 body{font-family:system-ui,Arial,sans-serif;max-width:920px;margin:2rem auto;padding:0 1rem;background:#10131a;color:#e8e8e8}
 a{color:#6cf} h1{margin-bottom:0} .muted{color:#8a93a6}
 .lists{display:grid;grid-template-columns:repeat(2,1fr);gap:1rem;margin-top:1rem}
 .card{background:#1b2030;border-radius:10px;padding:1rem}
 .card h3{margin:.2rem 0 .6rem} li{margin:.15rem 0}
 form.search{margin:1rem 0;display:flex;gap:.5rem} input[type=text]{flex:1;padding:.5rem;border-radius:6px;border:1px solid #333;background:#0d1017;color:#eee}
 button{padding:.4rem .7rem;border-radius:6px;border:0;background:#2b6cb0;color:#fff;cursor:pointer}
 .res{background:#1b2030;border-radius:10px;padding:.6rem 1rem;margin:.4rem 0}
 .add{display:inline-flex;gap:.3rem;margin-left:.5rem}
</style></head><body>
<h1>🎬 Meu catálogo de filmes</h1>
<p class="muted">Rodando localmente. API pública: {{ 'TMDB ligada' if tmdb_on else 'offline (defina TMDB_API_KEY p/ buscar online)' }}.</p>

<form class="search" action="{{ url_for('search') }}" method="get">
  <input type="text" name="q" placeholder="Buscar filme…" value="{{ q }}">
  <button>Buscar</button>
</form>

{% if results is not none %}
  <h2>Resultados para “{{ q }}”</h2>
  {% for r in results %}
   <div class="res"><b>{{ r.title }}</b> {{ '('~r.year~')' if r.year }}
     <span class="add">
     {% for c in lists_order %}
       <form action="{{ url_for('add') }}" method="post" style="display:inline">
        <input type="hidden" name="title" value="{{ r.title }}">
        <input type="hidden" name="year" value="{{ r.year }}">
        <input type="hidden" name="category" value="{{ c }}">
        <button title="add to {{ labels[c] }}">+ {{ labels[c] }}</button>
       </form>
     {% endfor %}
     </span>
   </div>
  {% else %}<p class="muted">Nada encontrado.</p>{% endfor %}
{% endif %}

<div class="lists">
 {% for c in lists_order %}
  <div class="card"><h3>{{ labels[c] }} <span class="muted">({{ lists[c]|length }})</span></h3>
   <ul>{% for m in lists[c] %}<li>{{ m.title }}{{ ' ('~m.year~')' if m.year }}{% if m.rating %} — {{ m.rating }}★{% endif %}</li>
       {% else %}<li class="muted">vazio</li>{% endfor %}</ul>
  </div>
 {% endfor %}
</div>
</body></html>
"""


def create_app(db_path: str = "movies.json") -> Flask:
    app = Flask(__name__)
    store = MovieStore(db_path)

    def ctx(results=None, q=""):
        return dict(lists={c: store.in_list(c) for c in LISTS},
                    lists_order=LISTS, labels=LIST_LABELS,
                    results=results, q=q, tmdb_on=tmdb.available())

    @app.get("/")
    def home():
        return render_template_string(PAGE, **ctx())

    @app.get("/search")
    def search():
        q = request.args.get("q", "").strip()
        if not q:
            return redirect(url_for("home"))
        results = tmdb.search(q)
        if not results:  # offline / no key → local catalog
            results = [{"title": m.title, "year": m.year or "", "overview": ""}
                       for m in store.search(q)]
        return render_template_string(PAGE, **ctx(results=results, q=q))

    @app.post("/add")
    def add():
        year = request.form.get("year") or ""
        store.add_to_list(request.form["title"], request.form["category"],
                          int(year) if year.isdigit() else None)
        return redirect(url_for("home"))

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
