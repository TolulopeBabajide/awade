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
  logout: () => void;
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

  // Validate token with backend
  const validateToken = async (): Promise<boolean> => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return false;
    }

    try {
      const response = await apiService.getCurrentUser();
      
      if (response.error) {
        // Token is invalid or expired
        logout();
        return false;
      }

      if (response.data) {
        setUser(response.data);
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Token validation error:', error);
      logout();
      return false;
    }
  };

  // Enhanced logout function
  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_data');
    setUser(null);
    // Redirect to login page
    navigate('/login');
  };

  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('access_token');
      const userData = localStorage.getItem('user_data');
      
      if (token && userData) {
        try {
          // Validate token with backend
          const isValid = await validateToken();
          if (!isValid) {
            // Token is invalid, clear storage
            localStorage.removeItem('access_token');
            localStorage.removeItem('user_data');
          }
        } catch (error) {
          console.error('Error validating token:', error);
          localStorage.removeItem('access_token');
          localStorage.removeItem('user_data');
        }
      }
      
      setIsLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const response = await apiService.login(email, password);
      
      if (response.error) {
        console.error('Login error:', response.error);
        return false;
      }

      if (response.data) {
        const { access_token, user: userData } = response.data;
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('user_data', JSON.stringify(userData));
        setUser(userData);
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const signup = async (userData: any): Promise<boolean> => {
    try {
      const response = await apiService.signup(userData);
      
      if (response.error) {
        console.error('Signup error:', response.error);
        return false;
      }

      if (response.data) {
        const { access_token, user: newUser } = response.data;
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('user_data', JSON.stringify(newUser));
        setUser(newUser);
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Signup error:', error);
      return false;
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    signup,
    logout,
    validateToken
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 