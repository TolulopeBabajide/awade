import React, { useState } from 'react';

const initialData = {
  topic: 'Introduction to Family',
  objectives: ['To introduce pupils to the meaning of family in African Setting'],
  tasks: [
    'Define What A Family Is',
    'Give Examples Of Family In African And Western World',
    'Write A Short Note On How Families Are Formed',
  ],
  resources: [
    'African Family And Values – Segun Onuha',
    'The Importance Of Love In An African Family – Gyan Asamoah',
  ],
};

const EditLessonPlanPage: React.FC = () => {
  const [topic, setTopic] = useState(initialData.topic);
  const [objectives, setObjectives] = useState(initialData.objectives);
  const [tasks, setTasks] = useState(initialData.tasks);
  const [resources, setResources] = useState(initialData.resources);
  const [newTask, setNewTask] = useState('');
  const [newResource, setNewResource] = useState('');

  const handleAddTask = () => {
    if (newTask.trim()) {
      setTasks([...tasks, newTask.trim()]);
      setNewTask('');
    }
  };
  const handleRemoveTask = (idx: number) => {
    setTasks(tasks.filter((_, i) => i !== idx));
  };
  const handleAddResource = () => {
    if (newResource.trim()) {
      setResources([...resources, newResource.trim()]);
      setNewResource('');
    }
  };
  const handleRemoveResource = (idx: number) => {
    setResources(resources.filter((_, i) => i !== idx));
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white rounded shadow-lg p-8 w-full max-w-2xl relative">
        {/* Close button */}
        <button className="absolute left-4 top-4 text-2xl text-red-500 hover:text-red-700">✖️</button>
        <h2 className="text-xl font-bold text-center mb-6">Edit Lesson Plan Week 1</h2>
        {/* Topic */}
        <div className="mb-4">
          <label className="block font-bold mb-1">Topic</label>
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={topic}
              onChange={e => setTopic(e.target.value)}
              className="w-full border rounded px-3 py-2"
            />
            <span className="text-orange-400 text-xl cursor-pointer" title="AI Suggestion">🤖</span>
          </div>
        </div>
        {/* Objectives */}
        <div className="mb-4">
          <label className="block font-bold mb-1">Objectives</label>
          <div className="flex items-center gap-2 mb-2">
            <input
              type="text"
              value={objectives[0]}
              onChange={e => setObjectives([e.target.value])}
              className="w-full border rounded px-3 py-2"
            />
            <span className="text-orange-400 text-xl cursor-pointer" title="AI Suggestion">🤖</span>
          </div>
        </div>
        {/* Tasks */}
        <div className="mb-4">
          <label className="block font-bold mb-1">Task</label>
          <ul className="mb-2">
            {tasks.map((task, idx) => (
              <li key={idx} className="flex items-center gap-2 mb-1">
                <span className="flex-1">{task}</span>
                <button className="text-red-400 hover:text-red-700 text-lg" onClick={() => handleRemoveTask(idx)} title="Remove">🗑️</button>
              </li>
            ))}
          </ul>
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={newTask}
              onChange={e => setNewTask(e.target.value)}
              className="w-full border rounded px-3 py-2"
              placeholder="Add new task"
            />
            <button className="bg-orange-400 text-white px-3 py-1 rounded" onClick={handleAddTask} type="button">+</button>
            <span className="text-orange-400 text-xl cursor-pointer" title="AI Suggestion">🤖</span>
          </div>
        </div>
        {/* Resources */}
        <div className="mb-4">
          <label className="block font-bold mb-1">Resources</label>
          <ul className="mb-2">
            {resources.map((res, idx) => (
              <li key={idx} className="flex items-center gap-2 mb-1">
                <span className="flex-1">{res}</span>
                <button className="text-red-400 hover:text-red-700 text-lg" onClick={() => handleRemoveResource(idx)} title="Remove">🗑️</button>
              </li>
            ))}
          </ul>
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={newResource}
              onChange={e => setNewResource(e.target.value)}
              className="w-full border rounded px-3 py-2"
              placeholder="Add new resource"
            />
            <button className="bg-green-400 text-white px-3 py-1 rounded" onClick={handleAddResource} type="button">⬇️</button>
          </div>
        </div>
        {/* Save Button */}
        <button className="w-full bg-orange-400 text-white font-bold py-3 rounded text-lg mt-6 hover:bg-orange-500">Save</button>
      </div>
    </div>
  );
};

export default EditLessonPlanPage; 