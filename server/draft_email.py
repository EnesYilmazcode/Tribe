"""
Draft a personalized outreach email for a prospect, grounded in their real giving.

Gemini (gemini-flash-latest) writes a short, warm, fundraiser-style email that
references the donor's actual cited giving. Baked into the demo snapshot for the
top donors so `?demo=1` shows it instantly (zero live calls on camera).

    from draft_email import draft_email
    p["draft_email"] = draft_email(p)   # -> {"subject": str, "body": str} | None

NOTE: human-in-the-loop draft (review before send), framed as research outreach.
"""
import os
import re
import sys
import json
import requests

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(_HERE), "agent"))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(_HERE), ".env"))

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def _natural_name(raw: str) -> str:
    parts = raw.split(",")
    if len(parts) == 2 and parts[0].strip() and parts[1].strip():
        return f"{parts[1].strip()} {parts[0].strip()}".title()
    return raw.strip()


_PROMPT = """You are a nonprofit development officer writing a brief, warm outreach email
to a prospective major donor, based ONLY on their public political-giving record below.
Do not invent facts or specific dollar figures beyond the summary.

Donor: {name}
Role: {role}
Location: {geo}
Cause focus (from giving): {causes}
Giving summary: {summary}

Write a short outreach email from a fundraiser at a {cause} nonprofit. Reference their
demonstrated commitment to {cause} (use the giving summary, kept general). Warm, specific,
professional, ~80-110 words. End with a soft ask for a 15-minute call. Sign as
"Warm regards,\\nJordan Rivera\\nDevelopment Director".

Return STRICT JSON, nothing else: {{"subject": "<concise subject line>", "body": "<email body>"}}
"""


def draft_email(prospect: dict) -> dict | None:
    key = os.environ.get("GEMINI_API_KEY")
    if not key or not prospect.get("name"):
        return None
    name = _natural_name(prospect["name"])
    causes = ", ".join(prospect.get("cause_tags") or ["this cause"])
    primary = (prospect.get("cause_tags") or ["this cause"])[0]
    role = (prospect.get("occupation") or "").strip() or "—"
    summary = (
        f"${prospect.get('total_given', 0):,} across {prospect.get('num_donations', 0)} "
        f"donations to {causes} committees "
        f"({prospect.get('first_gift_year', '')}-{prospect.get('last_gift_year', '')})"
    )
    prompt = _PROMPT.format(name=name, role=role, geo=prospect.get("geo", ""),
                            causes=causes, cause=primary, summary=summary)
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.4},
    }
    try:
        r = requests.post(GEMINI_URL.format(model=GEMINI_MODEL),
                          params={"key": key}, json=body, timeout=20)
        r.raise_for_status()
        txt = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        data = json.loads(txt)
        subject = (data.get("subject") or "").strip()
        email_body = (data.get("body") or "").strip()
        if not subject or not email_body:
            return None
        return {"subject": subject, "body": email_body}
    except Exception:
        return None


def draft_top(prospects: list[dict], n: int = 3) -> list[dict]:
    for i, p in enumerate(prospects):
        if i >= n:
            break
        p["draft_email"] = draft_email(p)
    return prospects


if __name__ == "__main__":
    sys.path.insert(0, os.path.join(os.path.dirname(_HERE), "agent"))
    from clickhouse_client import query
    p = query(cause="environment", geo="CA", min_amount=1000, limit=1)[0]
    print(json.dumps(draft_email(p), indent=2))
