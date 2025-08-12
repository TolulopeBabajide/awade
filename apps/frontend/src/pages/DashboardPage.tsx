import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import apiService from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { 
  FaHome, 
  FaBookOpen, 
  FaFolder, 
  FaComments, 
  FaHeadset, 
  FaCog, 
  FaSignOutAlt, 
  FaSearch, 
  FaUser, 
  FaPlus,
  FaEye,
  FaFileAlt,
  FaGraduationCap,
  FaGlobe,
  FaChevronLeft,
  FaChevronRight
} from 'react-icons/fa';

const aiSuggestedTopics = ['Fractions', 'Geometry', 'Measurements', 'Algebra', 'Simultaneous Equations'];

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
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
    topic: '',
  });
  const [selectedTopic, setSelectedTopic] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string>('');
  const [lessonPlans, setLessonPlans] = useState<any[]>([]);
  const [lessonResources, setLessonResources] = useState<any[]>([]);
  const [carouselRef, setCarouselRef] = useState<HTMLDivElement | null>(null);
  const [canScrollLeftState, setCanScrollLeftState] = useState(false);
  const [canScrollRightState, setCanScrollRightState] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

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

  // Handle carousel scroll events
  useEffect(() => {
    const handleScroll = () => {
      if (carouselRef) {
        setCanScrollLeftState(carouselRef.scrollLeft > 0);
        setCanScrollRightState(carouselRef.scrollLeft < (carouselRef.scrollWidth - carouselRef.clientWidth));
      }
    };

    if (carouselRef) {
      carouselRef.addEventListener('scroll', handleScroll);
      // Initial check
      handleScroll();
      
      return () => {
        carouselRef.removeEventListener('scroll', handleScroll);
      };
    }
  }, [carouselRef]);

  // Handle click outside user menu
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (showUserMenu && !(event.target as Element).closest('.user-menu-container')) {
        setShowUserMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showUserMenu]);

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
          // Don't set error for resources as it's not critical for dashboard functionality
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
        user_id: user?.user_id,
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

  // Carousel navigation functions
  const scrollCarousel = (direction: 'left' | 'right') => {
    if (carouselRef) {
      const scrollAmount = 240; // Adjusted for mobile card width + spacing
      const currentScroll = carouselRef.scrollLeft;
      
      if (direction === 'left') {
        carouselRef.scrollTo({
          left: Math.max(0, currentScroll - scrollAmount),
          behavior: 'smooth'
        });
      } else {
        const maxScroll = carouselRef.scrollWidth - carouselRef.clientWidth;
        carouselRef.scrollTo({
          left: Math.min(maxScroll, currentScroll + scrollAmount),
          behavior: 'smooth'
        });
      }
    }
  };

  const canScrollLeft = () => {
    return carouselRef ? carouselRef.scrollLeft > 0 : false;
  };

  const canScrollRight = () => {
    if (!carouselRef) return false;
    const maxScroll = carouselRef.scrollWidth - carouselRef.clientWidth;
    return carouselRef.scrollLeft < maxScroll;
  };

  return (
    <div className="min-h-screen flex flex-col lg:flex-row bg-gray-50 ">
      {/* Sidebar */}
      <aside className="w-full hidden lg:w-64 bg-white border-b lg:border-b-0 lg:border-r border-gray-200 flex flex-row lg:flex-col pb-3 md:pb-4 lg:pb-8 px-2 md:px-4 lg:px-4 lg:min-h-screen items-center lg:items-stretch flex-shrink-0">
        {/* Logo */}
        <div className="hidden lg:flex items-center mb-8 lg:mb-8 w-full justify-center ">
          
          <span className="font-bold text-3xl text-center tracking-wide text-primary-800">AWADE</span>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-2 w-full hidden lg:block">
          <button className="w-full text-left px-4 py-3 rounded-lg bg-accent-600 text-white font-semibold flex items-center">
            <FaHome className="w-4 h-4 mr-3" />
            Dashboard
          </button>
          <button 
            className="w-full text-left px-4 py-3 rounded-lg hover:bg-gray-100 text-gray-700 font-medium flex items-center"
            onClick={() => navigate('/lesson-plans')}
          >
            <FaBookOpen className="w-4 h-4 mr-3" />
            Lesson Plans
          </button>
          <button 
            className="w-full text-left px-4 py-3 rounded-lg hover:bg-gray-100 text-gray-700 font-medium flex items-center"
            onClick={() => navigate('/lesson-resources')}
          >
            <FaFolder className="w-4 h-4 mr-3" />
            Resources
          </button>
          
          
          <button className="w-full text-left px-4 py-3 rounded-lg hover:bg-gray-100 text-gray-700 font-medium flex items-center">
            <FaCog className="w-4 h-4 mr-3" />
            Settings
          </button>
        </nav>

        {/* Logout */}
        <button 
          className="mt-8 text-left px-4 py-3 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg hidden lg:flex items-center" 
          onClick={logout}
        >
          <FaSignOutAlt className="w-4 h-4 mr-3" />
          Log out
        </button>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col p-2 md:p-4 lg:p-6">
        {/* Header */}
        <div className="flex justify-between items-start pt-0 pb-2 md:pb-4 lg:pb-5 px-2 md:px-4 lg:px-5 gap-2 md:gap-4 flex-shrink-0">
          {/* Left Side - Welcome Message */}
          <div className="flex-1">
            {/* Welcome Message */}
            <div className="text-left">
              <h2 className="text-xl md:text-2xl lg:text-3xl xl:text-4xl font-bold mb-1 md:mb-2 text-gray-900 mt-0 pt-0">Welcome, {user?.full_name || 'User'}</h2>
              <p className="text-sm md:text-base lg:text-lg text-gray-600">Generate Lesson plans tailored towards your African Classroom.</p>
            </div>
          </div>
          
          {/* Right Side - User Profile */}
          <div className="flex items-center space-x-2 md:space-x-3 flex-shrink-0">
            <div className="relative user-menu-container">
              <button 
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="w-8 h-8 md:w-10 md:h-10 bg-primary-600 rounded-full flex items-center justify-center hover:bg-primary-700 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
              >
                <FaUser className="w-4 h-4 md:w-5 md:h-5 text-white" />
              </button>
              
              {/* User Menu Popup */}
              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
                  <div className="px-4 py-3 border-b border-gray-100">
                    <div className="font-semibold text-sm text-gray-900">{user?.full_name || 'User'}</div>
                    <div className="text-xs text-gray-500">{user?.role || 'Educator'}</div>
                  </div>
                  <button 
                    onClick={() => navigate('/profile')}
                    className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center"
                  >
                    <FaUser className="w-4 h-4 mr-2" />
                    View Profile
                  </button>
                  <button 
                    onClick={logout}
                    className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center"
                  >
                    <FaSignOutAlt className="w-4 h-4 mr-2" />
                    Logout
                  </button>
                </div>
              )}
            </div>
            
            <div className="hidden sm:block">
              <div className="font-semibold text-xs md:text-sm text-gray-900">{user?.full_name || 'User'}</div>
              <div className="text-xs text-gray-500">{user?.role || 'Educator'}</div>
            </div>
          </div>
        </div>

        {/* Dashboard Content - Natural flow on desktop, 100% Create Lesson Plan on mobile */}
        <div className="flex flex-col flex-1 overflow-y-auto md:overflow-y-auto">
          {/* Create Lesson Plan Section - Full height on mobile, natural height on desktop */}
          <div className="min-h-[500px] lg:min-h-0 p-2 md:p-4 lg:p-6 pb-20 md:pb-4">
            <div className="p-3 md:p-4 lg:p-5">
              <div className="flex items-center mb-3 md:mb-4">
                <h3 className="text-lg md:text-xl lg:text-2xl font-bold text-gray-900">
                  Create Lesson Plan
                </h3>
              </div>
              
              <form className="space-y-3 md:space-y-4 mb-6 md:mb-0">
                {/* First Row - Country and Curriculum */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-4">
                  <div className="space-y-1 md:space-y-2">
                    <label className="block text-xs md:text-sm font-semibold text-gray-700">
                      Country
                    </label>
                    <select 
                      value={selectedCountry} 
                      onChange={handleCountryChange} 
                      className="w-full border border-gray-300 rounded-lg px-3 md:px-4 py-2 md:py-3 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 text-sm bg-white hover:border-gray-400"
                    >
                      <option value="">Select Country</option>
                      {countries.map((country: any) => (
                        <option key={country.country_id} value={country.country_id}>{country.country_name}</option>
                      ))}
                    </select>
                  </div>
                  
                  <div className="space-y-1 md:space-y-2">
                    <label className="block text-xs md:text-sm font-semibold text-gray-700">
                      Curriculum
                    </label>
                    <select 
                      value={selectedCurriculum} 
                      onChange={handleCurriculumChange} 
                      className="w-full border border-gray-300 rounded-lg px-3 md:px-4 py-2 md:py-3 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 text-sm bg-white hover:border-gray-400"
                    >
                      <option value="">Select Curriculum</option>
                      {curriculums.map(curr => (
                        <option key={curr.curricula_id} value={curr.curricula_id}>
                          {curr.curricula_title}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Second Row - Subject and Grade Level */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-4">
                  <div className="space-y-1 md:space-y-2">
                    <label className="block text-xs md:text-sm font-semibold text-gray-700">
                      Subject
                    </label>
                    <select 
                      value={selectedSubject} 
                      onChange={handleSubjectChange} 
                      className="w-full border border-gray-300 rounded-lg px-3 md:px-4 py-2 md:py-3 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 text-sm bg-white hover:border-gray-400 disabled:bg-gray-50 disabled:cursor-not-allowed"
                      disabled={subjects.length === 0}
                    >
                      <option value="">Select Subject</option>
                      {subjects.map((subj: any) => (
                        <option key={subj.subject_id} value={subj.subject_id}>{subj.name}</option>
                      ))}
                    </select>
                  </div>
                  
                  <div className="space-y-1 md:space-y-2">
                    <label className="block text-xs md:text-sm font-semibold text-gray-700">
                      Grade Level
                    </label>
                    <select 
                      value={selectedGradeLevel} 
                      onChange={handleGradeLevelChange} 
                      className="w-full border border-gray-300 rounded-lg px-3 md:px-4 py-2 md:py-3 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 text-sm bg-white hover:border-gray-400 disabled:bg-gray-50 disabled:cursor-not-allowed"
                      disabled={gradeLevels.length === 0}
                    >
                      <option value="">Select Grade Level</option>
                      {gradeLevels.map((grade: any) => (
                        <option key={grade.grade_level_id} value={grade.grade_level_id}>{grade.name}</option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Suggested Topics */}
                <div className="space-y-1 md:space-y-2">
                  <label className="block text-xs md:text-sm font-semibold text-gray-700">Suggested Topics</label>
                  <div className="flex flex-wrap gap-1 md:gap-2">
                    {aiSuggestedTopics.map(topic => (
                      <button
                        type="button"
                        key={topic}
                        className={`px-3 md:px-4 py-2 rounded-full border transition-all duration-200 text-xs md:text-sm font-medium ${
                          selectedTopic === topic 
                            ? 'bg-primary-600 text-white border-primary-600 shadow-lg' 
                            : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100 hover:border-gray-300'
                        }`}
                        onClick={() => handleTopicSelect(topic)}
                      >
                        {topic}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Topic Input */}
                {/* Topic Input and Generate Button Row */}
                <div className="flex flex-col lg:flex-row gap-3 md:gap-4">
                  <div className="flex-1">
                    <div className="flex flex-col lg:flex-row lg:items-center gap-2 lg:gap-4">
                      <label className="block text-xs md:text-sm font-semibold text-gray-700 lg:w-16 lg:flex-shrink-0">
                        Topic
                      </label>
                      <input
                        type="text"
                        name="topic"
                        value={form.topic}
                        onChange={handleChange}
                        placeholder="Enter or select a topic"
                        className="w-full border border-gray-300 rounded-lg px-3 md:px-4 py-2 md:py-3 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 text-sm bg-white hover:border-gray-400"
                      />
                    </div>
                  </div>
                  <div className="w-full lg:w-auto">
                    <button
                      type="button"
                      className="w-full lg:w-auto bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 text-white font-semibold px-8 lg:px-10 py-3 lg:py-4 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-primary-500 focus:ring-opacity-30 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center space-x-3 text-sm lg:text-base"
                      onClick={handleGenerate}
                      disabled={isGenerating}
                    >
                      {isGenerating ? (
                        <>
                          <div className="w-4 h-4 lg:w-5 lg:h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                          <span>Generating...</span>
                        </>
                      ) : (
                        <>
                          <FaComments className="w-4 h-4 lg:w-5 lg:h-5" />
                          <span>Generate Lesson Plan</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>

                

                {error && (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                    <div className="flex items-center justify-center">
                      <div className="w-5 h-5 bg-red-500 rounded-full flex items-center justify-center mr-3">
                        <span className="text-white text-xs font-bold">!</span>
                      </div>
                      <p className="text-red-700 text-sm font-medium">{error}</p>
                    </div>
                  </div>
                )}
              </form>
            </div>
          </div>

          {/* Lesson Resources Section - Hidden on mobile, visible on desktop */}
          <div className="hidden md:block p-2 md:p-4 lg:p-6">
            {/* My Lesson Resources Section */}
            <div className="p-2 md:p-4 lg:p-6">
                              <div className="flex justify-between items-center mb-4">
                  <div className="flex items-center">
                    
                    <h4 className="text-xl lg:text-2xl font-bold text-primary-900">My Lesson Resources</h4>
                  </div>
                <button 
                  className="text-primary-600 hover:text-primary-700 underline font-medium text-sm lg:text-base hover:no-underline"
                  onClick={() => navigate('/lesson-resources')}
                >
                  View All
                </button>
              </div>
              
              {!user && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
                  <p className="text-yellow-800 text-xs lg:text-sm">
                    Please log in to view your lesson resources. 
                    <button 
                      onClick={() => navigate('/login')}
                      className="text-yellow-600 underline ml-1"
                    >
                      Login here
                    </button>
                  </p>
                </div>
              )}

              <div className="relative">
                {lessonResources.length > 0 ? (
                  <>
                    <div className="w-full max-w-5xl mx-auto relative overflow-hidden">
                                            {/* Left Arrow - Hidden on mobile for better UX */}
                      {canScrollLeftState && (
                        <button
                          onClick={() => scrollCarousel('left')}
                          className="hidden md:flex absolute left-0 top-1/2 transform -translate-y-1/2 z-10 w-8 h-8 md:w-10 md:h-10 bg-white border border-gray-200 rounded-full shadow-lg hover:shadow-xl items-center justify-center text-gray-600 hover:text-primary-600 transition-all duration-200 hover:scale-110 focus:outline-none focus:ring-2 focus:ring-primary-500"
                          aria-label="Scroll carousel left"
                        >
                          <FaChevronLeft className="w-3 h-3 md:w-4 md:h-4" />
                        </button>
                      )}
                      
                      {/* Right Arrow - Hidden on mobile for better UX */}
                      {canScrollRightState && (
                        <button
                          onClick={() => scrollCarousel('right')}
                          className="hidden md:flex absolute right-0 top-1/2 transform -translate-y-1/2 z-10 w-8 h-8 md:w-10 md:h-10 bg-white border border-gray-200 rounded-lg shadow-lg hover:shadow-xl items-center justify-center text-gray-600 hover:text-primary-600 transition-all duration-200 hover:scale-110 focus:outline-none focus:ring-2 focus:ring-primary-500"
                          aria-label="Scroll carousel right"
                        >
                          <FaChevronRight className="w-4 h-4" />
                        </button>
                      )}
                      
                      <div 
                        ref={setCarouselRef}
                        className="flex space-x-3 md:space-x-4 overflow-x-auto pb-4 justify-start md:justify-center snap-x snap-mandatory"
                        style={{ 
                          scrollbarWidth: 'none', 
                          msOverflowStyle: 'none',
                          WebkitOverflowScrolling: 'touch',
                          touchAction: 'pan-x',
                          userSelect: 'none',
                          minHeight: '200px'
                        }}
                      >
                        {lessonResources.slice(0, 6).map((resource: any) => {
                          // Parse AI content to get subject, topic, and grade level
                          let subject = 'Subject';
                          let topic = 'Topic';
                          let gradeLevel = 'Grade';
                          
                          try {
                            if (resource.ai_generated_content) {
                              const parsedContent = JSON.parse(resource.ai_generated_content);
                              if (parsedContent.title_header?.subject) {
                                subject = parsedContent.title_header.subject;
                              }
                              if (parsedContent.title_header?.topic) {
                                topic = parsedContent.title_header.topic;
                              }
                              if (parsedContent.title_header?.grade_level) {
                                gradeLevel = parsedContent.title_header.grade_level;
                              }
                            }
                          } catch (e) {
                            // If parsing fails, use default values
                          }
                          
                          return (
                            <div 
                              key={resource.lesson_resources_id} 
                              className="bg-white rounded-xl shadow-md hover:shadow-lg p-3 md:p-4 flex flex-col cursor-pointer transition-all duration-300 border border-gray-100 hover:border-primary-200 flex-shrink-0 w-56 md:w-64 min-w-0 group snap-start"
                              onClick={() => navigate(`/lesson-plans/${resource.lesson_plan_id}/resources/edit`)}
                            >
                              {/* Subject Icon - Centered */}
                              <div className="w-10 h-10 md:w-12 md:h-12 bg-gradient-to-br from-primary-100 to-primary-200 rounded-xl flex items-center justify-center mb-2 md:mb-3 text-lg md:text-xl group-hover:scale-110 transition-transform duration-300 mx-auto">
                                <FaBookOpen className="w-5 h-5 md:w-6 md:h-6 text-primary-600" />
                              </div>
                              
                              {/* Subject */}
                              <div className="text-xs md:text-sm font-semibold text-primary-600 mb-1 text-center">
                                {subject}
                              </div>
                              
                              {/* Topic */}
                              <div className="font-bold text-primary-900 mb-2 text-center line-clamp-2 text-xs md:text-sm leading-tight">
                                {topic}
                              </div>
                              
                              {/* Grade Level */}
                              <div className="text-xs text-primary-700 mb-1 text-center">
                                {gradeLevel}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                    {lessonResources.length > 6 && (
                      <div className="text-center mt-4">
                        <p className="text-sm text-gray-500">
                          Showing 6 of {lessonResources.length} resources
                        </p>
                        <p className="text-xs text-gray-400 mt-1 md:hidden">
                          Swipe left/right to see more resources
                        </p>
                        <div className="flex justify-center mt-2 md:hidden">
                          <div className="w-2 h-2 bg-gray-300 rounded-full mx-1"></div>
                          <div className="w-2 h-2 bg-gray-300 rounded-full mx-1"></div>
                          <div className="w-2 h-2 bg-gray-300 rounded-full mx-1"></div>
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  // Empty state when no lesson resources
                  <div className="text-center py-12">
                    <div className="w-20 h-20 bg-gradient-to-br from-blue-100 to-blue-200 rounded-full flex items-center justify-center mx-auto mb-6">
                      <FaFileAlt className="w-10 h-10 text-blue-600" />
                    </div>
                    <h3 className="text-xl font-semibold text-gray-700 mb-3">No Lesson Resources Yet</h3>
                    <p className="text-gray-500 mb-4">Create lesson plans to generate AI-powered resources</p>
                    <button 
                      onClick={() => navigate('/dashboard')}
                      className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-3 rounded-lg transition-all duration-200 transform hover:scale-105"
                    >
                      Create Lesson Plan
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Mobile Bottom Navigation */}
      <nav className="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 py-3 z-50 shadow-lg">
        <div className="flex justify-around items-center">
          <button 
            className="flex flex-col items-center py-2 px-3 text-primary-600 font-medium transition-colors duration-200"
            onClick={() => navigate('/dashboard')}
          >
            <FaHome className="w-6 h-6 mb-1" />
            <span className="text-xs font-medium">Dashboard</span>
          </button>
          <button 
            className="flex flex-col items-center py-2 px-3 text-gray-500 hover:text-primary-600 font-medium transition-colors duration-200"
            onClick={() => navigate('/lesson-plans')}
          >
            <FaBookOpen className="w-6 h-6 mb-1" />
            <span className="text-xs font-medium">Plans</span>
          </button>
          <button 
            className="flex flex-col items-center py-2 px-3 text-gray-500 hover:text-primary-600 font-medium transition-colors duration-200"
            onClick={() => navigate('/lesson-resources')}
          >
            <FaFolder className="w-6 h-6 mb-1" />
            <span className="text-xs font-medium">Resources</span>
          </button>
          <button 
            className="flex flex-col items-center py-2 px-3 text-gray-500 hover:text-primary-600 font-medium transition-colors duration-200"
            onClick={() => navigate('/dashboard')}
          >
            <FaCog className="w-6 h-6 mb-1" />
            <span className="text-xs font-medium">Settings</span>
          </button>
        </div>
      </nav>
    </div>
  );
};

export default DashboardPage; 