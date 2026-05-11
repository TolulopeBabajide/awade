import { renderHook, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import React from 'react'
import { MemoryRouter } from 'react-router-dom'
import { useGenerateLessonResource } from './useGenerateLessonResource'
import type { LessonPlanData } from '../types/lesson-plans'

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
    generateLessonResource: vi.fn(),
    submitContext: vi.fn(),
    getLessonResource: vi.fn(),
  },
}))

vi.mock('../utils/sanitizer', () => ({
  sanitizeInput: (v: string) => v,
}))

// ---------------------------------------------------------------------------
// Imports after mocks
// ---------------------------------------------------------------------------

import apiService from '../services/api'

const mockGenerateLessonResource = vi.mocked(apiService.generateLessonResource)
const mockGetLessonResource = vi.mocked(apiService.getLessonResource)
const mockSubmitContext = vi.mocked(apiService.submitContext)

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

const MOCK_LESSON_PLAN: LessonPlanData = {
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
// Render helper — hook requires router context for useNavigate
// ---------------------------------------------------------------------------

function renderGenHook(
  lessonPlan: LessonPlanData | null = MOCK_LESSON_PLAN,
  context = '',
  onClearContext = vi.fn(),
) {
  return renderHook(
    () => useGenerateLessonResource(lessonPlan, context, onClearContext),
    { wrapper: ({ children }) => React.createElement(MemoryRouter, null, children) },
  )
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('useGenerateLessonResource (AWD-L-29)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  // ── Initial state ──────────────────────────────────────────────────────

  describe('initial state', () => {
    it('returns falsy/null defaults before any generation', () => {
      const { result } = renderGenHook()

      expect(result.current.isGeneratingLessonResource).toBe(false)
      expect(result.current.contextFeedback).toBeNull()
      expect(result.current.currentGenerationStep).toBe('')
    })

    it('exposes handleGenerateLessonResource and resetGenerating as functions', () => {
      const { result } = renderGenHook()

      expect(typeof result.current.handleGenerateLessonResource).toBe('function')
      expect(typeof result.current.resetGenerating).toBe('function')
    })
  })

  // ── Guard: null lessonPlan ─────────────────────────────────────────────

  describe('null-lessonPlan guard', () => {
    it('does nothing when lessonPlan is null', async () => {
      const { result } = renderGenHook(null)

      await act(() => result.current.handleGenerateLessonResource())

      expect(mockGenerateLessonResource).not.toHaveBeenCalled()
      expect(result.current.isGeneratingLessonResource).toBe(false)
    })
  })

  // ── resetGenerating ────────────────────────────────────────────────────

  describe('resetGenerating', () => {
    it('sets isGeneratingLessonResource to false (used by AIGenerationLoading.onComplete)', async () => {
      vi.useFakeTimers()
      mockGenerateLessonResource.mockResolvedValue({
        data: { lesson_resources_id: 99, status: 'complete' },
      })

      const { result } = renderGenHook()

      // Start generation
      act(() => { result.current.handleGenerateLessonResource() })
      await act(() => vi.advanceTimersByTimeAsync(100))
      // isGenerating should be true mid-flight
      expect(result.current.isGeneratingLessonResource).toBe(true)

      // Calling resetGenerating should flip it back
      act(() => result.current.resetGenerating())
      expect(result.current.isGeneratingLessonResource).toBe(false)
    })
  })

  // ── Successful generation (immediate complete) ─────────────────────────

  describe('handleGenerateLessonResource — success path', () => {
    it('calls onClearContext after successful generation', async () => {
      vi.useFakeTimers()
      mockGenerateLessonResource.mockResolvedValue({
        data: { lesson_resources_id: 99, status: 'complete' },
      })
      const mockClear = vi.fn()
      const { result } = renderGenHook(MOCK_LESSON_PLAN, '', mockClear)

      act(() => { result.current.handleGenerateLessonResource() })
      // Advance past both 500ms pauses
      await act(() => vi.advanceTimersByTimeAsync(2000))

      expect(mockClear).toHaveBeenCalledOnce()
    })

    it('navigates to resources/edit after successful generation', async () => {
      vi.useFakeTimers()
      mockGenerateLessonResource.mockResolvedValue({
        data: { lesson_resources_id: 99, status: 'complete' },
      })

      const { result } = renderGenHook()

      act(() => { result.current.handleGenerateLessonResource() })
      await act(() => vi.advanceTimersByTimeAsync(2000))

      expect(mockNavigate).toHaveBeenCalledWith('/lesson-plans/1/resources/edit')
    })

    it('sets success contextFeedback after generation', async () => {
      vi.useFakeTimers()
      mockGenerateLessonResource.mockResolvedValue({
        data: { lesson_resources_id: 99, status: 'complete' },
      })

      const { result } = renderGenHook()

      act(() => { result.current.handleGenerateLessonResource() })
      await act(() => vi.advanceTimersByTimeAsync(2000))

      expect(result.current.contextFeedback?.type).toBe('success')
    })

    it('submits context when provided', async () => {
      vi.useFakeTimers()
      mockSubmitContext.mockResolvedValue({})
      mockGenerateLessonResource.mockResolvedValue({
        data: { lesson_resources_id: 99, status: 'complete' },
      })

      const { result } = renderGenHook(MOCK_LESSON_PLAN, 'extra context')

      act(() => { result.current.handleGenerateLessonResource() })
      await act(() => vi.advanceTimersByTimeAsync(2000))

      expect(mockSubmitContext).toHaveBeenCalledWith('1', 'extra context')
    })
  })

  // ── Error path ─────────────────────────────────────────────────────────

  describe('handleGenerateLessonResource — error path', () => {
    it('sets error contextFeedback when generateLessonResource rejects', async () => {
      vi.useFakeTimers()
      mockGenerateLessonResource.mockRejectedValue(new Error('API failure'))

      const { result } = renderGenHook()

      act(() => { result.current.handleGenerateLessonResource() })
      await act(() => vi.advanceTimersByTimeAsync(2000))

      expect(result.current.contextFeedback?.type).toBe('error')
      expect(result.current.contextFeedback?.message).toBe('API failure')
    })

    it('falls back to generic error message for non-Error throws', async () => {
      vi.useFakeTimers()
      mockGenerateLessonResource.mockRejectedValue('plain string')

      const { result } = renderGenHook()

      act(() => { result.current.handleGenerateLessonResource() })
      await act(() => vi.advanceTimersByTimeAsync(2000))

      expect(result.current.contextFeedback?.type).toBe('error')
      expect(result.current.contextFeedback?.message).toBeTruthy()
    })

    it('resets isGeneratingLessonResource to false after an error', async () => {
      vi.useFakeTimers()
      mockGenerateLessonResource.mockRejectedValue(new Error('fail'))

      const { result } = renderGenHook()

      act(() => { result.current.handleGenerateLessonResource() })
      await act(() => vi.advanceTimersByTimeAsync(2000))

      expect(result.current.isGeneratingLessonResource).toBe(false)
    })
  })

  // ── Polling path ───────────────────────────────────────────────────────

  describe('handleGenerateLessonResource — polling', () => {
    it('polls getLessonResource when initial status is processing, then succeeds', async () => {
      vi.useFakeTimers()
      mockGenerateLessonResource.mockResolvedValue({
        data: { lesson_resources_id: 55, status: 'processing' },
      })
      mockGetLessonResource
        .mockResolvedValueOnce({ data: { lesson_resources_id: 55, status: 'processing' } })
        .mockResolvedValueOnce({ data: { lesson_resources_id: 55, status: 'complete' } })

      const { result } = renderGenHook()

      act(() => { result.current.handleGenerateLessonResource() })
      // Advance past initial 500ms pause + 2 poll intervals (2s each)
      await act(() => vi.advanceTimersByTimeAsync(6000))

      expect(mockGetLessonResource).toHaveBeenCalledWith('55')
      expect(mockNavigate).toHaveBeenCalledWith('/lesson-plans/1/resources/edit')
    })
  })
})
