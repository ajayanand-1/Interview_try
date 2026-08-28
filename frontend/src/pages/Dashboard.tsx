import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Layers,
  Users,
  Briefcase,
  FileCheck,
  TrendingUp,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  Clock,
  Sparkles,
} from 'lucide-react';
import { api } from '../api/client';
import { EvaluationSummary } from '../types/api';
import { StatCard } from '../components/common/StatCard';
import { StatusBadge } from '../components/common/StatusBadge';
import { EmptyState } from '../components/common/EmptyState';

export const Dashboard: React.FC = () => {
  const [evaluations, setEvaluations] = useState<EvaluationSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const data = await api.getEvaluations();
        setEvaluations(data);
        setError(null);
      } catch (err: any) {
        setError(err.message || 'Failed to load evaluations from backend.');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const totalRuns = evaluations.length;
  const completedRuns = evaluations.filter((e) => e.status === 'completed').length;
  const uniqueCandidates = new Set(evaluations.map((e) => e.candidate_id)).size;
  const uniqueJobs = new Set(evaluations.map((e) => e.job_id)).size;

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-indigo-900/40 via-slate-900/60 to-slate-900/40 border border-indigo-500/20 rounded-2xl p-6 relative overflow-hidden shadow-lg shadow-indigo-950/20">
        <div className="max-w-2xl">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-mono mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            MULTI-AGENT DELIBERATION ENGINE ACTIVE
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight sm:text-3xl">
            Evidence-Grounded Hiring Intelligence
          </h1>
          <p className="mt-2 text-sm text-slate-300 leading-relaxed">
            Four isolated AI personas evaluate candidate profiles, cross-examine evidence, and reach uncompromised hiring verdicts with 100% citation traceability.
          </p>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="Total Evaluations"
          value={totalRuns}
          subtitle="All historical run workspaces"
          icon={Layers}
        />
        <StatCard
          title="Unique Candidates"
          value={uniqueCandidates}
          subtitle="Indexed profiles"
          icon={Users}
        />
        <StatCard
          title="Target Roles"
          value={uniqueJobs}
          subtitle="Job specifications"
          icon={Briefcase}
        />
        <StatCard
          title="Completed Decisions"
          value={completedRuns}
          subtitle="Traceable final reports"
          icon={FileCheck}
        />
      </div>

      {/* Recent Evaluations Table */}
      <div className="bg-[#131D31] border border-slate-800/80 rounded-xl overflow-hidden">
        <div className="p-5 border-b border-slate-800/80 flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-white tracking-tight">Recent Evaluation Sessions</h3>
            <p className="text-xs text-slate-400">Latest multi-agent debate and decision workflows</p>
          </div>
          <Link
            to="/evaluations"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
          >
            View All Runs <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {loading ? (
          <div className="p-12 text-center text-slate-400 text-sm">
            <div className="inline-block w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mb-2"></div>
            <p>Loading evaluation workspaces...</p>
          </div>
        ) : error ? (
          <div className="p-8 text-center text-rose-400 text-sm bg-rose-500/5">
            <XCircle className="w-6 h-6 mx-auto mb-2 opacity-80" />
            <p className="font-medium">{error}</p>
            <p className="text-xs text-slate-400 mt-1">Make sure the FastAPI backend is running on http://127.0.0.1:8000</p>
          </div>
        ) : evaluations.length === 0 ? (
          <div className="p-8">
            <EmptyState
              title="No evaluations created yet"
              description="Configure and launch your first multi-agent interview panel evaluation."
            />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#0B1120] text-slate-400 font-mono uppercase tracking-wider text-[11px] border-b border-slate-800">
                <tr>
                  <th className="py-3 px-5">Candidate</th>
                  <th className="py-3 px-4">Role / Job ID</th>
                  <th className="py-3 px-4">Status & Phase</th>
                  <th className="py-3 px-4">Run Identifier</th>
                  <th className="py-3 px-4">Created Date</th>
                  <th className="py-3 px-5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-medium">
                {evaluations.slice(0, 5).map((evalItem) => (
                  <tr key={evalItem.run_id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3.5 px-5">
                      <div className="font-semibold text-slate-100 text-sm">{evalItem.candidate_name}</div>
                      <div className="text-[11px] text-slate-400 font-mono">{evalItem.candidate_id}</div>
                    </td>
                    <td className="py-3.5 px-4 text-slate-300 font-mono text-xs">
                      {evalItem.job_id}
                    </td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={evalItem.status} phase={evalItem.phase} />
                    </td>
                    <td className="py-3.5 px-4 text-slate-400 font-mono text-[11px]">
                      {evalItem.run_id}
                    </td>
                    <td className="py-3.5 px-4 text-slate-400">
                      {new Date(evalItem.created_at).toLocaleDateString(undefined, {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </td>
                    <td className="py-3.5 px-5 text-right">
                      <Link
                        to={`/evaluations/${evalItem.run_id}`}
                        className="inline-flex items-center gap-1 px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs transition-colors"
                      >
                        Inspect <ArrowRight className="w-3 h-3" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
