# STATUS — live coordination across all instances

> **Every instance + Trevor: `git pull --rebase` and read this FIRST. Update it when you take or finish work, then push.**
> This is the shared source of truth for who owns what *right now* and what's still open.
> Personal plans live in `TODO-ENES.md`; the contract in `TEAM-SPLIT.md`. This doc = current state.
> Last updated: 2026-05-23 by the backend/coordination instance.

## Who owns what (current, 3-way)
| Owner | Lane | Status |
|---|---|---|
| **Trevor** | `agent/` — data collection: FEC → ClickHouse, cause tagging, committees/candidates | ongoing |
| **Other instance (Enes's #2)** | `web/` frontend + `server/load_fec_real.py` real-data loading + frontend verification | active |
| **This instance (backend/coord)** | `server/` — `/run` SSE backend, Gemini NL-parse, validation tooling, this STATUS doc | active |

**Rule to stop overlap:** before starting work, claim it here (add your name to an open item) and push. Don't touch another lane's files.

## Done ✅
- Backend `/run` SSE endpoint — emits the exact contract the frontend consumes; real data flows through it.
- NL parse — Gemini 2.5-flash (2.0-flash quota exhausted) + deterministic fallback.
- Real FEC data loaded — 303 real contributions, 206 real donors, genuine environment committees (Sierra Club, LCV, EDF, NextGen, Climate Hawks). Tom Steyer etc.
- Frontend renders real data — 20 cards, Steyer top, name-flip + employer casing fixed, 13 tests pass.

## OPEN — critical, in priority order
1. **🔴 4× donor-total inflation [owner: Trevor].** `committees` has each cmte_id ×2 AND `committee_causes` tags each ×2 → query JOIN multiplies totals by 4. Steyer shows **$2M; real is $500k**. **Blocks honest demo numbers + contradicts the fec.gov citations.**
   Fix (two safe commands):
   ```sql
   OPTIMIZE TABLE donor_agent.committees FINAL;
   OPTIMIZE TABLE donor_agent.committee_causes FINAL DEDUPLICATE;
   ```
2. **🟡 Demo cause = `environment` only.** `civil_rights` / `small_business` / `social_welfare` are ~90% party-proxy tags (DEM/REP/IND candidate mapping), not real cause-affinity. Don't demo those.
3. **🟡 Tagging false positives still live in DB** (Walgreen, Reform Party, Marine Engineers Union mis-tagged). cause_tag.py code is fixed but the table wasn't re-run. [owner: Trevor] — see `TAGGING-QUALITY.md`.
4. **🟢 Card count** — 20 is a long scroll for a 3-min demo; cap visible to ~top 10 (count still "20 found"). [owner: other instance]
5. **🟢 Live enrichment too slow + garbage output** [owner: Enes frontend instance — IN PROGRESS]. Nimble enrich ≈ 24–48s/prospect AND the regex extractors produce wrong fields ("Fahr, Llc at Founder", employer "State,"). Building two new files (no collision): `server/enrich_clean.py` (1 Nimble search + Gemini extraction → clean UI-shape enrichment) and `server/build_demo_snapshot.py` (bake a real, enriched run into `web/sample_prospects.json` so `?demo=1` is instant, real, and recording-proof).

## Decisions locked (don't re-litigate)
- Sponsors = **ClickHouse + Nimble**. Senso + x402 dropped.
- Demo data source = **FEC API** (real, cited), not scraping. Nimble = enrichment only.
- Submission = recorded 3-min video; freeze 3:45, submit by 4:15.
