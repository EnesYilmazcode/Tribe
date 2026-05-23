"""
Natural-language ask -> structured query params.

Primary: one Gemini call (free tier, REST — no SDK dependency) that maps the
sentence to our 20 real cause tags + geo + min_amount.
Fallback: deterministic cause_synonyms matching when the API is unavailable,
so the demo never hard-fails on a missing/rate-limited key.

    from nl_parse import parse_ask
    parse_ask("major clean-water donors in the Pacific Northwest who gave $1k+")
    # -> {"causes": ["environment"], "geo": "WA", "min_amount": 1000, "source": "gemini"}
"""
import os
import re
import json
import requests

from cause_synonyms import map_text_to_causes  # deterministic NL -> tags
from cause_tag import CAUSE_KEYWORDS            # the 20 real tags (source of truth)

VALID_TAGS = sorted(CAUSE_KEYWORDS)
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

# Full state names -> 2-letter, for the deterministic fallback's geo extraction.
_STATES = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA",
    "colorado": "CO", "connecticut": "CT", "delaware": "DE", "florida": "FL", "georgia": "GA",
    "hawaii": "HI", "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA",
    "kansas": "KS", "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
    "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV", "new hampshire": "NH",
    "new jersey": "NJ", "new mexico": "NM", "new york": "NY", "north carolina": "NC",
    "north dakota": "ND", "ohio": "OH", "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA",
    "rhode island": "RI", "south carolina": "SC", "south dakota": "SD", "tennessee": "TN",
    "texas": "TX", "utah": "UT", "vermont": "VT", "virginia": "VA", "washington": "WA",
    "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY",
}
# Region hints -> a representative state (so "Pacific Northwest" doesn't return null).
_REGIONS = {"pacific northwest": "WA", "pnw": "WA", "bay area": "CA", "new england": "MA",
            "midwest": "IL", "deep south": "GA", "west coast": "CA", "east coast": "NY"}

_PROMPT = """You convert a fundraiser's request into a donor-search query.
Valid cause tags (use ONLY these): {tags}

Return STRICT JSON, nothing else:
{{"causes": ["<tag>", ...], "geo": "<2-letter US state>" or null, "min_amount": <integer dollars>}}

Rules:
- "causes": every valid tag the ask relates to. Expand niche -> broad
  (e.g. lizards/whales/melting ice -> ["environment"]; Dreamers -> ["immigration"]).
- "geo": 2-letter state code if a place is named, else null. Map a region to one
  representative state (Pacific Northwest -> WA).
- "min_amount": minimum single gift in dollars if stated, else 200.
Ask: "{ask}"
"""


def _gemini(ask: str) -> dict:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY not set")
    body = {
        "contents": [{"parts": [{"text": _PROMPT.format(tags=VALID_TAGS, ask=ask)}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0},
    }
    r = requests.post(
        GEMINI_URL.format(model=GEMINI_MODEL),
        params={"key": key}, json=body, timeout=15,
    )
    r.raise_for_status()
    txt = r.json()["candidates"][0]["content"]["parts"][0]["text"]
    data = json.loads(txt)

    causes = [c for c in data.get("causes", []) if c in CAUSE_KEYWORDS]  # validate!
    if not causes:
        raise ValueError("Gemini returned no valid causes")
    geo = data.get("geo")
    geo = geo.strip().upper()[:2] if isinstance(geo, str) and geo.strip() else None
    try:
        amt = max(0, int(data.get("min_amount") or 200))
    except (TypeError, ValueError):
        amt = 200
    return {"causes": causes, "geo": geo, "min_amount": amt, "source": "gemini"}


def _extract_state(ask: str) -> str | None:
    low = f" {ask.lower()} "
    for name, ab in _REGIONS.items():
        if name in low:
            return ab
    for name, ab in _STATES.items():
        if f" {name} " in low:
            return ab
    # 2-letter code as a standalone token, e.g. "in WA"
    m = re.search(r"\b([A-Z]{2})\b", ask)
    if m and m.group(1) in _STATES.values():
        return m.group(1)
    return None


def _extract_amount(ask: str) -> int:
    # "$1,000" / "$5k" / "1000 dollars"
    m = re.search(r"\$?\s*([\d,]+)\s*(k|thousand)?", ask.lower())
    if not m:
        return 200
    try:
        n = int(m.group(1).replace(",", ""))
    except ValueError:
        return 200
    if m.group(2):
        n *= 1000
    return n if n >= 1 else 200


def _fallback(ask: str) -> dict:
    causes = map_text_to_causes(ask)
    return {
        "causes": causes,                  # may be [] if nothing matched
        "geo": _extract_state(ask),
        "min_amount": _extract_amount(ask),
        "source": "fallback",
    }


def parse_ask(ask: str) -> dict:
    """Return {causes:[...valid tags...], geo:str|None, min_amount:int, source:str}."""
    try:
        return _gemini(ask)
    except Exception as e:  # noqa: BLE001 - any failure should degrade, not crash
        print(f"[nl_parse] Gemini unavailable ({e}); using deterministic fallback")
        return _fallback(ask)


if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "major clean-water donors in the Pacific Northwest who gave $1k+"
    print(json.dumps(parse_ask(q), indent=2))
