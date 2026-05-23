import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Search, Check, Mail } from "lucide-react";

/* A purely decorative, auto-looping preview of a run — hardcoded filler data,
   no backend. Lives on the landing hero to show what Tribe does in action. */

const QUERY = "Wildlife & conservation donors in California, $2,500+";

const STEPS = [
  { lab: "Parsing request", meta: "cause: environment · CA" },
  { lab: "Querying FEC contributions", meta: "1,204 matches · 38ms" },
  { lab: "Enriching via live web", meta: "top 3 profiles" },
  { lab: "Scoring cause-affinity", meta: "ranked 0–100" },
];

const DONORS = [
  { initials: "MH", name: "Marlowe Hart", meta: "Founder, Cedar & Co. · Pasadena, CA", email: "marlowe.hart@cedarco.com", tags: ["environment", "water"], score: 94, give: "$42,000" },
  { initials: "IC", name: "Iris Calderón", meta: "Partner, Brightline Capital · Los Angeles, CA", email: "icalderon@brightlinecap.com", tags: ["environment"], score: 88, give: "$28,500" },
  { initials: "DO", name: "Devin Okafor", meta: "Retired · Santa Monica, CA", email: "devin.okafor47@gmail.com", tags: ["environment", "social welfare"], score: 81, give: "$15,200" },
];

type LogState = "idle" | "running" | "done";

export default function MockPreview() {
  const [log, setLog] = useState<LogState[]>(STEPS.map(() => "idle"));
  const [skeleton, setSkeleton] = useState(false);
  const [revealed, setRevealed] = useState(0);

  useEffect(() => {
    let cancelled = false;
    const sleep = (ms: number) => new Promise<void>((r) => setTimeout(r, ms));
    async function loop() {
      while (!cancelled) {
        setLog(STEPS.map(() => "idle"));
        setSkeleton(false);
        setRevealed(0);
        await sleep(700);
        for (let i = 0; i < STEPS.length && !cancelled; i++) {
          setLog((s) => s.map((v, j) => (j === i ? "running" : v)));
          await sleep(720);
          setLog((s) => s.map((v, j) => (j === i ? "done" : v)));
          await sleep(200);
        }
        if (cancelled) break;
        setSkeleton(true);
        await sleep(850);
        for (let i = 0; i < DONORS.length && !cancelled; i++) {
          setRevealed(i + 1);
          await sleep(380);
        }
        await sleep(4400);
      }
    }
    loop();
    return () => { cancelled = true; };
  }, []);

  return (
    <div className="overflow-hidden rounded-2xl border border-line bg-card shadow-[0_30px_70px_-35px_rgba(27,26,23,0.35)]">
      {/* title bar */}
      <div className="flex items-center gap-2 border-b border-line bg-paper/60 px-4 py-3">
        <span className="h-3 w-3 rounded-full bg-[#ff5f57]" />
        <span className="h-3 w-3 rounded-full bg-[#febc2e]" />
        <span className="h-3 w-3 rounded-full bg-[#28c840]" />
        <span className="ml-2 flex items-center gap-1.5 text-[12px] font-medium tracking-wide text-faint">
          <span className="h-1.5 w-1.5 rounded-full bg-accent soft-pulse" />
          tribe · live agent
        </span>
      </div>

      <div className="p-4">
        {/* query bar */}
        <div className="flex items-center gap-2.5 rounded-xl border border-line bg-paper px-3.5 py-2.5">
          <Search size={15} className="shrink-0 text-faint" strokeWidth={2} />
          <span className="truncate text-[13.5px] text-ink">{QUERY}</span>
        </div>

        {/* streaming log */}
        <div className="mt-4 flex flex-col gap-2.5">
          {STEPS.map((s, i) =>
            log[i] === "idle" ? null : (
              <motion.div
                key={s.lab}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="flex items-center gap-2.5 text-[12.5px]"
              >
                <span className="flex h-4 w-4 shrink-0 items-center justify-center">
                  {log[i] === "running" ? (
                    <span className="spin h-3 w-3 rounded-full border-[1.6px] border-line border-t-accent" />
                  ) : (
                    <Check size={13} className="text-accent" strokeWidth={3} />
                  )}
                </span>
                <span className={log[i] === "done" ? "text-ink" : "text-muted"}>
                  {s.lab}{log[i] === "running" ? "…" : ""}
                </span>
                {log[i] === "done" && (
                  <span className="ml-auto text-[11.5px] text-amber">{s.meta}</span>
                )}
              </motion.div>
            )
          )}
        </div>

        {/* prospect cards */}
        {skeleton && (
          <div className="mt-4 flex flex-col gap-2.5">
            <div className="text-[10.5px] font-semibold uppercase tracking-[0.16em] text-faint">
              your tribe — 3 of 1,204
            </div>
            {DONORS.map((d, i) =>
              i < revealed ? (
                <motion.div
                  key={d.name}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4 }}
                  className="flex items-center gap-3 rounded-xl border border-line bg-card px-3.5 py-2.5"
                >
                  <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-accent font-serif text-[15px] text-white">
                    {d.initials}
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="font-serif text-[15px] leading-tight text-ink">{d.name}</div>
                    <div className="truncate text-[11.5px] text-muted">{d.meta}</div>
                    <div className="mt-0.5 flex items-center gap-1 text-[11px] text-accent">
                      <Mail size={11} strokeWidth={2} className="shrink-0" />
                      <span className="truncate">{d.email}</span>
                    </div>
                    <div className="mt-1 flex gap-1.5">
                      {d.tags.map((t) => (
                        <span key={t} className="rounded-md border border-accent/25 bg-accent/5 px-1.5 py-0.5 text-[9px] uppercase tracking-wide text-accent">
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="shrink-0 text-right">
                    <div className="font-serif text-[22px] leading-none text-accent">{d.score}</div>
                    <div className="text-[8.5px] uppercase tracking-wide text-faint">affinity</div>
                    <div className="mt-0.5 text-[11px] text-amber">{d.give}</div>
                  </div>
                </motion.div>
              ) : (
                <div key={d.name} className="flex items-center gap-3 rounded-xl border border-line bg-card px-3.5 py-2.5">
                  <span className="h-9 w-9 shrink-0 rounded-lg bg-line soft-pulse" />
                  <div className="flex-1">
                    <div className="h-3 w-32 rounded bg-line soft-pulse" />
                    <div className="mt-2 h-2.5 w-44 rounded bg-line soft-pulse" />
                  </div>
                </div>
              )
            )}
          </div>
        )}
      </div>
    </div>
  );
}
