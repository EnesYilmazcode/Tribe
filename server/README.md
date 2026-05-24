# server/ : the /run SSE backend (Enes)

The engine the frontend (`web/`) calls. It parses the natural-language ask, queries the
friend's ClickHouse `query()`, and streams the agent run back as Server-Sent Events.

## Run
```bash
pip install -r server/requirements.txt
python -m uvicorn main:app --port 8000 --app-dir server
# health check: GET http://localhost:8000/health
```
The frontend defaults to `http://localhost:8000` (override with `VITE_API_URL`). With the
server up, `npm run dev` in `web/` renders the live run, no `?demo=1` needed.

## Contract (matches web/src/lib/runStream.ts)
`GET /run?ask=<text>` → SSE:
- `event: params` `{cause:[...], geo, min_amount}`
- `event: step`   `{key, label, status:"running"|"done", detail?}` (upserted by key)
- `event: result` `[prospect_record, ...]`
- `event: done`   `{}`

## Pipeline
Parse the ask (`nl_parse.parse_ask`: Gemini plus a deterministic `cause_synonyms` fallback),
then `expand_causes`, then `clickhouse_client.query()`, then optional Nimble enrich, then stream.

## Env flags (.env at repo root)
- `GEMINI_MODEL` defaults to `gemini-2.5-flash`. (Note: the `gemini-2.0-flash` free quota is exhausted and returns 429.)
- `TRIBE_SAMPLE_FALLBACK` defaults to `1`. When `query()` returns nothing (contributions table
  still empty), fall back to `web/sample_prospects.json` so the live run is demoable now.
  **Auto-switches to real donors the moment the contributions table is populated.**
- `TRIBE_ENRICH` defaults to `0`. Set `1` to call Nimble `enrich()` on the top 5 (costs credits).
- `TRIBE_PACE` defaults to `0.4`s between steps, so the activity stream is watchable.
