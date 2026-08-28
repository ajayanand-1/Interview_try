import React from 'react';
import { useLocation, Link } from 'react-router-dom';
import { Search, Plus } from 'lucide-react';

interface TopbarProps {
  onSearch?: (query: string) => void;
}

export const Topbar: React.FC<TopbarProps> = ({ onSearch }) => {
  const location = useLocation();

  const getPageTitle = () => {
    const path = location.pathname;
    if (path === '/') return 'Overview Dashboard';
    if (path === '/evaluations') return 'Evaluation Sessions';
    if (path === '/evaluations/new') return 'Configure New Evaluation';
    if (path.startsWith('/evaluations/')) return 'Evaluation Details & Transcripts';
    if (path === '/candidates') return 'Candidate Directory';
    if (path === '/jobs') return 'Active Job Profiles';
    if (path === '/reports') return 'Executive Reports & Deliverables';
    return 'Prompt Wars Intelligence';
  };

  return (
    <header className="h-16 bg-[#090D16]/90 backdrop-blur border-b border-slate-800/80 px-8 flex items-center justify-between sticky top-0 z-20">
      <div>
        <h2 className="text-lg font-bold text-white tracking-tight">{getPageTitle()}</h2>
        <p className="text-xs text-slate-400">Evidence-grounded multi-agent hiring intelligence</p>
      </div>

      <div className="flex items-center gap-4">
        {/* Search Input */}
        <div className="relative w-64">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search candidates, runs..."
            onChange={(e) => onSearch?.(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-[#131D31] border border-slate-700/60 rounded-lg text-slate-200 placeholder-slate-400 focus:outline-none focus:border-indigo-500 transition-colors"
          />
        </div>

        {/* Action Button */}
        <Link
          to="/evaluations/new"
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors shadow-sm"
        >
          <Plus className="w-3.5 h-3.5" />
          New Evaluation
        </Link>
      </div>
    </header>
  );
};
