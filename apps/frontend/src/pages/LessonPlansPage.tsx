import React from 'react';

const lessonPlans = [
  {
    subject: 'Social Studies',
    topic: 'Importance of United Family',
    grade: 'Grade 2',
    weeks: '12 Weeks Plan',
    icon: '🧑‍🏫',
  },
  {
    subject: 'Biology',
    topic: 'Photosynthesis',
    grade: 'Grade 3',
    weeks: '4 Weeks Plan',
    icon: '🧪',
  },
  {
    subject: 'Biology',
    topic: 'Human Skeletal System',
    grade: 'Grade 6',
    weeks: '2 Weeks Plan',
    icon: '🧪',
  },
  {
    subject: 'Inter.Science',
    topic: 'Health, Safety & Environment',
    grade: 'Grade 3',
    weeks: '7 Weeks Plan',
    icon: '⚗️',
  },
  {
    subject: 'Biology',
    topic: 'Reproduction In Mammals',
    grade: 'Grade 8',
    weeks: '3 Weeks Plan',
    icon: '🧪',
  },
  {
    subject: 'Inter.Science',
    topic: 'Health, Safety & Environment',
    grade: 'Grade 3',
    weeks: '7 Weeks Plan',
    icon: '⚗️',
  },
];

const LessonPlansPage: React.FC = () => {
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
          <button className="w-full text-left px-4 py-2 rounded hover:bg-gray-100">Dashboard</button>
          <button className="w-full text-left px-4 py-2 rounded bg-orange-100 text-orange-700 font-semibold">Lesson Plans</button>
          <button className="w-full text-left px-4 py-2 rounded hover:bg-gray-100">Resources</button>
          <button className="w-full text-left px-4 py-2 rounded hover:bg-gray-100">Messages <span className="ml-2 bg-green-100 text-green-700 rounded-full px-2 text-xs">0</span></button>
          <button className="w-full text-left px-4 py-2 rounded hover:bg-gray-100">Support</button>
          <button className="w-full text-left px-4 py-2 rounded hover:bg-gray-100">Settings</button>
        </nav>
        <button className="mt-8 text-left px-4 py-2 text-red-500 hover:underline">Log out</button>
      </aside>
      {/* Main Content */}
      <main className="flex-1 p-10">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-2xl font-bold">My Lesson Plans</h2>
          <button className="bg-orange-200 text-orange-900 font-semibold px-6 py-2 rounded flex items-center gap-2 hover:bg-orange-300">
            <span className="text-xl">📝</span> Create Lesson Plan
          </button>
        </div>
        {/* Lesson Plans Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3 gap-6">
          {lessonPlans.map((plan, idx) => (
            <div key={idx} className="bg-white rounded shadow p-6 flex flex-col items-center relative">
              <div className="w-14 h-14 bg-green-100 rounded-full flex items-center justify-center mb-2 text-3xl">
                {plan.icon}
              </div>
              <div className="font-bold text-lg mb-1 text-center">{plan.subject}</div>
              <div className="font-semibold text-sm mb-1 text-center">{plan.topic}</div>
              <div className="text-xs text-gray-500 mb-1 text-center">{plan.grade}</div>
              <div className="text-xs text-gray-400 mb-2 text-center">{plan.weeks}</div>
              <div className="absolute bottom-2 right-2 flex gap-2">
                <button className="text-gray-400 hover:text-gray-700" title="Edit"><span className="text-lg">✏️</span></button>
                <button className="text-red-400 hover:text-red-700" title="Delete"><span className="text-lg">🗑️</span></button>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
};

export default LessonPlansPage; 