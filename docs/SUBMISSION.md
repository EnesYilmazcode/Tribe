# SUBMISSION: paste-ready Devpost copy + checklist

> Everything needed to submit by 4:15 PM. Copy the sections straight into Devpost.
> Sponsor tools claimed: ClickHouse + Nimble (both load-bearing). Repo verified clean (no committed secrets).

---

## Project name
**Tribe**

## Tagline (one line)
An autonomous agent that finds your best donors from real public giving data. Type a sentence, get cited, ranked prospects.

## Elevator pitch (the "what it does" box)
Nonprofits waste weeks guessing who to ask for money. Tribe flips it: you type a plain-language ask like *"major environment donors in California who gave $1,000+"* and an autonomous agent reads **real public FEC giving records** to find the people who already fund your cause. It parses your request, queries **2.8 million real contributions** in ClickHouse in milliseconds, ranks donors by cause-affinity, enriches the top names from the live web with Nimble, and returns ranked prospect cards, every claim **cited back to the public FEC source**. The whole agent run streams live so you watch it reason. It even runs continuous **campaigns**: describe one once, and the agent auto-adds new matching donors to your pipeline with zero manual work.

---

## Inspiration
Fundraising tools like iWave and DonorSearch cost $4–5k/year and lean on wealth screening, *can* this person give, not *do* they care. But the strongest signal of who'll fund your cause is who **already funds that cause**. That data exists, publicly and for free: the FEC publishes every itemized political contribution in the US. We realized political giving is the only bulk, cause-tagged record of what people put their money behind, and that a small nonprofit should be able to query it in plain English instead of paying for a gated dashboard.

## What it does
1. **You describe who you're looking for** in natural language.
2. The agent **parses** it into a cause + geography + giving level (Gemini, with a deterministic fallback).
3. It **queries real FEC data in ClickHouse** (2.8M contributions, 597k donors, all causes, 5 states) and ranks by cause-affinity + recency + capacity (0–100).
4. It **enriches the top candidates from the live web** with Nimble (current role, bio, board seats).
5. It returns **ranked, cited prospect cards**, each donor's giving total, history, and a link to their public FEC record.
6. **Continuous auto-match:** define a campaign once ("protect oceans and marine wildlife") and a background agent keeps auto-adding newly-matched donors to its pipeline, acting on data with no human in the loop.

Every run streams to the UI as Server-Sent Events, so judges *watch* the agent parse, query, enrich, and score in real time.

## How we built it
- **ClickHouse Cloud** is the engine. We loaded **2.8M real FEC individual contributions** (official FEC API), tagged committees to ~20 causes, and query it in milliseconds. A dedup-safe query layer (`query_clean.py`) guarantees honest donor totals even with messy source rows.
- **Nimble** does live web enrichment. For each top donor we run a Nimble web search and distill it (employer, role, philanthropy, board seats) into a clean profile, cached for instant display.
- **Gemini** (`gemini-flash-latest`) turns the free-text ask into structured query params, the autonomy "type any sentence" magic.
- **FastAPI + Server-Sent Events** is a `/run` endpoint that streams each agent step to the UI live.
- **React + Vite + TypeScript + Tailwind** make up a "donor-intelligence terminal": ask box, live activity stream, cited prospect cards with `fec.gov ↗` source pills.
- **Data source: the official FEC API**, real public records, the same ones our citations point to. No scraping, no synthetic data.

## Sponsor tools used
- **ClickHouse** does real-time analytical queries over 2.8M+ FEC rows, the core of the product.
- **Nimble** does live, real-time web enrichment of donor candidates, the "acts on the open web" autonomy step.

## Challenges we ran into
- **Real data is messy.** We hit synthetic placeholder data, then a 4× donor-total inflation from duplicate committee rows + multi-cause tags. We fixed it with a dedup-safe query (verified: a megadonor's $2M inflated total dropped to the correct $500k).
- **Cause tagging false positives.** Keyword matching tagged "Walgreen" and "Marine Engineers' Union" as environment/veterans. We hardened it and demo only on clean causes.
- **Coordinating a multi-agent team:** three Claude Code instances + a teammate on one repo. We used a shared `STATUS.md` and strict git rebasing to claim lanes and never collide.
- **API rate limits.** Gemini's free tier 429'd under load, so we moved to Tier 1.

## Accomplishments we're proud of
- It runs **end-to-end on 2.8M real, cited public records**, not a mockup. Recognizable donors (e.g. climate megadonor Tom Steyer) surface with verifiable FEC links.
- **Honest numbers.** We caught and fixed the inflation so every dollar figure matches the public record.
- The **continuous auto-match agent** is real autonomy: campaigns that fill themselves.

## What we learned
- Political giving is a surprisingly strong proxy for charitable cause-affinity, and the framing matters: this is **research on public giving behavior**, not a solicitation list (FEC's 11 CFR §104.15 restricts using contributor data to *solicit*, and we cite the public record and never repackage it as a contact-to-ask list).
- For "sentence to known categories," an LLM classifier beats embeddings/RAG. It's cheaper, faster, with no vector infra.

## What's next
- Continuous auto-match agent at full scale (every 5–30 min, more campaigns).
- All 50 states + multi-cycle FEC data.
- A dedicated `animal_welfare` cause and richer taxonomy.
- Contact enrichment within the §104.15 legal guardrails.

## Built with
`clickhouse` · `nimble` · `python` · `fastapi` · `server-sent-events` · `gemini` · `react` · `typescript` · `vite` · `tailwindcss` · `fec-api`

---

## 4:15 SUBMISSION CHECKLIST (do in order)
- [ ] **Record** the 3-min demo on `?demo=1` (DEMO-SCRIPT.md). *Enes, #1 priority*
- [ ] **Upload the video** to YouTube/Vimeo (unlisted OK). Wait for processing. Copy the **link**.
- [ ] **Make the GitHub repo public.** (Verified: no secrets committed, only `.env.example`.)
- [ ] Final `git pull --rebase` + push so the public repo is current.
- [ ] **Devpost form:** paste the sections above (tagline, what it does, how built, challenges, etc.), add the **video link**, list **Built With** + sponsor tools (ClickHouse, Nimble), add the repo URL.
- [ ] **Submit by 4:15** (treat as the hard deadline, late may be cut off).

## Rehearsed answer if a judge asks about legality / privacy
> "It's all public record. The FEC publishes every itemized contribution. We present it as **research on public giving behavior**, with every claim linked back to its public FEC source, so a fundraiser can understand who already supports their cause. We deliberately don't repackage it as a 'go solicit this person' contact list. That's the line 11 CFR §104.15 draws, and we stay on the research side of it."
