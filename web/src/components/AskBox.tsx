import { ArrowRight } from "lucide-react";

const EXAMPLES = [
  "Major clean-water donors in the Pacific Northwest",
  "Climate givers in California who gave $500+",
  "Environment + conservation supporters in Oregon",
];

interface Props {
  value: string;
  onChange: (v: string) => void;
  onRun: (override?: string) => void;
  running: boolean;
}

export default function AskBox({ value, onChange, onRun, running }: Props) {
  return (
    <div className="w-full">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (value.trim() && !running) onRun();
        }}
        className="group flex items-center gap-3 rounded-lg border border-line bg-panel/70 px-4 py-3.5 backdrop-blur transition-colors focus-within:border-signal/60"
      >
        <span className="select-none text-signal">tribe&nbsp;❯</span>
        <input
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={running}
          placeholder="Describe who you're raising for…"
          className="min-w-0 flex-1 bg-transparent text-ink placeholder:text-muted/60 outline-none disabled:opacity-60"
          autoFocus
        />
        <button
          type="submit"
          disabled={running || !value.trim()}
          className="flex shrink-0 items-center gap-1.5 rounded-md bg-signal px-3.5 py-1.5 text-xs font-semibold uppercase tracking-wider text-void transition disabled:cursor-not-allowed disabled:opacity-30 hover:brightness-110"
        >
          {running ? "Running" : "Run"}
          {!running && <ArrowRight size={13} strokeWidth={2.5} />}
        </button>
      </form>

      <div className="mt-2.5 flex flex-wrap gap-2">
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
            className="rounded-full border border-line px-3 py-1 text-xs text-muted transition hover:border-signal/50 hover:text-ink disabled:opacity-40"
          >
            {ex}
          </button>
        ))}
      </div>
    </div>
  );
}
