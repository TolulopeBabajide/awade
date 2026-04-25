import React from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import MobileNavigation from '../components/MobileNavigation';
import { FaBookOpen } from 'react-icons/fa';
import { parseResourceContent } from '../utils/subjectIcons';
import { useAllLessonResources } from '../hooks/useEducatorData';

const LessonResourcesPage: React.FC = () => {
  const navigate = useNavigate();

  const { data: lessonResources = [], isLoading: loading, error: queryError } = useAllLessonResources();
  const error = queryError instanceof Error ? queryError.message : '';

  const handleResourceClick = (resource: any) => {
    navigate(`/lesson-plans/${resource.lesson_plan_id}/resources/edit`);
  };

  return (
    <div className="bg-gray-50 flex min-h-screen">
      <Sidebar currentPage="lesson-resources" />

      <main className="flex-1 lg:ml-64 p-4 md:p-6 lg:p-8 pb-20 lg:pb-8">
        {/* Header */}
        <div className="flex justify-between items-start pt-0 pb-2 md:pb-4 lg:pb-5 px-2 md:px-4 lg:px-5 gap-2 md:gap-4 flex-shrink-0">
          <div className="flex-1">
            <div className="text-left">
              <h2 className="text-xl md:text-2xl lg:text-3xl xl:text-4xl font-bold mb-1 md:mb-2 text-gray-900 mt-0 pt-0">Lesson Resources</h2>
              <p className="text-sm md:text-base lg:text-lg text-gray-600">Manage and view all your AI-generated lesson resources.</p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 p-2 md:p-4 lg:p-8 overflow-y-auto">
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
              <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 md:gap-4 lg:gap-6">
                {lessonResources.map((resource: any) => {
                  const { subject, topic, gradeLevel } = parseResourceContent(resource);

                  return (
                    <div
                      key={resource.lesson_resources_id}
                      className="bg-white rounded-xl shadow-md hover:shadow-lg p-3 md:p-4 flex flex-col cursor-pointer transition-all duration-300 border border-gray-100 hover:border-primary-200 group"
                      onClick={() => handleResourceClick(resource)}
                    >
                      <div className="w-10 h-10 md:w-12 md:h-12 bg-gradient-to-br from-primary-100 to-primary-200 rounded-xl flex items-center justify-center mb-2 md:mb-3 text-lg md:text-xl group-hover:scale-110 transition-transform duration-300 mx-auto">
                        <FaBookOpen className="w-5 h-5 md:w-6 md:h-6 text-primary-600" />
                      </div>
                      <div className="text-xs md:text-sm font-semibold text-primary-600 mb-1 text-center">{subject}</div>
                      <div className="font-bold text-primary-900 mb-2 text-center line-clamp-2 text-xs md:text-sm leading-tight">{topic}</div>
                      <div className="text-xs text-primary-700 mb-1 text-center">{gradeLevel}</div>
                    </div>
                  );
                })}
              </div>

              <div className="text-center mt-8">
                <p className="text-sm text-gray-500">
                  Showing {lessonResources.length} lesson resource{lessonResources.length !== 1 ? 's' : ''}
                </p>
              </div>
            </>
          )}
        </div>
      </main>

      <MobileNavigation />
    </div>
  );
};

export default LessonResourcesPage;
