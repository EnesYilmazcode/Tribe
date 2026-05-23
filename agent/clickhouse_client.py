"""
Public interface used by the platform (web/) side.

    from clickhouse_client import query

    prospects = query(cause="environment", geo="WA", min_amount=1000)
    prospects = query(causes=["environment", "housing"], geo="CA", min_amount=500)

Returns prospect_record dicts per docs/TEAM-SPLIT.md, enriched with full
donation history and committee names.  enrichment=None until nimble fills it.
"""

import math
import os
from functools import lru_cache

import certifi
import clickhouse_connect
from dotenv import load_dotenv

os.environ.setdefault("SSL_CERT_FILE", certifi.where())

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

CLICKHOUSE_HOST = os.environ["CLICKHOUSE_HOST"]
CLICKHOUSE_PORT = int(os.environ.get("CLICKHOUSE_PORT", 8443))
CLICKHOUSE_USER = os.environ.get("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.environ["CLICKHOUSE_PASSWORD"]
CLICKHOUSE_DB = os.environ.get("CLICKHOUSE_DB", "donor_agent")

FEC_RECEIPT_URL = "https://www.fec.gov/data/receipts/?committee_id={cmte_id}"
FEC_DONOR_URL = "https://www.fec.gov/data/receipts/individual-contributions/?contributor_name={name}&contributor_state={state}"


@lru_cache(maxsize=1)
def _get_client():
    return clickhouse_connect.get_client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT,
        username=CLICKHOUSE_USER,
        password=CLICKHOUSE_PASSWORD,
        secure=True,
        verify=certifi.where(),
    )


def _affinity_score(total_given: int, num_transactions: int, years_active: int) -> int:
    """0–100 score: log-scaled giving + recency + consistency bonus."""
    base = math.log10(max(total_given, 1)) * 15          # up to ~75 pts for $10M+
    consistency = min(15, num_transactions * 1.5)         # up to 15 pts for repeat giving
    recency = min(10, years_active * 2)                   # up to 10 pts for long history
    return min(100, int(base + consistency + recency))


def query(
    cause: str | None = None,
    causes: list[str] | None = None,
    geo: str | None = None,
    min_amount: int = 200,
    limit: int = 20,
) -> list[dict]:
    """
    Find top donors by cause affinity.

    Args:
        cause:      Single cause tag, e.g. 'environment'. See CAUSE_TAGS.md.
        causes:     List of cause tags — donors matching ANY tag are returned,
                    ranked by total giving across all matched causes.
        geo:        2-letter state code, e.g. 'WA'. None = all states.
        min_amount: Minimum single-transaction amount (default $200).
        limit:      Max candidates to return.

    Returns:
        List of prospect_record dicts sorted by affinity_score desc.
    """
    if cause and not causes:
        causes = [cause]
    if not causes:
        raise ValueError("Provide cause= or causes=")

    client = _get_client()

    cause_list = ", ".join(f"'{c}'" for c in causes)
    geo_filter = f"AND c.state = '{geo.upper()}'" if geo else ""

    # Pull aggregated donor stats + full individual transaction history in one pass.
    # groupArray collects every (date, amt, cmte_id, cmte_nm, cause_tag) tuple per donor.
    sql = f"""
    SELECT
        c.contributor_nm                                AS raw_name,
        c.state                                         AS geo,
        any(c.city)                                     AS city,
        any(c.employer)                                 AS employer,
        any(c.occupation)                               AS occupation,
        sum(c.transaction_amt)                          AS total_given,
        count()                                         AS num_transactions,
        min(c.transaction_dt)                           AS first_gift,
        max(c.transaction_dt)                           AS last_gift,
        groupUniqArray(cc.cause_tag)                    AS cause_tags,
        groupArray((
            toString(c.transaction_dt),
            c.transaction_amt,
            c.cmte_id,
            m.cmte_nm,
            cc.cause_tag
        ))                                              AS donation_history_raw
    FROM {CLICKHOUSE_DB}.contributions c
    JOIN {CLICKHOUSE_DB}.committee_causes cc ON c.cmte_id = cc.cmte_id
    JOIN {CLICKHOUSE_DB}.committees m        ON c.cmte_id = m.cmte_id
    WHERE cc.cause_tag IN ({cause_list})
      AND c.transaction_amt >= %(min_amount)s
      {geo_filter}
      AND c.contributor_nm != ''
    GROUP BY c.contributor_nm, c.state
    ORDER BY total_given DESC
    LIMIT %(limit)s
    """

    rows = client.query(sql, parameters={"min_amount": min_amount, "limit": limit})

    results = []
    for row in rows.named_results():
        first_year = row["first_gift"].year if row["first_gift"] else 0
        last_year  = row["last_gift"].year  if row["last_gift"]  else 0
        years_active = last_year - first_year + 1

        # Sort donation history newest-first, cap at 25 entries for payload size
        history_raw = sorted(row["donation_history_raw"], key=lambda x: x[0], reverse=True)[:25]
        donation_history = [
            {
                "date":           h[0],
                "amount":         h[1],
                "committee_id":   h[2],
                "committee_name": h[3].title(),
                "cause_tags":     [h[4]],
            }
            for h in history_raw
        ]

        # Primary committee for the FEC citation link
        primary_cmte = history_raw[0][2] if history_raw else ""
        name = row["raw_name"].title()
        state = row["geo"]

        cited_reasons = [
            {
                "text": (
                    f"Gave ${row['total_given']:,} across "
                    f"{row['num_transactions']} donations to "
                    f"{', '.join(row['cause_tags'])} committees "
                    f"({first_year}–{last_year})"
                ),
                "source_url": FEC_RECEIPT_URL.format(cmte_id=primary_cmte),
            },
            {
                "text": f"FEC individual contribution search for {name} in {state}",
                "source_url": FEC_DONOR_URL.format(
                    name=name.replace(" ", "+"),
                    state=state,
                ),
            },
        ]

        results.append({
            "name":             name,
            "affinity_score":   _affinity_score(row["total_given"], row["num_transactions"], years_active),
            "cause_tags":       list(row["cause_tags"]),
            "geo":              state,
            "city":             row["city"].title(),
            "employer":         row["employer"].title(),
            "occupation":       row["occupation"].title(),
            "total_given":      row["total_given"],
            "num_donations":    row["num_transactions"],
            "first_gift_year":  first_year,
            "last_gift_year":   last_year,
            "donation_history": donation_history,
            "cited_reasons":    cited_reasons,
            "enrichment":       None,
        })

    return results


def ping() -> bool:
    try:
        _get_client().command("SELECT 1")
        return True
    except Exception:
        return False
