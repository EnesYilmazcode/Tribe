# TEAM-SPLIT: who does what, and the contract between us

> Two people, ~4.5 hours. The goal: never block each other. The trick: agree ONE data contract up front, mock it, build both sides against the mock, integrate once.

## Why not "one fills the DB, one extracts it"

That seam splits in the wrong place. The **agent loop** and the **Senso publish** are the parts that win, and they'd fall in the crack. You'd also be unable to test either half until the end. Instead, split by **track ownership**, joined by the `prospect_record` JSON contract below.

## The split (DECIDED)

| | **Friend: Scraper / Data** (`agent/`) | **Enes: Platform** (`web/` + serving) |
|---|---|---|
| Owns tracks | ClickHouse, Nimble | **Senso ($3k)**, Presentation |
| Does | Fill the database: load FEC into ClickHouse and cause-tag it. Build the web enrichment (Nimble) as a callable function. Goal: a queryable, cause-tagged, enrichable donor store. | Read the database and build the product: NL parse, then query, then score/rank, then frontend (ask box + live activity stream + cited cards), then publish via Senso. **FIRST: de-risk Senso** (publish one hardcoded cited.md page end-to-end). |
| Exposes | `query(cause, geo, min_amount) → [candidate]` (over ClickHouse) and `enrich(candidate) → enrichment` (Nimble) | The platform that calls those + scores + renders + publishes |
| Builds against | Real FEC data | The **mock** `sample_prospects.json`, then the real `query()`/`enrich()` |

Note: NL-parse, scoring, orchestration, and the Senso publish live on the **platform** side (Enes). That's the "gets information from the database and does something with it" half. The friend's job is to make the database rich and fast to query, plus the live web enrichment.

## The contract: `prospect_record`

Agree this in the first 15 min. Both sides code to it. Engine produces it, Surface renders and publishes it.

```jsonc
{
  "name": "Jane Donor",
  "affinity_score": 87,               // 0-100
  "cause_tags": ["environment", "water"],
  "geo": "WA",
  "cited_reasons": [
    { "text": "Gave $12,000 across 3 environmental committees, 2022-2024",
      "source_url": "https://www.fec.gov/data/receipts/?committee_id=..." }
  ],
  "enrichment": {                     // from Nimble; may be null if not enriched
    "current_role": "...",
    "notes": "...",
    "source_url": "..."
  }
}
// NOTE: no suggested_ask / outreach_approach in the PUBLISHED record (solicitation framing — see STRATEGY.md legal reframe).
```

## Choreography

1. **First 15 min, together:** lock the `prospect_record` shape + pick the ONE demo ask you'll record. Commit a `sample_prospects.json` mock and push.
2. **Split, fully parallel.** Neither waits. B uses the mock, A makes it real.
3. **~3:00 integration:** swap B's mock for A's live `ask()`. One-line change because you both coded to the contract.
4. **3:45 demo recording:** B owns it (owns Presentation), with A on standby for the cached-fallback run.

**If a 3rd person joins:** split Engine into "Data" (load FEC into ClickHouse and tag it) and "Agent" (parse, query, enrich, score). Contract unchanged.

## Reminder
Commit and push frequently and `git pull --rebase` before pushing. Our two Claude Code agents only stay in sync through git. See `../CLAUDE.md`.
