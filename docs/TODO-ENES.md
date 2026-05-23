# TODO — Enes (the platform side). Wall-clock for 2026-05-23

> My half: read the DB → NL parse → query → score → frontend → **publish cited.md (Senso)**. Owns Senso ($3k) + Presentation.
> Friend's half (`agent/`): FEC → ClickHouse + cause-tag + Nimble `enrich()`. Not my job — I build against the mock until integration.
> **Rule: commit + push after EVERY block.** `git pull --rebase` first, short message, push. See `CLAUDE.md`.
> Now: 11:30 AM. Wall: 4:30 PM. Record at 3:45. Treat 4:15 as the real deadline.

## 11:30–11:45 — Joint sync + lock the contract (with friend)
- [ ] Agree the `prospect_record` JSON shape together (see `TEAM-SPLIT.md`). 5 min, no bikeshedding.
- [ ] Pick the ONE demo ask we'll record (e.g. "Major clean-water + environment donors in the Pacific Northwest"). Write it down.
- [ ] Write `web/sample_prospects.json` (3–5 realistic mock records). Commit + push so both of us build against it.

## 11:45–12:30 — DE-RISK SENSO (do this before anything fancy — binary $3k gate)
- [ ] Sign up / get `SENSO_API_KEY`. Install the CLI (`npm i -g @senso-ai/cli`), `senso whoami`.
- [ ] Publish ONE hardcoded cited.md page end-to-end (title/handle/slug/body/tags + a citation).
- [ ] Open the published URL — confirm it renders with the citation AND has the machine-readable markdown/JSON view.
- [ ] If publish is blocked: flag it loud, fall back to publishing cited markdown to a public GitHub Pages/repo path. Don't move on until the loop closes.
- [ ] Commit + push the working publish script (`web/senso_publish.*`).

## 12:30–1:15 — Frontend skeleton against the mock (use the `frontend-design` skill)
- [ ] Ask box (single NL input) + submit.
- [ ] Live agent activity stream (the autonomy money-shot — fake the steps for now).
- [ ] Cited prospect cards rendering `sample_prospects.json` (name, score, cited reasons, link).
- [ ] Commit + push.

## 1:15–1:45 — NL parse + wire the query call (grab lunch ~1:30, eat at desk)
- [ ] LLM parse: sentence → `{cause, geo, min_amount}`. Show parsed params in the activity stream.
- [ ] Call a `query()` stub that returns the mock for now (real one comes at integration).
- [ ] Commit + push.

## 1:45–2:30 — Wire REAL Senso publish into the flow
- [ ] For each top record: assemble the cited research record (NO suggested_ask / outreach in the published artifact — legal reframe, see `STRATEGY.md`).
- [ ] Publish via the de-risked path; each card links to its live cited.md page.
- [ ] Commit + push.

## 2:30–3:00 — Scoring + polish
- [ ] Score 0–100 (affinity + recency + capacity) with 2–3 cited reasons each; rank.
- [ ] Make the activity stream narrate the REAL steps (parse → query → decide → enrich → score → publish).
- [ ] Commit + push.

## 3:00–3:30 — Integration with friend
- [ ] Swap the `query()` stub for friend's real ClickHouse `query()`; call `enrich()` on top-N.
- [ ] Run the chosen demo ask end-to-end on REAL data. Fix what breaks.
- [ ] Commit + push.

## 3:30–3:45 — FREEZE + pre-test
- [ ] Run the demo ask 5+ times. Save a known-good run as a **cached fallback** (in case an API flakes on camera).
- [ ] Clean README/repo so it tells the FEC/cited-research story. Delete/ignore anything stale.
- [ ] Commit + push. **Features frozen at 3:45 — anything broken now doesn't go in the demo.**

## 3:45–4:15 — RECORD the 3-min demo (I own Presentation)
- [ ] Beat sheet: problem (15s) → type ask (20s) → autonomous run (90s) → land on published cited.md page w/ citations (30s) → 3-tool recap (25s).
- [ ] Use the cached fallback if live APIs flake. Re-record if rushed.

## 4:15–4:30 — SUBMIT (treat 4:15 as the deadline)
- [ ] Final `git pull --rebase` + push. Repo public.
- [ ] Devpost: repo link + video + all required fields. Submit with time to spare.

## If behind: cut from the bottom
Drop scoring polish → drop live integration (demo on mock data that looks real) → NEVER drop the Senso publish or the recording. A polished mock demo beats a broken real one with no video.
