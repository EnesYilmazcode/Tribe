# DEMO-SCRIPT — the 3-minute recording

> Record on the **`?demo=1`** path: real FEC data + real web enrichment, pre-baked so it's
> instant and cannot fail on camera. Freeze 3:45, submit by 4:15. Upload the video and paste
> the LINK into Devpost (a file doesn't count).

**Roles:**
- **Controller** (Enes) — drives the mouse, types, clicks. Stay calm, move deliberately.
- **Speaker** (Trevor) — narrates. Don't read off a script, just hit the beats. Natural > perfect.

---

## Setup (do this before hitting record)
1. Refresh the snapshot if data changed: `python server/build_demo_snapshot.py`
2. Start the frontend: `cd web && npm run dev`
3. Open **`http://localhost:5173/?demo=1`** — the `?demo=1` is essential
4. Full-screen the browser, hide bookmarks/extensions, light background
5. Do one dry run end-to-end so the cards are warm

---

## Beat sheet (~3:00)

### 0:00 – 0:15 · Landing page
| | |
|---|---|
| **Controller** | Hold still on the landing. Let the headline breathe. |
| **Speaker** | "Nonprofits spend weeks manually researching donors — Googling names, cross-referencing spreadsheets, guessing who actually cares. Tribe does that in seconds, from 2.8 million real FEC records." |

---

### 0:15 – 0:30 · Type the ask
| | |
|---|---|
| **Controller** | Click the example chip **"Major environment donors in California who gave $1,000+"** — or type it slowly so it reads on screen. Hit run. |
| **Speaker** | "I just describe what I'm looking for — the same way I'd explain it to a colleague. No forms, no filters." |

---

### 0:30 – 1:45 · Activity stream
| | |
|---|---|
| **Controller** | Stay on the activity stream as each step appears. Don't scroll yet. |
| **Speaker** | "Watch the agent work in real time. It parses the request with an LLM, queries 2.8 million real contribution records in ClickHouse, ranks donors by how consistently and recently they've given to this cause — and then it goes out to the live web through Nimble to pull each person's current bio. All of that autonomously, no human in the loop." |

---

### 1:45 – 2:20 · The Steyer card
| | |
|---|---|
| **Controller** | Scroll to the **Thomas F. Steyer** card. Let it sit. Maybe hover the citation pills to show they're real links. |
| **Speaker** | "Every result is real and fully cited. Tom Steyer — $500,000 to environment committees, verified directly against the FEC record. The citation pills link to the actual public filing — anyone can check. And this enrichment line — that's Nimble pulling his bio from the live web right now. This isn't a wealth-screening tool. We're showing you who *already gives to this cause*, with receipts." |

---

### 2:20 – 2:45 · Draft outreach email
| | |
|---|---|
| **Controller** | Click **"Draft outreach email"** on the Steyer card. |
| **Speaker** | "And it closes the loop. One click drafts a personalized outreach email, grounded in his actual giving history. Find, research, reach out — end to end. A human reviews before anything gets sent." |

---

### 2:45 – 3:00 · Wide shot of the ranked list
| | |
|---|---|
| **Controller** | Scroll back up slowly to show the full ranked list. |
| **Speaker** | "Real giving behavior. Cited from public records. Enriched live from the web. Built on ClickHouse and Nimble. That's Tribe." |

---

## Hard rules
- **Record on `?demo=1`.** If you want to show the live `/run`, do it as a second take only after the demo take is safely in the bag.
- Pre-test the exact click 5×. Keep the dry-run tab open as a fallback.
- Stick to **environment**. Don't demo `civil_rights` / `small_business` — those are party-proxy tags.
- Controller: move the mouse slowly and deliberately. Nervous fast-clicking reads badly on video.
- Speaker: breathe. Pauses are fine. "Natural" beats "polished" in a 3-minute hack demo.

## Money-shots — make sure these land on camera
1. The **activity stream** streaming step-by-step — this is the autonomy proof.
2. The **Steyer card** — score, `fec.gov` citation pills, and the live web enrichment row.
3. The one-sentence input → ranked cited results, zero manual steps.
