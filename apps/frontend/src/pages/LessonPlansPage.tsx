import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { FaArrowRight, FaBookOpen, FaPlus } from 'react-icons/fa'
import Sidebar from '../components/Sidebar'
import MobileNavigation from '../components/MobileNavigation'
import ScreenHeader from '../components/design/ScreenHeader'
import { useLessonPlans } from '../hooks/useEducatorData'
import type { LessonPlanData } from '../types/lesson-plans'

export default function LessonPlansPage() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const { data: lessonPlans = [], isLoading, error } = useLessonPlans()
  const plans: LessonPlanData[] = lessonPlans
  const visible = plans.filter(plan => `${plan.title} ${plan.topic} ${plan.subject} ${plan.grade_level}`.toLowerCase().includes(search.toLowerCase()))
  return <div className="new-screen flex min-h-screen">
    <Sidebar currentPage="lesson-plans" />
    <main id="main-content" tabIndex={-1} className="flex-1 min-w-0 lg:ml-64 pb-28 outline-none"><div className="screen-body">
      <ScreenHeader title="My Lesson Plans" label="Your teaching library" description="Good preparation is worth keeping. Find a lesson, make it your own, and bring it back to your classroom." action={<Link to="/dashboard" className="learning-button"><FaPlus aria-hidden="true" /> Create Lesson Plan</Link>} />
      <div className="screen-library-tools"><label className="screen-search">Find a lesson<input type="search" value={search} onChange={event => setSearch(event.target.value)} placeholder="Search topic, subject or grade" /></label><p className="text-sm text-gray-500">{plans.length} saved {plans.length === 1 ? 'plan' : 'plans'}</p></div>
      {isLoading ? <div className="screen-empty" role="status">Loading lesson plans...</div> : error ? <div className="screen-empty" role="alert"><h2>Could not load your lesson plans</h2><p>Please try again when your connection is available.</p></div> : visible.length === 0 ? <div className="screen-empty"><FaBookOpen aria-hidden="true" /><h2>{search ? 'No matching lessons' : 'No lesson plans yet'}</h2><p>{search ? 'Try a different topic, subject or grade.' : 'Start with your curriculum and a topic you want to teach.'}</p>{search ? <button className="learning-button-secondary" onClick={() => setSearch('')}>Clear search</button> : <Link className="learning-button" to="/dashboard">Create Lesson Plan</Link>}</div> : <div className="screen-library-grid">
        {visible.map(plan => <button className="screen-book" key={plan.lesson_id} onClick={() => navigate(`/lesson-plans/${plan.lesson_id}`, { state: { lessonPlanData: plan } })}><span className="screen-book-icon"><FaBookOpen aria-hidden="true" /></span><p className="text-sm text-primary-700">{plan.subject}</p><h2>{plan.title || plan.topic}</h2><p className="screen-book-meta">{plan.grade_level}{plan.duration_minutes ? ` • ${plan.duration_minutes} minutes` : ''}</p><span className="screen-book-action">Open lesson <FaArrowRight aria-hidden="true" /></span></button>)}
      </div>}
    </div></main><MobileNavigation currentPage="lesson-plans" />
  </div>
}
