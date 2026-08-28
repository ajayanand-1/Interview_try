import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Users, ArrowRight, Search, Layers, Award } from 'lucide-react';
import { api } from '../api/client';
import { StatusBadge } from '../components/common/StatusBadge';
import { EmptyState } from '../components/common/EmptyState';

export const CandidateList: React.FC = () => {
  const [candidates, setCandidates] = useState<
    Array<{
      candidate_id: string;
      candidate_name: string;
      evaluations_count: number;
      latest_status: string;
      latest_run_id: string;
      latest_job_id: string;
      latest_date: string;
      runs: any[];
    }>
  >([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const data = await api.getCandidates();
        setCandidates(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const filtered = candidates.filter((c) =>
    c.candidate_name.toLowerCase().includes(search.toLowerCase()) ||
    c.candidate_id.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Candidate Profiles Directory</h1>
          <p className="text-xs text-slate-400">Aggregated candidate evaluations and multi-job deliberation histories</p>
        </div>
        <div className="relative w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search candidate name or ID..."
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-[#131D31] border border-slate-700/60 rounded-lg text-slate-200 placeholder-slate-400 focus:outline-none focus:border-indigo-500 transition-colors"
          />
        </div>
      </div>

      {loading ? (
        <div className="p-12 text-center text-slate-400 text-sm">
          <div className="inline-block w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mb-2"></div>
          <p>Loading candidate directory...</p>
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState
          title="No candidates found"
          description="Candidates will appear here automatically once evaluations are launched."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filtered.map((c) => (
            <div
              key={c.candidate_id}
              className="bg-[#131D31] border border-slate-800/80 rounded-xl p-5 hover:border-slate-700 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-indigo-600 to-cyan-500 flex items-center justify-center font-bold text-white text-sm">
                    {c.candidate_name
                      .split(' ')
                      .map((n) => n[0])
                      .join('')}
                  </div>
                  <StatusBadge status={c.latest_status} size="sm" />
                </div>
                <h3 className="text-base font-bold text-white">{c.candidate_name}</h3>
                <p className="text-xs text-slate-400 font-mono">{c.candidate_id}</p>
                <div className="mt-2 text-xs text-slate-300 font-mono">
                  Latest Role: <span className="text-indigo-300">{c.latest_job_id}</span>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs">
                <span className="text-slate-400">
                  <b>{c.evaluations_count}</b> evaluation{c.evaluations_count > 1 ? 's' : ''} run
                </span>
                <Link
                  to={`/evaluations/${c.latest_run_id}`}
                  className="inline-flex items-center gap-1 font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
                >
                  Latest Run <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
