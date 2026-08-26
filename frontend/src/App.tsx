import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import Sidebar from './components/Sidebar';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import CamerasPage from './pages/CamerasPage';
import VehicleSearchPage from './pages/VehicleSearchPage';
import AnalyticsPage from './pages/AnalyticsPage';
import AlertsPage from './pages/AlertsPage';
import WatchlistPage from './pages/WatchlistPage';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

function App() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {isAuthenticated && <Sidebar />}
      <main className="flex-1 overflow-y-auto">
        <Routes>
          <Route path="/login" element={!isAuthenticated ? <LoginPage /> : <Navigate to="/dashboard" replace />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          <Route path="/cameras" element={<ProtectedRoute><CamerasPage /></ProtectedRoute>} />
          <Route path="/vehicles" element={<ProtectedRoute><VehicleSearchPage /></ProtectedRoute>} />
          <Route path="/analytics" element={<ProtectedRoute><AnalyticsPage /></ProtectedRoute>} />
          <Route path="/alerts" element={<ProtectedRoute><AlertsPage /></ProtectedRoute>} />
          <Route path="/watchlist" element={<ProtectedRoute><WatchlistPage /></ProtectedRoute>} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
