import type { Prospect, StreamHandlers } from "../types";
import { formatName } from "./format";
import prospects from "../../sample_prospects.json";

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

const data = prospects as unknown as Prospect[];

// Backend base URL — override with VITE_API_URL at build/run time.
const API_BASE =
  (import.meta.env as unknown as Record<string, string | undefined>).VITE_API_URL ??
  "http://localhost:8000";

/**
 * Entry point the UI calls. Picks the live SSE backend, but:
 *   - `?demo=1` in the URL forces the canned mock run (safe for recording).
 *   - any connection failure falls back to the mock so the demo never breaks.
 */
export function runAgent(ask: string, h: StreamHandlers): void {
  const forceMock =
    typeof window !== "undefined" &&
    new URLSearchParams(window.location.search).get("demo") === "1";
  if (forceMock) {
    void runMockStream(ask, h);
    return;
  }
  runSSE(ask, h);
}

/**
 * Consume the backend's Server-Sent Events stream.
 *
 * Backend contract — GET {API_BASE}/run?ask=<text>, emitting named events:
 *   event: params  data: {cause:[...], geo, min_amount}        (ParsedParams)
 *   event: step    data: {key, label, status, detail?}          (Step) — many
 *   event: result  data: [ prospect_record, ... ]               (Prospect[])
 *   event: done    data: {}                                      (stream end)
 * Each Step is upserted by `key` on the UI side, so emit a step "running" then
 * the same key "done" to flip its state — exactly like runMockStream below.
 */
export function runSSE(ask: string, h: StreamHandlers): void {
  let gotAnyEvent = false;
  let finished = false;

  let es: EventSource;
  try {
    es = new EventSource(`${API_BASE}/run?ask=${encodeURIComponent(ask)}`);
  } catch {
    void runMockStream(ask, h); // EventSource unavailable — go straight to mock
    return;
  }

  const finish = () => {
    if (finished) return;
    finished = true;
    es.close();
    h.onComplete();
  };

  es.addEventListener("params", (e) => {
    gotAnyEvent = true;
    h.onParams(JSON.parse((e as MessageEvent).data));
  });
  es.addEventListener("step", (e) => {
    gotAnyEvent = true;
    h.onStep(JSON.parse((e as MessageEvent).data));
  });
  es.addEventListener("result", (e) => {
    gotAnyEvent = true;
    h.onResult(JSON.parse((e as MessageEvent).data));
  });
  es.addEventListener("done", finish);

  es.onerror = () => {
    if (finished) return;
    if (gotAnyEvent) {
      // Stream started then dropped — keep what we have, just complete.
      finish();
    } else {
      // Never connected (backend down) — fall back to the mock run.
      finished = true;
      es.close();
      void runMockStream(ask, h);
    }
  };
}

/**
 * Mock run of the agent pipeline. Emits the same event shape the SSE backend
 * does, so the UI never has to branch. Drives the demo from sample_prospects.json.
 */
export async function runMockStream(ask: string, h: StreamHandlers): Promise<void> {
  // 1. Parse the request. Derive the shown params from the actual snapshot so the
  // chips/counts always match the cards (the snapshot can change without editing this).
  h.onStep({ key: "parse", label: "Parsing request", status: "running", detail: `"${ask}"` });
  await sleep(700);
  const causeTags = [...new Set(data.flatMap((p) => p.cause_tags))].slice(0, 2);
  const geos = [...new Set(data.map((p) => p.geo).filter(Boolean))];
  const params = {
    cause: causeTags.length ? causeTags : ["environment"],
    geo: geos.length === 1 ? geos[0] : geos.slice(0, 2).join(" · ") || "All states",
    min_amount: "$1,000+",
  };
  h.onParams(params);
  h.onStep({
    key: "parse",
    label: "Parsing request",
    status: "done",
    detail: `cause: ${params.cause.join(", ")} · geo: ${params.geo} · min: ${params.min_amount}`,
  });

  // 2. Query ClickHouse over FEC data
  h.onStep({ key: "query", label: "Querying ClickHouse · FEC contributions", status: "running" });
  await sleep(900);
  h.onStep({
    key: "query",
    label: "Querying ClickHouse · FEC contributions",
    status: "done",
    detail: `scanned 2.8M FEC contributions · ${data.length} cause-affinity matches`,
  });

  // 3. Rank by cause-affinity
  h.onStep({ key: "rank", label: "Ranking by cause-affinity + recency", status: "running" });
  await sleep(650);
  h.onStep({
    key: "rank",
    label: "Ranking by cause-affinity + recency",
    status: "done",
    detail: `top ${data.length} candidates selected`,
  });

  // 4. Live web enrichment (Nimble) — narrate per candidate
  h.onStep({ key: "enrich", label: "Enriching via live web · Nimble", status: "running" });
  for (const p of data) {
    await sleep(420);
    h.onStep({
      key: "enrich",
      label: "Enriching via live web · Nimble",
      status: "running",
      detail: `→ ${formatName(p.name)} (${p.geo})`,
    });
  }
  await sleep(300);
  h.onStep({
    key: "enrich",
    label: "Enriching via live web · Nimble",
    status: "done",
    detail: `${data.filter((p) => p.enrichment).length} of ${data.length} profiles enriched`,
  });

  // 5. Score
  h.onStep({ key: "score", label: "Scoring cause-affinity 0–100", status: "running" });
  await sleep(700);
  h.onStep({ key: "score", label: "Scoring cause-affinity 0–100", status: "done", detail: "complete" });

  // Final payload
  const ranked = [...data].sort((a, b) => b.affinity_score - a.affinity_score);
  h.onResult(ranked);
  h.onComplete();
}
