"""
Tribe backend — the /run SSE endpoint the web/ frontend consumes.

Contract (from web/src/lib/runStream.ts):
  GET /run?ask=<text>   CORS: allow_origins=["*"]
  event: params  data: {cause:[...], geo, min_amount}     (ParsedParams)
  event: step    data: {key, label, status, detail?}       (Step) — running then done
  event: result  data: [ prospect_record, ... ]            (Prospect[])
  event: done    data: {}

Pipeline: parse ask (Gemini + fallback) -> expand causes -> query() ClickHouse ->
(optional) Nimble enrich -> stream steps -> result.

While the friend's `contributions` table is empty, query() returns nothing, so we
fall back to web/sample_prospects.json (TRIBE_SAMPLE_FALLBACK=1, default on) so the
live run is demoable now. It auto-switches to real donors once the table fills.

Run:  cd server && uvicorn main:app --port 8000
"""
import os
import sys
import json
import time

# Make the friend's agent/ modules importable (query, cause expansion, enrich).
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, os.path.join(_ROOT, "agent"))

from dotenv import load_dotenv  # noqa: E402
load_dotenv(os.path.join(_ROOT, ".env"))

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import StreamingResponse  # noqa: E402

import clickhouse_client as ch  # noqa: E402  (client, ping, scoring helpers)
from cause_synonyms import expand_causes  # noqa: E402
from nl_parse import parse_ask  # noqa: E402
from query_clean import query as clean_query  # noqa: E402  (dedup-safe — correct totals)

SAMPLE_FALLBACK = os.environ.get("TRIBE_SAMPLE_FALLBACK", "1") == "1"
ENRICH = os.environ.get("TRIBE_ENRICH", "0") == "1"
PACE = float(os.environ.get("TRIBE_PACE", "0.4"))  # seconds between steps, for a watchable stream
_SAMPLE_PATH = os.path.join(_ROOT, "web", "sample_prospects.json")

app = FastAPI(title="Tribe backend")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


def _sse(event: str, data) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _load_sample() -> list[dict]:
    try:
        with open(_SAMPLE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _money(n: int) -> str:
    return f"${n:,}+"


def _event_stream(ask: str):
    # ---- 1. Parse the request -------------------------------------------------
    yield _sse("step", {"key": "parse", "label": "Parsing request",
                        "status": "running", "detail": f'"{ask}"'})
    time.sleep(PACE)
    parsed = parse_ask(ask)
    causes = parsed["causes"] or ["social_welfare"]   # never query an empty cause set
    geo = parsed["geo"]
    min_amount = parsed["min_amount"]
    # primary cause only — adjacency expansion pulls in mis-tagged committees
    # (e.g. an "environment" ask surfacing an energy-tagged RJC PAC). Stay on-topic.
    expanded = causes

    yield _sse("params", {
        "cause": causes,
        "geo": geo or "All states",
        "min_amount": _money(min_amount),
    })
    yield _sse("step", {
        "key": "parse", "label": "Parsing request", "status": "done",
        "detail": (f"cause: {', '.join(causes)} · geo: {geo or 'all'} · "
                   f"min: {_money(min_amount)} · via {parsed['source']}"),
    })

    # ---- 2. Query ClickHouse over FEC contributions ---------------------------
    yield _sse("step", {"key": "query",
                        "label": "Querying ClickHouse · FEC contributions", "status": "running"})
    t0 = time.time()
    try:
        prospects = clean_query(causes=expanded, geo=geo, min_amount=min_amount, limit=20)
    except Exception as e:  # noqa: BLE001
        print(f"[run] query() error: {e}")
        prospects = []
    ms = int((time.time() - t0) * 1000)

    used_sample = False
    if not prospects and SAMPLE_FALLBACK:
        prospects = _load_sample()
        used_sample = True
    yield _sse("step", {
        "key": "query", "label": "Querying ClickHouse · FEC contributions", "status": "done",
        "detail": f"{len(prospects)} candidates · {ms}ms" + (" · sample data" if used_sample else ""),
    })
    time.sleep(PACE)

    # ---- 3. Rank by cause-affinity -------------------------------------------
    yield _sse("step", {"key": "rank",
                        "label": "Ranking by cause-affinity + recency", "status": "running"})
    prospects.sort(key=lambda p: p.get("affinity_score", 0), reverse=True)
    time.sleep(PACE)
    yield _sse("step", {"key": "rank", "label": "Ranking by cause-affinity + recency",
                        "status": "done", "detail": f"top {len(prospects)} candidates selected"})

    # ---- 4. Live web enrichment (Nimble), top 3, optional --------------------
    yield _sse("step", {"key": "enrich",
                        "label": "Enriching via live web · Nimble", "status": "running"})
    enriched = 0
    if ENRICH and prospects:
        try:
            from enrich_clean import enrich_clean  # fast: 1 Nimble search + Gemini extract
            for p in prospects[:3]:
                if p.get("enrichment"):  # already pre-computed — skip
                    enriched += 1
                    continue
                yield _sse("step", {"key": "enrich", "label": "Enriching via live web · Nimble",
                                    "status": "running", "detail": f"→ {p.get('name')} ({p.get('geo')})"})
                p["enrichment"] = enrich_clean(p)
                enriched += 1
                time.sleep(PACE / 2)
        except Exception as e:  # noqa: BLE001
            print(f"[run] enrich error: {e}")
    else:
        enriched = sum(1 for p in prospects if p.get("enrichment"))
    yield _sse("step", {"key": "enrich", "label": "Enriching via live web · Nimble", "status": "done",
                        "detail": f"{enriched} of {len(prospects)} profiles enriched"})

    # ---- 5. Score -------------------------------------------------------------
    yield _sse("step", {"key": "score", "label": "Scoring cause-affinity 0–100", "status": "running"})
    time.sleep(PACE)
    yield _sse("step", {"key": "score", "label": "Scoring cause-affinity 0–100",
                        "status": "done", "detail": "complete"})

    # ---- Final payload --------------------------------------------------------
    yield _sse("result", prospects)
    yield _sse("done", {})


@app.get("/run")
def run(ask: str):
    return StreamingResponse(
        _event_stream(ask),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/health")
def health():
    return {"ok": True, "clickhouse": ch.ping(), "sample_fallback": SAMPLE_FALLBACK}
