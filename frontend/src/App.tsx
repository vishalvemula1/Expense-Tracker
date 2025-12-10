import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Layout } from './components/layout/Layout';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { Expenses } from './pages/Expenses';
import { Categories } from './pages/Categories';
import type { ReactNode } from 'react';

// Protected Route Component
const ProtectedRoute = ({ children }: { children: ReactNode }) => {
  const { isAuthenticated, loading } = useAuth();
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }
  if (!isAuthenticated) return <Navigate to="/login" />;
  return <>{children}</>;
};

// Public Route - redirect to dashboard if already logged in
const PublicRoute = ({ children }: { children: ReactNode }) => {
  const { isAuthenticated, loading } = useAuth();
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }
  if (isAuthenticated) return <Navigate to="/dashboard" />;
  return <>{children}</>;
};

const Landing = () => (
  <div className="flex flex-col items-center justify-center min-h-[70vh] text-center space-y-6 px-4">
    <div className="glass-panel p-12 rounded-2xl max-w-2xl w-full relative overflow-hidden group">
      <h1 className="text-5xl sm:text-6xl font-bold text-white mb-4">
        Expense Tracker
      </h1>
      <p className="text-zinc-400 text-lg sm:text-xl max-w-md mx-auto">
        Track, analyze, and optimize your spending with precision.
      </p>
      <div className="flex flex-col sm:flex-row justify-center gap-3 mt-10">
        <a href="/register" className="btn-primary text-center px-8 py-3.5">
          Get Started
        </a>
        <a href="/login" className="btn-secondary text-center px-8 py-3.5">
          Sign In
        </a>
      </div>
    </div>
  </div>
);

function App() {
  return (
    <AuthProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={
              <PublicRoute><Login /></PublicRoute>
            } />
            <Route path="/register" element={
              <PublicRoute><Register /></PublicRoute>
            } />
            <Route path="/dashboard" element={
              <ProtectedRoute><Dashboard /></ProtectedRoute>
            } />
            <Route path="/expenses" element={
              <ProtectedRoute><Expenses /></ProtectedRoute>
            } />
            <Route path="/categories" element={
              <ProtectedRoute><Categories /></ProtectedRoute>
            } />
          </Routes>
        </Layout>
      </Router>
    </AuthProvider>
  );
}

export default App;
