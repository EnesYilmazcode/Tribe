# web/ — the platform (Enes)

The product that reads the database and turns an ask into ranked, cited results. **This is Enes's side and it's a priority** (owns Presentation / the demo).

Sponsors are **ClickHouse + Nimble** (Senso and x402 dropped). No publish step — results render in the UI. Optional: a GitHub Pages dump of results at the end if ahead, to add a "real open-web action."

What lives here (the frontend):
- **Ask box** + **live agent activity stream** (the autonomy money-shot) + cited prospect cards (built with the `frontend-design` skill).
- `lib/runStream.ts` — `runAgent()` consumes the `/run` SSE stream from `../server/` and **falls back to `runMockStream()`** (driven by `sample_prospects.json`) if the server is down or `EventSource` is unavailable. The UI never branches — same step/param/result shape either way.

The NL parse, ClickHouse `query()`, scoring, and Nimble enrichment now live in **`../server/`** (the `/run` SSE backend). To run live, start that server (see `../server/README.md`); otherwise the frontend renders the mock automatically.

Build against the mock `prospect_record` (see `../docs/TEAM-SPLIT.md`) so you don't wait on the friend's data. Commit and push frequently — see `../CLAUDE.md`.
