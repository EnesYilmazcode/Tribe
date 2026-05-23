export interface Citation {
  text: string;
  source_url: string;
}

export interface Enrichment {
  current_role: string;
  notes: string | null;
  source_url: string;
}

export interface DonationItem {
  date: string;
  amount: number;
  committee_id: string;
  committee_name: string;
  cause_tags: string[];
}

export interface Prospect {
  name: string;
  affinity_score: number;
  cause_tags: string[];
  geo: string;
  cited_reasons: Citation[];
  enrichment: Enrichment | null;
  // Rich fields from clickhouse_client.query() — optional so mocks/partials still type-check.
  city?: string;
  employer?: string;
  occupation?: string;
  email?: string;
  total_given?: number;
  num_donations?: number;
  first_gift_year?: number;
  last_gift_year?: number;
  donation_history?: DonationItem[];
  draft_email?: { subject: string; body: string } | null;
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
