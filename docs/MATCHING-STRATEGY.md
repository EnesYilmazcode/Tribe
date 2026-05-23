# MATCHING-STRATEGY — how we match donors by meaning

> Decision from research on 2026-05-23. How we turn a natural-language ask into the right donors, beyond exact keyword matching.

## Decision
1. **Build LLM query-expansion** (Gemini). One call per ask maps the fundraiser's sentence → our real cause tags + related tags + committee-name keyword hints, then we run the existing `query(causes=[...])`. Delivers niche→broad, synonyms, and related-keyword exploration in ~1hr, no schema change.
2. **Add a hand-built cause-affinity map** (below) as a deterministic fallback + score booster when Gemini is slow/rate-limited/wrong.
3. **Skip embeddings / ClickHouse vector search** for the hackathon. Our signal is the cause *tags*, not committee *names* (short/opaque). Embeddings would need a schema migration + re-embedding every committee for recall we already get from Gemini. Right post-hackathon upgrade, wrong use of hours now.

## This is NOT RAG (demo talking point)
RAG feeds documents *into* the AI so it writes the answer. We do the reverse: the AI widens the *search query*, the **database** produces the donor list. Every result stays traceable to a real FEC row — the AI never invents a donor. That's the trust story for judges.

## Owners
- **Backend (Enes / this side):** build the expansion layer — `expand_ask(ask)` (Gemini → `{causes, keywords}`, validated against the real 20 tags) → call friend's `query(causes=...)`. Surface the expansion reasoning in the activity stream.
- **Data (friend / `agent/`):** fix the keyword false-positives in `cause_tag.py` (see below). Optionally fold the keyword hints into tagging.

## Cause-affinity map (paste-ready)
Weight: 1.0 = same theme / strong co-giving, 0.6 = adjacent/bridge, 0.3 = weak/ideological. For a niche ask, expand to neighbors ≥ threshold and discount their affinity_score contribution by the weight. Never let an expanded neighbor outrank a direct match.

```python
CAUSE_AFFINITY: dict[str, dict[str, float]] = {
    "environment": {"energy": 1.0, "agriculture": 0.6, "infrastructure": 0.6, "social_welfare": 0.3, "civil_rights": 0.3},
    "energy": {"environment": 1.0, "infrastructure": 0.6, "agriculture": 0.6, "finance": 0.3, "technology": 0.3},
    "agriculture": {"environment": 0.6, "energy": 0.6, "infrastructure": 0.6, "social_welfare": 0.6, "small_business": 0.3},
    "infrastructure": {"energy": 0.6, "environment": 0.6, "technology": 0.6, "agriculture": 0.6, "small_business": 0.3},
    "education": {"social_welfare": 1.0, "housing": 0.6, "healthcare": 0.6, "civil_rights": 0.6, "arts_culture": 0.6},
    "healthcare": {"social_welfare": 1.0, "reproductive_rights": 0.6, "education": 0.6, "housing": 0.6, "veterans": 0.3},
    "housing": {"social_welfare": 1.0, "education": 0.6, "healthcare": 0.6, "criminal_justice": 0.6, "immigration": 0.3},
    "social_welfare": {"housing": 1.0, "healthcare": 1.0, "education": 1.0, "immigration": 0.6, "civil_rights": 0.6, "agriculture": 0.6, "arts_culture": 0.3},
    "civil_rights": {"reproductive_rights": 1.0, "criminal_justice": 1.0, "immigration": 1.0, "gun_control": 0.6, "labor": 0.6, "education": 0.6, "social_welfare": 0.6},
    "reproductive_rights": {"civil_rights": 1.0, "healthcare": 0.6, "gun_control": 0.6, "immigration": 0.3},
    "immigration": {"civil_rights": 1.0, "labor": 0.6, "social_welfare": 0.6, "foreign_policy": 0.6, "criminal_justice": 0.6},
    "criminal_justice": {"civil_rights": 1.0, "gun_control": 0.6, "housing": 0.6, "immigration": 0.6, "social_welfare": 0.3},
    "gun_control": {"civil_rights": 0.6, "criminal_justice": 0.6, "reproductive_rights": 0.6},
    "labor": {"small_business": 0.6, "civil_rights": 0.6, "immigration": 0.6, "social_welfare": 0.6, "finance": 0.3},
    "small_business": {"finance": 1.0, "technology": 0.6, "labor": 0.6, "agriculture": 0.3, "infrastructure": 0.3},
    "finance": {"small_business": 1.0, "technology": 0.6, "energy": 0.3, "labor": 0.3},
    "technology": {"finance": 0.6, "small_business": 0.6, "infrastructure": 0.6, "energy": 0.3, "education": 0.3},
    "veterans": {"foreign_policy": 1.0, "healthcare": 0.3, "social_welfare": 0.3},
    "foreign_policy": {"veterans": 1.0, "immigration": 0.6, "civil_rights": 0.3, "finance": 0.3},
    "arts_culture": {"education": 0.6, "social_welfare": 0.3, "civil_rights": 0.3},
}
```

## cause_tag.py fixes (for the friend)
Current matcher is naive substring (`kw in name_lower`), no word boundaries. High-impact false positives:

| Keyword | Wrong tag | Mis-tags | Fix |
|---|---|---|---|
| `"reform"` | criminal_justice | "Tax Reform", "Education Reform" | drop bare word; keep `"prison reform"`, `"police reform"`, `"sentencing reform"` |
| `"social"` | social_welfare | "Social Security", "Social Media" | drop bare word; use `"social services"`, `"human services"` |
| `"trade"` | labor + foreign_policy | "Trade Association", "Board of Trade" | drop from labor; foreign_policy keep `"free trade"` only |
| `"women"` | civil_rights | "Women in Tech", "Women for Trump" | narrow to `"women's rights"`, `"gender equality"` |
| `"green"` | environment | surname "Green", "Evergreen" | drop; rely on `"climate"`, `"conservation"`, `"clean energy"` |
| `"ai "` | technology | "Air Force", "Repair", "Chair" | drop; keep `"artificial intelligence"` |
| `"gun"` | gun_control | "Gunderson", "Gunn" | word-boundary; keep `"gun safety"`, `"firearm"`, `"nra"` |
| `"food"` | agriculture | collides with "food bank" (social_welfare) | agriculture use `"food policy"`; keep `"food bank"` in social_welfare |

Structural fix that kills most of these at once — word-boundary regex instead of substring:
```python
import re
CAUSE_PATTERNS = {tag: re.compile(r"\b(?:%s)\b" % "|".join(re.escape(k) for k in kws))
                  for tag, kws in CAUSE_KEYWORDS.items()}
# tag if CAUSE_PATTERNS[tag].search(name_lower)
```
Plus: prefer multi-word keywords ("gun safety" over "gun"), and a per-tag stop-list for known traps.

## Evidence the affinity idea holds
Giving clusters along value axes (Moral Foundations Theory): care/fairness donors skew to civil_rights/environment/immigration; loyalty/authority donors skew to veterans/gun_rights. Political-donation platforms profile donors exactly this way (environmental + LGBTQ + gun-violence-prevention co-occur). Caveat: ~44% of giving is local/personal-experience-driven, so keep affinity as a *score booster, not a hard filter*.
Sources: Nilsson et al. (Eur. J. Personality 2020), Thottam & Kalamas (J. Consumer Behaviour 2024).
