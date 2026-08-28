import React from 'react';
import { EvaluationStatusType, EvaluationPhaseType } from '../../types/api';

interface StatusBadgeProps {
  status?: EvaluationStatusType | string;
  phase?: EvaluationPhaseType | string;
  verdict?: string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, phase, verdict, size = 'md' }) => {
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs font-medium';

  if (verdict) {
    const isHire = verdict.toLowerCase().includes('hire') && !verdict.toLowerCase().includes('no');
    return (
      <span
        className={`inline-flex items-center gap-1.5 rounded-full font-mono uppercase tracking-wider font-semibold ${sizeClasses} ${
          isHire
            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
            : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
        }`}
      >
        <span className={`w-1.5 h-1.5 rounded-full ${isHire ? 'bg-emerald-400' : 'bg-rose-400'}`}></span>
        {verdict.replace('_', ' ')}
      </span>
    );
  }

  if (status) {
    switch (status.toLowerCase()) {
      case 'completed':
        return (
          <span className={`inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 ${sizeClasses}`}>
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            Completed
          </span>
        );
      case 'running':
        return (
          <span className={`inline-flex items-center gap-1.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 animate-pulse ${sizeClasses}`}>
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400"></span>
            Running ({phase || 'active'})
          </span>
        );
      case 'queued':
        return (
          <span className={`inline-flex items-center gap-1.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 ${sizeClasses}`}>
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
            Queued
          </span>
        );
      case 'failed':
        return (
          <span className={`inline-flex items-center gap-1.5 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20 ${sizeClasses}`}>
            <span className="w-1.5 h-1.5 rounded-full bg-rose-400"></span>
            Failed
          </span>
        );
      default:
        return (
          <span className={`inline-flex items-center gap-1.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700 ${sizeClasses}`}>
            {status}
          </span>
        );
    }
  }

  return null;
};
