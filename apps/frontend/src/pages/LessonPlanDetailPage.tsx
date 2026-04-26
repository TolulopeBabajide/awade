import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';

import Sidebar from '../components/Sidebar';
import MobileNavigation from '../components/MobileNavigation';
import AIGenerationLoadingActual from '../components/AIGenerationLoadingActual';

import apiService from '../services/api';
import { sanitizeInput } from '../utils/sanitizer';

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
  const [isGeneratingLessonResource, setIsGeneratingLessonResource] = useState(false);
  const [contextFeedback, setContextFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [currentGenerationStep, setCurrentGenerationStep] = useState<string>('');

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

  // ... existing code ...

  const handleGenerateLessonResource = async () => {
    if (!lessonPlan) return;

    setIsGeneratingLessonResource(true);
    setContextFeedback(null);
    setCurrentGenerationStep('validate-lesson-plan');

    try {
      // Sanitize context input
      const sanitizedContext = sanitizeInput(context);

      // Step 1: Submit context if provided
      if (sanitizedContext) {
        setCurrentGenerationStep('submit-context');
        const contextResponse = await apiService.submitContext(
          lessonPlan.lesson_id.toString(),
          sanitizedContext
        );

        if (contextResponse.error) {
          throw new Error(contextResponse.error);
        }
      }

      // Step 2: Fetch curriculum data (simulated)
      setCurrentGenerationStep('fetch-curriculum-data');
      await new Promise(resolve => setTimeout(resolve, 500)); // Brief pause to show step

      // Step 3: Generate lesson resource (starts async process)
      setCurrentGenerationStep('ai-generation');
      const response = await apiService.generateLessonResource(
        lessonPlan.lesson_id.toString(),
        sanitizedContext || 'Generate a comprehensive lesson resource for this lesson plan'
      );

      if (response.error || !response.data) {
        throw new Error(response.error || 'Failed to initiate resource generation');
      }

      let resource = response.data;
      const resourceId = resource.lesson_resources_id;

      // Step 4: Poll for completion if status is processing
      if (resource.status === 'processing') {
        setCurrentGenerationStep('ai-generation'); // Keep showing generation step

        let attempts = 0;
        const maxAttempts = 60; // 2 minutes timeout (2s * 60)

        while (resource.status === 'processing' && attempts < maxAttempts) {
          await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2s
          attempts++;

          const pollResponse = await apiService.getLessonResource(resourceId.toString());
          if (pollResponse.error || !pollResponse.data) {
            console.warn("Polling failed temporarily", pollResponse.error);
            continue; // Retry polling
          }

          resource = pollResponse.data;
        }

        if (resource.status === 'processing') {
          throw new Error('Generation timed out. Please check back later.');
        }

        if (resource.status === 'failed') {
          throw new Error('AI generation failed. Please try again.');
        }
      }

      // Step 5: Complete
      setCurrentGenerationStep('complete');
      await new Promise(resolve => setTimeout(resolve, 500)); // Brief pause before redirect

      // Show success feedback
      setContextFeedback({
        type: 'success',
        message: 'Lesson resource generated successfully! You can now view and edit the generated content.'
      });
      setContext('');

      // Clear feedback after 5 seconds
      setTimeout(() => setContextFeedback(null), 5000);

      // Navigate to the edit page after successful generation
      navigate(`/lesson-plans/${lessonPlan.lesson_id}/resources/edit`);
    } catch (err: any) {
      setContextFeedback({
        type: 'error',
        message: err.message || 'Failed to generate lesson resource. Please try again.'
      });
    } finally {
      setIsGeneratingLessonResource(false);
      setCurrentGenerationStep('');
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
    <div className="bg-gray-50 flex min-h-screen">
      {/* Sidebar */}
      <Sidebar currentPage="lesson-plans" />

      {/* Main Content */}
      <main className="flex-1 lg:ml-64 p-4 md:p-6 lg:p-8 pb-20 lg:pb-8">
        {/* Back Navigation */}
        <div className="mb-4 md:mb-6">
          <button
            onClick={() => navigate('/dashboard')}
            className="text-primary-600 text-sm mb-2 flex items-center hover:text-primary-700 transition-colors duration-200"
          >
            &larr; Back to Dashboard
          </button>
        </div>

        {/* Breadcrumb */}
        <div className="flex items-center text-sm text-gray-500 mb-3 md:mb-4 gap-2">
          <span className="font-bold text-primary-700">Dashboard</span>
          <span>&gt;</span>
          <span className="font-bold text-primary-700">Lesson Plans</span>
          <span>&gt;</span>
          <span className="font-bold text-primary-600">{lessonPlan.subject}</span>
        </div>

        <div className="flex flex-col lg:flex-row gap-4 lg:gap-6">
          {/* Main lesson plan panel */}
          <div className="flex-1 bg-white rounded-xl shadow-lg p-4 md:p-6 lg:p-8">
            <div className="flex items-center gap-4 mb-2">
              <span className="bg-primary-100 text-primary-700 rounded-lg px-3 py-1 text-xs font-semibold">{lessonPlan.grade_level}</span>
            </div>
            <div className="text-lg md:text-xl font-bold mb-2 text-gray-900">{lessonPlan.title}</div>
            <div className="text-sm text-gray-500 mb-4 md:mb-6">
              Created: {new Date(lessonPlan.created_at).toLocaleDateString()}
            </div>

            {/* Curriculum Learning Objectives */}
            <div className="mb-4 md:mb-6">
              <div className="font-bold mb-2 md:mb-3 text-base md:text-lg text-primary-900">Curriculum Learning Objectives</div>
              <div className="bg-primary-50 p-3 md:p-4 rounded-lg border border-primary-100">
                {lessonPlan.curriculum_learning_objectives && lessonPlan.curriculum_learning_objectives.length > 0 ? (
                  <ul className="list-disc ml-4 md:ml-6 text-primary-800 space-y-1">
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
            <div className="mb-4 md:mb-6">
              <div className="font-bold mb-2 md:mb-3 text-base md:text-lg text-primary-900">Curriculum Contents</div>
              <div className="bg-accent-50 p-3 md:p-4 rounded-lg border border-accent-100">
                {lessonPlan.curriculum_contents && lessonPlan.curriculum_contents.length > 0 ? (
                  <ul className="list-disc ml-4 md:ml-6 text-accent-800 space-y-1">
                    {lessonPlan.curriculum_contents.map((content, index) => (
                      <li key={index} className="text-sm">{content}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-accent-600 text-sm">No content areas available for this topic.</p>
                )}
              </div>
            </div>

            {/* Context Input Section */}
            <div className="mb-4 md:mb-6">
              <h3 className="font-bold mb-2 md:mb-3 text-base md:text-lg text-primary-900">Add Context</h3>
              <textarea
                value={context}
                onChange={(e) => setContext(e.target.value)}
                placeholder="Add local context, available resources, student background, or any specific requirements..."
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200"
                rows={3}
              />

              {/* Loading State and Feedback */}


              {/* Success/Error Feedback */}
              {contextFeedback && (
                <div className={`mt-3 p-3 rounded-lg border ${contextFeedback.type === 'success'
                  ? 'bg-green-50 border-green-200'
                  : 'bg-red-50 border-red-200'
                  }`}>
                  <div className="flex items-center space-x-2">
                    <span className={`text-sm font-medium ${contextFeedback.type === 'success' ? 'text-green-800' : 'text-red-800'
                      }`}>
                      {contextFeedback.type === 'success' ? '✅' : '❌'} {contextFeedback.message}
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4 mt-6 md:mt-8">
              <button
                onClick={handleGenerateLessonResource}
                disabled={isGeneratingLessonResource}
                className="bg-primary-600 w-full text-center text-white font-semibold px-4 md:px-6 py-2 md:py-3 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm md:text-base transition-colors duration-200"
              >
                {isGeneratingLessonResource ? 'Generating...' : 'Generate Lesson Resource'}
              </button>
            </div>
          </div>

          {/* Right panel: Additional Info - Visible on all devices, stacked on mobile */}
          <div className="flex w-full lg:w-64 flex-col gap-4 lg:gap-6 order-last lg:order-none">
            <div className="bg-white rounded-xl shadow-lg p-4 border border-gray-100">
              <div className="font-bold mb-2 text-primary-900">Lesson Info</div>
              <div className="text-sm text-gray-600 space-y-1">
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

      {/* Mobile Bottom Navigation */}
      <MobileNavigation />

      {/* AI Generation Loading Modal */}
      <AIGenerationLoadingActual
        isVisible={isGeneratingLessonResource}
        onComplete={() => setIsGeneratingLessonResource(false)}
        onError={(error) => {
          setContextFeedback({
            type: 'error',
            message: error
          });
          setIsGeneratingLessonResource(false);
        }}
        generationType="lesson-resource"
        topic={lessonPlan?.topic}
        subject={lessonPlan?.subject}
        gradeLevel={lessonPlan?.grade_level}
        currentStep={currentGenerationStep}
        hasContext={!!context.trim()}
      />
    </div>
  );
};

export default LessonPlanDetailPage; 