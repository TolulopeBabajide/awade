import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaBookOpen, FaFolder, FaHome, FaHeadset, FaCog, FaSignOutAlt, FaUser } from 'react-icons/fa';
import apiService from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import Sidebar from '../components/Sidebar';

const LessonResourcesPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [lessonResources, setLessonResources] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const loadLessonResources = async () => {
      if (!user) {
        setLoading(false);
        return;
      }

      try {
        const response = await apiService.getAllLessonResources();
        if (response.data) {
          setLessonResources(response.data);
        } else if (response.error) {
          setError(response.error);
        }
      } catch (err: any) {
        setError('Failed to load lesson resources');
        console.error('Error loading lesson resources:', err);
      } finally {
        setLoading(false);
      }
    };

    loadLessonResources();
  }, [user]);

  const handleResourceClick = (resource: any) => {
    navigate(`/lesson-plans/${resource.lesson_plan_id}/resources/edit`);
  };

  const getSubjectIcon = (subjectName: string) => {
    const lowerSubject = subjectName.toLowerCase();
    if (lowerSubject.includes('math') || lowerSubject.includes('mathematics')) {
      return '🔢';
    } else if (lowerSubject.includes('science') || lowerSubject.includes('biology') || lowerSubject.includes('chemistry') || lowerSubject.includes('physics')) {
      return '🧪';
    } else if (lowerSubject.includes('english') || lowerSubject.includes('language')) {
      return '📚';
    } else if (lowerSubject.includes('history') || lowerSubject.includes('social')) {
      return '🏛️';
    } else if (lowerSubject.includes('geography')) {
      return '🌍';
    } else if (lowerSubject.includes('art') || lowerSubject.includes('music')) {
      return '🎨';
    } else if (lowerSubject.includes('physical') || lowerSubject.includes('pe')) {
      return '⚽';
    } else {
      return '📖';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <Sidebar currentPage="lesson-resources" />

      {/* Main Content */}
      <main className="flex-1 lg:ml-64 p-4 md:p-6 lg:p-8 pb-20 md:pb-6 lg:pb-8">
        {/* Header */}
        <div className="flex justify-between items-start pt-0 pb-2 md:pb-4 lg:pb-5 px-2 md:px-4 lg:px-5 gap-2 md:gap-4 flex-shrink-0">
          {/* Left Side - Page Title and Description */}
          <div className="flex-1">
            <div className="text-left">
              <h2 className="text-xl md:text-2xl lg:text-3xl xl:text-4xl font-bold mb-1 md:mb-2 text-gray-900 mt-0 pt-0">Lesson Resources</h2>
              <p className="text-sm md:text-base lg:text-lg text-gray-600">Manage and view all your AI-generated lesson resources.</p>
            </div>
          </div>
          
          
        </div>

        {/* Content */}
        <div className="flex-1 p-2 md:p-4 lg:p-8 pb-20 md:pb-4 lg:pb-8 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
          ) : error ? (
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">⚠️</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-700 mb-2">Error Loading Resources</h3>
              <p className="text-gray-500">{error}</p>
            </div>
          ) : lessonResources.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-20 h-20 bg-gradient-to-br from-primary-100 to-primary-200 rounded-full flex items-center justify-center mx-auto mb-6">
                <FaBookOpen className="w-10 h-10 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-700 mb-3">No Lesson Resources Yet</h3>
              <p className="text-gray-500 mb-4">Create lesson plans to generate AI-powered resources</p>
              <button 
                onClick={() => navigate('/dashboard')}
                className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-3 rounded-lg transition-all duration-200 transform hover:scale-105"
              >
                Create Lesson Plan
              </button>
            </div>
          ) : (
            <>
              {/* Resources Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 md:gap-4 lg:gap-6">
                {lessonResources.map((resource: any) => {
                  // Parse AI content to get subject, topic, and grade level
                  let subject = 'Subject';
                  let topic = 'Topic';
                  let gradeLevel = 'Grade';
                  
                  try {
                    if (resource.ai_generated_content) {
                      const parsedContent = JSON.parse(resource.ai_generated_content);
                      if (parsedContent.title_header?.subject) {
                        subject = parsedContent.title_header.subject;
                      }
                      if (parsedContent.title_header?.topic) {
                        topic = parsedContent.title_header.topic;
                      }
                      if (parsedContent.title_header?.grade_level) {
                        gradeLevel = parsedContent.title_header.grade_level;
                      }
                    }
                  } catch (e) {
                    // If parsing fails, use default values
                  }
                  
                  return (
                    <div 
                      key={resource.lesson_resources_id} 
                      className="bg-white rounded-xl shadow-md hover:shadow-lg p-3 md:p-4 flex flex-col cursor-pointer transition-all duration-300 border border-gray-100 hover:border-primary-200 group"
                      onClick={() => handleResourceClick(resource)}
                    >
                      {/* Subject Icon - Centered */}
                      <div className="w-10 h-10 md:w-12 md:h-12 bg-gradient-to-br from-primary-100 to-primary-200 rounded-xl flex items-center justify-center mb-2 md:mb-3 text-lg md:text-xl group-hover:scale-110 transition-transform duration-300 mx-auto">
                        <FaBookOpen className="w-5 h-5 md:w-6 md:h-6 text-primary-600" />
                      </div>
                      
                      {/* Subject */}
                      <div className="text-xs md:text-sm font-semibold text-primary-600 mb-1 text-center">
                        {subject}
                      </div>
                      
                      {/* Topic */}
                      <div className="font-bold text-primary-900 mb-2 text-center line-clamp-2 text-xs md:text-sm leading-tight">
                        {topic}
                      </div>
                      
                      {/* Grade Level */}
                      <div className="text-xs text-primary-700 mb-1 text-center">
                        {gradeLevel}
                      </div>
                    </div>
                  );
                })}
              </div>
              
              {/* Resource Count */}
              <div className="text-center mt-8">
                <p className="text-sm text-gray-500">
                  Showing {lessonResources.length} lesson resource{lessonResources.length !== 1 ? 's' : ''}
                </p>
              </div>
            </>
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
            className="flex flex-col items-center py-2 px-3 text-gray-500 hover:text-primary-600 font-medium transition-colors duration-200"
            onClick={() => navigate('/lesson-plans')}
          >
            <FaBookOpen className="w-6 h-6 mb-1" />
            <span className="text-xs">Plans</span>
          </button>
          <button 
            className="flex flex-col items-center py-2 px-3 text-primary-600 font-medium transition-colors duration-200"
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

export default LessonResourcesPage;
