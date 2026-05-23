import { motion } from "framer-motion";
import type { ParsedParams } from "../types";

export default function FilterChips({ params }: { params: ParsedParams | null }) {
  if (!params) return null;
  const chips = [...params.cause, params.geo, params.min_amount];
  return (
    <motion.div
      initial={{ opacity: 0, y: -4 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-3 flex flex-wrap items-center justify-center gap-2"
    >
      <span className="text-[11px] font-medium uppercase tracking-widest text-faint">parsed</span>
      {chips.map((c) => (
        <span
          key={c}
          className="rounded-full border border-accent/25 bg-accent/8 px-3 py-1 text-[13px] font-medium text-accent"
        >
          {c}
        </span>
      ))}
    </motion.div>
  );
}
