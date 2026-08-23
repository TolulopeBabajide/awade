import React, { useState } from 'react';
import type { CredentialResponse } from '@react-oauth/google';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import apiService from '../services/api';
import { sanitizeRedirectPath } from '../utils/sanitizer';
import { FaEye, FaEyeSlash, FaArrowLeft, FaEnvelope, FaLock } from 'react-icons/fa';
import ResponsiveGoogleLogin, { isGoogleAuthConfigured } from '../components/ResponsiveGoogleLogin';



const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, googleAuth } = useAuth();
  
  // Sanitize the redirect path from route state to prevent open-redirect (GHSA-wrjc-x8rr-h8h6)
  const from = sanitizeRedirectPath((location.state as any)?.from?.pathname);
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
  const handleGoogleSuccess = async (credentialResponse: CredentialResponse) => {
    setError(null);
    setLoading(true);
    try {
      if (!credentialResponse.credential) {
        setError('Google login failed. Please try email and password instead.');
        return;
      }
      const success = await googleAuth(credentialResponse.credential);
      if (success) {
        // Navigate to the originally requested page or dashboard
        navigate(from, { replace: true });
      } else {
        setError('Google login failed. Please try email/password login instead.');
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Google login failed. Please try email and password instead.');
    } finally {
      setLoading(false);
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
    } catch (_err: unknown) {
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
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 px-4 sm:px-6 lg:px-8">
      {/* Back Button */}
      <div className="absolute left-4 sm:left-8 top-6 sm:top-8">
        <button 
          onClick={() => navigate(-1)}
          className="flex min-h-11 min-w-11 items-center justify-center space-x-2 rounded-lg p-2 text-primary-600 transition-colors duration-200 hover:bg-primary-50 hover:text-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
          aria-label="Go back"
        >
          <FaArrowLeft className="w-4 h-4" />
          <span className="hidden sm:inline text-sm font-medium">Back</span>
        </button>
      </div>

      <div className="flex flex-col items-center w-full max-w-md">
        {/* Logo */}
        <div className="mt-8 sm:mt-12 mb-6 text-center">
          <h1 className="font-bold text-3xl sm:text-4xl text-primary-800 tracking-wide">
            <Link to="/" aria-label="Awade - Go to homepage">
              AWADE
            </Link>
          </h1>
          <p className="text-primary-600 text-sm sm:text-base mt-2">
            Learning support for home and school
          </p>
        </div>

        {/* Login Form Card */}
        <div className="bg-white rounded-xl shadow-lg p-6 sm:p-8 w-full border border-gray-100">
          <div className="text-center mb-6">
            <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">Welcome Back</h2>
            <p className="text-gray-600 text-sm sm:text-base">
              Continue helping learners at home or in the classroom
            </p>
          </div>

          {/* Show redirect message if user was redirected */}
          {isRedirected && (
            <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-blue-800 text-sm text-center">
                Please log in to access the requested page.
              </p>
            </div>
          )}

          {/* Google Login */}
          {isGoogleAuthConfigured && (
            <div className="mb-6">
              <ResponsiveGoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={handleGoogleError}
              />
            </div>
          )}

          {error && (
            <div role="alert" aria-live="polite" className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-600 text-sm text-center">{error}</p>
            </div>
          )}

          {isGoogleAuthConfigured && (
            <div className="flex items-center my-6">
              <div className="flex-grow border-t border-gray-200" />
              <span className="mx-4 text-gray-500 text-sm font-medium">or continue with email</span>
              <div className="flex-grow border-t border-gray-200" />
            </div>
          )}

          {showForgot ? (
            <form className="space-y-4 sm:space-y-5" onSubmit={handleForgotSubmit} autoComplete="off" noValidate>
              <div>
                <label htmlFor="forgot-email" className="block text-sm font-semibold text-gray-700 mb-2 flex items-center">
                  <FaEnvelope className="w-4 h-4 mr-2 text-primary-600" />
                  Email Address
                </label>
                <input
                  type="email"
                  id="forgot-email"
                  value={forgotEmail}
                  onChange={e => setForgotEmail(e.target.value)}
                  placeholder="Enter your email"
                  className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 text-sm sm:text-base"
                  required
                />
              </div>
              <button
                type="submit"
                className="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed text-sm sm:text-base"
                disabled={loading}
              >
                {loading ? (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Requesting...</span>
                  </div>
                ) : (
                  'Request Password Reset'
                )}
              </button>
              {forgotMsg && (
                <div role="status" className="p-3 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-green-600 text-sm text-center">{forgotMsg}</p>
                </div>
              )}
              <div className="text-center">
                <button 
                  type="button" 
                  className="inline-flex min-h-11 items-center rounded-md px-2 text-sm font-medium text-primary-700 underline hover:text-primary-800 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  onClick={() => setShowForgot(false)}
                >
                  ← Back to Login
                </button>
              </div>
            </form>
          ) : (
            <form className="space-y-4 sm:space-y-5" onSubmit={handleSubmit} autoComplete="off" noValidate>
              {/* Email */}
              <div>
                <label htmlFor="login-email" className="block text-sm font-semibold text-gray-700 mb-2 flex items-center">
                  <FaEnvelope className="w-4 h-4 mr-2 text-primary-600" />
                  Email Address
                </label>
                <input
                  type="email"
                  id="login-email"
                  name="email"
                  value={form.email}
                  onChange={handleChange}
                  placeholder="Enter your email"
                  className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 text-sm sm:text-base"
                  required
                />
              </div>

              {/* Password */}
              <div className="relative">
                <label htmlFor="login-password" className="block text-sm font-semibold text-gray-700 mb-2 flex items-center">
                  <FaLock className="w-4 h-4 mr-2 text-primary-600" />
                  Password
                </label>
                <input
                  type={showPassword ? "text" : "password"}
                  id="login-password"
                  name="password"
                  value={form.password}
                  onChange={handleChange}
                  placeholder="Enter your password"
                  className="w-full border border-gray-300 rounded-lg px-4 py-3 pr-12 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 text-sm sm:text-base"
                  required
                />
                <button
                  type="button"
                  className="absolute right-1 top-8 flex min-h-11 min-w-11 items-center justify-center rounded-md text-gray-400 transition-colors duration-200 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label="Toggle password visibility"
                >
                  {showPassword ? <FaEyeSlash className="w-5 h-5" /> : <FaEye className="w-5 h-5" />}
                </button>
              </div>

              {/* Forgot Password Link */}
              <div className="text-right">
                <button 
                  type="button" 
                  className="inline-flex min-h-11 items-center rounded-md px-2 text-sm font-medium text-primary-700 underline hover:text-primary-800 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  onClick={() => setShowForgot(true)}
                >
                  Forgot Password?
                </button>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                className="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed text-sm sm:text-base"
                disabled={loading}
              >
                {loading ? (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Signing In...</span>
                  </div>
                ) : (
                  'Sign In'
                )}
              </button>
            </form>
          )}

          {/* Signup Link */}
          <div className="text-center mt-6 pt-6 border-t border-gray-100">
            <p className="text-gray-600 text-sm">
              Don't have an account?{' '}
              <Link to="/signup" className="inline-flex min-h-11 items-center rounded-md px-1 font-semibold text-primary-700 underline hover:text-primary-800 focus:outline-none focus:ring-2 focus:ring-primary-500">
                Create one here
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage; 
