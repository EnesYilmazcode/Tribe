# DEVPOST — Agentic Engineering Hack (Datadog)

> Working doc to keep submission details organized. Source: Devpost listing, captured 2026-05-23.

## Event
- **Hackathon:** Agentic Engineering Hack (hosted by Datadog)
- **Deadline:** May 23, 2026 @ 4:30pm EDT (project submission)
- **Format:** Single-day. Coding 11:00 AM → 4:30 PM ET. Finalists/judging 5:00 PM, awards 7:00 PM.
- **Demo:** 3 minutes, live.
- **Team size:** Max 4.
- **Constraints:** No previous projects. Public GitHub repo required. Must use **2+ sponsor tools** (judging rewards **3+**).
- **Prize pool:** $5,000+ cash + credits.

## Theme
Ship an **autonomous agent that does real work on the open web** — publish, monitor, orchestrate, transact — grounded in **real sources**. Monetize with agent payment rails (x402, MPP, CDP, agentic.market).

## Judging criteria (20% each)
| Criterion | What they want |
|---|---|
| **Autonomy** | Agent acts on real-time data with no manual intervention |
| **Idea** | Solves a meaningful problem / real-world value |
| **Technical Implementation** | How well it's built |
| **Tool Use** | Effective use of 3+ sponsor tools |
| **Presentation** | 3-minute demo |

## Sponsor tracks
- **Nimble** — $1,500 cash + credits (2 winners). Best use of Nimble's API / Web Search Agents.
- **ClickHouse** — $1,000 cash + credits (2 winners). "Makes your life better" OR "Impact in community/World."
- **Senso.ai** — $3,000 credits (1 winner). Use Senso content-gen APIs to publish grounded, **citeable** content to `cited.md` (or another public destination). **Ingestion alone won't qualify** — must close the loop from knowledge base → published, agent-discoverable content. Docs: docs.senso.ai

## What to submit
1. **Demo video LINK** — the 3-min video must be uploaded to YouTube/Vimeo (unlisted is fine) and the **public URL pasted into Devpost.** A local file does NOT count. Upload right after recording — leave buffer for the upload to finish processing.
2. Public GitHub repo
3. All Devpost-required project details

## Our project — Tribe (donor-prospecting agent)
**One-liner:** Fundraiser types a natural-language ask → agent finds the best real donors and publishes cited prospect profiles, autonomously.

**Pipeline & tool mapping (3 sponsors — all with prize tracks):**
1. **ClickHouse** — query preloaded FEC bulk donation data (~tens of millions of real records) for cause-affinity candidates
2. **Nimble** — live-enrich each top candidate from public web sources
3. **Senso** — publish a cited prospect profile per match to cited.md (closes the KB → published loop)

*x402 (payment rail) is out of scope — not a prize-track sponsor, too much setup risk. The 3 above already meet the "3+ tools" judging mark.*

**Why it fits the theme:** Cause-affinity matching from *real giving behavior* (FEC is the only bulk, cause-tagged donation data) is a stronger fundraising signal than wealth screening. The agent acts on real data and takes real open-web action (publishing cited profiles).

## Status / TODO (as of capture)
- [ ] Repo currently has only skill-prompt specs + README stub — no running code yet
- [ ] Skill prompts describe generic CRM/wealth-screening flow; need to align to FEC + ClickHouse + Nimble + Senso
- [ ] Wire ClickHouse with FEC data loaded
- [ ] Wire Nimble enrichment
- [ ] Wire Senso → cited.md publishing
- [ ] Record 3-min demo
- [ ] Finalize public repo + Devpost submission
