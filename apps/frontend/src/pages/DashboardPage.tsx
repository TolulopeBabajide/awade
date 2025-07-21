import React, { useState } from 'react';

const subjects = ['Mathematics', 'Biology', 'Social Studies', 'Inter.Science'];
const grades = ['Grade 1', 'Grade 2', 'Grade 3', 'Grade 4', 'Grade 5', 'Grade 6', 'Grade 7', 'Grade 8'];
const countries = ['Nigeria', 'Ghana', 'Kenya', 'South Africa'];
const languages = ['English', 'French', 'Swahili'];
const teachingStyles = ['Lesson', 'Project', 'Discussion'];
const aiSuggestedTopics = ['Fractions', 'Geometry', 'Measurements', 'Algebra', 'Simultaneous Equations'];

const DashboardPage: React.FC = () => {
  const [form, setForm] = useState({
    subject: subjects[0],
    grade: grades[1],
    teachingStyle: teachingStyles[0],
    language: languages[0],
    country: countries[0],
    topic: '',
    weeks: '',
    classPerWeek: '',
    description: '',
  });
  const [selectedTopic, setSelectedTopic] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleTopicSelect = (topic: string) => {
    setSelectedTopic(topic);
    setForm({ ...form, topic });
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r flex flex-col py-8 px-4 min-h-screen">
        <div className="flex items-center mb-8">
          <div className="w-10 h-10 bg-green-200 rounded-full flex items-center justify-center mr-2">
            <span className="text-2xl font-bold text-green-700">O</span>
          </div>
          <span className="font-bold text-xl tracking-widest">AWADE</span>
        </div>
        <nav className="flex-1 space-y-2">
          <button className="w-full text-left px-4 py-2 rounded bg-orange-100 text-orange-700 font-semibold">Dashboard</button>
          <button className="w-full text-left px-4 py-2 rounded hover:bg-gray-100">Lesson Plans</button>
          <button className="w-full text-left px-4 py-2 rounded hover:bg-gray-100">Resources</button>
          <button className="w-full text-left px-4 py-2 rounded hover:bg-gray-100">Messages</button>
          <button className="w-full text-left px-4 py-2 rounded hover:bg-gray-100">Support</button>
          <button className="w-full text-left px-4 py-2 rounded hover:bg-gray-100">Settings</button>
        </nav>
        <button className="mt-8 text-left px-4 py-2 text-red-500 hover:underline">Log out</button>
      </aside>
      {/* Main Content */}
      <main className="flex-1 p-10">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
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
        <div className="bg-white rounded shadow p-8 mb-10">
          <h3 className="text-lg font-bold mb-4">Create Lesson Plan</h3>
          <form className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-semibold mb-1">Subject</label>
              <select name="subject" value={form.subject} onChange={handleChange} className="w-full border rounded px-3 py-2">
                {subjects.map(subj => <option key={subj}>{subj}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold mb-1">Grade Level</label>
              <select name="grade" value={form.grade} onChange={handleChange} className="w-full border rounded px-3 py-2">
                {grades.map(grade => <option key={grade}>{grade}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold mb-1">Teaching Style</label>
              <select name="teachingStyle" value={form.teachingStyle} onChange={handleChange} className="w-full border rounded px-3 py-2">
                {teachingStyles.map(style => <option key={style}>{style}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold mb-1">Language</label>
              <select name="language" value={form.language} onChange={handleChange} className="w-full border rounded px-3 py-2">
                {languages.map(lang => <option key={lang}>{lang}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold mb-1">Country</label>
              <select name="country" value={form.country} onChange={handleChange} className="w-full border rounded px-3 py-2">
                {countries.map(country => <option key={country}>{country}</option>)}
              </select>
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-semibold mb-1">AI Suggested Topics</label>
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
            <div>
              <label className="block text-sm font-semibold mb-1">Generate Lesson curriculum by</label>
              <select name="by" className="w-full border rounded px-3 py-2">
                <option>Weeks</option>
                <option>Months</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold mb-1">Number of Weeks</label>
              <input
                type="number"
                name="weeks"
                value={form.weeks}
                onChange={handleChange}
                className="w-full border rounded px-3 py-2"
                placeholder="12"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-1">Class Number per Week</label>
              <input
                type="number"
                name="classPerWeek"
                value={form.classPerWeek}
                onChange={handleChange}
                className="w-full border rounded px-3 py-2"
                placeholder="3"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-semibold mb-1">Description</label>
              <textarea
                name="description"
                value={form.description}
                onChange={handleChange}
                className="w-full border rounded px-3 py-2"
                placeholder="e.g. Understanding how numbers progress arithmetically"
                rows={2}
              />
            </div>
            <div className="md:col-span-2 flex justify-end">
              <button type="button" className="bg-orange-400 text-white font-semibold px-8 py-2 rounded hover:bg-orange-500">
                Generate
              </button>
            </div>
          </form>
        </div>
        {/* My Lesson Plans Section */}
        <div>
          <div className="flex justify-between items-center mb-4">
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
      </main>
    </div>
  );
};

export default DashboardPage; 