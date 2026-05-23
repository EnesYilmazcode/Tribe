"""
Fast, clean donor enrichment — replaces the slow/garbage regex path for the demo.

One Nimble web search (no slow page-extract) + one Gemini call to extract clean,
UI-shaped fields. ~5-10s/prospect vs ~24-48s, and readable instead of
"Fahr, Llc at Founder" / employer "State,".

    from enrich_clean import enrich_clean, enrich_top
    p["enrichment"] = enrich_clean(p)          # one prospect
    enrich_top(prospects, n=2)                 # top-N in place (for the snapshot)

Returns the UI enrichment shape: {"current_role", "notes"|None, "source_url"}.
Degrades gracefully (never raises) so the demo can't break.
"""
import os
import re
import sys
import json
import requests

_ACRONYMS = {"llc", "lp", "llp", "pac", "inc", "pllc"}


def _tidy_org(s: str) -> str:
    return re.sub(r"[A-Za-z]+", lambda m: m.group().upper()
                  if m.group().lower() in _ACRONYMS else m.group(), s)


def _natural_name(raw: str) -> str:
    """FEC 'LAST, FIRST M' -> 'First M Last' for web search and display."""
    parts = raw.split(",")
    if len(parts) == 2 and parts[0].strip() and parts[1].strip():
        return f"{parts[1].strip()} {parts[0].strip()}".title()
    return raw.strip()

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(_HERE), "agent"))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(_HERE), ".env"))

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

_PROMPT = """From the web search snippets below, extract a clean profile of {name},
a US political donor{ctx}. Use ONLY the snippets — do not invent anything.

Return STRICT JSON, nothing else:
{{"current_role": "<job title and org in natural order, e.g. 'Founder, Fahr LLC'; empty string if unknown>",
  "notes": "<ONE concise sentence on their philanthropy / board roles / public profile; empty string if none found>",
  "source_url": "<the single most authoritative URL from the list below; empty string if none>"}}

Snippets:
{snippets}
"""


def _search_snippets(name: str, employer: str) -> list[dict]:
    """One Nimble search; return [{title, text, url}]. Empty list on any failure."""
    try:
        from nimble_client import _search  # reuse Nimble auth/config
    except Exception:
        return []
    q = f"{_natural_name(name)} {employer} philanthropy foundation board".strip()
    try:
        hits = _search(q, num_results=5)
    except Exception:
        return []
    out = []
    for h in hits:
        text = h.get("snippet") or h.get("description") or ""
        url = h.get("url") or ""
        if text:
            out.append({"title": h.get("title", ""), "text": text, "url": url})
    return out


def _gemini_extract(name: str, ctx: str, snippets: list[dict]) -> dict | None:
    key = os.environ.get("GEMINI_API_KEY")
    if not key or not snippets:
        return None
    block = "\n".join(f"- {s['text']} ({s['url']})" for s in snippets[:5])
    body = {
        "contents": [{"parts": [{"text": _PROMPT.format(name=name, ctx=ctx, snippets=block)}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0},
    }
    try:
        r = requests.post(GEMINI_URL.format(model=GEMINI_MODEL),
                          params={"key": key}, json=body, timeout=15)
        r.raise_for_status()
        txt = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(txt)
    except Exception:
        return None


def _fallback(prospect: dict, snippets: list[dict]) -> dict:
    """No Gemini/Nimble — at least give a clean role from the FEC fields."""
    occ = (prospect.get("occupation") or "").strip()
    emp = (prospect.get("employer") or "").strip()
    role = ", ".join(x for x in [occ, emp] if x and x.upper() not in
                     {"", "RETIRED", "N/A", "NA", "SELF-EMPLOYED", "NONE"})
    return {
        "current_role": role,
        "notes": None,
        "source_url": snippets[0]["url"] if snippets else "",
    }


def enrich_clean(prospect: dict) -> dict | None:
    """Return clean {current_role, notes, source_url} for one prospect, or None."""
    raw = (prospect.get("name") or "").strip()
    if not raw:
        return None
    name = _natural_name(raw)
    employer = (prospect.get("employer") or "").strip()
    occ = (prospect.get("occupation") or "").strip()
    geo = (prospect.get("geo") or "").strip()
    ctx = ""
    if employer or occ:
        ctx += f" who is a {occ} at {employer}".rstrip()
    if geo:
        ctx += f" in {geo}"

    snippets = _search_snippets(raw, employer)
    data = _gemini_extract(name, ctx, snippets)
    if not data:
        return _fallback(prospect, snippets)

    valid_urls = {s["url"] for s in snippets if s["url"]}
    src = data.get("source_url") or ""
    if src not in valid_urls:
        src = next(iter(valid_urls), "")
    notes = (data.get("notes") or "").strip() or None
    role = (data.get("current_role") or "").strip()
    if not role:
        role = _fallback(prospect, snippets)["current_role"]
    return {"current_role": _tidy_org(role), "notes": notes, "source_url": src}


def enrich_top(prospects: list[dict], n: int = 2) -> list[dict]:
    """Enrich the top-n prospects in place (they arrive already score-sorted)."""
    for i, p in enumerate(prospects):
        if i >= n:
            break
        p["enrichment"] = enrich_clean(p)
    return prospects


if __name__ == "__main__":
    import time
    sys.path.insert(0, os.path.join(os.path.dirname(_HERE), "agent"))
    from clickhouse_client import query
    ps = query(cause="environment", geo="CA", min_amount=1000, limit=2)
    for p in ps:
        t = time.time()
        e = enrich_clean(p)
        print(f"\n{p['name']}  ({time.time()-t:.1f}s)")
        print(json.dumps(e, indent=2))
