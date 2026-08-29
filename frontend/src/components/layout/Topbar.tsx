import React from 'react';
import { useLocation, Link } from 'react-router-dom';
import { Search, Plus, Menu } from 'lucide-react';

interface TopbarProps {
  onSearch?: (query: string) => void;
  onToggleMobileMenu?: () => void;
}

export const Topbar: React.FC<TopbarProps> = ({ onSearch, onToggleMobileMenu }) => {
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
    <header className="h-16 bg-[#090D16]/95 backdrop-blur border-b border-slate-800/80 px-4 sm:px-6 lg:px-8 flex items-center justify-between sticky top-0 z-20">
      <div className="flex items-center gap-3 min-w-0">
        {/* Mobile Hamburger Button */}
        <button
          onClick={onToggleMobileMenu}
          className="lg:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors focus:outline-none"
          aria-label="Toggle Navigation Menu"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div className="min-w-0">
          <h2 className="text-sm sm:text-base lg:text-lg font-bold text-white tracking-tight truncate">{getPageTitle()}</h2>
          <p className="text-[11px] sm:text-xs text-slate-400 hidden sm:block truncate">Evidence-grounded multi-agent hiring intelligence</p>
        </div>
      </div>

      <div className="flex items-center gap-2 sm:gap-4">
        {/* Search Input - responsive width */}
        <div className="relative w-36 sm:w-56 md:w-64">
          <Search className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-slate-400 absolute left-2.5 sm:left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search..."
            onChange={(e) => onSearch?.(e.target.value)}
            className="w-full pl-8 sm:pl-9 pr-2.5 sm:pr-3 py-1 sm:py-1.5 text-xs bg-[#131D31] border border-slate-700/60 rounded-lg text-slate-200 placeholder-slate-400 focus:outline-none focus:border-indigo-500 transition-colors"
          />
        </div>

        {/* Action Button */}
        <Link
          to="/evaluations/new"
          className="inline-flex items-center gap-1 sm:gap-1.5 px-2.5 sm:px-3.5 py-1.5 text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors shadow-sm whitespace-nowrap"
        >
          <Plus className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">New Evaluation</span>
          <span className="sm:hidden">New</span>
        </Link>
      </div>
    </header>
  );
};
