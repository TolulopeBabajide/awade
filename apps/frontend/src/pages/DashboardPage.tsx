import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  FaBookOpen,
  FaComments,
  FaSignOutAlt,
  FaUser,
  FaFileAlt,
  FaChevronLeft,
  FaChevronRight
} from 'react-icons/fa';
import Sidebar from '../components/Sidebar';
import MobileNavigation from '../components/MobileNavigation';
import { sanitizeInput } from '../utils/sanitizer';
import { parseResourceContent } from '../utils/subjectIcons';
import {
  useCountries,
  useCurriculums,
  useCurriculumStructures,
  useSubjects,
  useGradeLevels,
  useTopics,
  useAllLessonResources,
  useGenerateLessonPlan,
} from '../hooks/useEducatorData';

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  // ── Selection state ──────────────────────────────────────────
  const [selectedCountry, setSelectedCountry] = useState<string>('');
  const [selectedCurriculum, setSelectedCurriculum] = useState<string>('');
  const [selectedSubject, setSelectedSubject] = useState<string>('');
  const [selectedGradeLevel, setSelectedGradeLevel] = useState<string>('');
  const [selectedTopic, setSelectedTopic] = useState('');
  const [form, setForm] = useState({ topic: '' });

  // ── UI state ─────────────────────────────────────────────────
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [error, setError] = useState<string>('');
  const [carouselRef, setCarouselRef] = useState<HTMLDivElement | null>(null);
  const [canScrollLeftState, setCanScrollLeftState] = useState(false);
  const [canScrollRightState, setCanScrollRightState] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  // ── React Query hooks ────────────────────────────────────────
  const { data: countries = [] } = useCountries();
  const { data: curriculums = [] } = useCurriculums(
    selectedCountry ? parseInt(selectedCountry) : null
  );
  const { data: structures = [] } = useCurriculumStructures(
    selectedCurriculum ? parseInt(selectedCurriculum) : null
  );
  const { data: allSubjects = [] } = useSubjects();
  const { data: allGradeLevels = [] } = useGradeLevels();
  const { data: lessonResources = [] } = useAllLessonResources();

  // Derive filtered subjects & grade levels from structures
  const subjects = useMemo(() => {
    if (!structures.length || !allSubjects.length) return [];
    const subjectIds = new Set(structures.map((s: any) => s.subject_id));
    return allSubjects.filter((s: any) => subjectIds.has(s.subject_id));
  }, [structures, allSubjects]);

  const gradeLevels = useMemo(() => {
    if (!structures.length || !allGradeLevels.length) return [];
    const gradeIds = new Set(structures.map((s: any) => s.grade_level_id));
    return allGradeLevels.filter((g: any) => gradeIds.has(g.grade_level_id));
  }, [structures, allGradeLevels]);

  // Find the matching curriculum structure ID for topics query
  const matchingStructureId = useMemo(() => {
    if (!selectedSubject || !selectedGradeLevel || !structures.length) return null;
    const match = structures.find(
      (s: any) =>
        s.subject_id === parseInt(selectedSubject) &&
        s.grade_level_id === parseInt(selectedGradeLevel)
    );
    return match?.curriculum_structure_id ?? null;
  }, [selectedSubject, selectedGradeLevel, structures]);

  const { data: topics = [] } = useTopics(matchingStructureId);

  // ── Derived data ─────────────────────────────────────────────
  const [filteredTopics, setFilteredTopics] = useState<any[]>([]);
  const suggestedTopics = useMemo(() => {
    if (!topics.length) return [];
    const shuffled = [...topics].sort(() => 0.5 - Math.random());
    return shuffled.slice(0, Math.min(3, topics.length));
  }, [topics]);

  // Sync filtered topics when topics change
  useEffect(() => {
    setFilteredTopics(topics);
    setSelectedTopic('');
    setForm({ topic: '' });
  }, [topics]);

  // Generate mutation
  const generateMutation = useGenerateLessonPlan();

  // ── Cascade resets ───────────────────────────────────────────
  useEffect(() => {
    setSelectedCurriculum('');
    setSelectedSubject('');
    setSelectedGradeLevel('');
  }, [selectedCountry]);

  useEffect(() => {
    setSelectedSubject('');
    setSelectedGradeLevel('');
  }, [selectedCurriculum]);

  // ── Carousel scroll ──────────────────────────────────────────
  useEffect(() => {
    const handleScroll = () => {
      if (carouselRef) {
        setCanScrollLeftState(carouselRef.scrollLeft > 0);
        setCanScrollRightState(carouselRef.scrollLeft < (carouselRef.scrollWidth - carouselRef.clientWidth));
      }
    };
    if (carouselRef) {
      carouselRef.addEventListener('scroll', handleScroll);
      handleScroll();
      return () => carouselRef.removeEventListener('scroll', handleScroll);
    }
  }, [carouselRef]);

  // ── Click outside user menu ──────────────────────────────────
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (showUserMenu && !(event.target as Element).closest('.user-menu-container')) {
        setShowUserMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showUserMenu]);

  // ── Handlers ─────────────────────────────────────────────────
  const handleTopicSelect = (topic: string) => {
    setSelectedTopic(topic);
    setForm({ topic });
  };

  const filterTopics = (input: string) => {
    if (!input.trim()) {
      setFilteredTopics(topics);
      return;
    }
    setFilteredTopics(
      topics.filter((t: any) => t.topic_title.toLowerCase().includes(input.toLowerCase()))
    );
  };

  const handleTopicInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setForm({ topic: value });
    filterTopics(value);
    setIsDropdownOpen(true);
  };

  const handleTopicSelectFromDropdown = (topicTitle: string) => {
    setForm({ topic: topicTitle });
    setSelectedTopic(topicTitle);
    setIsDropdownOpen(false);
    setFilteredTopics(topics);
  };

  const handleGenerate = async () => {
    if (!selectedCountry || !selectedCurriculum || !selectedSubject || !selectedGradeLevel) {
      setError('Please select all required fields');
      return;
    }
    if (!form.topic.trim()) {
      setError('Please enter or select a topic');
      return;
    }

    setError('');

    const subjectName = subjects.find((s: any) => s.subject_id === parseInt(selectedSubject))?.name || '';
    const gradeLevelName = gradeLevels.find((g: any) => g.grade_level_id === parseInt(selectedGradeLevel))?.name || '';

    if (!subjectName || !gradeLevelName) {
      setError('Invalid subject or grade level selection. Please try again.');
      return;
    }

    try {
      const data = await generateMutation.mutateAsync({
        subject: subjectName,
        grade_level: gradeLevelName,
        topic: sanitizeInput(form.topic),
        user_id: user?.user_id,
      });
      if (data) {
        navigate(`/lesson-plans/${data.lesson_id}`, { state: { lessonPlanData: data } });
      }
    } catch (err: any) {
      setError(err.message || 'Failed to generate lesson plan. Please try again.');
    }
  };

  const scrollCarousel = (direction: 'left' | 'right') => {
    if (!carouselRef) return;
    const scrollAmount = 240;
    const target =
      direction === 'left'
        ? Math.max(0, carouselRef.scrollLeft - scrollAmount)
        : Math.min(carouselRef.scrollWidth - carouselRef.clientWidth, carouselRef.scrollLeft + scrollAmount);
    carouselRef.scrollTo({ left: target, behavior: 'smooth' });
  };

  const isGenerating = generateMutation.isPending;

  return (
    <div className="bg-gray-50 flex min-h-screen w-full overflow-x-hidden">
      {/* Sidebar */}
      <Sidebar currentPage="dashboard" />

      {/* Main Content */}
      <main className="flex-1 lg:ml-64 p-4 md:p-6 lg:p-8 pb-20 lg:pb-8 w-full max-w-full overflow-x-hidden">
        {/* Header */}
        <div className="flex justify-between items-start pt-0 pb-2 md:pb-4 lg:pb-5 px-2 md:px-4 lg:px-5 gap-2 md:gap-4 flex-shrink-0 w-full max-w-full">
          {/* Left Side - Welcome Message */}
          <div className="flex-1 min-w-0">
            <div className="text-left">
              <h2 className="text-xl md:text-2xl lg:text-3xl xl:text-4xl font-bold mb-1 md:mb-2 text-gray-900 mt-0 pt-0 truncate">Welcome, {user?.full_name || 'User'}</h2>
              <p className="text-sm md:text-base lg:text-lg text-gray-600 break-words">Create teaching resources relevant to your classroom.</p>
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

              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
                  <div className="px-4 py-3 border-b border-gray-100">
                    <div className="font-semibold text-sm text-gray-900 truncate">{user?.full_name || 'User'}</div>
                    <div className="text-xs text-gray-500 truncate">{user?.role || 'Educator'}</div>
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
              <div className="font-semibold text-xs md:text-sm text-gray-900 truncate max-w-[100px]">{user?.full_name || 'User'}</div>
              <div className="text-xs text-gray-500 truncate max-w-[100px]">{user?.role || 'Educator'}</div>
            </div>
          </div>
        </div>

        {/* Dashboard Content */}
        <div className="flex flex-col flex-1 overflow-y-auto w-full max-w-full overflow-x-hidden">
          {/* Create Lesson Plan Section */}
          <div className="p-2 md:p-4 lg:p-6">
            <div className="p-3 md:p-4 lg:p-5">
              <div className="flex items-center mb-3 md:mb-4">
                <h3 className="text-lg md:text-xl lg:text-2xl font-bold text-gray-900">
                  Create Lesson Plan
                </h3>
              </div>

              <form className="space-y-3 md:space-y-4 mb-6 md:mb-0 w-full max-w-full">
                {/* First Row - Country and Curriculum */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-4 min-w-0">
                  <div className="space-y-1 md:space-y-2 min-w-0">
                    <label className="block text-xs md:text-sm font-semibold text-gray-700">Country</label>
                    <select
                      value={selectedCountry}
                      onChange={(e) => setSelectedCountry(e.target.value)}
                      className="w-full max-w-full border border-gray-300 rounded-lg px-3 md:px-4 py-2 md:py-3 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 text-sm bg-white hover:border-gray-400 truncate pr-8"
                    >
                      <option value="">Select Country</option>
                      {countries.map((country: any) => (
                        <option key={country.country_id} value={country.country_id} className="truncate">{country.country_name}</option>
                      ))}
                    </select>
                  </div>

                  <div className="space-y-1 md:space-y-2 min-w-0">
                    <label className="block text-xs md:text-sm font-semibold text-gray-700">Curriculum</label>
                    <select
                      value={selectedCurriculum}
                      onChange={(e) => setSelectedCurriculum(e.target.value)}
                      className="w-full max-w-full border border-gray-300 rounded-lg px-3 md:px-4 py-2 md:py-3 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 text-sm bg-white hover:border-gray-400 truncate pr-8"
                    >
                      <option value="">Select Curriculum</option>
                      {curriculums.map((curr: any) => (
                        <option key={curr.curricula_id} value={curr.curricula_id} className="truncate">
                          {curr.curricula_title}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Second Row - Subject and Grade Level */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-4 min-w-0">
                  <div className="space-y-1 md:space-y-2 min-w-0">
                    <label className="block text-xs md:text-sm font-semibold text-gray-700">Subject</label>
                    <select
                      value={selectedSubject}
                      onChange={(e) => setSelectedSubject(e.target.value)}
                      className="w-full max-w-full border border-gray-300 rounded-lg px-3 md:px-4 py-2 md:py-3 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 text-sm bg-white hover:border-gray-400 disabled:bg-gray-50 disabled:cursor-not-allowed truncate pr-8"
                      disabled={subjects.length === 0}
                    >
                      <option value="">Select Subject</option>
                      {subjects.map((subj: any) => (
                        <option key={subj.subject_id} value={subj.subject_id} className="truncate">{subj.name}</option>
                      ))}
                    </select>
                  </div>

                  <div className="space-y-1 md:space-y-2 min-w-0">
                    <label className="block text-xs md:text-sm font-semibold text-gray-700">Grade Level</label>
                    <select
                      value={selectedGradeLevel}
                      onChange={(e) => setSelectedGradeLevel(e.target.value)}
                      className="w-full max-w-full border border-gray-300 rounded-lg px-3 md:px-4 py-2 md:py-3 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 text-sm bg-white hover:border-gray-400 disabled:bg-gray-50 disabled:cursor-not-allowed truncate pr-8"
                      disabled={gradeLevels.length === 0}
                    >
                      <option value="">Select Grade Level</option>
                      {gradeLevels.map((grade: any) => (
                        <option key={grade.grade_level_id} value={grade.grade_level_id} className="truncate">{grade.name}</option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Suggested Topics */}
                <div className="space-y-2 md:space-y-3 w-full max-w-full">
                  <label className="block text-xs md:text-sm font-semibold text-gray-700">
                    Suggested Topics
                    {suggestedTopics.length > 0 && (
                      <span className="ml-2 text-xs text-gray-500 font-normal">
                        (try these {suggestedTopics.length} topics)
                      </span>
                    )}
                  </label>
                  {suggestedTopics.length > 0 ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 md:gap-3 w-full">
                      {suggestedTopics.map((topic: any) => (
                        <button
                          type="button"
                          key={topic.topic_id}
                          className={`w-full px-3 md:px-4 py-2 md:py-3 rounded-lg border transition-all duration-200 text-xs md:text-sm font-medium text-center hover:shadow-md break-words h-auto min-h-[40px] ${selectedTopic === topic.topic_title
                            ? 'bg-primary-600 text-white border-primary-600 shadow-lg'
                            : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100 hover:border-gray-300'
                            }`}
                          onClick={() => handleTopicSelect(topic.topic_title)}
                        >
                          {topic.topic_title}
                        </button>
                      ))}
                    </div>
                  ) : (
                    <div className="text-sm text-gray-500 italic p-3 bg-gray-50 rounded-lg border border-gray-100 w-full break-words">
                      {selectedSubject && selectedGradeLevel
                        ? 'Select a topic from the list below or enter your own'
                        : 'Select a subject and grade level to see suggested topics'
                      }
                    </div>
                  )}
                </div>

                {/* Topic Input and Generate Button Row */}
                <div className="flex flex-col lg:flex-row gap-3 md:gap-4 w-full max-w-full">
                  <div className="flex-1 min-w-0">
                    <div className="space-y-2 md:space-y-3">
                      <label className="block text-xs md:text-sm font-semibold text-gray-700">Topic</label>
                      <div className="relative w-full">
                        <input
                          type="text"
                          name="topic"
                          value={form.topic}
                          onChange={handleTopicInputChange}
                          onFocus={() => { setIsDropdownOpen(true); setFilteredTopics(topics); }}
                          onBlur={() => setTimeout(() => setIsDropdownOpen(false), 200)}
                          placeholder="Enter or select a topic"
                          className="w-full max-w-full border border-gray-300 rounded-lg px-3 md:px-4 py-2 md:py-3 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 text-sm bg-white hover:border-gray-400 pr-8"
                        />
                        <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                          <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                          </svg>
                        </div>

                        {isDropdownOpen && filteredTopics.length > 0 && (
                          <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                            {filteredTopics.map((topic: any) => (
                              <button
                                key={topic.topic_id}
                                type="button"
                                className="w-full text-left px-3 md:px-4 py-2 md:py-3 hover:bg-gray-50 focus:bg-gray-50 focus:outline-none text-sm border-b border-gray-100 last:border-b-0 transition-colors duration-150 truncate"
                                onClick={() => handleTopicSelectFromDropdown(topic.topic_title)}
                              >
                                {topic.topic_title}
                              </button>
                            ))}
                          </div>
                        )}

                        {isDropdownOpen && form.topic.trim() && filteredTopics.length === 0 && (
                          <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg">
                            <div className="px-3 md:px-4 py-2 md:py-3 text-sm text-gray-500 text-center break-words">
                              No topics found matching "{form.topic}"
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="w-full lg:w-auto">
                    <div>
                      <div className="h-6 hidden lg:block"></div>
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
                </div>

                {error && (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg w-full">
                    <div className="flex items-center justify-center">
                      <div className="w-5 h-5 bg-red-500 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                        <span className="text-white text-xs font-bold">!</span>
                      </div>
                      <p className="text-red-700 text-sm font-medium break-words">{error}</p>
                    </div>
                  </div>
                )}
              </form>
            </div>
          </div>

          {/* Lesson Resources Section */}
          <div className="block p-2 md:p-4 lg:p-6">
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
                    <button onClick={() => navigate('/login')} className="text-yellow-600 underline ml-1">Login here</button>
                  </p>
                </div>
              )}

              <div className="relative">
                {lessonResources.length > 0 ? (
                  <>
                    <div className="w-full max-w-5xl mx-auto relative overflow-hidden">
                      {canScrollLeftState && (
                        <button
                          onClick={() => scrollCarousel('left')}
                          className="hidden md:flex absolute left-0 top-1/2 transform -translate-y-1/2 z-10 w-8 h-8 md:w-10 md:h-10 bg-white border border-gray-200 rounded-full shadow-lg hover:shadow-xl items-center justify-center text-gray-600 hover:text-primary-600 transition-all duration-200 hover:scale-110 focus:outline-none focus:ring-2 focus:ring-primary-500"
                          aria-label="Scroll carousel left"
                        >
                          <FaChevronLeft className="w-3 h-3 md:w-4 md:h-4" />
                        </button>
                      )}

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
                          minHeight: '200px',
                          paddingRight: '1rem'
                        }}
                      >
                        {lessonResources.slice(0, 6).map((resource: any) => {
                          const { subject, topic, gradeLevel } = parseResourceContent(resource);

                          return (
                            <div
                              key={resource.lesson_resources_id}
                              className="bg-white rounded-xl shadow-md hover:shadow-lg p-3 md:p-4 flex flex-col cursor-pointer transition-all duration-300 border border-gray-100 hover:border-primary-200 flex-shrink-0 w-56 md:w-64 min-w-0 group snap-start"
                              onClick={() => navigate(`/lesson-plans/${resource.lesson_plan_id}/resources/edit`)}
                            >
                              <div className="w-10 h-10 md:w-12 md:h-12 bg-gradient-to-br from-primary-100 to-primary-200 rounded-xl flex items-center justify-center mb-2 md:mb-3 text-lg md:text-xl group-hover:scale-110 transition-transform duration-300 mx-auto">
                                <FaBookOpen className="w-5 h-5 md:w-6 md:h-6 text-primary-600" />
                              </div>
                              <div className="text-xs md:text-sm font-semibold text-primary-600 mb-1 text-center">{subject}</div>
                              <div className="font-bold text-primary-900 mb-2 text-center line-clamp-2 text-xs md:text-sm leading-tight">{topic}</div>
                              <div className="text-xs text-primary-700 mb-1 text-center">{gradeLevel}</div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                    {lessonResources.length > 6 && (
                      <div className="text-center mt-4">
                        <p className="text-sm text-gray-500">Showing 6 of {lessonResources.length} resources</p>
                        <p className="text-xs text-gray-400 mt-1 md:hidden">Swipe left/right to see more resources</p>
                        <div className="flex justify-center mt-2 md:hidden">
                          <div className="w-2 h-2 bg-gray-300 rounded-full mx-1"></div>
                          <div className="w-2 h-2 bg-gray-300 rounded-full mx-1"></div>
                          <div className="w-2 h-2 bg-gray-300 rounded-full mx-1"></div>
                        </div>
                      </div>
                    )}
                  </>
                ) : (
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
      <MobileNavigation />
    </div>
  );
};

export default DashboardPage;
