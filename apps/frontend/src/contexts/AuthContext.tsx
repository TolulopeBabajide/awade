import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import apiService from '../services/api';

interface User {
  user_id: number;
  email: string;
  full_name: string;
  role: string;
  country: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  signup: (userData: any) => Promise<boolean>;
  googleAuth: (credential: string, role?: string) => Promise<boolean>;
  logout: () => Promise<void>;
  validateToken: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  /**
   * Verify session by calling /api/auth/me.
   * The access_token is an HttpOnly cookie — no localStorage check needed.
   */
  const validateToken = async (): Promise<boolean> => {
    try {
      const response = await apiService.getCurrentUser();

      if (response.error) {
        return false;
      }

      if (response.data) {
        setUser(response.data);
        return true;
      }

      return false;
    } catch {
      return false;
    }
  };

  /**
   * Clear server-side cookies and local state, then redirect to login.
   * The api.ts logout() helper fires the server call; here we just update UI state.
   */
  const logout = async (): Promise<void> => {
    await apiService.logoutUser().catch(() => undefined);
    setUser(null);
    navigate('/login');
  };

  useEffect(() => {
    // On mount, silently probe the backend to restore session from cookie.
    const initializeAuth = async () => {
      await validateToken();
      setIsLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const response = await apiService.login(email, password);

      if (response.error) {
        return false;
      }

      if (response.data) {
        // Backend sets the access_token cookie; we only need the user payload.
        setUser(response.data.user);
        return true;
      }

      return false;
    } catch {
      return false;
    }
  };

  const googleAuth = async (credential: string, role?: string): Promise<boolean> => {
    try {
      const response = await apiService.googleAuth(credential, role);

      if (response.error) {
        return false;
      }

      if (response.data) {
        setUser(response.data.user);
        return true;
      }

      return false;
    } catch {
      return false;
    }
  };

  const signup = async (userData: any): Promise<boolean> => {
    try {
      const response = await apiService.signup(userData);

      if (response.error) {
        return false;
      }

      if (response.data) {
        setUser(response.data.user);
        return true;
      }

      return false;
    } catch {
      return false;
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    signup,
    googleAuth,
    logout,
    validateToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
