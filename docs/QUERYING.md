# QUERYING: how a natural-language ask becomes a ClickHouse query

> The platform (web/) turns a free-text ask into params for the friend's
> `query(causes=[...], geo=..., min_amount=...)`. This doc is the contract for
> that mapping and the semantic-similarity strategy. See `agent/CAUSE_TAGS.md`
> for the 20-tag vocabulary and `agent/cause_synonyms.py` for the data.

## The query surface (what the backend gives us)
`query()` takes:
- `causes`: one or more of the **20 fixed cause tags** (environment, healthcare, labor, etc).
- `geo`: a 2-letter state code, or none.
- `min_amount`: minimum single-gift dollars.

So the platform's entire job at parse time is to go from free text to `{causes[], geo, min_amount}`.

## Is this RAG? No, it's classification into a fixed taxonomy.
RAG means retrieve documents by embedding similarity, then generate. We don't need it:
- The hard semantic step (committee name to cause) is **already precomputed** into
  `committee_causes`. At query time there are no documents to retrieve.
- The only semantic step left is to map the user's words to 1 to 3 of 20 known tags.
  That's a classification problem over a tiny label set, which an LLM does more
  accurately than nearest-neighbour over embeddings, and with zero vector-DB infra.

**Verdict:** LLM classification (primary) plus a deterministic synonym/adjacency map
(fallback and expansion). Embeddings/RAG would only help if we were matching against
thousands of free-form committee names live, and we're not.

## Stage 1: NL to tags (the semantic step)
**Primary: one LLM call.** Prompt it with the 20 tags and their descriptions and ask
for strict JSON: `{ "causes": [...], "geo": "WA"|null, "min_amount": 1000 }`.
The LLM natively handles the similarity you described:
- "save the whales" / "lizards" / "animal habitat" map to **environment**
- "melting ice caps" / "snow pack" / "carbon" map to **environment**
- "help our troops" maps to veterans, "Roe" to reproductive_rights, "Dreamers" to immigration

This is also the autonomy money-shot. The judge types a sentence with none of our
tag words in it, and the agent still picks the right causes.

**Fallback (no LLM key): `map_text_to_causes(text)`** in `agent/cause_synonyms.py`, a
deterministic phrase-to-tag matching that covers the common synonyms.

## Stage 2: expansion (the "lizards to animals in general" intuition)
Someone who gives to lizards probably gives to animals/environment broadly. We model
this two ways:
1. **Within a tag:** the tag itself is the broad bucket. A lizard-conservation
   committee is tagged `environment`, so querying `environment` already returns the
   broad animal/wildlife/ocean donor universe.
2. **Across tags (adjacency):** `expand_causes()` adds related causes so we don't miss
   adjacent donors. For example `environment` adds `{energy, agriculture, infrastructure}`,
   and `civil_rights` adds `{reproductive_rights, immigration, criminal_justice}`. Pass the
   expanded list to `query(causes=[...])`, and the backend already **boosts donors who
   match multiple causes** (overlap means stronger affinity), which is exactly the
   "gives to X is more likely to give to related Y" signal.

Keep expansion shallow (depth 1) and optional, since over-expanding dilutes relevance.

## Known gap to flag (friend's side, optional)
Tagging is keyword-on-committee-name. A committee like "Desert Reptile Alliance" won't
match the `environment` keywords and stays untagged, so its donors are invisible. Improving
tagging recall (LLM-classify committee names, or embed them) is the only place
embeddings would actually help. Fine to skip for the demo, just note it as future work.

## Enrichment shape: reconcile at integration
Friend's `nimble_client.enrich()` returns
`{current_role, employer, bio_snippet, philanthropy, news, source_urls[]}`.
The UI's `prospect_record.enrichment` currently expects `{current_role, notes, source_url}`.
At integration, the orchestrator should map enrich() to the UI shape (or we widen the UI).
Tracked so it isn't forgotten.
