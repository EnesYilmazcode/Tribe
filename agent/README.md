# agent/ : the data side (Friend)

Fills the database and makes it queryable. **This is the friend's side** (owns the **ClickHouse** + **Nimble** tracks). Goal is a fast, cause-tagged, enrichable donor store that the platform (`../server/` and `../web/`) reads.

## Files
- `load_fec.py` downloads FEC bulk individual-contributions into ClickHouse (filter by cycle, states, or amount to stay fast).
- `load_nonprofits.py` is an extra source: ProPublica nonprofit data.
- `cause_tag.py` plus `cause_synonyms.py` map committees to ~20 cause tags (keyword match plus synonym/adjacency expansion). Vocabulary is in `CAUSE_TAGS.md`, and known false positives are tracked in `../docs/TAGGING-QUALITY.md`.
- `clickhouse_client.py` is `query(cause, geo, min_amount) -> [candidate]` plus `ping()`.
- `nimble_client.py` is `enrich(candidate) -> {current_role, employer, bio_snippet, philanthropy, news, source_urls[]}` (live web enrichment).
- `inspect_query.py` is a read-only data-quality probe over real `query()` output.
- `schema.sql`, `requirements.txt`.

## Status (2026-05-23)
committees (~20.9k) and committee_causes (~2.3k tagged) are loaded, and **individual contributions are loading.** Until that table lands, the server falls back to `../web/sample_prospects.json` and auto-switches to real donors the moment it's populated.

The server (`../server/`) calls `query()` and `enrich()`, and it does the NL parse, scoring, and streaming. The contract between the two sides is in `../docs/TEAM-SPLIT.md`. Commit and push frequently, see `../CLAUDE.md`.
