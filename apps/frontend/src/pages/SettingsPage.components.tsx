/**
 * SettingsPage.components.tsx
 * Tab components extracted from SettingsPage.tsx (AWD-M-122).
 * Each tab manages its own state; SettingsPage is a thin shell that owns
 * only the active-tab and settings-menu-open state.
 */
import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import apiService from '../services/api';
import {
  FaUser,
  FaShieldAlt,
  FaEdit,
  FaTimes,
  FaCheck,
  FaCog,
} from 'react-icons/fa';

// ── Shared types ────────────────────────────────────────────────────────────

export interface UserProfile {
  user_id: number;
  email: string;
  full_name: string;
  role: string;
  country: string;
  region?: string;
  school_name?: string;
  subjects?: string[];
  grade_levels?: string[];
  languages_spoken?: string;
  phone?: string;
  bio?: string;
  created_at: string;
  last_login?: string;
}

// ── ProfileTab ──────────────────────────────────────────────────────────────

export const ProfileTab: React.FC = () => {
  const { user } = useAuth();
  const [profileData, setProfileData] = useState<UserProfile | null>(null);
  const [editingField, setEditingField] = useState<string | null>(null);
  const [editForm, setEditForm] = useState({
    full_name: '',
    country: '',
    region: '',
    school_name: '',
    phone: '',
    bio: '',
    subjects: [] as string[],
    grade_levels: [] as string[],
    languages_spoken: '',
  });

  useEffect(() => {
    if (user?.user_id) {
      loadUserProfile();
    }
  }, [user?.user_id]);

  const loadUserProfile = async () => {
    try {
      const response = await apiService.getCurrentUser();
      if (response.data) {
        setProfileData(response.data);
        setEditForm({
          full_name: response.data.full_name || '',
          country: response.data.country || '',
          region: response.data.region || '',
          school_name: response.data.school_name || '',
          phone: response.data.phone || '',
          bio: response.data.bio || '',
          subjects: response.data.subjects || [],
          grade_levels: response.data.grade_levels || [],
          languages_spoken: response.data.languages_spoken || '',
        });
      }
    } catch {
      // Profile load failed silently; UI shows empty state
    }
  };

  const handleSaveField = async (field: string) => {
    try {
      if (!profileData?.user_id) return;
      const updateData = { [field]: editForm[field as keyof typeof editForm] };
      const response = await apiService.updateProfile(updateData, profileData.user_id);
      if (response.error) return;
      if (response.data) {
        setProfileData(response.data);
        setEditingField(null);
        setEditForm(prev => ({
          ...prev,
          [field]: response.data[field as keyof typeof response.data] || '',
        }));
      }
    } catch {
      // Silent error handling
    }
  };

  const handleCancelEdit = (field: string) => {
    setEditingField(null);
    if (profileData) {
      setEditForm(prev => ({
        ...prev,
        [field]: profileData[field as keyof UserProfile] || '',
      }));
    }
  };

  const handleInputChange = (field: string, value: string | string[]) => {
    setEditForm(prev => ({ ...prev, [field]: value }));
  };

  const getInitials = (name: string) =>
    name.split(' ').map(n => n[0]).join('').toUpperCase();

  const EditableField: React.FC<{
    field: string;
    label: string;
    value: string;
    inputType?: string;
    multiline?: boolean;
  }> = ({ field, label, value, inputType = 'text', multiline = false }) => (
    <div className={`flex ${multiline ? 'items-start' : 'items-center'} justify-between p-3 bg-gray-50 rounded-lg`}>
      <div className="flex-1">
        <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
        {editingField === field ? (
          multiline ? (
            <textarea
              value={value}
              onChange={e => handleInputChange(field, e.target.value)}
              rows={3}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500"
            />
          ) : (
            <input
              type={inputType}
              value={value}
              onChange={e => handleInputChange(field, e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500"
            />
          )
        ) : (
          <p className="text-gray-900">{profileData?.[field as keyof UserProfile]?.toString() || 'Not set'}</p>
        )}
      </div>
      <div className="flex space-x-2 ml-3">
        {editingField === field ? (
          <>
            <button
              onClick={() => handleSaveField(field)}
              className="p-2 text-green-600 hover:text-green-700 hover:bg-green-50 rounded-lg transition-colors duration-200"
              title="Save changes"
            >
              <FaCheck className="w-4 h-4" />
            </button>
            <button
              onClick={() => handleCancelEdit(field)}
              className="p-2 text-gray-600 hover:text-gray-700 hover:bg-gray-50 rounded-lg transition-colors duration-200"
            >
              <FaTimes className="w-4 h-4" />
            </button>
          </>
        ) : (
          <button
            onClick={() => setEditingField(field)}
            className="p-2 text-accent-600 hover:text-accent-700 hover:bg-accent-50 rounded-lg transition-colors duration-200"
          >
            <FaEdit className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );

  return (
    <div className="bg-white rounded-xl shadow-md border border-gray-100 p-4 md:p-6">
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between mb-4 sm:mb-6 gap-4">
        <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
          <div className="relative">
            <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white text-xl sm:text-2xl font-bold border-4 border-white shadow-md">
              {getInitials(profileData?.full_name || user?.full_name || '')}
            </div>
          </div>
          <div className="text-center sm:text-left">
            <h2 className="text-xl sm:text-2xl font-bold text-gray-900">
              {profileData?.full_name || user?.full_name}
            </h2>
            <p className="text-gray-600 text-sm sm:text-base">{profileData?.role || user?.role}</p>
            <p className="text-gray-600 text-sm sm:text-base">
              {profileData?.region && `${profileData.region}, `}
              {profileData?.country || user?.country}
            </p>
          </div>
        </div>
      </div>

      <div className="mb-6 sm:mb-8">
        <h3 className="text-lg sm:text-xl font-semibold text-gray-900 mb-3 sm:mb-4">Personal Information</h3>
        <div className="space-y-4">
          <EditableField field="full_name" label="Full Name" value={editForm.full_name} />
          <EditableField field="country" label="Country" value={editForm.country} />
          <EditableField field="phone" label="Phone" value={editForm.phone} inputType="tel" />
          <EditableField field="region" label="City/Region" value={editForm.region} />
          <EditableField field="bio" label="Bio" value={editForm.bio} multiline />
        </div>
      </div>
    </div>
  );
};

// ── SecurityTab ─────────────────────────────────────────────────────────────

export const SecurityTab: React.FC = () => {
  const { user } = useAuth();
  const [profileEmail, setProfileEmail] = useState<string | null>(null);
  const [isEditingLogin, setIsEditingLogin] = useState(false);
  const [loginForm, setLoginForm] = useState({
    email: '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });
  const [loginErrors, setLoginErrors] = useState<{ [key: string]: string }>({});

  useEffect(() => {
    if (user?.user_id) {
      apiService.getCurrentUser().then(response => {
        if (response.data?.email) setProfileEmail(response.data.email);
      }).catch(() => {});
    }
  }, [user?.user_id]);

  const handleEditLogin = () => {
    setIsEditingLogin(true);
    setLoginForm({
      email: profileEmail || user?.email || '',
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
    });
    setLoginErrors({});
  };

  const handleCancelLoginEdit = () => {
    setIsEditingLogin(false);
    setLoginForm({ email: '', currentPassword: '', newPassword: '', confirmPassword: '' });
    setLoginErrors({});
  };

  const validateLoginForm = () => {
    const errors: { [key: string]: string } = {};
    if (!loginForm.currentPassword) errors.currentPassword = 'Current password is required';
    if (loginForm.newPassword && loginForm.newPassword.length < 8)
      errors.newPassword = 'New password must be at least 8 characters';
    if (loginForm.newPassword && loginForm.newPassword !== loginForm.confirmPassword)
      errors.confirmPassword = 'Passwords do not match';
    if (loginForm.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(loginForm.email))
      errors.email = 'Please enter a valid email address';
    setLoginErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSaveLogin = async () => {
    if (!validateLoginForm()) return;
    const emailChanged = loginForm.email !== profileEmail;
    const passwordProvided = !!loginForm.newPassword;
    if (emailChanged || passwordProvided) {
      setLoginErrors({
        general: 'Email and password updates are not yet available. Please contact support if you need to change these details.',
      });
      return;
    }
    setIsEditingLogin(false);
    setLoginForm({ email: '', currentPassword: '', newPassword: '', confirmPassword: '' });
    setLoginErrors({});
  };

  const handleLoginFieldChange = (field: string, value: string) => {
    setLoginForm(prev => ({ ...prev, [field]: value }));
    if (loginErrors[field]) {
      setLoginErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const displayEmail = profileEmail || user?.email;

  return (
    <div className="bg-white rounded-xl shadow-md border border-gray-100 p-4 md:p-6">
      <div className="space-y-6 sm:space-y-8">
        <div className="border-2 border-dashed border-blue-300 rounded-lg p-4 md:p-6">
          <h3 className="text-lg sm:text-xl font-semibold text-gray-900 mb-3 sm:mb-4">Login Details</h3>

          {!isEditingLogin ? (
            <div className="space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                <div>
                  <p className="text-sm text-gray-600">Email Address</p>
                  <p className="text-gray-900">{displayEmail}</p>
                </div>
                <button
                  onClick={handleEditLogin}
                  className="bg-accent-600 hover:bg-accent-700 text-white px-4 py-2 rounded-lg font-medium w-full sm:w-auto"
                >
                  Edit Login Details
                </button>
              </div>
              <div>
                <p className="text-sm text-gray-600">Password</p>
                <p className="text-gray-900">••••••••••••</p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
                <input
                  type="email"
                  value={loginForm.email}
                  onChange={e => handleLoginFieldChange('email', e.target.value)}
                  className={`w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-accent-500 ${
                    loginErrors.email ? 'border-red-500' : 'border-gray-300 focus:border-accent-500'
                  }`}
                />
                {loginErrors.email && <p className="text-red-500 text-sm mt-1">{loginErrors.email}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Current Password</label>
                <input
                  type="password"
                  value={loginForm.currentPassword}
                  onChange={e => handleLoginFieldChange('currentPassword', e.target.value)}
                  className={`w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-accent-500 ${
                    loginErrors.currentPassword ? 'border-red-500' : 'border-gray-300 focus:border-accent-500'
                  }`}
                  placeholder="Enter your current password"
                />
                {loginErrors.currentPassword && (
                  <p className="text-red-500 text-sm mt-1">{loginErrors.currentPassword}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">New Password (Optional)</label>
                <input
                  type="password"
                  value={loginForm.newPassword}
                  onChange={e => handleLoginFieldChange('newPassword', e.target.value)}
                  className={`w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-accent-500 ${
                    loginErrors.newPassword ? 'border-red-500' : 'border-gray-300 focus:border-accent-500'
                  }`}
                  placeholder="Leave blank to keep current password"
                />
                {loginErrors.newPassword && (
                  <p className="text-red-500 text-sm mt-1">{loginErrors.newPassword}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Confirm New Password</label>
                <input
                  type="password"
                  value={loginForm.confirmPassword}
                  onChange={e => handleLoginFieldChange('confirmPassword', e.target.value)}
                  className={`w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-accent-500 ${
                    loginErrors.confirmPassword ? 'border-red-500' : 'border-gray-300 focus:border-accent-500'
                  }`}
                  placeholder="Confirm your new password"
                />
                {loginErrors.confirmPassword && (
                  <p className="text-red-500 text-sm mt-1">{loginErrors.confirmPassword}</p>
                )}
              </div>

              {loginErrors.general && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-red-600 text-sm">{loginErrors.general}</p>
                </div>
              )}

              <div className="flex flex-col sm:flex-row gap-3 pt-2">
                <button
                  onClick={handleSaveLogin}
                  className="bg-accent-600 hover:bg-accent-700 text-white px-4 py-2 rounded-lg font-medium w-full sm:w-auto"
                >
                  Save Changes
                </button>
                <button
                  onClick={handleCancelLoginEdit}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800 font-medium border border-gray-300 rounded-lg w-full sm:w-auto"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// ── LanguageTab ─────────────────────────────────────────────────────────────

export const LanguageTab: React.FC = () => (
  <div className="bg-white rounded-xl shadow-md border border-gray-100 p-4 md:p-6">
    <h3 className="text-lg sm:text-xl font-semibold text-gray-900 mb-3 sm:mb-4">Language Settings</h3>
    <p className="text-gray-600">Language settings will be implemented here.</p>
  </div>
);

// ── SettingsMenu ────────────────────────────────────────────────────────────

export interface SettingsMenuProps {
  activeTab: 'profile' | 'security' | 'language';
  onTabChange: (tab: 'profile' | 'security' | 'language') => void;
  onClose: () => void;
}

export const SettingsMenu: React.FC<SettingsMenuProps> = ({ activeTab, onTabChange, onClose }) => (
  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
    <button
      onClick={() => { onTabChange('profile'); onClose(); }}
      className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-50 flex items-center ${
        activeTab === 'profile' ? 'text-accent-600 bg-accent-50' : 'text-gray-700'
      }`}
    >
      <FaUser className="w-4 h-4 mr-2" />
      My Profile
    </button>
    <button
      onClick={() => { onTabChange('security'); onClose(); }}
      className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-50 flex items-center ${
        activeTab === 'security' ? 'text-accent-600 bg-accent-50' : 'text-gray-700'
      }`}
    >
      <FaShieldAlt className="w-4 h-4 mr-2" />
      Security
    </button>
    <button
      onClick={() => { onTabChange('language'); onClose(); }}
      className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-50 flex items-center ${
        activeTab === 'language' ? 'text-accent-600 bg-accent-50' : 'text-gray-700'
      }`}
    >
      <FaCog className="w-4 h-4 mr-2" />
      Language
    </button>
    <div className="border-t border-gray-100 my-1"></div>
    <button
      onClick={onClose}
      className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center"
    >
      <FaTimes className="w-4 h-4 mr-2" />
      Delete Account
    </button>
  </div>
);
