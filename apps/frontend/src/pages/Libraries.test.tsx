import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import LessonPlansPage from './LessonPlansPage'
import LessonResourcesPage from './LessonResourcesPage'

const data = vi.hoisted(() => ({ loading: false, error: null as Error | null }))
vi.mock('../components/Sidebar', () => ({ default: () => null }))
vi.mock('../components/MobileNavigation', () => ({ default: () => null }))
vi.mock('../hooks/useEducatorData', () => ({
  useLessonPlans: () => ({ isLoading: data.loading, error: data.error, data: [{ lesson_id: 1, title: 'Equal parts', topic: 'Fractions', subject: 'Mathematics', grade_level: 'JSS 1', duration_minutes: 40 }] }),
  useAllLessonResources: () => ({ isLoading: data.loading, error: data.error, data: [{ lesson_resources_id: 1, lesson_plan_id: 1, ai_generated_content: JSON.stringify({ title_header: { topic: 'Fractions', subject: 'Mathematics', grade_level: 'JSS 1' } }) }] }),
}))
describe('redesigned libraries', () => {
  it('filters saved lesson records and restores them when search is cleared', () => {
    render(<MemoryRouter><LessonPlansPage /></MemoryRouter>)
    expect(screen.getByRole('button', { name: /Equal parts/ })).toBeInTheDocument()
    fireEvent.change(screen.getByRole('searchbox'), { target: { value: 'poetry' } })
    expect(screen.getByText('No matching lessons')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Clear search' }))
    expect(screen.getByRole('button', { name: /Equal parts/ })).toBeInTheDocument()
  })
  it('shows keyboard-accessible resource entries with real content', () => {
    render(<MemoryRouter><LessonResourcesPage /></MemoryRouter>)
    expect(screen.getByRole('button', { name: /Fractions/ })).toBeInTheDocument()
    fireEvent.change(screen.getByRole('searchbox'), { target: { value: 'poetry' } })
    expect(screen.getByText('No matching resources')).toBeInTheDocument()
  })
  it('retains loading and error states', () => {
    data.loading = true
    const { rerender } = render(<MemoryRouter><LessonPlansPage /></MemoryRouter>)
    expect(screen.getByRole('status')).toHaveTextContent('Loading lesson plans')
    data.loading = false; data.error = new Error('Unavailable')
    rerender(<MemoryRouter><LessonPlansPage /></MemoryRouter>)
    expect(screen.getByRole('alert')).toHaveTextContent('Could not load your lesson plans')
    data.error = null
  })
})
