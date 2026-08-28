import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, Sparkles, CheckCircle2, AlertCircle, ArrowRight } from 'lucide-react';
import { api } from '../api/client';

export const NewEvaluation: React.FC = () => {
  const navigate = useNavigate();

  const [candidateName, setCandidateName] = useState('');
  const [candidateId, setCandidateId] = useState('');
  const [jobId, setJobId] = useState('ai_engineer_freight');
  const [runId, setRunId] = useState('');

  const [jdFile, setJdFile] = useState<File | null>(null);
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [transcriptFile, setTranscriptFile] = useState<File | null>(null);

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setCandidateName(val);
    if (!candidateId || candidateId === candidateName.toLowerCase().replace(/\s+/g, '_')) {
      setCandidateId(val.toLowerCase().replace(/[^a-z0-9_]/g, '_'));
    }
  };

  const setPreset = (name: string, id: string) => {
    setCandidateName(name);
    setCandidateId(id);
    setJobId('ai_engineer_freight');
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!candidateId.trim()) {
      setError('Candidate ID is required');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);

      const formData = new FormData();
      formData.append('candidate_id', candidateId.trim());
      if (candidateName.trim()) formData.append('candidate_name', candidateName.trim());
      if (jobId.trim()) formData.append('job_id', jobId.trim());
      if (runId.trim()) formData.append('run_id', runId.trim());

      if (jdFile) formData.append('job_description_file', jdFile);
      if (resumeFile) formData.append('resume_file', resumeFile);
      if (transcriptFile) formData.append('transcript_file', transcriptFile);

      const res = await api.createEvaluation(formData);
      navigate(`/evaluations/${res.run_id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to initiate evaluation run');
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight">Configure New Evaluation</h1>
        <p className="text-xs text-slate-400">Initialize a run-scoped multi-agent evaluation workspace</p>
      </div>

      {/* Preset Fast-Fills */}
      <div className="bg-[#131D31] border border-slate-800 rounded-xl p-4 flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs text-slate-300">
          <Sparkles className="w-4 h-4 text-indigo-400" />
          <span>Quick Demo Presets:</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setPreset('Ananya Iyer', 'ananya_iyer')}
            className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-indigo-300 rounded text-xs font-mono font-medium transition-colors"
          >
            Ananya Iyer
          </button>
          <button
            type="button"
            onClick={() => setPreset('Rohan Malhotra', 'rohan_malhotra')}
            className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-indigo-300 rounded text-xs font-mono font-medium transition-colors"
          >
            Rohan Malhotra
          </button>
        </div>
      </div>

      {/* Main Form */}
      <form onSubmit={handleSubmit} className="bg-[#131D31] border border-slate-800/80 rounded-xl p-6 space-y-6">
        {error && (
          <div className="p-3.5 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Candidate Full Name
            </label>
            <input
              type="text"
              placeholder="e.g. Alex Chen"
              value={candidateName}
              onChange={handleNameChange}
              className="w-full px-3.5 py-2 bg-[#0B1120] border border-slate-700/60 rounded-lg text-sm text-slate-100 placeholder-slate-400 focus:outline-none focus:border-indigo-500 transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Candidate Slug / ID <span className="text-rose-400">*</span>
            </label>
            <input
              type="text"
              required
              placeholder="e.g. alex_chen"
              value={candidateId}
              onChange={(e) => setCandidateId(e.target.value)}
              className="w-full px-3.5 py-2 bg-[#0B1120] border border-slate-700/60 rounded-lg text-sm text-slate-100 placeholder-slate-400 font-mono focus:outline-none focus:border-indigo-500 transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Target Role / Job ID
            </label>
            <input
              type="text"
              placeholder="e.g. ai_engineer_freight"
              value={jobId}
              onChange={(e) => setJobId(e.target.value)}
              className="w-full px-3.5 py-2 bg-[#0B1120] border border-slate-700/60 rounded-lg text-sm text-slate-100 placeholder-slate-400 font-mono focus:outline-none focus:border-indigo-500 transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Custom Run Identifier (Optional)
            </label>
            <input
              type="text"
              placeholder="Leave blank for automatic UUID"
              value={runId}
              onChange={(e) => setRunId(e.target.value)}
              className="w-full px-3.5 py-2 bg-[#0B1120] border border-slate-700/60 rounded-lg text-sm text-slate-100 placeholder-slate-400 font-mono focus:outline-none focus:border-indigo-500 transition-colors"
            />
          </div>
        </div>

        <hr className="border-slate-800/80 my-4" />

        {/* File Uploads Section */}
        <div>
          <h3 className="text-sm font-bold text-white mb-1">Evaluation Source Files (PDF)</h3>
          <p className="text-xs text-slate-400 mb-4">
            Upload custom PDFs, or leave empty to use staged fixture packets from <code className="text-indigo-400">data/</code>.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Job Description File */}
            <div className="border border-dashed border-slate-700/80 rounded-xl p-4 bg-[#0B1120]/60 text-center relative hover:border-indigo-500 transition-colors">
              <input
                type="file"
                accept=".pdf"
                onChange={(e) => setJdFile(e.target.files?.[0] || null)}
                className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
              />
              <FileText className="w-6 h-6 text-slate-400 mx-auto mb-2" />
              <div className="text-xs font-semibold text-slate-200">Job Description</div>
              <div className="text-[11px] text-slate-400 mt-1 truncate">
                {jdFile ? jdFile.name : 'Upload PDF'}
              </div>
            </div>

            {/* Resume File */}
            <div className="border border-dashed border-slate-700/80 rounded-xl p-4 bg-[#0B1120]/60 text-center relative hover:border-indigo-500 transition-colors">
              <input
                type="file"
                accept=".pdf"
                onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
                className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
              />
              <FileText className="w-6 h-6 text-slate-400 mx-auto mb-2" />
              <div className="text-xs font-semibold text-slate-200">Candidate Resume</div>
              <div className="text-[11px] text-slate-400 mt-1 truncate">
                {resumeFile ? resumeFile.name : 'Upload PDF'}
              </div>
            </div>

            {/* Transcript File */}
            <div className="border border-dashed border-slate-700/80 rounded-xl p-4 bg-[#0B1120]/60 text-center relative hover:border-indigo-500 transition-colors">
              <input
                type="file"
                accept=".pdf"
                onChange={(e) => setTranscriptFile(e.target.files?.[0] || null)}
                className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
              />
              <FileText className="w-6 h-6 text-slate-400 mx-auto mb-2" />
              <div className="text-xs font-semibold text-slate-200">Interview Transcript</div>
              <div className="text-[11px] text-slate-400 mt-1 truncate">
                {transcriptFile ? transcriptFile.name : 'Upload PDF'}
              </div>
            </div>
          </div>
        </div>

        {/* Form Actions */}
        <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
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
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 disabled:opacity-50 text-white text-xs font-semibold rounded-lg shadow-sm shadow-indigo-600/30 transition-all"
          >
            {submitting ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Creating Workspace...</span>
              </>
            ) : (
              <>
                <span>Launch Evaluation Panel</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
