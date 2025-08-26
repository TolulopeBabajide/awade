import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaBookOpen, FaFolder, FaHome, FaHeadset, FaCog, FaSignOutAlt, FaUser, FaEye, FaEdit, FaTrash } from 'react-icons/fa';
import { useAuth } from '../contexts/AuthContext';
import apiService from '../services/api';
import Sidebar from '../components/Sidebar';

interface LessonPlan {
  lesson_id: number;
  title: string;
  subject: string;
  grade_level: string;
  topic: string;
  author_id: number;
  duration_minutes: number;
  created_at: string;
  updated_at: string;
  status: string;
  curriculum_learning_objectives: string[];
  curriculum_contents: string[];
}

const LessonPlansPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [lessonPlans, setLessonPlans] = useState<LessonPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (showUserMenu && !(event.target as Element).closest('.user-menu-container')) {
        setShowUserMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showUserMenu]);

  useEffect(() => {
    fetchLessonPlans();
  }, []);

  const fetchLessonPlans = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await apiService.getLessonPlans();
      
      if (response.error) {
        throw new Error(response.error);
      }

      if (response.data) {
        setLessonPlans(response.data);
      } else {
        setLessonPlans([]);
      }
    } catch (err: any) {
      console.error('Error fetching lesson plans:', err);
      setError(err.message || 'Failed to load lesson plans');
    } finally {
      setLoading(false);
    }
  };

  const handleLessonPlanClick = (lessonPlan: LessonPlan) => {
    navigate(`/lesson-plans/${lessonPlan.lesson_id}`, { 
      state: { lessonPlanData: lessonPlan } 
    });
  };

  const getSubjectIcon = (subject: string) => {
    const subjectIcons: { [key: string]: string } = {
      'Biology': '🧪',
      'Chemistry': '⚗️',
      'Physics': '⚡',
      'Mathematics': '📐',
      'Social Studies': '🌍',
      'History': '📚',
      'Geography': '🗺️',
      'English': '📖',
      'Literature': '📚',
      'Science': '🔬',
      'Inter.Science': '🔬',
      'Computer Science': '💻',
      'Art': '🎨',
      'Music': '🎵',
      'Physical Education': '⚽',
      'Health': '🏥'
    };
    
    return subjectIcons[subject] || '📚';
  };

  const formatDuration = (minutes: number) => {
    if (minutes < 60) {
      return `${minutes} min`;
    } else if (minutes === 60) {
      return '1 hour';
    } else {
      const hours = Math.floor(minutes / 60);
      const remainingMinutes = minutes % 60;
      if (remainingMinutes === 0) {
        return `${hours} hour${hours > 1 ? 's' : ''}`;
      } else {
        return `${hours}h ${remainingMinutes}m`;
      }
    }
  };

  if (loading) {
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

          {/* Loading State */}
          <div className="flex-1 p-2 md:p-4 lg:p-8 overflow-y-auto">
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Loading lesson plans...</p>
              </div>
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
              onClick={() => navigate('/settings')}
            >
              <FaCog className="w-6 h-6 mb-1" />
              <span className="text-xs">Settings</span>
            </button>
          </div>
        </nav>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 flex min-h-screen">
      {/* Sidebar */}
      <Sidebar currentPage="lesson-plans" />

      {/* Main Content */}
      <main className="flex-1 lg:ml-64 p-4 md:p-6 lg:p-8 pb-20 lg:pb-8">
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
        <div className="flex-1 p-2 md:p-4 lg:p-8 overflow-y-auto">
          {/* Error Message */}
          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <p className="text-red-800 text-sm">{error}</p>
                <button 
                  onClick={fetchLessonPlans}
                  className="text-red-600 hover:text-red-800 text-sm font-medium"
                >
                  Retry
                </button>
              </div>
            </div>
          )}

          {/* Empty State */}
          {!loading && lessonPlans.length === 0 && (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <FaBookOpen className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No lesson plans yet</h3>
              <p className="text-gray-600 mb-6">Get started by creating your first lesson plan.</p>
              <button
                onClick={() => navigate('/dashboard')}
                className="bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 transition-colors duration-200"
              >
                Create Lesson Plan
              </button>
            </div>
          )}

          {/* Lesson Plans Grid */}
          {lessonPlans.length > 0 && (
            <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 md:gap-4 lg:gap-6 mt-2 md:mt-4">
              {lessonPlans.map((plan) => (
                <div 
                  key={plan.lesson_id} 
                  className="bg-white rounded-xl shadow-md hover:shadow-lg p-3 md:p-4 flex flex-col cursor-pointer transition-all duration-300 border border-gray-100 hover:border-primary-200 group"
                  onClick={() => handleLessonPlanClick(plan)}
                >
                  {/* Subject Icon - Centered */}
                  <div className="w-10 h-10 md:w-12 md:h-12 bg-gradient-to-br from-primary-100 to-primary-200 rounded-xl flex items-center justify-center mb-2 md:mb-3 text-lg md:text-xl group-hover:scale-110 transition-transform duration-300 mx-auto">
                    {getSubjectIcon(plan.subject)}
                  </div>
                  
                  {/* Subject */}
                  <div className="text-xs md:text-sm font-semibold text-primary-600 mb-1 text-center">
                    {plan.subject}
                  </div>
                  
                  {/* Topic */}
                  <div className="font-bold text-primary-900 mb-2 text-center line-clamp-2 text-xs md:text-sm leading-tight">
                    {plan.title || plan.topic}
                  </div>
                  
                  {/* Grade Level */}
                  <div className="text-xs text-primary-700 mb-1 text-center">
                    {plan.grade_level}
                  </div>
                  
                  {/* Duration */}
                  <div className="text-xs text-gray-500 mb-1 text-center">
                    {formatDuration(plan.duration_minutes)}
                  </div>

                  {/* Status Badge
                  <div className="mt-2 text-center">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      plan.status === 'completed' 
                        ? 'bg-green-100 text-green-800' 
                        : plan.status === 'in_progress'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {plan.status === 'completed' ? 'Completed' : 
                       plan.status === 'in_progress' ? 'In Progress' : 
                       plan.status === 'draft' ? 'Draft' : plan.status}
                    </span>
                  </div> */}
                </div>
              ))}
            </div>
          )}
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
            onClick={() => navigate('/settings')}
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