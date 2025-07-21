import React, { useState } from 'react';
import { GoogleLogin } from '@react-oauth/google';

function isAlphanumeric(str: string) {
  return /^[a-zA-Z0-9]+$/.test(str);
}

const SignupPage: React.FC = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [showRepeatPassword, setShowRepeatPassword] = useState(false);
  const [agreed, setAgreed] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    fullName: '',
    email: '',
    password: '',
    repeatPassword: '',
  });
  const [loading, setLoading] = useState(false);

  // Google OAuth handler (unchanged)
  const handleGoogleSuccess = async (credentialResponse: any) => {
    setError(null);
    try {
      const res = await fetch('/api/auth/google', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ credential: credentialResponse.credential }),
      });
      if (!res.ok) {
        throw new Error('Google authentication failed');
      }
      const data = await res.json();
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      // TODO: Redirect or update UI as needed
      console.log('Authenticated user:', data.user);
    } catch (err: any) {
      setError(err.message || 'Google login failed');
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
    if (!isAlphanumeric(form.password)) {
      setError('Password must be alphanumeric.');
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
      // Always use HTTPS in production
      const url = (import.meta as any).env.MODE === 'production'
        ? 'https://your-production-domain.com/api/auth/signup'
        : '/api/auth/signup';
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: form.email,
          password: form.password,
          full_name: form.fullName,
          role: 'educator',
          country: '',
          region: null,
          school_name: null,
          subjects: null,
          grade_levels: null,
          languages_spoken: null,
        }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Signup failed');
      }
      const data = await res.json();
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      // TODO: Redirect or update UI as needed
      console.log('Signed up user:', data.user);
    } catch (err: any) {
      setError(err.message || 'Signup failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
      <div className="absolute left-12 top-8 text-gray-400 text-lg">Sign Up</div>
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
          <h2 className="text-2xl font-semibold text-center mb-2">SIGN UP</h2>
          <p className="text-center text-gray-500 text-sm mb-6">
            Sign up to start your learning journey. Acquire precise knowledge tailored specifically to your development
          </p>
          {/* Google Sign Up */}
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
          <form className="space-y-4" onSubmit={handleSubmit} autoComplete="off">
            <div>
              <label className="block text-sm font-semibold mb-1">Full Name</label>
              <input
                type="text"
                name="fullName"
                value={form.fullName}
                onChange={handleChange}
                placeholder="Enter your Name"
                className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-200"
                required
              />
            </div>
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
                type={showPassword ? 'text' : 'password'}
                name="password"
                value={form.password}
                onChange={handleChange}
                placeholder="Enter your Password"
                className="w-full border border-gray-300 rounded px-3 py-2 pr-10 focus:outline-none focus:ring-2 focus:ring-indigo-200"
                required
                minLength={8}
                pattern="[a-zA-Z0-9]+"
              />
              <button
                type="button"
                className="absolute right-2 top-8 text-gray-400 hover:text-gray-600"
                tabIndex={-1}
                onClick={() => setShowPassword((v) => !v)}
                aria-label="Toggle password visibility"
              >
                {showPassword ? '🙈' : '👁️'}
              </button>
            </div>
            <div className="relative">
              <label className="block text-sm font-semibold mb-1">Repeat Password</label>
              <input
                type={showRepeatPassword ? 'text' : 'password'}
                name="repeatPassword"
                value={form.repeatPassword}
                onChange={handleChange}
                placeholder="Enter your Password"
                className="w-full border border-gray-300 rounded px-3 py-2 pr-10 focus:outline-none focus:ring-2 focus:ring-indigo-200"
                required
                minLength={8}
                pattern="[a-zA-Z0-9]+"
              />
              <button
                type="button"
                className="absolute right-2 top-8 text-gray-400 hover:text-gray-600"
                tabIndex={-1}
                onClick={() => setShowRepeatPassword((v) => !v)}
                aria-label="Toggle repeat password visibility"
              >
                {showRepeatPassword ? '🙈' : '👁️'}
              </button>
            </div>
            <div className="flex items-center">
              <input
                id="terms"
                type="checkbox"
                checked={agreed}
                onChange={() => setAgreed((v) => !v)}
                className="mr-2"
              />
              <label htmlFor="terms" className="text-xs text-gray-600">
                By signing up, you agree to our{' '}
                <a href="#" className="underline text-indigo-600">Terms & Conditions</a>
              </label>
            </div>
            <button
              type="submit"
              className="w-full bg-purple-200 text-gray-700 font-semibold py-2 rounded mt-2 hover:bg-purple-300 disabled:opacity-50"
              disabled={loading}
            >
              {loading ? 'Signing Up...' : 'Sign Up'}
            </button>
          </form>
          <div className="text-center text-xs text-gray-500 mt-4">
            Have an Account?{' '}
            <a href="#" className="underline text-indigo-600">Log In</a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignupPage; 