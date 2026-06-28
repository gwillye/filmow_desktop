"""Command-line interface for the local movie watch-history store."""
from __future__ import annotations
import argparse
from .store import Movie, MovieStore


def _print(movies):
    if not movies:
        print("(none)")
        return
    for m in sorted(movies, key=lambda x: (-(x.rating or 0), x.title)):
        star = f"{m.rating:.1f}*" if m.rating is not None else " -- "
        yr = f"({m.year})" if m.year else ""
        tags = f"  #{' #'.join(m.tags)}" if m.tags else ""
        print(f"  {star}  {m.title} {yr}{tags}")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(prog="moviehistory", description="Local movie watch-history.")
    ap.add_argument("--db", default="movies.json", help="path to the JSON store")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="add a movie")
    a.add_argument("title")
    a.add_argument("--year", type=int)
    a.add_argument("--rating", type=float)
    a.add_argument("--tag", action="append", default=[])
    a.add_argument("--notes", default="")

    r = sub.add_parser("rate", help="rate a movie 0-5")
    r.add_argument("title"); r.add_argument("rating", type=float); r.add_argument("--year", type=int)

    s = sub.add_parser("search", help="search by title"); s.add_argument("term")
    lst = sub.add_parser("list", help="list movies")
    lst.add_argument("--min-rating", type=float); lst.add_argument("--tag")
    sub.add_parser("stats", help="show stats")

    args = ap.parse_args(argv)
    store = MovieStore(args.db)

    if args.cmd == "add":
        store.add(Movie(title=args.title, year=args.year, rating=args.rating,
                        tags=args.tag, notes=args.notes))
        print(f"added: {args.title}")
    elif args.cmd == "rate":
        print("rated" if store.rate(args.title, args.rating, args.year) else "not found")
    elif args.cmd == "search":
        _print(store.search(args.term))
    elif args.cmd == "list":
        _print(store.filter(min_rating=args.min_rating, tag=args.tag))
    elif args.cmd == "stats":
        for k, v in store.stats().items():
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
