import AuthLayout from '../components/design/AuthLayout'
import { Link } from 'react-router-dom'
import React, { useState } from 'react';

function isAlphanumeric(str: string) {
  return /^[a-zA-Z0-9]+$/.test(str);
}

function getTokenFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return params.get('token') || '';
}

const ResetPasswordPage: React.FC = () => {
  const [form, setForm] = useState({
    password: '',
    repeatPassword: '',
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const token = getTokenFromUrl();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const validate = () => {
    if (!form.password || !form.repeatPassword) {
      setError('All fields are required.');
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
    setError(null);
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const res = await fetch('/api/auth/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, new_password: form.password }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to reset password');
      }
      setSuccess(data.message || 'Password has been reset successfully.');
    } catch (err: any) {
      setError(err.message || 'Failed to reset password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout mode="reset">
      <div className="account-form">
          <h2 className="text-2xl font-semibold text-center mb-2">Reset Password</h2>
          <p className="text-center text-gray-500 text-sm mb-6">
            Enter your new password below.
          </p>
          {error && <div role="alert" className="text-red-500 text-sm text-center mb-2">{error}</div>}
          {success && <div role="status" className="text-green-600 text-sm text-center mb-2">{success}</div>}
          <form className="space-y-4" onSubmit={handleSubmit} autoComplete="off">
            <div>
              <label htmlFor="reset-password" className="block text-sm font-semibold mb-1">New Password</label>
              <input
                type="password"
                id="reset-password"
                name="password"
                value={form.password}
                onChange={handleChange}
                placeholder="Enter new password"
                className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-200"
                required
                minLength={8}
                pattern="[a-zA-Z0-9]+"
              />
            </div>
            <div>
              <label htmlFor="reset-confirm" className="block text-sm font-semibold mb-1">Repeat New Password</label>
              <input
                type="password"
                id="reset-confirm"
                name="repeatPassword"
                value={form.repeatPassword}
                onChange={handleChange}
                placeholder="Repeat new password"
                className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-200"
                required
                minLength={8}
                pattern="[a-zA-Z0-9]+"
              />
            </div>
            <button
              type="submit"
              className="learning-button w-full mt-2 disabled:opacity-50"
              disabled={loading}
            >
              {loading ? 'Resetting...' : 'Reset Password'}
            </button>
          </form>
        <Link to="/login" className="account-return">Back to sign in</Link>
      </div>
    </AuthLayout>
  );
};

export default ResetPasswordPage; 