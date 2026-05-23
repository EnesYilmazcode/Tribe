# Tribe

Autonomous donor-prospecting agent. A fundraiser types a natural-language ask, and the agent finds the best real donors from FEC giving data, enriches them from the live web, and publishes a cited prospect profile for each.

Built for the Datadog Agentic Engineering Hack (2026-05-23). Sponsors used: ClickHouse, Nimble, Senso.

## Pipeline
NL ask → **ClickHouse** (query FEC bulk data → candidates) → **Nimble** (live web enrichment) → scoring → **Senso** (publish cited profile to cited.md)

## Repo layout
- `agent/` — the Python agent pipeline (the working product, code goes here)
- `web/` — the site (later)
- `docs/` — planning and reference
  - `PLAN.md` — time-boxed build sequence and descope rules
  - `SCHEDULE.md` — wall-clock plan for the day
  - `SPONSOR-TOOLS.md` — what each sponsor tool does and how it fits
  - `DEVPOST.md` — event facts and judging criteria
  - `skills/` — agent skill prompts for each pipeline stage

Start with `docs/PLAN.md`.
