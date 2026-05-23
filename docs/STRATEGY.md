# STRATEGY — Tribe win analysis & product spec

> Why we're building what we're building, and how we win. Companion to `PLAN.md` (how) and `DEVPOST.md` (rules).
> Based on research done 2026-05-23. Read this before arguing about direction.

## ⚠️ The FEC legal reframe (most important thing in this doc)

Using **FEC individual-contributor data to solicit donations is illegal** — 11 CFR §104.15 ("sale or use" restriction). The FEC has clarified it covers **charitable** solicitation too, and it's been enforced (Rep. Ro Khanna fined $16k, 2021; the *Tally Up* case). The prospect-research industry's own body (Apra) advises against using FEC data for fundraising.

A profile that says "named person + address → go ask them for money" is exactly the prohibited use.

**The fix is framing, not a rebuild.** Tribe's output is a **cited, publicly-sourced cause-affinity research record** — research intelligence on *public giving behavior* — NOT a solicitation contact list.
- Cite every claim back to the public FEC source row.
- Keep `suggested_ask` / `outreach_approach` OUT of the published cited.md artifact (that's the part that reads as solicitation). Internal-only if at all.
- This is also exactly what the Senso "cited/grounded public content" track rewards. Have the 11 CFR §104.15 answer rehearsed — it's the first hard question a sharp judge asks.

## Win-odds per prize (ranked by EV for THIS project)

| Prize | Odds | Note |
|---|---|---|
| **Senso — $3k credits, 1 winner** | **Highest ceiling, BINARY** | Near-perfect fit (publish cited FEC-grounded record). But ingestion alone scores ~0 — you win ONLY if the page renders with citations. De-risk first. |
| **ClickHouse — $1k, 2 winners** | **Best floor / most reliable** | Soft bar ("impact on community/world"), 2 slots, it's the spine (least likely to break). Safety medal. |
| **Overall grand — $5k+** | **Dark horse** | We score well on all 5 criteria. Weakness: autonomy is partly a fixed pipeline. Win by being the most complete/polished end-to-end product. |
| **Nimble — $1.5k, 2 winners** | **Long shot, don't chase** | Nimble rewards projects where web-search IS the centerpiece; for us it's mid-pipeline enrichment. Bonus only. |

## Specialize vs spread: SPECIALIZE

Tool Use is only 20% and the threshold for full credit is **3 tools**, not 4. Going 3→4 adds integration surface that can break the demo (Presentation, another 20%) and the "no manual intervention" story (Autonomy, another 20%). A half-wired 4th tool can cost two criteria to gain a fraction of one. **Build 3 well (ClickHouse → Nimble → Senso), go deep on Senso, drop x402.**

## Score-maxing per criterion (20% each)

- **Autonomy** (improvable gap): live LLM NL-parse in the demo is non-negotiable — it's the whole "no manual intervention" story. Show the agent *deciding* which candidates warrant deep enrichment (converts "pipeline" → "agent").
- **Idea** (strong): "read who's already given to the cause" beats wealth-screening. Lead with the problem in one line; quantify ("queried 20M real records").
- **Technical** (strong): show real ClickHouse latency on real row counts; show the cited.md machine-readable JSON/markdown to prove it's agent-discoverable. Don't dwell on the hand-built cause taxonomy.
- **Tool Use** (strong): show each tool doing distinct, necessary work (ClickHouse=find, Nimble=enrich-live, Senso=publish). Avoid tool-stuffing optics.
- **Presentation** (decided by prep): it's RECORDED — control it fully. Pre-test the one chosen ask 5+ times; keep a cached fallback run; never risk a live call on camera.

## Uniqueness (vs incumbents AND other teams)

"We use FEC data" is NOT the differentiator — DonorSearch/Kindsight already do, and the political→charitable signal is imperfect (studies show partial substitution). Lead with:
1. **Agentic NL interface** — type a sentence, the agent reasons. Incumbents are $4–5k/yr credit-gated dashboards.
2. **Cited, auditable reasoning** ← strongest, most defensible lever. Incumbent scores are black boxes; every Tribe claim links to its public source. Also exactly what Senso rewards.
3. **Transparent cause-affinity chain** instead of an opaque proprietary number.
4. **Live, on-demand enrichment** vs. periodically-refreshed static profiles.
5. **Accessibility** for small nonprofits priced out today (good story, not a judging lever).

Vs other hackathon teams: our moat is **completeness + polish + the closed cited.md loop on real data at real scale.** Most teams ship half-built slideware.

## Product spec (what it actually is)

One NL ask in → ranked **cited cause-affinity research records** out, published to cited.md, zero manual steps between. The agent loop:
1. **Parse** (LLM, live) — "climate donors in California who gave $500+" → `cause=environment, state=CA, min=500`.
2. **ClickHouse** — query the cause-tagged FEC subset → ranked candidates (ms).
3. **Agent decision** — pick top-N to deep-enrich based on score.
4. **Nimble** — live web enrichment (current role, public board seats, recent activity).
5. **Score & rank** — affinity + recency + capacity → 0–100, with cited reasons.
6. **Senso** — publish each as a cited research record to cited.md, citations → FEC source rows. ← money shot.

**Data scope (feasible in hours):** one cycle (2024), 2–3 states (CA/NY/TX), amount ≥ $200 → low-single-digit-million rows; sub-second queries. Hand-curate top ~50 committees by volume so demo causes are 100% accurate; keyword + LLM-classify the rest into ~20 cause tags joined on `CMTE_ID` (from the FEC committee master file).

**On the "scrape forever" question:** No. FEC data refreshes ~weekly; a forever-crawler is a cron job, not autonomy. Build **on-demand**, present the decision-loop as autonomous. The real-time part is live web enrichment, not a background scraper.

## Example user workflow

Maya, dev director at a small clean-water nonprofit (priced out of iWave):
1. One input box: "Describe who you're looking for."
2. Types: "Major donors who care about clean water and the environment in the Pacific Northwest."
3. **Live activity stream** shows the agent reasoning: parsed params → queried 4.2M FEC records (38ms) → selected top 25 → enriching 8 via live web → publishing.
4. **Ranked cards** fill in: name, 0–100 score, 2–3 **cited** reasons.
5. Click a card → the **published cited.md page** with citations back to FEC filings. ← the Senso win.

## Core website elements (one screen + the artifact)

1. **Ask box** — single NL input (the UX thesis).
2. **Live agent activity stream** — makes it look autonomous on camera.
3. **Ranked prospect cards** — name, score, transparent **cited** reasons.
4. **The published cited.md page** — the climax; show human view + machine-readable markdown/JSON.
5. **Footer tool strip** — ClickHouse · Nimble · Senso, each doing distinct work.

Use the `frontend-design` skill so it doesn't look like generic AI boilerplate.

## Demo (RECORDED 3-min video — the submission)

Only finalists present live (5 PM); the video is what gets you there. Beat sheet:
- 0:00–0:15 Problem: "Nonprofits guess who to ask. We read who's already given — from 20M real public records."
- 0:15–0:35 Type the ask on camera.
- 0:35–2:05 Watch it run autonomously: parse → ClickHouse (show latency) → agent decides → Nimble enriches → scores.
- 2:05–2:35 Land on the published cited.md page with real citations. **The money shot — rehearse the landing.**
- 2:35–3:00 Architecture + 3-tool recap.

Pre-test the chosen ask 5+ times; keep a cached fallback; never demo an unrehearsed live call.

## Top risks
1. Senso publish only ingests (kills $3k track) → de-risk with a hardcoded page FIRST.
2. FEC bulk load too slow → load a state+year-trimmed subset.
3. Live demo flakes → it's recorded; use cached fallback.
4. Autonomy reads as scripted → ship live NL-parse + narrate one real agent decision.
5. Privacy/legal optics → "cited public-record research," never "dossier."
