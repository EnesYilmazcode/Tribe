# web/ — the platform (Enes)

The product that reads the database and turns an ask into published, cited research records. **This is Enes's side and it's a priority** (owns the Senso $3k track + Presentation).

What lives here:
- **NL parse** — turn the fundraiser's sentence into `cause / geo / min_amount`.
- **Query + score** — call the friend's `query()` over ClickHouse, rank candidates.
- **Frontend** — ask box + live agent activity stream + cited prospect cards (use the `frontend-design` skill).
- **Senso publish** — publish each `prospect_record` as a cited page to cited.md. **De-risk this FIRST** with one hardcoded page end-to-end (binary $3k gate).

Build against the mock `prospect_record` (see `../docs/TEAM-SPLIT.md`) so you don't wait on the friend's data. Integrate once. Commit and push frequently — see `../CLAUDE.md`.
