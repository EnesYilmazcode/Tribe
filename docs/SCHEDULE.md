# SCHEDULE: Tribe @ Datadog Agentic Engineering Hack (2026-05-23)

> Wall-clock plan for the day. Anchored to the official event schedule.
> Maps directly to the build phases in `PLAN.md`.

## Key facts (answers to the obvious questions)
- **Is the demo live or recorded?** **Recorded.** You submit a **3-minute demo video**, a public GitHub repo, and Devpost details by the deadline. The video IS the submission.
- **When is the submission deadline?** **4:30 PM ET.** Late submissions may be cut off, so treat 4:15 PM as the real wall.
- **Is everyone guaranteed a live interview/presentation?** **No.** Only **finalists** present live at 5:00 PM. You must be selected from the submitted videos. So the recording quality is what gets you to the live round, not the other way around.
- **Coding window:** 11:00 AM to 4:30 PM ET is **5.5 hours total**, but ~45 min of that is demo recording plus submission. Real build time is about **4h 45m**.

## Official event timeline (fixed)
| Time | Event |
|---|---|
| 9:00 AM | Doors open (arrive early, capacity hits ~9:45 AM, first come first served) |
| 9:45 AM | Keynote & opening remarks |
| **11:00 AM** | **Start coding** |
| 1:30 PM | Lunch (grab it, keep working) |
| **4:30 PM** | **Submission deadline** (video + repo + Devpost) |
| 5:00 PM | Finalists present live + judging |
| 7:00 PM | Awards ceremony |

## Our build schedule (wall-clock)
| Block | Time | Phase (from PLAN.md) | Goal at end of block |
|---|---|---|---|
| **Setup** | 11:00 – 11:30 | Phase 0 | Stack chosen, all 4 sponsor signups started, FEC data downloading, repo scaffolded |
| **MVP spine** | 11:30 – 12:45 | Phase 1, ClickHouse | `agent.py` returns ranked real donors from real FEC data, the **MVP** |
| **Senso publish** | 12:45 – 1:45 | Phase 2, Senso | NL to FEC to a **published cited profile**. *3-tool threshold met, winnable here* |
| *Lunch* | grab at 1:30 | — | Eat at desk, don't lose the block |
| **Nimble enrich** | 1:45 – 2:30 | Phase 3, Nimble | Profiles blend FEC history with live web enrichment |
| **Autonomy polish** | 2:30 – 3:15 | Phase 4, LLM parse | Type a sentence, get a fully autonomous run. All 3 sponsor tools live |
| **Buffer / debug** | 3:15 – 3:45 | slack | Fix whatever's flaky, freeze features at 3:45 sharp |
| **DEMO RECORDING** | 3:45 – 4:15 | Phase 5 | 3-min video recorded, README cleaned to FEC story |
| **SUBMIT** | 4:15 – 4:30 | Phase 5 | Devpost submitted with 15 min to spare |

## Time budget summary
- **MVP (demoable):** ready by **~1:45 PM** (Phases 0–2). This is the "we can win" floor, about 2h45m in.
- **Full 3-tool build:** ~2:30 PM, polish plus buffer to 3:45 PM.
- **Demo recording:** **30 min reserved (3:45–4:15)**, non-negotiable, do not eat into this.
- **Submission buffer:** 15 min (4:15–4:30), treat 4:15 as the deadline.

## The 3-minute demo video script (record in Phase 5)
| Time | Beat |
|---|---|
| 0:00–0:15 | Problem: fundraisers waste weeks guessing who to ask. Real giving behavior is a better signal than wealth screening. |
| 0:15–0:35 | Type the natural-language ask on camera. |
| 0:35–2:05 | Watch it run **autonomously**: parse, ClickHouse FEC query, Nimble enrichment, scoring, then Senso publishes a cited profile. Narrate the autonomy. |
| 2:05–2:35 | Show the live published cited.md profile with real citations. This is the money shot. |
| 2:35–3:00 | Architecture plus a 3 sponsor tools recap (ClickHouse, Nimble, Senso). |

## Hard rules
- **Freeze features at 3:45 PM.** Anything not working by then doesn't go in the demo.
- **Record the demo even if incomplete.** A polished video of the MVP beats a broken full build with no video. No video means no chance at finalist.
- **Pre-test the demo example 3+ times** and keep a cached fallback run in case live APIs flake during recording.
- If behind schedule, **cut Nimble before Senso, never the demo recording.** (x402 is already out of scope.)
