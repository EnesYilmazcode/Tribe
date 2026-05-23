# Tribe

Autonomous **cause-affinity research agent**. A fundraiser types a natural-language ask; the agent parses it, queries real **FEC public-record giving data** in ClickHouse, enriches the top candidates from the live web with Nimble, scores them by cause-affinity, and returns ranked, **cited** prospect records in the UI.

Built for the Datadog Agentic Engineering Hack (2026-05-23). Sponsor tools: **ClickHouse** (FEC data warehouse) and **Nimble** (live web enrichment). *(Senso and x402 were dropped — results render in the UI rather than publishing to an external doc.)*

> Framing: this is research on **public giving behavior** with citations back to the public FEC source — not a solicitation list. See `docs/STRATEGY.md`.

## Pipeline
NL ask → **NL parse** (Gemini → `{cause, geo, min_amount}`, with a deterministic synonym/adjacency fallback) → **ClickHouse** (query cause-tagged FEC contributions → candidates) → **Nimble** (live web enrichment of the top candidates) → scoring (cause-affinity + recency + capacity, 0–100) → ranked, cited prospect cards in the UI.

The whole run streams to the frontend as **Server-Sent Events**, so the agent's steps are visible live — the autonomy money-shot.

## Who's building what (roles decided)
- **Friend — the data side (`agent/`).** FEC bulk load → ClickHouse, committee→cause tagging, and live web enrichment (Nimble), plus extra sources. Owns the **ClickHouse** + **Nimble** tracks.
- **Me (Enes) — the platform (`server/` + `web/`).** NL parse → query → score/rank → frontend, served over SSE. Owns **Presentation** / the demo.

The two sides meet at one contract — the ClickHouse table the friend fills and the `prospect_record` JSON the platform reads. Build against the mock, integrate once. See `docs/TEAM-SPLIT.md`.

## Repo layout
- `agent/` — data pipeline: FEC → ClickHouse → cause-tag → Nimble enrich, plus extra sources (ProPublica nonprofits, multi-cycle FEC, candidate master). Friend's side.
- `server/` — the `/run` SSE backend (Enes). NL parse → ClickHouse `query()` → optional Nimble enrich → streams the run. Falls back to `web/sample_prospects.json` until the contributions table is populated.
- `web/` — the frontend (Enes). Ask box + **live agent activity stream** + ranked cited prospect cards.
- `docs/` — planning & reference: `STRATEGY.md` (win analysis + legal reframe — read first), `PLAN.md` (build sequence), `TEAM-SPLIT.md` (roles + data contract), `SCHEDULE.md`, `SPONSOR-TOOLS.md`, `DEVPOST.md`, `QUERYING.md` (NL→query mapping), `TAGGING-QUALITY.md` (known tag issues), `skills/` (per-stage prompts).
- `tools/timer.html` — the day's pacing timer.

## Status (2026-05-23)
- **Frontend:** working demo end-to-end on mock data, plus a live SSE run with automatic mock fallback. ✅
- **NL parse + `/run` SSE backend:** built. ✅
- **ClickHouse:** committees (~20.9k) and committee_causes (~2.3k tagged) loaded; **individual contributions loading.** The live run auto-switches from the sample fallback to real donors the moment that table is populated.
- **Nimble enrichment:** wired, off by default (`TRIBE_ENRICH=1` to enable).

## Run locally
Backend: see `server/README.md`. Frontend: see `web/README.md`. Keys live in a gitignored `.env` (see `.env.example`).

Start with `docs/STRATEGY.md`, then `docs/PLAN.md`. Commit and push frequently — see `CLAUDE.md`.
