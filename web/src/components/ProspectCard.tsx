import { useState } from "react";
import { motion } from "framer-motion";
import { ChevronDown, ExternalLink, Globe } from "lucide-react";
import type { Prospect } from "../types";

function hostname(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return "source";
  }
}

function usd(n: number): string {
  return "$" + n.toLocaleString("en-US");
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

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div className="flex flex-col">
      <span className="font-medium tabular-nums text-ink">{value}</span>
      <span className="text-[11px] uppercase tracking-wider text-faint">{label}</span>
    </div>
  );
}

export default function ProspectCard({ prospect, rank }: { prospect: Prospect; rank: number }) {
  const [showHistory, setShowHistory] = useState(false);
  const p = prospect;
  const color = scoreColor(p.affinity_score);
  const role = [p.occupation, p.employer].filter(Boolean).join(" at ");
  const place = [p.city, p.geo].filter(Boolean).join(", ");
  const years =
    p.first_gift_year && p.last_gift_year
      ? p.first_gift_year === p.last_gift_year
        ? `${p.first_gift_year}`
        : `${p.first_gift_year}–${p.last_gift_year}`
      : null;
  const history = p.donation_history ?? [];

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
            <h3 className="font-serif text-[26px] leading-tight text-ink">{p.name}</h3>
          </div>
          <div className="mt-1 text-[13px] text-muted">
            {place}
            {role && place ? " · " : ""}
            {role}
          </div>
          <div className="mt-1.5 flex flex-wrap items-center gap-1.5">
            {p.cause_tags.map((t) => (
              <span key={t} className="rounded-full bg-paper px-2 py-0.5 text-[12px] text-muted">
                {t}
              </span>
            ))}
          </div>
        </div>
        <div className="shrink-0 text-right">
          <div className="font-serif text-[40px] leading-none" style={{ color }}>
            {p.affinity_score}
          </div>
          <div className="text-[10px] font-medium uppercase tracking-widest text-faint">affinity</div>
        </div>
      </div>

      {/* Giving stats */}
      {(p.total_given || p.num_donations) && (
        <div className="mt-4 flex flex-wrap gap-x-8 gap-y-2 rounded-xl bg-paper px-4 py-3 text-[15px]">
          {p.total_given != null && <Stat value={usd(p.total_given)} label="total given" />}
          {p.num_donations != null && <Stat value={String(p.num_donations)} label="donations" />}
          {years && <Stat value={years} label="years active" />}
        </div>
      )}

      <ul className="mt-4 space-y-2.5 border-t border-line pt-4">
        {p.cited_reasons.map((c, i) => (
          <li key={i} className="flex flex-wrap items-start gap-x-2 gap-y-1 text-[14px] leading-snug text-ink/90">
            <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-accent" />
            <span className="min-w-0 flex-1">{c.text}</span>
            <SourcePill url={c.source_url} />
          </li>
        ))}
      </ul>

      {p.enrichment && (
        <div className="mt-3 flex flex-wrap items-center gap-x-2 gap-y-1 rounded-xl bg-accent/6 px-3 py-2.5 text-[14px] text-ink/90">
          <span className="inline-flex items-center gap-1 rounded-md bg-accent/12 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-accent">
            <Globe size={10} /> live web
          </span>
          <span className="min-w-0 flex-1">
            {p.enrichment.current_role}
            {p.enrichment.notes && <span className="text-muted"> — {p.enrichment.notes}</span>}
          </span>
          <SourcePill url={p.enrichment.source_url} />
        </div>
      )}

      {/* Donation history (collapsible) */}
      {history.length > 0 && (
        <div className="mt-3">
          <button
            onClick={() => setShowHistory((s) => !s)}
            className="flex items-center gap-1 text-[13px] font-medium text-muted transition hover:text-accent"
          >
            <ChevronDown
              size={14}
              className={`transition-transform ${showHistory ? "rotate-180" : ""}`}
            />
            {showHistory ? "Hide" : "View"} giving history
          </button>
          {showHistory && (
            <motion.ul
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              className="mt-2 divide-y divide-line overflow-hidden rounded-lg border border-line"
            >
              {history.map((d, i) => (
                <li key={i} className="flex items-center justify-between gap-3 px-3 py-2 text-[13px]">
                  <span className="w-20 shrink-0 tabular-nums text-faint">{d.date}</span>
                  <span className="min-w-0 flex-1 truncate text-ink/85">{d.committee_name}</span>
                  <span className="shrink-0 font-medium tabular-nums text-ink">{usd(d.amount)}</span>
                </li>
              ))}
            </motion.ul>
          )}
        </div>
      )}
    </motion.article>
  );
}
