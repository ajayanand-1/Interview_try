import {
  EvaluationSummary,
  RosettaDocument,
  AgentMemo,
  DebateTranscript,
  FinalDecision,
  CandidateFeedback,
  ReportSummary,
  EvaluationStatusType,
  EvaluationPhaseType,
} from '../types/api';

// In development, default to http://127.0.0.1:8000; in production (unified server), default to '' (same-origin)
const rawBase = import.meta.env.VITE_API_BASE_URL;
const API_BASE = (
  rawBase !== undefined && rawBase !== ''
    ? rawBase
    : import.meta.env.DEV
    ? 'http://127.0.0.1:8000'
    : ''
).replace(/\/$/, '');

export class ApiError extends Error {
  status: number;
  data: any;
  constructor(message: string, status: number, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${path.startsWith('/') ? path : `/${path}`}`;
  try {
    const res = await fetch(url, options);
    if (!res.ok) {
      let errData;
      try {
        errData = await res.json();
      } catch {
        errData = { detail: res.statusText };
      }
      throw new ApiError(errData?.detail || `API error ${res.status}: ${res.statusText}`, res.status, errData);
    }
    return (await res.json()) as T;
  } catch (err: any) {
    if (err instanceof ApiError) throw err;
    throw new ApiError(err?.message || 'Network connection to backend failed', 0);
  }
}

export const api = {
  getHealth: () => request<{ status: string; service: string; version: string }>('/api/health'),

  getEvaluations: () => request<EvaluationSummary[]>('/api/evaluations'),

  getEvaluationMetadata: (runId: string) => request<EvaluationSummary>(`/api/evaluations/${runId}`),

  getEvaluationStatus: (runId: string) =>
    request<{
      run_id: string;
      status: EvaluationStatusType;
      phase: EvaluationPhaseType;
      error?: string | null;
      updated_at: string;
    }>(`/api/evaluations/${runId}/status`),

  getRosetta: (runId: string) => request<RosettaDocument>(`/api/evaluations/${runId}/rosetta`),

  getMemos: (runId: string) => request<Record<string, AgentMemo>>(`/api/evaluations/${runId}/memos`),

  getDebate: (runId: string) => request<DebateTranscript>(`/api/evaluations/${runId}/debate`),

  getDecision: (runId: string) => request<FinalDecision>(`/api/evaluations/${runId}/decision`),

  getFeedback: (runId: string) => request<CandidateFeedback>(`/api/evaluations/${runId}/feedback`),

  getReport: (runId: string) => request<ReportSummary>(`/api/evaluations/${runId}/report`),

  getReportPdfUrl: (runId: string) => `${API_BASE}/api/evaluations/${runId}/report/pdf`,

  getCandidates: () =>
    request<
      Array<{
        candidate_id: string;
        candidate_name: string;
        evaluations_count: number;
        latest_status: string;
        latest_run_id: string;
        latest_job_id: string;
        latest_date: string;
        runs: EvaluationSummary[];
      }>
    >('/api/candidates'),

  getJobs: () =>
    request<
      Array<{
        job_id: string;
        job_title: string;
        evaluations_count: number;
        candidates: string[];
        runs: EvaluationSummary[];
      }>
    >('/api/jobs'),

  getJobCandidatesComparison: (jobId: string) =>
    request<{
      job_id: string;
      job_title: string;
      total_candidates: number;
      candidates: Array<{
        run_id: string;
        candidate_id: string;
        candidate_name: string;
        status: string;
        phase: string;
        created_at: string;
        recommendation?: string | null;
        confidence?: string | null;
        strengths_count: number;
        concerns_count: number;
        scores: Record<string, number | null>;
      }>;
    }>(`/api/jobs/${jobId}/candidates`),

  createEvaluation: async (formData: FormData): Promise<EvaluationSummary> => {
    return request<EvaluationSummary>('/api/evaluations', {
      method: 'POST',
      body: formData,
    });
  },
};
