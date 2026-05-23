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

> ⚠️ **[coord → frontend instance] I edited `web/` at Enes's direct request.** `git pull --rebase` before editing `web/` so we don't conflict. Changes:
> - `0733254` — landing redesigned (`!started` branch in `App.tsx`) into a left hero + right auto-playing preview; added `MockPreview.tsx` (decorative filler). Post-submit workspace + `?demo=1` untouched.
> - `b4cf000` — trimmed/centered `logo.png`, dropped the wordmark "." dot + the subcopy paragraph.
> - `8245948` — added a varied **example contact email** to each donor: a field in `sample_prospects.json`, `email?` in `types.ts`, rendered in `ProspectCard.tsx` (mailto link under name). **⚠️ `build_demo_snapshot.py` does NOT generate emails — re-running it will wipe them.** If you re-bake the snapshot, re-add emails (or add a generator to the snapshot script). All builds pass, verified in browser.

## ▶ NEXT — ship plan (post-freeze, in priority order)
The build is essentially done; what's left is the recording + submission. Demo `?demo=1` is **verified recording-ready** (Steyer $500k deduped, person-first link, coherent chips, zero errors).
1. **🎥 [Enes] RECORD the 3-min demo NOW** on `?demo=1` per `docs/DEMO-SCRIPT.md`. This is the submission — highest priority, do before anything else.
2. **✅ DONE [coord] Submission prep:** **`docs/SUBMISSION.md`** has paste-ready Devpost copy (tagline, what-it-does, how-built, challenges, accomplishments, what's-next, built-with, sponsor tools ClickHouse+Nimble), a 4:15 checklist, and the rehearsed §104.15 legal answer. **Verified repo is safe to make public** — only `.env.example` tracked, key-pattern scan found zero leaked secrets. Just paste + add the video link at submit time.
3. **✅ READY — autonomy 2nd-clip (two options, both bulletproof terminal demos).** Record only if the main `?demo=1` take is done.
   - **`python server/auto_match.py demo`** [coord] — campaigns auto-fill with real donors; add a 3rd live; "0 new" proves continuous dedup. No Gemini.
   - **`python server/campaign_outreach.py demo`** [Enes, NEW] — the FULLER autonomy loop: each campaign auto-**matches** donors → auto-**finds a contact lead** → auto-**drafts** a personalized email, zero human input. Cached (0.5s replay, can't flake). Real donors: Steyer (oceans/CA), Connie Ballmer (clean-water/WA). **This is the strongest "autonomy + reach" beat** — directly answers "autonomously get contacts + update campaigns + draft outreach."
4. **🟡 [Trevor] Data is stable — leave it.** Optional only if idle: re-run tagging to drop the false positives (Walgreen/Reform/Marine) and add `animal_welfare`. NOT required for the locked environment demo. Don't destabilize the DB before recording.
5. **✅ DONE [Enes] AI outreach-email draft** — `server/draft_email.py` (Gemini) writes a personalized email grounded in the donor's real giving; baked into the snapshot for top donors; ProspectCard has a "Draft outreach email" button (instant from cache, recording-proof). Completes the find→research→reach-out loop. **`DEMO-SCRIPT.md` now has a closing email beat (~2:20–2:45)** — coord, re-read it if proofreading. (Contact enrichment / actual send = post-submission.)

**Freeze rule:** at 3:45 stop building. A polished `?demo=1` recording beats any half-finished feature. Upload the video immediately (processing takes minutes), paste the LINK into Devpost by 4:15.

## Done ✅
- Backend `/run` SSE endpoint — emits the exact contract the frontend consumes; real data flows through it.
- NL parse — Gemini + deterministic fallback. **✅ RATE LIMIT RESOLVED (Tier 1, $25/mo cap):** key now returns 200 on `gemini-flash-latest` AND `gemini-2.5-flash` — live parse works again. `GEMINI_MODEL=gemini-flash-latest` in `.env`. If it 429s again under heavy load, use a key from the Tier-1 (BoardBot) project for a durable fix. (Recorded demo uses `?demo=1` so it's unaffected regardless.)
- **Real FEC bulk data loaded — 2.8M real contributions, 597k donors, all 20 causes, 5 states (CA/NY/TX/WA/OR), 99.99% unique.** Data collection is largely DONE.
- Frontend renders real data — 20 cards, Steyer top, name-flip + employer casing fixed, 13 tests pass.
- **Persistent Nimble enrichments** — `agent/nimble_batch_enrich.py` pre-computes roles for top donors (via Nimble search → Gemini extraction, falling back to FEC occupation/employer) and stores in `donor_enrichments` table (`ReplacingMergeTree`). `clickhouse_client.query()` now batch-loads these at query time so UI gets instant bios with zero Nimble latency. `server/main.py` updated to use `enrich_clean` for any non-pre-computed top-3 donors. Batch enricher ran for environment/healthcare/labor/energy top-10. Server restarted.

## OPEN — critical, in priority order
1. **✅ DONE — Donor-total inflation fixed [backend/coord instance].** `server/query_clean.py` is a dedup-safe drop-in for `query()`: dedups contributions by `sub_id`, filters via `cmte_id IN (SELECT DISTINCT cmte_id FROM committee_causes WHERE cause_tag IN (...))` to avoid multi-cause multiplication, joins deduped name+tags 1:1. **`/run` now uses it** — verified: Steyer 2 gifts/$1M (inflated) → **1 gift/$500k (correct)**, Serrurier 6/$340k → 3/$170k. Leaves Trevor's `agent/clickhouse_client.py` untouched.
   ➡️ **Other instance: swap `build_demo_snapshot.py` to `from query_clean import query` and re-run** for honest snapshot totals (you already flagged this handoff).
2. **🟡 Demo cause = `environment` only.** `civil_rights` / `small_business` / `social_welfare` are ~90% party-proxy tags (DEM/REP/IND candidate mapping), not real cause-affinity. Don't demo those.
3. **🟡 Tagging false positives still live in DB** (Walgreen, Reform Party, Marine Engineers Union mis-tagged). cause_tag.py code is fixed but the table wasn't re-run. [owner: Trevor] — see `TAGGING-QUALITY.md`.
3b. **🟠 Ranking is capacity-first, not affinity-first [owner: coord — `query_clean.py`].** Found while demoing: `ORDER BY total_given DESC` ranks by raw dollars, so the single biggest donor recurs across unrelated asks (the RJC/energy donor keeps surfacing via adjacency + mis-tag). Should rank by an **affinity-first composite**: cause-specificity (giving concentration in the requested cause) → amount-to-that-cause → recency → geo. Full design in `docs/DEMO-FEEDBACK.md` §4. **#1 post-recording fix + strong "what's next" judging point** (affinity vs capacity = our thesis). Locked `?demo=1` is unaffected, so NOT before recording.
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

## Continuous auto-matching agent (the autonomy money-shot) — ✅ WORKING PROTOTYPE [backend/coord instance]
`server/auto_match.py` (CLI, standalone, no collision). A campaign = NL description → parse_ask → query_clean → top matches **auto-added to its pipeline, zero manual selection**. `--watch` loop re-checks every N sec and only surfaces NEW contacts as data grows. Verified: seeded 3 campaigns ("protect oceans…", "cancer research…", "support unions…") → one cycle auto-added 30 real donors (Steyer, Bloomberg, …) at correct deduped totals. `seed` / `run` / `watch` / `list` / `add` commands. (`campaigns.json` is gitignored runtime state — `seed` to regenerate.) This is the strongest Autonomy demo beat if we want a second segment.

## Demo feedback (2026-05-23) — full plan in `docs/DEMO-FEEDBACK.md`
Found while demoing. Snapshot fixes already done by Enes frontend (deduped totals via query_clean, person-first FEC link). Cross-lane items:
- **✅ DONE [coord]** Live `/run` now queries **primary cause only** (`expanded = causes`) — no more adjacency pollution (verified: "environment/CA" returns only `environment`-tagged donors). And `query_clean.py` `cited_reasons` reordered **person-first** (donor's FEC individual-contribution record leads, committee second).
- **[Trevor] Add an `animal_welfare` cause tag + tag its committees** (Humane Society Legislative Fund, ASPCA, Defenders of Wildlife). Niche asks like "dog shelter" have no home today → map to `environment` (climate donors). Taxonomy coarseness is the semantic bottleneck, not the parse.
- **[Enes, stretch] Contact enrichment** — extend `enrich_clean` to surface a public contact channel (LinkedIn/org), with the §104.15 legal gate.

## Note: `mockup/index.html` [coord]
Standalone visual concept mock (campfire/teepee Tribe theme — animated typewriter ask box + looping mock agent run with filler data). **Pure visuals, hardcoded, no backend.** Open directly in a browser. **Separate from `web/` and the locked `?demo=1` demo — touches neither.** Built at Enes's request to show the product vision.

## Decisions locked (don't re-litigate)
- Sponsors = **ClickHouse + Nimble**. Senso + x402 dropped.
- Demo data source = **FEC API** (real, cited), not scraping. Nimble = enrichment only.
- Submission = recorded 3-min video; freeze 3:45, submit by 4:15.
