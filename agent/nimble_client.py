"""
Nimble web enrichment for top FEC donor candidates.

Uses Nimble's Web Search API to pull live public signals for each donor:
  - Current employer / role
  - Recent public giving or philanthropy
  - Board memberships, nonprofit affiliations
  - News mentions

Usage:
    from nimble_client import enrich

    prospect = query(cause="environment", geo="WA")[0]
    prospect["enrichment"] = enrich(prospect)

Nimble docs: https://docs.nimbleway.com/nimble-api/web-api/realtime-search
"""

import os
import re

import certifi
import requests
from dotenv import load_dotenv

os.environ.setdefault("SSL_CERT_FILE", certifi.where())
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

NIMBLE_API_KEY = os.environ.get("NIMBLE_API_KEY", "")
NIMBLE_SEARCH_URL = "https://api.webit.live/api/v1/realtime/serp"
NIMBLE_EXTRACT_URL = "https://api.webit.live/api/v1/realtime/web"

HEADERS = {
    "Authorization": f"Basic {NIMBLE_API_KEY}",
    "Content-Type": "application/json",
}


def _search(query: str, num_results: int = 5) -> list[dict]:
    """Run a Nimble web search and return organic result snippets."""
    payload = {
        "search_engine": "google_search",
        "query": query,
        "num_results": num_results,
        "country": "US",
        "locale": "en",
        "parse": True,
    }
    r = requests.post(NIMBLE_SEARCH_URL, json=payload, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data.get("parsing", {}).get("entities", {}).get("OrganicResult", [])


def _extract_page(url: str) -> str:
    """Fetch a URL via Nimble and return clean markdown text."""
    payload = {
        "url": url,
        "render": False,
        "country": "US",
        "locale": "en",
        "format": "markdown",
    }
    r = requests.post(NIMBLE_EXTRACT_URL, json=payload, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json().get("text", "")


def enrich(prospect: dict) -> dict | None:
    """
    Live-enrich a prospect using Nimble web search.

    Args:
        prospect: A prospect_record dict from clickhouse_client.query().
                  Must have 'name', 'geo', 'employer', 'occupation'.

    Returns:
        enrichment dict or None on failure.
        {
            "current_role": str,
            "employer":     str,
            "bio_snippet":  str,
            "philanthropy": str,   # any public giving / nonprofit ties
            "news":         str,   # recent mentions
            "source_urls":  [str],
        }
    """
    if not NIMBLE_API_KEY:
        return None

    name     = prospect["name"]
    state    = prospect.get("geo", "")
    employer = prospect.get("employer", "")
    occ      = prospect.get("occupation", "")

    # Build targeted search queries
    search_queries = [
        f'"{name}" {state} donor philanthropist',
        f'"{name}" {employer} {occ} biography',
        f'"{name}" nonprofit board foundation giving',
    ]

    results = []
    source_urls = []

    for q in search_queries:
        try:
            hits = _search(q, num_results=3)
            for h in hits:
                snippet = h.get("description", "")
                url     = h.get("url", "")
                if snippet and name.split()[0].lower() in snippet.lower():
                    results.append(snippet)
                    if url:
                        source_urls.append(url)
        except Exception:
            continue

    if not results:
        return None

    # Try to extract the most promising URL for a deeper pull
    deep_text = ""
    if source_urls:
        for url in source_urls[:2]:
            try:
                text = _extract_page(url)
                if name.split()[0].lower() in text.lower():
                    deep_text = text[:2000]
                    break
            except Exception:
                continue

    combined = "\n".join(results) + "\n" + deep_text

    return {
        "current_role": _extract_role(combined, employer, occ),
        "employer":     _extract_employer(combined, employer),
        "bio_snippet":  combined[:400].strip(),
        "philanthropy": _extract_philanthropy(combined),
        "news":         _extract_news(combined, name),
        "source_urls":  source_urls[:3],
    }


def enrich_batch(prospects: list[dict], top_n: int = 5) -> list[dict]:
    """
    Enrich the top_n prospects in-place and return the full list.
    Only enriches the highest-scoring candidates to limit API calls.
    """
    sorted_prospects = sorted(prospects, key=lambda p: p.get("affinity_score", 0), reverse=True)
    for i, p in enumerate(sorted_prospects):
        if i >= top_n:
            break
        print(f"  Enriching [{i+1}/{top_n}]: {p['name']}...")
        p["enrichment"] = enrich(p)
    return sorted_prospects


# ── simple text extractors ────────────────────────────────────────────────────

def _extract_role(text: str, fallback_occ: str, fallback_employer: str) -> str:
    patterns = [
        r"(?:CEO|CFO|CTO|President|Founder|Partner|Director|Chair|Managing Director|Principal)[^\.\n]{0,60}",
        r"(?:serves?|is|was) (?:a |an |the )?([A-Z][a-z]+ (?:at|of|for) [A-Z][^\.\n]{0,40})",
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            return m.group(0).strip()
    return f"{fallback_occ} at {fallback_employer}".strip(" at")


def _extract_employer(text: str, fallback: str) -> str:
    m = re.search(r"(?:at|with|of) ([A-Z][A-Za-z &,\.]+(?:LLC|Inc|Corp|Group|Capital|Partners|Fund|Foundation)?)", text)
    return m.group(1).strip() if m else fallback


def _extract_philanthropy(text: str) -> str:
    sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
    philanthropy_kw = ["donat", "philanthrop", "foundation", "nonprofit", "endow",
                       "grant", "charit", "board", "trustee", "million"]
    hits = [s for s in sentences if any(kw in s.lower() for kw in philanthropy_kw)]
    return ". ".join(hits[:3]) if hits else ""


def _extract_news(text: str, name: str) -> str:
    sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
    first = name.split()[0].lower()
    news_kw = ["announced", "named", "appointed", "raised", "launched", "invested",
               "awarded", "joined", "led", "founded"]
    hits = [s for s in sentences
            if first in s.lower() and any(kw in s.lower() for kw in news_kw)]
    return ". ".join(hits[:2]) if hits else ""
