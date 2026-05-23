# BUILD-STEPS — Enes's platform, broken into small steps

> The platform = 3 layers: **input** (sentence → params), **agent** (get data + narrate steps), **output** (ranked cited cards). Build on the mock (`sample_prospects.json`) first so a demo always exists, then swap in the real ClickHouse at the end.
> Commit + push after every step. See `../CLAUDE.md`.

## Phase A — working demo on mock data  ✅ DONE
A recordable demo exists on mock data (`npm run dev`, click an example, watch the run).
- [x] **A1. Scaffold** — Vite + React + TS + Tailwind v4 + framer-motion + lucide-react + clsx. Builds + dev server boots.
- [x] **A2. Layout shell** — header + ask box + two-pane console (activity left, prospects right). Dark "donor intelligence terminal" theme, signal-lime accent, IBM Plex Mono + Instrument Serif.
- [x] **A3. Mock cards** — `ProspectCard` renders `sample_prospects.json`: serif name, color-graded affinity score, cause badges, cited_reasons with `fec.gov ↗` source pills, "live web" enrichment line.
- [x] **A4. Activity stream + mock run** — `runMockStream()` emits parse→query→rank→enrich→score on timed delays; `ActivityStream` shows running-pulse → green-check rows + blinking cursor + parsed-param chips.
- [x] **A5. Commit + push.** ➡️ A full demo now exists.

## Phase B — make it agentic  ✅ DONE
- [x] **B1. NL parse** — `server/nl_parse.py` turns the sentence into `{cause, geo, min_amount}` (Gemini + deterministic `cause_synonyms` fallback), shown as param chips. (The Autonomy proof.)
- [x] **B2. Real streaming** — FastAPI `/run` SSE endpoint (`server/main.py`) emits the real step shape; `runStream.ts` `runAgent()` consumes it via `EventSource` and **falls back to `runMockStream()`** on error/unavailable. CORS open.

## Phase C — integration with friend  (~2:15–3:00) — IN PROGRESS
- [x] **C1.** `/run` calls friend's real ClickHouse `query()`; `TRIBE_SAMPLE_FALLBACK=1` serves the sample set until the contributions table is populated, then auto-switches to real donors.
- [ ] **C2.** Call friend's `enrich()` on the top 5 (`TRIBE_ENRICH=1`); narrate each live Nimble hit in the stream. Run the demo ask end-to-end on real data once contributions land.

## Phase D — polish + freeze  (~3:00–3:45)
- [ ] **D1.** Tighten UI + stream narration.
- [ ] **D2.** Capture one known-good run into `runMockStream()` as demo-mode (`?demo=1`).
- [ ] **D3.** Pre-test the demo ask 5×; cache fallback. **Freeze 3:45.**

## Component map (keep flat)
```
web/src/
  App.tsx                 // layout + run orchestration + state
  lib/runStream.ts        // runMockStream() now; runSSE() in B2 (identical emit shape)
  components/ AskBox · FilterChips · ActivityStream · StepRow · ProspectCard · ProspectDetail · SourcePill
  sample_prospects.json   // the build target / mock
```
