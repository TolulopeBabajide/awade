import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import LessonPlanDetailPage from './LessonPlanDetailPage'

// ---------------------------------------------------------------------------
// Module mocks
// ---------------------------------------------------------------------------

vi.mock('../services/api', () => ({
  default: {
    getLessonPlan: vi.fn(),
    generateLessonResource: vi.fn(),
    submitContext: vi.fn(),
    getLessonResource: vi.fn(),
  },
}))

vi.mock('../utils/sanitizer', () => ({
  sanitizeInput: (v: string) => v,
}))

vi.mock('../components/Sidebar', () => ({
  default: () => <nav data-testid="sidebar" />,
}))

vi.mock('../components/MobileNavigation', () => ({
  default: () => <nav data-testid="mobile-nav" />,
}))

vi.mock('../components/AIGenerationLoading', () => ({
  default: () => null,
}))

// ---------------------------------------------------------------------------
// Imports after mocks
// ---------------------------------------------------------------------------

import apiService from '../services/api'

const mockGetLessonPlan = vi.mocked(apiService.getLessonPlan)

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

const MOCK_LESSON_PLAN = {
  lesson_id: 1,
  title: 'Introduction to Fractions',
  subject: 'Mathematics',
  grade_level: 'Grade 5',
  topic: 'Fractions',
  author_id: 42,
  duration_minutes: 60,
  created_at: '2026-05-01T00:00:00Z',
  updated_at: '2026-05-01T00:00:00Z',
  status: 'published',
  curriculum_learning_objectives: ['Understand halves and quarters'],
  curriculum_contents: ['Fractions as parts of a whole'],
}

// ---------------------------------------------------------------------------
// Render helper
// ---------------------------------------------------------------------------

function renderPage(lessonId = '1') {
  return render(
    <MemoryRouter initialEntries={[`/lesson-plans/${lessonId}`]}>
      <Routes>
        <Route path="/lesson-plans/:id" element={<LessonPlanDetailPage />} />
      </Routes>
    </MemoryRouter>
  )
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('LessonPlanDetailPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders loading state initially', () => {
    // Never resolves — stays in loading
    mockGetLessonPlan.mockReturnValue(new Promise(() => {}))
    renderPage()
    expect(screen.getByText('Loading lesson plan...')).toBeInTheDocument()
  })

  it('renders lesson plan data on success', async () => {
    mockGetLessonPlan.mockResolvedValue({ data: MOCK_LESSON_PLAN })
    renderPage()
    await waitFor(() =>
      expect(screen.getByText('Introduction to Fractions')).toBeInTheDocument()
    )
    expect(screen.getByText('Understand halves and quarters')).toBeInTheDocument()
    expect(screen.getByText('Fractions as parts of a whole')).toBeInTheDocument()
  })

  it('shows 403 error message when permission is denied', async () => {
    mockGetLessonPlan.mockRejectedValue(new Error('403 Forbidden'))
    renderPage()
    await waitFor(() =>
      expect(
        screen.getByText(/You do not have permission to access this lesson plan/)
      ).toBeInTheDocument()
    )
  })

  it('shows 404 error message when lesson plan is not found', async () => {
    mockGetLessonPlan.mockRejectedValue(new Error('404 Not Found'))
    renderPage()
    await waitFor(() =>
      expect(
        screen.getByText(/Lesson plan not found/)
      ).toBeInTheDocument()
    )
  })

  it('shows generic error message for unknown errors', async () => {
    mockGetLessonPlan.mockRejectedValue(new Error('Network timeout'))
    renderPage()
    await waitFor(() =>
      expect(screen.getByText('Network timeout')).toBeInTheDocument()
    )
  })

  it('shows generic fallback when non-Error is thrown', async () => {
    mockGetLessonPlan.mockRejectedValue('unexpected string error')
    renderPage()
    await waitFor(() =>
      expect(screen.getByText('unexpected string error')).toBeInTheDocument()
    )
  })

  it('shows API error from response.error field', async () => {
    mockGetLessonPlan.mockResolvedValue({ error: 'Service unavailable' })
    renderPage()
    await waitFor(() =>
      expect(screen.getByText('Service unavailable')).toBeInTheDocument()
    )
  })

  it('renders lesson plan from navigation state without API call', async () => {
    // When navigation state carries lessonPlanData, getLessonPlan should NOT be called
    render(
      <MemoryRouter
        initialEntries={[{ pathname: '/lesson-plans/1', state: { lessonPlanData: MOCK_LESSON_PLAN } }]}
      >
        <Routes>
          <Route path="/lesson-plans/:id" element={<LessonPlanDetailPage />} />
        </Routes>
      </MemoryRouter>
    )
    await waitFor(() =>
      expect(screen.getByText('Introduction to Fractions')).toBeInTheDocument()
    )
    expect(mockGetLessonPlan).not.toHaveBeenCalled()
  })
})
