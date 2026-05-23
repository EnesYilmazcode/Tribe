"""
Dedup-safe donor query — drop-in replacement for clickhouse_client.query().

Fixes the donor-total inflation without touching Trevor's agent/ code:
  - dedups duplicate contribution rows by sub_id (DISTINCT in the inner query)
  - filters with `cmte_id IN (SELECT DISTINCT cmte_id ...)` instead of JOINing
    committee_causes, so a committee tagged with several matching causes can't
    multiply a contribution
  - joins deduped committee name + aggregated cause tags 1:1 per committee

Same output shape as clickhouse_client.query(). Reuses its scoring + URL helpers.

    from query_clean import query
    query(cause="environment", geo="CA", min_amount=1000)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "agent"))
import clickhouse_client as ch  # reuse client, _affinity_score, URL constants


def query(cause=None, causes=None, geo=None, min_amount=200, limit=20):
    if cause and not causes:
        causes = [cause]
    if not causes:
        raise ValueError("Provide cause= or causes=")

    client = ch._get_client()
    db = ch.CLICKHOUSE_DB
    cause_list = ", ".join(f"'{c}'" for c in causes)
    geo_filter = f"AND c.state = '{geo.upper()}'" if geo else ""

    sql = f"""
    SELECT
        raw_name,
        geo,
        any(city)        AS city,
        any(employer)    AS employer,
        any(occupation)  AS occupation,
        sum(amt)         AS total_given,
        count()          AS num_transactions,
        min(dt)          AS first_gift,
        max(dt)          AS last_gift,
        arrayDistinct(arrayFlatten(groupArray(tags))) AS cause_tags,
        groupArray((toString(dt), amt, cmte_id, cmte_nm, tags)) AS donation_history_raw
    FROM (
        SELECT DISTINCT
            c.sub_id          AS sub_id,
            c.contributor_nm  AS raw_name,
            c.state           AS geo,
            c.city            AS city,
            c.employer        AS employer,
            c.occupation      AS occupation,
            c.transaction_amt AS amt,
            c.transaction_dt  AS dt,
            c.cmte_id         AS cmte_id
        FROM {db}.contributions c
        WHERE c.cmte_id IN (
                SELECT DISTINCT cmte_id FROM {db}.committee_causes
                WHERE cause_tag IN ({cause_list})
            )
          AND c.transaction_amt >= %(min_amount)s
          {geo_filter}
          AND c.contributor_nm != ''
    ) c
    LEFT JOIN (
        SELECT cmte_id, any(cmte_nm) AS cmte_nm FROM {db}.committees GROUP BY cmte_id
    ) m USING (cmte_id)
    LEFT JOIN (
        SELECT cmte_id, groupUniqArray(cause_tag) AS tags FROM {db}.committee_causes GROUP BY cmte_id
    ) t USING (cmte_id)
    GROUP BY raw_name, geo
    ORDER BY total_given DESC
    LIMIT %(limit)s
    """

    rows = client.query(sql, parameters={"min_amount": min_amount, "limit": limit})

    # Batch-load pre-computed Nimble enrichments
    raw_pairs = [(r[0], r[1]) for r in rows.result_rows]
    enrichment_cache = ch._load_precomputed_enrichments(client, raw_pairs)

    results = []
    for row in rows.named_results():
        first_year = row["first_gift"].year if row["first_gift"] else 0
        last_year = row["last_gift"].year if row["last_gift"] else 0
        years_active = (last_year - first_year + 1) if last_year else 0

        history_raw = sorted(row["donation_history_raw"], key=lambda x: x[0], reverse=True)[:25]
        donation_history = [
            {
                "date": h[0],
                "amount": h[1],
                "committee_id": h[2],
                "committee_name": (h[3] or "").title(),
                "cause_tags": list(h[4]) if h[4] else [],
            }
            for h in history_raw
        ]
        primary_cmte = history_raw[0][2] if history_raw else ""
        name = row["raw_name"].title()
        state = row["geo"]

        cited_reasons = [
            {
                "text": (
                    f"Gave ${row['total_given']:,} across {row['num_transactions']} "
                    f"donations to {', '.join(row['cause_tags'])} committees "
                    f"({first_year}–{last_year})"
                ),
                "source_url": ch.FEC_RECEIPT_URL.format(cmte_id=primary_cmte),
            },
            {
                "text": f"FEC individual contribution search for {name} in {state}",
                "source_url": ch.FEC_DONOR_URL.format(name=name.replace(" ", "+"), state=state),
            },
        ]

        results.append({
            "name": name,
            "affinity_score": ch._affinity_score(row["total_given"], row["num_transactions"], years_active),
            "cause_tags": list(row["cause_tags"]),
            "geo": state,
            "city": (row["city"] or "").title(),
            "employer": (row["employer"] or "").title(),
            "occupation": (row["occupation"] or "").title(),
            "total_given": row["total_given"],
            "num_donations": row["num_transactions"],
            "first_gift_year": first_year,
            "last_gift_year": last_year,
            "donation_history": donation_history,
            "cited_reasons": cited_reasons,
            "enrichment": enrichment_cache.get((row["raw_name"], row["geo"])),
        })

    return results
