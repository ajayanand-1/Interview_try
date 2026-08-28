import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { Dashboard } from './pages/Dashboard';
import { EvaluationList } from './pages/EvaluationList';
import { NewEvaluation } from './pages/NewEvaluation';
import { EvaluationDetail } from './pages/EvaluationDetail';
import { CandidateList } from './pages/CandidateList';
import { JobList } from './pages/JobList';
import { Reports } from './pages/Reports';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="evaluations" element={<EvaluationList />} />
          <Route path="evaluations/new" element={<NewEvaluation />} />
          <Route path="evaluations/:run_id" element={<EvaluationDetail />} />
          <Route path="candidates" element={<CandidateList />} />
          <Route path="jobs" element={<JobList />} />
          <Route path="reports" element={<Reports />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};
export default App;
