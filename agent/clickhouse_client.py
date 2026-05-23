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


def _nonprofit_employer_bonus(nonprofit_name: str, source_url: str) -> dict:
    """Build an extra cited_reason for a donor whose employer is a cause-aligned nonprofit."""
    return {
        "text": f"Works at {nonprofit_name} — cause-aligned nonprofit (IRS 990 via ProPublica)",
        "source_url": source_url,
    }


def _load_nonprofit_index(client, causes: list[str], geo: str | None) -> dict[str, tuple[str, str]]:
    """
    Load cause-relevant nonprofit org names from nonprofit_orgs table.
    Returns {lower_org_name: (display_name, source_url)}.
    """
    cause_list = ", ".join(f"'{c}'" for c in causes)
    geo_filter = f"AND nonprofit_state = '{geo.upper()}'" if geo else ""
    try:
        sql = f"""
        SELECT DISTINCT nonprofit_name, source_url
        FROM {CLICKHOUSE_DB}.nonprofit_orgs
        WHERE cause_tag IN ({cause_list})
          {geo_filter}
        """
        rows = client.query(sql)
        return {
            row[0].lower(): (row[0], row[1])
            for row in rows.result_rows
        }
    except Exception:
        return {}


def query(
    cause: str | None = None,
    causes: list[str] | None = None,
    geo: str | None = None,
    min_amount: int = 200,
    limit: int = 20,
) -> list[dict]:
    """
    Find top donors by cause affinity.

    Queries FEC political giving and cross-references employer fields against
    the nonprofit_orgs table (ProPublica 990 data) for a richer affinity signal.

    Args:
        cause:      Single cause tag. See CAUSE_TAGS.md.
        causes:     List of cause tags — donors matching ANY tag.
        geo:        2-letter state code. None = all states.
        min_amount: Minimum FEC transaction amount (default $200).
        limit:      Max candidates to return.

    Returns:
        List of prospect_record dicts sorted by affinity_score desc.
    """
    if cause and not causes:
        causes = [cause]
    if not causes:
        raise ValueError("Provide cause= or causes=")

    client = _get_client()

    # Load nonprofit org names for employer cross-reference (best-effort)
    nonprofit_index = _load_nonprofit_index(client, causes, geo)

    cause_list = ", ".join(f"'{c}'" for c in causes)
    geo_filter = f"AND c.state = '{geo.upper()}'" if geo else ""

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

        primary_cmte = history_raw[0][2] if history_raw else ""
        name       = row["raw_name"].title()
        state      = row["geo"]
        employer   = row["employer"]
        score      = _affinity_score(row["total_given"], row["num_transactions"], years_active)

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

        # If employer matches a cause-relevant nonprofit, boost score + add citation
        employer_key = employer.lower().strip()
        if employer_key and nonprofit_index:
            for np_key, (np_display, np_url) in nonprofit_index.items():
                if np_key and (np_key in employer_key or employer_key in np_key):
                    cited_reasons.append(
                        _nonprofit_employer_bonus(np_display, np_url)
                    )
                    score = min(100, score + 10)
                    break

        results.append({
            "name":             name,
            "affinity_score":   score,
            "cause_tags":       list(row["cause_tags"]),
            "geo":              state,
            "city":             row["city"].title(),
            "employer":         employer.title(),
            "occupation":       row["occupation"].title(),
            "total_given":      row["total_given"],
            "num_donations":    row["num_transactions"],
            "first_gift_year":  first_year,
            "last_gift_year":   last_year,
            "donation_history": donation_history,
            "cited_reasons":    cited_reasons,
            "enrichment":       None,
            "source":           "fec",
        })

    results.sort(key=lambda p: p["affinity_score"], reverse=True)
    return results


def ping() -> bool:
    try:
        _get_client().command("SELECT 1")
        return True
    except Exception:
        return False
