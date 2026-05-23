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

## OPEN — critical, in priority order
1. **🟡 Donor-total inflation — now SMALL [owner: backend/coord instance — IN PROGRESS].** Re-verified against the 2.8M-row load: contributions is **99.99% unique** (264 dupe rows / 2.8M) and the committee-table `OPTIMIZE` largely held. Residual inflation: duplicate contribution rows + committees tagged with multiple matching causes → JOIN multiplies. Example: Steyer environment shows $1.26M; correct is **3 gifts / $760k**.
   **Fix I'm building (no collision):** `server/query_clean.py` — a dedup-safe drop-in for `query()` that (a) dedups contributions by `sub_id`, (b) filters via `cmte_id IN (SELECT DISTINCT cmte_id FROM committee_causes WHERE cause_tag IN (...))` to avoid multi-cause multiplication, (c) joins deduped committee name + aggregated tags 1:1. `/run` will use it; **other instance: point `build_demo_snapshot.py` at `server.query_clean.query` for honest snapshot numbers** (one import swap). Leaves Trevor's `agent/clickhouse_client.py` untouched.
2. **🟡 Demo cause = `environment` only.** `civil_rights` / `small_business` / `social_welfare` are ~90% party-proxy tags (DEM/REP/IND candidate mapping), not real cause-affinity. Don't demo those.
3. **🟡 Tagging false positives still live in DB** (Walgreen, Reform Party, Marine Engineers Union mis-tagged). cause_tag.py code is fixed but the table wasn't re-run. [owner: Trevor] — see `TAGGING-QUALITY.md`.
4. **🟢 Card count** — 20 is a long scroll for a 3-min demo; cap visible to ~top 10 (count still "20 found"). [owner: other instance]
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

## Future / stretch — continuous auto-matching agent (the autonomy money-shot)
Vision: campaigns live on the platform (e.g. "clean water", "turtle rescue"). A background agent re-pulls fresh FEC + web data every 5–30 min; when a new high-affinity contact matches an existing campaign, it's **auto-added to that campaign's pipeline — zero manual work.** This is the strongest possible Autonomy story (acts on real-time data, no human in the loop — exactly the judging criterion). Buildable as a backend feature: a campaign store + a scheduler + match-on-new-contact. Stretch for today, but a strong differentiator if there's time after the demo is locked. [candidate owner: backend/coord instance]

## Decisions locked (don't re-litigate)
- Sponsors = **ClickHouse + Nimble**. Senso + x402 dropped.
- Demo data source = **FEC API** (real, cited), not scraping. Nimble = enrichment only.
- Submission = recorded 3-min video; freeze 3:45, submit by 4:15.
