import React, { useState, useEffect, useRef } from 'react';
import websocketService, { ProgressUpdate, GenerationSession } from '../services/websocket';

interface AIGenerationLoadingRealtimeProps {
  isVisible: boolean;
  onComplete?: (data?: any) => void;
  onError?: (error: string) => void;
  generationType: 'lesson-plan' | 'lesson-resource';
  topic?: string;
  subject?: string;
  gradeLevel?: string;
  sessionId?: string;
}

interface GenerationStep {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'in-progress' | 'completed' | 'error';
  progress?: number;
  message?: string;
}

const AIGenerationLoadingRealtime: React.FC<AIGenerationLoadingRealtimeProps> = ({
  isVisible,
  onComplete,
  onError,
  generationType,
  topic,
  subject,
  gradeLevel,
  sessionId
}) => {
  const [steps, setSteps] = useState<GenerationStep[]>([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [overallProgress, setOverallProgress] = useState(0);
  const [estimatedTimeRemaining, setEstimatedTimeRemaining] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const sessionRef = useRef<string | null>(null);

  // Initialize steps based on generation type
  useEffect(() => {
    if (generationType === 'lesson-plan') {
      setSteps([
        {
          id: 'validate-input',
          title: 'Validating Input',
          description: 'Checking topic, subject, and grade level requirements',
          status: 'pending'
        },
        {
          id: 'find-topic',
          title: 'Finding Topic in Curriculum',
          description: 'Locating topic in the curriculum database',
          status: 'pending'
        },
        {
          id: 'create-lesson-plan',
          title: 'Creating Lesson Plan',
          description: 'Setting up lesson plan structure and metadata',
          status: 'pending'
        },
        {
          id: 'complete',
          title: 'Generation Complete',
          description: 'Lesson plan created successfully',
          status: 'pending'
        }
      ]);
    } else {
      setSteps([
        {
          id: 'validate-lesson-plan',
          title: 'Validating Lesson Plan',
          description: 'Checking lesson plan access and permissions',
          status: 'pending'
        },
        {
          id: 'fetch-curriculum-data',
          title: 'Fetching Curriculum Data',
          description: 'Retrieving learning objectives and content areas',
          status: 'pending'
        },
        {
          id: 'prepare-context',
          title: 'Preparing Context',
          description: 'Combining stored context with additional input',
          status: 'pending'
        },
        {
          id: 'ai-generation',
          title: 'AI Content Generation',
          description: 'Generating comprehensive lesson resources using AI',
          status: 'pending'
        },
        {
          id: 'save-resource',
          title: 'Saving Resource',
          description: 'Storing generated content in database',
          status: 'pending'
        },
        {
          id: 'complete',
          title: 'Generation Complete',
          description: 'Lesson resource ready for editing',
          status: 'pending'
        }
      ]);
    }
  }, [generationType]);

  // WebSocket event handlers
  useEffect(() => {
    if (!isVisible) return;

    // Check connection status
    setIsConnected(websocketService.isConnected());

    // Start generation session
    const session: GenerationSession = {
      sessionId: sessionId || `gen_${Date.now()}`,
      type: generationType,
      topic,
      subject,
      gradeLevel
    };

    sessionRef.current = session.sessionId;
    websocketService.startGeneration(session);

    // Subscribe to WebSocket events
    const unsubscribeProgress = websocketService.on('progress_update', (update: ProgressUpdate) => {
      handleProgressUpdate(update);
    });

    const unsubscribeComplete = websocketService.on('generation_complete', (data: any) => {
      handleGenerationComplete(data);
    });

    const unsubscribeError = websocketService.on('generation_error', (error: any) => {
      handleGenerationError(error);
    });

    const unsubscribeSessionStarted = websocketService.on('session_started', (data: any) => {
      console.log('Generation session started:', data);
    });

    return () => {
      unsubscribeProgress();
      unsubscribeComplete();
      unsubscribeError();
      unsubscribeSessionStarted();
      
      // Cancel generation if still in progress
      if (sessionRef.current) {
        websocketService.cancelGeneration(sessionRef.current);
      }
    };
  }, [isVisible, generationType, topic, subject, gradeLevel, sessionId]);

  const handleProgressUpdate = (update: ProgressUpdate) => {
    setSteps(prev => prev.map(step => {
      if (step.id === update.step) {
        return {
          ...step,
          status: update.status === 'started' ? 'in-progress' : 
                  update.status === 'completed' ? 'completed' :
                  update.status === 'error' ? 'error' : 'in-progress',
          progress: update.progress,
          message: update.message
        };
      }
      return step;
    }));

    setOverallProgress(update.progress);
    
    if (update.estimatedTimeRemaining) {
      setEstimatedTimeRemaining(update.estimatedTimeRemaining);
    }

    // Update current step
    const stepIndex = steps.findIndex(step => step.id === update.step);
    if (stepIndex !== -1) {
      setCurrentStep(stepIndex);
    }
  };

  const handleGenerationComplete = (data: any) => {
    setSteps(prev => prev.map(step => ({
      ...step,
      status: 'completed'
    })));
    setOverallProgress(100);
    setEstimatedTimeRemaining(0);
    
    setTimeout(() => {
      onComplete?.(data);
    }, 1000);
  };

  const handleGenerationError = (error: any) => {
    setError(error.message || 'An error occurred during generation');
    setSteps(prev => prev.map(step => ({
      ...step,
      status: step.status === 'in-progress' ? 'error' : step.status
    })));
    
    setTimeout(() => {
      onError?.(error.message || 'Generation failed');
    }, 1000);
  };

  const formatTime = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const getStepIcon = (step: GenerationStep) => {
    switch (step.status) {
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
          
          {/* Connection Status */}
          <div className="mt-2 flex items-center justify-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-xs text-gray-500">
              {isConnected ? 'Connected' : 'Connecting...'}
            </span>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Progress</span>
            <span>{Math.round(overallProgress)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-orange-500 h-2 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${overallProgress}%` }}
            ></div>
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>
              {estimatedTimeRemaining > 0 ? `Est. time remaining: ${formatTime(estimatedTimeRemaining)}` : 'Almost done...'}
            </span>
            <span>Step {currentStep + 1} of {steps.length}</span>
          </div>
        </div>

        {/* Steps */}
        <div className="space-y-3">
          {steps.map((step) => (
            <div key={step.id} className="flex items-start space-x-3">
              {getStepIcon(step)}
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
                  {step.message || step.description}
                </p>
                {step.status === 'in-progress' && step.progress !== undefined && (
                  <div className="mt-2">
                    <div className="w-full bg-gray-200 rounded-full h-1">
                      <div 
                        className="bg-orange-500 h-1 rounded-full transition-all duration-300"
                        style={{ width: `${step.progress}%` }}
                      ></div>
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
            This process is powered by AI and provides real-time updates.
            <br />
            Please don't close this window while generation is in progress.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AIGenerationLoadingRealtime;
