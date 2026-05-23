"""
Bake a REAL, enriched run into web/sample_prospects.json so the demo is instant
and recording-proof. `?demo=1` (and the SSE fallback) then replay this exact run
with the activity-stream animation — no live API waits, no flaky calls on camera.

    python build_demo_snapshot.py
    python build_demo_snapshot.py "healthcare donors in California who gave $1,000+"

Pipeline: parse_ask -> expand_causes -> query() -> enrich_top() (clean Gemini
enrichment) -> write JSON. Re-run anytime the data changes (e.g. after the dedup
fix) to refresh the cached demo.
"""
import os
import sys
import json

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, os.path.join(_ROOT, "agent"))
sys.path.insert(0, _HERE)

from dotenv import load_dotenv
load_dotenv(os.path.join(_ROOT, ".env"))

from query_clean import query as clean_query   # dedup-safe (honest totals, no dup history)
from nl_parse import parse_ask
from enrich_clean import enrich_top
from draft_email import draft_top

DEFAULT_ASK = "major environment donors in California who gave $1,000+"
SNAPSHOT_PATH = os.path.join(_ROOT, "web", "sample_prospects.json")
LIMIT = 12          # tighter than 20 — a cleaner scroll for a 3-min demo
ENRICH_N = 3        # enrich the top 3 (the ones the demo will dwell on)


def main() -> None:
    ask = " ".join(sys.argv[1:]) or DEFAULT_ASK
    print(f"ask: {ask}")
    parsed = parse_ask(ask)
    causes = parsed["causes"] or ["environment"]
    print(f"parsed: causes={causes} geo={parsed['geo']} min=${parsed['min_amount']} (via {parsed['source']})")

    # Primary cause only (no adjacency expansion) — keeps the demo on-topic and
    # avoids pulling mis-tagged committees from adjacent causes (e.g. RJC PAC tagged 'energy').
    prospects = clean_query(causes=causes, geo=parsed["geo"],
                            min_amount=parsed["min_amount"], limit=LIMIT)
    if not prospects:
        print("No prospects returned — is the contributions table populated for this cause/geo?")
        return
    print(f"query: {len(prospects)} prospects")

    print(f"enriching top {ENRICH_N} via live web (one-time, cached into the snapshot)...")
    enrich_top(prospects, n=ENRICH_N)

    print(f"drafting outreach emails for top {ENRICH_N}...")
    draft_top(prospects, n=ENRICH_N)

    # Put the donor's individual-contribution search FIRST so clicking the top
    # citation verifies the *person's* history, not just the committee.
    for p in prospects:
        cr = p.get("cited_reasons") or []
        cr.sort(key=lambda r: 0 if "individual-contributions" in (r.get("source_url") or "") else 1)
        p["cited_reasons"] = cr

    with open(SNAPSHOT_PATH, "w", encoding="utf-8") as f:
        json.dump(prospects, f, indent=2, default=str)

    top = prospects[0]
    enriched = sum(1 for p in prospects if p.get("enrichment"))
    print(f"\nwrote {len(prospects)} prospects -> {SNAPSHOT_PATH}")
    print(f"top donor: {top['name']} · score {top['affinity_score']} · ${top.get('total_given', 0):,}")
    print(f"enriched: {enriched}/{len(prospects)}")
    if top.get("total_given", 0) > 1_000_000:
        print("\n⚠ top total looks inflated (>$1M) — if the 4x dedup fix isn't in yet,")
        print("  re-run this AFTER `OPTIMIZE TABLE ... FINAL [DEDUPLICATE]` to refresh real numbers.")


if __name__ == "__main__":
    main()
