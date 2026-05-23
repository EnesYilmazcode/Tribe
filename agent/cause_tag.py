"""
Maps FEC committee names → cause tags using keyword matching.
Covers ~20 causes; hand-curated for the top committee name patterns.

Matching uses word-boundary regex (\b...\b) to avoid substring false positives
(e.g. "labor" matching "laboratory", "tech" matching "biotech").
"""

import re

CAUSE_KEYWORDS: dict[str, list[str]] = {
    "environment":  ["environment", "climate", "clean energy", "clean water", "conservation",
                     "sierra club", "renewable", "wildlife", "ocean", "nature",
                     "earth", "wilderness", "planet", "sustainability"],
    # "green" removed — too many surname false positives (Al Green, Gene Green, etc.)
    "education":    ["education", "school", "teacher", "student", "university", "college",
                     "literacy", "learning", "academic", "classroom"],
    "healthcare":   ["health", "medical", "hospital", "cancer", "mental health", "disease",
                     "pharma", "nurse", "doctor", "clinic", "medicare", "medicaid"],
    "housing":      ["housing", "affordable housing", "homeless", "tenant", "shelter", "rental",
                     "community development"],
    # "affordable" removed alone — matched "Affordable Care Act" as housing
    "immigration":  ["immigration", "immigrant", "refugee", "asylum", "daca", "border"],
    "criminal_justice": ["criminal justice", "prison", "policing", "incarceration", "justice reform",
                         "public safety", "law enforcement",
                         "prison reform", "police reform", "bail reform", "sentencing reform"],
    # bare "reform" removed — matched Tax Reform, Education Reform, Healthcare Reform, Reform Party
    "civil_rights": ["civil rights", "racial equity", "gender equity", "equity justice",
                     "equality", "discrimination", "naacp",
                     "voting rights", "disability", "lgbtq", "women's rights"],
    # bare "equity" removed — matched Private Equity funds heavily
    # "women" narrowed to "women's rights" to avoid "Women for Trump"-style mismatches
    "labor":        ["labor union", "trade union", "building trades", "workers union",
                     "union", "worker", "wage", "afl", "seiu", "teamster"],
    # bare "labor" removed — matched "laboratory"; bare "trade" removed — matched trade associations
    "veterans":     ["veteran", "military", "armed forces", "soldier", "navy", "army",
                     "marine corps", "marines", "air force"],
    # bare "marine" removed — matched "Marine Biological Lab", "Marine Manufacturers", "Marine Engineers"
    "gun_control":  ["gun safety", "gun violence", "gun control", "firearm", "nra",
                     "second amendment"],
    # bare "gun" removed — word boundary handles "Gunn" but "gun" alone is fine with \b
    "reproductive_rights": ["reproductive", "abortion", "planned parenthood", "naral",
                            "pro-choice", "pro-life", "family planning"],
    "agriculture":  ["agriculture", "farm", "rural", "farmer", "crop", "livestock",
                     "food policy", "food bank"],
    # "food" alone removed from agriculture — "food bank" belongs to social_welfare; "food policy" is agriculture
    "small_business": ["small business", "entrepreneur", "startup", "chamber of commerce"],
    "technology":   ["technology", "innovation", "artificial intelligence",
                     "digital", "internet", "cybersecurity"],
    # bare "tech" removed (matched "biotech"); "ai " removed (fragile trailing space)
    "finance":      ["banking", "finance", "financial", "wall street", "securities",
                     "investment", "credit union"],
    # "credit" narrowed to "credit union" — bare "credit" was too broad
    "energy":       ["energy", "oil", "gas", "coal", "pipeline", "utility", "electric",
                     "nuclear", "solar", "wind"],
    "foreign_policy": ["foreign policy", "foreign affairs", "international relations",
                       "israel", "ukraine", "nato", "middle east", "free trade",
                       "global policy"],
    # "international" removed alone — matched every international union (Teamsters, IBEW, etc.)
    # "global" narrowed; "trade" narrowed to "free trade" only
    "social_welfare": ["social services", "human services", "poverty", "food bank", "hunger",
                       "welfare", "community", "charity", "nonprofit"],
    # bare "social" removed — "Social Security" was the #1 false positive
    "infrastructure": ["infrastructure", "transportation", "transit", "highway", "broadband",
                       "water system"],
    "arts_culture": ["arts", "performing arts", "arts and culture", "museum", "music",
                     "film", "theater"],
    # bare "culture" and "heritage" removed — matched Heritage Foundation, "Culture of Life" PACs
}

# Pre-compile word-boundary patterns for each keyword once at import time.
# Using \b...\b prevents substring hits (e.g. \blabor\b won't match "laboratory").
_PATTERNS: dict[str, list[re.Pattern]] = {
    cause: [re.compile(r"\b" + re.escape(kw) + r"\b") for kw in keywords]
    for cause, keywords in CAUSE_KEYWORDS.items()
}


def tag_committee(cmte_nm: str) -> list[str]:
    """Return cause tags for a committee name (may be empty if no match)."""
    name_lower = cmte_nm.lower()
    tags = []
    for cause, patterns in _PATTERNS.items():
        if any(p.search(name_lower) for p in patterns):
            tags.append(cause)
    return tags


def build_cause_rows(committees: list[dict]) -> list[tuple[str, str]]:
    """
    Given a list of dicts with 'cmte_id' and 'cmte_nm',
    return (cmte_id, cause_tag) rows for insertion.
    """
    rows = []
    for c in committees:
        for tag in tag_committee(c["cmte_nm"]):
            rows.append((c["cmte_id"], tag))
    return rows
