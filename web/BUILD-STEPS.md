# BUILD-STEPS — Enes's platform, broken into small steps

> The platform = 3 layers: **input** (sentence → params), **agent** (get data + narrate steps), **output** (ranked cited cards). Build on the mock (`sample_prospects.json`) first so a demo always exists, then swap in the real ClickHouse at the end.
> Commit + push after every step. See `../CLAUDE.md`.

## Phase A — working demo on mock data  (target done ~1:00)
Highest value: by the end there is a recordable demo even if nothing else gets built.
- [ ] **A1. Scaffold** — Vite + React + TS + Tailwind v4 + framer-motion + lucide-react + clsx. `npm run dev` loads.
- [ ] **A2. Layout shell** — header + top ask box + two columns (activity stream left ~38%, results right ~62%). Dark theme, one accent.
- [ ] **A3. Mock cards** — render `sample_prospects.json` as `<ProspectCard>`: name + color-graded score chip, cause_tags badges, cited_reasons bullets each with a clickable `fec.gov ↗` source pill.
- [ ] **A4. Activity stream + mock run** — `runMockStream()` emits canned steps on ~500ms delays; `<ActivityStream>` renders rows with running-pulse → green-check + framer-motion. Ask box "Run" triggers it, then reveals cards.
- [ ] **A5. Commit + push.** ➡️ A full demo now exists.

## Phase B — make it agentic  (~1:00–2:00)
- [ ] **B1. NL parse** — LLM turns the sentence into `{cause, geo, min_amount}`, shown as editable param chips. (The Autonomy proof.)
- [ ] **B2. Real streaming** — FastAPI `/run` SSE endpoint emits the same step shape from real code; React `EventSource` consumes it, falls back to `runMockStream()` on error. Add `CORSMiddleware(allow_origins=["*"])` immediately.

## Phase C — integration with friend  (~2:15–3:00)
- [ ] **C1.** Swap `query()` stub for friend's real ClickHouse `query()`.
- [ ] **C2.** Call friend's `enrich()` on the top 5; narrate each live Nimble hit in the stream. Run the demo ask end-to-end on real data.

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
