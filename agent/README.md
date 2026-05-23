# agent/ — the data side (Friend)

Fills the database and makes it queryable. **This is the friend's side** (owns the **ClickHouse** + **Nimble** tracks). Goal: a fast, cause-tagged, enrichable donor store the platform (`../server/` + `../web/`) reads.

## Files
- `load_fec.py` — download FEC bulk individual-contributions → ClickHouse (filter by cycle / states / amount to stay fast).
- `load_nonprofits.py` — extra source: ProPublica nonprofit data.
- `cause_tag.py` + `cause_synonyms.py` — map committees → ~20 cause tags (keyword match + synonym/adjacency expansion). Vocabulary in `CAUSE_TAGS.md`; known false positives tracked in `../docs/TAGGING-QUALITY.md`.
- `clickhouse_client.py` — `query(cause, geo, min_amount) -> [candidate]` plus `ping()`.
- `nimble_client.py` — `enrich(candidate) -> {current_role, employer, bio_snippet, philanthropy, news, source_urls[]}` (live web enrichment).
- `inspect_query.py` — read-only data-quality probe over real `query()` output.
- `schema.sql`, `requirements.txt`.

## Status (2026-05-23)
committees (~20.9k) and committee_causes (~2.3k tagged) are loaded; **individual contributions loading.** Until that table lands, the server falls back to `../web/sample_prospects.json` and auto-switches to real donors the moment it's populated.

The server (`../server/`) calls `query()` and `enrich()`; it does the NL parse, scoring, and streaming. The contract between the two sides is in `../docs/TEAM-SPLIT.md`. Commit and push frequently — see `../CLAUDE.md`.
