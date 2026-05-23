# SPONSOR TOOLS — reference for Tribe

> Canonical reference for which sponsor tools we use, what each does, and how they fit our pipeline.
> Read this before touching integration code. Companion to `PLAN.md` and `DEVPOST.md`.

## What "tool" means here (settled)
- A **sponsor tool = a sponsor company/platform**, not a product inside it.
- Rule: **use 2+ sponsor tools.** Judging rewards **3+** (Tool Use is 20% of score).
- Using multiple products from ONE sponsor (e.g. Nimble Search + Crawl) still counts as **one** tool for the threshold, but deepens the "effective use" score.
- **We use 4 sponsors: Nimble, ClickHouse, Senso, x402.** Need 3, planning all 4 = safe margin.

## The pipeline and where each tool sits
```
NL ask
  │  (LLM parses ask → cause tags, geography, capacity)
  ▼
ClickHouse ── instant query over preloaded FEC bulk data → ranked candidates
  │
  ▼
Nimble ──── live web enrichment of top candidates (employer, bio, recent giving)
  │
  ▼
Scoring ─── cause-affinity + recency + capacity → 0–100
  │
  ▼
Senso ───── publish a cited prospect profile to cited.md
  │
  ▼
x402 ────── meter the deep-enrichment / per-fetch access as paid calls
```
Order note: **ClickHouse first** (find candidates from bulk FEC data, milliseconds), **Nimble second** (enrich them from the live web). Not the other way around.

---

## 1. ClickHouse — the FEC search layer
**What it is:** Open-source columnar OLAP database for real-time analytics. Queries billions of rows in milliseconds.
**Our use:** Load FEC bulk individual-contribution data (~tens of millions of rows). Query by cause tag + geography + capacity band to instantly rank candidate donors by giving behavior.
**How to access:**
- **ClickHouse Cloud** — serverless hosted, free trial available. Fastest for a hackathon (no infra).
- **Open-source server** — always free, self-host if Cloud signup is slow.
- Query via SQL over HTTP interface or the Python client (`clickhouse-connect`).
**Track:** "Makes your life better" OR "Impact in community/World." Our cause-affinity matching fits the impact angle.
**Docs:** https://clickhouse.com/cloud · https://clickhouse.com/docs

## 2. Nimble — live web enrichment
**What it is:** Real-time web intelligence via Web Search Agents. Turns the live internet into structured data. REST API, zero infra.
**Products (all count as the one Nimble "tool"):**
- **Search API** — AI agents search the live web for precise info + optional answer synthesis. `nimble.search(query=..., include_answer=True)`. Best for "what is this person doing now."
- **Extract API** — clean structured data/HTML/markdown from any URL. `nimble.extract(url=..., formats=["markdown"])`.
- **Web Search Agents** — pre-built or custom agents that extract structured knowledge from a site. `nimble.agent.run(agent=..., params=...)`.
- **Crawl API** — bulk extract a whole site in one request.
- **Map API** — discover a site's URL structure.
- **MCP server** — feed Nimble data to agents over Model Context Protocol.
**Our use:** For each top FEC candidate, fire Search/Extract to pull current public signals (employer, bio, board roles, recent public giving) before publishing.
**Track:** Best use of Nimble's API / Web Search Agents.
**Docs:** https://docs.nimbleway.com/home · https://www.nimbleway.com/

## 3. Senso — publish cited content (the $3k track)
**What it is:** "The context layer for AI agents" (YC W24). CMS for the agentic web — ingest knowledge, search it, generate content, and **publish citeable content to cited.md**.
**cited.md:** an open, agent-native domain where experts publish structured context and agents cite (and pay to fetch) it. Published at `cited.md/<handle>/<slug>`. Content schema: `title`, `handle`, `slug`, `body`, `tags`, `provenance`. Served as both human HTML and agent-native markdown+JSON.
**How to access:**
- CLI-first / agent-driven, not raw REST: `npm install -g @senso-ai/cli`, set `SENSO_API_KEY`, then `senso whoami`.
- The "cited" skill interviews/structures content into the schema and publishes the citeable.
- Workflow: ingest source data → generate grounded draft → publish citeable to cited.md.
**Track (READ CAREFULLY):** $3k credits, **1 winner**. Must **close the loop from knowledge base → published, agent-discoverable content.** Ingestion alone does NOT qualify — you must publish a cited.md (or other public) destination. This is the highest-EV track (smallest field, cleanest fit).
**Our use:** Publish one cited prospect profile per match to cited.md, with citations back to the FEC source rows. This IS our "real open-web action."
**Docs:** https://docs.senso.ai · https://www.senso.ai/cited-md · https://cited.md/

## 4. x402 — agent payment rail
**What it is:** Open payment standard using HTTP 402 Payment Required. Lets agents pay onchain in stablecoins at the HTTP level.
**How it works:** Agent requests a paid resource → server returns HTTP 402 with payment instructions → agent signs a stablecoin authorization → attaches proof, retries → server verifies and returns data. A **facilitator** (Coinbase/CDP hosts one) abstracts the blockchain via `POST /verify` and `POST /settle`.
**Free tier:** CDP facilitator processes ERC-20 payments on Base, Polygon, Arbitrum, World, Solana — **1,000 transactions/month free.**
**Native fit:** cited.md content is designed to be **priced per fetch via x402 micropayments** — so metering profile access or deep-enrichment with x402 is the intended design, not bolted-on.
**Our use:** Meter deep-enrichment calls and/or per-fetch access to published profiles as paid x402 calls. Even one real metered call sells the payment-rail narrative.
**Docs:** https://docs.cdp.coinbase.com/x402/welcome · https://www.x402.org/

---

## Build priority (mirrors PLAN.md descope order)
1. **ClickHouse** — the spine, do first. Covers Autonomy + ClickHouse track.
2. **Senso** — second. Completes the 3-tool threshold and the $3k single-winner track. Confirm you can actually *publish*, not just ingest.
3. **Nimble** — third. Adds the Nimble track and stronger enrichment.
4. **x402** — last. Native fit with cited.md per-fetch pricing; cut before cutting NL parsing if time runs out.

## Risks specific to tools
- **Senso publish path** — verify early you can publish to cited.md (it's CLI/agent-driven, not plain REST). Gates the $3k track.
- **FEC bulk load** — full individual-contributions file is huge; load a state/year-trimmed subset for the demo.
- **API signups are the long pole** — one owner per sponsor, start all four at 11:00.
