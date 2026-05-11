import { renderHook, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useConsentGate } from './useConsentGate'

// ---------------------------------------------------------------------------
// Module mocks
// ---------------------------------------------------------------------------

vi.mock('../services/api', () => ({
  default: {
    recordConsent: vi.fn(),
  },
}))

import apiService from '../services/api'
const mockApiService = vi.mocked(apiService)

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const mockRefetchConsent = vi.fn().mockResolvedValue(undefined)
const mockOnConsentGranted = vi.fn()

function renderGate(hasConsented = false) {
  return renderHook(() =>
    useConsentGate(
      { has_consented: hasConsented, consent: null },
      mockRefetchConsent,
      mockOnConsentGranted,
    ),
  )
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('useConsentGate', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRefetchConsent.mockResolvedValue(undefined)
  })

  // ── openConsentGate ────────────────────────────────────────────────────

  describe('openConsentGate', () => {
    it('calls onConsentGranted immediately when consent is already on record', () => {
      const { result } = renderGate(/* hasConsented */ true)

      act(() => result.current.openConsentGate())

      expect(mockOnConsentGranted).toHaveBeenCalledOnce()
      expect(result.current.showConsentModal).toBe(false)
    })

    it('opens the consent modal when consent has not yet been given', () => {
      const { result } = renderGate(/* hasConsented */ false)

      act(() => result.current.openConsentGate())

      expect(result.current.showConsentModal).toBe(true)
      expect(mockOnConsentGranted).not.toHaveBeenCalled()
    })

    it('opens the consent modal when consentStatus is undefined (loading)', () => {
      const { result } = renderHook(() =>
        useConsentGate(undefined, mockRefetchConsent, mockOnConsentGranted),
      )

      act(() => result.current.openConsentGate())

      expect(result.current.showConsentModal).toBe(true)
    })
  })

  // ── handleConsentConfirmed ─────────────────────────────────────────────

  describe('handleConsentConfirmed', () => {
    it('records consent, closes modal, and calls onConsentGranted on success', async () => {
      mockApiService.recordConsent.mockResolvedValue({})
      const { result } = renderGate()

      act(() => result.current.openConsentGate())
      expect(result.current.showConsentModal).toBe(true)

      await act(() => result.current.handleConsentConfirmed())

      expect(mockApiService.recordConsent).toHaveBeenCalledOnce()
      expect(mockRefetchConsent).toHaveBeenCalledOnce()
      expect(result.current.showConsentModal).toBe(false)
      expect(result.current.consentError).toBeNull()
      expect(mockOnConsentGranted).toHaveBeenCalledOnce()
    })

    it('sets consentError and does not call onConsentGranted when API returns error', async () => {
      mockApiService.recordConsent.mockResolvedValue({ error: 'Server rejected consent' })
      const { result } = renderGate()

      await act(() => result.current.handleConsentConfirmed())

      expect(result.current.consentError).toBe('Server rejected consent')
      expect(result.current.showConsentModal).toBe(false) // was false — never opened
      expect(mockOnConsentGranted).not.toHaveBeenCalled()
    })

    it('surfaces err.message when recordConsent throws an Error (AWD-M-81)', async () => {
      mockApiService.recordConsent.mockRejectedValue(new Error('Network down'))
      const { result } = renderGate()

      await act(() => result.current.handleConsentConfirmed())

      expect(result.current.consentError).toBe('Network down')
      expect(mockOnConsentGranted).not.toHaveBeenCalled()
    })

    it('falls back to default message when a non-Error value is thrown', async () => {
      mockApiService.recordConsent.mockRejectedValue('plain-string-rejection')
      const { result } = renderGate()

      await act(() => result.current.handleConsentConfirmed())

      expect(result.current.consentError).toBe('Something went wrong. Please try again.')
      expect(mockOnConsentGranted).not.toHaveBeenCalled()
    })

    it('clears consentSubmitting flag after API call (success path)', async () => {
      mockApiService.recordConsent.mockResolvedValue({})
      const { result } = renderGate()

      await act(() => result.current.handleConsentConfirmed())

      expect(result.current.consentSubmitting).toBe(false)
    })

    it('clears consentSubmitting flag after API call (error path)', async () => {
      mockApiService.recordConsent.mockRejectedValue(new Error('fail'))
      const { result } = renderGate()

      await act(() => result.current.handleConsentConfirmed())

      expect(result.current.consentSubmitting).toBe(false)
    })
  })

  // ── handleCancel ───────────────────────────────────────────────────────

  describe('handleCancel', () => {
    it('closes the modal and clears any prior consentError', async () => {
      mockApiService.recordConsent.mockRejectedValue(new Error('Network error'))
      const { result } = renderGate()

      // Trigger an error first so consentError is non-null.
      await act(() => result.current.handleConsentConfirmed())
      expect(result.current.consentError).toBe('Network error')

      // Open modal, then cancel.
      act(() => result.current.openConsentGate())
      expect(result.current.showConsentModal).toBe(true)

      act(() => result.current.handleCancel())

      expect(result.current.showConsentModal).toBe(false)
      expect(result.current.consentError).toBeNull()
    })
  })
})
