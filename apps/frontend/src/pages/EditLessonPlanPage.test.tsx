import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import EditLessonPlanPage from './EditLessonPlanPage'
import apiService from '../services/api'

vi.mock('../services/api', () => ({ default: { getLessonPlan: vi.fn() } }))
vi.mock('../components/Sidebar', () => ({ default: () => null }))
vi.mock('../components/MobileNavigation', () => ({ default: () => null }))
const plan = { lesson_id: 7, title: 'Equal parts', subject: 'Mathematics', topic: 'Fractions', grade_level: 'JSS 1', author_id: 1, duration_minutes: 40, status: 'draft', created_at: '', updated_at: '', curriculum_learning_objectives: ['Recognise equal parts'], curriculum_contents: [] }
function setup() {
  return render(<QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}><MemoryRouter initialEntries={['/lesson-plans/7/edit']}><Routes><Route path="/lesson-plans/:id/edit" element={<EditLessonPlanPage />} /></Routes></MemoryRouter></QueryClientProvider>)
}

describe('lesson details screen', () => {
  beforeEach(() => vi.clearAllMocks())
  it('loads the actual record and leads to the working teaching resource editor', async () => {
    vi.mocked(apiService.getLessonPlan).mockResolvedValue({ data: plan })
    setup()
    expect(await screen.findByRole('heading', { name: 'Equal parts' })).toBeInTheDocument()
    expect(screen.getByText('Recognise equal parts')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Edit teaching resource' })).toHaveAttribute('href', '/lesson-plans/7/resources/edit')
    expect(screen.queryByRole('button', { name: /save/i })).not.toBeInTheDocument()
  })
  it('shows a recoverable loading error without sample content', async () => {
    vi.mocked(apiService.getLessonPlan).mockResolvedValue({ error: 'Not found' })
    setup()
    expect(screen.getByRole('status')).toHaveTextContent('Loading your lesson')
    expect(await screen.findByRole('alert')).toHaveTextContent('Could not load this lesson')
    expect(screen.getByRole('button', { name: 'Try again' })).toBeInTheDocument()
    expect(screen.queryByText('Introduction to Family')).not.toBeInTheDocument()
  })
})
