# Tribe

Autonomous donor-prospecting agent. A fundraiser types a natural-language ask, and the agent finds the best real donors from FEC giving data, enriches them from the live web, and publishes a cited prospect profile for each.

Built for the Datadog Agentic Engineering Hack (2026-05-23). Sponsors used: ClickHouse, Nimble, Senso.

## Pipeline
NL ask → **ClickHouse** (query FEC bulk data → candidates) → **Nimble** (live web enrichment) → scoring → **Senso** (publish cited profile to cited.md)

## Who's building what (roles decided)
- **Friend — the scraper / data side (`agent/`).** Fills the database: FEC bulk load → ClickHouse, cause-tagging, and the live web enrichment (Nimble). Produces queryable, cause-tagged, enriched donor data. Owns the **ClickHouse** + **Nimble** tracks.
- **Me (Enes) — the platform (`web/` + serving).** Reads from the database: NL ask → query → score/rank → frontend → publish cited records (Senso). Owns the **Senso** ($3k) + **Presentation** scoring.

The two sides meet at one contract — the ClickHouse table the friend fills and the `prospect_record` JSON the platform reads/publishes. Build against the mock, integrate once. See `docs/TEAM-SPLIT.md`.

## Repo layout
- `agent/` — the scraper / data pipeline (FEC → ClickHouse → cause-tag → enrich). Friend's side.
- `web/` — the platform/site that reads the DB and publishes. My side.
- `docs/` — planning and reference
  - `STRATEGY.md` — win analysis, legal reframe, product spec, demo plan (read this)
  - `TEAM-SPLIT.md` — who does what + the data contract between the two sides
  - `PLAN.md` — time-boxed build sequence and descope rules
  - `SCHEDULE.md` — wall-clock plan for the day
  - `SPONSOR-TOOLS.md` — what each sponsor tool does and how it fits
  - `DEVPOST.md` — event facts and judging criteria
  - `skills/` — agent skill prompts for each pipeline stage

Start with `docs/STRATEGY.md`, then `docs/PLAN.md`. Commit and push frequently — see `CLAUDE.md`.
