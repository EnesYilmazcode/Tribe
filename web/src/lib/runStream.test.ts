import { describe, it, expect, vi } from "vitest";
import { runMockStream } from "./runStream";
import type { ParsedParams, Prospect, Step } from "../types";

describe("runMockStream", () => {
  it("emits the full pipeline and ranked, complete results", async () => {
    vi.useFakeTimers();

    const steps: Step[] = [];
    let params: ParsedParams | null = null;
    let result: Prospect[] = [];
    let completed = false;

    const promise = runMockStream("clean water donors in WA", {
      onStep: (s) => steps.push(s),
      onParams: (p) => (params = p),
      onResult: (r) => (result = r),
      onComplete: () => (completed = true),
    });

    await vi.runAllTimersAsync();
    await promise;
    vi.useRealTimers();

    // every pipeline phase fired, each reaching "done"
    const doneKeys = steps.filter((s) => s.status === "done").map((s) => s.key);
    for (const key of ["parse", "query", "rank", "enrich", "score"]) {
      expect(doneKeys).toContain(key);
    }

    expect(params).not.toBeNull();
    expect(completed).toBe(true);
    expect(result.length).toBeGreaterThan(0);

    // results are sorted by affinity_score descending
    const scores = result.map((p) => p.affinity_score);
    expect(scores).toEqual([...scores].sort((a, b) => b - a));
  });
});
