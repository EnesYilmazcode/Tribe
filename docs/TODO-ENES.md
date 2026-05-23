# TODO — Enes (the platform side). Wall-clock for 2026-05-23

## ✅ CURRENT STATE (~freeze time) — frontend & demo are DONE
- Frontend renders real, cited, enriched donors (names normalized, totals deduped, person-first FEC links, cards capped to 10). 13 tests pass.
- Fast clean enrichment (`server/enrich_clean.py`) + instant demo snapshot (`server/build_demo_snapshot.py`).
- `?demo=1` **verified recording-ready**: chips "environment · CA · $1,000+", top = Thomas F. Steyer $500k (deduped), person-first link, zero console errors.
- Gemini billing fixed (Tier-1) — live parse works too.
- **NEXT (the only thing left for me): RECORD the 3-min demo** on `?demo=1` per `docs/DEMO-SCRIPT.md`, then **upload + submit**. See the PRE-RECORDING CHECKLIST below.
- After recording (stretch, only if time): contact enrichment (`enrich_clean` → public LinkedIn/org channel, §104.15 caveat).

---

> My half: read the DB → NL parse → query → score → frontend (results in the UI). Owns Presentation/the demo.
> **Senso + x402 are DROPPED.** Sponsors = ClickHouse + Nimble. Open-web + autonomy story rests on live Nimble enrichment.
> Friend's half (`agent/`): FEC → ClickHouse + cause-tag + Nimble `enrich()`. I build against the mock until integration.
> **Rule: commit + push after EVERY block.** `git pull --rebase` first, short message, push. See `CLAUDE.md`.
> Now: 11:30 AM. Wall: 4:30 PM. Record at 3:45. Treat 4:15 as the real deadline.

## 11:30–11:45 — Joint sync + lock the contract (with friend)
- [ ] Agree the `prospect_record` JSON shape together (see `TEAM-SPLIT.md`). 5 min, no bikeshedding.
- [ ] Pick the ONE demo ask we'll record (e.g. "Major clean-water + environment donors in the Pacific Northwest"). Write it down.
- [ ] Write `web/sample_prospects.json` (3–5 realistic mock records). Commit + push so both of us build against it.

## 11:45–12:45 — Frontend skeleton against the mock (use the `frontend-design` skill)
- [ ] Ask box (single NL input) + submit.
- [ ] **Live agent activity stream** — THE money-shot for autonomy. Show steps: parse → query → enrich (live web) → score. Fake the timing for now.
- [ ] Cited prospect cards rendering `sample_prospects.json` (name, score, cited reasons w/ FEC source links).
- [ ] Make it look intentional, not AI-boilerplate. Commit + push.

## 12:45–1:30 — NL parse + wire the query call (grab lunch ~1:30, eat at desk)
- [ ] LLM parse: sentence → `{cause, geo, min_amount}`. Show parsed params in the activity stream.
- [ ] Call a `query()` stub that returns the mock for now (real one comes at integration).
- [ ] Commit + push.

## 1:30–2:15 — Scoring + make the stream real
- [ ] Score 0–100 (affinity + recency + capacity) with 2–3 cited reasons each; rank.
- [ ] Activity stream narrates the REAL pipeline steps as they happen — this is the autonomy proof.
- [ ] Commit + push.

## 2:15–3:00 — Integration with friend
- [ ] Swap the `query()` stub for friend's real ClickHouse `query()`; call `enrich()` on top-N (live Nimble — narrate "going to the open web in real time").
- [ ] Run the chosen demo ask end-to-end on REAL data. Fix what breaks.
- [ ] Commit + push.

## 3:00–3:30 — Polish + OPTIONAL open-web action
- [ ] Tighten the UI + the activity-stream narration.
- [ ] **If ahead:** dump the cited results to GitHub Pages (~15 min) → gets back a "real open-web action" + a 3rd artifact. Skip if behind.
- [ ] Commit + push.

## 3:30–3:45 — FREEZE + pre-test
- [ ] Run the demo ask 5+ times. Save a known-good run as a **cached fallback** (in case an API flakes on camera).
- [ ] Clean README/repo so it tells the FEC + live-enrichment story. Delete/ignore anything stale.
- [ ] Commit + push. **Features frozen at 3:45.**

## 3:45–4:15 — RECORD the 3-min demo (I own Presentation)
- [ ] Beats: problem (15s) → type ask (20s) → autonomous run, NARRATE the live Nimble web pull (90s) → ranked cited results (30s) → ClickHouse + Nimble recap (25s).
- [ ] Use the cached fallback if live APIs flake. Re-record if rushed.
- [ ] **Upload the video to YouTube/Vimeo (unlisted ok) IMMEDIATELY and grab the link.** Devpost needs the URL, not a file — upload/processing takes a few minutes. Do this before submitting.

## 4:15–4:30 — SUBMIT (treat 4:15 as the deadline)
- [ ] Final `git pull --rebase` + push. Repo public.
- [ ] Devpost: repo link + **video LINK** (the uploaded URL) + all required fields. Submit with time to spare.

## If behind: cut from the bottom
Drop GitHub Pages publish → drop scoring polish → drop live integration (demo on mock data that looks real) → NEVER drop the recording. A polished mock demo beats a broken real one with no video.

## 🎬 PRE-RECORDING CHECKLIST + QUOTA SAFETY (do this before 3:45)
> Status at ~2:45 PM: real FEC data is LIVE (2.8M rows, 597k donors); query() returns real donors (Steyer, Ballmer, Wayburn). Core demo works. These are the de-risk items before recording.

### ⚠️ Quota safety — DO NOT hit a quota live on camera
- **Record on `?demo=1`.** The team baked a real, enriched environment/CA run into `web/sample_prospects.json`, so `?demo=1` replays it instantly and makes **zero live Gemini and zero live Nimble calls** during the recording. No quota can be hit on camera. This is the safe path — use it.
- **Gemini quota reality (2026-05-23):** `gemini-2.5-flash` AND `gemini-2.0-flash` are 429 quota-exhausted; only **`gemini-flash-latest`** works. It's set as `GEMINI_MODEL=gemini-flash-latest` in `.env` on the demo machine. (See `docs/STATUS.md`.)
- **If we want a LIVE parse on camera (riskier):** pre-raise the Gemini quota in Google AI Studio / Cloud console *before* recording — don't wait to hit the limit mid-take. If it 429s, nl_parse silently falls back to the deterministic keyword match (still works, but weakens the autonomy story). **Enes can bump the quota quickly if needed — do it ahead of time, not live.**
- **Nimble:** enrichments are pre-computed into the snapshot, so the demo needs no live Nimble credits. Only run live Nimble (`TRIBE_ENRICH=1`) for at most 2–3 rehearsals, never burn it on every test.

### Verify before recording
- [ ] **Open `?demo=1` and confirm cards show REAL donors** (Steyer/Ballmer/etc.), NOT the old seed names (Adams/Allen/Anderson). If the snapshot is stale, re-run `python server/build_demo_snapshot.py` (one command — refreshes from real, deduped data).
- [ ] **Click the top citation on a card** — confirm the fec.gov *individual-contribution* search actually lands on that person (links were reordered person-first in the snapshot).
- [ ] **Pre-test the exact demo ask 5×** and confirm `?demo=1` params/chips match the sentence typed (use `environment` / CA — avoid civil_rights/small_business/social_welfare, which are ~90% party-proxy tags per STATUS.md).
- [ ] Repo **public** + `.env` **gitignored** (no keys committed) before submit.
- [ ] **Upload the video immediately after recording**, grab the URL (processing takes minutes); Devpost needs the link.

## Note
Senso analysis is still in `STRATEGY.md` if we reconsider — dropping it loses the $3k track and the publish-to-web action, but removes the riskiest integration. Decision made ~11:30 to skip it.
