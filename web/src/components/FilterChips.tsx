import { motion } from "framer-motion";
import type { ParsedParams } from "../types";

export default function FilterChips({ params }: { params: ParsedParams | null }) {
  if (!params) return null;
  const chips = [...params.cause, params.geo, params.min_amount];
  return (
    <motion.div
      initial={{ opacity: 0, y: -4 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-3 flex flex-wrap items-center gap-2"
    >
      <span className="text-[11px] uppercase tracking-widest text-muted/70">parsed</span>
      {chips.map((c) => (
        <span
          key={c}
          className="rounded-full border border-signal/30 bg-signal-dim px-2.5 py-0.5 text-xs text-signal"
        >
          {c}
        </span>
      ))}
    </motion.div>
  );
}
