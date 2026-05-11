import React, { useState, useEffect } from 'react';
import { GoogleLogin } from '@react-oauth/google';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { FaEye, FaEyeSlash, FaArrowLeft, FaUser, FaEnvelope, FaLock, FaCheckCircle, FaGraduationCap, FaChild } from 'react-icons/fa';
import { getErrorMessage } from '../utils/errors';

type AccountRole = 'PARENT' | 'EDUCATOR';

const SignupPage: React.FC = () => {
  const navigate = useNavigate();
  const { signup, googleAuth } = useAuth();
  const [selectedRole, setSelectedRole] = useState<AccountRole | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [showRepeatPassword, setShowRepeatPassword] = useState(false);
  const [agreed, setAgreed] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [form, setForm] = useState({
    fullName: '',
    email: '',
    password: '',
    repeatPassword: ''
  });
  const [loading, setLoading] = useState(false);

  // Handle redirect after successful signup
  useEffect(() => {
    if (showSuccessModal) {
      const timer = setTimeout(() => {
        setShowSuccessModal(false);
        // PARENT users go through onboarding to add their first child
        navigate(selectedRole === 'PARENT' ? '/onboarding' : '/dashboard');
      }, 2000);

      return () => clearTimeout(timer);
    }
  }, [showSuccessModal, navigate, selectedRole]);

  // Google OAuth handler
  const handleGoogleSuccess = async (credentialResponse: any) => {
    if (!selectedRole) {
      setError('Please select whether you are a parent or educator first.');
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const success = await googleAuth(credentialResponse.credential, selectedRole);
      if (success) {
        // PARENT users go through onboarding to add their first child
        navigate(selectedRole === 'PARENT' ? '/onboarding' : '/dashboard');
      } else {
        setError('Google signup failed. Please try email/password signup instead.');
      }
    } catch (err: unknown) {
      setError(getErrorMessage(err, 'Google signup failed'));
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleError = () => {
    setError('Google Sign In was unsuccessful');
  };

  // Input change handler
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  // Form validation
  const validate = () => {
    if (!form.fullName.trim() || !form.email.trim() || !form.password || !form.repeatPassword) {
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
    if (form.password.length > 128) {
      setError('Password must be no more than 128 characters.');
      return false;
    }
    if (form.password !== form.repeatPassword) {
      setError('Passwords do not match.');
      return false;
    }
    if (!agreed) {
      setError('You must agree to the Terms & Conditions.');
      return false;
    }
    if (!selectedRole) {
      setError('Please select whether you are a parent or educator.');
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
      const success = await signup({
        email: form.email,
        password: form.password,
        full_name: form.fullName,
        role: selectedRole,
        country: 'Nigeria',
        region: null,
        school_name: null,
        subjects: null,
        grade_levels: null,
        languages_spoken: null,
      });
      
      if (success) {
        setShowSuccessModal(true);
      } else {
        setError('Signup failed. Please try again.');
      }
    } catch (err: unknown) {
      setError(getErrorMessage(err, 'Signup failed'));
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
          className="flex items-center space-x-2 text-primary-600 hover:text-primary-700 transition-colors duration-200 p-2 rounded-lg hover:bg-primary-50"
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
            Support your child's learning
          </p>
        </div>

        {/* Signup Form Card */}
        <div className="bg-white rounded-xl shadow-lg p-6 sm:p-8 w-full border border-gray-100">
          <div className="text-center mb-6">
            <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">Create Account</h2>
            <p className="text-gray-600 text-sm sm:text-base">
              Join thousands of families and educators across Africa
            </p>
          </div>

          {/* Role Selector */}
          <div className="mb-6">
            <p className="text-sm font-semibold text-gray-700 mb-3 text-center">I am a...</p>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setSelectedRole('PARENT')}
                className={`flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all duration-200 ${
                  selectedRole === 'PARENT'
                    ? 'border-accent-600 bg-accent-50 shadow-sm'
                    : 'border-gray-200 bg-white hover:border-accent-300'
                }`}
              >
                <FaChild className={`w-6 h-6 ${selectedRole === 'PARENT' ? 'text-accent-600' : 'text-gray-400'}`} />
                <span className={`text-sm font-semibold ${selectedRole === 'PARENT' ? 'text-accent-700' : 'text-gray-600'}`}>
                  Parent
                </span>
                <span className="text-xs text-gray-400 text-center leading-tight">
                  Help my child at home
                </span>
              </button>
              <button
                type="button"
                onClick={() => setSelectedRole('EDUCATOR')}
                className={`flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all duration-200 ${
                  selectedRole === 'EDUCATOR'
                    ? 'border-primary-600 bg-primary-50 shadow-sm'
                    : 'border-gray-200 bg-white hover:border-primary-300'
                }`}
              >
                <FaGraduationCap className={`w-6 h-6 ${selectedRole === 'EDUCATOR' ? 'text-primary-600' : 'text-gray-400'}`} />
                <span className={`text-sm font-semibold ${selectedRole === 'EDUCATOR' ? 'text-primary-700' : 'text-gray-600'}`}>
                  Educator
                </span>
                <span className="text-xs text-gray-400 text-center leading-tight">
                  Create lesson plans
                </span>
              </button>
            </div>
          </div>

          {/* Google Sign Up */}
          <div className="mb-6">
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={handleGoogleError}
              width="100%"
              useOneTap
            />
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-600 text-sm text-center">{error}</p>
            </div>
          )}

          <div className="flex items-center my-6">
            <div className="flex-grow border-t border-gray-200" />
            <span className="mx-4 text-gray-400 text-sm font-medium">or continue with email</span>
            <div className="flex-grow border-t border-gray-200" />
          </div>

          <form className="space-y-4 sm:space-y-5" onSubmit={handleSubmit} autoComplete="off">
            {/* Full Name */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2 flex items-center">
                <FaUser className="w-4 h-4 mr-2 text-primary-600" />
                Full Name
              </label>
              <input
                type="text"
                name="fullName"
                value={form.fullName}
                onChange={handleChange}
                placeholder="Enter your full name"
                className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 text-sm sm:text-base"
                required
              />
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2 flex items-center">
                <FaEnvelope className="w-4 h-4 mr-2 text-primary-600" />
                Email Address
              </label>
              <input
                type="email"
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
              <label className="block text-sm font-semibold text-gray-700 mb-2 flex items-center">
                <FaLock className="w-4 h-4 mr-2 text-primary-600" />
                Password
              </label>
              <input
                type={showPassword ? 'text' : 'password'}
                name="password"
                value={form.password}
                onChange={handleChange}
                placeholder="Create a password"
                className="w-full border border-gray-300 rounded-lg px-4 py-3 pr-12 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 text-sm sm:text-base"
                required
                minLength={8}
                maxLength={128}
              />
              <button
                type="button"
                className="absolute right-3 top-10 text-gray-400 hover:text-gray-600 transition-colors duration-200"
                onClick={() => setShowPassword((v) => !v)}
                aria-label="Toggle password visibility"
              >
                {showPassword ? <FaEyeSlash className="w-5 h-5" /> : <FaEye className="w-5 h-5" />}
              </button>
            </div>

            {/* Repeat Password */}
            <div className="relative">
              <label className="block text-sm font-semibold text-gray-700 mb-2 flex items-center">
                <FaLock className="w-4 h-4 mr-2 text-primary-600" />
                Confirm Password
              </label>
              <input
                type={showRepeatPassword ? 'text' : 'password'}
                name="repeatPassword"
                value={form.repeatPassword}
                onChange={handleChange}
                placeholder="Confirm your password"
                className="w-full border border-gray-300 rounded-lg px-4 py-3 pr-12 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 text-sm sm:text-base"
                required
                minLength={8}
                maxLength={128}
              />
              <button
                type="button"
                className="absolute right-3 top-10 text-gray-400 hover:text-gray-600 transition-colors duration-200"
                onClick={() => setShowRepeatPassword((v) => !v)}
                aria-label="Toggle repeat password visibility"
              >
                {showRepeatPassword ? <FaEyeSlash className="w-5 h-5" /> : <FaEye className="w-5 h-5" />}
              </button>
            </div>

            {/* Terms Checkbox */}
            <div className="flex items-start space-x-3">
              <input
                id="terms"
                type="checkbox"
                checked={agreed}
                onChange={() => setAgreed((v) => !v)}
                className="mt-1 w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
              <label htmlFor="terms" className="text-sm text-gray-600 leading-relaxed">
                I agree to the{' '}
                <a href="#" className="text-primary-600 hover:text-primary-700 underline font-medium">
                  Terms & Conditions
                </a>{' '}
                and{' '}
                <a href="#" className="text-primary-600 hover:text-primary-700 underline font-medium">
                  Privacy Policy
                </a>
              </label>
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
                  <span>Creating Account...</span>
                </div>
              ) : (
                'Create Account'
              )}
            </button>
          </form>

          {/* Login Link */}
          <div className="text-center mt-6 pt-6 border-t border-gray-100">
            <p className="text-gray-600 text-sm">
              Already have an account?{' '}
              <Link to="/login" className="text-primary-600 hover:text-primary-700 font-semibold underline">
                Sign in here
              </Link>
            </p>
          </div>
        </div>
      </div>

      {/* Success Modal */}
      {showSuccessModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 sm:p-8 max-w-md w-full mx-4 text-center">
            <div className="mb-6">
              <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100">
                <FaCheckCircle className="h-8 w-8 text-green-600" />
              </div>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-3">Welcome to Awade!</h3>
            <p className="text-gray-600 text-sm sm:text-base mb-6">
              {selectedRole === 'PARENT'
                ? "Your account is ready. Let's add your first child!"
                : "Your account is ready. Let's get started!"}
            </p>
            <div className="flex justify-center">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SignupPage; 