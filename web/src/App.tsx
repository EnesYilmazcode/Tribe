import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import AskBox from "./components/AskBox";
import FilterChips from "./components/FilterChips";
import ActivityStream from "./components/ActivityStream";
import ProspectCard from "./components/ProspectCard";
import { runAgent } from "./lib/runStream";
import type { ParsedParams, Prospect, Step } from "./types";

function Wordmark({ className = "" }: { className?: string }) {
  return (
    <span className={`font-serif leading-none text-ink ${className}`}>
      Tribe<span className="text-accent">.</span>
    </span>
  );
}

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
    runAgent(q, {
      onStep: upsertStep,
      onParams: setParams,
      onResult: setProspects,
      onComplete: () => setRunning(false),
    });
  }

  return (
    <div className="flex min-h-screen w-full flex-col px-6">
      <AnimatePresence mode="wait">
        {!started ? (
          /* ── Landing: just the ask ─────────────────────────────── */
          <motion.div
            key="hero"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.4 }}
            className="mx-auto flex w-full max-w-5xl flex-1 flex-col items-center justify-center gap-9 py-16 text-center"
          >
            <Wordmark className="text-2xl" />
            <h1 className="font-serif text-6xl leading-[1.03] text-balance text-ink sm:text-7xl lg:text-[5.5rem]">
              Find the donors who already care<span className="text-accent">.</span>
            </h1>
            <div className="w-full max-w-2xl">
              <AskBox value={ask} onChange={setAsk} onRun={handleRun} running={running} />
            </div>
          </motion.div>
        ) : (
          /* ── Workspace: ask → activity → prospects ─────────────── */
          <motion.div
            key="work"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45, ease: "easeOut" }}
            className="mx-auto flex w-full max-w-4xl flex-1 flex-col gap-6 py-7"
          >
            <header className="flex items-center justify-between">
              <Wordmark className="text-xl" />
              <span className="text-[11px] font-medium uppercase tracking-[0.16em] text-faint">
                ClickHouse · Nimble
              </span>
            </header>

            <div>
              <AskBox
                value={ask}
                onChange={setAsk}
                onRun={handleRun}
                running={running}
                showExamples={false}
              />
              <FilterChips params={params} />
            </div>

            <AnimatePresence>
              {steps.length > 0 && (
                <motion.div
                  key="activity"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4 }}
                >
                  <ActivityStream steps={steps} running={running} />
                </motion.div>
              )}
            </AnimatePresence>

            <AnimatePresence>
              {prospects.length > 0 && (
                <motion.section
                  key="prospects"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4 }}
                  className="flex flex-col gap-3"
                >
                  <div className="flex items-baseline justify-between">
                    <h2 className="text-[11px] font-semibold uppercase tracking-[0.18em] text-faint">
                      Ranked prospects
                    </h2>
                    <span className="text-[13px] tabular-nums text-muted">
                      {prospects.length} found
                    </span>
                  </div>
                  {prospects.map((p, i) => (
                    <ProspectCard key={p.name} prospect={p} rank={i} />
                  ))}
                </motion.section>
              )}
            </AnimatePresence>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
