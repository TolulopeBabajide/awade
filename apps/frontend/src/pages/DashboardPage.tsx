import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const teachingStyles = ['Lesson', 'Project', 'Discussion'];
const languages = ['English', 'French', 'Swahili'];
const aiSuggestedTopics = ['Fractions', 'Geometry', 'Measurements', 'Algebra', 'Simultaneous Equations'];

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
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

  // Fetch countries on mount
  useEffect(() => {
    fetch('/api/countries/')
      .then(res => res.json())
      .then(setCountries);
  }, []);

  // Fetch curriculums when country changes
  useEffect(() => {
    if (selectedCountry) {
      fetch(`/api/curriculum?country_id=${selectedCountry}`)
        .then(res => res.json())
        .then(setCurriculums);
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
      // Fetch subjects for the selected curriculum
      fetch(`/api/curriculum-structures?curricula_id=${selectedCurriculum}`)
        .then(res => res.json())
        .then(structures => {
          // Extract unique subject and grade level IDs
          const subjectIds = Array.from(new Set(structures.map((s: any) => s.subject_id)));
          const gradeLevelIds = Array.from(new Set(structures.map((s: any) => s.grade_level_id)));

          // Fetch subject details
          Promise.all([
            fetch('/api/subjects/').then(res => res.json()),
            fetch('/api/grade-levels/').then(res => res.json())
          ]).then(([allSubjects, allGrades]) => {
            setSubjects(allSubjects.filter((s: any) => subjectIds.includes(s.subject_id)));
            setGradeLevels(allGrades.filter((g: any) => gradeLevelIds.includes(g.grade_level_id)));
            setSelectedSubject('');
            setSelectedGradeLevel('');
          });
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
        user_id: 1, // TODO: Get from authentication context
      };

      const response = await fetch('/api/lesson-plans/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Navigate to lesson plan detail page with the generated data
      navigate(`/lesson-plans/${data.lesson_id}`, { 
        state: { lessonPlanData: data } 
      });
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
        <button className="mt-8 text-left px-4 py-2 text-red-500 hover:underline hidden md:block">Log out</button>
      </aside>
      {/* Main Content */}
      <main className="flex-1 p-4 md:p-10">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-center mb-8 gap-4">
          <div className="text-center md:text-left">
            <h2 className="text-2xl font-bold mb-1">Welcome, Ada</h2>
            <p className="text-gray-500">Generate Lesson plans tailored towards your African Classroom.</p>
          </div>
          <div className="flex items-center space-x-2 bg-white px-4 py-2 rounded shadow">
            <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
              <span className="text-lg font-bold text-gray-700">A</span>
            </div>
            <div>
              <div className="font-semibold text-sm">Ada, Oljude</div>
              <div className="text-xs text-gray-500">Educator</div>
            </div>
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
            <button className="text-orange-600 underline">View All</button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {/* Placeholder cards */}
            {[1,2,3,4,5].map(i => (
              <div key={i} className="bg-white rounded shadow p-4 flex flex-col items-center">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-2">
                  <span className="text-2xl">{i % 2 === 0 ? '🧪' : '📚'}</span>
                </div>
                <div className="font-semibold mb-1">{i % 2 === 0 ? 'Biology' : 'Social Studies'}</div>
                <div className="text-xs text-gray-500 mb-1">{i % 2 === 0 ? 'Grade 6' : 'Grade 2'}</div>
                <div className="text-xs text-gray-400 mb-2">{i % 2 === 0 ? '2 Weeks Plan' : '12 Weeks Plan'}</div>
                <div className="text-xs text-gray-600 text-center">{i % 2 === 0 ? 'Human Skeletal System' : 'Importance of United Family'}</div>
              </div>
            ))}
          </div>
        </div>
        {/* My Lesson Notes Section */}
        <div className="mt-10">
          <div className="flex flex-col md:flex-row justify-between items-center mb-4 gap-2 md:gap-0">
            <h4 className="text-lg font-bold">My Lesson Resources</h4>
            <button className="text-orange-600 underline">View All</button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {/* Placeholder cards for lesson resources */}
            {[1,2,3,4,5].map(i => (
              <div key={i} className="bg-white rounded shadow p-4 flex flex-col items-center">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-2">
                  <span className="text-2xl">{i % 2 === 0 ? '📄' : '🔗'}</span>
                </div>
                <div className="font-semibold mb-1">{i % 2 === 0 ? 'Fractions Resource' : 'Geometry Resource'}</div>
                <div className="text-xs text-gray-500 mb-1">{i % 2 === 0 ? 'PDF' : 'Link'}</div>
                <div className="text-xs text-gray-400 mb-2">{i % 2 === 0 ? 'Uploaded' : 'Generated'}</div>
                <div className="text-xs text-gray-600 text-center">{i % 2 === 0 ? 'Fraction Worksheets' : 'Geometry Video'}</div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
};

export default DashboardPage; 