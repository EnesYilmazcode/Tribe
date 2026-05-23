# DEMO-SCRIPT — the 3-minute recording

> Record on the **`?demo=1`** path: real FEC data + real web enrichment, pre-baked so it's
> instant and cannot fail on camera. Freeze 3:45, submit by 4:15. Upload the video and paste
> the LINK into Devpost (a file doesn't count).

## Setup (do this before hitting record)
1. Refresh the snapshot if data changed: `python server/build_demo_snapshot.py` (one command).
2. Start the frontend: `cd web && npm run dev`.
3. Open **`http://localhost:5173/?demo=1`** (the `?demo=1` is essential — instant, reliable).
4. Full-screen the browser, hide bookmarks/extensions, light background.
5. Do one dry run end-to-end so the cards are warm.

## The one ask we record
Click the first example chip **"Major environment donors in California who gave $1,000+"**
(or type it). It matches the snapshot exactly — the parsed chips, the activity stream, and
the cards are all coherent (environment · CA).

## Beat sheet (~3:00)
| Time | What's on screen | Say (narration) |
|---|---|---|
| 0:00–0:15 | Landing: "Find the donors who already care." | "Nonprofits waste weeks guessing who to ask. Tribe reads who's *already given* to your cause — from 2.8 million real FEC records." |
| 0:15–0:30 | Click the example chip; the run starts | "I describe my cause in one sentence. No filters, no forms." |
| 0:30–1:45 | Activity stream filling in (parse → query → rank → enrich → score), then cards appear | "The agent parses it with an LLM, queries 2.8M real contributions in ClickHouse, ranks by cause-affinity, then goes out to the **live web** to enrich the top prospects — all autonomously, no human in the loop." |
| 1:45–2:20 | The **Thomas F. Steyer** card | "Every prospect is real and **cited**. Steyer — a known climate megadonor, $500K to environment committees. Each reason links to the public FEC record, and this **LIVE WEB** line is Nimble pulling his bio from Wikipedia. This is the difference from wealth-screening: we show *who already gives to the cause*, with receipts." |
| 2:20–2:45 | Click **"Draft outreach email"** on the card | "And it closes the loop — one click drafts a personalized outreach email grounded in his actual giving. Find, research, reach out, end to end. (A human reviews before sending.)" |
| 2:45–3:00 | Clean wide shot of the ranked list | "Real giving behavior, cited from public records, enriched live, ready to act on — built on ClickHouse and Nimble. That's Tribe." |

## Hard rules
- **Record on `?demo=1`.** If you want to also show the live `/run`, do it as a *second* take only after the `?demo=1` take is safely recorded.
- Pre-test the exact click 5×. Keep the dry-run tab open as a fallback.
- Don't show `civil_rights` / `small_business` (party-proxy tags). Stick to **environment**.
- If totals still look inflated (Steyer > ~$760k), re-run `build_demo_snapshot.py` after the query `sub_id` dedup lands.

## Money-shots to make sure land on camera
1. The **activity stream** streaming step-by-step (the autonomy proof).
2. The **Steyer card**: score + `fec.gov` citation pills + the **LIVE WEB** Wikipedia enrichment row.
3. The one-sentence input → ranked cited results, with zero manual steps.
