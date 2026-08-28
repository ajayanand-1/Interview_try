import React from 'react';

interface CitationBadgeProps {
  citationId: string;
  onClick?: (citationId: string) => void;
  className?: string;
}

export const CitationBadge: React.FC<CitationBadgeProps> = ({
  citationId,
  onClick,
  className = '',
}) => {
  const isResume = citationId.startsWith('R-');
  const isTranscript = citationId.startsWith('T-');

  return (
    <button
      type="button"
      onClick={(e) => {
        e.stopPropagation();
        onClick?.(citationId);
      }}
      title={`Inspect source evidence for ${citationId}`}
      className={`inline-flex items-center gap-1 font-mono text-[11px] font-semibold px-2 py-0.5 rounded transition-all cursor-pointer select-none ${
        isResume
          ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 hover:bg-cyan-500/20 hover:border-cyan-500/40'
          : isTranscript
          ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 hover:bg-indigo-500/20 hover:border-indigo-500/40'
          : 'bg-slate-800 text-slate-300 border border-slate-700 hover:bg-slate-700'
      } ${className}`}
    >
      <span>{citationId}</span>
    </button>
  );
};
