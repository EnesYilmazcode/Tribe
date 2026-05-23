"""
Quick smoke-test: pull a small sample of real FEC individual contributions
via the FEC REST API (no bulk download needed) and insert into ClickHouse.

Usage:
    python3 load_fec_sample.py                    # ~2000 rows from WA + CA
    python3 load_fec_sample.py --rows 500         # smaller sample

This is intentionally small — use load_fec.py for full bulk load.
"""

import argparse
import os
import time
from datetime import date

import certifi
import requests
import clickhouse_connect
from dotenv import load_dotenv

os.environ.setdefault("SSL_CERT_FILE", certifi.where())
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

CLICKHOUSE_HOST     = os.environ["CLICKHOUSE_HOST"]
CLICKHOUSE_PORT     = int(os.environ.get("CLICKHOUSE_PORT", 8443))
CLICKHOUSE_USER     = os.environ.get("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.environ["CLICKHOUSE_PASSWORD"]
CLICKHOUSE_DB       = os.environ.get("CLICKHOUSE_DB", "donor_agent")

FEC_API_BASE = "https://api.open.fec.gov/v1"
FEC_API_KEY  = "DEMO_KEY"   # 30 req/hour; plenty for a smoke test
CYCLE        = 2024
PER_PAGE     = 100


def get_ch_client():
    return clickhouse_connect.get_client(
        host=CLICKHOUSE_HOST, port=CLICKHOUSE_PORT,
        username=CLICKHOUSE_USER, password=CLICKHOUSE_PASSWORD,
        secure=True, verify=certifi.where(),
    )


def fetch_page(state: str, min_amount: int, last_index: str | None,
               last_amount: str | None) -> dict:
    params = {
        "state":                        state,
        "min_amount":                   min_amount,
        "two_year_transaction_period":  CYCLE,
        "entity_type":                  "IND",
        "sort":                         "-contribution_receipt_amount",
        "per_page":                     PER_PAGE,
        "api_key":                      FEC_API_KEY,
    }
    if last_index and last_amount:
        params["last_index"]                       = last_index
        params["last_contribution_receipt_amount"] = last_amount

    resp = requests.get(f"{FEC_API_BASE}/schedules/schedule_a/",
                        params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def parse_row(r: dict) -> tuple | None:
    dt_str = r.get("contribution_receipt_date")
    if not dt_str:
        return None
    try:
        dt = date.fromisoformat(dt_str[:10])
    except ValueError:
        return None

    sub_id_raw = r.get("sub_id")
    try:
        sub_id = int(sub_id_raw)
    except (TypeError, ValueError):
        return None

    amt_raw = r.get("contribution_receipt_amount")
    try:
        amt = int(float(amt_raw))
    except (TypeError, ValueError):
        return None

    return (
        r.get("committee_id") or "",
        r.get("contributor_name") or "",
        r.get("contributor_city") or "",
        r.get("contributor_state") or "",
        r.get("contributor_zip") or "",
        r.get("contributor_employer") or "",
        r.get("contributor_occupation") or "",
        dt,
        amt,
        sub_id,
    )


COLUMNS = ["cmte_id", "contributor_nm", "city", "state",
           "zip_code", "employer", "occupation",
           "transaction_dt", "transaction_amt", "sub_id"]


def fetch_page_with_retry(state, min_amount, last_index, last_amount,
                          max_retries=4) -> dict:
    for attempt in range(max_retries):
        try:
            return fetch_page(state, min_amount, last_index, last_amount)
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 429:
                wait = 15 * (2 ** attempt)
                print(f"  rate limited — waiting {wait}s...")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Max retries exceeded")


def load_state(client, state: str, target_rows: int) -> int:
    print(f"\nFetching {target_rows} contributions from {state}...")
    total_inserted, batch, last_index, last_amount, page = 0, [], None, None, 0

    while total_inserted + len(batch) < target_rows:
        data = fetch_page_with_retry(state, min_amount=200,
                                     last_index=last_index,
                                     last_amount=last_amount)
        results = data.get("results", [])
        if not results:
            break

        for r in results:
            parsed = parse_row(r)
            if parsed:
                batch.append(parsed)

        pagination   = data.get("pagination", {})
        last_indexes = pagination.get("last_indexes", {})
        last_index   = last_indexes.get("last_index")
        last_amount  = last_indexes.get("last_contribution_receipt_amount")
        page += 1

        # Insert every 200 rows so partial runs still save data
        if len(batch) >= 200:
            client.insert(f"{CLICKHOUSE_DB}.contributions", batch,
                          column_names=COLUMNS)
            total_inserted += len(batch)
            print(f"  page {page}: inserted batch → {total_inserted:,} total")
            batch = []

        if not last_index:
            break
        time.sleep(2)  # stay well under rate limit

    # Flush remainder
    if batch:
        client.insert(f"{CLICKHOUSE_DB}.contributions", batch,
                      column_names=COLUMNS)
        total_inserted += len(batch)
        print(f"  Flushed final batch → {total_inserted:,} total for {state}")

    return total_inserted


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=1000,
                        help="Target rows per state (default 1000)")
    parser.add_argument("--states", nargs="*", default=["WA", "CA"],
                        help="States to sample (default WA CA)")
    args = parser.parse_args()

    client = get_ch_client()

    before = client.query(f"SELECT count() FROM {CLICKHOUSE_DB}.contributions").result_rows[0][0]
    print(f"contributions before: {before:,}")

    total = 0
    for state in args.states:
        total += load_state(client, state, args.rows)

    after = client.query(f"SELECT count() FROM {CLICKHOUSE_DB}.contributions").result_rows[0][0]
    print(f"\nDone. Inserted {total:,} rows total.")
    print(f"contributions now: {after:,}")

    # Quick sanity query
    print("\nTop 5 donors by total giving (sample data):")
    r = client.query(f"""
        SELECT contributor_nm, state, sum(transaction_amt) AS total
        FROM {CLICKHOUSE_DB}.contributions
        GROUP BY contributor_nm, state
        ORDER BY total DESC
        LIMIT 5
    """)
    for row in r.result_rows:
        print(f"  {row[0].title():<35} {row[1]}  ${row[2]:,}")

    # Check how many hit tagged committees
    r2 = client.query(f"""
        SELECT count(DISTINCT c.contributor_nm) AS tagged_donors
        FROM {CLICKHOUSE_DB}.contributions c
        JOIN {CLICKHOUSE_DB}.committee_causes cc ON c.cmte_id = cc.cmte_id
    """)
    print(f"\nDonors to tagged committees (queryable): {r2.result_rows[0][0]:,}")


if __name__ == "__main__":
    main()
