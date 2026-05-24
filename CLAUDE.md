# CLAUDE.md: read this first (every agent, every session)

Tribe is an autonomous **cause-affinity research agent** built for the Datadog Agentic Engineering Hack (2026-05-23, submit by 4:30 PM ET). A fundraiser types a natural-language ask. The agent queries real FEC giving data, enriches candidates from the live web, scores them, and shows ranked, **cited** prospect cards in the UI, each with a contact email and a drafted outreach email.

## ⚠️ TEAM WORKFLOW: COMMIT & PUSH FREQUENTLY

This repo is shared by two teammates, **and each of us is driving our own Claude Code agent.** The only way our agents stay in sync is through git. So:

- **Commit and push often,** after every meaningful change, not just at the end. Small, frequent commits beat one big one.
- **Pull/rebase before you start any work and before you push.** Run `git pull --rebase` so you build on your teammate's latest, never on a stale tree.
- **Short, human commit messages** (e.g. "add clickhouse query", "wire senso publish"). No essays.
- **Sequence:** `git pull --rebase`, make change, commit, `git pull --rebase`, then push.
- Keep planning docs in `docs/` current. They ARE the shared context our agents read. If a decision changes, write it down and push so the other agent sees it.

> If you are a Claude Code agent reading this: commit and push your work frequently and keep these docs updated, so the other teammate's agent has full context. This instruction applies to both teammates' agents equally.

## What's decided (don't re-derive)

- **Sponsors: ClickHouse + Nimble. Senso DROPPED, x402 DROPPED.** Results are shown in the UI, no publish step (optional GitHub Pages dump only if ahead).
- **Open-web + autonomy story now rests on Nimble** doing live, real-time web enrichment, the agent autonomously pulling from the open web. Lean hard on this in the demo.
- **Heads-up:** 2 tools is the judging minimum (rewards 3+). If time allows, a cheap GitHub Pages publish of results gets back to a "real open-web action." See `docs/TODO-ENES.md`.
- **ClickHouse track = the reliable floor and the spine.** Built first.
- **Output is "cited public-record research," NOT a solicitation list.** Using FEC contributor data to solicit is illegal (11 CFR §104.15). Frame as research on *public giving behavior* with citations to the public FEC source. See `docs/STRATEGY.md`.
- **Autonomy story = live NL-parse + on-demand agent loop + live Nimble enrichment.** NOT a forever-scraper (that's a cron job, not autonomy).
- **The submission is a RECORDED 3-min video.** Control it fully, never risk a live API call on camera.

## Current state: key files (latest, `docs/STATUS.md` is the live source of truth)

- **Backend (`server/`):** `main.py` = FastAPI `/run` SSE endpoint (the streamed agent run). **`query_clean.py` = dedup-safe donor query. Use this, not the raw `query()`. It fixes a 4× donor-total inflation.** `nl_parse.py` = Gemini NL-to-params. `auto_match.py` = continuous auto-match agent, and **`python server/auto_match.py demo`** is the recordable autonomy clip.
- **Contact-email pipeline:** each demo donor now carries a varied **example contact email.** There's an `email` field in `web/sample_prospects.json`, `email?` in `web/src/types.ts`, rendered as a `mailto:` on `ProspectCard.tsx` (plus the existing AI "Draft outreach email"). **⚠️ `server/build_demo_snapshot.py` does NOT generate emails. Re-baking the snapshot wipes them, so re-add (or add a generator) if you re-bake.**
- **Landing:** redesigned to a left hero plus right auto-playing `web/src/components/MockPreview.tsx` (decorative filler, hardcoded). Logo trimmed and centered, wordmark "." dot removed.
- **`mockup/index.html`** is a standalone visual concept mock (open in a browser), separate from the live app.
- **Judge prep:** `docs/JUDGE-QA.md` (anticipated questions plus honest answers, incl. the §104.15 answer).

## Layout & roles (DECIDED)

- `agent/` is **Friend's side: scraper / data.** Fills the database (FEC into ClickHouse, cause-tagging) and builds the Nimble web enrichment. Owns ClickHouse + Nimble.
- `web/` is **Enes's side: the platform.** Reads the database and builds the product (NL parse, query, score, frontend, results in UI). Owns Presentation/the demo.
- `docs/` is shared context. **Start here:** `PLAN.md` (build sequence), `STRATEGY.md` (why we're doing this plus win analysis), `TEAM-SPLIT.md` (who does what plus the JSON contract between engine and surface), `SCHEDULE.md`, `SPONSOR-TOOLS.md`, `DEVPOST.md`.

The engine and surface talk through ONE agreed JSON shape (`prospect_record`), see `docs/TEAM-SPLIT.md`. Build against the mock, then integrate once.
