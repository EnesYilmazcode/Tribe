import { motion } from "framer-motion";
import { ExternalLink, Globe } from "lucide-react";
import type { Prospect } from "../types";

function hostname(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return "source";
  }
}

function SourcePill({ url }: { url: string }) {
  return (
    <a
      href={url}
      target="_blank"
      rel="noreferrer"
      className="inline-flex items-center gap-1 rounded-md border border-line bg-paper px-1.5 py-0.5 text-[11px] text-muted transition hover:border-accent/40 hover:text-accent"
    >
      {hostname(url)}
      <ExternalLink size={10} />
    </a>
  );
}

function scoreColor(n: number): string {
  if (n >= 80) return "var(--color-accent)";
  if (n >= 70) return "var(--color-amber)";
  return "var(--color-faint)";
}

export default function ProspectCard({ prospect, rank }: { prospect: Prospect; rank: number }) {
  const color = scoreColor(prospect.affinity_score);
  return (
    <motion.article
      layout
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: rank * 0.07, ease: "easeOut" }}
      className="rounded-2xl border border-line bg-card p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="flex items-baseline gap-2">
            <span className="text-xs font-medium tabular-nums text-faint">#{rank + 1}</span>
            <h3 className="font-serif text-[26px] leading-tight text-ink">{prospect.name}</h3>
          </div>
          <div className="mt-1.5 flex flex-wrap items-center gap-1.5 text-[13px] text-muted">
            <span>{prospect.geo}</span>
            <span className="text-faint">·</span>
            {prospect.cause_tags.map((t) => (
              <span key={t} className="rounded-full bg-paper px-2 py-0.5 text-[12px] text-muted">
                {t}
              </span>
            ))}
          </div>
        </div>
        <div className="shrink-0 text-right">
          <div className="font-serif text-[40px] leading-none" style={{ color }}>
            {prospect.affinity_score}
          </div>
          <div className="text-[10px] font-medium uppercase tracking-widest text-faint">affinity</div>
        </div>
      </div>

      <ul className="mt-4 space-y-2.5 border-t border-line pt-4">
        {prospect.cited_reasons.map((c, i) => (
          <li key={i} className="flex flex-wrap items-start gap-x-2 gap-y-1 text-[14px] leading-snug text-ink/90">
            <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-accent" />
            <span className="min-w-0 flex-1">{c.text}</span>
            <SourcePill url={c.source_url} />
          </li>
        ))}
      </ul>

      {prospect.enrichment && (
        <div className="mt-3 flex flex-wrap items-center gap-x-2 gap-y-1 rounded-xl bg-accent/6 px-3 py-2.5 text-[14px] text-ink/90">
          <span className="inline-flex items-center gap-1 rounded-md bg-accent/12 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-accent">
            <Globe size={10} /> live web
          </span>
          <span className="min-w-0 flex-1">
            {prospect.enrichment.current_role}
            {prospect.enrichment.notes && <span className="text-muted"> — {prospect.enrichment.notes}</span>}
          </span>
          <SourcePill url={prospect.enrichment.source_url} />
        </div>
      )}
    </motion.article>
  );
}
