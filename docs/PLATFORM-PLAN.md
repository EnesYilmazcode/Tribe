# PLATFORM-PLAN — Enes's side (the web product)

> How the Tribe frontend/platform is organized. Decided from 3 parallel research agents (input model, frontend architecture, reference UX). Read with `TODO-ENES.md`.
> Sponsors: ClickHouse + Nimble. Results render in the UI (no publish step). Recorded 3-min demo. Build against the mock `prospect_record` first, integrate once.

## 1. Input model (DECIDED): NL text box first, parsed-chips second, upload optional

- **Primary = one natural-language text box** plus a "Find prospects" button plus 2-3 one-click example prompts (example chips de-risk the recording, click, run, done).
  - A structured FORM is rejected as the primary input: a human filling dropdowns visibly does the agent's job and kills the Autonomy score (20%).
- **After parsing, show editable filter chips** (cause / geo / capacity / amount) that the agent auto-filled from the sentence. Proves the agent understood the ask (autonomy + transparency) and lets the user tune it. Best of NL and form. (Clay + Apollo pattern.)
- **Optional "Advanced filters"** panel, present but collapsed by default ("power available," not "manual work required").
- **Optional stretch: "auto-fill from a campaign doc"**, use a PASTE-TEXT box, NOT file upload (avoids PDF-parsing risk). Only build if core loop is green with >1hr left. Voiceover can still say "works with your case-for-support."

**Params the agent must extract** (the query contract to the DB): `cause/issue`, `geography`, `capacity/amount band`, `donor_type`. These map to the industry's capacity / affinity / propensity framework and are all directly queryable in the FEC data.

## 2. Stack (DECIDED): Vite + React + TS + Tailwind + shadcn (cherry-picked) + framer-motion

- **Vite + React + TypeScript + Tailwind v4** (`@tailwindcss/vite` plugin, no PostCSS dance).
- **shadcn/ui**, pull ONLY: card, badge, button, input, separator, scroll-area, sheet/dialog. Cherry-pick so it looks intentional, not boilerplate.
- **framer-motion** (stream enter animations), **lucide-react** (step icons), **clsx**.
- **Rejected:** Streamlit/Gradio (looks generic, fights streaming, judges have seen 50). Next.js (SSR/routing wasted on one page + Python backend).
- **Anti-generic look** (use the `frontend-design` skill): dark theme, one strong accent, **monospace font for the activity stream** (reads like an agent log, not a chat bubble), generous spacing, real data density on cards. Avoid the purple-gradient-hero AI aesthetic.

Scaffold:
```
npm create vite@latest web -- --template react-ts
cd web && npm i && npm i -D tailwindcss @tailwindcss/vite
npm i framer-motion lucide-react clsx
# then add shadcn per https://ui.shadcn.com/docs/installation/vite
```

## 3. Layout (DECIDED): single page, two columns, modal for detail

```
┌──────────── Tribe — donor prospecting agent ────────────┐
│ [ Ask box: "Find major clean-water donors in the PNW" ] [Run ▸] │
│ (after parse) chips: [water] [environment] [WA/OR] [$5k+] (editable) │
├───────────────────────────┬──────────────────────────────┤
│ AGENT ACTIVITY (~38%)      │  RANKED PROSPECTS (~62%)       │
│ monospace, terminal-style  │  grid of cited cards by score  │
│ ✓ Parsed ask → {…}         │  ┌────────────────────────┐    │
│ ✓ Queried ClickHouse·1,204 │  │ Jane Donor      [ 87 ]  │    │
│ ⟳ Enriching top 5 (web)…   │  │ WA · environment·water  │    │
│   → fec.gov/data/receipts  │  │ • $12k to 3 env cmtes ↗ │    │
│ · Scoring…                 │  │ • Current role … (web)↗ │    │
│                            │  │            [Details ▸]  │    │
└───────────────────────────┴──────────────────────────────┘
```

- **Activity stream (left, the star):** step rows, only one "active" at a time (running pulse, then green check), concrete changing detail per step, ~400-700ms pacing so it's readable on camera. Phases are parse, query, enrich, score, done.
- **Prospect card (right), per `prospect_record`:** name + color-graded score chip, geo + cause_tags badges, `cited_reasons[]` each as a bullet with an inline **↗ source pill** (show hostname `fec.gov ↗`, not raw URL), enrichment line tagged "live web" (the Nimble open-web action), and a Details button that opens the drawer.
- **Detail drawer (shadcn sheet):** full cited reasons + enrichment + a "Sources" footer (Perplexity-style numbered cites).
- **Citation UX = the credibility play:** inline numbered cite, hover snippet, source pill. When a claim has no source, SAY "no public record found" rather than omitting. That transparency out-trusts black-box incumbent scores (DonorSearch/iWave).

## 4. The live activity stream: SSE + simulated fallback

- **FastAPI** `/run?ask=...` returns `EventSourceResponse` (`sse-starlette`), yielding `step` events as the real pipeline runs (each pipeline step calls an `emit(phase, status, detail)` callback so the stream narrates REAL work), then a final `result` event holding `prospect_record[]`.
- **React** native `EventSource`: on `step` append, on `result` render cards, on `error` fall back to `runMockStream()`.
- Add `CORSMiddleware(allow_origins=["*"])` immediately (Vite :5173 talking to FastAPI :8000). Add `await asyncio.sleep(0.4)` between emits for readable pacing.
- **Build the simulated `runMockStream()` FIRST.** Same shape as SSE, it's both the early demo and the on-camera fallback.

## 5. Build order (each step demoable, fallback first)
1. (~30m) Scaffold and render `sample_prospects.json` into the card grid, a screen that looks real.
2. (~45m) **`runMockStream()`**, canned steps on timed delays with a working-to-done animation. **This alone makes a convincing demo on mock data. De-risks everything.**
3. (~30m) Ask box wired to `runDemo()` that picks SSE if backend reachable, else mock. Same state shape, no UI branching.
4. (~45m) Real FastAPI SSE `/run` with `emit()` in the parse/query/score path (query() still a stub).
5. (~45m, ~3:00) Integration: swap the stub for the real `query()`, call `enrich()` on top-N, narrate each live Nimble hit.
6. (freeze 3:45) Capture a known-good real run into `runMockStream()` as "demo mode" (`?demo=1` flag). Record with this if anything flakes.

## 6. Top risks and mitigations
- **Streaming flakes on camera (#1):** `onerror` auto-falls back to mock plus a `?demo=1` forced-mock flag. Demo cannot break.
- **CORS:** add middleware in step 4, not at integration.
- **SSE buffering (all-at-once):** sse-starlette handles it, add `X-Accel-Buffering: no` if proxied, and the `sleep` guarantees staging.
- **Integration slips:** steps 1-4 are 100% mock-driven and fully demoable, so record on mock if needed.

## Component structure
```
web/src/
  App.tsx                 // layout + run orchestration + state
  lib/runStream.ts        // runSSE() + runMockStream() — identical emit shape
  data/sample_prospects.json
  data/cannedRun.ts        // captured known-good run (demo mode)
  components/ AskBox · FilterChips · ActivityStream · StepRow · ProspectCard · ProspectDetail · SourcePill
```
