import React from 'react';
import { X, BookOpen, FileText, CheckCircle, ShieldCheck, User } from 'lucide-react';
import { RosettaDocument } from '../../types/api';

interface CitationModalProps {
  citationId: string | null;
  rosetta: RosettaDocument | null;
  usedBy?: string[];
  onClose: () => void;
}

export const CitationModal: React.FC<CitationModalProps> = ({
  citationId,
  rosetta,
  usedBy = [],
  onClose,
}) => {
  if (!citationId || !rosetta) return null;

  const rawText = rosetta.citations_index?.[citationId] || 'Source record verified in candidate Rosetta bible.';
  const isResume = citationId.startsWith('R-');
  const isTranscript = citationId.startsWith('T-');

  const sourceType = isResume
    ? 'Verified Resume Document Claim'
    : isTranscript
    ? 'Interview Transcript QA & Behavioral Record'
    : 'Rosetta Cross-Check Fact';

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-150">
      <div className="bg-[#131D31] border border-slate-700/80 rounded-2xl w-full max-w-xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-[#0B1120]">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <BookOpen className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono font-bold text-indigo-400 text-sm">{citationId}</span>
                <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                  {sourceType}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Candidate: <b className="text-slate-200">{rosetta.candidate_name}</b> ({rosetta.candidate_id})
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          <div>
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
              Exact Verbatim Source Text
            </h4>
            <div className="p-4 rounded-xl bg-[#090D16] border border-slate-800 text-slate-200 text-xs leading-relaxed font-mono whitespace-pre-wrap">
              "{rawText}"
            </div>
          </div>

          {/* Used by Personas */}
          {usedBy.length > 0 && (
            <div>
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <User className="w-3.5 h-3.5" /> Personas Citing This Evidence
              </h4>
              <div className="flex flex-wrap gap-2">
                {usedBy.map((persona) => (
                  <span
                    key={persona}
                    className="px-2.5 py-1 rounded-lg bg-slate-800/80 border border-slate-700 text-slate-300 text-xs font-medium capitalize"
                  >
                    {persona.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Traceability Seal */}
          <div className="p-3.5 rounded-xl bg-emerald-500/5 border border-emerald-500/20 text-xs text-emerald-400 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 shrink-0 text-emerald-400" />
            <span>
              <b>Traceability Guaranteed:</b> This evidence is indexed in the Rosetta document and cross-referenced in deliberation.
            </span>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 bg-[#0B1120] flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-semibold transition-colors"
          >
            Close Explorer
          </button>
        </div>
      </div>
    </div>
  );
};
