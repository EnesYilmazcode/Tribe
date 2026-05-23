export interface Citation {
  text: string;
  source_url: string;
}

export interface Enrichment {
  current_role: string;
  notes: string | null;
  source_url: string;
}

export interface Prospect {
  name: string;
  affinity_score: number;
  cause_tags: string[];
  geo: string;
  cited_reasons: Citation[];
  enrichment: Enrichment | null;
}

export interface ParsedParams {
  cause: string[];
  geo: string;
  min_amount: string;
}

export type StepStatus = "running" | "done";

export interface Step {
  key: string;
  label: string;
  detail?: string;
  status: StepStatus;
}

export interface StreamHandlers {
  onStep: (step: Step) => void;
  onParams: (params: ParsedParams) => void;
  onResult: (prospects: Prospect[]) => void;
  onComplete: () => void;
}
