import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import EditLessonResourcePage from './EditLessonResourcePage'
import apiService from '../services/api'

vi.mock('../components/Sidebar', () => ({ default: () => null }))
vi.mock('../components/MobileNavigation', () => ({ default: () => null }))
vi.mock('../services/api', () => ({ default: { getLessonPlan: vi.fn(), getLessonResources: vi.fn() } }))

function setup() {
  return render(<MemoryRouter initialEntries={['/lesson-plans/1/resources/edit']}><Routes><Route path="/lesson-plans/:lessonPlanId/resources/edit" element={<EditLessonResourcePage />} /></Routes></MemoryRouter>)
}

describe('resource concept integration', () => {
  it('keeps loading available before content arrives', () => {
    vi.mocked(apiService.getLessonPlan).mockReturnValue(new Promise(() => {}))
    setup()
    expect(screen.queryByText('Explore the concept')).not.toBeInTheDocument()
    expect(document.querySelector('.animate-spin')).toBeInTheDocument()
  })
  it('renders a matching concept alongside existing resource content', async () => {
    vi.mocked(apiService.getLessonPlan).mockResolvedValue({ data: {} })
    vi.mocked(apiService.getLessonResources).mockResolvedValue({ data: [{
      lesson_resources_id: 1, lesson_plan_id: 1, user_id: 1, status: 'complete', created_at: '2026-11-07',
      ai_generated_content: JSON.stringify({ title_header: { topic: 'Fractions', subject: 'Mathematics' }, learning_objectives: ['Recognise equal parts'] }),
    }] })
    setup()
    expect(await screen.findByRole('heading', { name: 'Parts of a whole' })).toBeInTheDocument()
    expect(screen.getByText('Recognise equal parts')).toBeInTheDocument()
    expect(screen.getByText(/^Ask your class:/)).toBeInTheDocument()
  })
  it('does not attach a model to unrelated generated content', async () => {
    vi.mocked(apiService.getLessonPlan).mockResolvedValue({ data: {} })
    vi.mocked(apiService.getLessonResources).mockResolvedValue({ data: [{
      lesson_resources_id: 1, lesson_plan_id: 1, user_id: 1, status: 'complete', created_at: '2026-11-07',
      ai_generated_content: JSON.stringify({ title_header: { topic: 'Poetry', subject: 'English' } }),
    }] })
    setup()
    expect(await screen.findByText('Poetry')).toBeInTheDocument()
    expect(screen.queryByText('Explore the concept')).not.toBeInTheDocument()
  })
})
