# Tribe

**An autonomous cause-affinity research agent for nonprofit fundraising.**

![Tribe landing page](docs/images/landing.png)

A fundraiser describes their cause in one plain-English sentence. Tribe parses it on its own, then searches 2.8 million real FEC public-record contributions in ClickHouse for donors whose actual giving behavior matches that cause. It enriches the top candidates from the live web with Nimble, scores them by cause-affinity, and returns a ranked list of prospects where every claim is cited. For each one, it drafts a personalized outreach email.

The idea is simple. Who already gives to your cause is a better signal than who happens to be wealthy. Tribe reads what people actually do with their money instead of screening for net worth.

> Built in one day for the Datadog Agentic Engineering Hack (2026-05-23).

---

## What it does

- **Natural-language search.** Type something like "Climate and clean-water givers on the West Coast" and the agent works out the cause, the geography, and the giving threshold on its own. No forms, no filters.
- **Real, cited prospects.** Every result is a real FEC donor, and every claim links back to the public filing on `fec.gov`. Nothing is a black-box score.
- **Live web enrichment.** Nimble pulls each top donor's current role and public bio in real time. Steyer resolves to Wikipedia, Serrurier to the Earthjustice board, and so on.
- **Drafted outreach.** One click drafts a personalized email grounded in the donor's real giving history. A human reviews it before anything gets sent.
- **A visible agent run.** The whole pipeline streams to the UI one step at a time over Server-Sent Events, so you watch the agent parse, query, rank, enrich, and score as it happens.
- **Continuous campaign agent.** Define a campaign in plain English and a background agent keeps re-running it, adding new high-affinity donors as fresh data comes in. No manual selection.

![Tribe ranked prospects with live agent activity and cited reasons](docs/images/demo.png)

---

## How it works

```
natural-language ask
   │
   ▼
NL parse  ── Gemini → { cause, geo, min_amount }   (deterministic synonym/adjacency fallback)
   │
   ▼
ClickHouse ── query 2.8M cause-tagged FEC contributions → ranked candidates  (dedup-safe)
   │
   ▼
Nimble ───── live web enrichment of the top candidates (role, bio, public profile)
   │
   ▼
Scoring ──── cause-affinity + recency + capacity → 0–100
   │
   ▼
UI ───────── ranked, cited prospect list (master-detail) + AI-drafted outreach
```

The run is exposed as a `/run` Server-Sent Events stream, so the frontend can render each agent step as it happens.

### The data

- **FEC bulk individual contributions.** About 2.8M real records, 597k donors, all 20 cause categories, across 5 states (CA, NY, TX, WA, OR), loaded into ClickHouse.
- **Committee to cause tagging.** Committees mapped to roughly 20 cause tags using keyword matching plus candidate-party inference.
- **ProPublica nonprofits and the FEC candidate master.** Extra org and candidate context.

---

## Tech stack

| Layer | Tech |
|---|---|
| Data warehouse | **ClickHouse** (FEC contributions, committees, causes, candidates) |
| Live web enrichment | **Nimble** Web Search API plus Gemini extraction |
| NL parse and email drafting | **Gemini** (`gemini-flash-latest`) |
| Backend | **FastAPI** with Server-Sent Events (Python) |
| Frontend | **Vite + React + TypeScript + Tailwind v4 + framer-motion** |

Sponsor tools are **ClickHouse** for the FEC data warehouse and **Nimble** for live web enrichment.

---

## Repo layout

```
agent/    Data pipeline: FEC bulk load into ClickHouse, committee-to-cause tagging,
          Nimble enrichment, ProPublica and candidate sources.
server/   FastAPI /run SSE backend. NL parse, query_clean (dedup-safe donor query),
          enrichment, scoring, stream. Plus the autonomy agents:
          auto_match.py and campaign_outreach.py.
web/      Vite/React frontend: ask box, live activity stream, master-detail
          prospect list with cited reasons, enrichment, giving history, draft email.
docs/     Strategy, data and query notes, demo script, judge Q&A, and more.
```

---

## Running locally

You need Python 3.11+, Node 20+, and access to a ClickHouse instance loaded with FEC data.

```bash
# 1. Secrets. Copy and fill in real values. .env is gitignored and never committed.
cp .env.example .env      # set CLICKHOUSE_*, NIMBLE_API_KEY, GEMINI_API_KEY

# 2. Backend
cd server && pip install -r requirements.txt
uvicorn main:app --port 8000

# 3. Frontend (separate terminal)
cd web && npm install
npm run dev               # http://localhost:5173
```

**Instant demo with no live API calls.** Open `http://localhost:5173/?demo=1`. This replays a real, pre-enriched run baked into `web/sample_prospects.json`. It's instant and reliable, with no Gemini or Nimble calls.

**The autonomy agent (terminal):**

```bash
python server/campaign_outreach.py demo   # campaigns, auto-match, find contact, draft email
python server/auto_match.py demo          # continuous campaign auto-matching
```

---

## Limitations and what's next

Where it stands after one day:

- **Ranking is capacity-first for now.** Results currently rank by total giving. The next step is affinity-first scoring (cause-specificity, then amount given to that cause, then recency, then geography) so the most relevant donor wins instead of the richest one. The design is in `docs/DEMO-FEEDBACK.md`.
- **The cause taxonomy is coarse, around 20 tags.** Niche asks like "animal shelter" map to the nearest tag, which is `environment`. Adding categories such as `animal_welfare` and improving the committee-tagging recall would sharpen the matches.
- **Contact info.** FEC has no emails or phones. The contact channels shown come from web enrichment, and the drafted emails are research outreach for a human to review, not automated solicitation.
- **Data scope** is 5 states and one cycle for the demo. The pipeline scales to all states and cycles.

---

## Ethics and legal

Tribe treats FEC data as public-record research on giving behavior, with every claim cited back to its public source, not as a solicitation contact list. 11 CFR §104.15 restricts using FEC individual-contributor data to solicit donations, so outreach here is framed as human-reviewed research and the contact channels are sourced independently from the web. See `docs/STRATEGY.md` for the full reasoning.

---

## Built by

Enes Yilmaz and Trevor at the Datadog Agentic Engineering Hack, built across multiple Claude Code agents that coordinated through git. See `docs/STATUS.md` for how the team split the work.
