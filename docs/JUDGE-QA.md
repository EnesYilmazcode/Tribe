# JUDGE Q&A PREP — Tribe

> Anticipated questions + strong, **honest** answers. Judges reward candor over hype.
> Read the §104.15 answer and the sponsor answer until you can say them cold.

## 30-second pitch (say this first if asked "what is it")
Nonprofits waste weeks guessing who to ask for money, and the tools that help cost $4–5k/year. Tribe flips it: you type a plain-language ask, and an autonomous agent reads **2.8 million real public FEC giving records** to find the people who *already fund your cause* — ranked by cause-affinity, enriched from the live web, and **cited back to the public record**. The whole run streams live, and it even runs continuous campaigns that auto-add new matching donors with no human in the loop.

---

## ⭐ THE MOST IMPORTANT ANSWER — "If FEC filings are public, why is this even an issue?"
**Short answer:** The *data* is public; what's regulated is *how you use it*. FEC rule **11 CFR §104.15** ("sale or use") says you can't use the contributor names/addresses from FEC reports **to solicit contributions or for commercial purposes** — and the FEC has said that covers charitable solicitation too (e.g. Rep. Ro Khanna was fined ~$16k in 2021). So a tool that says "here's a name + address, go ask them for money" is exactly the prohibited use.

**How Tribe stays on the right side of it:**
- We present **research on public giving behavior**, not a solicitation contact list — every claim links back to the public FEC source so a fundraiser can *understand* who supports their cause.
- We don't repackage the FEC's name+address as a "go solicit this person" list.
- The outreach drafts are **human-reviewed before anything is sent**, and contact channels would come from *separate public/professional sources* (e.g. a foundation's website), not from the FEC record.
- For the demo, the contact emails shown are **illustrative examples**, not scraped personal data.

**One-liner:** *"The records are public — we just have to use them as research, not as a mailing list. That's the line §104.15 draws, and we stay on the research side."*

---

## SPONSOR TOOLS — "How did you use the sponsors?"
We used **two** sponsor tools, both load-bearing (not bolted on):

- **ClickHouse** — the engine. We loaded **2.8M real FEC individual contributions** (597k donors, 5 states, all causes) plus committee + cause-tag tables. Every query joins contributions → committees → cause tags and aggregates per donor in **milliseconds** — that real-time speed over millions of rows is exactly what ClickHouse is for, and it's why the demo feels instant.
- **Nimble** — the "acts on the open web" layer. For each top donor we fire a **Nimble web Search** on their name + employer, then distill the results (role, bio, board seats, philanthropy) into a clean profile. That's the live, real-world data the agent acts on.

**"Why only two — doesn't the rubric reward 3+?"** Honest answer: yes, and it was a deliberate call. We chose **two tools used deeply over three used shallowly**. A half-wired third integration would have hurt the demo and the autonomy story (both also 20%). ClickHouse and Nimble each do distinct, necessary work; nothing is there for show.

---

## TECHNICAL — "How did you actually build it?"
Pipeline: **NL ask → parse → query → enrich → score → cited cards → (auto-match).**

- **NL parse:** Gemini (`gemini-flash-latest`) turns the free-text ask into structured params `{cause, geo, min_amount}`, with a deterministic synonym/adjacency fallback if the API is down. This is the autonomy "type any sentence" moment.
- **Query:** Python over ClickHouse. A **dedup-safe query** (`query_clean.py`) counts `DISTINCT sub_id` and filters via `cmte_id IN (matching committees)` so duplicate rows / multi-cause committees can't inflate totals — we caught and fixed a 4× inflation bug this way (a megadonor's $2M → the correct $500k).
- **Scoring:** 0–100 = log-scaled total giving + recency + consistency (repeat gifts).
- **Enrichment:** Nimble search → Gemini extraction → cached in a ClickHouse `donor_enrichments` table (ReplacingMergeTree) so the UI shows bios instantly with zero live latency.
- **Streaming:** a FastAPI `/run` **Server-Sent Events** endpoint pushes each agent step to the React frontend live (the activity stream).
- **Frontend:** React + Vite + TypeScript + Tailwind. Cited prospect cards with `fec.gov ↗` source pills.
- **Continuous auto-match agent:** describe a campaign once → it parses, queries, and **auto-adds** matching donors to the pipeline each cycle, only surfacing *new* ones.

**"Is it RAG?"** No — and that's intentional. We don't retrieve documents to feed the model. The LLM does **classification / query-expansion** (sentence → known cause tags), then a normal database query runs. The model shapes the *question*; the **database** produces the answer, so every result is grounded in a real FEC row — no hallucinated donors.

**"Why ClickHouse over Postgres?"** Columnar + built for real-time aggregation over millions of rows; sub-40ms group-bys that Postgres would struggle with at this scale.

**"What's real vs. canned in the demo?"** The data and pipeline are **real** (2.8M real FEC rows, real ClickHouse queries, real Nimble enrichment). For the recorded demo we replay a **captured real run** (`?demo=1`) so it's reliable on camera — we can also run it live. The contact emails on cards are **illustrative examples** (we don't hold personal emails).

---

## DATA & SCRAPING — "Other than FEC, what do you scrape?"
- **We don't mass-scrape the web.** The donor universe comes from the **official FEC API** (real public records — the same ones our citations point to). No scraping for the core data.
- **Nimble does targeted web *search*** (not crawling) on a specific person — pulling from public sources like LinkedIn, an employer/foundation site, or news, only to enrich a donor we already found.
- We also pulled **ProPublica nonprofit data** (org/EIN/cause) as a supporting source.
- **Data quality is honest:** cause tagging is keyword-based on committee names (we fixed false positives like "Walgreen"→environment), and we demo on clean causes (environment) rather than the party-proxy ones. We're upfront that this is a hackathon dataset (5 states, 2.8M rows), not the full FEC.

---

## AUTONOMY — "How autonomous is it really?" (20% of the score)
- **No forms.** You type a sentence; the agent decides the causes, runs the query, picks which candidates to deep-enrich, scores them, and streams its reasoning — no manual steps.
- **The continuous auto-match agent** is the strongest version: a campaign described once keeps **auto-adding new high-affinity donors as data arrives, with no human in the loop** — that's "acts on real-time data without manual intervention," verbatim the criterion.
- Honest boundary: outreach is **drafted, not auto-sent** — a human reviews (also the right call legally).

---

## IDEA / AUDIENCE / MARKET
**"How did you think of this?"** Wealth-screening tools answer "*can* this person give?" But the strongest signal is "*do* they already give to this cause?" — and that data is public: FEC is the only bulk, **cause-tagged** record of what people put money behind. Political giving is a strong proxy for charitable cause-affinity.

**"Who's the target audience?"** Small-to-mid nonprofits, advocacy groups, and political/issue campaigns — the ones priced out of iWave/DonorSearch ($4–5k/yr) who currently guess or cold-prospect.

**"What makes you different from DonorSearch/iWave?"** (1) Plain-language agent interface vs. credit-gated dashboards. (2) **Cited, auditable reasoning** — every score links to its public source; incumbents are black boxes. (3) Cause-affinity from real giving vs. opaque wealth scores. (4) Live web enrichment vs. stale static profiles.

---

## FUTURE / MONETIZATION
**"If you had another month, what would you build?"**
1. **Richer taxonomy** — a dedicated `animal_welfare` cause and a proper cause ontology (the "dog shelter" gap), plus embeddings/semantic matching on committee names.
2. **Full data** — all 50 states + multiple cycles; nightly FEC refresh.
3. **Productionize the continuous auto-match agent** — campaigns that run on a schedule and notify you of new matches.
4. **Warm-path / relationship graph** — surface donors connected to your board or existing supporters (huge for fundraisers).
5. **CRM integrations** — push prospects into Salesforce NPSP, Bloomerang, etc.
6. **Compliant contact enrichment** — surface a *public professional* channel (org/LinkedIn) within the §104.15 guardrails.

**"How would you monetize?"** SaaS, undercutting incumbents: a free tier for tiny orgs, then per-seat plans (~$50–150/mo) with usage-based enrichment credits. The wedge is accessibility — bringing $4–5k/yr capability to orgs that can't afford it.

**"How would you reach your community?"** Nonprofit/fundraiser communities (AFP chapters, Nonprofit subreddits, fundraising Slack/Discords), partnerships with fiscal sponsors and nonprofit accelerators, and content/SEO around "find donors for X cause."

---

## SKEPTICAL / GOTCHA QUESTIONS (have these ready)
- **"Political giving ≠ charitable giving."** True, it's a proxy, not a guarantee — studies show partial substitution. That's why we present it as *research with cited evidence* a fundraiser interprets, and rank by affinity rather than claiming certainty.
- **"Aren't these just rich people / a wealth screen in disguise?"** No — we rank by *cause-specific* giving behavior, not net worth. Someone who gave $1k to clean water repeatedly ranks for a water campaign; a billionaire who never gave to your cause doesn't.
- **"What if the AI hallucinates a donor?"** It can't — the LLM only shapes the query; the donors come straight from FEC rows in ClickHouse, each with a citation link.
- **"Is the contact info real?"** For the demo it's illustrative. Real personal contact info isn't in public donation data and we wouldn't fabricate it in production — outreach would go through public/professional channels, human-reviewed.
- **"Privacy?"** Everything shown is already public record; we add transparency (citations), not new private data.

---

## DEEP-DIVE FUTURE IDEAS (brainstorm — pick a couple to mention)
- **Lapsed-donor reactivation** — flag donors who gave to your cause before and went quiet.
- **Recurring-gift prediction** — model who's likely to become a sustaining donor.
- **Multi-source affinity** — blend FEC + nonprofit 990 board/officer data + ProPublica for a fuller picture.
- **Affinity over time** — show a donor's cause trajectory (are they leaning more into climate lately?).
- **Campaign portfolio view** — one dashboard of all your campaigns auto-filling in parallel.
- **Outreach A/B testing** — generate + test email variants, learn what converts per donor type.
- **Board/affiliation graph** — "who sits on the board of a cause nonprofit" as a gold-tier signal.
- **Agentic outreach pipeline** — draft → human approve → send → track reply → auto-follow-up.

---

## QUICK ONE-LINERS (memorize)
- *"We read who already gives, instead of guessing who might."*
- *"Every number links to a real fec.gov record — no black-box scores."*
- *"The AI widens the question; the database produces the answer."*
- *"Public records, used as research — not a mailing list."*
- *"Two sponsor tools, used deeply: ClickHouse finds them in milliseconds, Nimble enriches them live."*
