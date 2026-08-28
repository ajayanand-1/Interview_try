import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Users, ArrowRight, Layers, Award } from 'lucide-react';
import { api } from '../api/client';
import { EvaluationSummary } from '../types/api';
import { StatusBadge } from '../components/common/StatusBadge';
import { EmptyState } from '../components/common/EmptyState';

export const CandidateList: React.FC = () => {
  const [evaluations, setEvaluations] = useState<EvaluationSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const data = await api.getEvaluations();
        setEvaluations(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  // Aggregate by candidate_id
  const candidateMap: Record<
    string,
    { name: string; id: string; count: number; latestStatus: string; latestRunId: string; latestDate: string }
  > = {};

  evaluations.forEach((e) => {
    if (!candidateMap[e.candidate_id]) {
      candidateMap[e.candidate_id] = {
        name: e.candidate_name,
        id: e.candidate_id,
        count: 1,
        latestStatus: e.status,
        latestRunId: e.run_id,
        latestDate: e.created_at,
      };
    } else {
      candidateMap[e.candidate_id].count += 1;
    }
  });

  const candidates = Object.values(candidateMap);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight">Candidate Profiles</h1>
        <p className="text-xs text-slate-400">Aggregated candidate evaluations and deliberation history</p>
      </div>

      {loading ? (
        <div className="p-12 text-center text-slate-400 text-sm">
          <div className="inline-block w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mb-2"></div>
          <p>Loading candidate directory...</p>
        </div>
      ) : candidates.length === 0 ? (
        <EmptyState
          title="No candidates indexed yet"
          description="Candidates will appear here automatically once evaluations are launched."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {candidates.map((c) => (
            <div key={c.id} className="bg-[#131D31] border border-slate-800/80 rounded-xl p-5 hover:border-slate-700 transition-all flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-indigo-600 to-cyan-500 flex items-center justify-center font-bold text-white text-sm">
                    {c.name.split(' ').map((n) => n[0]).join('')}
                  </div>
                  <StatusBadge status={c.latestStatus} size="sm" />
                </div>
                <h3 className="text-base font-bold text-white">{c.name}</h3>
                <p className="text-xs text-slate-400 font-mono">{c.id}</p>
              </div>

              <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs">
                <span className="text-slate-400">
                  <b>{c.count}</b> evaluation{c.count > 1 ? 's' : ''} run
                </span>
                <Link
                  to={`/evaluations/${c.latestRunId}`}
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
