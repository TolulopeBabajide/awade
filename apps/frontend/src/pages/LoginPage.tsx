import React, { useState, useEffect } from 'react';
import { GoogleLogin } from '@react-oauth/google';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import apiService from '../services/api';

function isAlphanumeric(str: string) {
  return /^[a-zA-Z0-9]+$/.test(str);
}

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  
  // Get the redirect path from location state, or default to dashboard
  const from = (location.state as any)?.from?.pathname || '/dashboard';
  const isRedirected = (location.state as any)?.from;
  
  const [form, setForm] = useState({
    email: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [showForgot, setShowForgot] = useState(false);
  const [forgotEmail, setForgotEmail] = useState('');
  const [forgotMsg, setForgotMsg] = useState<string | null>(null);

  // Google OAuth handler
  const handleGoogleSuccess = async (credentialResponse: any) => {
    setError(null);
    try {
      const response = await apiService.googleAuth(credentialResponse.credential);
      if (response.error) {
        throw new Error(response.error);
      }
      if (response.data) {
        const { access_token, user } = response.data;
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('user_data', JSON.stringify(user));
        console.log('Authenticated user:', user);
        navigate(from, { replace: true });
      }
    } catch (err: any) {
      console.error('Google OAuth error:', err);
      setError(err.message || 'Google login failed. Please try email/password login instead.');
    }
  };

  const handleGoogleError = () => {
    setError('Google Sign In was unsuccessful. Please try email/password login instead.');
  };

  // Input change handler
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  // Forgot password handler
  const handleForgotSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setForgotMsg(null);
    setError(null);
    if (!forgotEmail.trim() || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(forgotEmail)) {
      setError('Please enter a valid email address.');
      return;
    }
    setLoading(true);
    try {
      const response = await apiService.forgotPassword(forgotEmail);
      if (response.error) {
        setError('Failed to request password reset.');
      } else {
        setForgotMsg(response.data?.message || 'If the email exists, a reset link has been sent.');
      }
    } catch (err: any) {
      setError('Failed to request password reset.');
    } finally {
      setLoading(false);
    }
  };

  // Form validation
  const validate = () => {
    if (!form.email.trim() || !form.password) {
      setError('All fields are required.');
      return false;
    }
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(form.email)) {
      setError('Please enter a valid email address.');
      return false;
    }
    if (form.password.length < 8) {
      setError('Password must be at least 8 characters.');
      return false;
    }
    if (!isAlphanumeric(form.password)) {
      setError('Password must be alphanumeric.');
      return false;
    }
    setError(null);
    return true;
  };

  // Form submit handler
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    setError(null);
    
    try {
      const success = await login(form.email, form.password);
      if (success) {
        // Navigate to the originally requested page or dashboard
        navigate(from, { replace: true });
      } else {
        setError('Invalid email or password');
      }
    } catch (err: any) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
      <div className="absolute left-12 top-8 text-gray-400 text-lg">Log In</div>
      <div className="flex flex-col items-center w-full">
        {/* Logo */}
        <div className="mt-12 mb-4">
          <span className="font-bold text-2xl tracking-widest">AWADE</span>
        </div>
        <div className="bg-white rounded-md shadow-md p-8 w-full max-w-md border border-gray-300 relative">
          {/* Back arrow */}
          <button className="absolute left-4 top-4 text-gray-500 hover:text-gray-700" aria-label="Back">
            &#8592;
          </button>
          <h2 className="text-2xl font-semibold text-center mb-2">LOG IN</h2>
          <p className="text-center text-gray-500 text-sm mb-6">
            Log in to access your personalized teaching dashboard and resources.
          </p>
          
          {/* Show redirect message if user was redirected */}
          {isRedirected && (
            <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
              <p className="text-blue-800 text-sm text-center">
                Please log in to access the requested page.
              </p>
            </div>
          )}
          
          {/* Google Login */}
          <div className="flex items-center justify-center w-full mb-4">
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={handleGoogleError}
              width="100%"
              useOneTap
            />
          </div>
          {error && <div className="text-red-500 text-sm text-center mb-2">{error}</div>}
          <div className="flex items-center my-4">
            <div className="flex-grow border-t border-gray-300" />
            <span className="mx-2 text-gray-400 text-xs">OR</span>
            <div className="flex-grow border-t border-gray-300" />
          </div>
          {showForgot ? (
            <form className="space-y-4" onSubmit={handleForgotSubmit} autoComplete="off">
              <div>
                <label className="block text-sm font-semibold mb-1">E-mail</label>
                <input
                  type="email"
                  value={forgotEmail}
                  onChange={e => setForgotEmail(e.target.value)}
                  placeholder="Enter your mail"
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-200"
                  required
                />
              </div>
              <button
                type="submit"
                className="w-full bg-purple-200 text-gray-700 font-semibold py-2 rounded mt-2 hover:bg-purple-300 disabled:opacity-50"
                disabled={loading}
              >
                {loading ? 'Requesting...' : 'Request Password Reset'}
              </button>
              {forgotMsg && <div className="text-green-600 text-sm text-center mt-2">{forgotMsg}</div>}
              <div className="text-center text-xs text-gray-500 mt-2">
                <button type="button" className="underline text-indigo-600" onClick={() => setShowForgot(false)}>
                  Back to Login
                </button>
              </div>
            </form>
          ) : (
            <form className="space-y-4" onSubmit={handleSubmit} autoComplete="off">
              <div>
                <label className="block text-sm font-semibold mb-1">E-mail</label>
                <input
                  type="email"
                  name="email"
                  value={form.email}
                  onChange={handleChange}
                  placeholder="Enter your mail"
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-200"
                  required
                />
              </div>
              <div className="relative">
                <label className="block text-sm font-semibold mb-1">Password</label>
                <input
                  type={showPassword ? "text" : "password"}
                  name="password"
                  value={form.password}
                  onChange={handleChange}
                  placeholder="Enter your password"
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-200"
                  required
                />
                <button
                  type="button"
                  className="absolute right-3 top-8 text-gray-400 hover:text-gray-600"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? "👁️" : "👁️‍🗨️"}
                </button>
              </div>
              <button
                type="submit"
                className="w-full bg-indigo-600 text-white font-semibold py-2 rounded mt-2 hover:bg-indigo-700 disabled:opacity-50"
                disabled={loading}
              >
                {loading ? 'Logging in...' : 'Log In'}
              </button>
              <div className="text-center text-xs text-gray-500 mt-2">
                <button type="button" className="underline text-indigo-600" onClick={() => setShowForgot(true)}>
                  Forgot Password?
                </button>
              </div>
            </form>
          )}
          <div className="text-center text-xs text-gray-500 mt-4">
            Don't have an account?{' '}
            <Link to="/signup" className="underline text-indigo-600">
              Sign up
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage; 