# agent/ — the scraper / data side (Friend)

Fills the database and makes it queryable. **This is the friend's side** (owns the ClickHouse + Nimble tracks). Goal: a fast, cause-tagged, enrichable donor store the platform (`../web/`) can read.

Planned files (see `../docs/PLAN.md` Phase 0–3):
- `load_fec.py` — download FEC bulk individual-contributions, load into ClickHouse (one cycle, 2-3 states, amount >= $200 to keep it fast).
- `cause_tag.py` — map committees → ~20 cause tags (keyword + LLM; hand-curate the top ~50 by volume). Join on `CMTE_ID`.
- `clickhouse_client.py` — `query(cause, geo, min_amount) -> [candidate]`.
- `nimble_client.py` — `enrich(candidate) -> enrichment` (live web enrichment).
- `.env.example`, `requirements.txt`.

The platform calls `query()` and `enrich()`; it does the NL parse, scoring, and Senso publish. The contract between the two sides is in `../docs/TEAM-SPLIT.md`. Commit and push frequently — see `../CLAUDE.md`.
