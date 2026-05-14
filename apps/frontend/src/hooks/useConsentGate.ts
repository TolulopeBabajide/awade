import { useState } from 'react'
import apiService from '../services/api'
import { getErrorMessage } from '../utils/errors'
import type { ConsentStatusResponse } from '../types/children'

/**
 * AWD-M-132 — COPPA consent gate hook.
 *
 * Manages the three state items and two handlers that exclusively serve the
 * ConsentModal flow, reducing ParentDashboardPage's useState footprint.
 *
 * @param consentStatus  - current COPPA consent status from the API query
 * @param refetchConsent - RefetchFunction from the consentStatus useQuery
 * @param onConsentGranted - called after consent is recorded (opens AddChildModal)
 */
export function useConsentGate(
  consentStatus: ConsentStatusResponse | undefined,
  refetchConsent: () => Promise<unknown>,
  onConsentGranted: () => void,
): {
  showConsentModal: boolean
  consentSubmitting: boolean
  consentError: string | null
  openConsentGate: () => void
  handleConsentConfirmed: () => Promise<void>
  handleCancel: () => void
} {
  const [showConsentModal, setShowConsentModal] = useState(false)
  const [consentSubmitting, setConsentSubmitting] = useState(false)
  const [consentError, setConsentError] = useState<string | null>(null)

  /**
   * Entry point for the "Add Child" intent.
   * Skips the modal when consent is already on record; otherwise opens it.
   */
  const openConsentGate = () => {
    if (consentStatus?.has_consented) {
      onConsentGranted()
    } else {
      setShowConsentModal(true)
    }
  }

  /**
   * Called when the parent presses "I Agree" inside ConsentModal.
   * Records consent via the API, refetches the consent status, and calls
   * `onConsentGranted` so the caller can open AddChildModal.
   */
  const handleConsentConfirmed = async () => {
    setConsentSubmitting(true)
    setConsentError(null)
    try {
      const res = await apiService.recordConsent()
      if (res.error) {
        setConsentError(res.error)
        return
      }
      // Invalidate the consent-status query so subsequent checks are fresh.
      await refetchConsent()
      setShowConsentModal(false)
      onConsentGranted()
    } catch (err) {
      // AWD-M-81: surface the underlying error message when available.
      setConsentError(getErrorMessage(err))
    } finally {
      setConsentSubmitting(false)
    }
  }

  /**
   * Called when the parent dismisses ConsentModal without agreeing.
   * Closes the modal and clears any previous error.
   */
  const handleCancel = () => {
    setShowConsentModal(false)
    setConsentError(null)
  }

  return {
    showConsentModal,
    consentSubmitting,
    consentError,
    openConsentGate,
    handleConsentConfirmed,
    handleCancel,
  }
}
