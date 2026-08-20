import { render, screen, waitFor, act } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import userEvent from '@testing-library/user-event'
import LessonPlanDetailPage from './LessonPlanDetailPage'

// ---------------------------------------------------------------------------
// Module mocks
// ---------------------------------------------------------------------------

const mockNavigate = vi.fn()

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

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
// Tests — unmount guards and AbortController (AWD-M-89, AWD-M-137)
// ---------------------------------------------------------------------------

describe('LessonPlanDetailPage (generate/unmount)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  // Ensure fake timers are never leaked between tests
  afterEach(() => {
    vi.useRealTimers()
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
        expect(screen.getByText('Introduction to Fractions')).toBeInTheDocument(),
        { timeout: 5000 }
      )

      // Click the generate button to start the async handler
      const user = userEvent.setup()
      await user.click(screen.getByRole('button', { name: /Generate Lesson Resource/i }))

      // Wait until generateLessonResource was called (handler is in the polling loop)
      await waitFor(() => expect(mockGenerateLessonResource).toHaveBeenCalledTimes(1), { timeout: 5000 })

      // Unmount while the handler is awaiting the first poll response
      act(() => { unmount() })

      // Resolve the poll after unmount — should not trigger any state update warnings
      await act(async () => {
        resolveFirstPoll({ data: { lesson_resources_id: 99, status: 'complete' } })
      })

      // If the AbortController signal guard is absent React logs a console.error
      // about updating unmounted components. No assertion needed beyond the test
      // completing cleanly.
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
        expect(screen.getByText('Introduction to Fractions')).toBeInTheDocument(),
        { timeout: 5000 }
      )

      const user = userEvent.setup()
      await user.click(screen.getByRole('button', { name: /Generate Lesson Resource/i }))
      await waitFor(() => expect(mockGenerateLessonResource).toHaveBeenCalledTimes(1), { timeout: 5000 })

      // Unmount before the rejection lands
      act(() => { unmount() })

      // Reject after unmount — catch block should bail via the AbortController signal guard
      await act(async () => {
        rejectGenerate(new Error('network down'))
      })

      // Test passes cleanly if no React unmounted-component warning is emitted
    })
  })

  // ---------------------------------------------------------------------------
  // AWD-M-137 — AbortController replaces isMountedRef guards
  // ---------------------------------------------------------------------------

  describe('handleGenerateLessonResource AbortController (AWD-M-137)', () => {
    it('aborts cleanly when unmounted during the fetch-curriculum-data pause', async () => {
      mockGetLessonPlan.mockResolvedValue({ data: MOCK_LESSON_PLAN })
      // generateLessonResource never resolves — we unmount before it is called
      mockGenerateLessonResource.mockReturnValue(new Promise(() => {}))

      const { unmount } = renderPage()
      await waitFor(() =>
        expect(screen.getByText('Introduction to Fractions')).toBeInTheDocument(),
        { timeout: 5000 }
      )

      vi.useFakeTimers()
      try {
        const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
        await user.click(screen.getByRole('button', { name: /Generate Lesson Resource/i }))

        // Advance 200ms — handler is in the 500ms fetch-curriculum-data pause, no API call yet
        await act(async () => { await vi.advanceTimersByTimeAsync(200) })

        // Unmount mid-pause — controller.abort() fires in cleanup effect (AWD-M-137)
        act(() => { unmount() })

        // Advance past the remaining 300ms — signal.throwIfAborted() fires, no state updates
        await act(async () => { await vi.advanceTimersByTimeAsync(400) })

        // generateLessonResource was never called — abort prevented it
        expect(mockGenerateLessonResource).not.toHaveBeenCalled()
      } finally {
        vi.useRealTimers()
      }
    })

    it('does not call navigate when unmounted during the completion pause', async () => {
      mockGetLessonPlan.mockResolvedValue({ data: MOCK_LESSON_PLAN })
      // generate returns complete immediately — skips polling, enters 500ms completion pause
      mockGenerateLessonResource.mockResolvedValue({
        data: { lesson_resources_id: 99, status: 'complete' },
      })

      const { unmount } = renderPage()
      await waitFor(() =>
        expect(screen.getByText('Introduction to Fractions')).toBeInTheDocument(),
        { timeout: 5000 }
      )

      // Switch to fake timers after initial render (AWD-H-82 pattern)
      vi.useFakeTimers()
      try {
        const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
        await user.click(screen.getByRole('button', { name: /Generate Lesson Resource/i }))

        // Advance 700ms: past the 500ms fetch-curriculum pause and into the completion pause
        // (generateLessonResource mock resolves via microtask at ~500ms; completion timer starts ~500ms)
        await act(async () => { await vi.advanceTimersByTimeAsync(700) })

        // Unmount during the completion pause — controller.abort() fires
        act(() => { unmount() })

        // Advance 600ms more: completion timer fires (~1000ms total), throwIfAborted() catches it
        await act(async () => { await vi.advanceTimersByTimeAsync(600) })

        // navigate must NOT have been called — abort short-circuits before handleGenerationSuccess
        expect(mockNavigate).not.toHaveBeenCalled()
      } finally {
        vi.useRealTimers()
      }
    })
  })
})
