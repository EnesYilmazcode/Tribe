import { AnimatePresence, motion } from "framer-motion";
import { Check, Loader2 } from "lucide-react";
import type { Step } from "../types";

function StepRow({ step, last }: { step: Step; last: boolean }) {
  const running = step.status === "running";
  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className="relative flex gap-3.5"
    >
      {/* node + connector */}
      <div className="relative flex flex-col items-center">
        {running ? (
          <span className="z-10 flex h-6 w-6 items-center justify-center rounded-full border border-accent/30 bg-accent/8 text-accent">
            <Loader2 size={13} className="spin" strokeWidth={2.5} />
          </span>
        ) : (
          <span className="z-10 flex h-6 w-6 items-center justify-center rounded-full bg-accent text-white">
            <Check size={13} strokeWidth={3} />
          </span>
        )}
        {!last && <span className="w-px flex-1 bg-line" />}
      </div>

      {/* label + detail */}
      <div className="min-w-0 flex-1 pb-5">
        <div className={`text-[15px] font-medium ${running ? "text-ink" : "text-ink/80"}`}>
          {step.label}
        </div>
        <AnimatePresence mode="popLayout">
          {step.detail && (
            <motion.div
              key={step.detail}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className={`mt-0.5 truncate text-[13px] ${running ? "text-accent" : "text-muted"}`}
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
}

export default function ActivityStream({ steps, running }: Props) {
  return (
    <div className="rounded-2xl border border-line bg-card p-5 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <span className="text-[11px] font-semibold uppercase tracking-[0.18em] text-faint">
          Agent activity
        </span>
        <span className="flex items-center gap-1.5 text-[12px] font-medium">
          {running ? (
            <>
              <span className="soft-pulse h-2 w-2 rounded-full bg-accent" />
              <span className="text-accent">working</span>
            </>
          ) : (
            <>
              <Check size={13} className="text-accent" strokeWidth={3} />
              <span className="text-muted">complete</span>
            </>
          )}
        </span>
      </div>

      <div className="flex flex-col">
        {steps.map((s, i) => (
          <StepRow key={s.key} step={s} last={i === steps.length - 1} />
        ))}
      </div>
    </div>
  );
}
