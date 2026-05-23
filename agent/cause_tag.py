"""
Maps FEC committee names → cause tags using keyword matching.
Covers ~20 causes; hand-curated for the top committee name patterns.
"""

CAUSE_KEYWORDS: dict[str, list[str]] = {
    "environment":  ["environment", "climate", "clean energy", "clean water", "conservation",
                     "sierra club", "green", "renewable", "wildlife", "ocean", "nature",
                     "earth", "wilderness", "planet", "sustainability"],
    "education":    ["education", "school", "teacher", "student", "university", "college",
                     "literacy", "learning", "academic", "classroom"],
    "healthcare":   ["health", "medical", "hospital", "cancer", "mental health", "disease",
                     "pharma", "nurse", "doctor", "clinic", "medicare", "medicaid"],
    "housing":      ["housing", "affordable", "homeless", "tenant", "shelter", "rental",
                     "community development"],
    "immigration":  ["immigration", "immigrant", "refugee", "asylum", "daca", "border"],
    "criminal_justice": ["criminal justice", "prison", "policing", "incarceration", "justice reform",
                         "public safety", "law enforcement", "reform"],
    "civil_rights": ["civil rights", "equity", "equality", "discrimination", "naacp",
                     "voting rights", "disability", "lgbtq", "women"],
    "labor":        ["labor", "union", "worker", "wage", "afl", "seiu", "teamster", "trade"],
    "veterans":     ["veteran", "military", "armed forces", "soldier", "navy", "army",
                     "marine", "air force"],
    "gun_control":  ["gun", "firearm", "nra", "second amendment", "gun safety", "gun violence"],
    "reproductive_rights": ["reproductive", "abortion", "planned parenthood", "naral",
                            "pro-choice", "pro-life", "family planning"],
    "agriculture":  ["agriculture", "farm", "rural", "farmer", "crop", "livestock", "food"],
    "small_business": ["small business", "entrepreneur", "startup", "chamber of commerce"],
    "technology":   ["technology", "tech", "innovation", "ai ", "artificial intelligence",
                     "digital", "internet", "cybersecurity"],
    "finance":      ["banking", "finance", "financial", "wall street", "securities",
                     "investment", "credit"],
    "energy":       ["energy", "oil", "gas", "coal", "pipeline", "utility", "electric",
                     "nuclear", "solar", "wind"],
    "foreign_policy": ["foreign", "international", "israel", "ukraine", "nato", "asia",
                       "middle east", "trade", "global"],
    "social_welfare": ["social", "poverty", "food bank", "hunger", "welfare", "community",
                       "charity", "nonprofit"],
    "infrastructure": ["infrastructure", "transportation", "transit", "highway", "broadband",
                       "water system"],
    "arts_culture": ["arts", "culture", "museum", "music", "film", "theater", "heritage"],
}


def tag_committee(cmte_nm: str) -> list[str]:
    """Return cause tags for a committee name (may be empty if no match)."""
    name_lower = cmte_nm.lower()
    tags = []
    for cause, keywords in CAUSE_KEYWORDS.items():
        if any(kw in name_lower for kw in keywords):
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
