import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import apiService from '../services/api';
import Sidebar from '../components/Sidebar';
// import Footer from '../components/Footer';
import { 
  FaUser, 
  FaShieldAlt, 
  FaGlobe, 
  FaTrash, 
  FaEdit, 
  FaTimes,
  FaCheck,
  FaSignOutAlt,
  FaBell,
  FaHeadset,
  FaPhone,
  FaEnvelope,
  FaMapMarkerAlt,
  FaUserEdit,
  FaKey,
  FaCog
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
  const [editingField, setEditingField] = useState<string | null>(null);
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
  const [showSettingsMenu, setShowSettingsMenu] = useState(false);

  useEffect(() => {
    if (user) {
      loadUserProfile();
    }
  }, [user]);

  // Handle click outside settings menu
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Element;
      if (showSettingsMenu && !target.closest('.settings-menu-container')) {
        setShowSettingsMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showSettingsMenu]);

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



  const handleSaveField = async (field: string) => {
    try {
      const updateData = { [field]: editForm[field as keyof typeof editForm] };
      
      if (!profileData?.user_id) {
        return;
      }
      
      const response = await apiService.updateProfile(updateData, profileData?.user_id);
      
      if (response.error) {
        return;
      }
      
      if (response.data) {
        setProfileData(response.data);
        setEditingField(null);
        // Update the form with new data
        setEditForm(prev => ({
          ...prev,
          [field]: response.data[field as keyof typeof response.data] || ''
        }));
      }
    } catch (error) {
      // Silent error handling
    }
  };

  const handleCancelEdit = (field: string) => {
    setEditingField(null);
    // Reset the specific field to current profile data
    if (profileData) {
      setEditForm(prev => ({
        ...prev,
        [field]: profileData[field as keyof typeof profileData] || ''
      }));
    }
  };

  const handleStartEdit = (field: string) => {
    setEditingField(field);
  };

  // Login details editing functions
  const handleEditLogin = () => {
    setIsEditingLogin(true);
    setLoginForm({
      email: profileData?.email || user?.email || '',
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
      <main className="flex-1 lg:ml-64 p-4 md:p-6 lg:p-8 pb-20 md:pb-6 lg:pb-8">
        {/* Header */}
        <div className="flex justify-between items-start pt-0 pb-2 md:pb-4 lg:pb-5 px-2 md:px-4 lg:px-5 gap-2 md:gap-4 flex-shrink-0">
          {/* Left Side - Page Title and Description */}
          <div className="flex-1">
            <div className="text-left">
              <h2 className="text-xl md:text-2xl lg:text-3xl xl:text-4xl font-bold mb-1 md:mb-2 text-gray-900 mt-0 pt-0">Account Settings</h2>
              <p className="text-sm md:text-base lg:text-lg text-gray-600">Manage your profile, security, and preferences.</p>
            </div>
          </div>
          
          {/* Right Side - Settings Menu */}
          <div className="flex items-center space-x-2 md:space-x-3 flex-shrink-0">
            <div className="relative settings-menu-container">
              <button 
                onClick={() => setShowSettingsMenu(!showSettingsMenu)}
                className="w-8 h-8 md:w-10 md:h-10 bg-accent-600 rounded-full flex items-center justify-center hover:bg-accent-700 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:ring-offset-2"
              >
                <FaCog className="w-4 h-4 md:w-5 md:h-5 text-white" />
              </button>
              
              {/* Settings Menu Popup */}
              {showSettingsMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
                  <button 
                    onClick={() => { setActiveTab('profile'); setShowSettingsMenu(false); }}
                    className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-50 flex items-center ${
                      activeTab === 'profile' ? 'text-accent-600 bg-accent-50' : 'text-gray-700'
                    }`}
                  >
                    <FaUser className="w-4 h-4 mr-2" />
                    My Profile
                  </button>
                  <button 
                    onClick={() => { setActiveTab('security'); setShowSettingsMenu(false); }}
                    className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-50 flex items-center ${
                      activeTab === 'security' ? 'text-accent-600 bg-accent-50' : 'text-gray-700'
                    }`}
                  >
                    <FaShieldAlt className="w-4 h-4 mr-2" />
                    Security
                  </button>
                  <button 
                    onClick={() => { setActiveTab('language'); setShowSettingsMenu(false); }}
                    className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-50 flex items-center ${
                      activeTab === 'language' ? 'text-accent-600 bg-accent-50' : 'text-gray-700'
                    }`}
                  >
                    <FaGlobe className="w-4 h-4 mr-2" />
                    Language
                  </button>
                  <div className="border-t border-gray-100 my-1"></div>
                  <button 
                    onClick={() => setShowSettingsMenu(false)}
                    className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center"
                  >
                    <FaTrash className="w-4 h-4 mr-2" />
                    Delete Account
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 p-2 md:p-4 lg:p-8 pb-20 md:pb-4 lg:pb-8 overflow-y-auto">

          {/* Content Area */}
          <div className="flex-1">
            {activeTab === 'profile' && (
              <div className="bg-white rounded-xl shadow-md border border-gray-100 p-4 md:p-6">
                <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between mb-4 sm:mb-6 gap-4">
                  <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
                    {/* Profile Image */}
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



                {/* Personal Information */}
                <div className="mb-6 sm:mb-8">
                  <h3 className="text-lg sm:text-xl font-semibold text-gray-900 mb-3 sm:mb-4">Personal Information</h3>
                  <div className="space-y-4">
                    {/* Full Name */}
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex-1">
                        <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                        {editingField === 'full_name' ? (
                          <input
                            type="text"
                            value={editForm.full_name}
                            onChange={(e) => handleInputChange('full_name', e.target.value)}
                            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500"
                          />
                        ) : (
                          <p className="text-gray-900">{profileData?.full_name || 'Not set'}</p>
                        )}
                      </div>
                      <div className="flex space-x-2 ml-3">
                        {editingField === 'full_name' ? (
                          <>
                            <button
                              onClick={() => handleSaveField('full_name')}
                              className="p-2 text-green-600 hover:text-green-700 hover:bg-green-50 rounded-lg transition-colors duration-200"
                              title="Save changes"
                            >
                              <FaCheck className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleCancelEdit('full_name')}
                              className="p-2 text-gray-600 hover:text-gray-700 hover:bg-gray-50 rounded-lg transition-colors duration-200"
                            >
                              <FaTimes className="w-4 h-4" />
                            </button>
                          </>
                        ) : (
                          <button
                            onClick={() => handleStartEdit('full_name')}
                            className="p-2 text-accent-600 hover:text-accent-700 hover:bg-accent-50 rounded-lg transition-colors duration-200"
                          >
                            <FaEdit className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </div>
                    
                    {/* Country */}
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex-1">
                        <label className="block text-sm font-medium text-gray-700 mb-1">Country</label>
                        {editingField === 'country' ? (
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
                      <div className="flex space-x-2 ml-3">
                        {editingField === 'country' ? (
                          <>
                            <button
                              onClick={() => handleSaveField('country')}
                              className="p-2 text-green-600 hover:text-green-700 hover:bg-green-50 rounded-lg transition-colors duration-200"
                              title="Save changes"
                            >
                              <FaCheck className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleCancelEdit('country')}
                              className="p-2 text-gray-600 hover:text-gray-700 hover:bg-gray-50 rounded-lg transition-colors duration-200"
                            >
                              <FaTimes className="w-4 h-4" />
                            </button>
                          </>
                        ) : (
                          <button
                            onClick={() => handleStartEdit('country')}
                            className="p-2 text-accent-600 hover:text-accent-700 hover:bg-accent-50 rounded-lg transition-colors duration-200"
                          >
                            <FaEdit className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </div>
                    
                    {/* Phone */}
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex-1">
                        <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                        {editingField === 'phone' ? (
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
                      <div className="flex space-x-2 ml-3">
                        {editingField === 'phone' ? (
                          <>
                            <button
                              onClick={() => handleSaveField('phone')}
                              className="p-2 text-green-600 hover:text-green-700 hover:bg-green-50 rounded-lg transition-colors duration-200"
                              title="Save changes"
                            >
                              <FaCheck className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleCancelEdit('phone')}
                              className="p-2 text-gray-600 hover:text-gray-700 hover:bg-gray-50 rounded-lg transition-colors duration-200"
                            >
                              <FaTimes className="w-4 h-4" />
                            </button>
                          </>
                        ) : (
                          <button
                            onClick={() => handleStartEdit('phone')}
                            className="p-2 text-accent-600 hover:text-accent-700 hover:bg-accent-50 rounded-lg transition-colors duration-200"
                          >
                            <FaEdit className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </div>
                    
                    {/* City/Region */}
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex-1">
                        <label className="block text-sm font-medium text-gray-700 mb-1">City/Region</label>
                        {editingField === 'region' ? (
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
                      <div className="flex space-x-2 ml-3">
                        {editingField === 'region' ? (
                          <>
                            <button
                              onClick={() => handleSaveField('region')}
                              className="p-2 text-green-600 hover:text-green-700 hover:bg-green-50 rounded-lg transition-colors duration-200"
                              title="Save changes"
                            >
                              <FaCheck className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleCancelEdit('region')}
                              className="p-2 text-gray-600 hover:text-gray-700 hover:bg-gray-50 rounded-lg transition-colors duration-200"
                            >
                              <FaTimes className="w-4 h-4" />
                            </button>
                          </>
                        ) : (
                          <button
                            onClick={() => handleStartEdit('region')}
                            className="p-2 text-accent-600 hover:text-accent-700 hover:bg-accent-50 rounded-lg transition-colors duration-200"
                          >
                            <FaEdit className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </div>
                    
                    {/* Bio */}
                    <div className="flex items-start justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex-1">
                        <label className="block text-sm font-medium text-gray-700 mb-1">Bio</label>
                        {editingField === 'bio' ? (
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
                      <div className="flex space-x-2 ml-3">
                        {editingField === 'bio' ? (
                          <>
                            <button
                              onClick={() => handleSaveField('bio')}
                              className="p-2 text-green-600 hover:text-green-700 hover:bg-green-50 rounded-lg transition-colors duration-200"
                              title="Save changes"
                            >
                              <FaCheck className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleCancelEdit('bio')}
                              className="p-2 text-gray-600 hover:text-gray-700 hover:bg-gray-50 rounded-lg transition-colors duration-200"
                            >
                              <FaTimes className="w-4 h-4" />
                            </button>
                          </>
                        ) : (
                          <button
                            onClick={() => handleStartEdit('bio')}
                            className="p-2 text-accent-600 hover:text-accent-700 hover:bg-accent-50 rounded-lg transition-colors duration-200"
                          >
                            <FaEdit className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>






              </div>
            )}

            {activeTab === 'security' && (
              <div className="bg-white rounded-xl shadow-md border border-gray-100 p-4 md:p-6">
                <div className="space-y-6 sm:space-y-8">
                  {/* Login Details */}
                  <div className="border-2 border-dashed border-blue-300 rounded-lg p-4 md:p-6">
                    <h3 className="text-lg sm:text-xl font-semibold text-gray-900 mb-3 sm:mb-4">Login Details</h3>
                    
                    {!isEditingLogin ? (
                      <div className="space-y-3">
                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                          <div>
                            <p className="text-sm text-gray-600">Email Address</p>
                            <p className="text-gray-900">{profileData?.email || user.email}</p>
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
            )}

            {activeTab === 'language' && (
              <div className="bg-white rounded-xl shadow-md border border-gray-100 p-4 md:p-6">
                <h3 className="text-lg sm:text-xl font-semibold text-gray-900 mb-3 sm:mb-4">Language Settings</h3>
                <p className="text-gray-600">Language settings will be implemented here.</p>
              </div>
            )}
          </div>
        </div>

        {/* Mobile Bottom Navigation */}
        <nav className="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 py-3 z-50 shadow-lg">
          <div className="flex justify-around items-center">
            <button 
              className="flex flex-col items-center py-2 px-3 text-gray-500 hover:text-primary-600 font-medium transition-colors duration-200"
              onClick={() => navigate('/dashboard')}
            >
              <FaUser className="w-6 h-6 mb-1" />
              <span className="text-xs">Dashboard</span>
            </button>
            <button 
              className="flex flex-col items-center py-2 px-3 text-gray-500 hover:text-primary-600 font-medium transition-colors duration-200"
              onClick={() => navigate('/lesson-plans')}
            >
              <FaShieldAlt className="w-6 h-6 mb-1" />
              <span className="text-xs">Plans</span>
            </button>
            <button 
              className="flex flex-col items-center py-2 px-3 text-gray-500 hover:text-primary-600 font-medium transition-colors duration-200"
              onClick={() => navigate('/lesson-resources')}
            >
              <FaGlobe className="w-6 h-6 mb-1" />
              <span className="text-xs">Resources</span>
            </button>
            <button 
              className="flex flex-col items-center py-2 px-3 text-primary-600 font-medium transition-colors duration-200"
              onClick={() => navigate('/settings')}
            >
              <FaCog className="w-6 h-6 mb-1" />
              <span className="text-xs">Settings</span>
            </button>
          </div>
        </nav>
      </main>

      {/* Footer */}
      {/* <Footer /> */}
    </div>
  );
};

export default SettingsPage;
