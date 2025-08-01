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
  borderColor
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
        <div className="space-y-2">
          {editContent.map((item: string, index: number) => (
            <div key={index} className="flex gap-2">
              <input
                type="text"
                value={item}
                onChange={(e) => {
                  const newContent = [...editContent];
                  newContent[index] = e.target.value;
                  setEditContent(newContent);
                }}
                className="flex-1 p-2 border border-gray-300 rounded text-sm"
              />
              <button
                onClick={() => {
                  const newContent = editContent.filter((_: string, i: number) => i !== index);
                  setEditContent(newContent);
                }}
                className="px-2 py-1 text-red-600 hover:text-red-800 text-sm"
              >
                Remove
              </button>
            </div>
          ))}
          <button
            onClick={() => setEditContent([...editContent, ''])}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            + Add Item
          </button>
        </div>
      );
    } else if (typeof content === 'object' && content !== null) {
      return (
        <div className="space-y-3">
          {Object.entries(content).map(([key, value]) => (
            <div key={key}>
              <label className="block text-sm font-medium mb-1 capitalize">
                {key.replace(/_/g, ' ')}
              </label>
              {Array.isArray(value) ? (
                <div className="space-y-2">
                  {editContent[key].map((item: string, index: number) => (
                    <div key={index} className="flex gap-2">
                      <input
                        type="text"
                        value={item}
                        onChange={(e) => {
                          const newContent = { ...editContent };
                          newContent[key] = [...newContent[key]];
                          newContent[key][index] = e.target.value;
                          setEditContent(newContent);
                        }}
                        className="flex-1 p-2 border border-gray-300 rounded text-sm"
                      />
                      <button
                        onClick={() => {
                          const newContent = { ...editContent };
                          newContent[key] = newContent[key].filter((_: string, i: number) => i !== index);
                          setEditContent(newContent);
                        }}
                        className="px-2 py-1 text-red-600 hover:text-red-800 text-sm"
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
                    className="text-sm text-blue-600 hover:text-blue-800"
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
                  className="w-full p-2 border border-gray-300 rounded text-sm"
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
          className="w-full p-3 border border-gray-300 rounded text-sm"
          rows={4}
        />
      );
    }
  };

  return (
    <div className={`${bgColor} rounded-lg p-4 border ${borderColor}`}>
      <div className="flex justify-between items-center mb-3">
        <h3 className={`font-semibold ${textColor}`}>{title}</h3>
        {!isEditing ? (
          <button
            onClick={onEdit}
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            Edit
          </button>
        ) : (
          <div className="flex gap-2">
            <button
              onClick={handleSave}
              className="text-sm text-green-600 hover:text-green-800 font-medium"
            >
              Save
            </button>
            <button
              onClick={onCancel}
              className="text-sm text-gray-600 hover:text-gray-800 font-medium"
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
      loadLessonResource();
    }
  }, [lessonPlanId]);

  const loadLessonResource = async () => {
    try {
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
            setStructuredContent(parsed);
          } catch (error) {
            setError('Failed to parse lesson resource content');
          }
        }
      } else {
        await generateLessonResource();
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load lesson resource');
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
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Edit Lesson Resource</h1>
              <p className="text-gray-600">Edit each section directly to customize for your classroom</p>
            </div>
            <div className="flex space-x-3">
              <button
                onClick={() => navigate('/dashboard')}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Back to Dashboard
              </button>
              <button
                onClick={saveAllChanges}
                disabled={isSaving}
                className="px-4 py-2 bg-orange-500 text-white rounded-md hover:bg-orange-600 disabled:opacity-50"
              >
                {isSaving ? 'Saving...' : 'Save All Changes'}
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
            {/* AI Disclaimer */}
            <div className="bg-amber-50 border border-amber-200 rounded-md p-4">
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
                    <p className="mt-2">Click the "Edit" button on any section to customize the content for your classroom needs.</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Read-only Sections */}
            {structuredContent.title_header && (
              <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                <div className="mb-3">
                  <h3 className="font-semibold text-blue-900">Lesson Overview</h3>
                </div>
                <div className="space-y-2">
                  {Object.entries(structuredContent.title_header).map(([key, value]) => (
                    <div key={key}>
                      <span className="font-medium capitalize">{key.replace(/_/g, ' ')}:</span>
                      <span className="ml-2 text-sm text-blue-700">{value as string}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {structuredContent.learning_objectives && (
              <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                <div className="mb-3">
                  <h3 className="font-semibold text-green-900">Learning Objectives</h3>
                </div>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  {structuredContent.learning_objectives.map((objective, index) => (
                    <li key={index} className="text-green-800">{objective}</li>
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
                bgColor="bg-purple-50"
                textColor="text-purple-900"
                borderColor="border-purple-200"
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
                borderColor="border-orange-200"
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
                borderColor="border-indigo-200"
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
                borderColor="border-teal-200"
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
                borderColor="border-gray-200"
              />
            )}
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