export type EvaluationStatusType = 'queued' | 'running' | 'completed' | 'failed' | 'unknown';
export type EvaluationPhaseType = 'ingestion' | 'rosetta' | 'agents' | 'debate' | 'decision' | 'report' | 'finalized' | 'error' | 'unknown';

export interface EvaluationSummary {
  run_id: string;
  candidate_id: string;
  candidate_name: string;
  job_id: string;
  status: EvaluationStatusType;
  phase: EvaluationPhaseType;
  error?: string | null;
  created_at: string;
  updated_at: string;
}

export interface EvidenceItem {
  claim: string;
  citation_id: string;
}

export interface AgentMemo {
  persona: string;
  candidate_id: string;
  score: number | null;
  confidence: string;
  verdict_summary: string;
  strengths: EvidenceItem[];
  gaps: EvidenceItem[];
  insufficient_evidence_items?: string[];
  contrarian_argument?: string | null;
  created_at: string;
}

export interface DebateTurn {
  persona: string;
  statement: string;
  cites: string[];
  responds_to?: string | null;
  is_counter_question_response?: boolean;
}

export interface DebateRound {
  round_num: number;
  agenda_item: string;
  turns: DebateTurn[];
  votes: Record<string, number>;
  score_deltas_from_previous_round?: Record<string, string>;
  auto_resolve_triggered?: string | null;
}

export interface DebateTranscript {
  candidate_id: string;
  candidate_name: string;
  agenda: string[];
  rounds: DebateRound[];
  maturity_reached: boolean;
  total_rounds: number;
  finalized_at: string;
}

export interface OverrideMotion {
  filed_by: string;
  motion_text: string;
  proposed_decision: string;
  votes: Record<string, string>;
  support_count: number;
  passed: boolean;
  rationale: string;
}

export interface FinalDecisionPath {
  auto_resolved: boolean;
  auto_resolve_reason?: string | null;
  original_gs_decision: string;
  original_gs_confidence: string;
  original_gs_rationale: string;
  override_motion_filed: boolean;
  override_motion?: OverrideMotion | null;
  final_decision_after_overrides: string;
  final_confidence: string;
}

export interface FinalDecision {
  candidate_id: string;
  candidate_name: string;
  final_recommendation: 'hire' | 'no_hire' | 'auto_hire' | 'auto_reject';
  confidence_level: 'low' | 'medium' | 'high';
  strengths: EvidenceItem[];
  concerns: EvidenceItem[];
  unresolved_disagreements?: Array<{
    topic: string;
    positions: Record<string, string>;
  }>;
  decision_path: FinalDecisionPath;
  generated_at: string;
}

export interface RosettaDocument {
  candidate_id: string;
  candidate_name: string;
  job_title: string;
  resume_facts: {
    education: Array<{ degree: string; institution?: string; year?: number; citation_id: string }>;
    experience: Array<{ company: string; role: string; start: string; end: string; tenure_years: number; claims: Array<{ text: string; citation_id: string }> }>;
    skills: string[];
    certifications?: string[];
  };
  transcript_facts: {
    technical_qa: Array<{ qid: string; topic: string; question: string; answer: string; answer_citation_id: string; self_disclosed_gap?: boolean }>;
    behavioral: {
      friction_event_citation_id?: string;
      friction_event_quote?: string;
      skeptic_followup_citation_id?: string;
      skeptic_followup_quote?: string;
      skeptic_followup_word_count?: number;
      skeptic_followup_defensiveness?: string;
      friction_notes?: string;
    };
    ownership_hiring_qa: Array<{ qid: string; gap_probed: string; response_summary: string; response_quote?: string; response_style?: string; citation_id: string }>;
  };
  consistency_flags: Array<{ claim_citation_id: string; transcript_citation_id: string; description: string; severity: string }>;
  citations_index: Record<string, string>;
}

export interface ReportSummary {
  run_id: string;
  candidate_id: string;
  candidate_name: string;
  decision: FinalDecision;
  pdf_download_url: string;
  has_pdf: boolean;
  has_markdown: boolean;
}
