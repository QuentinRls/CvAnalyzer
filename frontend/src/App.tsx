import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

// Pages
import Login from './pages/Login.tsx';
import Dashboard from './pages/Dashboard.tsx';
import NewDossier from './pages/NewDossier.tsx';
import Review from './pages/Review.tsx';
import Compare from './pages/Compare.tsx';
import CompareResult from './pages/CompareResult.tsx';
import CVHistory from './pages/CVHistory.tsx';

function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen" style={{ backgroundColor: 'var(--bg)' }}>
        <main>
          <Routes>
            {/* Routes publiques */}
            <Route path="/login" element={<Login />} />
            
            {/* Routes protégées */}
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/new" 
              element={
                <ProtectedRoute>
                  <NewDossier />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/review" 
              element={
                <ProtectedRoute>
                  <Review />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/compare" 
              element={
                <ProtectedRoute>
                  <Compare />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/compare/result" 
              element={
                <ProtectedRoute>
                  <CompareResult />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/history" 
              element={
                <ProtectedRoute>
                  <CVHistory />
                </ProtectedRoute>
              } 
            />
            
            {/* Route racine - rediriger vers dashboard si connecté */}
            <Route 
              path="/" 
              element={
                <ProtectedRoute>
                  <Navigate to="/dashboard" replace />
                </ProtectedRoute>
              } 
            />
            
            {/* Fallback pour routes non trouvées */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </main>
      </div>
    </AuthProvider>
  );
}

export default App;
