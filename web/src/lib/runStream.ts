import type { Prospect, StreamHandlers } from "../types";
import prospects from "../../sample_prospects.json";

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

const data = prospects as unknown as Prospect[];

/**
 * Mock run of the agent pipeline. Emits the same step/param/result shape that
 * the real SSE backend will (Phase B), so the UI never has to branch.
 * Drives the demo entirely from `sample_prospects.json`.
 */
export async function runMockStream(ask: string, h: StreamHandlers): Promise<void> {
  // 1. Parse the request
  h.onStep({ key: "parse", label: "Parsing request", status: "running", detail: `"${ask}"` });
  await sleep(700);
  const params = { cause: ["water", "environment"], geo: "WA · OR", min_amount: "$1,000+" };
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
    detail: "1,204 matching contributions · 38ms",
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
      detail: `→ ${p.name} (${p.geo})`,
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
  h.onStep({
    key: "score",
    label: "Scoring cause-affinity 0–100",
    status: "done",
    detail: "complete",
  });

  // Final payload
  const ranked = [...data].sort((a, b) => b.affinity_score - a.affinity_score);
  h.onResult(ranked);
  h.onComplete();
}
