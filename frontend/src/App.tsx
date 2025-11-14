import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from '@/components/Layout';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { Login } from '@/pages/Login';
import { Signup } from '@/pages/Signup';
import { Dashboard } from '@/pages/Dashboard';
import { Categories } from '@/pages/Categories';
import { Expenses } from '@/pages/Expenses';
import { Profile } from '@/pages/Profile';
import { useAuthStore } from '@/store/auth';

function App() {
  const { isAuthenticated } = useAuthStore();

  // Handle API errors globally
  useEffect(() => {
    const handleError = (error: Error) => {
      if (error.message === 'UNAUTHORIZED') {
        // Token expired or invalid
        useAuthStore.getState().logout();
        window.location.href = '/login';
      } else if (error.message === 'FORBIDDEN') {
        // Access denied
        alert('You do not have permission to perform this action');
      } else if (error.message === 'NOT_FOUND') {
        // Resource not found
        alert('The requested resource was not found');
      }
    };

    // Set up global error handling if needed
    window.addEventListener('unhandledrejection', (event) => {
      if (event.reason instanceof Error) {
        handleError(event.reason);
      }
    });

    return () => {
      window.removeEventListener('unhandledrejection', () => {});
    };
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route
          path="/login"
          element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login />}
        />
        <Route
          path="/signup"
          element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Signup />}
        />

        {/* Protected routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/expenses"
          element={
            <ProtectedRoute>
              <Layout>
                <Expenses />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/categories"
          element={
            <ProtectedRoute>
              <Layout>
                <Categories />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Layout>
                <Profile />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* Default redirect */}
        <Route
          path="/"
          element={<Navigate to={isAuthenticated ? '/dashboard' : '/login'} replace />}
        />

        {/* 404 Not Found */}
        <Route
          path="*"
          element={
            <div className="flex min-h-screen items-center justify-center bg-gray-50">
              <div className="text-center">
                <h1 className="text-6xl font-bold text-gray-900">404</h1>
                <p className="mt-4 text-xl text-gray-600">Page not found</p>
                <a href="/" className="mt-6 inline-block btn btn-primary">
                  Go Home
                </a>
              </div>
            </div>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
