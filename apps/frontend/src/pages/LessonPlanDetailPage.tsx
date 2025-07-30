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
        const response = await fetch(`/api/lesson-plans/${id}`);
        if (!response.ok) {
          throw new Error('Failed to fetch lesson plan');
        }
        const data = await response.json();
        setLessonPlan(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load lesson plan');
      } finally {
        setLoading(false);
      }
    };

    fetchLessonPlan();
  }, [id, location.state]);

  const handleContextSubmit = async () => {
    if (!context.trim() || !lessonPlan) return;

    setIsSubmittingContext(true);
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

      // Show success message
      alert('Context submitted successfully! Resource generated.');
      setContext('');
    } catch (err: any) {
      setError(err.message || 'Failed to submit context');
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
            className="text-gray-500 text-sm mb-2 flex items-center hover:text-gray-700"
          >
            &larr; Back to Dashboard
          </button>
          <div className="text-lg font-bold mb-2">Lesson Plan</div>
        </div>
        
        {/* Context Input Section */}
        <div className="mb-6">
          <h3 className="font-bold mb-3">Add Context</h3>
          <textarea
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="Add local context, available resources, student background, or any specific requirements..."
            className="w-full border rounded px-3 py-2 text-sm resize-none"
            rows={4}
          />
          <button
            onClick={handleContextSubmit}
            disabled={!context.trim() || isSubmittingContext}
            className="w-full mt-2 bg-orange-400 text-white font-semibold px-4 py-2 rounded hover:bg-orange-500 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
          >
            {isSubmittingContext ? 'Submitting...' : 'Submit Context'}
          </button>
        </div>

        {/* Quick Actions */}
        <div className="flex-1">
          <h3 className="font-bold mb-3">Quick Actions</h3>
          <div className="space-y-2">
            <button className="w-full text-left px-3 py-2 rounded bg-gray-100 hover:bg-gray-200 text-sm">
              📝 Edit Plan
            </button>
            <button 
              onClick={handleGenerateLessonNote}
              disabled={isGeneratingLessonNote}
              className="w-full text-left px-3 py-2 rounded bg-gray-100 hover:bg-gray-200 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isGeneratingLessonNote ? 'Generating...' : '📝 Generate Lesson Note'}
            </button>
            <button className="w-full text-left px-3 py-2 rounded bg-gray-100 hover:bg-gray-200 text-sm">
              📄 Export PDF
            </button>
            <button className="w-full text-left px-3 py-2 rounded bg-gray-100 hover:bg-gray-200 text-sm">
              🔗 Share Plan
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-10">
        {/* Breadcrumb */}
        <div className="flex items-center text-sm text-gray-500 mb-4 gap-2">
          <span className="font-bold text-gray-700">Dashboard</span>
          <span>&gt;</span>
          <span className="font-bold text-gray-700">Lesson Plans</span>
          <span>&gt;</span>
          <span className="font-bold text-orange-700">{lessonPlan.subject}</span>
        </div>

        <div className="flex gap-8">
          {/* Main lesson plan panel */}
          <div className="flex-1 bg-white rounded shadow p-8">
            <div className="flex items-center gap-4 mb-2">
              <span className="font-bold text-lg">{lessonPlan.subject}</span>
              <span className="bg-gray-100 text-gray-700 rounded px-2 py-1 text-xs font-semibold">{lessonPlan.grade_level}</span>
              <span className="bg-gray-100 text-gray-700 rounded px-2 py-1 text-xs font-semibold capitalize">{lessonPlan.status}</span>
            </div>
            <div className="text-xl font-bold mb-2">{lessonPlan.title}</div>
            <div className="text-sm text-gray-500 mb-6">
              Created: {new Date(lessonPlan.created_at).toLocaleDateString()}
            </div>

            {/* Curriculum Learning Objectives */}
            <div className="mb-6">
              <div className="font-bold mb-3 text-lg">Curriculum Learning Objectives</div>
              <div className="bg-blue-50 p-4 rounded-lg">
                {lessonPlan.curriculum_learning_objectives && lessonPlan.curriculum_learning_objectives.length > 0 ? (
                  <ul className="list-disc ml-6 text-gray-700 space-y-1">
                    {lessonPlan.curriculum_learning_objectives.map((objective, index) => (
                      <li key={index} className="text-sm">{objective}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-gray-500 text-sm">No learning objectives available for this topic.</p>
                )}
              </div>
            </div>

            {/* Curriculum Contents */}
            <div className="mb-6">
              <div className="font-bold mb-3 text-lg">Curriculum Contents</div>
              <div className="bg-green-50 p-4 rounded-lg">
                {lessonPlan.curriculum_contents && lessonPlan.curriculum_contents.length > 0 ? (
                  <ul className="list-disc ml-6 text-gray-700 space-y-1">
                    {lessonPlan.curriculum_contents.map((content, index) => (
                      <li key={index} className="text-sm">{content}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-gray-500 text-sm">No content areas available for this topic.</p>
                )}
              </div>
            </div>

            {/* Lesson Details */}
            <div className="mb-6">
              <div className="font-bold mb-3 text-lg">Lesson Details</div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-semibold">Topic:</span> {lessonPlan.topic}
                </div>
                <div>
                  <span className="font-semibold">Duration:</span> {lessonPlan.duration_minutes} minutes
                </div>
                <div>
                  <span className="font-semibold">Author ID:</span> {lessonPlan.author_id}
                </div>
                <div>
                  <span className="font-semibold">Status:</span> {lessonPlan.status}
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4 mt-8">
              <button className="bg-gray-200 text-gray-700 font-semibold px-6 py-2 rounded hover:bg-gray-300 flex items-center gap-2">
                ✏️ Edit Plan
              </button>
              <button 
                onClick={handleGenerateLessonNote}
                disabled={isGeneratingLessonNote}
                className="bg-orange-400 text-white font-semibold px-6 py-2 rounded hover:bg-orange-500 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isGeneratingLessonNote ? 'Generating...' : '📝 Generate Lesson Note'}
              </button>
            </div>
          </div>

          {/* Right panel: Additional Info */}
          <div className="w-64 flex flex-col gap-6">
            <div className="bg-white rounded shadow p-4">
              <div className="font-bold mb-2">Lesson Info</div>
              <div className="text-sm text-gray-600 space-y-1">
                <div><span className="font-semibold">ID:</span> {lessonPlan.lesson_id}</div>
                <div><span className="font-semibold">Subject:</span> {lessonPlan.subject}</div>
                <div><span className="font-semibold">Grade:</span> {lessonPlan.grade_level}</div>
                <div><span className="font-semibold">Topic:</span> {lessonPlan.topic}</div>
              </div>
            </div>

            <div className="bg-white rounded shadow p-4">
              <div className="font-bold mb-2">Curriculum Standards</div>
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