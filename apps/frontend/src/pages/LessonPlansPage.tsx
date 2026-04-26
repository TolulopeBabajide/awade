import React from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import MobileNavigation from '../components/MobileNavigation';
import { FaBookOpen, FaPlus } from 'react-icons/fa';
import { getSubjectIcon } from '../utils/subjectIcons';
import { useLessonPlans } from '../hooks/useEducatorData';

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

const formatDuration = (minutes: number) => {
  if (minutes < 60) return `${minutes} min`;
  if (minutes === 60) return '1 hour';
  const hours = Math.floor(minutes / 60);
  const rem = minutes % 60;
  return rem === 0 ? `${hours} hour${hours > 1 ? 's' : ''}` : `${hours}h ${rem}m`;
};

const LessonPlansPage: React.FC = () => {
  const navigate = useNavigate();

  const { data: lessonPlans = [], isLoading: loading, error: queryError } = useLessonPlans();
  const error = queryError instanceof Error ? queryError.message : '';

  const handleLessonPlanClick = (lessonPlan: LessonPlan) => {
    navigate(`/lesson-plans/${lessonPlan.lesson_id}`, {
      state: { lessonPlanData: lessonPlan }
    });
  };

  if (loading) {
    return (
      <div className="bg-gray-50 flex min-h-screen">
        <Sidebar currentPage="lesson-plans" />
        <main className="flex-1 lg:ml-64 p-4 md:p-6 lg:p-8 pb-20 lg:pb-8">
          <div className="flex justify-between items-start pt-0 pb-2 md:pb-4 lg:pb-5 px-2 md:px-4 lg:px-5 gap-2 md:gap-4 flex-shrink-0">
            <div className="flex-1">
              <div className="text-left">
                <h2 className="text-xl md:text-2xl lg:text-3xl xl:text-4xl font-bold mb-1 md:mb-2 text-gray-900 mt-0 pt-0">My Lesson Plans</h2>
                <p className="text-sm md:text-base lg:text-lg text-gray-600">View and manage all your created lesson plans.</p>
              </div>
            </div>
            <div className="flex items-center space-x-2 md:space-x-3 flex-shrink-0">
              <button
                className="bg-accent-600 hover:bg-accent-700 text-white font-semibold px-3 md:px-6 py-2 md:py-3 rounded-lg flex items-center gap-2 transition-colors duration-200 text-sm md:text-base"
                onClick={() => navigate('/dashboard')}
              >
                <FaPlus className="w-3 h-3 md:w-4 md:h-4" />
                <span className="hidden sm:inline">Create Lesson Plan</span>
                <span className="sm:hidden">Create</span>
              </button>
            </div>
          </div>

          <div className="flex-1 p-2 md:p-4 lg:p-8 overflow-y-auto">
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Loading lesson plans...</p>
              </div>
            </div>
          </div>
        </main>
        <MobileNavigation />
      </div>
    );
  }

  return (
    <div className="bg-gray-50 flex min-h-screen">
      <Sidebar currentPage="lesson-plans" />

      <main className="flex-1 lg:ml-64 p-4 md:p-6 lg:p-8 pb-20 lg:pb-8">
        {/* Header */}
        <div className="flex justify-between items-start pt-0 pb-2 md:pb-4 lg:pb-5 px-2 md:px-4 lg:px-5 gap-2 md:gap-4 flex-shrink-0">
          <div className="flex-1">
            <div className="text-left">
              <h2 className="text-xl md:text-2xl lg:text-3xl xl:text-4xl font-bold mb-1 md:mb-2 text-gray-900 mt-0 pt-0">My Lesson Plans</h2>
              <p className="text-sm md:text-base lg:text-lg text-gray-600">View and manage all your created lesson plans.</p>
            </div>
          </div>
          <div className="flex items-center space-x-2 md:space-x-3 flex-shrink-0">
            <button
              className="bg-accent-600 hover:bg-accent-700 text-white font-semibold px-3 md:px-6 py-2 md:py-3 rounded-lg flex items-center gap-2 transition-colors duration-200 text-sm md:text-base"
              onClick={() => navigate('/dashboard')}
            >
              <FaPlus className="w-3 h-3 md:w-4 md:h-4" />
              <span className="hidden sm:inline">Create Lesson Plan</span>
              <span className="sm:hidden">Create</span>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 p-2 md:p-4 lg:p-8 overflow-y-auto">
          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            </div>
          )}

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

          {lessonPlans.length > 0 && (
            <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 md:gap-4 lg:gap-6 mt-4">
              {lessonPlans.map((plan: any) => (
                <div
                  key={plan.lesson_id}
                  className="bg-white rounded-xl shadow-md hover:shadow-lg p-3 md:p-4 flex flex-col cursor-pointer transition-all duration-300 border border-gray-100 hover:border-primary-200 group"
                  onClick={() => handleLessonPlanClick(plan)}
                >
                  <div className="w-10 h-10 md:w-12 md:h-12 bg-gradient-to-br from-primary-100 to-primary-200 rounded-xl flex items-center justify-center mb-2 md:mb-3 text-lg md:text-xl group-hover:scale-110 transition-transform duration-300 mx-auto">
                    {getSubjectIcon(plan.subject)}
                  </div>
                  <div className="text-xs md:text-sm font-semibold text-primary-600 mb-1 text-center">{plan.subject}</div>
                  <div className="font-bold text-primary-900 mb-2 text-center line-clamp-2 text-xs md:text-sm leading-tight">{plan.title || plan.topic}</div>
                  <div className="text-xs text-primary-700 mb-1 text-center">{plan.grade_level}</div>
                  <div className="text-xs text-gray-500 mb-1 text-center">{formatDuration(plan.duration_minutes)}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>

      <MobileNavigation />
    </div>
  );
};

export default LessonPlansPage;
