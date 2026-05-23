"""
Demo-readiness validator. Run this once the contributions table is populated to
see which natural-language ask produces the best-looking real donor results.

    python -m server.validate_demo            # runs the candidate asks
    python server/validate_demo.py "custom ask here"

For each ask it prints: parsed params, result count, and the top donors
(name, score, total given, employer, cause tags), plus quality flags. Skips
Nimble enrichment (too slow); this is about whether the ClickHouse layer returns
demo-worthy donors.
"""
import sys
import os

try:  # Windows console defaults to cp1252 and chokes on ✓/⚠/→
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "agent"))
sys.path.insert(0, os.path.join(ROOT, "server"))
from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"))

import clickhouse_client as ch
from cause_synonyms import expand_causes
from nl_parse import parse_ask

# Causes that are now party-proxies (DEM->civil_rights, REP->small_business,
# IND->social_welfare) via candidate tagging — avoid these for the demo ask.
PARTY_PROXY = {"civil_rights", "small_business", "social_welfare"}

CANDIDATE_ASKS = [
    "major environment and clean-water donors in Washington who gave $1,000+",
    "healthcare donors in California who gave $500+",
    "labor and worker-rights donors in New York",
    "environment donors in Oregon",
    "education donors in Texas who gave $1,000+",
]


def _flags(causes, prospects):
    out = []
    if any(c in PARTY_PROXY for c in causes):
        out.append("⚠ uses a party-proxy cause (civil_rights/small_business/social_welfare)")
    if not prospects:
        out.append("✗ ZERO results")
    else:
        named = [p for p in prospects if p.get("name", "").strip()]
        if len(named) < len(prospects):
            out.append(f"⚠ {len(prospects)-len(named)} blank names")
        if all(p.get("total_given", 0) < 1000 for p in prospects):
            out.append("⚠ all donors under $1k (thin)")
    return out or ["✓ looks clean"]


def run_ask(ask: str):
    print(f"\n{'='*70}\nASK: {ask}")
    parsed = parse_ask(ask)
    causes = parsed["causes"]
    expanded = expand_causes(causes)
    print(f"  parsed: causes={causes} geo={parsed['geo']} min=${parsed['min_amount']} (via {parsed['source']})")
    print(f"  expanded causes: {expanded}")
    try:
        prospects = ch.query(causes=expanded, geo=parsed["geo"], min_amount=parsed["min_amount"], limit=10)
    except Exception as e:
        print(f"  query ERROR: {e}")
        return
    print(f"  results: {len(prospects)}")
    for p in prospects[:5]:
        print(f"    {p.get('affinity_score','?'):>3}  {p.get('name',''):28} "
              f"${p.get('total_given',0):>9,}  {p.get('num_donations','?')} gifts  "
              f"{p.get('city','')}, {p.get('geo','')}  | {p.get('employer','')[:30]} "
              f"| tags={p.get('cause_tags',[])}")
    for f in _flags(causes, prospects):
        print(f"  {f}")


if __name__ == "__main__":
    contrib = ch._get_client().query(f"SELECT count() FROM {ch.CLICKHOUSE_DB}.contributions").result_rows[0][0]
    print(f"contributions rows: {contrib:,}")
    if contrib == 0:
        print("⚠ contributions table is empty — run this again once the load finishes.")
    asks = [" ".join(sys.argv[1:])] if len(sys.argv) > 1 else CANDIDATE_ASKS
    for a in asks:
        run_ask(a)
    print(f"\n{'='*70}\nPick the ask with the cleanest results and a non-party-proxy cause for the demo.")
