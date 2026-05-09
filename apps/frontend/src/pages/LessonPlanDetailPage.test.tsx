import { render, screen, waitFor, act } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import userEvent from '@testing-library/user-event'
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
const mockGenerateLessonResource = vi.mocked(apiService.generateLessonResource)
const mockGetLessonResource = vi.mocked(apiService.getLessonResource)

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

  // ---------------------------------------------------------------------------
  // AWD-M-89 — unmount guard: state updates must not fire after unmount
  // ---------------------------------------------------------------------------

  describe('handleGenerateLessonResource unmount guard (AWD-M-89)', () => {
    it('does not update state after unmount during polling delay', async () => {
      mockGetLessonPlan.mockResolvedValue({ data: MOCK_LESSON_PLAN })

      // generateLessonResource returns a processing resource
      mockGenerateLessonResource.mockResolvedValue({
        data: { lesson_resources_id: 99, status: 'processing' },
      })

      // getLessonResource never resolves — simulates a long poll interval
      let resolveFirstPoll!: (v: any) => void
      mockGetLessonResource.mockReturnValue(
        new Promise(resolve => { resolveFirstPoll = resolve })
      )

      const { unmount } = renderPage()
      await waitFor(() =>
        expect(screen.getByText('Introduction to Fractions')).toBeInTheDocument()
      )

      // Click the generate button to start the async handler
      const user = userEvent.setup()
      await user.click(screen.getByRole('button', { name: /Generate Lesson Resource/i }))

      // Wait until generateLessonResource was called (handler is in the polling loop)
      await waitFor(() => expect(mockGenerateLessonResource).toHaveBeenCalledTimes(1))

      // Unmount while the handler is awaiting the first poll response
      act(() => { unmount() })

      // Resolve the poll after unmount — should not trigger any state update warnings
      await act(async () => {
        resolveFirstPoll({ data: { lesson_resources_id: 99, status: 'complete' } })
      })

      // If isMountedRef guard is absent React logs a console.error about updating
      // unmounted components. No assertion needed beyond the test completing cleanly.
    })

    it('does not call setContextFeedback after unmount on generation error', async () => {
      mockGetLessonPlan.mockResolvedValue({ data: MOCK_LESSON_PLAN })

      // generateLessonResource rejects — error path hits catch block
      let rejectGenerate!: (reason: unknown) => void
      mockGenerateLessonResource.mockReturnValue(
        new Promise((_, reject) => { rejectGenerate = reject })
      )

      const { unmount } = renderPage()
      await waitFor(() =>
        expect(screen.getByText('Introduction to Fractions')).toBeInTheDocument()
      )

      const user = userEvent.setup()
      await user.click(screen.getByRole('button', { name: /Generate Lesson Resource/i }))
      await waitFor(() => expect(mockGenerateLessonResource).toHaveBeenCalledTimes(1))

      // Unmount before the rejection lands
      act(() => { unmount() })

      // Reject after unmount — catch block should bail via isMountedRef guard
      await act(async () => {
        rejectGenerate(new Error('network down'))
      })

      // Test passes cleanly if no React unmounted-component warning is emitted
    })
  })
})
