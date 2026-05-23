import { formatName, scoreColor } from "../lib/format";
import type { Prospect } from "../types";

interface Props {
  prospect: Prospect;
  rank: number;
  selected: boolean;
  onClick: () => void;
}

export default function ProspectRow({ prospect, rank, selected, onClick }: Props) {
  const color = scoreColor(prospect.affinity_score);
  return (
    <button
      onClick={onClick}
      className={`flex w-full items-center gap-3 border-l-2 px-3 py-2.5 text-left transition ${
        selected
          ? "border-accent bg-accent/8"
          : "border-transparent hover:bg-paper"
      }`}
    >
      <span className="w-5 shrink-0 text-xs tabular-nums text-faint">#{rank + 1}</span>
      <div className="min-w-0 flex-1">
        <div className="truncate font-serif text-[17px] leading-tight text-ink">
          {formatName(prospect.name)}
        </div>
        <div className="truncate text-[12px] text-muted">
          {prospect.geo}
          {prospect.cause_tags?.length ? ` · ${prospect.cause_tags[0]}` : ""}
        </div>
      </div>
      <span className="shrink-0 font-serif text-[20px] leading-none" style={{ color }}>
        {prospect.affinity_score}
      </span>
    </button>
  );
}
