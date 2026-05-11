/**
 * ParentDashboardPage — consent gate + delete workflow tests (AWD-M-141).
 *
 * Covers:
 *   - handleConsentConfirmed error narrowing (AWD-M-81)
 *   - handleDeleteChild error feedback (AWD-H-80, AWD-M-80)
 *   - switch child card clears deleteError (AWD-L-26)
 *   - DeleteChildConfirmModal (AWD-M-80)
 *
 * See ParentDashboardPage.render.test.tsx for page state + a11y tests.
 */

import React from 'react'
import { screen, waitFor, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { makeChild, renderPage } from './__fixtures__/parentDashboardPage'

// ---------------------------------------------------------------------------
// Module mocks (must remain here — vi.mock is hoisted at compile time)
// ---------------------------------------------------------------------------

vi.mock('../services/api', () => ({
  default: {
    getChildren: vi.fn(),
    getChildTopics: vi.fn(),
    deleteChild: vi.fn(),
  },
}))

vi.mock('../contexts/AuthContext', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  useAuth: vi.fn(),
}))

vi.mock('../components/Sidebar', () => ({
  default: () => <nav data-testid="sidebar" />,
}))

vi.mock('../components/MobileNavigation', () => ({
  default: () => <nav data-testid="mobile-nav" />,
}))

vi.mock('../components/AddChildModal', () => ({
  default: ({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) =>
    isOpen ? (
      <div data-testid="add-child-modal">
        <button onClick={onClose}>Close modal</button>
      </div>
    ) : null,
}))

vi.mock('../hooks/useFocusTrap', () => ({
  useFocusTrap: () => {},
}))

// ---------------------------------------------------------------------------
// Setup
// ---------------------------------------------------------------------------

import apiService from '../services/api'
import { useAuth } from '../contexts/AuthContext'

const mockApiService = vi.mocked(apiService)
const mockUseAuth = useAuth as ReturnType<typeof vi.fn>

beforeEach(() => {
  vi.clearAllMocks()

  mockUseAuth.mockReturnValue({
    user: {
      user_: 10,
      email: 'parent@test.invalid',
      full_name: 'Test Parent',
      role: 'PARENT',
      country: 'ZZ',
    },
    isAuthenticated: true,
    isLoading: false,
    login: vi.fn(),
    signup: vi.fn(),
    googleAuth: vi.fn(),
    logout: vi.fn(),
    validateToken: vi.fn(),
  })
})

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('ParentDashboardPage — delete & consent', () => {
  describe('handleConsentConfirmed error narrowing (AWD-M-81)', () => {
    /**
     * AWD-M-81: the catch block in handleConsentConfirmed previously discarded
     * the thrown error and always set a generic "Something went wrong" message.
     * It must now surface `err.message` when the thrown value is an Error
     * instance so network/API failures bubble up to the parent.
     */
    const setupConsentFlow = (recordConsentImpl: () => Promise<unknown>) => {
      mockApiService.getChildren.mockResolvedValue({
        error: undefined,
        data: { children: [], total: 0 },
      })
      mockApiService.getConsentStatus = vi.fn().mockResolvedValue({
        error: undefined,
        data: { has_consented: false },
      })
      mockApiService.recordConsent = vi.fn().mockImplementation(recordConsentImpl)
    }

    const triggerConsentSubmit = async () => {
      await waitFor(() => expect(screen.getByText(/Add Your Child/i)).toBeTruthy())
      fireEvent.click(screen.getByText(/Add Your Child/i))

      const checkbox = await screen.findByRole('checkbox')
      fireEvent.click(checkbox)

      const submitBtn = screen.getByRole('button', { name: /I Agree — Add a Child/i })
      fireEvent.click(submitBtn)
    }

    it('surfaces err.message when recordConsent rejects with an Error instance', async () => {
      setupConsentFlow(() => Promise.reject(new Error('Network down')))

      renderPage()
      await triggerConsentSubmit()

      await waitFor(() => {
        const alert = screen.getByRole('alert')
        expect(alert.textContent).toContain('Network down')
      })
    })

    it('falls back to the generic message when a non-Error value is thrown', async () => {
      setupConsentFlow(() => Promise.reject('plain-string-error'))

      renderPage()
      await triggerConsentSubmit()

      await waitFor(() => {
        const alert = screen.getByRole('alert')
        expect(alert.textContent).toContain('Something went wrong. Please try again.')
      })
    })
  })

  describe('handleDeleteChild error feedback (AWD-H-80, AWD-M-80)', () => {
    /**
     * AWD-H-80: deleteChild API rejections were previously absorbed in `finally`
     * with no user-visible feedback. The fix adds a catch block that sets
     * `deleteError` state, which is rendered as an inline role="alert" message
     * above the child selector cards.
     *
     * AWD-M-80: confirmation gating moved from window.confirm() to a controlled
     * DeleteChildConfirmModal. Tests now click the trash button to open the
     * modal, then press its "Remove" button to trigger the API call.
     */
    const setupChildList = () => {
      mockApiService.getChildren.mockResolvedValue({
        error: undefined,
        data: { children: [makeChild({ child_id: 1, name: 'Child A' })], total: 1 },
      })
      mockApiService.getChildTopics.mockResolvedValue({ error: undefined, data: [] })
    }

    const openAndConfirmDelete = async () => {
      await waitFor(() => expect(screen.getByTitle('Remove')).toBeTruthy())
      fireEvent.click(screen.getByTitle('Remove'))
      const dialog = await screen.findByRole('dialog')
      const confirmBtn = dialog.querySelector('button') as HTMLButtonElement
      fireEvent.click(confirmBtn)
    }

    it('shows an inline error message when deleteChild API call rejects with an Error', async () => {
      setupChildList()
      mockApiService.deleteChild.mockRejectedValue(new Error('Server unavailable'))

      renderPage()
      await openAndConfirmDelete()

      await waitFor(() => {
        const alert = screen.getByRole('alert')
        expect(alert.textContent).toContain('Server unavailable')
      })
    })

    it('shows a generic fallback message when deleteChild rejects with a non-Error value', async () => {
      setupChildList()
      mockApiService.deleteChild.mockRejectedValue('plain-string-rejection')

      renderPage()
      await openAndConfirmDelete()

      await waitFor(() => {
        const alert = screen.getByRole('alert')
        expect(alert.textContent).toContain('Failed to remove child profile. Please try again.')
      })
    })

    it('clears any previous delete error when a new delete attempt begins', async () => {
      setupChildList()
      mockApiService.deleteChild
        .mockRejectedValueOnce(new Error('Temporary failure'))
        .mockResolvedValueOnce({ data: null, error: undefined })

      renderPage()

      await openAndConfirmDelete()
      await waitFor(() => expect(screen.getByRole('alert')).toBeTruthy())

      await openAndConfirmDelete()
      await waitFor(() => expect(screen.queryByRole('alert')).toBeNull())
    })
  })

  describe('switch child card clears deleteError (AWD-L-26)', () => {
    /**
     * AWD-L-26: `deleteError` was cleared on a new delete attempt and on
     * delete success, but it persisted when the parent switched to a
     * different child via the selector cards. A stale banner from Child A
     * could remain visible while the user was now viewing Child B. The
     * fix adds `setDeleteError(null)` to both the click and keyboard
     * handlers on the child selector card.
     */
    const setupTwoChildren = () => {
      mockApiService.getChildren.mockResolvedValue({
        error: undefined,
        data: {
          children: [
            makeChild({ child_id: 1, name: 'Child A' }),
            makeChild({ child_id: 2, name: 'Child B' }),
          ],
          total: 2,
        },
      })
      mockApiService.getChildTopics.mockResolvedValue({ error: undefined, data: [] })
    }

    const failDeleteOnSelectedChild = async () => {
      const removeButtons = await screen.findAllByTitle('Remove')
      fireEvent.click(removeButtons[0])
      const dialog = await screen.findByRole('dialog')
      const confirmBtn = dialog.querySelector('button') as HTMLButtonElement
      fireEvent.click(confirmBtn)
    }

    it('clears the delete-error banner when the parent clicks another child card', async () => {
      setupTwoChildren()
      mockApiService.deleteChild.mockRejectedValue(new Error('Server unavailable'))

      renderPage()

      await failDeleteOnSelectedChild()
      await waitFor(() => expect(screen.getByRole('alert')).toBeTruthy())

      fireEvent.click(screen.getByText('Child B'))

      await waitFor(() => expect(screen.queryByRole('alert')).toBeNull())
    })

    it('clears the delete-error banner when the parent activates another child card via Enter', async () => {
      setupTwoChildren()
      mockApiService.deleteChild.mockRejectedValue(new Error('Server unavailable'))

      renderPage()

      await failDeleteOnSelectedChild()
      await waitFor(() => expect(screen.getByRole('alert')).toBeTruthy())

      const childBCard = screen.getByRole('group', { name: 'Child B' })
      fireEvent.keyDown(childBCard, { key: 'Enter' })

      await waitFor(() => expect(screen.queryByRole('alert')).toBeNull())
    })
  })

  describe('DeleteChildConfirmModal (AWD-M-80)', () => {
    /**
     * AWD-M-80: replace browser-native window.confirm() with an in-app
     * accessible confirmation modal. The modal must:
     *  - Open when the trash button is clicked (gates the delete API call).
     *  - Expose role="dialog" with aria-modal="true" for assistive tech.
     *  - Cancel without calling deleteChild.
     *  - Confirm by calling deleteChild then closing on success.
     */
    const setupChildList = () => {
      mockApiService.getChildren.mockResolvedValue({
        error: undefined,
        data: { children: [makeChild({ child_id: 1, name: 'Child A' })], total: 1 },
      })
      mockApiService.getChildTopics.mockResolvedValue({ error: undefined, data: [] })
    }

    it('does NOT call window.confirm() when the trash button is clicked', async () => {
      setupChildList()
      const confirmSpy = vi.spyOn(window, 'confirm')

      renderPage()
      await waitFor(() => expect(screen.getByTitle('Remove')).toBeTruthy())
      fireEvent.click(screen.getByTitle('Remove'))

      expect(confirmSpy).not.toHaveBeenCalled()
      confirmSpy.mockRestore()
    })

    it('opens an accessible role="dialog" when the trash button is clicked', async () => {
      setupChildList()

      renderPage()
      await waitFor(() => expect(screen.getByTitle('Remove')).toBeTruthy())
      fireEvent.click(screen.getByTitle('Remove'))

      const dialog = await screen.findByRole('dialog')
      expect(dialog.getAttribute('aria-modal')).toBe('true')
      expect(dialog.textContent).toContain("Remove Child A's profile?")
    })

    it('Cancel closes the modal without calling deleteChild', async () => {
      setupChildList()

      renderPage()
      await waitFor(() => expect(screen.getByTitle('Remove')).toBeTruthy())
      fireEvent.click(screen.getByTitle('Remove'))

      const cancelBtn = await screen.findByRole('button', { name: /^Cancel$/ })
      fireEvent.click(cancelBtn)

      await waitFor(() => expect(screen.queryByRole('dialog')).toBeNull())
      expect(mockApiService.deleteChild).not.toHaveBeenCalled()
    })

    it('Remove button inside the modal calls deleteChild with the right id and closes the modal', async () => {
      setupChildList()
      mockApiService.deleteChild.mockResolvedValue({ data: null, error: undefined })

      renderPage()
      await waitFor(() => expect(screen.getByTitle('Remove')).toBeTruthy())
      fireEvent.click(screen.getByTitle('Remove'))

      const dialog = await screen.findByRole('dialog')
      const confirmBtn = dialog.querySelector('button') as HTMLButtonElement
      expect(confirmBtn).toBeTruthy()
      fireEvent.click(confirmBtn)

      await waitFor(() => expect(mockApiService.deleteChild).toHaveBeenCalledWith(1))
      await waitFor(() => expect(screen.queryByRole('dialog')).toBeNull())
    })
  })
})
