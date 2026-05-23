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
      className="inline-flex items-center gap-1 rounded border border-line px-1.5 py-0.5 text-[10px] text-muted transition hover:border-signal/50 hover:text-signal"
    >
      {hostname(url)}
      <ExternalLink size={9} />
    </a>
  );
}

function scoreColor(n: number): string {
  if (n >= 80) return "var(--color-signal)";
  if (n >= 70) return "var(--color-amber)";
  return "var(--color-rust)";
}

export default function ProspectCard({ prospect, rank }: { prospect: Prospect; rank: number }) {
  const color = scoreColor(prospect.affinity_score);
  return (
    <motion.article
      layout
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: rank * 0.06 }}
      className="rounded-lg border border-line bg-panel/60 p-4 transition-colors hover:border-line/80 hover:bg-panel-2/60"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="flex items-baseline gap-2">
            <span className="text-xs tabular-nums text-muted/50">#{rank + 1}</span>
            <h3 className="font-serif text-2xl leading-tight text-ink">{prospect.name}</h3>
          </div>
          <div className="mt-1 flex flex-wrap items-center gap-1.5 text-xs text-muted">
            <span>{prospect.geo}</span>
            <span className="text-muted/30">·</span>
            {prospect.cause_tags.map((t) => (
              <span key={t} className="rounded-full bg-panel-2 px-2 py-0.5 text-[11px] text-muted">
                {t}
              </span>
            ))}
          </div>
        </div>
        <div className="shrink-0 text-right">
          <div className="font-serif text-4xl leading-none" style={{ color }}>
            {prospect.affinity_score}
          </div>
          <div className="text-[10px] uppercase tracking-widest text-muted/60">affinity</div>
        </div>
      </div>

      <ul className="mt-3.5 space-y-2 border-t border-line/60 pt-3">
        {prospect.cited_reasons.map((c, i) => (
          <li key={i} className="flex flex-wrap items-start gap-x-2 gap-y-1 text-[13px] leading-snug text-ink/90">
            <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-signal/70" />
            <span className="min-w-0 flex-1">{c.text}</span>
            <SourcePill url={c.source_url} />
          </li>
        ))}
      </ul>

      {prospect.enrichment && (
        <div className="mt-3 flex flex-wrap items-center gap-x-2 gap-y-1 rounded-md bg-panel-2/70 px-3 py-2 text-[13px] text-ink/90">
          <span className="inline-flex items-center gap-1 rounded bg-signal-dim px-1.5 py-0.5 text-[10px] uppercase tracking-wider text-signal">
            <Globe size={9} /> live web
          </span>
          <span className="min-w-0 flex-1">
            {prospect.enrichment.current_role}
            {prospect.enrichment.notes && (
              <span className="text-muted"> — {prospect.enrichment.notes}</span>
            )}
          </span>
          <SourcePill url={prospect.enrichment.source_url} />
        </div>
      )}
    </motion.article>
  );
}
