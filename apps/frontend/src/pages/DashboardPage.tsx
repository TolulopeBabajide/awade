import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiService from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const teachingStyles = ['Lesson', 'Project', 'Discussion'];
const languages = ['English', 'French', 'Swahili'];
const aiSuggestedTopics = ['Fractions', 'Geometry', 'Measurements', 'Algebra', 'Simultaneous Equations'];

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [countries, setCountries] = useState<any[]>([]);
  const [selectedCountry, setSelectedCountry] = useState<string>('');
  const [curriculums, setCurriculums] = useState<any[]>([]);
  const [selectedCurriculum, setSelectedCurriculum] = useState<string>('');
  const [subjects, setSubjects] = useState<any[]>([]);
  const [selectedSubject, setSelectedSubject] = useState<string>('');
  const [gradeLevels, setGradeLevels] = useState<any[]>([]);
  const [selectedGradeLevel, setSelectedGradeLevel] = useState<string>('');
  const [form, setForm] = useState({
    teachingStyle: teachingStyles[0],
    language: languages[0],
    topic: '',
    weeks: '',
    classPerWeek: '',
    description: '',
  });
  const [selectedTopic, setSelectedTopic] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string>('');
  const [lessonPlans, setLessonPlans] = useState<any[]>([]);
  const [lessonResources, setLessonResources] = useState<any[]>([]);

  // Fetch countries on mount
  useEffect(() => {
    const loadCountries = async () => {
      // Only load if user is authenticated
      if (!user) {
        return;
      }
      
      try {
        const response = await apiService.getCountries();
        if (response.data) {
          setCountries(response.data);
        } else if (response.error) {
          console.error('Error loading countries:', response.error);
          setError(response.error);
        }
      } catch (err: any) {
        console.error('Error fetching countries:', err);
        setError('Failed to load countries');
      }
    };

    loadCountries();
  }, [user]); // Add user as dependency

  // Load lesson plans and resources
  useEffect(() => {
    const loadDashboardData = async () => {
      // Only load if user is authenticated
      if (!user) {
        return;
      }
      
      try {
        // Load lesson plans
        const plansResponse = await apiService.getLessonPlans();
        if (plansResponse.data) {
          setLessonPlans(plansResponse.data);
        } else if (plansResponse.error) {
          console.error('Error loading lesson plans:', plansResponse.error);
        }

        // Load lesson resources
        const resourcesResponse = await apiService.getAllLessonResources();
        if (resourcesResponse.data) {
          setLessonResources(resourcesResponse.data);
        } else if (resourcesResponse.error) {
          console.error('Error loading lesson resources:', resourcesResponse.error);
        }
      } catch (err: any) {
        console.error('Error loading dashboard data:', err);
      }
    };

    loadDashboardData();
  }, [user]); // Add user as dependency

  // Fetch curriculums when country changes
  useEffect(() => {
    if (selectedCountry) {
      apiService.getCurriculums(parseInt(selectedCountry))
        .then(response => {
          if (response.data) {
            setCurriculums(response.data);
          } else if (response.error) {
            console.error('Error fetching curriculums:', response.error);
            setError('Failed to load curriculums');
          }
        })
        .catch(err => {
          console.error('Error fetching curriculums:', err);
          setError('Failed to load curriculums');
        });
    } else {
      setCurriculums([]);
    }
    setSelectedCurriculum('');
    setSubjects([]);
    setSelectedSubject('');
    setGradeLevels([]);
    setSelectedGradeLevel('');
  }, [selectedCountry]);

  // Fetch subjects and grade levels when a curriculum is selected
  useEffect(() => {
    if (selectedCurriculum) {
      // Fetch curriculum structures for the selected curriculum
      apiService.getCurriculumStructures(parseInt(selectedCurriculum))
        .then(response => {
          if (response.data) {
            const structures = response.data;
            // Extract unique subject and grade level IDs
            const subjectIds = Array.from(new Set(structures.map((s: any) => s.subject_id)));
            const gradeLevelIds = Array.from(new Set(structures.map((s: any) => s.grade_level_id)));

            // Fetch subject and grade level details
            Promise.all([
              apiService.getSubjects(),
              apiService.getGradeLevels()
            ]).then(([subjectsResponse, gradesResponse]) => {
              if (subjectsResponse.data && gradesResponse.data) {
                setSubjects(subjectsResponse.data.filter((s: any) => subjectIds.includes(s.subject_id)));
                setGradeLevels(gradesResponse.data.filter((g: any) => gradeLevelIds.includes(g.grade_level_id)));
                setSelectedSubject('');
                setSelectedGradeLevel('');
              } else {
                console.error('Error fetching subjects/grade levels:', subjectsResponse.error || gradesResponse.error);
                setError('Failed to load subjects and grade levels');
              }
            }).catch(err => {
              console.error('Error fetching subjects/grade levels:', err);
              setError('Failed to load subjects and grade levels');
            });
          } else if (response.error) {
            console.error('Error fetching curriculum structures:', response.error);
            setError('Failed to load curriculum structures');
          }
        })
        .catch(err => {
          console.error('Error fetching curriculum structures:', err);
          setError('Failed to load curriculum structures');
        });
    } else {
      setSubjects([]);
      setGradeLevels([]);
      setSelectedSubject('');
      setSelectedGradeLevel('');
    }
  }, [selectedCurriculum]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  const handleCurriculumChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedCurriculum(e.target.value);
  };

  const handleSubjectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedSubject(e.target.value);
  };

  const handleGradeLevelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedGradeLevel(e.target.value);
  };

  const handleCountryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedCountry(e.target.value);
  };

  const handleTopicSelect = (topic: string) => {
    setSelectedTopic(topic);
    setForm({ ...form, topic });
  };

  const handleGenerate = async () => {
    // Validate required fields
    if (!selectedSubject || !selectedGradeLevel || !form.topic.trim()) {
      setError('Please select subject, grade level, and enter a topic.');
      return;
    }

    setIsGenerating(true);
    setError('');
    
    try {
      // Get subject and grade level names from the selected options
      const subjectName = subjects.find(s => s.subject_id === parseInt(selectedSubject))?.name || '';
      const gradeLevelName = gradeLevels.find(g => g.grade_level_id === parseInt(selectedGradeLevel))?.name || '';
      
      // Additional validation for names
      if (!subjectName || !gradeLevelName) {
        throw new Error('Invalid subject or grade level selection. Please try again.');
      }

      const requestBody = {
        subject: subjectName,
        grade_level: gradeLevelName,
        topic: form.topic.trim(),
        user_id: user?.user_id || 1,
      };

      const response = await apiService.generateLessonPlan(requestBody);

      if (response.error) {
        throw new Error(response.error);
      }

      if (response.data) {
        // Navigate to lesson plan detail page with the generated data
        navigate(`/lesson-plans/${response.data.lesson_id}`, { 
          state: { lessonPlanData: response.data } 
        });
      }
    } catch (err: any) {
      setError(err.message || 'Failed to generate lesson plan. Please try again.');
      console.error(err);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col md:flex-row">
      {/* Sidebar */}
      <aside className="w-full md:w-64 bg-white border-b md:border-b-0 md:border-r flex flex-row md:flex-col py-4 md:py-8 px-4 md:min-h-screen items-center md:items-stretch">
        <div className="flex items-center mb-8 md:mb-8 w-full justify-center md:justify-start">
          <div className="w-10 h-10 bg-green-200 rounded-full flex items-center justify-center mr-2">
            <span className="text-2xl font-bold text-green-700">O</span>
          </div>
          <span className="font-bold text-xl tracking-widest">AWADE</span>
        </div>
        <nav className="flex-1 space-y-2 w-full hidden md:block">
          <button className="w-full text-left px-4 py-2 rounded bg-orange-100 text-orange-700 font-semibold">Dashboard</button>
          <button className="w-full text-left px-4 py-2 rounded hover:bg-gray-100">Lesson Plans</button>
          <button className="w-full text-left px-4 py-2 rounded hover:bg-gray-100">Resources</button>
          <button className="w-full text-left px-4 py-2 rounded hover:bg-gray-100">Messages</button>
          <button className="w-full text-left px-4 py-2 rounded hover:bg-gray-100">Support</button>
          <button className="w-full text-left px-4 py-2 rounded hover:bg-gray-100">Settings</button>
        </nav>
        <button className="mt-8 text-left px-4 py-2 text-red-500 hover:underline hidden md:block" onClick={logout}>Log out</button>
      </aside>
      {/* Main Content */}
      <main className="flex-1 p-4 md:p-10">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-center mb-8 gap-4">
          <div className="text-center md:text-left">
            <h2 className="text-2xl font-bold mb-1">Welcome, {user?.full_name || 'User'}</h2>
            <p className="text-gray-500">Generate Lesson plans tailored towards your African Classroom.</p>
          </div>
          <div className="flex items-center space-x-2 bg-white px-4 py-2 rounded shadow">
            <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
              <span className="text-lg font-bold text-gray-700">{user?.full_name?.charAt(0) || 'U'}</span>
            </div>
            <div>
              <div className="font-semibold text-sm">{user?.full_name || 'User'}</div>
              <div className="text-xs text-gray-500">{user?.role || 'Educator'}</div>
            </div>
            {/* Mobile logout button */}
            <button 
              className="md:hidden ml-2 text-red-500 hover:text-red-700 text-sm font-medium"
              onClick={logout}
            >
              Logout
            </button>
          </div>
        </div>
        

        {/* Create Lesson Plan Form */}
        <div className="bg-white rounded shadow p-4 md:p-8 mb-10">
          <h3 className="text-lg font-bold mb-4">Create Lesson Plan</h3>
          <form className="grid grid-cols-1 sm:grid-cols-2 gap-4 md:gap-6">
            <div>
              <label className="block text-sm font-semibold mb-1">Country</label>
              <select value={selectedCountry} onChange={handleCountryChange} className="w-full border rounded px-3 py-2">
                <option value="">Select Country</option>
                {countries.map((country: any) => (
                  <option key={country.country_id} value={country.country_id}>{country.country_name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold mb-1">Curriculum</label>
              <select value={selectedCurriculum} onChange={handleCurriculumChange} className="w-full border rounded px-3 py-2">
                <option value="">Select Curriculum</option>
                {curriculums.map(curr => (
                  <option key={curr.curricula_id} value={curr.curricula_id}>
                    {curr.curricula_title}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold mb-1">Subject</label>
              <select value={selectedSubject} onChange={handleSubjectChange} className="w-full border rounded px-3 py-2" disabled={subjects.length === 0}>
                <option value="">Select Subject</option>
                {subjects.map((subj: any) => (
                  <option key={subj.subject_id} value={subj.subject_id}>{subj.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold mb-1">Grade Level</label>
              <select value={selectedGradeLevel} onChange={handleGradeLevelChange} className="w-full border rounded px-3 py-2" disabled={gradeLevels.length === 0}>
                <option value="">Select Grade Level</option>
                {gradeLevels.map((grade: any) => (
                  <option key={grade.grade_level_id} value={grade.grade_level_id}>{grade.name}</option>
                ))}
              </select>
            </div>
            <div className="sm:col-span-2">
              <label className="block text-sm font-semibold mb-1">Suggested Topics</label>
              <div className="flex flex-wrap gap-2 mb-2">
                {aiSuggestedTopics.map(topic => (
                  <button
                    type="button"
                    key={topic}
                    className={`px-4 py-1 rounded-full border ${selectedTopic === topic ? 'bg-orange-200 border-orange-400' : 'bg-gray-100 border-gray-300'} text-sm`}
                    onClick={() => handleTopicSelect(topic)}
                  >
                    {topic}
                  </button>
                ))}
              </div>
              <input
                type="text"
                name="topic"
                value={form.topic}
                onChange={handleChange}
                placeholder="Enter or select a topic"
                className="w-full border rounded px-3 py-2"
              />
            </div>
            <div className="sm:col-span-2 flex justify-end">
              <button
                type="button"
                className="bg-orange-400 text-white font-semibold px-8 py-2 rounded hover:bg-orange-500 disabled:opacity-50 disabled:cursor-not-allowed"
                onClick={handleGenerate}
                disabled={isGenerating}
              >
                {isGenerating ? 'Generating...' : 'Generate'}
              </button>
            </div>
            {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
            

          </form>
        </div>
        {/* My Lesson Plans Section */}
        <div>
          <div className="flex flex-col md:flex-row justify-between items-center mb-4 gap-2 md:gap-0">
            <h4 className="text-lg font-bold">My Lesson Plans</h4>
            <button 
              className="text-orange-600 underline"
              onClick={() => navigate('/lesson-plans')}
            >
              View All
            </button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {lessonPlans.length > 0 ? (
              lessonPlans.slice(0, 5).map((plan: any) => (
                <div key={plan.lesson_id} className="bg-white rounded shadow p-4 flex flex-col items-center cursor-pointer hover:shadow-md transition-shadow"
                     onClick={() => navigate(`/lesson-plans/${plan.lesson_id}`)}>
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-2">
                    <span className="text-2xl">📚</span>
                  </div>
                  <div className="font-semibold mb-1 text-center text-sm">{plan.subject}</div>
                  <div className="text-xs text-gray-500 mb-1">{plan.grade_level}</div>
                  <div className="text-xs text-gray-400 mb-2">{plan.duration_minutes || 45} min</div>
                  <div className="text-xs text-gray-600 text-center line-clamp-2">{plan.topic || 'No topic'}</div>
                </div>
              ))
            ) : (
              // Empty state when no lesson plans
              <div className="col-span-full text-center py-8">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">📚</span>
                </div>
                <h3 className="text-lg font-semibold text-gray-700 mb-2">No Lesson Plans Yet</h3>
                <p className="text-gray-500 mb-4">Create your first lesson plan to get started</p>
                <button 
                  className="bg-orange-400 text-white px-4 py-2 rounded hover:bg-orange-500"
                  onClick={() => {
                    // Scroll to the form and focus on the topic input
                    const topicInput = document.querySelector('input[name="topic"]') as HTMLInputElement;
                    if (topicInput) {
                      topicInput.scrollIntoView({ behavior: 'smooth' });
                      topicInput.focus();
                    }
                  }}
                >
                  Create Lesson Plan
                </button>
              </div>
            )}
          </div>
        </div>
        {/* My Lesson Resources Section */}
        <div className="mt-10">
          <div className="flex flex-col md:flex-row justify-between items-center mb-4 gap-2 md:gap-0">
            <h4 className="text-lg font-bold">My Lesson Resources</h4>
            <button 
              className="text-orange-600 underline"
              onClick={() => navigate('/lesson-plans')}
            >
              View All
            </button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {lessonResources.length > 0 ? (
              lessonResources.slice(0, 5).map((resource: any) => {
                // Parse AI content to get title if available
                let title = 'Lesson Resource';
                let description = 'AI-generated content';
                
                try {
                  if (resource.ai_generated_content) {
                    const parsedContent = JSON.parse(resource.ai_generated_content);
                    if (parsedContent.title_header?.topic) {
                      title = `${parsedContent.title_header.subject || 'Subject'}: ${parsedContent.title_header.topic}`;
                    }
                    if (parsedContent.lesson_content?.introduction) {
                      description = parsedContent.lesson_content.introduction.substring(0, 50) + '...';
                    }
                  }
                } catch (e) {
                  // If parsing fails, use default values
                }
                
                return (
                  <div key={resource.lesson_resources_id} 
                       className="bg-white rounded shadow p-4 flex flex-col items-center cursor-pointer hover:shadow-md transition-shadow"
                       onClick={() => navigate(`/lesson-plans/${resource.lesson_plan_id}/resources/edit`)}>
                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-2">
                      <span className="text-2xl">{resource.export_format === 'pdf' ? '📄' : '📝'}</span>
                    </div>
                    <div className="font-semibold mb-1 text-center text-sm line-clamp-2">{title}</div>
                    <div className="text-xs text-gray-500 mb-1">{resource.export_format?.toUpperCase() || 'DRAFT'}</div>
                    <div className="text-xs text-gray-400 mb-2">{resource.status}</div>
                    <div className="text-xs text-gray-600 text-center line-clamp-2">{description}</div>
                  </div>
                );
              })
            ) : (
              // Empty state when no lesson resources
              <div className="col-span-full text-center py-8">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">📄</span>
                </div>
                <h3 className="text-lg font-semibold text-gray-700 mb-2">No Lesson Resources Yet</h3>
                <p className="text-gray-500 mb-4">Create lesson plans to generate AI-powered resources</p>
                <button 
                  className="bg-orange-400 text-white px-4 py-2 rounded hover:bg-orange-500"
                  onClick={() => {
                    const topicInput = document.querySelector('input[name="topic"]') as HTMLInputElement;
                    if (topicInput) {
                      topicInput.scrollIntoView({ behavior: 'smooth' });
                      topicInput.focus();
                    }
                  }}
                >
                  Create Lesson Plan
                </button>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default DashboardPage; 