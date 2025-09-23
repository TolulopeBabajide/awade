import React, { useState, useEffect } from 'react';

interface AIGenerationLoadingActualProps {
  isVisible: boolean;
  onComplete?: () => void;
  onError?: (error: string) => void;
  generationType: 'lesson-plan' | 'lesson-resource';
  topic?: string;
  subject?: string;
  gradeLevel?: string;
  currentStep?: string;
  hasContext?: boolean;
}

interface GenerationStep {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'in-progress' | 'completed' | 'error';
}

const AIGenerationLoadingActual: React.FC<AIGenerationLoadingActualProps> = ({
  isVisible,
  onComplete,
  onError,
  generationType,
  topic,
  subject,
  gradeLevel,
  currentStep,
  hasContext = false
}) => {
  const [steps, setSteps] = useState<GenerationStep[]>([]);
  const [progress, setProgress] = useState(0);

  // Initialize steps based on generation type and context
  useEffect(() => {
    if (generationType === 'lesson-resource') {
      const baseSteps = [
        {
          id: 'validate-lesson-plan',
          title: 'Validating Lesson Plan',
          description: 'Checking lesson plan access and permissions',
          status: 'pending' as const
        }
      ];

      // Add context step only if context is provided
      if (hasContext) {
        baseSteps.push({
          id: 'submit-context',
          title: 'Submitting Context',
          description: 'Saving additional context to database',
          status: 'pending' as const
        });
      }

      baseSteps.push(
        {
          id: 'fetch-curriculum-data',
          title: 'Fetching Curriculum Data',
          description: 'Retrieving learning objectives and content areas',
          status: 'pending' as const
        },
        {
          id: 'ai-generation',
          title: 'AI Content Generation',
          description: 'Generating comprehensive lesson resources using AI',
          status: 'pending' as const
        },
        {
          id: 'save-resource',
          title: 'Saving Resource',
          description: 'Storing generated content in database',
          status: 'pending' as const
        },
        {
          id: 'complete',
          title: 'Generation Complete',
          description: 'Lesson resource ready for editing',
          status: 'pending' as const
        }
      );

      setSteps(baseSteps);
    }
  }, [generationType, hasContext]);

  // Update step status based on currentStep prop
  useEffect(() => {
    if (!isVisible || !currentStep) return;

    setSteps(prev => prev.map(step => {
      if (step.id === currentStep) {
        return { ...step, status: 'in-progress' };
      } else if (prev.findIndex(s => s.id === step.id) < prev.findIndex(s => s.id === currentStep)) {
        return { ...step, status: 'completed' };
      }
      return step;
    }));

    // Calculate progress
    const currentStepIndex = steps.findIndex(step => step.id === currentStep);
    const totalSteps = steps.length;
    const progressPercentage = ((currentStepIndex + 1) / totalSteps) * 100;
    setProgress(progressPercentage);
  }, [currentStep, isVisible, steps.length]);

  // Handle completion
  useEffect(() => {
    if (isVisible && currentStep === 'complete') {
      setSteps(prev => prev.map(step => ({ ...step, status: 'completed' })));
      setProgress(100);
      setTimeout(() => {
        onComplete?.();
      }, 1000);
    }
  }, [currentStep, isVisible, onComplete]);

  const getStepIcon = (status: GenerationStep['status']) => {
    switch (status) {
      case 'completed':
        return (
          <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        );
      case 'in-progress':
        return (
          <div className="w-6 h-6 bg-orange-500 rounded-full flex items-center justify-center">
            <div className="w-3 h-3 bg-white rounded-full animate-pulse"></div>
          </div>
        );
      case 'error':
        return (
          <div className="w-6 h-6 bg-red-500 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
        );
      default:
        return (
          <div className="w-6 h-6 bg-gray-300 rounded-full flex items-center justify-center">
            <div className="w-2 h-2 bg-gray-500 rounded-full"></div>
          </div>
        );
    }
  };

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            AI {generationType === 'lesson-plan' ? 'Lesson Plan' : 'Lesson Resource'} Generation
          </h3>
          <p className="text-gray-600 text-sm">
            {topic && subject && gradeLevel && (
              <>
                Generating for <span className="font-medium">{topic}</span> in <span className="font-medium">{subject}</span> ({gradeLevel})
              </>
            )}
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Progress</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-orange-500 h-2 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Step {steps.filter(s => s.status === 'completed' || s.status === 'in-progress').length} of {steps.length}</span>
            <span>AI Generation in Progress</span>
          </div>
        </div>

        {/* Steps */}
        <div className="space-y-3">
          {steps.map((step) => (
            <div key={step.id} className="flex items-start space-x-3">
              {getStepIcon(step.status)}
              <div className="flex-1 min-w-0">
                <p className={`text-sm font-medium ${
                  step.status === 'completed' ? 'text-green-700' :
                  step.status === 'in-progress' ? 'text-orange-700' :
                  step.status === 'error' ? 'text-red-700' :
                  'text-gray-500'
                }`}>
                  {step.title}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {step.description}
                </p>
                {step.status === 'in-progress' && (
                  <div className="mt-2">
                    <div className="w-full bg-gray-200 rounded-full h-1">
                      <div className="bg-orange-500 h-1 rounded-full animate-pulse" style={{ width: '60%' }}></div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="mt-6 pt-4 border-t border-gray-200">
          <p className="text-xs text-gray-500 text-center">
            This process is powered by AI and may take a few moments to complete.
            <br />
            Please don't close this window while generation is in progress.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AIGenerationLoadingActual;

