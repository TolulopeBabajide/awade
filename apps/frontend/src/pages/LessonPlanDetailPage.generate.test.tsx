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
const mockSubmitContext = vi.mocked(apiService.submitContext)

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
// Tests — generation workflow / polling (AWD-L-30)
// Unmount guards and AbortController tests extracted to
// LessonPlanDetailPage.generate.unmount.test.tsx (AWD-M-250)
// ---------------------------------------------------------------------------

describe('LessonPlanDetailPage (generate)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  // Ensure fake timers are never leaked between tests
  afterEach(() => {
    vi.useRealTimers()
  })

  // ---------------------------------------------------------------------------
  // AWD-M-133 — pollUntilComplete and handleGenerationSuccess coverage
  // ---------------------------------------------------------------------------

  describe('pollUntilComplete and handleGenerationSuccess (AWD-M-133)', () => {
    it('shows "AI generation failed" error when poll returns failed status', async () => {
      mockGetLessonPlan.mockResolvedValue({ data: MOCK_LESSON_PLAN })
      // Initial generate call returns processing — triggers pollUntilComplete
      mockGenerateLessonResource.mockResolvedValue({
        data: { lesson_resources_id: 99, status: 'processing' },
      })
      // First poll returns failed — pollUntilComplete should throw "AI generation failed"
      mockGetLessonResource.mockResolvedValue({
        data: { lesson_resources_id: 99, status: 'failed' },
      })

      renderPage()
      // Resolve the initial getLessonPlan with real timers before switching to fake
      await waitFor(() =>
        expect(screen.getByText('Introduction to Fractions')).toBeInTheDocument(),
        { timeout: 5000 }
      )

      // NOW switch to fake timers — initial render complete with real timers
      // userEvent.setup must be called AFTER vi.useFakeTimers() so advanceTimers
      // captures the mocked implementation, not the real one (AWD-H-82 fix)
      vi.useFakeTimers()
      try {
        const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
        await user.click(screen.getByRole('button', { name: /Generate Lesson Resource/i }))

        // Advance past: 500ms fetch-curriculum pause + 2000ms first poll delay.
        // Direct assertion (no waitFor) because waitFor's setInterval retry is
        // faked and never fires when jest global is absent (AWD-H-82 fix).
        // Second act() pass flushes React state updates that land in native
        // timer callbacks (originalSetTimeout) outside act's immediate scope.
        await act(async () => { await vi.advanceTimersByTimeAsync(3000) })
        // Second act() flushes React state updates from native timer callbacks.
        // Regex matcher needed: component renders "❌ message" so exact string
        // matching fails (getByText does full-text comparison per element).
        await act(async () => {})
        expect(
          screen.getByText(/AI generation failed\. Please try again\./)
        ).toBeInTheDocument()
      } finally {
        vi.useRealTimers()
      }
    })

    it('shows "Generation timed out" after 60 failed polls', async () => {
      mockGetLessonPlan.mockResolvedValue({ data: MOCK_LESSON_PLAN })
      mockGenerateLessonResource.mockResolvedValue({
        data: { lesson_resources_id: 99, status: 'processing' },
      })
      // Always returns processing — loop exhausts maxAttempts (60)
      mockGetLessonResource.mockResolvedValue({
        data: { lesson_resources_id: 99, status: 'processing' },
      })

      renderPage()
      // Resolve the initial getLessonPlan with real timers before switching to fake
      await waitFor(() =>
        expect(screen.getByText('Introduction to Fractions')).toBeInTheDocument(),
        { timeout: 5000 }
      )

      // NOW switch to fake timers — initial render complete with real timers
      // userEvent.setup must be called AFTER vi.useFakeTimers() (AWD-H-82 fix)
      vi.useFakeTimers()
      try {
        const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
        await user.click(screen.getByRole('button', { name: /Generate Lesson Resource/i }))

        // 500ms pause + 60 polls × 2000ms = 120500ms; advance past that.
        // Direct assertion (no waitFor) — see AWD-H-82 fix comment above.
        // Second act() pass flushes React state updates from native timer callbacks.
        await act(async () => { await vi.advanceTimersByTimeAsync(125000) })
        // Second act() flushes React state updates from native timer callbacks.
        // Regex matcher: component renders "❌ message" so exact string fails.
        await act(async () => {})
        expect(
          screen.getByText(/Generation timed out\. Please check back later\./)
        ).toBeInTheDocument()
      } finally {
        vi.useRealTimers()
      }
    })
  })

  // ---------------------------------------------------------------------------
  // AWD-M-135 — pollUntilComplete: unknown status throws instead of silently passing
  // ---------------------------------------------------------------------------

  describe('pollUntilComplete unknown status guard (AWD-M-135)', () => {
    it('shows "Unexpected resource status" error when poll returns an unrecognised status', async () => {
      mockGetLessonPlan.mockResolvedValue({ data: MOCK_LESSON_PLAN })
      // Initial generate call returns processing — triggers pollUntilComplete
      mockGenerateLessonResource.mockResolvedValue({
        data: { lesson_resources_id: 99, status: 'processing' },
      })
      // First poll returns an unknown status value (e.g. 'error' / 'cancelled')
      mockGetLessonResource.mockResolvedValue({
        data: { lesson_resources_id: 99, status: 'error' },
      })

      renderPage()
      // Resolve the initial getLessonPlan with real timers before switching to fake
      await waitFor(() =>
        expect(screen.getByText('Introduction to Fractions')).toBeInTheDocument(),
        { timeout: 5000 }
      )

      // NOW switch to fake timers — initial render complete with real timers (AWD-H-82 fix)
      vi.useFakeTimers()
      try {
        const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
        await user.click(screen.getByRole('button', { name: /Generate Lesson Resource/i }))

        // Advance past: 500ms fetch-curriculum pause + 2000ms first poll delay.
        await act(async () => { await vi.advanceTimersByTimeAsync(3000) })
        // Second act() flushes React state updates from native timer callbacks.
        await act(async () => {})
        expect(
          screen.getByText(/Unexpected resource status: error/)
        ).toBeInTheDocument()
      } finally {
        vi.useRealTimers()
      }
    })
  })

  // ---------------------------------------------------------------------------
  // AWD-M-134 — submitContextIfProvided: no-context path + error path
  // ---------------------------------------------------------------------------

  describe('submitContextIfProvided (AWD-M-134)', () => {
    it('skips submitContext API call when context input is empty', async () => {
      mockGetLessonPlan.mockResolvedValue({ data: MOCK_LESSON_PLAN })
      // generate returns complete immediately — bypasses polling
      mockGenerateLessonResource.mockResolvedValue({
        data: { lesson_resources_id: 99, status: 'complete' },
      })

      renderPage()
      await waitFor(() =>
        expect(screen.getByText('Introduction to Fractions')).toBeInTheDocument(),
        { timeout: 5000 }
      )

      vi.useFakeTimers()
      try {
        const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
        // Context input is left empty — default state is ''
        await user.click(screen.getByRole('button', { name: /Generate Lesson Resource/i }))
        await act(async () => { await vi.advanceTimersByTimeAsync(1500) })
        // submitContext must NOT have been called because context was empty
        expect(mockSubmitContext).not.toHaveBeenCalled()
      } finally {
        vi.useRealTimers()
      }
    })

    it('shows context submission error when submitContext returns an API error', async () => {
      mockGetLessonPlan.mockResolvedValue({ data: MOCK_LESSON_PLAN })
      mockSubmitContext.mockResolvedValue({ error: 'Context submission failed' })

      renderPage()
      await waitFor(() =>
        expect(screen.getByText('Introduction to Fractions')).toBeInTheDocument(),
        { timeout: 5000 }
      )

      // Type something into the context textarea so submitContextIfProvided is reached
      const textarea = screen.getByPlaceholderText(/Add local context/i)
      await userEvent.type(textarea, 'some context')

      vi.useFakeTimers()
      try {
        const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
        await user.click(screen.getByRole('button', { name: /Generate Lesson Resource/i }))
        // submitContext is synchronous-ish — no timer advance needed before the error appears
        await act(async () => { await vi.advanceTimersByTimeAsync(100) })
        await act(async () => {})
        expect(
          screen.getByText(/Context submission failed/)
        ).toBeInTheDocument()
        // generateLessonResource must NOT have been called — error should abort step 1
        expect(mockGenerateLessonResource).not.toHaveBeenCalled()
      } finally {
        vi.useRealTimers()
      }
    })
  })

  // ---------------------------------------------------------------------------
  // AWD-M-90 — happy-path generation success → navigate to edit page
  // ---------------------------------------------------------------------------

  describe('handleGenerateLessonResource happy path (AWD-M-90)', () => {
    it('navigates to /lesson-plans/:id/resources/edit when generation completes immediately', async () => {
      mockGetLessonPlan.mockResolvedValue({ data: MOCK_LESSON_PLAN })
      // Initial generate call returns complete — bypasses pollUntilComplete entirely
      mockGenerateLessonResource.mockResolvedValue({
        data: { lesson_resources_id: 99, status: 'complete' },
      })

      renderPage()
      // Resolve the initial getLessonPlan with real timers before switching to fake
      await waitFor(() =>
        expect(screen.getByText('Introduction to Fractions')).toBeInTheDocument(),
        { timeout: 5000 }
      )

      // NOW switch to fake timers — initial render complete with real timers
      // userEvent.setup must be called AFTER vi.useFakeTimers() (AWD-H-82 fix)
      vi.useFakeTimers()
      try {
        const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
        await user.click(screen.getByRole('button', { name: /Generate Lesson Resource/i }))

        // Advance past the 500ms fetch-curriculum pause + 500ms completion pause.
        // Direct assertions (no waitFor) — see AWD-H-82 fix comment above.
        await act(async () => { await vi.advanceTimersByTimeAsync(1500) })
        expect(mockNavigate).toHaveBeenCalledWith('/lesson-plans/1/resources/edit')
        // Polling endpoint must NOT have been called — status was already complete
        expect(mockGetLessonResource).not.toHaveBeenCalled()
      } finally {
        vi.useRealTimers()
      }
    })
  })

})
