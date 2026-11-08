import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { FaArrowRight, FaBookOpen } from 'react-icons/fa'
import Sidebar from '../components/Sidebar'
import MobileNavigation from '../components/MobileNavigation'
import ScreenHeader from '../components/design/ScreenHeader'
import { parseResourceContent } from '../utils/subjectIcons'
import { useAllLessonResources } from '../hooks/useEducatorData'

interface ResourceSummary { lesson_resources_id: number; lesson_plan_id: number; ai_generated_content?: string }

export default function LessonResourcesPage() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const { data: resources = [], isLoading, error } = useAllLessonResources()
  const items = (resources as ResourceSummary[]).map(resource => ({ resource, ...parseResourceContent(resource) }))
  const visible = items.filter(item => `${item.subject} ${item.topic} ${item.gradeLevel}`.toLowerCase().includes(search.toLowerCase()))
  return <div className="new-screen flex min-h-screen"><Sidebar currentPage="lesson-resources" />
    <main id="main-content" tabIndex={-1} className="flex-1 min-w-0 lg:ml-64 pb-28 outline-none"><div className="screen-body">
      <ScreenHeader title="Lesson Resources" label="Ready to revisit" description="Your classroom ideas, all in one place. Review, adapt and export a resource for your next lesson." action={<Link className="learning-button-secondary" to="/lesson-plans">View lesson plans</Link>} />
      <div className="screen-library-tools"><label className="screen-search">Find a resource<input type="search" value={search} onChange={event => setSearch(event.target.value)} placeholder="Search topic, subject or grade" /></label><p className="text-sm text-gray-500">{items.length} saved {items.length === 1 ? 'resource' : 'resources'}</p></div>
      {isLoading ? <div className="screen-empty" role="status">Loading resources...</div> : error ? <div className="screen-empty" role="alert"><h2>Could not load your resources</h2><p>Please try again when your connection is available.</p></div> : visible.length === 0 ? <div className="screen-empty"><FaBookOpen aria-hidden="true" /><h2>{search ? 'No matching resources' : 'No Lesson Resources Yet'}</h2><p>{search ? 'Try a different topic, subject or grade.' : 'Create a lesson plan, then generate a resource for your classroom.'}</p>{search ? <button className="learning-button-secondary" onClick={() => setSearch('')}>Clear search</button> : <Link className="learning-button" to="/dashboard">Create Lesson Plan</Link>}</div> : <div className="screen-library-grid">{visible.map(item => <button key={item.resource.lesson_resources_id} className="screen-book" onClick={() => navigate(`/lesson-plans/${item.resource.lesson_plan_id}/resources/edit`)}><span className="screen-book-icon"><FaBookOpen aria-hidden="true" /></span><p className="text-sm text-primary-700">{item.subject}</p><h2>{item.topic}</h2><p className="screen-book-meta">{item.gradeLevel}</p><span className="screen-book-action">Review resource <FaArrowRight aria-hidden="true" /></span></button>)}</div>}
    </div></main><MobileNavigation currentPage="lesson-resources" />
  </div>
}
