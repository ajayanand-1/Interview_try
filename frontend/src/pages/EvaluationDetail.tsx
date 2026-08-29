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
  Sparkles,
  Lightbulb,
  GraduationCap,
  Briefcase,
  Target,
  FileText,
  Play,
  Square,
  Volume2,
  Mic,
  Shield,
  User,
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

export const PERSONA_ROSTER: Record<string, {
  name: string;
  role: string;
  gender: 'Female' | 'Male';
  voiceMac: string;
  pitch: number;
  rate: number;
  badgeBg: string;
  textColor: string;
  borderColor: string;
  description: string;
}> = {
  technical_agent: {
    name: 'Dr. Maya Lin',
    role: 'Lead AI Systems Architect',
    gender: 'Female',
    voiceMac: 'Karen',
    pitch: 1.05,
    rate: 1.0,
    badgeBg: 'bg-cyan-500/10',
    textColor: 'text-cyan-400',
    borderColor: 'border-cyan-500/30',
    description: 'Systematic, analytical, focused on software architecture, vector indexing, framework internals, and execution correctness.'
  },
  hr_culture_agent: {
    name: 'Marcus Vance',
    role: 'Head of People & Organizational Culture',
    gender: 'Male',
    voiceMac: 'Oliver',
    pitch: 0.95,
    rate: 0.98,
    badgeBg: 'bg-emerald-500/10',
    textColor: 'text-emerald-400',
    borderColor: 'border-emerald-500/30',
    description: 'Empathetic, psychologically perceptive, values team safety, blameless communication, accountability during incidents.'
  },
  hiring_manager_agent: {
    name: 'David Sterling',
    role: 'VP of Engineering & Product Delivery',
    gender: 'Male',
    voiceMac: 'Fred',
    pitch: 0.9,
    rate: 1.02,
    badgeBg: 'bg-amber-500/10',
    textColor: 'text-amber-400',
    borderColor: 'border-amber-500/30',
    description: 'Executive, ROI-focused, strategic, evaluating payroll risk, ramp-up schedules, retention horizons, and velocity.'
  },
  skeptic_agent: {
    name: 'Dr. Rachel Thorne',
    role: 'Principal Forensic Auditor & Critic',
    gender: 'Female',
    voiceMac: 'Samantha',
    pitch: 1.1,
    rate: 0.98,
    badgeBg: 'bg-rose-500/10',
    textColor: 'text-rose-400',
    borderColor: 'border-rose-500/30',
    description: 'Forensic auditor, relentless evidence auditor, searching for unverified claims, benchmark omissions, and attribution gaps.'
  },
  general_secretary: {
    name: 'Arthur Pendelton',
    role: 'General Secretary & Panel Chair',
    gender: 'Male',
    voiceMac: 'Daniel',
    pitch: 0.85,
    rate: 0.95,
    badgeBg: 'bg-indigo-500/10',
    textColor: 'text-indigo-400',
    borderColor: 'border-indigo-500/30',
    description: 'Impartial, structured, ensuring parliamentary order, enforcing civil dialogue, managing round timers, and synthesizing verdicts.'
  }
};

type TabType = 'overview' | 'rosetta' | 'memos' | 'debate' | 'decision_path' | 'feedback';

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

  // Audio Speech Playback state
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [currentSpeakingTurn, setCurrentSpeakingTurn] = useState<{ roundIdx: number; turnIdx: number } | null>(null);

  const stopAudioPlayback = () => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    setIsPlayingAudio(false);
    setCurrentSpeakingTurn(null);
  };

  const playDebateAudio = () => {
    if (!debate || typeof window === 'undefined' || !('speechSynthesis' in window)) return;

    stopAudioPlayback();
    setIsPlayingAudio(true);

    const allTurns: { roundIdx: number; turnIdx: number; persona: string; statement: string }[] = [];
    debate.rounds.forEach((rnd, rIdx) => {
      rnd.turns.forEach((turn, tIdx) => {
        allTurns.push({
          roundIdx: rIdx,
          turnIdx: tIdx,
          persona: turn.persona,
          statement: turn.statement.replace(/\[.*?\]/g, '').replace(/[*_#]/g, ''),
        });
      });
    });

    const availableVoices = window.speechSynthesis.getVoices();
    let step = 0;

    const speakNext = () => {
      if (step >= allTurns.length) {
        setIsPlayingAudio(false);
        setCurrentSpeakingTurn(null);
        return;
      }

      const item = allTurns[step];
      setCurrentSpeakingTurn({ roundIdx: item.roundIdx, turnIdx: item.turnIdx });

      const personaInfo = PERSONA_ROSTER[item.persona] || PERSONA_ROSTER.general_secretary;
      const utterance = new SpeechSynthesisUtterance(item.statement);
      utterance.pitch = personaInfo.pitch;
      utterance.rate = personaInfo.rate;

      if (personaInfo.gender === 'Female') {
        const femaleVoice =
          availableVoices.find(
            (v) =>
              (v.name.toLowerCase().includes('karen') ||
                v.name.toLowerCase().includes('samantha') ||
                v.name.toLowerCase().includes('victoria') ||
                v.name.toLowerCase().includes('zira') ||
                v.name.toLowerCase().includes('female')) &&
              v.lang.startsWith('en')
          ) || availableVoices.find((v) => v.lang.startsWith('en'));
        if (femaleVoice) utterance.voice = femaleVoice;
      } else {
        const maleVoice =
          availableVoices.find(
            (v) =>
              (v.name.toLowerCase().includes('daniel') ||
                v.name.toLowerCase().includes('alex') ||
                v.name.toLowerCase().includes('fred') ||
                v.name.toLowerCase().includes('oliver') ||
                v.name.toLowerCase().includes('male') ||
                v.name.toLowerCase().includes('david')) &&
              v.lang.startsWith('en')
          ) || availableVoices.find((v) => v.lang.startsWith('en'));
        if (maleVoice) utterance.voice = maleVoice;
      }

      utterance.onend = () => {
        step++;
        speakNext();
      };

      utterance.onerror = () => {
        step++;
        speakNext();
      };

      window.speechSynthesis.speak(utterance);
    };

    speakNext();
  };

  useEffect(() => {
    return () => {
      if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

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
        <button
          onClick={() => setActiveTab('feedback')}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold rounded-t-lg transition-colors border-b-2 whitespace-nowrap ${
            activeTab === 'feedback'
              ? 'border-indigo-500 text-indigo-400 bg-indigo-500/5'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Sparkles className="w-4 h-4 text-amber-400" />
          Candidate Feedback & Growth
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
          {/* Civil Debate & Voice Control Panel */}
          <div className="bg-[#131D31] border border-slate-800 rounded-xl p-5 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
              <div>
                <div className="flex items-center gap-2">
                  <Volume2 className="w-5 h-5 text-indigo-400" />
                  <h3 className="text-sm sm:text-base font-bold text-white">Parliamentary Civil Debate Audio</h3>
                </div>
                <p className="text-xs text-slate-400 mt-0.5">
                  Sequential, non-overlapping deliberation with distinct fixed voices across 2 female and 2 male AI agents.
                </p>
              </div>

              {/* Audio Controls */}
              <div className="flex items-center gap-2.5">
                {!isPlayingAudio ? (
                  <button
                    onClick={playDebateAudio}
                    className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white text-xs font-semibold rounded-lg shadow-md shadow-indigo-600/20 transition-all cursor-pointer"
                  >
                    <Play className="w-4 h-4 fill-white" />
                    <span>Play Voice Stream</span>
                  </button>
                ) : (
                  <button
                    onClick={stopAudioPlayback}
                    className="inline-flex items-center gap-2 px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold rounded-lg shadow-md shadow-rose-600/20 transition-all cursor-pointer"
                  >
                    <Square className="w-3.5 h-3.5 fill-white" />
                    <span>Stop Voice Stream</span>
                  </button>
                )}
              </div>
            </div>

            {/* Speaking Status Indicator */}
            {isPlayingAudio && currentSpeakingTurn && (
              <div className="flex items-center gap-3 p-3 bg-indigo-950/40 border border-indigo-500/30 rounded-lg text-xs animate-pulse">
                <div className="flex items-center gap-1">
                  <span className="w-1.5 h-3 bg-indigo-400 rounded-full animate-bounce"></span>
                  <span className="w-1.5 h-4 bg-indigo-300 rounded-full animate-bounce [animation-delay:0.15s]"></span>
                  <span className="w-1.5 h-2 bg-indigo-400 rounded-full animate-bounce [animation-delay:0.3s]"></span>
                </div>
                <span className="text-indigo-200 font-medium">
                  Currently Speaking: Round {currentSpeakingTurn.roundIdx + 1}, Turn {currentSpeakingTurn.turnIdx + 1}
                </span>
              </div>
            )}

            {/* 5-Persona Evaluator Roster Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 pt-1">
              {Object.entries(PERSONA_ROSTER).map(([pKey, pInfo]) => (
                <div
                  key={pKey}
                  className={`p-3 rounded-lg border bg-[#0B1120] ${pInfo.borderColor} space-y-1.5 transition-all`}
                >
                  <div className="flex items-center justify-between">
                    <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded font-mono ${pInfo.badgeBg} ${pInfo.textColor}`}>
                      {pInfo.gender === 'Female' ? '♀ Female' : '♂ Male'}
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">{pInfo.voiceMac}</span>
                  </div>
                  <div>
                    <h5 className="text-xs font-bold text-white">{pInfo.name}</h5>
                    <p className="text-[10px] text-slate-400 leading-tight">{pInfo.role}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Structured Debate Rounds */}
          {debate ? (
            <div className="space-y-6">
              {debate.rounds.map((rnd, rIdx) => (
                <div key={rnd.round_num} className="bg-[#131D31] border border-slate-800 rounded-xl p-4 sm:p-6 space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                    <div>
                      <span className="text-[11px] font-mono font-bold text-indigo-400 uppercase tracking-wider">
                        Round {rnd.round_num}
                      </span>
                      <h4 className="text-sm font-bold text-white">{rnd.agenda_item}</h4>
                    </div>
                  </div>

                  {/* Turns Dialogue with Rebuttal Badges & Discussion Pillars */}
                  <div className="space-y-3">
                    {rnd.turns.map((turn, tIdx) => {
                      const speaker = PERSONA_ROSTER[turn.persona] || PERSONA_ROSTER.general_secretary;
                      const isCurrentSpeaking =
                        isPlayingAudio &&
                        currentSpeakingTurn?.roundIdx === rIdx &&
                        currentSpeakingTurn?.turnIdx === tIdx;

                      // Detect discussion pillars
                      const hasProblem = turn.statement.toLowerCase().includes('problem');
                      const hasExpectation = turn.statement.toLowerCase().includes('expectation');
                      const hasProsCons =
                        turn.statement.toLowerCase().includes('pro') ||
                        turn.statement.toLowerCase().includes('con') ||
                        turn.statement.toLowerCase().includes('strength');
                      const hasSolution =
                        turn.statement.toLowerCase().includes('solution') ||
                        turn.statement.toLowerCase().includes('ramp') ||
                        turn.statement.toLowerCase().includes('pairing') ||
                        turn.statement.toLowerCase().includes('checklist');

                      return (
                        <div
                          key={tIdx}
                          className={`p-4 rounded-xl border text-xs leading-relaxed transition-all ${
                            isCurrentSpeaking
                              ? 'ring-2 ring-indigo-500 bg-indigo-950/40 border-indigo-400/50 shadow-lg'
                              : turn.persona === 'general_secretary'
                              ? 'bg-indigo-950/20 border-indigo-500/20 text-slate-200'
                              : 'bg-[#0B1120] border-slate-800/80 text-slate-300'
                          }`}
                        >
                          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                            <div className="flex items-center gap-2 flex-wrap">
                              <span className="font-bold text-white text-sm">{speaker.name}</span>
                              <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${speaker.badgeBg} ${speaker.textColor} font-semibold`}>
                                {speaker.gender === 'Female' ? '♀ Female' : '♂ Male'} ({speaker.voiceMac})
                              </span>
                              <span className="text-[10px] text-slate-400 font-mono hidden md:inline">
                                • {speaker.role}
                              </span>

                              {turn.responds_to && (
                                <span className="text-[10px] px-2 py-0.5 rounded bg-rose-500/10 text-rose-300 border border-rose-500/20 font-semibold">
                                  Rebutting {PERSONA_ROSTER[turn.responds_to]?.name || turn.responds_to.replace(/_/g, ' ')}
                                </span>
                              )}
                              {turn.is_counter_question_response && (
                                <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20">
                                  Counter-Question Response
                                </span>
                              )}
                            </div>

                            {turn.cites && turn.cites.length > 0 && (
                              <div className="flex items-center gap-1 flex-wrap">
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

                          <p className="text-slate-200 leading-relaxed mb-2.5">{turn.statement}</p>

                          {/* 4 Pillars Tags Footer */}
                          <div className="flex items-center gap-1.5 flex-wrap pt-2 border-t border-slate-800/60">
                            {hasProblem && (
                              <span className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded bg-rose-500/10 text-rose-300 border border-rose-500/20">
                                🎯 Problem Analyzed
                              </span>
                            )}
                            {hasExpectation && (
                              <span className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded bg-blue-500/10 text-blue-300 border border-blue-500/20">
                                📋 Role Expectation
                              </span>
                            )}
                            {hasProsCons && (
                              <span className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded bg-purple-500/10 text-purple-300 border border-purple-500/20">
                                ⚖️ Pros & Cons Grounded
                              </span>
                            )}
                            {hasSolution && (
                              <span className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                                💡 Viable Solution Proposed
                              </span>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {/* Deliberation Opinion Shifts Callout (PRD §9) */}
                  {rnd.score_deltas_from_previous_round && Object.keys(rnd.score_deltas_from_previous_round).length > 0 && (
                    <div className="p-3.5 bg-amber-500/5 border border-amber-500/20 rounded-lg text-xs space-y-1">
                      <div className="flex items-center gap-1.5 text-amber-400 font-semibold mb-1">
                        <TrendingUp className="w-3.5 h-3.5" />
                        <span>Deliberation Score Shifts (Opinion Changed)</span>
                      </div>
                      {Object.entries(rnd.score_deltas_from_previous_round).map(([p, reason]) => (
                        <div key={p} className="text-slate-300">
                          <b className="capitalize text-slate-200">{PERSONA_ROSTER[p]?.name || p.replace(/_/g, ' ')}:</b> {reason}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Round Votes Table */}
                  <div className="p-3.5 bg-[#0B1120] rounded-lg border border-slate-800 grid grid-cols-2 sm:grid-cols-4 gap-2 font-mono text-xs">
                    {Object.entries(rnd.votes).map(([persona, score]) => (
                      <div key={persona} className="text-center p-2 rounded bg-[#131D31]/60 border border-slate-800/60">
                        <div className="text-[10px] text-slate-400">{PERSONA_ROSTER[persona]?.name || persona.replace('_agent', '')}</div>
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

      {/* Tab 6: Candidate Feedback & Growth Playbook */}
      {activeTab === 'feedback' && (
        <div className="space-y-6">
          {decision?.feedback ? (
            <div className="space-y-6">
              {/* Top Overview Banner */}
              <div className="bg-gradient-to-r from-indigo-950/40 via-purple-950/30 to-slate-900 border border-indigo-500/30 rounded-2xl p-6 relative overflow-hidden">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-amber-300 shrink-0">
                    <Sparkles className="w-6 h-6" />
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-3">
                      <h3 className="text-base font-bold text-white tracking-wide">
                        Candidate Growth & Interview Preparation Playbook
                      </h3>
                      <span className="px-2.5 py-0.5 text-[10px] font-bold rounded-full uppercase bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                        Evidence-Grounded Insights
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed max-w-4xl">
                      {decision.feedback.overall_summary}
                    </p>
                  </div>
                </div>
              </div>

              {/* Section 1: Resume Improvements */}
              <div className="bg-[#131D31] border border-slate-800 rounded-xl p-6 space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4 text-sky-400" />
                    <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                      1. Resume Improvements & Rewriting Guide
                    </h3>
                  </div>
                  <span className="text-xs text-slate-400">
                    {decision.feedback.resume_improvements.length} Key Optimizations
                  </span>
                </div>

                <div className="grid grid-cols-1 gap-4">
                  {decision.feedback.resume_improvements.map((item, idx) => (
                    <div key={idx} className="bg-[#0B1120] border border-slate-800 rounded-xl p-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <h4 className="text-xs font-bold text-white tracking-wide flex items-center gap-2">
                          <span className="w-5 h-5 rounded-full bg-sky-500/20 text-sky-400 flex items-center justify-center text-[10px] font-bold">
                            {idx + 1}
                          </span>
                          {item.section}
                        </h4>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                        <div className="p-3 rounded-lg bg-rose-500/5 border border-rose-500/20">
                          <p className="text-[10px] font-bold text-rose-400 uppercase tracking-wider mb-1">
                            Identified Issue / Gap
                          </p>
                          <p className="text-slate-300">{item.current_issue}</p>
                        </div>
                        <div className="p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/20">
                          <p className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider mb-1">
                            Actionable Recommendation
                          </p>
                          <p className="text-slate-300">{item.recommendation}</p>
                        </div>
                      </div>

                      {item.example_before && item.example_after && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs pt-1">
                          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 font-mono">
                            <span className="text-[10px] font-bold text-slate-400 uppercase block mb-1">
                              ❌ Before (Current Resume)
                            </span>
                            <span className="text-slate-400 line-through">"{item.example_before}"</span>
                          </div>
                          <div className="p-3 rounded-lg bg-slate-900 border border-emerald-500/30 font-mono">
                            <span className="text-[10px] font-bold text-emerald-400 uppercase block mb-1">
                              ✨ Recommended Rewrite
                            </span>
                            <span className="text-emerald-300 font-medium">"{item.example_after}"</span>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Section 2: Required Skills Roadmap */}
              <div className="bg-[#131D31] border border-slate-800 rounded-xl p-6 space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div className="flex items-center gap-2">
                    <Target className="w-4 h-4 text-indigo-400" />
                    <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                      2. Target Role Skills Roadmap & Gap Analysis
                    </h3>
                  </div>
                  <span className="text-xs text-slate-400">
                    {decision.feedback.required_skills.length} Critical Capabilities
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {decision.feedback.required_skills.map((skill, idx) => (
                    <div key={idx} className="bg-[#0B1120] border border-slate-800 rounded-xl p-4 space-y-3 flex flex-col justify-between">
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <GraduationCap className="w-4 h-4 text-indigo-400 shrink-0" />
                          <h4 className="text-xs font-bold text-white">{skill.skill_category}</h4>
                        </div>
                        <div className="space-y-1.5 text-xs">
                          <div>
                            <span className="text-[10px] font-bold text-slate-400 uppercase block">Company Expectation</span>
                            <p className="text-slate-300 text-[11px]">{skill.target_job_expectation}</p>
                          </div>
                          <div>
                            <span className="text-[10px] font-bold text-amber-400 uppercase block">Current Verified Level</span>
                            <p className="text-slate-300 text-[11px]">{skill.current_candidate_level}</p>
                          </div>
                        </div>
                      </div>

                      <div className="p-2.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-xs">
                        <span className="text-[10px] font-bold text-indigo-400 uppercase block mb-1">Growth & Mastery Plan</span>
                        <p className="text-slate-200 text-[11px]">{skill.growth_path}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Section 3: Company & Leadership Expectations */}
              <div className="bg-[#131D31] border border-slate-800 rounded-xl p-6 space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div className="flex items-center gap-2">
                    <Briefcase className="w-4 h-4 text-purple-400" />
                    <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                      3. Hiring Company & Engineering Expectations
                    </h3>
                  </div>
                  <span className="text-xs text-slate-400">
                    {decision.feedback.company_expectations.length} Organizational Pillars
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {decision.feedback.company_expectations.map((exp, idx) => (
                    <div key={idx} className="bg-[#0B1120] border border-slate-800 rounded-xl p-4 space-y-3">
                      <h4 className="text-xs font-bold text-purple-300">{exp.pillar}</h4>
                      <div className="space-y-2 text-xs">
                        <div>
                          <span className="text-[10px] font-bold text-slate-400 uppercase block">Company Standard</span>
                          <p className="text-slate-300 text-[11px]">{exp.company_standard}</p>
                        </div>
                        <div>
                          <span className="text-[10px] font-bold text-slate-400 uppercase block">Assessment Finding</span>
                          <p className="text-slate-300 text-[11px]">{exp.assessment_finding}</p>
                        </div>
                        <div className="p-2.5 rounded-lg bg-purple-500/10 border border-purple-500/20">
                          <span className="text-[10px] font-bold text-purple-400 uppercase block mb-0.5">Interview Preparation Tip</span>
                          <p className="text-slate-200 text-[11px]">{exp.advice_for_future_interviews}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Section 4: 5-Persona Evaluation Breakdown */}
              <div className="bg-[#131D31] border border-slate-800 rounded-xl p-6 space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div className="flex items-center gap-2">
                    <Layers className="w-4 h-4 text-emerald-400" />
                    <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                      4. 5-Persona Evaluation Feedback Breakdown
                    </h3>
                  </div>
                  <span className="text-xs text-slate-400">All Evaluator Perspectives</span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {decision.feedback.persona_feedback.map((item, idx) => {
                    const personaTitle = item.persona
                      .split('_')
                      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
                      .join(' ');
                    return (
                      <div key={idx} className="bg-[#0B1120] border border-slate-800 rounded-xl p-4 space-y-3 flex flex-col justify-between">
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="px-2 py-0.5 text-[10px] font-bold uppercase rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                              {personaTitle}
                            </span>
                          </div>
                          <h4 className="text-xs font-bold text-white tracking-wide">{item.headline}</h4>
                          <p className="text-xs text-slate-300 leading-relaxed">{item.feedback}</p>
                        </div>
                        <div className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-xs">
                          <span className="text-[10px] font-bold text-emerald-400 uppercase block mb-0.5">Key Recommendation</span>
                          <p className="text-slate-200 text-[11px]">{item.key_recommendation}</p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          ) : (
            <div className="p-12 text-center text-slate-400 bg-[#131D31] rounded-xl border border-slate-800 space-y-3">
              <Clock className="w-8 h-8 mx-auto text-indigo-400 animate-spin" />
              <h4 className="text-sm font-bold text-white">Synthesizing Candidate Feedback...</h4>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                Candidate feedback across HR, Skeptic, Hiring Manager, Technical, and General Secretary agents is being compiled.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
