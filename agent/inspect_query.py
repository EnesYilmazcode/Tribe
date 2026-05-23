"""
Inspect REAL query() output to ground the UI/mock in reality and surface data-quality
issues. Read-only. Run from agent/:  python inspect_query.py

Reports, per (cause, geo) probe: row count, score spread, and flags for messy fields
(name format, missing employer/occupation/city, empty history). Then dumps 2 full records.
"""

import json
from collections import Counter

from clickhouse_client import ping, query

PROBES = [
    {"cause": "environment", "geo": "WA", "min_amount": 1000},
    {"cause": "environment", "geo": None, "min_amount": 2000},
    {"cause": "healthcare", "geo": "CA", "min_amount": 1000},
    {"cause": "education", "geo": None, "min_amount": 500},
    {"causes": ["environment", "social_welfare"], "geo": "CA", "min_amount": 1000},
]


def flags(rec: dict) -> list[str]:
    f = []
    name = rec.get("name", "")
    if not name.strip():
        f.append("EMPTY_NAME")
    if "," in name:
        f.append("NAME_HAS_COMMA(last,first?)")
    if any(ch.isdigit() for ch in name):
        f.append("NAME_HAS_DIGIT")
    if not rec.get("employer", "").strip():
        f.append("NO_EMPLOYER")
    elif rec["employer"].lower() in {"retired", "none", "n/a", "not employed", "self", "self-employed", "self employed"}:
        f.append(f"EMPLOYER_NONINFO({rec['employer']})")
    if not rec.get("occupation", "").strip():
        f.append("NO_OCCUPATION")
    if not rec.get("city", "").strip():
        f.append("NO_CITY")
    if not rec.get("donation_history"):
        f.append("NO_HISTORY")
    # contact fields the product wants but FEC never provides
    if "email" not in rec and "phone" not in rec:
        pass  # expected — noted in summary
    return f


def main() -> None:
    print("ping:", ping())
    all_flags = Counter()
    total = 0

    for probe in PROBES:
        try:
            rows = query(limit=10, **probe)
        except Exception as e:
            print(f"\n## probe {probe} -> ERROR: {e}")
            continue
        scores = [r["affinity_score"] for r in rows]
        print(f"\n## probe {probe}")
        print(f"   rows={len(rows)}  score[min/max]={min(scores, default='-')}/{max(scores, default='-')}")
        for r in rows:
            total += 1
            for fl in flags(r):
                all_flags[fl] += 1
        # show the messy bits compactly
        for r in rows[:3]:
            print(f"   - {r['name']!r:32} | emp={r.get('employer','')!r:18} | occ={r.get('occupation','')!r:16} | {flags(r)}")

    print("\n## DATA-QUALITY SUMMARY (across", total, "records)")
    for fl, n in all_flags.most_common():
        print(f"   {n:4}  {fl}")
    print("   NOTE: no email/phone fields exist in FEC data — contact info needs enrichment/append.")

    # dump 2 full real records so we can mirror the exact shape in the mock
    sample = query(cause="environment", geo="WA", min_amount=1000, limit=2)
    print("\n## SAMPLE FULL RECORDS")
    print(json.dumps(sample, indent=2, default=str)[:3000])


if __name__ == "__main__":
    main()
