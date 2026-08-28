import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Layers,
  PlusCircle,
  ArrowRight,
  RefreshCw,
  AlertCircle,
  Search,
  Filter,
} from 'lucide-react';
import { api } from '../api/client';
import { EvaluationSummary } from '../types/api';
import { StatusBadge } from '../components/common/StatusBadge';
import { EmptyState } from '../components/common/EmptyState';

export const EvaluationList: React.FC = () => {
  const [evaluations, setEvaluations] = useState<EvaluationSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  const fetchRuns = async () => {
    try {
      setLoading(true);
      const data = await api.getEvaluations();
      setEvaluations(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch evaluations');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRuns();
  }, []);

  const filtered = evaluations.filter((e) => {
    const matchesSearch =
      e.candidate_name.toLowerCase().includes(search.toLowerCase()) ||
      e.candidate_id.toLowerCase().includes(search.toLowerCase()) ||
      e.job_id.toLowerCase().includes(search.toLowerCase()) ||
      e.run_id.toLowerCase().includes(search.toLowerCase());

    const matchesStatus =
      statusFilter === 'all' || e.status.toLowerCase() === statusFilter.toLowerCase();

    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Evaluation Sessions</h1>
          <p className="text-xs text-slate-400">All isolated multi-agent interview panel run workspaces</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchRuns}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-[#131D31] hover:bg-slate-800 border border-slate-700 text-slate-300 rounded-lg text-xs font-medium transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <Link
            to="/evaluations/new"
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold shadow-sm transition-colors"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            New Evaluation
          </Link>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-[#131D31] border border-slate-800 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search candidate, job, or run ID..."
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-[#0B1120] border border-slate-700/60 rounded-lg text-slate-200 placeholder-slate-400 focus:outline-none focus:border-indigo-500 transition-colors"
          />
        </div>

        <div className="flex items-center gap-2 text-xs">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-slate-400 font-semibold">Status:</span>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-[#0B1120] border border-slate-700/60 rounded-lg px-2.5 py-1 text-slate-200 focus:outline-none focus:border-indigo-500 text-xs"
          >
            <option value="all">All States</option>
            <option value="completed">Completed</option>
            <option value="running">Running</option>
            <option value="queued">Queued</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>

      {/* Evaluations Table */}
      <div className="bg-[#131D31] border border-slate-800/80 rounded-xl overflow-hidden shadow-sm">
        {loading ? (
          <div className="p-12 text-center text-slate-400 text-sm">
            <div className="inline-block w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mb-2"></div>
            <p>Scanning evaluation workspaces...</p>
          </div>
        ) : error ? (
          <div className="p-8 text-center text-rose-400 text-sm bg-rose-500/5">
            <AlertCircle className="w-6 h-6 mx-auto mb-2 opacity-80" />
            <p className="font-medium">{error}</p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-10">
            <EmptyState
              title="No evaluation runs match your criteria"
              description="Adjust search filters or start a new candidate evaluation."
            />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#0B1120] text-slate-400 font-mono uppercase tracking-wider text-[11px] border-b border-slate-800">
                <tr>
                  <th className="py-3 px-5">Candidate Name</th>
                  <th className="py-3 px-4">Role / Job</th>
                  <th className="py-3 px-4">Lifecycle Status</th>
                  <th className="py-3 px-4">Run Identifier</th>
                  <th className="py-3 px-4">Created Timestamp</th>
                  <th className="py-3 px-5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-medium">
                {filtered.map((evalItem) => (
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
                      {new Date(evalItem.created_at).toLocaleString()}
                    </td>
                    <td className="py-3.5 px-5 text-right">
                      <Link
                        to={`/evaluations/${evalItem.run_id}`}
                        className="inline-flex items-center gap-1.5 px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs transition-colors"
                      >
                        Details <ArrowRight className="w-3.5 h-3.5" />
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
