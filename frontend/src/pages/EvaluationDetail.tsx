import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  FileCheck,
  Download,
  RefreshCw,
  AlertCircle,
  Clock,
  Layers,
  BookOpen,
  MessageSquare,
  Scale,
  Award,
  ArrowLeft,
  ChevronRight,
  ShieldAlert,
  GitCommit,
  TrendingUp,
  UserCheck,
  UserX,
  HelpCircle,
  ArrowRight,
  CheckCircle2,
  XCircle,
} from 'lucide-react';
import { api } from '../api/client';
import {
  EvaluationSummary,
  RosettaDocument,
  AgentMemo,
  DebateTranscript,
  FinalDecision,
} from '../types/api';
import { StatusBadge } from '../components/common/StatusBadge';
import { CitationBadge } from '../components/common/CitationBadge';
import { CitationModal } from '../components/common/CitationModal';

type TabType = 'overview' | 'rosetta' | 'memos' | 'debate' | 'decision_path';

export const EvaluationDetail: React.FC = () => {
  const { run_id } = useParams<{ run_id: string }>();

  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [meta, setMeta] = useState<EvaluationSummary | null>(null);
  const [decision, setDecision] = useState<FinalDecision | null>(null);
  const [rosetta, setRosetta] = useState<RosettaDocument | null>(null);
  const [memos, setMemos] = useState<Record<string, AgentMemo> | null>(null);
  const [debate, setDebate] = useState<DebateTranscript | null>(null);

  // Evidence Explorer Modal state
  const [selectedCitationId, setSelectedCitationId] = useState<string | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadRunData = async () => {
    if (!run_id) return;
    try {
      setLoading(true);
      const metadata = await api.getEvaluationMetadata(run_id);
      setMeta(metadata);

      try {
        const dec = await api.getDecision(run_id);
        setDecision(dec);
      } catch {}

      try {
        const ros = await api.getRosetta(run_id);
        setRosetta(ros);
      } catch {}

      try {
        const mem = await api.getMemos(run_id);
        setMemos(mem);
      } catch {}

      try {
        const deb = await api.getDebate(run_id);
        setDebate(deb);
      } catch {}

      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load evaluation details');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRunData();
    const interval = setInterval(() => {
      if (meta?.status === 'running' || meta?.status === 'queued') {
        loadRunData();
      }
    }, 2500);
    return () => clearInterval(interval);
  }, [run_id, meta?.status]);

  if (loading && !meta) {
    return (
      <div className="p-12 text-center text-slate-400 text-sm">
        <div className="inline-block w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mb-2"></div>
        <p>Loading run workspace...</p>
      </div>
    );
  }

  if (error || !meta) {
    return (
      <div className="max-w-4xl mx-auto p-8 rounded-xl bg-rose-500/5 border border-rose-500/20 text-center">
        <AlertCircle className="w-8 h-8 text-rose-400 mx-auto mb-2" />
        <h3 className="text-base font-bold text-white">Evaluation Not Found</h3>
        <p className="text-xs text-slate-400 mt-1 mb-4">{error || `No workspace exists for run ID ${run_id}`}</p>
        <Link
          to="/evaluations"
          className="inline-flex items-center gap-1.5 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold rounded-lg transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Evaluations
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Evidence Explorer Modal */}
      <CitationModal
        citationId={selectedCitationId}
        rosetta={rosetta}
        onClose={() => setSelectedCitationId(null)}
      />

      {/* Top Breadcrumb Bar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <Link to="/evaluations" className="hover:text-white transition-colors">
            Evaluations
          </Link>
          <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-slate-200 font-mono">{meta.run_id}</span>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={loadRunData}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-[#131D31] hover:bg-slate-800 border border-slate-700 text-slate-300 rounded-lg text-xs font-medium transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${meta.status === 'running' ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          {decision && (
            <a
              href={api.getReportPdfUrl(meta.run_id)}
              download
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold shadow-sm transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              Download PDF Report
            </a>
          )}
        </div>
      </div>

      {/* Hero Run Card */}
      <div className="bg-[#131D31] border border-slate-800/80 rounded-2xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-white tracking-tight">{meta.candidate_name}</h1>
              <StatusBadge status={meta.status} phase={meta.phase} />
              {decision && <StatusBadge verdict={decision.final_recommendation} />}
            </div>
            <p className="text-xs text-slate-400 font-mono mt-1">
              Target Role: <span className="text-slate-300">{meta.job_id}</span> | Candidate ID:{' '}
              <span className="text-slate-300">{meta.candidate_id}</span> | Run ID:{' '}
              <span className="text-indigo-400">{meta.run_id}</span>
            </p>
          </div>
          <div className="text-xs text-slate-400 text-right font-mono">
            <div>Created: {new Date(meta.created_at).toLocaleTimeString()}</div>
            <div>Updated: {new Date(meta.updated_at).toLocaleTimeString()}</div>
          </div>
        </div>

        {/* Phase Progress Bar for active runs */}
        {meta.status === 'running' && (
          <div className="mt-5 pt-4 border-t border-slate-800/80">
            <div className="flex items-center justify-between text-xs text-slate-300 font-mono mb-2">
              <span className="text-indigo-400 font-semibold animate-pulse">
                Phase Active: {meta.phase.toUpperCase()}
              </span>
              <span className="text-slate-400">Processing multi-agent deliberation...</span>
            </div>
            <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
              <div className="bg-indigo-500 h-full w-2/3 animate-pulse rounded-full"></div>
            </div>
          </div>
        )}
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-px overflow-x-auto">
        <button
          onClick={() => setActiveTab('overview')}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold rounded-t-lg transition-colors border-b-2 whitespace-nowrap ${
            activeTab === 'overview'
              ? 'border-indigo-500 text-indigo-400 bg-indigo-500/5'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Scale className="w-4 h-4" />
          Verdict & Overview
        </button>
        <button
          onClick={() => setActiveTab('rosetta')}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold rounded-t-lg transition-colors border-b-2 whitespace-nowrap ${
            activeTab === 'rosetta'
              ? 'border-indigo-500 text-indigo-400 bg-indigo-500/5'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <BookOpen className="w-4 h-4" />
          Rosetta Document
        </button>
        <button
          onClick={() => setActiveTab('memos')}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold rounded-t-lg transition-colors border-b-2 whitespace-nowrap ${
            activeTab === 'memos'
              ? 'border-indigo-500 text-indigo-400 bg-indigo-500/5'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Layers className="w-4 h-4" />
          Sealed Agent Memos
        </button>
        <button
          onClick={() => setActiveTab('debate')}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold rounded-t-lg transition-colors border-b-2 whitespace-nowrap ${
            activeTab === 'debate'
              ? 'border-indigo-500 text-indigo-400 bg-indigo-500/5'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <MessageSquare className="w-4 h-4" />
          Debate Replay & Deltas
        </button>
        <button
          onClick={() => setActiveTab('decision_path')}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold rounded-t-lg transition-colors border-b-2 whitespace-nowrap ${
            activeTab === 'decision_path'
              ? 'border-indigo-500 text-indigo-400 bg-indigo-500/5'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <GitCommit className="w-4 h-4" />
          Decision Path Flow
        </button>
      </div>

      {/* Tab 1: Overview & Verdict */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {decision ? (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column: General Secretary Verdict */}
              <div className="lg:col-span-2 space-y-6">
                <div className="bg-[#131D31] border border-slate-800 rounded-xl p-6">
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-2 flex items-center gap-2">
                    <Scale className="w-4 h-4 text-indigo-400" />
                    General Secretary Adjudication Synthesis
                  </h3>
                  <p className="text-sm text-slate-200 leading-relaxed bg-[#0B1120] p-4 rounded-lg border border-slate-800/80">
                    {decision.decision_path.original_gs_rationale}
                  </p>

                  {/* Override Motion Record */}
                  {decision.decision_path.override_motion_filed && decision.decision_path.override_motion && (
                    <div className="mt-4 p-4 rounded-lg bg-amber-500/5 border border-amber-500/20 text-xs">
                      <div className="flex items-center gap-2 text-amber-400 font-semibold mb-1">
                        <ShieldAlert className="w-4 h-4" />
                        <span>Override Motion Deliberation</span>
                      </div>
                      <p className="text-slate-300">
                        <b>Motion filed by:</b>{' '}
                        <span className="capitalize">{decision.decision_path.override_motion.filed_by.replace(/_/g, ' ')}</span>
                      </p>
                      <p className="text-slate-400 mt-1 italic">
                        "{decision.decision_path.override_motion.motion_text}"
                      </p>
                      <div className="mt-2 text-slate-300">
                        <b>Supermajority Vote:</b>{' '}
                        <span className="font-mono text-amber-300">
                          {decision.decision_path.override_motion.support_count}/4 in favor (
                          {decision.decision_path.override_motion.passed ? 'PASSED' : 'FAILED - Motion Rejected'})
                        </span>
                      </div>
                    </div>
                  )}
                </div>

                {/* Evidence Strengths & Concerns with Clickable Citation Badges */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <div className="bg-[#131D31] border border-slate-800 rounded-xl p-5">
                    <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-3">
                      Verified Strengths ({decision.strengths.length})
                    </h4>
                    <ul className="space-y-3 text-xs text-slate-300">
                      {decision.strengths.map((s, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <CitationBadge
                            citationId={s.citation_id}
                            onClick={(cid) => setSelectedCitationId(cid)}
                            className="shrink-0"
                          />
                          <span className="leading-snug">{s.claim}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="bg-[#131D31] border border-slate-800 rounded-xl p-5">
                    <h4 className="text-xs font-bold text-rose-400 uppercase tracking-wider mb-3">
                      Verified Concerns ({decision.concerns.length})
                    </h4>
                    <ul className="space-y-3 text-xs text-slate-300">
                      {decision.concerns.map((c, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <CitationBadge
                            citationId={c.citation_id}
                            onClick={(cid) => setSelectedCitationId(cid)}
                            className="shrink-0"
                          />
                          <span className="leading-snug">{c.claim}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>

              {/* Right Column: Key Decision Attributes */}
              <div className="space-y-6">
                <div className="bg-[#131D31] border border-slate-800 rounded-xl p-5 space-y-4">
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                    Executive Decision Metrics
                  </h4>
                  <div className="space-y-3 font-mono text-xs">
                    <div className="flex justify-between py-2 border-b border-slate-800">
                      <span className="text-slate-400">Final Verdict:</span>
                      <StatusBadge verdict={decision.final_recommendation} size="sm" />
                    </div>
                    <div className="flex justify-between py-2 border-b border-slate-800">
                      <span className="text-slate-400">Confidence:</span>
                      <span className="text-slate-100 font-semibold uppercase">{decision.confidence_level}</span>
                    </div>
                    <div className="flex justify-between py-2 border-b border-slate-800">
                      <span className="text-slate-400">Route:</span>
                      <span className="text-slate-200">
                        {decision.decision_path.auto_resolved ? 'Auto-Resolved' : 'Adjudication'}
                      </span>
                    </div>
                    <div className="flex justify-between py-2">
                      <span className="text-slate-400">Override:</span>
                      <span className="text-slate-200">
                        {decision.decision_path.override_motion_filed ? 'Filed & Evaluated' : 'None Filed'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Evidence Explorer Info Card */}
                <div className="bg-gradient-to-br from-indigo-950/40 to-slate-900 border border-indigo-500/20 rounded-xl p-5">
                  <div className="flex items-center gap-2 text-indigo-400 font-bold text-xs mb-1">
                    <Award className="w-4 h-4" />
                    Evidence Explorer Active
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    Click any citation tag (e.g. <code className="text-indigo-400">[T-A7]</code> or <code className="text-cyan-400">[R-EXP-01]</code>) anywhere in the report to inspect the exact verbatim source text and verify evidentiary grounding.
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-10 text-center text-slate-400 bg-[#131D31] rounded-xl border border-slate-800">
              <Clock className="w-6 h-6 mx-auto mb-2 text-indigo-400 animate-spin" />
              <p className="text-sm font-semibold text-white">Evaluation is currently executing...</p>
              <p className="text-xs mt-1">Phase: {meta.phase}. Decision deliverables will appear once debate concludes.</p>
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Rosetta Bible */}
      {activeTab === 'rosetta' && (
        <div className="space-y-6">
          {rosetta ? (
            <div className="bg-[#131D31] border border-slate-800 rounded-xl p-6 space-y-6">
              <div>
                <h3 className="text-base font-bold text-white">Project Rosetta — Candidate Profile Bible</h3>
                <p className="text-xs text-slate-400 font-mono">
                  Indexed facts with stable citations for evaluating personas
                </p>
              </div>

              {/* Citations Index Table */}
              <div>
                <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider mb-2">
                  Master Citation Index ({Object.keys(rosetta.citations_index).length} items)
                </h4>
                <div className="max-h-96 overflow-y-auto border border-slate-800 rounded-lg">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-[#0B1120] text-slate-400 font-mono text-[11px] sticky top-0">
                      <tr>
                        <th className="py-2.5 px-4 w-32">Citation ID</th>
                        <th className="py-2.5 px-4">Verbatim Record Text</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 font-mono">
                      {Object.entries(rosetta.citations_index).map(([cid, text]) => (
                        <tr
                          key={cid}
                          onClick={() => setSelectedCitationId(cid)}
                          className="hover:bg-indigo-500/5 cursor-pointer transition-colors"
                        >
                          <td className="py-2.5 px-4">
                            <CitationBadge citationId={cid} onClick={(id) => setSelectedCitationId(id)} />
                          </td>
                          <td className="py-2.5 px-4 text-slate-300 font-sans text-xs">{text}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-8 text-center text-slate-400 bg-[#131D31] rounded-xl border border-slate-800">
              <Clock className="w-6 h-6 mx-auto mb-2 text-indigo-400 animate-spin" />
              <p className="text-sm font-semibold text-white">Extracting Rosetta Profile Facts...</p>
            </div>
          )}
        </div>
      )}

      {/* Tab 3: Sealed Memos */}
      {activeTab === 'memos' && (
        <div className="space-y-6">
          <div className="bg-[#131D31] border border-slate-800/80 rounded-xl p-4 text-xs text-slate-300 flex items-center gap-2">
            <Layers className="w-4 h-4 text-indigo-400 shrink-0" />
            <span>
              <b>Pre-Debate Isolated Reasoning:</b> Each persona received ONLY the Job Description and Rosetta profile before deliberation.
            </span>
          </div>

          {memos ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {Object.entries(memos).map(([persona, memo]) => (
                <div key={persona} className="bg-[#131D31] border border-slate-800 rounded-xl p-5 space-y-3">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                    <div>
                      <h4 className="text-sm font-bold text-white capitalize">{persona.replace(/_/g, ' ')}</h4>
                      <p className="text-[11px] text-slate-400 font-mono">Confidence: {memo.confidence}</p>
                    </div>
                    <div className="text-right">
                      <span className="text-xl font-bold font-mono text-indigo-400">
                        {memo.score !== null ? `${memo.score}/10` : 'N/A'}
                      </span>
                    </div>
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed italic bg-[#0B1120] p-3 rounded border border-slate-800/60">
                    "{memo.verdict_summary}"
                  </p>

                  <div className="space-y-1.5">
                    <span className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider">
                      Strengths ({memo.strengths.length})
                    </span>
                    {memo.strengths.map((s, idx) => (
                      <div key={idx} className="text-xs text-slate-300 flex items-center gap-1.5">
                        <CitationBadge citationId={s.citation_id} onClick={(id) => setSelectedCitationId(id)} />
                        <span className="truncate">{s.claim}</span>
                      </div>
                    ))}
                  </div>

                  <div className="space-y-1.5">
                    <span className="text-[11px] font-semibold text-rose-400 uppercase tracking-wider">
                      Gaps ({memo.gaps.length})
                    </span>
                    {memo.gaps.map((g, idx) => (
                      <div key={idx} className="text-xs text-slate-300 flex items-center gap-1.5">
                        <CitationBadge citationId={g.citation_id} onClick={(id) => setSelectedCitationId(id)} />
                        <span className="truncate">{g.claim}</span>
                      </div>
                    ))}
                  </div>

                  {memo.contrarian_argument && (
                    <div className="p-2.5 rounded bg-amber-500/5 border border-amber-500/20 text-[11px] text-amber-300">
                      <b>Devil's Advocate Argument:</b> {memo.contrarian_argument}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center text-slate-400 bg-[#131D31] rounded-xl border border-slate-800">
              <Clock className="w-6 h-6 mx-auto mb-2 text-indigo-400 animate-spin" />
              <p className="text-sm font-semibold text-white">Generating Isolated Agent Memos...</p>
            </div>
          )}
        </div>
      )}

      {/* Tab 4: Debate Replay & Deliberation Deltas */}
      {activeTab === 'debate' && (
        <div className="space-y-6">
          {debate ? (
            <div className="space-y-6">
              {debate.rounds.map((rnd) => (
                <div key={rnd.round_num} className="bg-[#131D31] border border-slate-800 rounded-xl p-6 space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                    <div>
                      <span className="text-[11px] font-mono font-bold text-indigo-400 uppercase tracking-wider">
                        Round {rnd.round_num}
                      </span>
                      <h4 className="text-sm font-bold text-white">{rnd.agenda_item}</h4>
                    </div>
                  </div>

                  {/* Turns Dialogue with Rebuttal Badges */}
                  <div className="space-y-3">
                    {rnd.turns.map((turn, tIdx) => (
                      <div
                        key={tIdx}
                        className={`p-3.5 rounded-lg border text-xs leading-relaxed ${
                          turn.persona === 'general_secretary'
                            ? 'bg-indigo-950/20 border-indigo-500/20 text-slate-200'
                            : 'bg-[#0B1120] border-slate-800 text-slate-300'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-1.5">
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-white capitalize">{turn.persona.replace(/_/g, ' ')}</span>
                            {turn.responds_to && (
                              <span className="text-[10px] px-2 py-0.5 rounded bg-rose-500/10 text-rose-300 border border-rose-500/20 font-semibold">
                                Rebutting {turn.responds_to.replace(/_/g, ' ')}
                              </span>
                            )}
                            {turn.is_counter_question_response && (
                              <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20">
                                Counter-Question Response
                              </span>
                            )}
                          </div>
                          {turn.cites && turn.cites.length > 0 && (
                            <div className="flex items-center gap-1">
                              {turn.cites.map((c) => (
                                <CitationBadge
                                  key={c}
                                  citationId={c}
                                  onClick={(id) => setSelectedCitationId(id)}
                                />
                              ))}
                            </div>
                          )}
                        </div>
                        <p>{turn.statement}</p>
                      </div>
                    ))}
                  </div>

                  {/* Deliberation Opinion Shifts Callout (PRD §9) */}
                  {rnd.score_deltas_from_previous_round && Object.keys(rnd.score_deltas_from_previous_round).length > 0 && (
                    <div className="p-3 bg-amber-500/5 border border-amber-500/20 rounded-lg text-xs space-y-1">
                      <div className="flex items-center gap-1.5 text-amber-400 font-semibold mb-1">
                        <TrendingUp className="w-3.5 h-3.5" />
                        <span>Deliberation Score Shifts (Opinion Changed)</span>
                      </div>
                      {Object.entries(rnd.score_deltas_from_previous_round).map(([p, reason]) => (
                        <div key={p} className="text-slate-300">
                          <b className="capitalize text-slate-200">{p.replace(/_/g, ' ')}:</b> {reason}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Round Votes Table */}
                  <div className="p-3 bg-[#0B1120] rounded-lg border border-slate-800 flex items-center justify-around font-mono text-xs">
                    {Object.entries(rnd.votes).map(([persona, score]) => (
                      <div key={persona} className="text-center">
                        <div className="text-[10px] text-slate-400 capitalize">{persona.replace('_agent', '')}</div>
                        <div className="text-sm font-bold text-indigo-400">{score}/10</div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center text-slate-400 bg-[#131D31] rounded-xl border border-slate-800">
              <Clock className="w-6 h-6 mx-auto mb-2 text-indigo-400 animate-spin" />
              <p className="text-sm font-semibold text-white">Debate Session in Progress...</p>
            </div>
          )}
        </div>
      )}

      {/* Tab 5: Decision Path Flow Diagram */}
      {activeTab === 'decision_path' && (
        <div className="space-y-6">
          {decision ? (
            <div className="bg-[#131D31] border border-slate-800 rounded-xl p-6 space-y-6">
              <div>
                <h3 className="text-base font-bold text-white">Deliberation & Adjudication Pipeline Flow</h3>
                <p className="text-xs text-slate-400">
                  Step-by-step decision pathway from independent sealed memos to final recommendation
                </p>
              </div>

              {/* Visual Flow Steps */}
              <div className="space-y-4 max-w-2xl mx-auto">
                {/* Step 1 */}
                <div className="p-4 rounded-xl bg-[#0B1120] border border-slate-800 flex items-center gap-4">
                  <div className="w-8 h-8 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-xs shrink-0">
                    1
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-white uppercase tracking-wider">Independent Sealed Memos</h4>
                    <p className="text-xs text-slate-400">4 personas evaluate isolated Rosetta profile facts independently.</p>
                  </div>
                </div>

                <div className="flex justify-center text-slate-600">
                  <ArrowRight className="w-4 h-4 rotate-90" />
                </div>

                {/* Step 2 */}
                <div className="p-4 rounded-xl bg-[#0B1120] border border-slate-800 flex items-center gap-4">
                  <div className="w-8 h-8 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-xs shrink-0">
                    2
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-white uppercase tracking-wider">General Secretary Debate</h4>
                    <p className="text-xs text-slate-400">Agenda items debated across turns with direct rebuttals and integer voting.</p>
                  </div>
                </div>

                <div className="flex justify-center text-slate-600">
                  <ArrowRight className="w-4 h-4 rotate-90" />
                </div>

                {/* Step 3 */}
                <div className="p-4 rounded-xl bg-[#0B1120] border border-indigo-500/30 flex items-center gap-4">
                  <div className="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-xs shrink-0">
                    3
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-white uppercase tracking-wider">General Secretary Recommendation</h4>
                    <p className="text-xs text-slate-300">
                      Non-averaging verdict: <b className="text-indigo-400 uppercase">{decision.decision_path.original_gs_decision}</b> (Confidence: {decision.decision_path.original_gs_confidence.toUpperCase()})
                    </p>
                  </div>
                </div>

                <div className="flex justify-center text-slate-600">
                  <ArrowRight className="w-4 h-4 rotate-90" />
                </div>

                {/* Step 4: Override */}
                <div className={`p-4 rounded-xl border flex items-center gap-4 ${
                  decision.decision_path.override_motion_filed
                    ? 'bg-amber-500/5 border-amber-500/30'
                    : 'bg-[#0B1120] border-slate-800'
                }`}>
                  <div className="w-8 h-8 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center font-bold text-xs shrink-0">
                    4
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-white uppercase tracking-wider">Override Motion Deliberation</h4>
                    <p className="text-xs text-slate-300">
                      {decision.decision_path.override_motion_filed
                        ? `Motion filed by ${decision.decision_path.override_motion?.filed_by}. Result: ${decision.decision_path.override_motion?.support_count}/4 votes (${decision.decision_path.override_motion?.passed ? 'PASSED' : 'FAILED'}).`
                        : 'No override motion filed by any agent.'}
                    </p>
                  </div>
                </div>

                <div className="flex justify-center text-slate-600">
                  <ArrowRight className="w-4 h-4 rotate-90" />
                </div>

                {/* Final Step */}
                <div className={`p-4 rounded-xl border flex items-center gap-4 ${
                  decision.final_recommendation === 'hire'
                    ? 'bg-emerald-500/10 border-emerald-500/30'
                    : 'bg-rose-500/10 border-rose-500/30'
                }`}>
                  <div className="w-8 h-8 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-xs shrink-0">
                    5
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-white uppercase tracking-wider">Final Hiring Verdict</h4>
                    <p className="text-sm font-bold text-white font-mono uppercase">
                      {decision.final_recommendation} (Confidence: {decision.confidence_level})
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-8 text-center text-slate-400 bg-[#131D31] rounded-xl border border-slate-800">
              <Clock className="w-6 h-6 mx-auto mb-2 text-indigo-400 animate-spin" />
              <p className="text-sm font-semibold text-white">Generating Decision Path...</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
