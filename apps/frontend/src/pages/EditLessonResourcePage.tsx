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
}

// Component to render structured content
const StructuredContentRenderer: React.FC<{ content: string }> = ({ content }) => {
  const [parsedContent, setParsedContent] = useState<StructuredLessonContent | null>(null);
  const [parseError, setParseError] = useState<string>('');

  useEffect(() => {
    if (!content) return;

    try {
      const parsed = JSON.parse(content);
      setParsedContent(parsed);
      setParseError('');
    } catch (error) {
      setParseError('Failed to parse structured content');
      setParsedContent(null);
    }
  }, [content]);

  if (parseError) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
        <p className="text-yellow-800 text-sm">{parseError}</p>
        <pre className="mt-2 text-xs bg-gray-100 p-2 rounded overflow-auto max-h-64">
          {content}
        </pre>
      </div>
    );
  }

  if (!parsedContent) {
    return (
      <div className="bg-gray-50 rounded-md p-4">
        <p className="text-sm text-gray-600">No structured content available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Title Header */}
      {parsedContent.title_header && (
        <div className="bg-blue-50 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-3">Lesson Overview</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            {parsedContent.title_header.topic && (
              <div>
                <span className="font-medium">Topic:</span> {parsedContent.title_header.topic}
              </div>
            )}
            {parsedContent.title_header.subject && (
              <div>
                <span className="font-medium">Subject:</span> {parsedContent.title_header.subject}
              </div>
            )}
            {parsedContent.title_header.grade_level && (
              <div>
                <span className="font-medium">Grade Level:</span> {parsedContent.title_header.grade_level}
              </div>
            )}
            {parsedContent.title_header.country && (
              <div>
                <span className="font-medium">Country:</span> {parsedContent.title_header.country}
              </div>
            )}
          </div>
          {parsedContent.title_header.local_context && (
            <div className="mt-3">
              <span className="font-medium">Local Context:</span>
              <p className="text-sm mt-1">{parsedContent.title_header.local_context}</p>
            </div>
          )}
        </div>
      )}

      {/* Learning Objectives */}
      {parsedContent.learning_objectives && parsedContent.learning_objectives.length > 0 && (
        <div className="bg-green-50 rounded-lg p-4">
          <h3 className="font-semibold text-green-900 mb-3">Learning Objectives</h3>
          <ul className="list-disc list-inside space-y-1 text-sm">
            {parsedContent.learning_objectives.map((objective, index) => (
              <li key={index} className="text-green-800">{objective}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Lesson Content */}
      {parsedContent.lesson_content && (
        <div className="bg-purple-50 rounded-lg p-4">
          <h3 className="font-semibold text-purple-900 mb-3">Lesson Content</h3>
          
          {parsedContent.lesson_content.introduction && (
            <div className="mb-4">
              <h4 className="font-medium text-purple-800 mb-2">Introduction</h4>
              <p className="text-sm text-purple-700">{parsedContent.lesson_content.introduction}</p>
            </div>
          )}

          {parsedContent.lesson_content.main_concepts && parsedContent.lesson_content.main_concepts.length > 0 && (
            <div className="mb-4">
              <h4 className="font-medium text-purple-800 mb-2">Main Concepts</h4>
              <ul className="list-disc list-inside space-y-1 text-sm">
                {parsedContent.lesson_content.main_concepts.map((concept, index) => (
                  <li key={index} className="text-purple-700">{concept}</li>
                ))}
              </ul>
            </div>
          )}

          {parsedContent.lesson_content.examples && parsedContent.lesson_content.examples.length > 0 && (
            <div className="mb-4">
              <h4 className="font-medium text-purple-800 mb-2">Examples</h4>
              <ul className="list-disc list-inside space-y-1 text-sm">
                {parsedContent.lesson_content.examples.map((example, index) => (
                  <li key={index} className="text-purple-700">{example}</li>
                ))}
              </ul>
            </div>
          )}

          {parsedContent.lesson_content.step_by_step_instructions && parsedContent.lesson_content.step_by_step_instructions.length > 0 && (
            <div>
              <h4 className="font-medium text-purple-800 mb-2">Step-by-Step Instructions</h4>
              <ol className="list-decimal list-inside space-y-1 text-sm">
                {parsedContent.lesson_content.step_by_step_instructions.map((step, index) => (
                  <li key={index} className="text-purple-700">{step}</li>
                ))}
              </ol>
            </div>
          )}
        </div>
      )}

      {/* Assessment */}
      {parsedContent.assessment && parsedContent.assessment.length > 0 && (
        <div className="bg-orange-50 rounded-lg p-4">
          <h3 className="font-semibold text-orange-900 mb-3">Assessment</h3>
          <ul className="list-disc list-inside space-y-1 text-sm">
            {parsedContent.assessment.map((item, index) => (
              <li key={index} className="text-orange-800">{item}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Key Takeaways */}
      {parsedContent.key_takeaways && parsedContent.key_takeaways.length > 0 && (
        <div className="bg-indigo-50 rounded-lg p-4">
          <h3 className="font-semibold text-indigo-900 mb-3">Key Takeaways</h3>
          <ul className="list-disc list-inside space-y-1 text-sm">
            {parsedContent.key_takeaways.map((takeaway, index) => (
              <li key={index} className="text-indigo-800">{takeaway}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Related Projects/Activities */}
      {parsedContent.related_projects_or_activities && parsedContent.related_projects_or_activities.length > 0 && (
        <div className="bg-teal-50 rounded-lg p-4">
          <h3 className="font-semibold text-teal-900 mb-3">Related Projects & Activities</h3>
          <ul className="list-disc list-inside space-y-1 text-sm">
            {parsedContent.related_projects_or_activities.map((activity, index) => (
              <li key={index} className="text-teal-800">{activity}</li>
            ))}
          </ul>
        </div>
      )}

      {/* References */}
      {parsedContent.references && parsedContent.references.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-3">References</h3>
          <ul className="list-disc list-inside space-y-1 text-sm">
            {parsedContent.references.map((reference, index) => (
              <li key={index} className="text-gray-700">{reference}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

const EditLessonResourcePage: React.FC = () => {
  const { lessonPlanId } = useParams<{ lessonPlanId: string }>();
  const navigate = useNavigate();
  
  const [lessonResource, setLessonResource] = useState<LessonResource | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string>('');
  const [successMessage, setSuccessMessage] = useState<string>('');
  
  // Form states
  const [aiContent, setAiContent] = useState('');
  const [userEditedContent, setUserEditedContent] = useState('');
  const [exportFormat, setExportFormat] = useState<'pdf' | 'docx'>('pdf');
  
  useEffect(() => {
    if (lessonPlanId) {
      loadLessonResource();
    }
  }, [lessonPlanId]);

  const loadLessonResource = async () => {
    try {
      // First, try to get existing lesson resource
      const response = await apiService.getLessonResources(lessonPlanId!);
      
      if (response.error) {
        setError(response.error);
        setSuccessMessage(''); // Clear success message
        return;
      }

      if (response.data && response.data.length > 0) {
        const resource = response.data[0]; // Get the most recent resource
        setLessonResource(resource);
        setAiContent(resource.ai_generated_content || '');
        setUserEditedContent(resource.user_edited_content || '');
        setExportFormat((resource.export_format as 'pdf' | 'docx') || 'pdf');
      } else {
        // No existing resource, generate one
        await generateLessonResource();
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load lesson resource');
      setSuccessMessage(''); // Clear success message
    } finally {
      setIsLoading(false);
    }
  };

  // Function to convert structured JSON to readable format for editing
  const convertStructuredToReadable = (jsonContent: string): string => {
    try {
      const parsed = JSON.parse(jsonContent);
      let readable = '';

      if (parsed.title_header) {
        readable += `# Lesson Overview\n`;
        if (parsed.title_header.topic) readable += `Topic: ${parsed.title_header.topic}\n`;
        if (parsed.title_header.subject) readable += `Subject: ${parsed.title_header.subject}\n`;
        if (parsed.title_header.grade_level) readable += `Grade Level: ${parsed.title_header.grade_level}\n`;
        if (parsed.title_header.country) readable += `Country: ${parsed.title_header.country}\n`;
        if (parsed.title_header.local_context) readable += `Local Context: ${parsed.title_header.local_context}\n`;
        readable += '\n';
      }

      if (parsed.learning_objectives && parsed.learning_objectives.length > 0) {
        readable += `# Learning Objectives\n`;
        parsed.learning_objectives.forEach((objective: string, index: number) => {
          readable += `${index + 1}. ${objective}\n`;
        });
        readable += '\n';
      }

      if (parsed.lesson_content) {
        readable += `# Lesson Content\n`;
        if (parsed.lesson_content.introduction) {
          readable += `## Introduction\n${parsed.lesson_content.introduction}\n\n`;
        }
        if (parsed.lesson_content.main_concepts && parsed.lesson_content.main_concepts.length > 0) {
          readable += `## Main Concepts\n`;
          parsed.lesson_content.main_concepts.forEach((concept: string, index: number) => {
            readable += `${index + 1}. ${concept}\n`;
          });
          readable += '\n';
        }
        if (parsed.lesson_content.examples && parsed.lesson_content.examples.length > 0) {
          readable += `## Examples\n`;
          parsed.lesson_content.examples.forEach((example: string, index: number) => {
            readable += `${index + 1}. ${example}\n`;
          });
          readable += '\n';
        }
        if (parsed.lesson_content.step_by_step_instructions && parsed.lesson_content.step_by_step_instructions.length > 0) {
          readable += `## Step-by-Step Instructions\n`;
          parsed.lesson_content.step_by_step_instructions.forEach((step: string, index: number) => {
            readable += `${index + 1}. ${step}\n`;
          });
          readable += '\n';
        }
      }

      if (parsed.assessment && parsed.assessment.length > 0) {
        readable += `# Assessment\n`;
        parsed.assessment.forEach((item: string, index: number) => {
          readable += `${index + 1}. ${item}\n`;
        });
        readable += '\n';
      }

      if (parsed.key_takeaways && parsed.key_takeaways.length > 0) {
        readable += `# Key Takeaways\n`;
        parsed.key_takeaways.forEach((takeaway: string, index: number) => {
          readable += `${index + 1}. ${takeaway}\n`;
        });
        readable += '\n';
      }

      if (parsed.related_projects_or_activities && parsed.related_projects_or_activities.length > 0) {
        readable += `# Related Projects & Activities\n`;
        parsed.related_projects_or_activities.forEach((activity: string, index: number) => {
          readable += `${index + 1}. ${activity}\n`;
        });
        readable += '\n';
      }

      if (parsed.references && parsed.references.length > 0) {
        readable += `# References\n`;
        parsed.references.forEach((reference: string, index: number) => {
          readable += `${index + 1}. ${reference}\n`;
        });
        readable += '\n';
      }

      return readable.trim();
    } catch (error) {
      return jsonContent; // Return original content if parsing fails
    }
  };

  const generateLessonResource = async () => {
    try {
      setError(''); // Clear any previous errors
      setSuccessMessage(''); // Clear any previous success messages
      const response = await apiService.generateLessonResource(lessonPlanId!, '');
      
      if (response.error) {
        setError(response.error);
        return;
      }

      if (response.data) {
        setLessonResource(response.data);
        setAiContent(response.data.ai_generated_content || '');
        setUserEditedContent(response.data.user_edited_content || '');
        setExportFormat((response.data.export_format as 'pdf' | 'docx') || 'pdf');
      } else {
        setError('No data received from lesson resource generation');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to generate lesson resource');
    }
  };

  const saveLessonResource = async () => {
    if (!lessonResource) {
      setError('No lesson resource available to save');
      setSuccessMessage(''); // Clear success message
      return;
    }

    setIsSaving(true);
    setError('');
    setSuccessMessage(''); // Clear any previous success message

    try {
      const response = await apiService.updateLessonResource(
        lessonResource.lesson_resources_id.toString(),
        userEditedContent
      );

      if (response.error) {
        setError(response.error);
        return;
      }

      if (response.data) {
        setLessonResource(response.data);
        setSuccessMessage('Lesson resource saved successfully!');
        // Clear success message after 3 seconds
        setTimeout(() => setSuccessMessage(''), 3000);
      } else {
        setError('No data received from save request');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to save lesson resource');
    } finally {
      setIsSaving(false);
    }
  };

  const exportLessonResource = async (format: 'pdf' | 'docx') => {
    if (!lessonResource) {
      setError('No lesson resource available for export');
      setSuccessMessage(''); // Clear success message
      return;
    }

    try {
      setError(''); // Clear any previous errors
      setSuccessMessage(''); // Clear any previous success messages
      const response = await apiService.exportLessonResource(
        lessonResource.lesson_resources_id.toString(),
        format
      );

      if (response.error) {
        setError(response.error);
        return;
      }

      if (response.data) {
        // Create download link
        const url = window.URL.createObjectURL(response.data);
        const a = document.createElement('a');
        a.href = url;
        a.download = `lesson-resource.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        // Show success message
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

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Edit Lesson Resource</h1>
              <p className="text-gray-600">Customize AI-generated content for your classroom</p>
            </div>
            <div className="flex space-x-3">
              <button
                onClick={() => navigate('/dashboard')}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Back to Dashboard
              </button>
              <button
                onClick={saveLessonResource}
                disabled={isSaving}
                className="px-4 py-2 bg-orange-500 text-white rounded-md hover:bg-orange-600 disabled:opacity-50"
              >
                {isSaving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}
        {successMessage && (
          <div className="mb-6 bg-green-50 border border-green-200 rounded-md p-4">
            <p className="text-green-800">{successMessage}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* AI Generated Content */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold mb-4">AI Generated Content</h2>
              
              {/* AI Disclaimer */}
              <div className="bg-amber-50 border border-amber-200 rounded-md p-4 mb-4">
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-amber-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-amber-800">AI-Generated Content Disclaimer</h3>
                    <div className="mt-2 text-sm text-amber-700">
                      <p>This lesson resource has been generated by AI and may contain inaccuracies or require adjustments. As an educator, you should:</p>
                      <ul className="list-disc list-inside mt-2 space-y-1">
                        <li>Review all content for accuracy and appropriateness</li>
                        <li>Edit and customize to align with your curriculum standards</li>
                        <li>Adapt to your students' specific needs and learning levels</li>
                        <li>Verify cultural relevance and local context</li>
                        <li>Ensure alignment with your teaching methodology</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-2">Structured lesson content:</p>
                <StructuredContentRenderer content={aiContent} />
              </div>
            </div>

            {/* User Edited Content */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold">Your Customizations</h2>
                <button
                  onClick={() => setUserEditedContent(convertStructuredToReadable(aiContent))}
                  className="text-sm text-green-600 hover:text-green-800 underline"
                >
                  Convert AI Content to Editable Format
                </button>
              </div>
              <textarea
                value={userEditedContent}
                onChange={(e) => setUserEditedContent(e.target.value)}
                placeholder="Edit and customize the AI-generated content for your classroom... Click 'Convert AI Content to Editable Format' to start with the structured content."
                className="w-full h-64 p-4 border border-gray-300 rounded-md focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
              <p className="text-sm text-gray-600 mt-2">
                Customize the content to fit your teaching style and classroom needs. You can convert the structured AI content to a readable format for easier editing.
              </p>
            </div>


          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Export Options */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Export Options</h3>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Export Format
                </label>
                <select
                  value={exportFormat}
                  onChange={(e) => setExportFormat(e.target.value as 'pdf' | 'docx')}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-orange-500"
                >
                  <option value="pdf">PDF Document</option>
                  <option value="docx">Word Document (DOCX)</option>
                </select>
              </div>

              <button
                onClick={() => exportLessonResource(exportFormat)}
                className="w-full px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600"
              >
                Export Lesson Resource
              </button>
            </div>

            {/* Status */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Resource Status</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Status:</span>
                  <span className="text-sm font-medium text-orange-600">
                    {lessonResource?.status || 'Draft'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Created:</span>
                  <span className="text-sm text-gray-900">
                    {lessonResource?.created_at ? new Date(lessonResource.created_at).toLocaleDateString() : 'N/A'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Resource ID:</span>
                  <span className="text-sm text-gray-900">
                    {lessonResource?.lesson_resources_id || 'N/A'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EditLessonResourcePage; 