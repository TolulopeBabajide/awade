import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import apiService from '../services/api';

interface LessonResource {
  lesson_resources_id: number;
  lesson_plan_id: number;
  user_id: number;
  context_input?: string;
  ai_generated_content?: string;
  user_edited_content?: string;
  export_format?: string;
  status: string;
  created_at: string;
}

// Interface for structured AI content
interface StructuredLessonContent {
  title_header?: {
    topic?: string;
    subject?: string;
    grade_level?: string;
    country?: string;
    local_context?: string;
  };
  learning_objectives?: string[];
  lesson_content?: {
    introduction?: string;
    main_concepts?: string[];
    examples?: string[];
    step_by_step_instructions?: string[];
  };
  assessment?: string[];
  key_takeaways?: string[];
  related_projects_or_activities?: string[];
  references?: string[];
  explanations?: {
    learning_objectives?: string;
    lesson_content?: string;
    assessment?: string;
    key_takeaways?: string;
    related_projects_or_activities?: string;
    references?: string;
  };
}

// Tooltip component
interface TooltipProps {
  content: string;
  children: React.ReactNode;
}

// Helper function to get fallback explanations
const getFallbackExplanation = (title: string): string => {
  const explanations: { [key: string]: string } = {
    'Lesson Content': 'This section contains the main instructional content including introduction, main concepts, examples, and step-by-step instructions. The content is designed to be engaging and age-appropriate for your students.',
    'Assessment': 'This section provides various assessment strategies to measure student understanding and progress. These assessments are designed to be practical and aligned with learning objectives.',
    'Key Takeaways': 'These are the essential points that students should remember from this lesson. They summarize the most important concepts and skills covered.',
    'Related Projects & Activities': 'These activities provide hands-on learning opportunities and practical applications of the lesson concepts. They help reinforce learning through active engagement.',
    'References': 'This section lists relevant resources, materials, and references that support the lesson content and provide additional context for teachers and students.'
  };
  
  return explanations[title] || `This section contains AI-generated content for ${title} that can be customized for your classroom needs.`;
};

const Tooltip: React.FC<TooltipProps> = ({ content, children }) => {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div className="relative inline-block">
      <div
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
        className="cursor-help"
      >
        {children}
      </div>
      {isVisible && (
        <div className="absolute z-50 w-80 p-3 bg-gray-900 text-white text-sm rounded-lg shadow-lg -top-2 left-full ml-2 border border-gray-700">
          <div className="relative">
            <div className="absolute -left-2 top-3 w-0 h-0 border-t-4 border-b-4 border-r-4 border-transparent border-r-gray-900"></div>
            <p className="whitespace-pre-wrap leading-relaxed">{content}</p>
          </div>
        </div>
      )}
    </div>
  );
};

// Editable section component
interface EditableSectionProps {
  title: string;
  content: any;
  onSave: (updatedContent: any) => void;
  isEditing: boolean;
  onEdit: () => void;
  onCancel: () => void;
  bgColor: string;
  textColor: string;
  borderColor: string;
  explanation?: string;
}

const EditableSection: React.FC<EditableSectionProps> = ({
  title,
  content,
  onSave,
  isEditing,
  onEdit,
  onCancel,
  bgColor,
  textColor,
  borderColor,
  explanation
}) => {
  const [editContent, setEditContent] = useState<any>(content);

  useEffect(() => {
    setEditContent(content);
  }, [content]);

  const handleSave = () => {
    onSave(editContent);
  };

  const renderContent = () => {
    if (Array.isArray(content)) {
      return (
        <ul className="list-disc list-inside space-y-1 text-sm">
          {content.map((item, index) => (
            <li key={index} className={textColor}>{item}</li>
          ))}
        </ul>
      );
    } else if (typeof content === 'object' && content !== null) {
      return (
        <div className="space-y-2">
          {Object.entries(content).map(([key, value]) => (
            <div key={key}>
              <span className="font-medium capitalize">{key.replace(/_/g, ' ')}:</span>
              {Array.isArray(value) ? (
                <ul className="list-disc list-inside ml-4 mt-1">
                  {value.map((item: string, index: number) => (
                    <li key={index} className="text-sm">{item}</li>
                  ))}
                </ul>
              ) : (
                <span className="ml-2 text-sm">{value as string}</span>
              )}
            </div>
          ))}
        </div>
      );
    } else {
      return <p className="text-sm">{content}</p>;
    }
  };

  const renderEditForm = () => {
    if (Array.isArray(content)) {
      return (
        <div className="space-y-3">
          {editContent.map((item: string, index: number) => (
            <div key={index} className="flex flex-col sm:flex-row gap-2">
              <input
                type="text"
                value={item}
                onChange={(e) => {
                  const newContent = [...editContent];
                  newContent[index] = e.target.value;
                  setEditContent(newContent);
                }}
                className="flex-1 p-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200"
              />
              <button
                onClick={() => {
                  const newContent = editContent.filter((_: string, i: number) => i !== index);
                  setEditContent(newContent);
                }}
                className="w-full sm:w-auto px-3 py-2 text-red-600 hover:text-red-800 text-sm border border-red-200 rounded-lg hover:bg-red-50 transition-colors duration-200"
              >
                Remove
              </button>
            </div>
          ))}
          <button
            onClick={() => setEditContent([...editContent, ''])}
            className="w-full sm:w-auto text-sm text-primary-600 hover:text-primary-800 px-3 py-2 border border-primary-200 rounded-lg hover:bg-primary-50 transition-colors duration-200"
          >
            + Add Item
          </button>
        </div>
      );
    } else if (typeof content === 'object' && content !== null) {
      return (
        <div className="space-y-4">
          {Object.entries(content).map(([key, value]) => (
            <div key={key}>
              <label className="block text-sm font-medium mb-2 capitalize text-gray-700">
                {key.replace(/_/g, ' ')}
              </label>
              {Array.isArray(value) ? (
                <div className="space-y-3">
                  {editContent[key].map((item: string, index: number) => (
                    <div key={index} className="flex flex-col sm:flex-row gap-2">
                      <input
                        type="text"
                        value={item}
                        onChange={(e) => {
                          const newContent = { ...editContent };
                          newContent[key] = [...newContent[key]];
                          newContent[key][index] = e.target.value;
                          setEditContent(newContent);
                        }}
                        className="flex-1 p-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200"
                      />
                      <button
                        onClick={() => {
                          const newContent = { ...editContent };
                          newContent[key] = newContent[key].filter((_: string, i: number) => i !== index);
                          setEditContent(newContent);
                        }}
                        className="w-full sm:w-auto px-3 py-2 text-red-600 hover:text-red-800 text-sm border border-red-200 rounded-lg hover:bg-red-50 transition-colors duration-200"
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                  <button
                    onClick={() => {
                      const newContent = { ...editContent };
                      newContent[key] = [...newContent[key], ''];
                      setEditContent(newContent);
                    }}
                    className="w-full sm:w-auto text-sm text-primary-600 hover:text-primary-800 px-3 py-2 border border-primary-200 rounded-lg hover:bg-primary-50 transition-colors duration-200"
                  >
                    + Add {key.replace(/_/g, ' ')}
                  </button>
                </div>
              ) : (
                <textarea
                  value={editContent[key]}
                  onChange={(e) => {
                    const newContent = { ...editContent };
                    newContent[key] = e.target.value;
                    setEditContent(newContent);
                  }}
                  className="w-full p-3 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 resize-none"
                  rows={3}
                />
              )}
            </div>
          ))}
        </div>
      );
    } else {
      return (
        <textarea
          value={editContent}
          onChange={(e) => setEditContent(e.target.value)}
          className="w-full p-3 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 resize-none"
          rows={4}
        />
      );
    }
  };

  return (
    <div className={`${bgColor} rounded-lg p-3 md:p-4 border ${borderColor}`}>
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-3 gap-2">
        <div className="flex items-center gap-2">
          <h3 className={`font-semibold ${textColor} text-base md:text-lg`}>{title}</h3>
          {explanation ? (
            <Tooltip content={explanation}>
              <svg className="w-4 h-4 text-gray-500 hover:text-gray-700" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
              </svg>
            </Tooltip>
          ) : (
            <Tooltip content={getFallbackExplanation(title)}>
              <svg className="w-4 h-4 text-gray-400 hover:text-gray-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
              </svg>
            </Tooltip>
          )}
        </div>
        {!isEditing ? (
          <button
            onClick={onEdit}
            className="w-full sm:w-auto text-sm text-primary-600 hover:text-primary-800 font-medium px-3 py-1 border border-primary-200 rounded-lg hover:bg-primary-50 transition-colors duration-200"
          >
            Edit
          </button>
        ) : (
          <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
            <button
              onClick={handleSave}
              className="w-full sm:w-auto text-sm text-green-600 hover:text-green-800 font-medium px-3 py-1 border border-green-200 rounded-lg hover:bg-green-50 transition-colors duration-200"
            >
              Save
            </button>
            <button
              onClick={onCancel}
              className="w-full sm:w-auto text-sm text-gray-600 hover:text-gray-800 font-medium px-3 py-1 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors duration-200"
            >
              Cancel
            </button>
          </div>
        )}
      </div>
      
      {isEditing ? renderEditForm() : renderContent()}
    </div>
  );
};

const EditLessonResourcePage: React.FC = () => {
  const { lessonPlanId } = useParams<{ lessonPlanId: string }>();
  const navigate = useNavigate();
  
  const [lessonResource, setLessonResource] = useState<LessonResource | null>(null);
  const [lessonPlan, setLessonPlan] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string>('');
  const [successMessage, setSuccessMessage] = useState<string>('');
  
  // Structured content state
  const [structuredContent, setStructuredContent] = useState<StructuredLessonContent | null>(null);
  const [editingSection, setEditingSection] = useState<string | null>(null);
  
  // Export format
  const [exportFormat, setExportFormat] = useState<'pdf' | 'docx'>('pdf');
  
  useEffect(() => {
    if (lessonPlanId) {
      loadLessonPlanAndResource();
    }
  }, [lessonPlanId]);

  const loadLessonPlanAndResource = async () => {
    try {
      // First, fetch the lesson plan to get the subject
      const lessonPlanResponse = await apiService.getLessonPlan(lessonPlanId!);
      if (lessonPlanResponse.data) {
        setLessonPlan(lessonPlanResponse.data);
      }

      // Then fetch the lesson resource
      const response = await apiService.getLessonResources(lessonPlanId!);
      
      if (response.error) {
        setError(response.error);
        return;
      }

      if (response.data && response.data.length > 0) {
        const resource = response.data[0];
        setLessonResource(resource);
        
        // Parse structured content - prioritize user_edited_content over ai_generated_content
        let contentToParse = resource.user_edited_content || resource.ai_generated_content;
        if (contentToParse) {
          try {
            const parsed = JSON.parse(contentToParse);
            console.log('Parsed structured content:', parsed);
            console.log('Explanations available:', parsed.explanations);
            console.log('Explanations structure:', {
              learning_objectives: parsed.explanations?.learning_objectives,
              lesson_content: parsed.explanations?.lesson_content,
              assessment: parsed.explanations?.assessment,
              key_takeaways: parsed.explanations?.key_takeaways,
              related_projects_or_activities: parsed.explanations?.related_projects_or_activities
            });
            setStructuredContent(parsed);
          } catch (error) {
            setError('Failed to parse lesson resource content');
          }
        }
      } else {
        await generateLessonResource();
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load lesson plan or resource');
    } finally {
      setIsLoading(false);
    }
  };

  const generateLessonResource = async () => {
    try {
      setError('');
      const response = await apiService.generateLessonResource(lessonPlanId!, '');
      
      if (response.error) {
        setError(response.error);
        return;
      }

      if (response.data) {
        setLessonResource(response.data);
        
        // Parse structured content - prioritize user_edited_content over ai_generated_content
        let contentToParse = response.data.user_edited_content || response.data.ai_generated_content;
        if (contentToParse) {
          try {
            const parsed = JSON.parse(contentToParse);
            console.log('Generated structured content:', parsed);
            console.log('Explanations available:', parsed.explanations);
            console.log('Explanations structure:', {
              learning_objectives: parsed.explanations?.learning_objectives,
              lesson_content: parsed.explanations?.lesson_content,
              assessment: parsed.explanations?.assessment,
              key_takeaways: parsed.explanations?.key_takeaways,
              related_projects_or_activities: parsed.explanations?.related_projects_or_activities
            });
            setStructuredContent(parsed);
          } catch (error) {
            setError('Failed to parse lesson resource content');
          }
        }
      } else {
        setError('No data received from lesson resource generation');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to generate lesson resource');
    }
  };

  const handleSectionSave = (sectionKey: string, updatedContent: any) => {
    if (!structuredContent) return;

    const updatedStructuredContent = {
      ...structuredContent,
      [sectionKey]: updatedContent
    };

    setStructuredContent(updatedStructuredContent);
    setEditingSection(null);
  };

  const saveAllChanges = async () => {
    if (!lessonResource || !structuredContent) {
      setError('No lesson resource available to save');
      return;
    }

    setIsSaving(true);
    setError('');

    try {
      // Convert structured content back to JSON string for storage
      const updatedContent = JSON.stringify(structuredContent, null, 2);
      
      console.log('Saving updated content:', updatedContent);
      
      const response = await apiService.updateLessonResource(
        lessonResource.lesson_resources_id.toString(),
        updatedContent
      );

      if (response.error) {
        setError(response.error);
        return;
      }

      if (response.data) {
        // Update the lesson resource with the response data
        setLessonResource(response.data);
        
        // Update the AI generated content in the resource to reflect our changes
        const updatedResource = {
          ...response.data,
          ai_generated_content: updatedContent
        };
        setLessonResource(updatedResource);
        
        setSuccessMessage('Lesson resource saved successfully! All changes have been persisted to the database.');
        setTimeout(() => setSuccessMessage(''), 5000);
        
        console.log('Successfully saved lesson resource:', response.data);
      } else {
        setError('No data received from save request');
      }
    } catch (err: any) {
      console.error('Error saving lesson resource:', err);
      setError(err.message || 'Failed to save lesson resource');
    } finally {
      setIsSaving(false);
    }
  };

  const exportLessonResource = async (format: 'pdf' | 'docx') => {
    if (!lessonResource) {
      setError('No lesson resource available for export');
      return;
    }

    try {
      setError('');
      const response = await apiService.exportLessonResource(
        lessonResource.lesson_resources_id.toString(),
        format
      );

      if (response.error) {
        setError(response.error);
        return;
      }

      if (response.data) {
        const url = window.URL.createObjectURL(response.data);
        const a = document.createElement('a');
        a.href = url;
        a.download = `lesson-resource.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        setSuccessMessage(`Lesson resource exported successfully as ${format.toUpperCase()}!`);
        setTimeout(() => setSuccessMessage(''), 3000);
      } else {
        setError('No data received from export request');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to export lesson resource');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading lesson resource...</p>
        </div>
      </div>
    );
  }

  if (!structuredContent) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">No structured content available</p>
          <button
            onClick={generateLessonResource}
            className="mt-4 px-4 py-2 bg-orange-500 text-white rounded-md hover:bg-orange-600"
          >
            Generate Lesson Resource
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Header */}
      {/* <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center py-4 gap-4">
            <div>
              <h1 className="text-xl md:text-2xl font-bold text-primary-900">Edit Lesson Resource</h1>
              <p className="text-sm md:text-base text-gray-600">Edit each section directly to customize for your classroom</p>
            </div>
            <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3 w-full sm:w-auto">
              <button
                onClick={() => navigate('/dashboard')}
                className="w-full sm:w-auto px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 text-sm transition-colors duration-200"
              >
                Back to Dashboard
              </button>
              <button
                onClick={saveAllChanges}
                disabled={isSaving}
                className="w-full sm:w-auto px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 text-sm transition-colors duration-200"
              >
                {isSaving ? 'Saving...' : 'Save All Changes'}
              </button>
            </div>
          </div>
        </div>
      </div> */}

        

      <div className=" flex-1 p-4 md:p-6 lg:p-8">


        {/* Back Navigation */}
        <div className="mb-4 md:mb-6">
          <button 
            onClick={() => navigate('/dashboard')}
            className="text-primary-600 text-sm mb-2 flex items-center hover:text-primary-700 transition-colors duration-200"
          >
            &larr; Back to Dashboard
          </button>
        </div>


        {/* Breadcrumb Navigation */}
        <div className="flex items-center text-sm text-gray-500 mb-3 md:mb-4 gap-2">
          <span className="font-bold text-primary-700">Dashboard</span>
          <span>&gt;</span>
          <span className="font-bold text-primary-700">Lesson Plans</span>
          <span>&gt;</span>
          <span className="font-bold text-primary-700">{lessonPlan?.subject || 'Subject'}</span>
          <span>&gt;</span>
          <span className="font-bold text-primary-600">Generate Lesson Note</span>
        </div>

        {error && (
          <div className="mb-4 md:mb-6 bg-red-50 border border-red-200 rounded-lg p-3 md:p-4">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}
        {successMessage && (
          <div className="mb-4 md:mb-6 bg-green-50 border border-green-200 rounded-lg p-3 md:p-4">
            <p className="text-green-800 text-sm">{successMessage}</p>
          </div>
        )}

        <div className="flex flex-col lg:flex-row gap-4 lg:gap-6">
          {/* Main Content */}
          <div className="flex-1 bg-white rounded-xl shadow-lg p-4 md:p-6 lg:p-8 space-y-4 md:space-y-6">
            {/* AI Disclaimer */}
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 md:p-4">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-amber-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-amber-800">AI-Generated Content Disclaimer</h3>
                  <div className="mt-2 text-sm text-amber-700">
                    <p>This lesson resource has been generated by AI and may contain inaccuracies. As an educator, you should:</p>
                    <ul className="list-disc list-inside mt-2 space-y-1">
                      <li>Review content for accuracy and appropriateness</li>
                      <li>Customize to align with your curriculum standards</li>
                      <li>Adapt to your students' specific needs</li>
                      <li>Verify cultural relevance and local context</li>
                    </ul>
                    <p className="mt-2">Click "Edit" on any section to customize for your classroom.</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Read-only Sections */}
            {structuredContent.title_header && (
              <div className="bg-primary-50 rounded-lg p-3 md:p-4 border border-primary-100">
                <div className="mb-3">
                  <div className="flex items-center gap-2">
                    <h3 className="font-bold mb-2 md:mb-3 text-base md:text-lg text-primary-900">Lesson Overview</h3>
                    <Tooltip content="This section contains the basic information about the lesson including topic, subject, grade level, and local context. This information is automatically generated based on your lesson plan and cannot be edited.">
                      <svg className="w-4 h-4 text-primary-500 hover:text-primary-700" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                      </svg>
                    </Tooltip>
                  </div>
                </div>
                <div className="space-y-2">
                  {Object.entries(structuredContent.title_header).map(([key, value]) => (
                    <div key={key}>
                      <span className="font-semibold text-primary-700 text-sm">{key.replace(/_/g, ' ')}:</span>
                      <span className="ml-2 text-sm text-primary-800">{value as string}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {structuredContent.learning_objectives && (
              <div className="bg-primary-50 rounded-lg p-3 md:p-4 border border-primary-100">
                <div className="mb-3">
                  <div className="flex items-center gap-2">
                    <h3 className="font-bold mb-2 md:mb-3 text-base md:text-lg text-primary-900">Learning Objectives</h3>
                    <Tooltip content={structuredContent.explanations?.learning_objectives || "Learning objectives define what students should know, understand, and be able to do by the end of the lesson. These are aligned with curriculum standards and grade-level expectations."}>
                      <svg className="w-4 h-4 text-primary-500 hover:text-primary-700" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                      </svg>
                    </Tooltip>
                  </div>
                </div>
                <ul className="list-disc ml-4 md:ml-6 text-primary-800 space-y-1">
                  {structuredContent.learning_objectives.map((objective, index) => (
                    <li key={index} className="text-sm">{objective}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Editable Sections */}
            {structuredContent.lesson_content && (
              <EditableSection
                title="Lesson Content"
                content={structuredContent.lesson_content}
                onSave={(updatedContent) => handleSectionSave('lesson_content', updatedContent)}
                isEditing={editingSection === 'lesson_content'}
                onEdit={() => setEditingSection('lesson_content')}
                onCancel={() => setEditingSection(null)}
                bgColor="bg-accent-50"
                textColor="text-accent-900"
                borderColor="border-accent-100"
                explanation={structuredContent.explanations?.lesson_content}
              />
            )}

            {structuredContent.assessment && (
              <EditableSection
                title="Assessment"
                content={structuredContent.assessment}
                onSave={(updatedContent) => handleSectionSave('assessment', updatedContent)}
                isEditing={editingSection === 'assessment'}
                onEdit={() => setEditingSection('assessment')}
                onCancel={() => setEditingSection(null)}
                bgColor="bg-orange-50"
                textColor="text-orange-900"
                borderColor="border-orange-100"
                explanation={structuredContent.explanations?.assessment}
              />
            )}

            {structuredContent.key_takeaways && (
              <EditableSection
                title="Key Takeaways"
                content={structuredContent.key_takeaways}
                onSave={(updatedContent) => handleSectionSave('key_takeaways', updatedContent)}
                isEditing={editingSection === 'key_takeaways'}
                onEdit={() => setEditingSection('key_takeaways')}
                onCancel={() => setEditingSection(null)}
                bgColor="bg-indigo-50"
                textColor="text-indigo-900"
                borderColor="border-indigo-100"
                explanation={structuredContent.explanations?.key_takeaways}
              />
            )}

            {structuredContent.related_projects_or_activities && (
              <EditableSection
                title="Related Projects & Activities"
                content={structuredContent.related_projects_or_activities}
                onSave={(updatedContent) => handleSectionSave('related_projects_or_activities', updatedContent)}
                isEditing={editingSection === 'related_projects_or_activities'}
                onEdit={() => setEditingSection('related_projects_or_activities')}
                onCancel={() => setEditingSection(null)}
                bgColor="bg-teal-50"
                textColor="text-teal-900"
                borderColor="border-teal-100"
                explanation={structuredContent.explanations?.related_projects_or_activities}
              />
            )}

            {structuredContent.references && (
              <EditableSection
                title="References"
                content={structuredContent.references}
                onSave={(updatedContent) => handleSectionSave('references', updatedContent)}
                isEditing={editingSection === 'references'}
                onEdit={() => setEditingSection('references')}
                onCancel={() => setEditingSection(null)}
                bgColor="bg-gray-50"
                textColor="text-gray-900"
                borderColor="border-gray-100"
                explanation={structuredContent.explanations?.references}
              />
            )}
          </div>

          {/* Sidebar - Hidden on mobile, shown on desktop */}
          <div className="hidden lg:flex w-64 flex-col gap-4 lg:gap-6">
            {/* Export Options */}
            <div className="bg-white rounded-xl shadow-lg p-4 border border-gray-100">
              <div className="font-bold mb-2 text-primary-900">Export Options</div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Export Format
                </label>
                <select
                  value={exportFormat}
                  onChange={(e) => setExportFormat(e.target.value as 'pdf' | 'docx')}
                  className="w-full p-2 md:p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm transition-all duration-200"
                >
                  <option value="pdf">PDF Document</option>
                  <option value="docx">Word Document (DOCX)</option>
                </select>
              </div>

              <button
                onClick={() => exportLessonResource(exportFormat)}
                className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm transition-colors duration-200"
              >
                Export Lesson Resource
              </button>
            </div>

            {/* Status */}
            <div className="bg-white rounded-xl shadow-lg p-4 border border-gray-100">
              <div className="font-bold mb-2 text-primary-900">Resource Status</div>
              <div className="text-sm text-gray-600 space-y-1">
                <div><span className="font-semibold text-primary-700">Status:</span> <span className="text-gray-700">{lessonResource?.status || 'Draft'}</span></div>
                <div><span className="font-bold text-primary-700">Created:</span> <span className="text-gray-700">{lessonResource?.created_at ? new Date(lessonResource.created_at).toLocaleDateString() : 'N/A'}</span></div>
                <div><span className="font-semibold text-primary-700">Resource ID:</span> <span className="text-gray-700">{lessonResource?.lesson_resources_id || 'N/A'}</span></div>
              </div>
            </div>
          </div>
        </div>

        {/* Mobile Export Section - Shown only on mobile */}
        <div className="lg:hidden mt-6 space-y-4">
          {/* Export Options */}
          <div className="bg-white rounded-xl shadow-lg p-4 border border-gray-100">
            <div className="font-bold mb-2 text-primary-900">Export Options</div>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Export Format
              </label>
              <select
                value={exportFormat}
                onChange={(e) => setExportFormat(e.target.value as 'pdf' | 'docx')}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
              >
                <option value="pdf">PDF Document</option>
                <option value="docx">Word Document (DOCX)</option>
              </select>
            </div>

            <button
              onClick={() => exportLessonResource(exportFormat)}
              className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
            >
              Export Lesson Resource
            </button>
          </div>

          {/* Status */}
          <div className="bg-white rounded-xl shadow-lg p-4 border border-gray-100">
            <div className="font-bold mb-2 text-primary-900">Resource Status</div>
            <div className="text-sm text-gray-600 space-y-1">
              <div><span className="font-semibold text-primary-700">Status:</span> <span className="text-gray-700">{lessonResource?.status || 'Draft'}</span></div>
              <div><span className="font-semibold text-primary-700">Created:</span> <span className="text-gray-700">{lessonResource?.created_at ? new Date(lessonResource.created_at).toLocaleDateString() : 'N/A'}</span></div>
              <div><span className="font-semibold text-primary-700">Resource ID:</span> <span className="text-gray-700">{lessonResource?.lesson_resources_id || 'N/A'}</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EditLessonResourcePage; 