import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface ParentRouteProps {
  children: React.ReactNode;
}

const ParentRoute: React.FC<ParentRouteProps> = ({ children }) => {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Only PARENT role may access these routes
  if (!user || user.role !== 'PARENT') {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};

export default ParentRoute;
