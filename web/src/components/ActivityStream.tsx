import { AnimatePresence, motion } from "framer-motion";
import { Check } from "lucide-react";
import type { Step } from "../types";

function StepRow({ step, index }: { step: Step; index: number }) {
  const running = step.status === "running";
  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: -6 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.25 }}
      className="flex gap-3 px-4 py-2.5"
    >
      <div className="mt-0.5 shrink-0">
        {running ? (
          <span className="pulse block h-3.5 w-3.5 rounded-full border border-signal bg-signal-dim" />
        ) : (
          <span className="flex h-3.5 w-3.5 items-center justify-center rounded-full bg-signal text-void">
            <Check size={10} strokeWidth={3} />
          </span>
        )}
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-baseline gap-2">
          <span className="text-[10px] tabular-nums text-muted/50">{String(index + 1).padStart(2, "0")}</span>
          <span className={running ? "text-ink" : "text-muted"}>{step.label}</span>
        </div>
        <AnimatePresence mode="popLayout">
          {step.detail && (
            <motion.div
              key={step.detail}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className={`mt-0.5 truncate pl-6 text-xs ${running ? "text-signal/90" : "text-muted/70"}`}
            >
              {step.detail}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}

interface Props {
  steps: Step[];
  running: boolean;
  started: boolean;
}

export default function ActivityStream({ steps, running, started }: Props) {
  return (
    <div className="flex h-full flex-col overflow-hidden rounded-lg border border-line bg-panel/50">
      <div className="flex items-center justify-between border-b border-line px-4 py-2.5">
        <span className="text-[11px] uppercase tracking-[0.2em] text-muted">Agent activity</span>
        <span
          className={`h-2 w-2 rounded-full ${
            running ? "bg-signal pulse" : started ? "bg-signal" : "bg-muted/40"
          }`}
        />
      </div>

      <div className="flex-1 divide-y divide-line/60 overflow-y-auto">
        {!started ? (
          <div className="flex h-full items-center justify-center px-6 py-16 text-center text-sm text-muted/60">
            Awaiting a request. The agent's reasoning will stream here.
          </div>
        ) : (
          <>
            {steps.map((s, i) => (
              <StepRow key={s.key} step={s} index={i} />
            ))}
            {running && (
              <div className="px-4 py-2.5 pl-[2.6rem] text-xs text-muted/70">
                <span className="cursor" />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
