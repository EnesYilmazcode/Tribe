import { useState } from "react";
import AskBox from "./components/AskBox";
import FilterChips from "./components/FilterChips";
import ActivityStream from "./components/ActivityStream";
import ProspectCard from "./components/ProspectCard";
import { runMockStream } from "./lib/runStream";
import type { ParsedParams, Prospect, Step } from "./types";

export default function App() {
  const [ask, setAsk] = useState("");
  const [steps, setSteps] = useState<Step[]>([]);
  const [params, setParams] = useState<ParsedParams | null>(null);
  const [prospects, setProspects] = useState<Prospect[]>([]);
  const [running, setRunning] = useState(false);
  const [started, setStarted] = useState(false);

  function upsertStep(step: Step) {
    setSteps((prev) => {
      const idx = prev.findIndex((s) => s.key === step.key);
      if (idx >= 0) {
        const next = [...prev];
        next[idx] = step;
        return next;
      }
      return [...prev, step];
    });
  }

  function handleRun(override?: string) {
    const q = (override ?? ask).trim();
    if (!q || running) return;
    setAsk(q);
    setSteps([]);
    setParams(null);
    setProspects([]);
    setStarted(true);
    setRunning(true);
    runMockStream(q, {
      onStep: upsertStep,
      onParams: setParams,
      onResult: setProspects,
      onComplete: () => setRunning(false),
    });
  }

  return (
    <div className="mx-auto flex min-h-full max-w-6xl flex-col px-5 py-6 sm:px-8">
      {/* Header */}
      <header className="mb-6 flex items-end justify-between border-b border-line pb-4">
        <div>
          <h1 className="font-serif text-3xl leading-none text-ink">
            Tribe<span className="text-signal">.</span>
          </h1>
          <p className="mt-1 text-xs tracking-wide text-muted">
            autonomous donor-prospecting agent · cited from public FEC records
          </p>
        </div>
        <div className="hidden text-right text-[11px] uppercase tracking-widest text-muted/70 sm:block">
          <div>ClickHouse · Nimble</div>
          <div className="text-muted/40">real-time open web</div>
        </div>
      </header>

      {/* Ask */}
      <section className="mb-6">
        <AskBox value={ask} onChange={setAsk} onRun={handleRun} running={running} />
        <FilterChips params={params} />
      </section>

      {/* Two-pane console */}
      <section className="grid flex-1 grid-cols-1 gap-5 lg:h-[68vh] lg:grid-cols-[minmax(0,0.62fr)_minmax(0,1fr)]">
        <div className="h-[42vh] lg:h-full">
          <ActivityStream steps={steps} running={running} started={started} />
        </div>

        <div className="flex h-full flex-col overflow-hidden">
          <div className="mb-3 flex items-baseline justify-between">
            <span className="text-[11px] uppercase tracking-[0.2em] text-muted">
              Ranked prospects
            </span>
            {prospects.length > 0 && (
              <span className="text-xs tabular-nums text-muted/60">{prospects.length} found</span>
            )}
          </div>

          {prospects.length === 0 ? (
            <div className="flex flex-1 items-center justify-center rounded-lg border border-dashed border-line/70 px-6 py-16 text-center text-sm text-muted/60">
              {started ? "Researching candidates…" : "Ranked, cited prospects will appear here."}
            </div>
          ) : (
            <div className="flex-1 space-y-3 overflow-y-auto pr-1">
              {prospects.map((p, i) => (
                <ProspectCard key={p.name} prospect={p} rank={i} />
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
