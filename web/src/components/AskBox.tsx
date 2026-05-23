import { ArrowRight, Search } from "lucide-react";

const EXAMPLES = [
  "Major clean-water donors in the Pacific Northwest",
  "Climate givers in California who gave $500+",
  "Environment supporters in Oregon",
];

interface Props {
  value: string;
  onChange: (v: string) => void;
  onRun: (override?: string) => void;
  running: boolean;
  showExamples?: boolean;
}

export default function AskBox({ value, onChange, onRun, running, showExamples = true }: Props) {
  return (
    <div className="w-full">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (value.trim() && !running) onRun();
        }}
        className="flex items-center gap-3 rounded-2xl border border-line bg-card px-4 py-3 shadow-sm transition focus-within:border-accent/50 focus-within:shadow-md"
      >
        <Search size={18} className="shrink-0 text-faint" strokeWidth={2} />
        <input
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={running}
          placeholder="Describe who you're raising for…"
          className="min-w-0 flex-1 bg-transparent text-ink placeholder:text-faint outline-none disabled:opacity-60"
          autoFocus
        />
        <button
          type="submit"
          disabled={running || !value.trim()}
          className="flex shrink-0 items-center gap-1.5 rounded-xl bg-accent px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:brightness-105 disabled:cursor-not-allowed disabled:opacity-30"
        >
          {running ? "Running…" : "Find prospects"}
          {!running && <ArrowRight size={15} strokeWidth={2.5} />}
        </button>
      </form>

      {showExamples && (
        <div className="mt-3 flex flex-wrap justify-center gap-2">
          {EXAMPLES.map((ex) => (
            <button
              key={ex}
              onClick={() => {
                if (!running) {
                  onChange(ex);
                  onRun(ex);
                }
              }}
              disabled={running}
              className="rounded-full border border-line bg-card px-3.5 py-1.5 text-[13px] text-muted transition hover:border-accent/40 hover:text-accent disabled:opacity-40"
            >
              {ex}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
