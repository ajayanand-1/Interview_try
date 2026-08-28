import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { FileCheck, Download, ExternalLink, ArrowRight, ShieldCheck } from 'lucide-react';
import { api } from '../api/client';
import { EvaluationSummary } from '../types/api';
import { StatusBadge } from '../components/common/StatusBadge';
import { EmptyState } from '../components/common/EmptyState';

export const Reports: React.FC = () => {
  const [evaluations, setEvaluations] = useState<EvaluationSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const data = await api.getEvaluations();
        setEvaluations(data.filter((e) => e.status === 'completed'));
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight">Executive Reports & Deliverables</h1>
        <p className="text-xs text-slate-400">Publication-quality hiring recommendations with 100% evidence resolution</p>
      </div>

      {loading ? (
        <div className="p-12 text-center text-slate-400 text-sm">
          <div className="inline-block w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mb-2"></div>
          <p>Loading report deliverables...</p>
        </div>
      ) : evaluations.length === 0 ? (
        <EmptyState
          title="No completed reports available"
          description="Reports are generated automatically once an evaluation panel finishes debate."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {evaluations.map((e) => (
            <div
              key={e.run_id}
              className="bg-[#131D31] border border-slate-800/80 rounded-xl p-6 hover:border-slate-700 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-mono text-slate-400">{e.run_id}</span>
                  <StatusBadge status={e.status} size="sm" />
                </div>
                <h3 className="text-lg font-bold text-white tracking-tight">{e.candidate_name}</h3>
                <p className="text-xs text-slate-400 font-mono">Role: {e.job_id}</p>
                <div className="mt-3 flex items-center gap-2 text-xs text-slate-300">
                  <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>100% Evidence Traceability Index Included</span>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-center justify-between gap-3">
                <Link
                  to={`/evaluations/${e.run_id}`}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium transition-colors"
                >
                  View in UI <ExternalLink className="w-3.5 h-3.5" />
                </Link>

                <a
                  href={api.getReportPdfUrl(e.run_id)}
                  download
                  className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold shadow-sm transition-colors"
                >
                  <Download className="w-3.5 h-3.5" />
                  Download PDF
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
