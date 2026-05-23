# web/ — the platform (Enes)

The product that reads the database and turns an ask into ranked, cited results. **This is Enes's side and it's a priority** (owns Presentation / the demo).

Sponsors are **ClickHouse + Nimble** (Senso and x402 dropped). No publish step — results render in the UI. Optional: a GitHub Pages dump of results at the end if ahead, to add a "real open-web action."

What lives here:
- **NL parse** — turn the fundraiser's sentence into `cause / geo / min_amount`.
- **Query + score** — call the friend's `query()` over ClickHouse, rank candidates 0–100 with cited reasons.
- **Frontend** — ask box + **live agent activity stream** (the autonomy money-shot) + cited prospect cards (use the `frontend-design` skill).

Build against the mock `prospect_record` (see `../docs/TEAM-SPLIT.md`) so you don't wait on the friend's data. Integrate once. Commit and push frequently — see `../CLAUDE.md`.
