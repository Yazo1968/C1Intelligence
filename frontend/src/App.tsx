import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './auth/AuthContext';
import { AuthGuard } from './auth/AuthGuard';
import { LoginPage } from './pages/LoginPage';
import { ProjectsPage } from './pages/ProjectsPage';
import { ProjectWorkspacePage } from './pages/ProjectWorkspacePage';
import { AuditLogPage } from './pages/AuditLogPage';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/projects" element={<AuthGuard><ProjectsPage /></AuthGuard>} />
          <Route path="/projects/:projectId" element={<AuthGuard><ProjectWorkspacePage /></AuthGuard>} />
          <Route path="/projects/:projectId/audit-log" element={<AuthGuard><AuditLogPage /></AuthGuard>} />
          <Route path="*" element={<Navigate to="/projects" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
