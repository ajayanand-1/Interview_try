import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Upload,
  FileText,
  Sparkles,
  Plus,
  Trash2,
  AlertCircle,
  ArrowRight,
  Users,
  CheckCircle2,
} from 'lucide-react';
import { api } from '../api/client';

interface CandidateFormEntry {
  id: string;
  name: string;
  slug: string;
  resumeFile: File | null;
  transcriptFile: File | null;
}

export const NewEvaluation: React.FC = () => {
  const navigate = useNavigate();

  const [jobId, setJobId] = useState('ai_engineer_freight');
  const [jdFile, setJdFile] = useState<File | null>(null);

  const [candidates, setCandidates] = useState<CandidateFormEntry[]>([
    {
      id: 'c-1',
      name: '',
      slug: '',
      resumeFile: null,
      transcriptFile: null,
    },
  ]);

  const [submitting, setSubmitting] = useState(false);
  const [batchProgress, setBatchProgress] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const addCandidateEntry = () => {
    const nextIdx = candidates.length + 1;
    setCandidates([
      ...candidates,
      {
        id: `c-${Date.now()}`,
        name: '',
        slug: '',
        resumeFile: null,
        transcriptFile: null,
      },
    ]);
  };

  const removeCandidateEntry = (id: string) => {
    if (candidates.length <= 1) return;
    setCandidates(candidates.filter((c) => c.id !== id));
  };

  const updateCandidate = (id: string, field: keyof CandidateFormEntry, value: any) => {
    setCandidates(
      candidates.map((c) => {
        if (c.id !== id) return c;
        const updated = { ...c, [field]: value };
        if (field === 'name' && (!c.slug || c.slug === c.name.toLowerCase().replace(/\s+/g, '_'))) {
          updated.slug = (value as string).toLowerCase().replace(/[^a-z0-9_]/g, '_');
        }
        return updated;
      })
    );
  };

  const setPresetDemo = (presetName: 'ananya' | 'rohan' | 'both') => {
    setJobId('ai_engineer_freight');
    setError(null);

    if (presetName === 'ananya') {
      setCandidates([
        {
          id: 'c-ananya',
          name: 'Ananya Iyer',
          slug: 'ananya_iyer',
          resumeFile: null,
          transcriptFile: null,
        },
      ]);
    } else if (presetName === 'rohan') {
      setCandidates([
        {
          id: 'c-rohan',
          name: 'Rohan Malhotra',
          slug: 'rohan_malhotra',
          resumeFile: null,
          transcriptFile: null,
        },
      ]);
    } else {
      setCandidates([
        {
          id: 'c-ananya',
          name: 'Ananya Iyer',
          slug: 'ananya_iyer',
          resumeFile: null,
          transcriptFile: null,
        },
        {
          id: 'c-rohan',
          name: 'Rohan Malhotra',
          slug: 'rohan_malhotra',
          resumeFile: null,
          transcriptFile: null,
        },
      ]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    const cleanJob = jobId.trim() || 'default_job';
    const seenSlugs = new Set<string>();

    for (let i = 0; i < candidates.length; i++) {
      const c = candidates[i];
      const cleanSlug = c.slug.trim();
      if (!cleanSlug) {
        setError(`Candidate #${i + 1} must have a valid Candidate ID / slug.`);
        return;
      }
      if (seenSlugs.has(cleanSlug)) {
        setError(`Duplicate Candidate ID "${cleanSlug}" detected in batch. Each candidate ID must be unique.`);
        return;
      }
      seenSlugs.add(cleanSlug);
    }

    try {
      setSubmitting(true);
      setError(null);
      const createdRuns: string[] = [];

      for (let i = 0; i < candidates.length; i++) {
        const c = candidates[i];
        setBatchProgress(`Launching evaluation ${i + 1} of ${candidates.length} (${c.name || c.slug})...`);

        const formData = new FormData();
        formData.append('candidate_id', c.slug.trim());
        if (c.name.trim()) formData.append('candidate_name', c.name.trim());
        formData.append('job_id', cleanJob);

        if (jdFile) formData.append('job_description_file', jdFile);
        if (c.resumeFile) formData.append('resume_file', c.resumeFile);
        if (c.transcriptFile) formData.append('transcript_file', c.transcriptFile);

        const res = await api.createEvaluation(formData);
        createdRuns.push(res.run_id);
      }

      if (createdRuns.length === 1) {
        navigate(`/evaluations/${createdRuns[0]}`);
      } else {
        navigate('/evaluations');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to submit candidate evaluations');
      setSubmitting(false);
      setBatchProgress(null);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight">Configure New Evaluation Panel</h1>
        <p className="text-xs text-slate-400">
          Upload a Job Description and 1 or more candidates to launch isolated multi-agent deliberations
        </p>
      </div>

      {/* Preset Demo Buttons */}
      <div className="bg-[#131D31] border border-slate-800 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-xs text-slate-300">
          <Sparkles className="w-4 h-4 text-indigo-400 shrink-0" />
          <span>Quick Demo Packets (Staged Fixtures):</span>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <button
            type="button"
            onClick={() => setPresetDemo('ananya')}
            className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-indigo-300 rounded text-xs font-mono font-medium transition-colors"
          >
            Ananya Iyer
          </button>
          <button
            type="button"
            onClick={() => setPresetDemo('rohan')}
            className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-indigo-300 rounded text-xs font-mono font-medium transition-colors"
          >
            Rohan Malhotra
          </button>
          <button
            type="button"
            onClick={() => setPresetDemo('both')}
            className="px-3 py-1 bg-indigo-900/40 hover:bg-indigo-900/60 text-indigo-200 border border-indigo-500/30 rounded text-xs font-mono font-semibold transition-colors"
          >
            Batch: Both Candidates (1 Job + 2 Candidates)
          </button>
        </div>
      </div>

      {/* Main Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center gap-2.5">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Section 1: Job Description */}
        <div className="bg-[#131D31] border border-slate-800/80 rounded-xl p-6 space-y-4">
          <div className="flex items-center gap-2">
            <span className="w-6 h-6 rounded-full bg-indigo-600/20 text-indigo-400 flex items-center justify-center font-bold text-xs">
              1
            </span>
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">Target Job Specification</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                Target Role / Job ID <span className="text-rose-400">*</span>
              </label>
              <input
                type="text"
                required
                value={jobId}
                onChange={(e) => setJobId(e.target.value)}
                placeholder="e.g. ai_engineer_freight"
                className="w-full px-3.5 py-2 bg-[#0B1120] border border-slate-700/60 rounded-lg text-sm text-slate-100 placeholder-slate-400 font-mono focus:outline-none focus:border-indigo-500 transition-colors"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                Job Description Document (PDF)
              </label>
              <div className="border border-dashed border-slate-700/80 rounded-lg p-2.5 bg-[#0B1120] text-center relative hover:border-indigo-500 transition-colors">
                <input
                  type="file"
                  accept=".pdf,.txt"
                  onChange={(e) => setJdFile(e.target.files?.[0] || null)}
                  className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
                />
                <div className="text-xs text-slate-300 flex items-center justify-center gap-2 truncate">
                  <FileText className="w-4 h-4 text-indigo-400 shrink-0" />
                  <span className="truncate">{jdFile ? jdFile.name : 'Upload custom JD PDF or use default'}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Section 2: Candidate Entries (1 or N Candidates) */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-indigo-600/20 text-indigo-400 flex items-center justify-center font-bold text-xs">
                2
              </span>
              <h2 className="text-sm font-bold text-white uppercase tracking-wider">
                Candidates to Evaluate ({candidates.length})
              </h2>
            </div>
            <button
              type="button"
              onClick={addCandidateEntry}
              className="inline-flex items-center gap-1.5 px-3 py-1 bg-[#131D31] hover:bg-slate-800 border border-slate-700 text-indigo-400 rounded-lg text-xs font-semibold transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              Add Candidate
            </button>
          </div>

          {candidates.map((cand, idx) => (
            <div
              key={cand.id}
              className="bg-[#131D31] border border-slate-800/80 rounded-xl p-6 space-y-4 relative group"
            >
              <div className="flex items-center justify-between border-b border-slate-800/60 pb-3">
                <span className="text-xs font-bold text-slate-300 font-mono">Candidate #{idx + 1}</span>
                {candidates.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeCandidateEntry(cand.id)}
                    className="p-1 text-slate-400 hover:text-rose-400 transition-colors"
                    title="Remove candidate"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                    Candidate Full Name
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Alex Chen"
                    value={cand.name}
                    onChange={(e) => updateCandidate(cand.id, 'name', e.target.value)}
                    className="w-full px-3.5 py-2 bg-[#0B1120] border border-slate-700/60 rounded-lg text-sm text-slate-100 placeholder-slate-400 focus:outline-none focus:border-indigo-500 transition-colors"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                    Candidate ID / Slug <span className="text-rose-400">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. alex_chen"
                    value={cand.slug}
                    onChange={(e) => updateCandidate(cand.id, 'slug', e.target.value)}
                    className="w-full px-3.5 py-2 bg-[#0B1120] border border-slate-700/60 rounded-lg text-sm text-slate-100 placeholder-slate-400 font-mono focus:outline-none focus:border-indigo-500 transition-colors"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                    Candidate Resume (PDF/TXT)
                  </label>
                  <div className="border border-dashed border-slate-700/80 rounded-lg p-2.5 bg-[#0B1120] text-center relative hover:border-indigo-500 transition-colors">
                    <input
                      type="file"
                      accept=".pdf,.txt"
                      onChange={(e) => updateCandidate(cand.id, 'resumeFile', e.target.files?.[0] || null)}
                      className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
                    />
                    <div className="text-xs text-slate-300 flex items-center justify-center gap-2 truncate">
                      <FileText className="w-4 h-4 text-cyan-400 shrink-0" />
                      <span className="truncate">
                        {cand.resumeFile ? cand.resumeFile.name : 'Upload Resume PDF or use demo'}
                      </span>
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                    Interview Transcript (PDF/TXT)
                  </label>
                  <div className="border border-dashed border-slate-700/80 rounded-lg p-2.5 bg-[#0B1120] text-center relative hover:border-indigo-500 transition-colors">
                    <input
                      type="file"
                      accept=".pdf,.txt"
                      onChange={(e) => updateCandidate(cand.id, 'transcriptFile', e.target.files?.[0] || null)}
                      className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
                    />
                    <div className="text-xs text-slate-300 flex items-center justify-center gap-2 truncate">
                      <FileText className="w-4 h-4 text-indigo-400 shrink-0" />
                      <span className="truncate">
                        {cand.transcriptFile ? cand.transcriptFile.name : 'Upload Transcript PDF or use demo'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-4 border-t border-slate-800">
          <div className="text-xs text-slate-400">
            {batchProgress && <span className="text-indigo-400 font-mono animate-pulse">{batchProgress}</span>}
          </div>

          <div className="flex items-center justify-end gap-3 w-full sm:w-auto">
            <button
              type="button"
              onClick={() => navigate('/evaluations')}
              className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-white transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="inline-flex items-center justify-center gap-2 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 disabled:opacity-50 text-white text-xs font-semibold rounded-lg shadow-sm shadow-indigo-600/30 transition-all w-full sm:w-auto"
            >
              {submitting ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Launching Batch...</span>
                </>
              ) : (
                <>
                  <span>
                    Start {candidates.length > 1 ? `Batch (${candidates.length} Candidates)` : 'Evaluation'}
                  </span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};
