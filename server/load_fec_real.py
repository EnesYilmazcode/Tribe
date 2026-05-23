"""
Load REAL FEC individual contributions into ClickHouse via the official FEC API.

This replaces the synthetic smoke-test data with real, citeable donor records.
Scoped to the demo: contributions to environment-tagged committees from donors in
chosen states. The FEC API is the official public source — the same records our
fec.gov citations point to. (Nimble is NOT used here; Nimble only enriches a known
person afterward. The donor universe comes from the FEC.)

Setup:
  1. Get a FREE personal FEC API key (instant): https://api.data.gov/signup/
  2. Put it in .env as FEC_API_KEY=...   (DEMO_KEY works but is capped at 40/hour)

Run:
  python server/load_fec_real.py --states WA OR --min-amount 200 --max-committees 25
  python server/load_fec_real.py --truncate ...   # clear synthetic rows first

A personal key allows 1000 calls/hour, plenty for a scoped demo load.
"""
import sys
import os
import time
import argparse
from datetime import datetime

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "agent"))
from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"))
import clickhouse_client as ch

FEC_API = "https://api.open.fec.gov/v1/schedules/schedule_a/"
API_KEY = os.environ.get("FEC_API_KEY", "DEMO_KEY")


def env_committee_ids(limit: int) -> list[tuple[str, str]]:
    """Real environment-tagged PAC committees from our DB (not candidate committees)."""
    c = ch._get_client()
    rows = c.query(f"""
        SELECT DISTINCT m.cmte_id, any(m.cmte_nm)
        FROM {ch.CLICKHOUSE_DB}.committee_causes cc
        JOIN {ch.CLICKHOUSE_DB}.committees m ON cc.cmte_id = m.cmte_id
        WHERE cc.cause_tag = 'environment' AND m.cmte_tp != 'P'
        GROUP BY m.cmte_id
        LIMIT {limit}
    """).result_rows
    return [(r[0], r[1]) for r in rows]


def fetch_contributions(cmte_id: str, states: list[str], min_amount: int,
                        cycle: int, max_pages: int = 3) -> list[dict]:
    """Pull real individual contributions to one committee via keyset pagination."""
    out = []
    last_index = last_amt = None
    for _ in range(max_pages):
        params = {
            "api_key": API_KEY, "committee_id": cmte_id,
            "contributor_state": states, "two_year_transaction_period": cycle,
            "min_amount": min_amount, "is_individual": "true",
            "per_page": 100, "sort": "-contribution_receipt_amount",
        }
        if last_index is not None:
            params["last_index"] = last_index
            params["last_contribution_receipt_amount"] = last_amt
        r = requests.get(FEC_API, params=params, timeout=30)
        if r.status_code == 429:
            print("  ! rate limited (429) — get a personal FEC_API_KEY for a larger load")
            break
        r.raise_for_status()
        body = r.json()
        results = body.get("results", [])
        out.extend(results)
        pg = body.get("pagination", {})
        idxs = pg.get("last_indexes") or {}
        if not results or not idxs:
            break
        last_index = idxs.get("last_index")
        last_amt = idxs.get("last_contribution_receipt_amount")
        time.sleep(0.4)  # be gentle on the API
    return out


def to_row(rec: dict) -> tuple | None:
    try:
        dt = rec.get("contribution_receipt_date")
        d = datetime.fromisoformat(dt).date() if dt else None
        if d is None:
            return None
        return (
            rec.get("committee_id", "") or "",
            (rec.get("contributor_name") or "").strip(),
            (rec.get("contributor_city") or "").strip(),
            (rec.get("contributor_state") or "").strip(),
            (rec.get("contributor_zip") or "").strip(),
            (rec.get("contributor_employer") or "").strip(),
            (rec.get("contributor_occupation") or "").strip(),
            d,
            int(rec.get("contribution_receipt_amount") or 0),
            int(rec.get("sub_id") or 0),
        )
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--states", nargs="+", default=["WA", "OR"])
    ap.add_argument("--min-amount", type=int, default=200)
    ap.add_argument("--cycle", type=int, default=2024)
    ap.add_argument("--max-committees", type=int, default=25)
    ap.add_argument("--truncate", action="store_true",
                    help="DELETE existing contributions first (clears synthetic data)")
    args = ap.parse_args()

    if API_KEY == "DEMO_KEY":
        print("⚠ Using DEMO_KEY (40 calls/hour). Set FEC_API_KEY in .env for a real load.")
    c = ch._get_client()
    db = ch.CLICKHOUSE_DB

    if args.truncate:
        print("Truncating contributions (removing synthetic data)...")
        c.command(f"TRUNCATE TABLE {db}.contributions")

    committees = env_committee_ids(args.max_committees)
    print(f"Loading real contributions to {len(committees)} environment committees, "
          f"states={args.states}, min=${args.min_amount}, cycle={args.cycle}")

    rows, seen = [], set()
    for cmte_id, name in committees:
        recs = fetch_contributions(cmte_id, args.states, args.min_amount, args.cycle)
        added = 0
        for rec in recs:
            row = to_row(rec)
            if row and row[9] not in seen:   # dedup by sub_id
                seen.add(row[9]); rows.append(row); added += 1
        if added:
            print(f"  {cmte_id} {name[:40]:40} +{added}")

    if not rows:
        print("No real rows fetched (rate limit or no matches). Need a personal FEC_API_KEY.")
        return

    cols = ["cmte_id", "contributor_nm", "city", "state", "zip_code", "employer",
            "occupation", "transaction_dt", "transaction_amt", "sub_id"]
    c.insert(f"{db}.contributions", rows, column_names=cols)
    print(f"\nInserted {len(rows):,} REAL contributions. "
          f"Distinct donors: {len({r[1] for r in rows}):,}")


if __name__ == "__main__":
    main()
