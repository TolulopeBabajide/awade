import React, { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import apiService from '../services/api';

interface LessonPlanData {
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

const LessonPlanDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const navigate = useNavigate();
  const [lessonPlan, setLessonPlan] = useState<LessonPlanData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [context, setContext] = useState('');
  const [isSubmittingContext, setIsSubmittingContext] = useState(false);
  const [isGeneratingLessonNote, setIsGeneratingLessonNote] = useState(false);
  const [contextFeedback, setContextFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  useEffect(() => {
    const fetchLessonPlan = async () => {
      try {
        // If we have data from navigation state, use it
        if (location.state?.lessonPlanData) {
          setLessonPlan(location.state.lessonPlanData);
          setLoading(false);
          return;
        }

        // Otherwise fetch from API
        const response = await apiService.getLessonPlan(id!);
        if (response.error) {
          throw new Error(response.error);
        }
        if (response.data) {
          setLessonPlan(response.data);
        } else {
          throw new Error('No data received from lesson plan request');
        }
      } catch (err: any) {
        console.error('Error loading lesson plan:', err);
        if (err.message?.includes('403')) {
          setError('You do not have permission to access this lesson plan. It may belong to another user.');
        } else if (err.message?.includes('404')) {
          setError('Lesson plan not found. It may have been deleted or moved.');
        } else {
          setError(err.message || 'Failed to load lesson plan. Please try again.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchLessonPlan();
  }, [id, location.state]);

  const handleContextSubmit = async () => {
    if (!context.trim() || !lessonPlan) return;

    setIsSubmittingContext(true);
    setContextFeedback(null);
    
    try {
      // Submit context to database
      const contextResponse = await apiService.submitContext(
        lessonPlan.lesson_id.toString(),
        context
      );

      if (contextResponse.error) {
        throw new Error(contextResponse.error);
      }

      // Generate lesson resource with the submitted context
      const resourceResponse = await apiService.generateLessonResource(
        lessonPlan.lesson_id.toString(),
        context
      );

      if (resourceResponse.error) {
        throw new Error(resourceResponse.error);
      }

      // Show success feedback
      setContextFeedback({
        type: 'success',
        message: 'Context submitted successfully! Lesson resource generated. You can now view and edit the generated content.'
      });
      setContext('');
      
      // Clear feedback after 5 seconds
      setTimeout(() => setContextFeedback(null), 5000);
    } catch (err: any) {
      setContextFeedback({
        type: 'error',
        message: err.message || 'Failed to submit context. Please try again.'
      });
    } finally {
      setIsSubmittingContext(false);
    }
  };

  const handleGenerateLessonNote = async () => {
    if (!lessonPlan) return;

    setIsGeneratingLessonNote(true);
    try {
      // Generate lesson resource using GPT service
      const response = await apiService.generateLessonResource(
        lessonPlan.lesson_id.toString(),
        context || 'Generate a comprehensive lesson note for this lesson plan'
      );

      if (response.error) {
        throw new Error(response.error);
      }

      // Navigate to the edit page after successful generation
      navigate(`/lesson-plans/${lessonPlan.lesson_id}/resources/edit`);
    } catch (err: any) {
      setError(err.message || 'Failed to generate lesson resource');
    } finally {
      setIsGeneratingLessonNote(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-400 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading lesson plan...</p>
        </div>
      </div>
    );
  }

  if (error || !lessonPlan) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error || 'Lesson plan not found'}</p>
          <button 
            onClick={() => navigate('/dashboard')}
            className="bg-orange-400 text-white px-4 py-2 rounded hover:bg-orange-500"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-80 bg-white border-r flex flex-col py-8 px-4 min-h-screen">
        <div className="mb-6">
          <button 
            onClick={() => navigate('/dashboard')}
            className="text-primary-600 text-sm mb-2 flex items-center hover:text-primary-700 transition-colors duration-200"
          >
            &larr; Back to Dashboard
          </button>
        </div>
        
        {/* Context Input Section */}
        <div className="mb-6">
          <h3 className="font-bold mb-3 text-primary-900">Add Context</h3>
          <textarea
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="Add local context, available resources, student background, or any specific requirements..."
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200"
            rows={4}
          />
          
          {/* Loading State and Feedback */}
          {isSubmittingContext && (
            <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-600 border-t-transparent"></div>
                <span className="text-blue-800 text-sm font-medium">Processing context and generating resource...</span>
              </div>
              <p className="text-blue-600 text-xs mt-2">This may take 30-60 seconds depending on complexity</p>
            </div>
          )}
          
          {/* Success/Error Feedback */}
          {contextFeedback && (
            <div className={`mt-3 p-3 rounded-lg border ${
              contextFeedback.type === 'success' 
                ? 'bg-green-50 border-green-200' 
                : 'bg-red-50 border-red-200'
            }`}>
              <div className="flex items-center space-x-2">
                <span className={`text-sm font-medium ${
                  contextFeedback.type === 'success' ? 'text-green-800' : 'text-red-800'
                }`}>
                  {contextFeedback.type === 'success' ? '✅' : '❌'} {contextFeedback.message}
                </span>
              </div>
            </div>
          )}
          
          <button
            onClick={handleContextSubmit}
            disabled={!context.trim() || isSubmittingContext}
            className="w-full mt-2 bg-primary-600 text-white font-semibold px-4 py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm transition-colors duration-200"
          >
            {isSubmittingContext ? (
              <div className="flex items-center justify-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                <span>Processing...</span>
              </div>
            ) : (
              'Submit Context'
            )}
          </button>
        </div>

        {/* Quick Actions */}
        {/* <div className="flex-1">
          <h3 className="font-bold mb-3 text-primary-900">Quick Actions</h3>
          <div className="space-y-2">
            <button className="w-full text-left px-3 py-2 rounded-lg bg-gray-100 hover:bg-primary-50 hover:text-primary-700 text-sm text-gray-700 transition-colors duration-200">
              📝 Edit Plan
            </button>
            <button 
              onClick={handleGenerateLessonNote}
              disabled={isGeneratingLessonNote}
              className="w-full text-left px-3 py-2 rounded-lg bg-primary-100 hover:bg-primary-200 text-primary-700 text-sm disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            >
              {isGeneratingLessonNote ? 'Generating...' : '📝 Generate Lesson Note'}
            </button>
            <button className="w-full text-left px-3 py-2 rounded-lg bg-gray-100 hover:bg-primary-50 hover:text-primary-700 text-sm text-gray-700 transition-colors duration-200">
              📄 Export PDF
            </button>
            <button className="w-full text-left px-3 py-2 rounded-lg bg-gray-100 hover:bg-primary-50 hover:text-primary-700 text-sm text-gray-700 transition-colors duration-200">
              🔗 Share Plan
            </button>
          </div>
        </div> */}
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-10">
        {/* Breadcrumb */}
        <div className="flex items-center text-sm text-gray-500 mb-4 gap-2">
          <span className="font-bold text-primary-700">Dashboard</span>
          <span>&gt;</span>
          <span className="font-bold text-primary-700">Lesson Plans</span>
          <span>&gt;</span>
          <span className="font-bold text-primary-600">{lessonPlan.subject}</span>
        </div>

        <div className="flex gap-8">
          {/* Main lesson plan panel */}
          <div className="flex-1 bg-white rounded-xl shadow-lg p-8">
            <div className="flex items-center gap-4 mb-2">
              <span className="bg-primary-100 text-primary-700 rounded-lg px-3 py-1 text-xs font-semibold">{lessonPlan.grade_level}</span>
            </div>
            <div className="text-xl font-bold mb-2 text-gray-900">{lessonPlan.title}</div>
            <div className="text-sm text-gray-500 mb-6">
              Created: {new Date(lessonPlan.created_at).toLocaleDateString()}
            </div>

            {/* Curriculum Learning Objectives */}
            <div className="mb-6">
              <div className="font-bold mb-3 text-lg text-primary-900">Curriculum Learning Objectives</div>
              <div className="bg-primary-50 p-4 rounded-lg border border-primary-100">
                {lessonPlan.curriculum_learning_objectives && lessonPlan.curriculum_learning_objectives.length > 0 ? (
                  <ul className="list-disc ml-6 text-primary-800 space-y-1">
                    {lessonPlan.curriculum_learning_objectives.map((objective, index) => (
                      <li key={index} className="text-sm">{objective}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-primary-600 text-sm">No learning objectives available for this topic.</p>
                )}
              </div>
            </div>

            {/* Curriculum Contents */}
            <div className="mb-6">
              <div className="font-bold mb-3 text-lg text-primary-900">Curriculum Contents</div>
              <div className="bg-accent-50 p-4 rounded-lg border border-accent-100">
                {lessonPlan.curriculum_contents && lessonPlan.curriculum_contents.length > 0 ? (
                  <ul className="list-disc ml-6 text-accent-800 space-y-1">
                    {lessonPlan.curriculum_contents.map((content, index) => (
                      <li key={index} className="text-sm">{content}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-accent-600 text-sm">No content areas available for this topic.</p>
                )}
              </div>
            </div>

            {/* Lesson Details */}
            <div className="mb-6">
              <div className="font-bold mb-3 text-lg text-primary-900">Lesson Details</div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-semibold text-primary-700">Topic:</span> <span className="text-gray-700">{lessonPlan.topic}</span>
                </div>
                <div>
                  <span className="font-semibold text-primary-700">Duration:</span> <span className="text-gray-700">{lessonPlan.duration_minutes} minutes</span>
                </div>
                
                <div>
                  <span className="font-semibold text-primary-700">Status:</span> <span className="text-gray-700">{lessonPlan.status}</span>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4 mt-8">
              <button className="bg-gray-200 text-gray-700 font-semibold px-6 py-3 rounded-lg hover:bg-gray-300 flex items-center gap-2 transition-colors duration-200">
                ✏️ Edit Plan
              </button>
              <button 
                onClick={handleGenerateLessonNote}
                disabled={isGeneratingLessonNote}
                className="bg-primary-600 text-white font-semibold px-6 py-3 rounded-lg hover:bg-primary-700 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
              >
                {isGeneratingLessonNote ? 'Generating...' : '📝 Generate Lesson Note'}
              </button>
            </div>
          </div>

          {/* Right panel: Additional Info */}
          <div className="w-64 flex flex-col gap-6">
            <div className="bg-white rounded-xl shadow-lg p-4 border border-gray-100">
              <div className="font-bold mb-2 text-primary-900">Lesson Info</div>
              <div className="text-sm text-gray-600 space-y-1">
                <div><span className="font-semibold text-primary-700">ID:</span> <span className="text-gray-700">{lessonPlan.lesson_id}</span></div>
                <div><span className="font-semibold text-primary-700">Subject:</span> <span className="text-gray-700">{lessonPlan.subject}</span></div>
                <div><span className="font-semibold text-primary-700">Grade:</span> <span className="text-gray-700">{lessonPlan.grade_level}</span></div>
                <div><span className="font-semibold text-primary-700">Topic:</span> <span className="text-gray-700">{lessonPlan.topic}</span></div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-4 border border-gray-100">
              <div className="font-bold mb-2 text-primary-900">Curriculum Standards</div>
              <div className="text-xs text-gray-700">
                <p>This lesson plan is aligned with the national curriculum standards for {lessonPlan.subject} in {lessonPlan.grade_level}.</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default LessonPlanDetailPage; 