import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import AskBox from "./components/AskBox";
import FilterChips from "./components/FilterChips";
import ActivityStream from "./components/ActivityStream";
import ProspectCard from "./components/ProspectCard";
import { runMockStream } from "./lib/runStream";
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
    runMockStream(q, {
      onStep: upsertStep,
      onParams: setParams,
      onResult: setProspects,
      onComplete: () => setRunning(false),
    });
  }

  return (
    <div className="mx-auto flex min-h-screen w-full max-w-3xl flex-col px-5">
      <AnimatePresence mode="wait">
        {!started ? (
          /* ── Landing: just the ask ─────────────────────────────── */
          <motion.div
            key="hero"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.4 }}
            className="flex flex-1 flex-col items-center justify-center gap-7 py-16 text-center"
          >
            <Wordmark className="text-2xl" />
            <div className="space-y-3">
              <h1 className="font-serif text-5xl leading-[1.05] text-ink sm:text-6xl">
                Find the donors who
                <br />
                already care<span className="text-accent">.</span>
              </h1>
              <p className="mx-auto max-w-lg text-[15px] text-muted">
                Describe your cause. Tribe reads millions of real public giving records and
                surfaces your best prospects — each one cited.
              </p>
            </div>
            <div className="w-full max-w-xl">
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
            className="flex flex-1 flex-col gap-6 py-7"
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
