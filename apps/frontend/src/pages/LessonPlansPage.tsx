import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaBookOpen, FaFolder, FaHome, FaHeadset, FaCog, FaSignOutAlt, FaUser } from 'react-icons/fa';
import { useAuth } from '../contexts/AuthContext';

const lessonPlans = [
  {
    subject: 'Social Studies',
    topic: 'Importance of United Family',
    grade: 'Grade 2',
    weeks: '12 Weeks Plan',
    icon: '🧑‍🏫',
  },
  {
    subject: 'Biology',
    topic: 'Photosynthesis',
    grade: 'Grade 3',
    weeks: '4 Weeks Plan',
    icon: '🧪',
  },
  {
    subject: 'Biology',
    topic: 'Human Skeletal System',
    grade: 'Grade 6',
    weeks: '2 Weeks Plan',
    icon: '🧪',
  },
  {
    subject: 'Inter.Science',
    topic: 'Health, Safety & Environment',
    grade: 'Grade 3',
    weeks: '7 Weeks Plan',
    icon: '⚗️',
  },
  {
    subject: 'Biology',
    topic: 'Reproduction In Mammals',
    grade: 'Grade 8',
    weeks: '3 Weeks Plan',
    icon: '🧪',
  },
  {
    subject: 'Inter.Science',
    topic: 'Health, Safety & Environment',
    grade: 'Grade 3',
    weeks: '7 Weeks Plan',
    icon: '⚗️',
  },
];

const LessonPlansPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (showUserMenu && !(event.target as Element).closest('.user-menu-container')) {
        setShowUserMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showUserMenu]);

  return (
    <div className="min-h-screen flex flex-col lg:flex-row bg-gray-50">
      {/* Sidebar */}
      <aside className="hidden w-full lg:w-64 bg-white border-b lg:border-b-0 lg:border-r border-gray-200 lg:flex flex-row lg:flex-col pb-3 md:pb-4 lg:pb-8 px-2 md:px-4 lg:px-4 lg:min-h-screen items-center lg:items-stretch flex-shrink-0">
        {/* Logo */}
        <div className=" items-center mb-8 lg:mb-8 w-full justify-center">
          <span className="font-bold text-3xl text-center tracking-wide text-primary-800">AWADE</span>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-2 w-full hidden lg:block">
          <button 
            className="w-full text-left px-4 py-3 rounded-lg hover:bg-gray-100 text-gray-700 font-medium flex items-center"
            onClick={() => navigate('/dashboard')}
          >
            <FaHome className="w-4 h-4 mr-3" />
            Dashboard
          </button>
          <button className="w-full text-left px-4 py-3 rounded-lg bg-accent-600 text-white font-semibold flex items-center">
            <FaBookOpen className="w-4 h-4 mr-3" />
            Lesson Plans
          </button>
          <button 
            className="w-full text-left px-4 py-3 rounded-lg hover:bg-gray-100 text-gray-700 font-medium flex items-center"
            onClick={() => navigate('/lesson-resources')}
          >
            <FaFolder className="w-4 h-4 mr-3" />
            Resources
          </button>
          <button className="w-full text-left px-4 py-3 rounded-lg hover:bg-gray-100 text-gray-700 font-medium flex items-center">
            <FaCog className="w-4 h-4 mr-3" />
            Settings
          </button>
        </nav>

        {/* Logout */}
        <button 
          className="mt-8 text-left px-4 py-3 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg hidden lg:flex items-center" 
          onClick={logout}
        >
          <FaSignOutAlt className="w-4 h-4 mr-3" />
          Log out
        </button>
      </aside>

              {/* Main Content */}
        <main className="flex-1 flex flex-col mb-6 p-2 md:p-4 lg:p-6">
          {/* Header */}
          <div className="flex justify-between items-start pt-0 pb-2 md:pb-4 lg:pb-5 px-2 md:px-4 lg:px-5 gap-2 md:gap-4 flex-shrink-0">
            {/* Left Side - Page Title and Description */}
            <div className="flex-1">
              <div className="text-left">
                <h2 className="text-xl md:text-2xl lg:text-3xl xl:text-4xl font-bold mb-1 md:mb-2 text-gray-900 mt-0 pt-0">My Lesson Plans</h2>
                <p className="text-sm md:text-base lg:text-lg text-gray-600">View and manage all your created lesson plans.</p>
              </div>
            </div>
          
            {/* Right Side - User Profile and Create Button */}
            <div className="lg:flex hidden items-center space-x-2 md:space-x-3 flex-shrink-0">
              <button 
                className="bg-accent-600 hover:bg-accent-700 text-white font-semibold px-4 md:px-6 py-2 md:py-3 rounded-lg flex items-center gap-2 transition-colors duration-200"
                onClick={() => navigate('/dashboard')}
              >
                <span className=" sm:inline">Create Lesson Plan</span>
              </button>
              
            </div>
          </div>

        {/* Content */}
        <div className="flex-1 p-2 md:p-4 lg:p-8 pb-20 md:pb-4 lg:pb-8 overflow-y-auto">
          {/* Lesson Plans Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 p-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 md:gap-4 lg:gap-6 mt-2 md:mt-4">
            {lessonPlans.map((plan, idx) => (
              <div key={idx} className="bg-white gap-2 rounded-xl shadow-md hover:shadow-lg p-3 md:p-4 flex flex-col cursor-pointer transition-all duration-300 border border-gray-100 hover:border-primary-200 group">
                {/* Subject Icon - Centered */}
                <div className="w-10 h-10 md:w-12 md:h-12 bg-gradient-to-br from-primary-100 to-primary-200 rounded-xl flex items-center justify-center mb-2 md:mb-3 text-lg md:text-xl group-hover:scale-110 transition-transform duration-300 mx-auto">
                  {plan.icon}
                </div>
                
                {/* Subject */}
                <div className="text-xs md:text-sm font-semibold text-primary-600 mb-1 text-center">
                  {plan.subject}
                </div>
                
                {/* Topic */}
                <div className="font-bold text-primary-900 mb-2 text-center line-clamp-2 text-xs md:text-sm leading-tight">
                  {plan.topic}
                </div>
                
                {/* Grade Level */}
                <div className="text-xs text-primary-700 mb-1 text-center">
                  {plan.grade}
                </div>
                
                {/* Weeks */}
                <div className="text-xs text-gray-500 mb-1 text-center">
                  {plan.weeks}
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>

      {/* Mobile Bottom Navigation */}
      <nav className="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 py-3 z-50 shadow-lg">
        <div className="flex justify-around items-center">
          <button 
            className="flex flex-col items-center py-2 px-3 text-gray-500 hover:text-primary-600 font-medium transition-colors duration-200"
            onClick={() => navigate('/dashboard')}
          >
            <FaHome className="w-6 h-6 mb-1" />
            <span className="text-xs">Dashboard</span>
          </button>
          <button 
            className="flex flex-col items-center py-2 px-3 text-primary-600 font-medium transition-colors duration-200"
            onClick={() => navigate('/lesson-plans')}
          >
            <FaBookOpen className="w-6 h-6 mb-1" />
            <span className="text-xs">Plans</span>
          </button>
          <button 
            className="flex flex-col items-center py-2 px-3 text-gray-500 hover:text-primary-600 font-medium transition-colors duration-200"
            onClick={() => navigate('/lesson-resources')}
          >
            <FaFolder className="w-6 h-6 mb-1" />
            <span className="text-xs">Resources</span>
          </button>
          <button 
            className="flex flex-col items-center py-2 px-3 text-gray-500 hover:text-primary-600 font-medium transition-colors duration-200"
            onClick={() => navigate('/dashboard')}
          >
            <FaCog className="w-6 h-6 mb-1" />
            <span className="text-xs">Settings</span>
          </button>
        </div>
      </nav>
    </div>
  );
};

export default LessonPlansPage; 