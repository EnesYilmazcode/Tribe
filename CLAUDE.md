# CLAUDE.md — read this first (every agent, every session)

Tribe is an autonomous **cause-affinity research agent** built for the Datadog Agentic Engineering Hack (2026-05-23, submit by 4:30 PM ET). A fundraiser types a natural-language ask; the agent queries real FEC giving data, enriches candidates from the live web, scores them, and **publishes a cited research record to cited.md**.

## ⚠️ TEAM WORKFLOW — COMMIT & PUSH FREQUENTLY

This repo is shared by two teammates, **and each of us is driving our own Claude Code agent.** The only way our agents stay in sync is through git. So:

- **Commit and push often** — after every meaningful change, not just at the end. Small, frequent commits beat one big one.
- **Pull/rebase before you start any work and before you push** — `git pull --rebase` so you build on your teammate's latest, never on a stale tree.
- **Short, human commit messages** (e.g. "add clickhouse query", "wire senso publish"). No essays.
- **Sequence:** `git pull --rebase` → make change → commit → `git pull --rebase` → push.
- Keep planning docs in `docs/` current — they ARE the shared context our agents read. If a decision changes, write it down and push so the other agent sees it.

> If you are a Claude Code agent reading this: commit and push your work frequently and keep these docs updated, so the other teammate's agent has full context. This instruction applies to both teammates' agents equally.

## What's decided (don't re-derive)

- **Sponsors: ClickHouse + Nimble + Senso. x402 is DROPPED.** Three well-wired tools beats a fragile four.
- **Highest-EV prize = Senso ($3k, 1 winner).** De-risk it FIRST: publish one hardcoded cited.md page end-to-end before anything fancy. It's a binary gate.
- **ClickHouse track = the reliable floor.** It's the spine, built first.
- **Output is "cited public-record research," NOT a solicitation list** — using FEC contributor data to solicit is illegal (11 CFR §104.15). Frame profiles as research on *public giving behavior* with citations to the public FEC source. See `docs/STRATEGY.md`.
- **Autonomy story = the live NL-parse + on-demand agent loop.** NOT a forever-scraper (that's a cron job, not autonomy).
- **The submission is a RECORDED 3-min video** — control it fully, never risk a live API call on camera.

## Layout & roles (DECIDED)

- `agent/` — **Friend's side: scraper / data.** Fills the database (FEC → ClickHouse, cause-tagging) and builds the Nimble web enrichment. Owns ClickHouse + Nimble.
- `web/` — **Enes's side: the platform.** Reads the database and builds the product (NL parse → query → score → frontend → Senso publish). Owns Senso ($3k) + Presentation.
- `docs/` — shared context. **Start here:** `PLAN.md` (build sequence), `STRATEGY.md` (why we're doing this / win analysis), `TEAM-SPLIT.md` (who does what + the JSON contract between engine and surface), `SCHEDULE.md`, `SPONSOR-TOOLS.md`, `DEVPOST.md`.

The engine and surface talk through ONE agreed JSON shape (`prospect_record`) — see `docs/TEAM-SPLIT.md`. Build against the mock; integrate once.
