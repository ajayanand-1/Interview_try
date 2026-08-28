import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Briefcase,
  Users,
  PlusCircle,
  ArrowRight,
  ChevronDown,
  ChevronUp,
  Award,
  Layers,
  Scale,
} from 'lucide-react';
import { api } from '../api/client';
import { StatusBadge } from '../components/common/StatusBadge';
import { EmptyState } from '../components/common/EmptyState';

export const JobList: React.FC = () => {
  const [jobs, setJobs] = useState<
    Array<{
      job_id: string;
      job_title: string;
      evaluations_count: number;
      candidates: string[];
      runs: any[];
    }>
  >([]);
  const [loading, setLoading] = useState(true);

  // Selected job for deep hiring-room comparison (Phase K)
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const [comparisonData, setComparisonData] = useState<any | null>(null);
  const [comparisonLoading, setComparisonLoading] = useState(false);

  useEffect(() => {
    const loadJobs = async () => {
      try {
        setLoading(true);
        const data = await api.getJobs();
        setJobs(data);
        if (data.length > 0) {
          setSelectedJobId(data[0].job_id);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadJobs();
  }, []);

  useEffect(() => {
    if (!selectedJobId) return;
    const loadComparison = async () => {
      try {
        setComparisonLoading(true);
        const comp = await api.getJobCandidatesComparison(selectedJobId);
        setComparisonData(comp);
      } catch (err) {
        console.error(err);
      } finally {
        setComparisonLoading(false);
      }
    };
    loadComparison();
  }, [selectedJobId]);

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Job Roles & Multi-Candidate Hiring Room</h1>
          <p className="text-xs text-slate-400">
            Compare candidate evidence, agent scores, and deliberation outcomes side-by-side
          </p>
        </div>
        <Link
          to="/evaluations/new"
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold shadow-sm transition-colors"
        >
          <PlusCircle className="w-3.5 h-3.5" />
          Evaluate Candidate for Job
        </Link>
      </div>

      {loading ? (
        <div className="p-12 text-center text-slate-400 text-sm">
          <div className="inline-block w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mb-2"></div>
          <p>Loading job roles and pipelines...</p>
        </div>
      ) : jobs.length === 0 ? (
        <EmptyState
          title="No job roles indexed"
          description="Create your first evaluation to link candidate pipelines to a role."
        />
      ) : (
        <div className="space-y-8">
          {/* Job Selector Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {jobs.map((j) => (
              <div
                key={j.job_id}
                onClick={() => setSelectedJobId(j.job_id)}
                className={`p-5 rounded-xl border cursor-pointer transition-all ${
                  selectedJobId === j.job_id
                    ? 'bg-indigo-600/10 border-indigo-500/50 shadow-md shadow-indigo-950/30'
                    : 'bg-[#131D31] border-slate-800/80 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                    <Briefcase className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white uppercase font-mono">{j.job_title}</h3>
                    <p className="text-[11px] text-slate-400 font-mono">{j.job_id}</p>
                  </div>
                </div>
                <div className="mt-3 flex items-center justify-between text-xs text-slate-300">
                  <span>
                    <b>{j.candidates.length}</b> candidate{j.candidates.length > 1 ? 's' : ''} evaluated
                  </span>
                  <span className="font-mono text-indigo-400 text-[11px]">
                    {selectedJobId === j.job_id ? 'Active Selection' : 'Click to Compare'}
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Hiring Room Comparison Matrix (Phase K) */}
          {selectedJobId && (
            <div className="bg-[#131D31] border border-slate-800/80 rounded-xl p-6 space-y-5">
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <div>
                  <div className="inline-flex items-center gap-1.5 text-xs font-mono text-indigo-400 uppercase font-semibold mb-1">
                    <Scale className="w-3.5 h-3.5" />
                    Hiring Room Comparison Matrix
                  </div>
                  <h2 className="text-lg font-bold text-white tracking-tight">
                    Candidates for {selectedJobId.replace(/_/g, ' ').toUpperCase()}
                  </h2>
                </div>
                <div className="text-xs text-slate-400 font-mono">
                  Total Evaluated: <b>{comparisonData?.total_candidates || 0}</b>
                </div>
              </div>

              {comparisonLoading ? (
                <div className="p-8 text-center text-slate-400 text-xs">
                  <div className="inline-block w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mb-2"></div>
                  <p>Comparing candidate evidence matrices...</p>
                </div>
              ) : !comparisonData || comparisonData.candidates.length === 0 ? (
                <div className="p-6 text-center text-slate-400 text-xs">
                  No candidate evaluations found for this job specification.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-[#0B1120] text-slate-400 font-mono uppercase text-[11px] border-b border-slate-800">
                      <tr>
                        <th className="py-3 px-4">Candidate</th>
                        <th className="py-3 px-4">Verdict</th>
                        <th className="py-3 px-4">Confidence</th>
                        <th className="py-3 px-4 text-center">Tech</th>
                        <th className="py-3 px-4 text-center">HR</th>
                        <th className="py-3 px-4 text-center">HM</th>
                        <th className="py-3 px-4 text-center">Skeptic</th>
                        <th className="py-3 px-4">Evidence Strengths / Gaps</th>
                        <th className="py-3 px-4 text-right">Inspect</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 font-medium">
                      {comparisonData.candidates.map((c: any) => (
                        <tr key={c.run_id} className="hover:bg-slate-800/30 transition-colors">
                          <td className="py-3 px-4">
                            <div className="font-bold text-white text-sm">{c.candidate_name}</div>
                            <div className="text-[11px] text-slate-400 font-mono">{c.candidate_id}</div>
                          </td>
                          <td className="py-3 px-4">
                            {c.recommendation ? (
                              <StatusBadge verdict={c.recommendation} size="sm" />
                            ) : (
                              <StatusBadge status={c.status} phase={c.phase} size="sm" />
                            )}
                          </td>
                          <td className="py-3 px-4 font-mono uppercase text-slate-300">
                            {c.confidence || '—'}
                          </td>
                          <td className="py-3 px-4 text-center font-mono font-bold text-indigo-400">
                            {c.scores?.technical_agent !== undefined ? `${c.scores.technical_agent}/10` : '—'}
                          </td>
                          <td className="py-3 px-4 text-center font-mono font-bold text-indigo-400">
                            {c.scores?.hr_culture_agent !== undefined ? `${c.scores.hr_culture_agent}/10` : '—'}
                          </td>
                          <td className="py-3 px-4 text-center font-mono font-bold text-indigo-400">
                            {c.scores?.hiring_manager_agent !== undefined ? `${c.scores.hiring_manager_agent}/10` : '—'}
                          </td>
                          <td className="py-3 px-4 text-center font-mono font-bold text-indigo-400">
                            {c.scores?.skeptic_agent !== undefined ? `${c.scores.skeptic_agent}/10` : '—'}
                          </td>
                          <td className="py-3 px-4 text-slate-300">
                            <div className="flex items-center gap-2 font-mono text-[11px]">
                              <span className="text-emerald-400">+{c.strengths_count} strengths</span>
                              <span className="text-slate-600">|</span>
                              <span className="text-rose-400">-{c.concerns_count} concerns</span>
                            </div>
                          </td>
                          <td className="py-3 px-4 text-right">
                            <Link
                              to={`/evaluations/${c.run_id}`}
                              className="inline-flex items-center gap-1 px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs transition-colors"
                            >
                              Run <ArrowRight className="w-3 h-3" />
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
