"""
Continuous auto-matching agent — the autonomy money-shot.

You describe a campaign in plain language ("protect oceans and marine wildlife").
The agent parses it, queries real FEC giving, and AUTO-ADDS the top matching donors
to that campaign's pipeline — no human picks anyone. Re-run on a schedule and it
only surfaces NEWLY-matched contacts as the data grows, looping them in automatically.

Standalone (no edits to main.py / frontend). Reuses parse_ask + query_clean.

    python server/auto_match.py seed                 # create a few demo campaigns
    python server/auto_match.py run                   # one cycle: auto-add new matches
    python server/auto_match.py watch --interval 30   # continuous loop (the autonomy story)
    python server/auto_match.py list                  # campaigns + their pipelines
    python server/auto_match.py add "fund cancer research and hospitals in California"
"""
import os
import sys
import json
import time
import argparse
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "server"))
sys.path.insert(0, os.path.join(ROOT, "agent"))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"))

from nl_parse import parse_ask
from query_clean import query as query_clean

STORE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "campaigns.json")
TOP_N = 10

_SEED = [
    "protect oceans and marine wildlife on the west coast",
    "fund cancer research and hospitals in California",
    "support workers and labor unions in New York",
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%S")


def load() -> list[dict]:
    if os.path.exists(STORE):
        with open(STORE, encoding="utf-8") as f:
            return json.load(f)
    return []


def save(campaigns: list[dict]) -> None:
    with open(STORE, "w", encoding="utf-8") as f:
        json.dump(campaigns, f, indent=2)


def _key(p: dict) -> str:
    return f"{p['name']}|{p['geo']}"


def add_campaign(description: str) -> dict:
    parsed = parse_ask(description)
    campaigns = load()
    cid = max([c["id"] for c in campaigns], default=0) + 1
    camp = {
        "id": cid,
        "description": description,
        "causes": parsed["causes"] or ["social_welfare"],
        "geo": parsed["geo"],
        "min_amount": parsed["min_amount"],
        "pipeline": [],   # auto-matched contacts (with first_matched time)
        "seen": [],       # keys we've already matched, to detect new ones
    }
    campaigns.append(camp)
    save(campaigns)
    print(f"+ campaign #{cid}: \"{description}\"")
    print(f"  parsed -> causes={camp['causes']} geo={camp['geo']} min=${camp['min_amount']}")
    return camp


def run_cycle(verbose: bool = True) -> int:
    """For each campaign: query real FEC data, auto-add NEWLY-matched donors."""
    campaigns = load()
    total_new = 0
    for camp in campaigns:
        # primary parsed causes only (no adjacency expansion) to stay on-topic
        try:
            matches = query_clean(
                causes=camp["causes"], geo=camp.get("geo"),
                min_amount=camp.get("min_amount", 200), limit=TOP_N,
            )
        except Exception as e:  # noqa: BLE001
            print(f"  ! campaign #{camp['id']} query failed: {e}")
            continue
        seen = set(camp["seen"])
        new = [m for m in matches if _key(m) not in seen]
        for m in new:
            camp["pipeline"].append({
                "name": m["name"], "geo": m["geo"], "city": m.get("city", ""),
                "affinity_score": m["affinity_score"], "total_given": m["total_given"],
                "employer": m.get("employer", ""),
                "first_matched": _now(),
            })
            camp["seen"].append(_key(m))
        total_new += len(new)
        if verbose:
            print(f"[{_now()}] campaign #{camp['id']} \"{camp['description'][:48]}\" "
                  f"-> {len(new)} NEW matched (pipeline now {len(camp['pipeline'])})")
            for m in new[:5]:
                print(f"      auto-added: {m['name']:24} score {m['affinity_score']:>3}  "
                      f"${m['total_given']:>9,}  {m.get('city','')}, {m['geo']}")
    save(campaigns)
    return total_new


def watch(interval: int) -> None:
    print(f"Auto-match agent watching {len(load())} campaigns; re-checking every {interval}s. Ctrl-C to stop.")
    cycle = 0
    while True:
        cycle += 1
        print(f"\n=== cycle {cycle} @ {_now()} ===")
        n = run_cycle()
        if n == 0:
            print("  (no new contacts this cycle — pipelines steady)")
        time.sleep(interval)


def show() -> None:
    for c in load():
        print(f"\n#{c['id']} \"{c['description']}\"  [{', '.join(c['causes'])} · {c.get('geo') or 'all'}]")
        for p in sorted(c["pipeline"], key=lambda x: x["affinity_score"], reverse=True):
            print(f"   {p['affinity_score']:>3}  {p['name']:24} ${p['total_given']:>9,}  "
                  f"{p.get('city','')}, {p['geo']}  (matched {p['first_matched']})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("seed")
    sub.add_parser("run")
    sub.add_parser("list")
    w = sub.add_parser("watch"); w.add_argument("--interval", type=int, default=30)
    a = sub.add_parser("add"); a.add_argument("description", nargs="+")
    args = ap.parse_args()

    if args.cmd == "seed":
        if load():
            print("campaigns.json already has campaigns; use 'add' or delete the file to reseed.")
        else:
            for d in _SEED:
                add_campaign(d)
            print("\nSeeded. Run `python server/auto_match.py run` to auto-fill pipelines.")
    elif args.cmd == "add":
        add_campaign(" ".join(args.description))
    elif args.cmd == "run":
        n = run_cycle()
        print(f"\nCycle complete — {n} new contacts auto-added across all campaigns.")
    elif args.cmd == "watch":
        watch(args.interval)
    elif args.cmd == "list":
        show()
    else:
        ap.print_help()
