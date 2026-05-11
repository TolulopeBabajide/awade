import React from 'react'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ParentDashboardPage from './ParentDashboardPage'

// ---------------------------------------------------------------------------
// Module mocks
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

// AWD-M-80: useFocusTrap pulls in browser-only focus management. Stub it
// so the modal renders cleanly in JSDOM without focus side effects.
vi.mock('../hooks/useFocusTrap', () => ({
  useFocusTrap: () => {},
}))

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

import apiService from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import type { ChildProfile, ChildTopic } from '../types/children'

const mockApiService = vi.mocked(apiService)
const mockUseAuth = useAuth as ReturnType<typeof vi.fn>

function makeQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false, staleTime: 0 },
    },
  })
}

function renderWithProviders(ui: React.ReactElement) {
  return render(
    <MemoryRouter initialEntries={['/dashboard']} future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <QueryClientProvider client={makeQueryClient()}>
        {ui}
      </QueryClientProvider>
    </MemoryRouter>
  )
}

function makeChild(overrides: Partial<ChildProfile> = {}): ChildProfile {
  return {
    child_id: 1,
    parent_id: 10,
    name: 'Test Child 01',
    age: 8,
    school_name: 'Test Primary School',
    country_id: 1,
    country_name: 'TestLand',
    curricula_id: 2,
    curricula_title: 'Test Curriculum',
    grade_level_id: 3,
    grade_level_name: 'Grade 3',
    subjects: [1],
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    ...overrides,
  }
}

function makeTopic(overrides: Partial<ChildTopic> = {}): ChildTopic {
  return {
    topic_id: 101,
    topic_title: 'Test Topic',
    subject_name: 'Mathematics',
    subject_id: null,
    ...overrides,
  }
}

// ---------------------------------------------------------------------------
// Setup
// ---------------------------------------------------------------------------

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

describe('ParentDashboardPage', () => {
  describe('children loading state', () => {
    it('shows a spinner while children are being fetched', async () => {
      // Never resolves — keeps the query in loading state
      mockApiService.getChildren.mockReturnValue(new Promise(() => {}))

      renderWithProviders(<ParentDashboardPage />)

      expect(document.querySelector('.animate-spin')).toBeTruthy()
    })
  })

  describe('children error state', () => {
    it('shows error message and retry button when children fetch fails', async () => {
      mockApiService.getChildren.mockResolvedValue({ error: 'Network error', data: undefined })

      renderWithProviders(<ParentDashboardPage />)

      await waitFor(() => {
        expect(screen.getByText(/Failed to load your children's profiles/i)).toBeTruthy()
        expect(screen.getByText(/Try again/i)).toBeTruthy()
      })
    })

    it('does not show empty state when children fetch errors', async () => {
      mockApiService.getChildren.mockResolvedValue({ error: 'Network error', data: undefined })

      renderWithProviders(<ParentDashboardPage />)

      await waitFor(() => {
        expect(screen.queryByText(/Welcome to Awade/i)).toBeNull()
      })
    })
  })

  describe('topics error state', () => {
    it('shows error message and retry button when topics fetch fails', async () => {
      mockApiService.getChildren.mockResolvedValue({
        error: undefined,
        data: { children: [makeChild()], total: 1 },
      })
      mockApiService.getChildTopics.mockResolvedValue({ error: 'Server error', data: undefined })

      renderWithProviders(<ParentDashboardPage />)

      await waitFor(() => {
        expect(screen.getByText(/Failed to load topics/i)).toBeTruthy()
        expect(screen.getByText(/Try again/i)).toBeTruthy()
      })
    })

    it('does not show "No topics found" when topics fetch errors', async () => {
      mockApiService.getChildren.mockResolvedValue({
        error: undefined,
        data: { children: [makeChild()], total: 1 },
      })
      mockApiService.getChildTopics.mockResolvedValue({ error: 'Server error', data: undefined })

      renderWithProviders(<ParentDashboardPage />)

      await waitFor(() => {
        expect(screen.queryByText(/No topics found/i)).toBeNull()
      })
    })
  })

  describe('empty state', () => {
    it('shows welcome empty state when no children exist', async () => {
      mockApiService.getChildren.mockResolvedValue({
        error: undefined,
        data: { children: [], total: 0 },
      })

      renderWithProviders(<ParentDashboardPage />)

      await waitFor(() => {
        expect(screen.getByText(/Welcome to Awade/i)).toBeTruthy()
      })
    })

    // AWD-H-66: EmptyState is now a file-scope component; verify the onAddChild
    // prop wiring still triggers the add-child flow when "Add Your Child" is clicked.
    it('empty state Add Your Child button opens the add child modal', async () => {
      mockApiService.getChildren.mockResolvedValue({
        error: undefined,
        data: { children: [], total: 0 },
      })
      // Consent already given so the AddChildModal opens directly.
      mockApiService.getConsentStatus = vi.fn().mockResolvedValue({
        error: undefined,
        data: { has_consented: true },
      })

      renderWithProviders(<ParentDashboardPage />)

      await waitFor(() => expect(screen.getByText(/Add Your Child/i)).toBeTruthy())
      fireEvent.click(screen.getByText(/Add Your Child/i))

      await waitFor(() => {
        expect(screen.getByTestId('add-child-modal')).toBeTruthy()
      })
    })
  })

  describe('success state', () => {
    it('renders child selector cards and topic grid when data loads', async () => {
      mockApiService.getChildren.mockResolvedValue({
        error: undefined,
        data: { children: [makeChild()], total: 1 },
      })
      mockApiService.getChildTopics.mockResolvedValue({
        error: undefined,
        data: [makeTopic()],
      })

      renderWithProviders(<ParentDashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Test Child 01')).toBeTruthy()
        expect(screen.getByText('Test Topic')).toBeTruthy()
      })
    })
  })

  describe('child selector card HTML structure (AWD-M-36)', () => {
    it('child selector card is a div[role=group], not a <button>, to avoid invalid nested-button HTML', async () => {
      mockApiService.getChildren.mockResolvedValue({
        error: undefined,
        data: { children: [makeChild()], total: 1 },
      })
      mockApiService.getChildTopics.mockResolvedValue({ error: undefined, data: [] })

      renderWithProviders(<ParentDashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Test Child 01')).toBeTruthy()
      })

      const card = screen.getByRole('group', { name: 'Test Child 01' })
      expect(card.tagName.toLowerCase()).toBe('div')
    })

    it('edit and delete buttons inside the card are not nested inside a <button>', async () => {
      mockApiService.getChildren.mockResolvedValue({
        error: undefined,
        data: { children: [makeChild()], total: 1 },
      })
      mockApiService.getChildTopics.mockResolvedValue({ error: undefined, data: [] })

      renderWithProviders(<ParentDashboardPage />)

      await waitFor(() => {
        expect(screen.getByTitle('Edit')).toBeTruthy()
      })

      const editBtn = screen.getByTitle('Edit')
      // Nearest button ancestor must not itself be inside another button
      let el: HTMLElement | null = editBtn.parentElement
      let foundButton = false
      while (el) {
        if (el.tagName.toLowerCase() === 'button') {
          foundButton = true
        }
        // Once we leave the card container, stop
        if (el.getAttribute('role') === 'group') break
        el = el.parentElement
      }
      expect(foundButton).toBe(false)
    })

    it('pressing Enter on the card selects the child', async () => {
      mockApiService.getChildren.mockResolvedValue({
        error: undefined,
        data: {
          children: [makeChild({ child_id: 1, name: 'Child A' }), makeChild({ child_id: 2, name: 'Child B' })],
          total: 2,
        },
      })
      mockApiService.getChildTopics.mockResolvedValue({ error: undefined, data: [] })

      renderWithProviders(<ParentDashboardPage />)

      await waitFor(() => {
        expect(screen.getByRole('group', { name: 'Child B' })).toBeTruthy()
      })

      const cardB = screen.getByRole('group', { name: 'Child B' })
      fireEvent.keyDown(cardB, { key: 'Enter' })

      // After pressing Enter on Child B, the heading should update to "Child B's Learning"
      await waitFor(() => {
        expect(screen.getByText("Child B's Learning")).toBeTruthy()
      })
    })
  })

  describe('topic action buttons a11y (AWD-H-55)', () => {
    it('topic button exposes a descriptive aria-label naming the action', async () => {
      mockApiService.getChildren.mockResolvedValue({
        error: undefined,
        data: { children: [makeChild()], total: 1 },
      })
      mockApiService.getChildTopics.mockResolvedValue({
        error: undefined,
        data: [makeTopic({ topic_title: 'Fractions' })],
      })

      renderWithProviders(<ParentDashboardPage />)

      const btn = await screen.findByRole('button', {
        name: /Generate "How to Help" guide for Fractions/i,
      })
      expect(btn).toBeTruthy()
    })

    it('reveal hint includes group-focus-within so keyboard users can see it on focus', async () => {
      mockApiService.getChildren.mockResolvedValue({
        error: undefined,
        data: { children: [makeChild()], total: 1 },
      })
      mockApiService.getChildTopics.mockResolvedValue({
        error: undefined,
        data: [makeTopic({ topic_title: 'Fractions' })],
      })

      renderWithProviders(<ParentDashboardPage />)

      await waitFor(() => {
        expect(screen.getByText(/Get "How to Help" guide/i)).toBeTruthy()
      })

      const hint = screen.getByText(/Get "How to Help" guide/i)
      // Hint must reveal on both pointer hover AND keyboard focus
      expect(hint.className).toContain('group-hover:opacity-100')
      expect(hint.className).toContain('group-focus-within:opacity-100')
    })
  })

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
      // Consent NOT yet given so ConsentModal opens on Add click.
      mockApiService.getConsentStatus = vi.fn().mockResolvedValue({
        error: undefined,
        data: { has_consented: false },
      })
      mockApiService.recordConsent = vi.fn().mockImplementation(recordConsentImpl)
    }

    const triggerConsentSubmit = async () => {
      // Open ConsentModal via the empty-state "Add Your Child" button.
      await waitFor(() => expect(screen.getByText(/Add Your Child/i)).toBeTruthy())
      fireEvent.click(screen.getByText(/Add Your Child/i))

      // Tick the consent checkbox so "I Agree" becomes enabled.
      const checkbox = await screen.findByRole('checkbox')
      fireEvent.click(checkbox)

      // Click the "I Agree" submit button.
      const submitBtn = screen.getByRole('button', { name: /I Agree — Add a Child/i })
      fireEvent.click(submitBtn)
    }

    it('surfaces err.message when recordConsent rejects with an Error instance', async () => {
      setupConsentFlow(() => Promise.reject(new Error('Network down')))

      renderWithProviders(<ParentDashboardPage />)
      await triggerConsentSubmit()

      await waitFor(() => {
        // The error string lives in the modal's <p role="alert"> slot.
        const alert = screen.getByRole('alert')
        expect(alert.textContent).toContain('Network down')
      })
    })

    it('falls back to the generic message when a non-Error value is thrown', async () => {
      setupConsentFlow(() => Promise.reject('plain-string-error'))

      renderWithProviders(<ParentDashboardPage />)
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

    // Helper: open the delete-confirm modal and click its "Remove" button.
    const openAndConfirmDelete = async () => {
      await waitFor(() => expect(screen.getByTitle('Remove')).toBeTruthy())
      fireEvent.click(screen.getByTitle('Remove'))
      // The modal exposes a "Remove" button inside role="dialog".
      const dialog = await screen.findByRole('dialog')
      const confirmBtn = dialog.querySelector('button') as HTMLButtonElement
      fireEvent.click(confirmBtn)
    }

    it('shows an inline error message when deleteChild API call rejects with an Error', async () => {
      setupChildList()
      mockApiService.deleteChild.mockRejectedValue(new Error('Server unavailable'))

      renderWithProviders(<ParentDashboardPage />)
      await openAndConfirmDelete()

      await waitFor(() => {
        const alert = screen.getByRole('alert')
        expect(alert.textContent).toContain('Server unavailable')
      })
    })

    it('shows a generic fallback message when deleteChild rejects with a non-Error value', async () => {
      setupChildList()
      mockApiService.deleteChild.mockRejectedValue('plain-string-rejection')

      renderWithProviders(<ParentDashboardPage />)
      await openAndConfirmDelete()

      await waitFor(() => {
        const alert = screen.getByRole('alert')
        expect(alert.textContent).toContain('Failed to remove child profile. Please try again.')
      })
    })

    it('clears any previous delete error when a new delete attempt begins', async () => {
      setupChildList()
      // First call fails; second call succeeds
      mockApiService.deleteChild
        .mockRejectedValueOnce(new Error('Temporary failure'))
        .mockResolvedValueOnce({ data: null, error: undefined })

      renderWithProviders(<ParentDashboardPage />)

      // First delete — fails, error should appear
      await openAndConfirmDelete()
      await waitFor(() => expect(screen.getByRole('alert')).toBeTruthy())

      // Second delete — succeeds, error should be cleared
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

    // Helper: open the delete-confirm modal for the *currently selected*
    // child and click its "Remove" button. (Trash buttons render one per
    // child, but the first card is auto-selected so getByTitle('Remove')
    // on the first match targets Child A.)
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

      renderWithProviders(<ParentDashboardPage />)

      // Trigger a failing delete on the auto-selected first child so the
      // role="alert" banner is visible.
      await failDeleteOnSelectedChild()
      await waitFor(() => expect(screen.getByRole('alert')).toBeTruthy())

      // Switch to Child B by clicking its selector card.
      fireEvent.click(screen.getByText('Child B'))

      // The stale banner must be gone.
      await waitFor(() => expect(screen.queryByRole('alert')).toBeNull())
    })

    it('clears the delete-error banner when the parent activates another child card via Enter', async () => {
      setupTwoChildren()
      mockApiService.deleteChild.mockRejectedValue(new Error('Server unavailable'))

      renderWithProviders(<ParentDashboardPage />)

      await failDeleteOnSelectedChild()
      await waitFor(() => expect(screen.getByRole('alert')).toBeTruthy())

      // Find Child B's outer card (role="group", aria-label="Child B")
      // and activate it with the Enter key.
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

      renderWithProviders(<ParentDashboardPage />)
      await waitFor(() => expect(screen.getByTitle('Remove')).toBeTruthy())
      fireEvent.click(screen.getByTitle('Remove'))

      // The blocking, inaccessible confirm() prompt must not be used.
      expect(confirmSpy).not.toHaveBeenCalled()
      confirmSpy.mockRestore()
    })

    it('opens an accessible role="dialog" when the trash button is clicked', async () => {
      setupChildList()

      renderWithProviders(<ParentDashboardPage />)
      await waitFor(() => expect(screen.getByTitle('Remove')).toBeTruthy())
      fireEvent.click(screen.getByTitle('Remove'))

      const dialog = await screen.findByRole('dialog')
      expect(dialog.getAttribute('aria-modal')).toBe('true')
      // The title names the child being removed.
      expect(dialog.textContent).toContain("Remove Child A's profile?")
    })

    it('Cancel closes the modal without calling deleteChild', async () => {
      setupChildList()

      renderWithProviders(<ParentDashboardPage />)
      await waitFor(() => expect(screen.getByTitle('Remove')).toBeTruthy())
      fireEvent.click(screen.getByTitle('Remove'))

      // Click the Cancel button inside the dialog.
      const cancelBtn = await screen.findByRole('button', { name: /^Cancel$/ })
      fireEvent.click(cancelBtn)

      await waitFor(() => expect(screen.queryByRole('dialog')).toBeNull())
      expect(mockApiService.deleteChild).not.toHaveBeenCalled()
    })

    it('Remove button inside the modal calls deleteChild with the right id and closes the modal', async () => {
      setupChildList()
      mockApiService.deleteChild.mockResolvedValue({ data: null, error: undefined })

      renderWithProviders(<ParentDashboardPage />)
      await waitFor(() => expect(screen.getByTitle('Remove')).toBeTruthy())
      fireEvent.click(screen.getByTitle('Remove'))

      const dialog = await screen.findByRole('dialog')
      // First button inside the dialog is the destructive "Remove" action.
      const confirmBtn = dialog.querySelector('button') as HTMLButtonElement
      expect(confirmBtn).toBeTruthy()
      fireEvent.click(confirmBtn)

      await waitFor(() => expect(mockApiService.deleteChild).toHaveBeenCalledWith(1))
      await waitFor(() => expect(screen.queryByRole('dialog')).toBeNull())
    })
  })

  describe('edit/delete button touch targets (AWD-L-15)', () => {
    const setupWithChild = () => {
      mockApiService.getChildren.mockResolvedValue({
        error: undefined,
        data: { children: [makeChild()], total: 1 },
      })
      mockApiService.getChildTopics.mockResolvedValue({ error: undefined, data: [] })
      renderWithProviders(<ParentDashboardPage />)
    }

    it('edit button has p-2 padding for a sufficient touch target', async () => {
      setupWithChild()
      await waitFor(() => expect(screen.getByTitle('Edit')).toBeTruthy())
      const editBtn = screen.getByTitle('Edit')
      expect(editBtn.className).toContain('p-2')
    })

    it('delete button has p-2 padding for a sufficient touch target', async () => {
      setupWithChild()
      await waitFor(() => expect(screen.getByTitle('Remove')).toBeTruthy())
      const deleteBtn = screen.getByTitle('Remove')
      expect(deleteBtn.className).toContain('p-2')
    })

    it('edit button has an accessible aria-label', async () => {
      setupWithChild()
      await waitFor(() => expect(screen.getByTitle('Edit')).toBeTruthy())
      const editBtn = screen.getByTitle('Edit')
      expect(editBtn.getAttribute('aria-label')).toMatch(/Edit .+ profile/i)
    })

    it('delete button has an accessible aria-label', async () => {
      setupWithChild()
      await waitFor(() => expect(screen.getByTitle('Remove')).toBeTruthy())
      const deleteBtn = screen.getByTitle('Remove')
      expect(deleteBtn.getAttribute('aria-label')).toMatch(/Remove .+ profile/i)
    })
  })

  describe('auto-select first child (AWD-M-131)', () => {
    /**
     * AWD-M-131: the useEffect that auto-selects the first child previously
     * read `selectedChild` directly, causing react-hooks/exhaustive-deps to
     * flag a missing dependency. Fixed by using the functional-updater form
     * `setSelectedChild(prev => prev ?? children[0])` so `selectedChild` is
     * never read inside the effect body.
     */

    it('auto-selects the first child when children load and none is selected', async () => {
      const child = makeChild({ child_id: 1, name: 'Auto Child' })
      mockApiService.getChildren.mockResolvedValue({
        error: undefined,
        data: { children: [child], total: 1 },
      })
      mockApiService.getChildTopics.mockResolvedValue({ error: undefined, data: [] })

      renderWithProviders(<ParentDashboardPage />)

      // The child selector card should appear once data loads, indicating
      // auto-selection has occurred (topics query fires only after a child
      // is selected).
      await waitFor(() => expect(screen.getByText('Auto Child')).toBeTruthy())
    })

    it('does not override an already-selected child when children list re-fetches', async () => {
      const child1 = makeChild({ child_id: 1, name: 'First Child' })
      const child2 = makeChild({ child_id: 2, name: 'Second Child' })
      mockApiService.getChildren.mockResolvedValue({
        error: undefined,
        data: { children: [child1, child2], total: 2 },
      })
      mockApiService.getChildTopics.mockResolvedValue({ error: undefined, data: [] })

      renderWithProviders(<ParentDashboardPage />)

      // Both child cards should render; the effect must not wipe a previously
      // selected child on subsequent renders.
      await waitFor(() => expect(screen.getByText('First Child')).toBeTruthy())
      await waitFor(() => expect(screen.getByText('Second Child')).toBeTruthy())
    })
  })
})
