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
- NL parse — Gemini + deterministic fallback. **⚠️ MODEL FIX: `gemini-2.5-flash` AND `gemini-2.0-flash` are now 429 quota-exhausted; `gemini-flash-latest` works (200).** Set `GEMINI_MODEL=gemini-flash-latest` in `.env` (done on this machine). nl_parse should default to it too, else parse silently falls back to deterministic and the autonomy story weakens.
- **Real FEC bulk data loaded — 2.8M real contributions, 597k donors, all 20 causes, 5 states (CA/NY/TX/WA/OR), 99.99% unique.** Data collection is largely DONE.
- Frontend renders real data — 20 cards, Steyer top, name-flip + employer casing fixed, 13 tests pass.
- **Persistent Nimble enrichments** — `agent/nimble_batch_enrich.py` pre-computes roles for top donors (via Nimble search → Gemini extraction, falling back to FEC occupation/employer) and stores in `donor_enrichments` table (`ReplacingMergeTree`). `clickhouse_client.query()` now batch-loads these at query time so UI gets instant bios with zero Nimble latency. `server/main.py` updated to use `enrich_clean` for any non-pre-computed top-3 donors. Batch enricher ran for environment/healthcare/labor/energy top-10. Server restarted.

## OPEN — critical, in priority order
1. **✅ DONE — Donor-total inflation fixed [backend/coord instance].** `server/query_clean.py` is a dedup-safe drop-in for `query()`: dedups contributions by `sub_id`, filters via `cmte_id IN (SELECT DISTINCT cmte_id FROM committee_causes WHERE cause_tag IN (...))` to avoid multi-cause multiplication, joins deduped name+tags 1:1. **`/run` now uses it** — verified: Steyer 2 gifts/$1M (inflated) → **1 gift/$500k (correct)**, Serrurier 6/$340k → 3/$170k. Leaves Trevor's `agent/clickhouse_client.py` untouched.
   ➡️ **Other instance: swap `build_demo_snapshot.py` to `from query_clean import query` and re-run** for honest snapshot totals (you already flagged this handoff).
2. **🟡 Demo cause = `environment` only.** `civil_rights` / `small_business` / `social_welfare` are ~90% party-proxy tags (DEM/REP/IND candidate mapping), not real cause-affinity. Don't demo those.
3. **🟡 Tagging false positives still live in DB** (Walgreen, Reform Party, Marine Engineers Union mis-tagged). cause_tag.py code is fixed but the table wasn't re-run. [owner: Trevor] — see `TAGGING-QUALITY.md`.
4. **✅ DONE — Card count** capped to top 10 (count still shows total). [Enes frontend instance]
   Also done: `?demo=1` activity-stream params now derive from the snapshot (chips match cards: "environment · CA"), example chip matches the baked run, names flipped in enrich narration, and **`docs/DEMO-SCRIPT.md`** — the 3-min recording guide (record on `?demo=1`). **Demo path is locked + recording-proof.**
   ⏳ Pending handoff: when `server/query_clean.py` lands, I swap `build_demo_snapshot.py` to import it and re-run (one command) for honest totals.
5. **✅ DONE — fast clean enrichment + instant demo snapshot** [Enes frontend instance]. `server/enrich_clean.py`: 1 Nimble search + Gemini (`gemini-flash-latest`) → clean UI-shape enrichment in ~8s (was 24–48s of garbage). e.g. Steyer → "Founder, Fahr LLC" + Wikipedia-cited bio; Serrurier → real role "Co-Founder, Redwood Grove Capital" + Earthjustice board note. `server/build_demo_snapshot.py` bakes a real, enriched **environment/CA** run into `web/sample_prospects.json` (top 3 enriched, primary-cause only to avoid adjacency mis-tags), so `?demo=1` replays it instantly and recording-proof. Verified end-to-end in the browser.
   **NOTE for whoever fixes #1 (query dedup):** the snapshot's totals are still inflated (Steyer $1M vs real ~$760k). After the `DISTINCT sub_id` query fix lands, just re-run `python server/build_demo_snapshot.py` to refresh real numbers — one command.
   **Found while doing this:** adjacency expansion (`expand_causes`) pulls mis-tagged committees into a focused demo (an "environment" ask surfaced a Republican Jewish Coalition donor via the bad RJC→energy tag). The snapshot now queries the **primary cause only** to stay on-topic.

## Integration status — ~80%, core works end-to-end on REAL data
- Data (Trevor): ✅ ~90% — 2.8M real rows, all causes, 5 states. Residual: sub_id dedup in query().
- Backend `/run` + NL parse (this instance): ✅ done.
- Frontend rendering real data (other instance): ✅ done.
- Enrichment quality (other instance): 🟡 in progress (LLM extraction + demo snapshot).
- Demo recording: ⬜ not started.
**Not a large portion missing** — what's left is quality polish (enrichment, dedup, card cap) + the recording. We're close.

## Continuous auto-matching agent (the autonomy money-shot) — 🔨 IN PROGRESS [backend/coord instance]
Vision: campaigns live on the platform (e.g. "clean water", "turtle rescue"). A background agent re-checks every cycle; when a new high-affinity contact matches a campaign, it's **auto-added to that campaign's pipeline — zero manual work.** Strongest Autonomy story (acts on real-time data, no human in the loop).
Building in MY lane (no collision): `server/auto_match.py` + `server/campaigns.json`. Each campaign = NL description → parse_ask → query_clean → top matches auto-added; a `--watch` loop re-runs and reports NEW matches as data grows. Standalone module/CLI (no edits to main.py or the frontend's files).

## Demo feedback (2026-05-23) — full plan in `docs/DEMO-FEEDBACK.md`
Found while demoing. Snapshot fixes already done by Enes frontend (deduped totals via query_clean, person-first FEC link). Cross-lane items:
- **[coord] Live `/run`: query primary cause only** (drop/discount `expand_causes`) — adjacency pulls mis-tagged committees (RJC PAC tagged `energy`) into focused asks. And **reorder `cited_reasons` person-first** in `query_clean.py` (one-liner) to match the snapshot.
- **[Trevor] Add an `animal_welfare` cause tag + tag its committees** (Humane Society Legislative Fund, ASPCA, Defenders of Wildlife). Niche asks like "dog shelter" have no home today → map to `environment` (climate donors). Taxonomy coarseness is the semantic bottleneck, not the parse.
- **[Enes, stretch] Contact enrichment** — extend `enrich_clean` to surface a public contact channel (LinkedIn/org), with the §104.15 legal gate.

## Decisions locked (don't re-litigate)
- Sponsors = **ClickHouse + Nimble**. Senso + x402 dropped.
- Demo data source = **FEC API** (real, cited), not scraping. Nimble = enrichment only.
- Submission = recorded 3-min video; freeze 3:45, submit by 4:15.
