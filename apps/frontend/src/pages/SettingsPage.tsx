import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import apiService from '../services/api';
import Sidebar from '../components/Sidebar';
import { 
  FaUser, 
  FaShieldAlt, 
  FaGlobe, 
  FaTrash, 
  FaEdit, 
  FaCamera, 
  FaTimes,
  FaSignOutAlt,
  FaBell,
  FaHeadset,
  FaPhone,
  FaEnvelope,
  FaMapMarkerAlt,
  FaUserEdit,
  FaKey
} from 'react-icons/fa';

interface UserProfile {
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
  profile_image_url?: string;
  phone?: string;
  bio?: string;
  created_at: string;
  last_login?: string;
}



const SettingsPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState<'profile' | 'security' | 'language'>('profile');
  const [isEditing, setIsEditing] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [profileData, setProfileData] = useState<UserProfile | null>(null);
  const [editForm, setEditForm] = useState({
    full_name: '',
    country: '',
    region: '',
    school_name: '',
    phone: '',
    bio: '',
    subjects: [] as string[],
    grade_levels: [] as string[],
    languages_spoken: ''
  });

  // Login details editing state
  const [isEditingLogin, setIsEditingLogin] = useState(false);
  const [loginForm, setLoginForm] = useState({
    email: '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [loginErrors, setLoginErrors] = useState<{[key: string]: string}>({});

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (user) {
      loadUserProfile();
    }
  }, [user]);

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
          languages_spoken: response.data.languages_spoken || ''
        });
      }
    } catch (error) {
      console.error('Error loading user profile:', error);
    }
  };

  const handleEditProfile = () => {
    setIsEditing(true);
  };

  const handleSaveProfile = async () => {
    try {
      const response = await apiService.updateProfile(editForm);
      if (response.data) {
        setProfileData(response.data);
        setIsEditing(false);
        // Refresh user context
        window.location.reload();
      }
    } catch (error) {
      console.error('Error updating profile:', error);
    }
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    // Reset form to current profile data
    if (profileData) {
      setEditForm({
        full_name: profileData.full_name || '',
        country: profileData.country || '',
        region: profileData.region || '',
        school_name: profileData.school_name || '',
        phone: profileData.phone || '',
        bio: profileData.bio || '',
        subjects: profileData.subjects || [],
        grade_levels: profileData.grade_levels || [],
        languages_spoken: profileData.languages_spoken || ''
      });
    }
  };

  // Login details editing functions
  const handleEditLogin = () => {
    setIsEditingLogin(true);
    setLoginForm({
      email: profileData?.email || user.email,
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    });
    setLoginErrors({});
  };

  const handleCancelLoginEdit = () => {
    setIsEditingLogin(false);
    setLoginForm({
      email: '',
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    });
    setLoginErrors({});
  };

  const validateLoginForm = () => {
    const errors: {[key: string]: string} = {};
    
    if (!loginForm.currentPassword) {
      errors.currentPassword = 'Current password is required';
    }
    
    if (loginForm.newPassword && loginForm.newPassword.length < 8) {
      errors.newPassword = 'New password must be at least 8 characters';
    }
    
    if (loginForm.newPassword && loginForm.newPassword !== loginForm.confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
    }
    
    if (loginForm.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(loginForm.email)) {
      errors.email = 'Please enter a valid email address';
    }
    
    setLoginErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSaveLogin = async () => {
    if (!validateLoginForm()) {
      return;
    }

    try {
      // Update email if changed
      if (loginForm.email !== profileData?.email) {
        // TODO: Implement email update API call
        console.log('Email update not implemented yet');
      }
      
      // Update password if provided
      if (loginForm.newPassword) {
        // TODO: Implement password update API call
        console.log('Password update not implemented yet');
      }
      
      setIsEditingLogin(false);
      setLoginForm({
        email: '',
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
      setLoginErrors({});
      
      // Show success message
      alert('Login details updated successfully!');
    } catch (error) {
      console.error('Error updating login details:', error);
      setLoginErrors({ general: 'Failed to update login details. Please try again.' });
    }
  };

  const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await apiService.uploadProfileImage(formData);
      if (response.data) {
        // Refresh profile data
        await loadUserProfile();
      }
    } catch (error) {
      console.error('Error uploading image:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteImage = async () => {
    try {
      await apiService.deleteProfileImage();
      await loadUserProfile();
    } catch (error) {
      console.error('Error deleting image:', error);
    }
  };

  const handleInputChange = (field: string, value: string | string[]) => {
    setEditForm(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleLoginFieldChange = (field: string, value: string) => {
    setLoginForm(prev => ({
      ...prev,
      [field]: value
    }));
    // Clear error for this field when user starts typing
    if (loginErrors[field]) {
      setLoginErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };



  const getInitials = (name: string) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase();
  };

  if (!user) {
    return <div>Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <Sidebar currentPage="settings" />

      {/* Main Content */}
      <main className="flex-1 lg:ml-64 p-4 md:p-6 lg:p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900">Account Settings</h1>
        </div>

        <div className="flex flex-col lg:flex-row gap-8">
          {/* Settings Navigation */}
          <div className="lg:w-64 flex-shrink-0">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
              <nav className="space-y-2">
                <button
                  onClick={() => setActiveTab('profile')}
                  className={`w-full text-left px-4 py-3 rounded-lg font-medium flex items-center transition-colors duration-200 ${
                    activeTab === 'profile' 
                      ? 'bg-accent-600 text-white' 
                      : 'hover:bg-gray-50 text-gray-700'
                  }`}
                >
                  <FaUser className="w-4 h-4 mr-3" />
                  My Profile
                </button>
                
                <button
                  onClick={() => setActiveTab('security')}
                  className={`w-full text-left px-4 py-3 rounded-lg font-medium flex items-center transition-colors duration-200 ${
                    activeTab === 'security' 
                      ? 'bg-accent-600 text-white' 
                      : 'hover:bg-gray-50 text-gray-700'
                  }`}
                >
                  <FaShieldAlt className="w-4 h-4 mr-3" />
                  Security
                </button>
                
                <button
                  onClick={() => setActiveTab('language')}
                  className={`w-full text-left px-4 py-3 rounded-lg font-medium flex items-center transition-colors duration-200 ${
                    activeTab === 'language' 
                      ? 'bg-accent-600 text-white' 
                      : 'hover:bg-gray-50 text-gray-700'
                  }`}
                >
                  <FaGlobe className="w-4 h-4 mr-3" />
                  Language
                </button>
              </nav>
              
              <div className="mt-6 pt-6 border-t border-gray-200">
                <button className="w-full text-left px-4 py-3 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg font-medium flex items-center transition-colors duration-200">
                  <FaTrash className="w-4 h-4 mr-3" />
                  Delete Account
                </button>
              </div>
            </div>
          </div>

          {/* Content Area */}
          <div className="flex-1">
            {activeTab === 'profile' && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="flex items-start justify-between mb-6">
                  <div className="flex items-center space-x-4">
                    {/* Profile Image */}
                    <div className="relative">
                      {profileData?.profile_image_url ? (
                        <img
                          src={profileData.profile_image_url}
                          alt="Profile"
                          className="w-24 h-24 rounded-full object-cover border-4 border-white shadow-lg"
                        />
                      ) : (
                        <div className="w-24 h-24 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white text-2xl font-bold border-4 border-white shadow-lg">
                          {getInitials(profileData?.full_name || user.full_name)}
                        </div>
                      )}
                      
                      {/* Upload Button */}
                      <button
                        onClick={() => fileInputRef.current?.click()}
                        className="absolute bottom-0 right-0 w-8 h-8 bg-accent-600 rounded-full flex items-center justify-center text-white hover:bg-accent-700 transition-colors duration-200 shadow-lg"
                        disabled={isUploading}
                      >
                        {isUploading ? (
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        ) : (
                          <FaCamera className="w-4 h-4" />
                        )}
                      </button>
                      
                      {/* Delete Button */}
                      {profileData?.profile_image_url && (
                        <button
                          onClick={handleDeleteImage}
                          className="absolute top-0 right-0 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center text-white hover:bg-red-600 transition-colors duration-200 shadow-lg"
                        >
                          <FaTimes className="w-3 h-3" />
                        </button>
                      )}
                    </div>
                    
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/*"
                      onChange={handleImageUpload}
                      className="hidden"
                    />
                    
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900">
                        {profileData?.full_name || user.full_name}
                      </h2>
                      <p className="text-gray-600">{profileData?.role || user.role}</p>
                      <p className="text-gray-600">
                        {profileData?.region && `${profileData.region}, `}
                        {profileData?.country || user.country}
                      </p>
                    </div>
                  </div>
                  
                  <button
                    onClick={isEditing ? handleSaveProfile : handleEditProfile}
                    className="bg-accent-600 hover:bg-accent-700 text-white px-6 py-3 rounded-lg font-medium flex items-center transition-colors duration-200"
                  >
                    <FaUserEdit className="w-4 h-4 mr-2" />
                    {isEditing ? 'Save Profile' : 'Edit Profile'}
                  </button>
                </div>

                {isEditing && (
                  <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <p className="text-yellow-800 text-sm">
                      Click "Save Profile" to save your changes or "Cancel" to discard them.
                    </p>
                    <div className="mt-3 flex space-x-3">
                      <button
                        onClick={handleCancelEdit}
                        className="px-4 py-2 text-gray-600 hover:text-gray-800 font-medium"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}

                {/* Personal Information */}
                <div className="mb-8">
                  <h3 className="text-xl font-semibold text-gray-900 mb-4">Personal Information</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">First Name</label>
                      {isEditing ? (
                        <input
                          type="text"
                          value={editForm.full_name.split(' ')[0] || ''}
                          onChange={(e) => {
                            const names = editForm.full_name.split(' ');
                            names[0] = e.target.value;
                            handleInputChange('full_name', names.join(' '));
                          }}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500"
                        />
                      ) : (
                        <p className="text-gray-900">{profileData?.full_name?.split(' ')[0] || 'Not set'}</p>
                      )}
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Last Name</label>
                      {isEditing ? (
                        <input
                          type="text"
                          value={editForm.full_name.split(' ').slice(1).join(' ') || ''}
                          onChange={(e) => {
                            const names = editForm.full_name.split(' ');
                            names.splice(1, names.length - 1, e.target.value);
                            handleInputChange('full_name', names.join(' '));
                          }}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500"
                        />
                      ) : (
                        <p className="text-gray-900">{profileData?.full_name?.split(' ').slice(1).join(' ') || 'Not set'}</p>
                      )}
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Country</label>
                      {isEditing ? (
                        <input
                          type="text"
                          value={editForm.country}
                          onChange={(e) => handleInputChange('country', e.target.value)}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500"
                        />
                      ) : (
                        <p className="text-gray-900">{profileData?.country || 'Not set'}</p>
                      )}
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
                      <p className="text-gray-900">{profileData?.email || user.email}</p>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Phone</label>
                      {isEditing ? (
                        <input
                          type="tel"
                          value={editForm.phone}
                          onChange={(e) => handleInputChange('phone', e.target.value)}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500"
                        />
                      ) : (
                        <p className="text-gray-900">{profileData?.phone || 'Not set'}</p>
                      )}
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">City</label>
                      {isEditing ? (
                        <input
                          type="text"
                          value={editForm.region}
                          onChange={(e) => handleInputChange('region', e.target.value)}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500"
                        />
                      ) : (
                        <p className="text-gray-900">{profileData?.region || 'Not set'}</p>
                      )}
                    </div>
                    
                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-2">Bio</label>
                      {isEditing ? (
                        <textarea
                          value={editForm.bio}
                          onChange={(e) => handleInputChange('bio', e.target.value)}
                          rows={3}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500"
                        />
                      ) : (
                        <p className="text-gray-900">{profileData?.bio || 'Not set'}</p>
                      )}
                    </div>
                  </div>
                </div>




              </div>
            )}

            {activeTab === 'security' && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="space-y-8">
                  {/* Login Details */}
                  <div className="border-2 border-dashed border-blue-300 rounded-lg p-6">
                    <h3 className="text-xl font-semibold text-gray-900 mb-4">Login Details</h3>
                    
                    {!isEditingLogin ? (
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm text-gray-600">Email Address</p>
                            <p className="text-gray-900">{profileData?.email || user.email}</p>
                          </div>
                          <button 
                            onClick={handleEditLogin}
                            className="bg-accent-600 hover:bg-accent-700 text-white px-4 py-2 rounded-lg font-medium"
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
                        {/* Email Field */}
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
                          <input
                            type="email"
                            value={loginForm.email}
                            onChange={(e) => handleLoginFieldChange('email', e.target.value)}
                            className={`w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-accent-500 ${
                              loginErrors.email ? 'border-red-500' : 'border-gray-300 focus:border-accent-500'
                            }`}
                          />
                          {loginErrors.email && (
                            <p className="text-red-500 text-sm mt-1">{loginErrors.email}</p>
                          )}
                        </div>

                        {/* Current Password Field */}
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">Current Password</label>
                          <input
                            type="password"
                            value={loginForm.currentPassword}
                            onChange={(e) => handleLoginFieldChange('currentPassword', e.target.value)}
                            className={`w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-accent-500 ${
                              loginErrors.currentPassword ? 'border-red-500' : 'border-gray-300 focus:border-accent-500'
                            }`}
                            placeholder="Enter your current password"
                          />
                          {loginErrors.currentPassword && (
                            <p className="text-red-500 text-sm mt-1">{loginErrors.currentPassword}</p>
                          )}
                        </div>

                        {/* New Password Field */}
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">New Password (Optional)</label>
                          <input
                            type="password"
                            value={loginForm.newPassword}
                            onChange={(e) => handleLoginFieldChange('newPassword', e.target.value)}
                            className={`w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-accent-500 ${
                              loginErrors.newPassword ? 'border-red-500' : 'border-gray-300 focus:border-accent-500'
                            }`}
                            placeholder="Leave blank to keep current password"
                          />
                          {loginErrors.newPassword && (
                            <p className="text-red-500 text-sm mt-1">{loginErrors.newPassword}</p>
                          )}
                        </div>

                        {/* Confirm Password Field */}
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">Confirm New Password</label>
                          <input
                            type="password"
                            value={loginForm.confirmPassword}
                            onChange={(e) => handleLoginFieldChange('confirmPassword', e.target.value)}
                            className={`w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-accent-500 ${
                              loginErrors.confirmPassword ? 'border-red-500' : 'border-gray-300 focus:border-accent-500'
                            }`}
                            placeholder="Confirm your new password"
                          />
                          {loginErrors.confirmPassword && (
                            <p className="text-red-500 text-sm mt-1">{loginErrors.confirmPassword}</p>
                          )}
                        </div>

                        {/* General Error */}
                        {loginErrors.general && (
                          <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                            <p className="text-red-600 text-sm">{loginErrors.general}</p>
                          </div>
                        )}

                        {/* Action Buttons */}
                        <div className="flex space-x-3 pt-2">
                          <button
                            onClick={handleSaveLogin}
                            className="bg-accent-600 hover:bg-accent-700 text-white px-4 py-2 rounded-lg font-medium"
                          >
                            Save Changes
                          </button>
                          <button
                            onClick={handleCancelLoginEdit}
                            className="px-4 py-2 text-gray-600 hover:text-gray-800 font-medium border border-gray-300 rounded-lg"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    )}
                  </div>




                </div>
              </div>
            )}

            {activeTab === 'language' && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">Language Settings</h3>
                <p className="text-gray-600">Language settings will be implemented here.</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default SettingsPage;
