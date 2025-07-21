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
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
      <div className="flex flex-col items-center w-full">
        <div className="mt-12 mb-4">
          <span className="font-bold text-2xl tracking-widest">AWADE</span>
        </div>
        <div className="bg-white rounded-md shadow-md p-8 w-full max-w-md border border-gray-300 relative">
          <h2 className="text-2xl font-semibold text-center mb-2">Reset Password</h2>
          <p className="text-center text-gray-500 text-sm mb-6">
            Enter your new password below.
          </p>
          {error && <div className="text-red-500 text-sm text-center mb-2">{error}</div>}
          {success && <div className="text-green-600 text-sm text-center mb-2">{success}</div>}
          <form className="space-y-4" onSubmit={handleSubmit} autoComplete="off">
            <div>
              <label className="block text-sm font-semibold mb-1">New Password</label>
              <input
                type="password"
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
              <label className="block text-sm font-semibold mb-1">Repeat New Password</label>
              <input
                type="password"
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
              className="w-full bg-purple-200 text-gray-700 font-semibold py-2 rounded mt-2 hover:bg-purple-300 disabled:opacity-50"
              disabled={loading}
            >
              {loading ? 'Resetting...' : 'Reset Password'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ResetPasswordPage; 