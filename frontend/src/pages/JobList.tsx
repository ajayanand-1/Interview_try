import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Briefcase, Users, PlusCircle, ArrowRight } from 'lucide-react';
import { api } from '../api/client';
import { EvaluationSummary } from '../types/api';
import { EmptyState } from '../components/common/EmptyState';

export const JobList: React.FC = () => {
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

  // Aggregate by job_id
  const jobMap: Record<string, { jobId: string; count: number; candidates: Set<string> }> = {};

  evaluations.forEach((e) => {
    const jId = e.job_id || 'ai_engineer_freight';
    if (!jobMap[jId]) {
      jobMap[jId] = {
        jobId: jId,
        count: 1,
        candidates: new Set([e.candidate_name]),
      };
    } else {
      jobMap[jId].count += 1;
      jobMap[jId].candidates.add(e.candidate_name);
    }
  });

  const jobs = Object.values(jobMap);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Target Role Specifications</h1>
          <p className="text-xs text-slate-400">Open positions and candidate pipeline allocations</p>
        </div>
        <Link
          to="/evaluations/new"
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold shadow-sm transition-colors"
        >
          <PlusCircle className="w-3.5 h-3.5" />
          Evaluate for Job
        </Link>
      </div>

      {loading ? (
        <div className="p-12 text-center text-slate-400 text-sm">
          <div className="inline-block w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mb-2"></div>
          <p>Loading job specifications...</p>
        </div>
      ) : jobs.length === 0 ? (
        <EmptyState
          title="No target jobs configured"
          description="Create your first evaluation to link candidate pipelines to a role."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {jobs.map((j) => (
            <div key={j.jobId} className="bg-[#131D31] border border-slate-800/80 rounded-xl p-6 hover:border-slate-700 transition-all">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2.5 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  <Briefcase className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white uppercase tracking-wider font-mono text-sm">
                    {j.jobId.replace(/_/g, ' ')}
                  </h3>
                  <p className="text-xs text-slate-400 font-mono">Job ID: {j.jobId}</p>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-300">
                <div className="flex items-center gap-2">
                  <Users className="w-4 h-4 text-slate-400" />
                  <span>
                    <b>{j.candidates.size}</b> candidate{j.candidates.size > 1 ? 's' : ''} evaluated ({j.count} runs)
                  </span>
                </div>
                <Link
                  to="/evaluations"
                  className="inline-flex items-center gap-1 font-semibold text-indigo-400 hover:text-indigo-300"
                >
                  View Pipeline <ArrowRight className="w-3 h-3" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
