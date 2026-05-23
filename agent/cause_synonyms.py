"""
Semantic layer for query-time NL -> cause mapping.

The committee-name keyword matcher (cause_tag.CAUSE_KEYWORDS) is tuned for tagging
*committee names*. This module adds the words a *user* actually types when describing
a cause ("save the whales", "melting ice caps", "Dreamers") and a cause-adjacency
graph so related donor universes can be pulled together.

Used by the platform's NL parser as the deterministic fallback when no LLM is
available, and by expansion regardless. See docs/QUERYING.md.

    from cause_synonyms import map_text_to_causes, expand_causes

    map_text_to_causes("help save the whales and clean up the ocean")
    # -> ["environment"]

    expand_causes(["environment"])
    # -> ["environment", "energy", "agriculture", "infrastructure"]
"""

from cause_tag import CAUSE_KEYWORDS

# Extra phrases a USER types (beyond committee-name keywords). Tag must be one of
# the 20 in CAUSE_TAGS.md. Keep these as substrings, lowercase.
USER_SYNONYMS: dict[str, list[str]] = {
    # These cover NL terms a user might type that don't appear in CAUSE_KEYWORDS
    # (which was tightened for committee-name matching to reduce false positives).
    # USER_SYNONYMS is only used in map_text_to_causes() — never for committee tagging.
    "environment":  ["green", "go green", "whale", "lizard", "animal", "wildlife", "species",
                     "habitat", "marine", "fish", "bird", "forest", "tree", "river", "lake",
                     "watershed", "ice", "snow", "glacier", "arctic", "polar", "carbon",
                     "emission", "global warming", "endangered", "national park", "land", "reef"],
    "education":    ["kid", "child", "youth", "scholarship", "tuition", "tutor", "stem",
                     "early childhood", "pre-k", "k-12", "library"],
    "healthcare":   ["wellness", "vaccine", "alzheimer", "diabetes", "heart disease",
                     "addiction", "opioid", "hospice", "caregiver", "public health"],
    "housing":      ["rent", "eviction", "mortgage", "unhoused", "supportive housing",
                     "section 8", "zoning", "affordable"],
    "immigration":  ["migrant", "dreamer", "citizenship", "deportation", "undocumented"],
    "criminal_justice": ["reform", "criminal reform", "justice reform", "police reform",
                         "police", "jail", "sentencing", "bail", "death penalty",
                         "wrongful conviction", "reentry"],
    "civil_rights": ["equity", "race", "racial", "gender", "ballot", "trans", "gay",
                     "marriage equality", "voter", "human rights", "freedom", "women"],
    "labor":        ["labor", "workers", "worker rights", "workers rights", "trade union",
                     "job", "minimum wage", "strike", "collective bargaining", "gig worker",
                     "pension", "overtime", "unions"],
    "veterans":     ["marine", "troop", "vet ", "gi bill", "ptsd", "service member",
                     "wounded warrior"],
    "gun_control":  ["gun", "shooting", "ammunition", "mass shooting", "background check",
                     "assault weapon"],
    "reproductive_rights": ["roe", "contraception", "birth control", "ivf", "maternal"],
    "agriculture":  ["ranch", "harvest", "dairy", "organic", "soil", "fishery", "food"],
    "small_business": ["sme", "main street", "mom and pop", "franchise"],
    "technology":   ["tech", "ai", "software", "data", "privacy", "robot", "semiconductor",
                     "crypto policy"],
    "finance":      ["bank", "banking", "crypto", "stock", "wall st", "fintech",
                     "mortgage rate", "credit"],
    "energy":       ["drilling", "grid", "power plant", "renewable energy", "fracking", "ev"],
    "foreign_policy": ["international", "global", "gaza", "china", "russia", "war", "treaty",
                       "sanction", "diplomacy", "aid", "trade"],
    "social_welfare": ["social", "social issues", "community", "hunger", "poverty", "homeless",
                       "food", "soup kitchen", "low income", "disaster relief", "orphan"],
    "infrastructure": ["road", "bridge", "transit", "train", "rail", "internet access",
                       "broadband"],
    "arts_culture": ["culture", "heritage", "museum", "theater", "orchestra", "artist",
                     "gallery", "humanities", "dance"],
}

# Related causes — a donor to X is more likely to also give to these. Shallow on purpose.
ADJACENCY: dict[str, list[str]] = {
    "environment":        ["energy", "agriculture", "infrastructure"],
    "energy":             ["environment", "infrastructure"],
    "agriculture":        ["environment", "social_welfare"],
    "infrastructure":     ["environment", "housing"],
    "healthcare":         ["reproductive_rights", "social_welfare"],
    "reproductive_rights":["healthcare", "civil_rights"],
    "civil_rights":       ["reproductive_rights", "immigration", "criminal_justice"],
    "immigration":        ["civil_rights", "social_welfare"],
    "criminal_justice":   ["civil_rights", "gun_control"],
    "gun_control":        ["criminal_justice", "civil_rights"],
    "labor":              ["social_welfare", "small_business"],
    "small_business":     ["finance", "technology"],
    "technology":         ["finance", "small_business"],
    "finance":            ["small_business", "technology"],
    "education":          ["social_welfare", "arts_culture"],
    "arts_culture":       ["education"],
    "housing":            ["social_welfare", "infrastructure"],
    "social_welfare":     ["housing", "healthcare", "education"],
    "veterans":           ["healthcare", "foreign_policy"],
    "foreign_policy":     ["veterans"],
}


def map_text_to_causes(text: str, max_causes: int = 3) -> list[str]:
    """Deterministic NL -> cause tags. Scores each tag by phrase matches across both
    the user-synonym list and the committee keyword list; returns top tags."""
    low = f" {text.lower()} "
    scores: dict[str, int] = {}
    for tag in CAUSE_KEYWORDS:
        phrases = CAUSE_KEYWORDS.get(tag, []) + USER_SYNONYMS.get(tag, [])
        hits = sum(1 for p in phrases if p in low)
        if hits:
            scores[tag] = hits
    ranked = sorted(scores, key=lambda t: scores[t], reverse=True)
    return ranked[:max_causes]


def expand_causes(causes: list[str], depth: int = 1) -> list[str]:
    """Add adjacent causes (related donor universes). Order-preserving, deduped."""
    out = list(causes)
    frontier = list(causes)
    for _ in range(depth):
        nxt = []
        for c in frontier:
            for adj in ADJACENCY.get(c, []):
                if adj not in out:
                    out.append(adj)
                    nxt.append(adj)
        frontier = nxt
    return out


if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "help save the whales and protect the ocean in oregon"
    causes = map_text_to_causes(q)
    print(f"ask:      {q}")
    print(f"causes:   {causes}")
    print(f"expanded: {expand_causes(causes)}")
