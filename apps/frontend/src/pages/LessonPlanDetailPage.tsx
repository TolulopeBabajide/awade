import React, { useState } from 'react';

const weeks = [
  { week: 1, title: 'Introduction to Family' },
  { week: 2, title: 'Types of Family' },
  { week: 3, title: 'Importance of Family' },
  { week: 4, title: 'Importance of United Family' },
];

const lessonPlan = {
  subject: 'Social Studies',
  plan: '12 Weeks Plan',
  grade: 'Grade 2',
  title: 'Importance of a United Family',
  week: 1,
  weekTitle: 'Introduction to Family',
  objective: 'To introduce pupils to the meaning of family in African Setting',
  tasks: [
    'Define What A Family Is',
    'Give Examples Of Family In African And Western World',
    'Write A Short Note On How Families Are Formed',
  ],
  resources: [
    { name: 'African Family And Values – Segun Onuha', url: '#' },
    { name: 'The Importance Of Love In An African Family – Gyan Asamoah', url: '#' },
  ],
  standards: ['I056-AP-02', 'I056-AP-03', 'I056-AP-04', 'I056-AP-05', 'I056-AP-06'],
  video: { title: 'Introduction to Family', url: '#', duration: '11:20min' },
};

const LessonPlanDetailPage: React.FC = () => {
  const [selectedWeek, setSelectedWeek] = useState(1);
  const selected = weeks.find(w => w.week === selectedWeek) || weeks[0];

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar calendar */}
      <aside className="w-80 bg-white border-r flex flex-col py-8 px-4 min-h-screen">
        <div className="mb-6">
          <button className="text-gray-500 text-sm mb-2 flex items-center">&larr; My Lesson Plans</button>
          <div className="text-lg font-bold mb-2">July</div>
          <div className="flex justify-between text-xs text-gray-400 mb-2">
            <span>Sun</span><span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span>
          </div>
        </div>
        <div className="flex-1 flex flex-col gap-4">
          {weeks.map(w => (
            <button
              key={w.week}
              className={`w-full text-left px-4 py-3 rounded-lg mb-2 font-semibold ${selectedWeek === w.week ? 'bg-orange-200 text-orange-900' : 'bg-gray-100 text-gray-700'}`}
              onClick={() => setSelectedWeek(w.week)}
            >
              Week {w.week}: {w.title}
            </button>
          ))}
        </div>
      </aside>
      {/* Main Content */}
      <main className="flex-1 p-10">
        {/* Breadcrumb */}
        <div className="flex items-center text-sm text-gray-500 mb-4 gap-2">
          <span className="font-bold text-gray-700">Dashboard</span>
          <span>&gt;</span>
          <span className="font-bold text-gray-700">My Lesson Plans</span>
          <span>&gt;</span>
          <span className="font-bold text-orange-700">{lessonPlan.subject}</span>
        </div>
        <div className="flex gap-8">
          {/* Main lesson plan panel */}
          <div className="flex-1 bg-white rounded shadow p-8">
            <div className="flex items-center gap-4 mb-2">
              <span className="font-bold text-lg">{lessonPlan.subject}</span>
              <span className="bg-gray-100 text-gray-700 rounded px-2 py-1 text-xs font-semibold">{lessonPlan.plan}</span>
              <span className="bg-gray-100 text-gray-700 rounded px-2 py-1 text-xs font-semibold">{lessonPlan.grade}</span>
            </div>
            <div className="text-xl font-bold mb-2">{lessonPlan.title}</div>
            <div className="flex items-center gap-2 mb-4">
              <span className="bg-gray-200 text-gray-700 rounded px-2 py-1 text-xs font-semibold">Week {selectedWeek}</span>
              <span className="font-semibold">{selected.title}</span>
            </div>
            <div className="mb-4">
              <div className="font-bold mb-1">Objective</div>
              <div className="text-gray-700 text-sm">{lessonPlan.objective}</div>
            </div>
            <div className="mb-4">
              <div className="font-bold mb-1">Task</div>
              <ul className="list-disc ml-6 text-gray-700 text-sm">
                {lessonPlan.tasks.map((t, i) => <li key={i}>{t}</li>)}
              </ul>
            </div>
            <div className="mb-4">
              <div className="font-bold mb-1">Resources</div>
              <ul className="ml-2 text-gray-700 text-sm">
                {lessonPlan.resources.map((r, i) => (
                  <li key={i} className="flex items-center gap-1">
                    <span className="font-semibold">{r.name}</span>
                    <a href={r.url} target="_blank" rel="noopener noreferrer" className="text-green-600 hover:underline text-xs">↗</a>
                  </li>
                ))}
              </ul>
            </div>
            <div className="flex gap-4 mt-6">
              <button className="bg-gray-200 text-gray-700 font-semibold px-6 py-2 rounded hover:bg-gray-300 flex items-center gap-2">
                ✏️ Edit Plan
              </button>
              <button className="bg-orange-400 text-white font-semibold px-6 py-2 rounded hover:bg-orange-500 flex items-center gap-2">
                📝 Generate Lesson Note
              </button>
            </div>
          </div>
          {/* Right panel: Video and Standards */}
          <div className="w-64 flex flex-col gap-6">
            <div className="bg-white rounded shadow p-4">
              <div className="font-bold mb-2">Videos</div>
              <div className="flex items-center gap-2">
                <span className="bg-red-100 text-red-600 rounded p-2">▶️</span>
                <div>
                  <div className="font-semibold text-sm">{lessonPlan.video.title}</div>
                  <div className="text-xs text-gray-400">{lessonPlan.video.duration}</div>
                </div>
              </div>
            </div>
            <div className="bg-white rounded shadow p-4">
              <div className="font-bold mb-2">Standards</div>
              <ul className="text-xs text-gray-700">
                {lessonPlan.standards.map((s, i) => <li key={i}>{s}</li>)}
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default LessonPlanDetailPage; 