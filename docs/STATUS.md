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
- **Real FEC bulk data loaded — 2.8M real contributions, 597k donors, all 20 causes, 5 states (CA/NY/TX/WA/OR), 99.99% unique.** Data collection is largely DONE.
- Frontend renders real data — 20 cards, Steyer top, name-flip + employer casing fixed, 13 tests pass.

## OPEN — critical, in priority order
1. **🟡 Donor-total inflation — now SMALL [owner: Trevor / query fix].** Re-verified against the 2.8M-row load: contributions is **99.99% unique** (264 dupe rows / 2.8M) and the committee-table `OPTIMIZE` largely held. Residual inflation is a few duplicate contribution rows + the JOIN not deduping. Example: Steyer environment shows $1.26M; deduped-by-sub_id it's the correct **3 gifts / $760k**.
   **Durable fix:** make `query()` aggregate over `DISTINCT sub_id` (count distinct sub_id; sum over distinct (sub_id, amount)); use `(SELECT DISTINCT cmte_id, cause_tag FROM committee_causes)` in the join. Robust against concurrent loads — better than one-shot OPTIMIZE. ~Few-line change in `agent/clickhouse_client.py`. (I ran the OPTIMIZE commands; they helped but concurrent loads re-introduce dupes, so the query-level dedup is the real fix.)
2. **🟡 Demo cause = `environment` only.** `civil_rights` / `small_business` / `social_welfare` are ~90% party-proxy tags (DEM/REP/IND candidate mapping), not real cause-affinity. Don't demo those.
3. **🟡 Tagging false positives still live in DB** (Walgreen, Reform Party, Marine Engineers Union mis-tagged). cause_tag.py code is fixed but the table wasn't re-run. [owner: Trevor] — see `TAGGING-QUALITY.md`.
4. **🟢 Card count** — 20 is a long scroll for a 3-min demo; cap visible to ~top 10 (count still "20 found"). [owner: other instance]
5. **🟢 Live enrichment too slow + garbage output** [owner: Enes frontend instance — IN PROGRESS]. Nimble enrich ≈ 24–48s/prospect AND the regex extractors produce wrong fields ("Fahr, Llc at Founder", employer "State,"). Building two new files (no collision): `server/enrich_clean.py` (1 Nimble search + Gemini extraction → clean UI-shape enrichment) and `server/build_demo_snapshot.py` (bake a real, enriched run into `web/sample_prospects.json` so `?demo=1` is instant, real, and recording-proof).

## Integration status — ~80%, core works end-to-end on REAL data
- Data (Trevor): ✅ ~90% — 2.8M real rows, all causes, 5 states. Residual: sub_id dedup in query().
- Backend `/run` + NL parse (this instance): ✅ done.
- Frontend rendering real data (other instance): ✅ done.
- Enrichment quality (other instance): 🟡 in progress (LLM extraction + demo snapshot).
- Demo recording: ⬜ not started.
**Not a large portion missing** — what's left is quality polish (enrichment, dedup, card cap) + the recording. We're close.

## Future / stretch — continuous auto-matching agent (the autonomy money-shot)
Vision: campaigns live on the platform (e.g. "clean water", "turtle rescue"). A background agent re-pulls fresh FEC + web data every 5–30 min; when a new high-affinity contact matches an existing campaign, it's **auto-added to that campaign's pipeline — zero manual work.** This is the strongest possible Autonomy story (acts on real-time data, no human in the loop — exactly the judging criterion). Buildable as a backend feature: a campaign store + a scheduler + match-on-new-contact. Stretch for today, but a strong differentiator if there's time after the demo is locked. [candidate owner: backend/coord instance]

## Decisions locked (don't re-litigate)
- Sponsors = **ClickHouse + Nimble**. Senso + x402 dropped.
- Demo data source = **FEC API** (real, cited), not scraping. Nimble = enrichment only.
- Submission = recorded 3-min video; freeze 3:45, submit by 4:15.
