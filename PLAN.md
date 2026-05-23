# PLAN — Tribe: Autonomous Donor-Prospecting Agent

> Build plan for the Datadog Agentic Engineering Hack. **Deadline: today, 2026-05-23 @ 4:30pm ET.**
> Status at start: nothing built yet (only skill-prompt specs + README). ~5 hours on the clock.
> Guiding rule: **protect the 3-minute demo.** A working spine beats a half-wired 4-tool stack that breaks on stage.

## The product (one-liner)
A fundraiser types a natural-language ask ("I need major donors for a clean-water campaign in the Pacific Northwest"). The agent autonomously: queries real FEC donation data → finds cause-affinity matches → enriches them from the live web → publishes a cited prospect profile for each → meters the deep-enrichment calls as paid actions.

## Sponsor-tool mapping (4 tools — judging needs 3)
| Tool | Role in pipeline | Track eligibility |
|---|---|---|
| **ClickHouse** | Query preloaded FEC bulk donation data for cause-affinity candidates | ClickHouse track |
| **Nimble** | Live-enrich top candidates from public web sources | Nimble track |
| **Senso** | Publish a cited prospect profile per match to cited.md | Senso track (must close KB→published loop) |
| **x402** | Meter deep-enrichment calls (payment rail) | Monetization bonus |

## Architecture (keep it flat — it's a hackathon)
```
NL ask
  │
  ▼
[Agent orchestrator]  ── parses ask → cause tags, geography, capacity
  │
  ▼
ClickHouse  ── SQL over FEC contributions → ranked candidate list
  │
  ▼
Nimble      ── for top N: live web enrichment (employer, bio, current giving)
  │
  ▼
Scoring     ── cause-affinity + recency + capacity → 0–100
  │
  ▼
Senso       ── publish cited prospect profile → cited.md   ◄── the "real open-web action"
  │
  ▼
x402        ── meter each deep-enrichment as a paid call
```

## Time-boxed build sequence (descope from the bottom up)
Each phase ends in something demoable. If we run out of time, we stop at the last completed phase and demo that.

### Phase 0 — Setup (~30 min) — DO FIRST, IN PARALLEL ACROSS TEAM
- [ ] Pick stack: **Python** (fastest for ClickHouse + HTTP + an LLM orchestrator). Single `agent.py` entrypoint.
- [ ] Get API keys / accounts: ClickHouse Cloud, Nimble, Senso, x402. **One person owns each — start signups now, they're the long pole.**
- [ ] Download FEC bulk data: individual contributions (`indiv` file) from FEC bulk-data, OR use a trimmed sample if full load is too slow. https://www.fec.gov/data/browse-data/?tab=bulk-data
- [ ] Repo scaffolding: `agent.py`, `clickhouse_client.py`, `nimble_client.py`, `senso_client.py`, `x402_client.py`, `.env.example`, `requirements.txt`.

### Phase 1 — ClickHouse spine (~75 min) ← MINIMUM VIABLE DEMO STARTS HERE
- [ ] Load FEC contributions into a ClickHouse table (committee_id, contributor name/employer/occupation, amount, date, recipient, state).
- [ ] Map recipient committees → cause tags (small lookup table; even a hand-built ~20-cause map is fine for demo).
- [ ] Write the candidate query: given cause tags + geography + capacity band, return top contributors ranked by total giving to matching causes + recency.
- [ ] Hard-code a sample NL ask → parsed params for now (LLM parsing comes in Phase 4).
- **Checkpoint:** `python agent.py` prints a ranked list of real donors from real FEC data. *This alone covers Autonomy + ClickHouse track.*

### Phase 2 — Senso publishing (~60 min) ← THIS IS THE HIGHEST-EV TRACK ($3k, 1 winner)
- [ ] For top candidate(s), assemble a prospect profile (name, giving history pulled from FEC, match reasoning, suggested ask).
- [ ] Call Senso content-gen API to produce a grounded, **cited** profile and publish to cited.md (or chosen public destination).
- [ ] Verify the published page renders with citations back to FEC source rows. **Ingestion alone does NOT qualify — must publish.**
- **Checkpoint:** End-to-end NL→FEC→published cited profile. *Covers Autonomy + ClickHouse + Senso = 3 tools = judging threshold met. If we ship nothing else, we can still win.*

### Phase 3 — Nimble enrichment (~45 min)
- [ ] For each top candidate, fire a Nimble web search/agent to pull current public signals (employer, recent public giving, board roles).
- [ ] Merge enrichment into the profile before Senso publishes (re-order: enrich → then publish).
- **Checkpoint:** Profiles now blend historical FEC data + live web data. *Adds Nimble track + strengthens Autonomy.*

### Phase 4 — Autonomy polish + x402 (~45 min)
- [ ] LLM parses the raw NL ask into cause tags / geography / capacity (replaces hard-coded params). This is the key "no manual intervention" autonomy story.
- [ ] x402: wrap the Nimble deep-enrichment call so it's metered as a paid action (even one real metered call sells the payment-rail narrative).
- **Checkpoint:** Type a sentence → fully autonomous run → published profiles, with metered paid calls. *All 4 tools live.*

### Phase 5 — Demo prep (~45 min) — RESERVE THIS, DO NOT SKIP
- [ ] Pick ONE clean, reliable example ask that gives an impressive result. Pre-test it 5+ times.
- [ ] Have a fallback: cached/recorded run in case live APIs flake on stage.
- [ ] Record the 3-min demo: problem (10s) → type the ask (20s) → watch it run autonomously (90s) → show the published cited.md profile (30s) → tool/architecture recap (30s).
- [ ] Clean README so the repo tells the FEC story (the current skill files describe the OLD generic-CRM direction — fix or delete them).
- [ ] Submit on Devpost (repo link + recording + details). **Do this with 15 min to spare — late submissions may be cut off.**

## Hard descope rules
- If behind at any checkpoint, **stop adding tools and lock the demo** at the last working phase.
- **Phase 2 (Senso) is the priority over Phase 3 (Nimble)** — it's the $3k single-winner track with the cleanest fit, and it completes the 3-tool threshold.
- Never demo a feature live that hasn't been run 3+ times successfully. Use the cached fallback.
- LLM parsing (Phase 4) is the only thing standing between "scripted" and "autonomous" in the judges' eyes — if you must cut something, cut x402 before cutting NL parsing.

## Known risks
- **FEC bulk load time** — full individual-contributions file is huge. Use a state/year-trimmed subset for the demo.
- **Senso "publish" requirement** — confirm early that we can actually publish to cited.md, not just ingest. This gates the $3k track.
- **API signups** — sponsor accounts/keys are the long pole. Start all four in Phase 0.
- **Stale skill files** — `prospect-finding/scoring/outreach/crm-tracking.md` describe the old direction and will confuse judges; align them or remove from the demo path.
