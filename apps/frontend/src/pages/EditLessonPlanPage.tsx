import { Link, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import Sidebar from '../components/Sidebar'
import MobileNavigation from '../components/MobileNavigation'
import ScreenHeader from '../components/design/ScreenHeader'
import apiService from '../services/api'
import { educatorKeys } from '../hooks/useEducatorData'
import type { LessonPlanData } from '../types/lesson-plans'

export default function EditLessonPlanPage() {
  const { id } = useParams<{ id: string }>()
  const { data: plan, isLoading, error, refetch } = useQuery<LessonPlanData, Error>({
    queryKey: educatorKeys.lessonPlan(id ?? ''),
    enabled: Boolean(id),
    queryFn: async () => {
      const response = await apiService.getLessonPlan(id!)
      if (response.error || !response.data) throw new Error('Could not load this lesson. Please try again.')
      return response.data
    },
  })
  return <div className="new-screen flex min-h-screen"><Sidebar currentPage="lesson-plans" />
    <main id="main-content" tabIndex={-1} className="flex-1 min-w-0 lg:ml-64 pb-28 outline-none"><div className="screen-body screen-editor">
      <ScreenHeader title="Your lesson, in context." description="Review the curriculum behind your lesson. Adapt its activities, explanations and assessment in the teaching resource." action={<Link to="/lesson-plans" className="learning-button-secondary">Back to lesson plans</Link>} />
      {isLoading ? <div className="screen-empty" role="status">Loading your lesson...</div> : error || !plan ? <div className="screen-empty" role="alert"><h2>Could not load this lesson</h2><p>Please return to your lesson plans or try again.</p><button className="learning-button-secondary" onClick={() => void refetch()}>Try again</button></div> : <section className="screen-editor-fields">
        <div className="screen-editor-meta"><span>{plan.subject}</span><span>{plan.grade_level}</span><span>{plan.topic}</span></div>
        <h2 className="text-2xl font-semibold mb-4">{plan.title}</h2>
        <p className="text-sm text-gray-600 mb-5">These details come from the selected curriculum. Changes to teaching content are saved through the resource editor.</p>
        <div className="flex flex-wrap gap-3"><Link to={`/lesson-plans/${id}/resources/edit`} className="learning-button">Edit teaching resource</Link><Link to={`/lesson-plans/${id}`} className="learning-button-secondary">Return to lesson</Link></div>
        <section className="screen-editor-objectives"><h2>Curriculum objectives</h2><ul>{(plan.curriculum_learning_objectives ?? []).map((objective, index) => <li key={index}>{objective}</li>)}</ul></section>
        {(plan.curriculum_contents ?? []).length > 0 && <section className="screen-editor-objectives"><h2>Content to cover</h2><ul>{plan.curriculum_contents.map((content, index) => <li key={index}>{content}</li>)}</ul></section>}
      </section>}
    </div></main><MobileNavigation currentPage="lesson-plans" />
  </div>
}
