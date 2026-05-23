"""
Pre-compute Nimble enrichments for top donors and store persistently in ClickHouse.

Stored enrichments are served instantly by clickhouse_client.query() — no live
Nimble call needed at query time for donors already in this table.

Usage:
    python3 nimble_batch_enrich.py                          # top 10 per demo cause
    python3 nimble_batch_enrich.py --causes environment labor --top 25
    python3 nimble_batch_enrich.py --causes healthcare --geo CA --top 20
"""

import argparse
import os
import sys
import time

import certifi
import clickhouse_connect
from dotenv import load_dotenv

os.environ.setdefault("SSL_CERT_FILE", certifi.where())
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

# Make server/ importable so we can use enrich_clean
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "server"))
sys.path.insert(0, os.path.join(_ROOT, "agent"))

from enrich_clean import enrich_clean  # noqa: E402

CLICKHOUSE_HOST     = os.environ["CLICKHOUSE_HOST"]
CLICKHOUSE_PORT     = int(os.environ.get("CLICKHOUSE_PORT", 8443))
CLICKHOUSE_USER     = os.environ.get("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.environ["CLICKHOUSE_PASSWORD"]
CLICKHOUSE_DB       = os.environ.get("CLICKHOUSE_DB", "donor_agent")

DEMO_CAUSES = ["environment", "healthcare", "labor", "energy"]


def get_client():
    return clickhouse_connect.get_client(
        host=CLICKHOUSE_HOST, port=CLICKHOUSE_PORT,
        username=CLICKHOUSE_USER, password=CLICKHOUSE_PASSWORD,
        secure=True, verify=certifi.where(),
    )


def ensure_table(client):
    client.command(f"""
    CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DB}.donor_enrichments (
        contributor_nm  String,
        state           String,
        current_role    String,
        notes           String,
        source_url      String,
        enriched_at     DateTime DEFAULT now()
    ) ENGINE = ReplacingMergeTree(enriched_at)
    ORDER BY (contributor_nm, state)
    """)


def already_enriched(client, names_states: list[tuple[str, str]]) -> set[tuple[str, str]]:
    if not names_states:
        return set()
    rows_str = ", ".join(f"('{n}', '{s}')" for n, s in names_states)
    r = client.query(f"""
        SELECT contributor_nm, state FROM {CLICKHOUSE_DB}.donor_enrichments
        WHERE (contributor_nm, state) IN ({rows_str})
    """)
    return {(row[0], row[1]) for row in r.result_rows}


def fetch_top_donors(client, cause: str, geo: str | None, top: int) -> list[dict]:
    geo_filter = f"AND c.state = '{geo.upper()}'" if geo else ""
    r = client.query(f"""
        SELECT
            c.contributor_nm, c.state,
            any(c.city)        AS city,
            any(c.employer)    AS employer,
            any(c.occupation)  AS occupation,
            sum(c.transaction_amt) AS total_given
        FROM {CLICKHOUSE_DB}.contributions c
        JOIN {CLICKHOUSE_DB}.committee_causes cc ON c.cmte_id = cc.cmte_id
        WHERE cc.cause_tag = '{cause}'
          AND c.contributor_nm != ''
          {geo_filter}
        GROUP BY c.contributor_nm, c.state
        ORDER BY total_given DESC
        LIMIT {top}
    """)
    return [
        {
            "name":       row[0],
            "geo":        row[1],
            "city":       row[2],
            "employer":   row[3],
            "occupation": row[4],
            "total_given": row[5],
        }
        for row in r.result_rows
    ]


def run_batch(causes: list[str], geo: str | None, top: int):
    client = get_client()
    ensure_table(client)

    all_donors: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for cause in causes:
        donors = fetch_top_donors(client, cause, geo, top)
        print(f"  {cause}: {len(donors)} top donors fetched")
        for d in donors:
            key = (d["name"], d["geo"])
            if key not in seen:
                seen.add(key)
                all_donors.append(d)

    # Skip already enriched
    already = already_enriched(client, [(d["name"], d["geo"]) for d in all_donors])
    to_enrich = [d for d in all_donors if (d["name"], d["geo"]) not in already]
    print(f"\n{len(all_donors)} unique donors, {len(already)} already enriched, "
          f"{len(to_enrich)} to enrich now\n")

    rows = []
    for i, donor in enumerate(to_enrich):
        name = donor["name"]
        state = donor["geo"]
        print(f"  [{i+1}/{len(to_enrich)}] {name} ({state}) "
              f"employer={donor.get('employer','?')[:30]}")
        try:
            result = enrich_clean(donor)
        except Exception as e:
            print(f"    ! error: {e}")
            result = None

        if result:
            rows.append((
                name, state,
                result.get("current_role") or "",
                result.get("notes") or "",
                result.get("source_url") or "",
            ))
            print(f"    role: {result.get('current_role','')}")
            print(f"    notes: {str(result.get('notes',''))[:80]}")
        else:
            rows.append((name, state, "", "", ""))
            print("    (no enrichment returned)")

        # Flush every 5 rows so partial runs save data
        if len(rows) >= 5:
            client.insert(
                f"{CLICKHOUSE_DB}.donor_enrichments", rows,
                column_names=["contributor_nm", "state", "current_role", "notes", "source_url"],
            )
            print(f"  → saved batch of {len(rows)}")
            rows = []
        time.sleep(1.5)  # stay under Nimble rate limits

    if rows:
        client.insert(
            f"{CLICKHOUSE_DB}.donor_enrichments", rows,
            column_names=["contributor_nm", "state", "current_role", "notes", "source_url"],
        )

    total = client.query(
        f"SELECT count() FROM {CLICKHOUSE_DB}.donor_enrichments"
    ).result_rows[0][0]
    print(f"\nDone. donor_enrichments now has {total:,} rows.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--causes", nargs="*", default=DEMO_CAUSES)
    parser.add_argument("--geo",    default=None, help="State code, e.g. CA")
    parser.add_argument("--top",    type=int, default=10,
                        help="Top donors per cause to enrich (default 10)")
    args = parser.parse_args()
    print(f"Batch enriching top {args.top} donors for causes: {args.causes}"
          + (f" in {args.geo}" if args.geo else " (all states)"))
    run_batch(args.causes, args.geo, args.top)


if __name__ == "__main__":
    main()
