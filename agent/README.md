# agent/

The Python agent pipeline — the actual working product. This is where code lives.

Planned files (see `../docs/PLAN.md` Phase 0):
- `agent.py` — entrypoint and orchestrator (NL ask → candidates → enrich → publish)
- `clickhouse_client.py` — query the FEC bulk data
- `nimble_client.py` — live web enrichment of candidates
- `senso_client.py` — publish cited prospect profiles to cited.md
- `.env.example` — required keys (ClickHouse, Nimble, Senso)
- `requirements.txt`

Skill prompts that drive the agent stages live in `../docs/skills/`.
