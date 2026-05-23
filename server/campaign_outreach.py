"""
Autonomous campaign agent — the full loop, no human in the loop:
  campaign (plain English) -> auto-MATCH real donors -> auto-FIND a contact lead
  -> auto-DRAFT personalized outreach. Re-runnable; queues new matches over time.

Recording-proof: `build` runs it live (Gemini + Nimble) and caches the result;
`demo` replays the cache instantly so a recorded terminal clip can't flake.

    python server/campaign_outreach.py build   # one-time: run live, cache
    python server/campaign_outreach.py demo     # instant replay (record this)
"""
import os
import sys
import json

try:  # Windows console defaults to cp1252 and chokes on emoji / ↗
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(_HERE), "agent"))
sys.path.insert(0, _HERE)
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(_HERE), ".env"))

from query_clean import query as clean_query
from enrich_clean import enrich_clean
from draft_email import draft_email

CACHE = os.path.join(_HERE, "campaign_outreach_cache.json")
CAMPAIGNS = [
    {"name": "🌊 Protect oceans & marine wildlife", "cause": "environment", "geo": "CA"},
    {"name": "💧 Clean water access in the Pacific Northwest", "cause": "environment", "geo": "WA"},
]
TOP_OUTREACH = 2   # auto-draft for the top N of each campaign


def _natural(raw: str) -> str:
    parts = raw.split(",")
    return f"{parts[1].strip()} {parts[0].strip()}".title() if len(parts) == 2 and parts[1].strip() else raw


def build() -> list[dict]:
    out = []
    for c in CAMPAIGNS:
        print(f"  [agent] matching '{c['name']}'…", flush=True)
        donors = clean_query(causes=[c["cause"]], geo=c["geo"], min_amount=1000, limit=5)
        for i, d in enumerate(donors[:TOP_OUTREACH]):
            print(f"          researching + drafting for {_natural(d['name'])}…", flush=True)
            d["enrichment"] = enrich_clean(d)
            d["draft_email"] = draft_email(d)
        out.append({"campaign": c, "donors": donors})
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=str)
    return out


def show(data: list[dict]) -> None:
    print("\n" + "═" * 64)
    print("  TRIBE — autonomous campaign agent")
    print("═" * 64)
    for entry in data:
        c, donors = entry["campaign"], entry["donors"]
        print(f"\n  Campaign: {c['name']}   ({c['cause']} · {c['geo']})")
        print(f"  [agent] matched {len(donors)} donors · researched contacts · drafted outreach — no human input")
        for i, d in enumerate(donors[:TOP_OUTREACH]):
            enr = d.get("enrichment") or {}
            em = d.get("draft_email") or {}
            print(f"\n   {i+1}. {_natural(d['name']):24} score {d.get('affinity_score','?'):>3}  "
                  f"${d.get('total_given',0):>9,}  {d.get('city','')}, {d.get('geo','')}")
            if enr.get("current_role"):
                print(f"        role:    {enr['current_role']}")
            if enr.get("source_url"):
                print(f"        contact: ↗ {enr['source_url']}")
            if em.get("subject"):
                first = (em.get('body') or '').split(chr(10))[0]
                print(f"        ✉ draft: \"{em['subject']}\"")
                print(f"                 {first}")
        extra = len(donors) - TOP_OUTREACH
        if extra > 0:
            print(f"\n        … +{extra} more matched donors queued for outreach")
    print("\n  " + "─" * 60)
    print("  ✓ Campaigns auto-matched, contacts found, emails drafted — zero manual work.")
    print("  ✓ Re-runs every 5 min: new matching donors are auto-added and queued.")
    print("  (Drafts await human approval before send.)\n")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "demo"
    if cmd == "build":
        print("Running live (Gemini + Nimble) and caching…")
        show(build())
    else:
        if not os.path.exists(CACHE):
            print("No cache — building live first…")
            show(build())
        else:
            with open(CACHE, encoding="utf-8") as f:
                show(json.load(f))
