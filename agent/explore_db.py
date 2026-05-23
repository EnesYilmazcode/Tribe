"""
Zero-cost database explorer.  READ-ONLY, ClickHouse only.

  *** This spends NO API credits and NO LLM tokens. ***
  It only reads the ClickHouse tables (database reads are free). It never calls
  Nimble (credits) or Gemini (tokens). Browse as much as you want.

Usage (run from agent/):
  python explore_db.py                      # overview: table sizes + data-reality check
  python explore_db.py causes               # list the cause tags and how many committees each has
  python explore_db.py <cause> [STATE] [min_amount]
                                            # e.g. python explore_db.py environment WA 1000
  python explore_db.py raw [N]              # dump N raw contribution rows (default 10)
"""

import sys

import clickhouse_client as ch


def overview() -> None:
    c = ch._get_client()
    db = ch.CLICKHOUSE_DB
    print(f"\nClickHouse: {ch.CLICKHOUSE_HOST}  db={db}  ping={ch.ping()}\n")
    print(f"{'table':22} {'rows':>12}")
    print("-" * 36)
    for t in ["contributions", "committees", "committee_causes", "nonprofit_orgs"]:
        try:
            n = int(c.command(f"SELECT count() FROM {db}.{t}"))
            print(f"{t:22} {n:>12,}")
        except Exception as e:
            print(f"{t:22}  ERROR {str(e)[:40]}")

    # Reality check: how many DISTINCT donors? few + round numbers = seed data.
    try:
        rows, uniq, lo, hi, avg = c.query(
            f"SELECT count(), uniq(contributor_nm), min(transaction_amt), "
            f"max(transaction_amt), round(avg(transaction_amt)) "
            f"FROM {db}.contributions"
        ).result_rows[0]
        print(f"\ncontributions: {rows:,} rows but only {uniq:,} DISTINCT donors")
        print(f"amount  min=${lo:,}  max=${hi:,}  avg=${int(avg):,}")
        if uniq < 1000:
            print("⚠️  Few distinct donors + round amounts = SYNTHETIC SEED DATA, not real FEC yet.")
        else:
            print("✅  Looks like real FEC contribution variety.")
    except Exception as e:
        print("reality check failed:", e)
    print("\nTry:  python explore_db.py causes   |   python explore_db.py environment WA")


def causes() -> None:
    c = ch._get_client()
    db = ch.CLICKHOUSE_DB
    rows = c.query(
        f"SELECT cause_tag, count() AS n FROM {db}.committee_causes "
        f"GROUP BY cause_tag ORDER BY n DESC"
    ).result_rows
    print(f"\n{'cause_tag':24} committees")
    print("-" * 38)
    for tag, n in rows:
        print(f"{tag:24} {n:>10,}")


def raw(n: int) -> None:
    c = ch._get_client()
    db = ch.CLICKHOUSE_DB
    rows = c.query(
        f"SELECT contributor_nm, state, city, employer, transaction_amt, transaction_dt, cmte_id "
        f"FROM {db}.contributions LIMIT {n}"
    ).result_rows
    for r in rows:
        print(" ", r)


def run_query(cause: str, state: str | None, min_amount: int) -> None:
    rows = ch.query(cause=cause, geo=state, min_amount=min_amount, limit=15)
    head = f'query(cause="{cause}"' + (f', geo="{state}"' if state else "") + f", min_amount={min_amount})"
    print(f"\n{head} -> {len(rows)} donors\n")
    print(f"{'name':26} {'st':3} {'total':>11} {'gifts':>6} {'score':>6}  causes")
    print("-" * 70)
    for r in rows:
        print(f"{r['name']:26} {r['geo']:3} ${r['total_given']:>9,} {r['num_donations']:>6} "
              f"{r['affinity_score']:>6}  {', '.join(r['cause_tags'])}")
    if rows:
        print("\nfirst donor's cited_reasons (these become the citation links in the UI):")
        for cr in rows[0]["cited_reasons"]:
            print(f"  • {cr['text']}\n    {cr['source_url']}")


def main() -> None:
    args = sys.argv[1:]
    if not args:
        overview()
    elif args[0] == "causes":
        causes()
    elif args[0] == "raw":
        raw(int(args[1]) if len(args) > 1 else 10)
    else:
        cause = args[0]
        state = args[1].upper() if len(args) > 1 and not args[1].isdigit() else None
        amt_arg = next((a for a in args[1:] if a.isdigit()), None)
        run_query(cause, state, int(amt_arg) if amt_arg else 200)


if __name__ == "__main__":
    main()
