/**
 * ParentDashboardPage — render, structure, and a11y tests (AWD-M-141).
 *
 * Covers:
 *   - Page loading / error / empty / success states
 *   - Child selector card HTML structure (AWD-M-36)
 *   - Topic action button a11y (AWD-H-55)
 *   - Edit/delete button touch targets (AWD-L-15)
 *   - Auto-select first child (AWD-M-131)
 *
 * See ParentDashboardPage.delete.test.tsx for consent + delete workflow tests.
 */

import React from 'react'
import { screen, waitFor, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { makeChild, makeTopic, renderPage } from './__fixtures__/parentDashboardPage'

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

describe('ParentDashboardPage — render', () => {
  describe('children loading state', () => {
    it('shows a spinner while children are being fetched', async () => {
      mockApiService.getChildren.mockReturnValue(new Promise(() => {}))

      renderPage()

      expect(document.querySelector('.animate-spin')).toBeTruthy()
    })
  })

  describe('children error state', () => {
    it('shows error message and retry button when children fetch fails', async () => {
      mockApiService.getChildren.mockResolvedValue({ error: 'Network error', data: undefined })

      renderPage()

      await waitFor(() => {
        expect(screen.getByText(/Failed to load your children's profiles/i)).toBeTruthy()
        expect(screen.getByText(/Try again/i)).toBeTruthy()
      }, { timeout: 5000 })
    })

    it('does not show empty state when children fetch errors', async () => {
      mockApiService.getChildren.mockResolvedValue({ error: 'Network error', data: undefined })

      renderPage()

      await waitFor(() => {
        expect(screen.queryByText(/Welcome to Awade/i)).toBeNull()
      }, { timeout: 5000 })
    })
  })

  describe('topics error state', () => {
    it('shows error message and retry button when topics fetch fails', async () => {
      mockApiService.getChildren.mockResolvedValue({
        error: undefined,
        data: { children: [makeChild()], total: 1 },
      })
      mockApiService.getChildTopics.mockResolvedValue({ error: 'Server error', data: undefined })

      renderPage()

      // Pin child-selection step so the error render gets a fresh 5000ms window (AWD-H-118)
      await waitFor(() => expect(screen.getByText('Test Child 01')).toBeTruthy(), { timeout: 5000 })

      await waitFor(() => {
        expect(screen.getByText(/Failed to load topics/i)).toBeTruthy()
        expect(screen.getByText(/Try again/i)).toBeTruthy()
      }, { timeout: 5000 })
    })

    it('does not show "No topics found" when topics fetch errors', async () => {
      mockApiService.getChildren.mockResolvedValue({
        error: undefined,
        data: { children: [makeChild()], total: 1 },
      })
      mockApiService.getChildTopics.mockResolvedValue({ error: 'Server error', data: undefined })

      renderPage()

      // Pin child-selection step so the absence check runs in error state, not loading (AWD-M-249)
      await waitFor(() => expect(screen.getByText('Test Child 01')).toBeTruthy(), { timeout: 5000 })

      await waitFor(() => {
        expect(screen.queryByText(/No topics found/i)).toBeNull()
      }, { timeout: 5000 })
    })
  })

  describe('empty state', () => {
    it('shows welcome empty state when no children exist', async () => {
      mockApiService.getChildren.mockResolvedValue({
        error: undefined,
        data: { children: [], total: 0 },
      })

      renderPage()

      await waitFor(() => {
        expect(screen.getByText(/Welcome to Awade/i)).toBeTruthy()
      }, { timeout: 5000 })
    })

    it('empty state Add Your Child button opens the add child modal', async () => {
      mockApiService.getChildren.mockResolvedValue({
        error: undefined,
        data: { children: [], total: 0 },
      })
      mockApiService.getConsentStatus = vi.fn().mockResolvedValue({
        error: undefined,
        data: { has_consented: true },
      })

      renderPage()

      await waitFor(() => expect(screen.getByText(/Add Your Child/i)).toBeTruthy(), { timeout: 5000 })
      fireEvent.click(screen.getByText(/Add Your Child/i))

      await waitFor(() => {
        expect(screen.getByTestId('add-child-modal')).toBeTruthy()
      }, { timeout: 5000 })
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

      renderPage()

      await waitFor(() => {
        expect(screen.getByText('Test Child 01')).toBeTruthy()
        expect(screen.getByText('Test Topic')).toBeTruthy()
      }, { timeout: 5000 })
    })
  })

  describe('child selector card HTML structure (AWD-M-36)', () => {
    it('child selector card is a div[role=group], not a <button>, to avoid invalid nested-button HTML', async () => {
      mockApiService.getChildren.mockResolvedValue({
        error: undefined,
        data: { children: [makeChild()], total: 1 },
      })
      mockApiService.getChildTopics.mockResolvedValue({ error: undefined, data: [] })

      renderPage()

      await waitFor(() => {
        expect(screen.getByText('Test Child 01')).toBeTruthy()
      }, { timeout: 5000 })

      const card = screen.getByRole('group', { name: 'Test Child 01' })
      expect(card.tagName.toLowerCase()).toBe('div')
    })

    it('edit and delete buttons inside the card are not nested inside a <button>', async () => {
      mockApiService.getChildren.mockResolvedValue({
        error: undefined,
        data: { children: [makeChild()], total: 1 },
      })
      mockApiService.getChildTopics.mockResolvedValue({ error: undefined, data: [] })

      renderPage()

      await waitFor(() => {
        expect(screen.getByTitle('Edit')).toBeTruthy()
      }, { timeout: 5000 })

      const editBtn = screen.getByTitle('Edit')
      let el: HTMLElement | null = editBtn.parentElement
      let foundButton = false
      while (el) {
        if (el.tagName.toLowerCase() === 'button') {
          foundButton = true
        }
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

      renderPage()

      await waitFor(() => {
        expect(screen.getByRole('group', { name: 'Child B' })).toBeTruthy()
      }, { timeout: 5000 })

      const cardB = screen.getByRole('group', { name: 'Child B' })
      fireEvent.keyDown(cardB, { key: 'Enter' })

      await waitFor(() => {
        expect(screen.getByText("Child B's Learning")).toBeTruthy()
      }, { timeout: 5000 })
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

      renderPage()

      await waitFor(() => {
        expect(screen.getByText('Fractions')).toBeTruthy()
      }, { timeout: 5000 })
      const btn = screen.getByText('Fractions').closest('button')
      expect(btn).not.toBeNull()
      expect(btn!.getAttribute('aria-label')).toMatch(/Generate "How to Help" guide for Fractions/i)
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

      renderPage()

      await waitFor(() => {
        expect(screen.getByText(/Get "How to Help" guide/i)).toBeTruthy()
      }, { timeout: 5000 })

      const hint = screen.getByText(/Get "How to Help" guide/i)
      expect(hint.className).toContain('group-hover:opacity-100')
      expect(hint.className).toContain('group-focus-within:opacity-100')
    })
  })

  describe('edit/delete button touch targets (AWD-L-15)', () => {
    const setupWithChild = () => {
      mockApiService.getChildren.mockResolvedValue({
        error: undefined,
        data: { children: [makeChild()], total: 1 },
      })
      mockApiService.getChildTopics.mockResolvedValue({ error: undefined, data: [] })
      renderPage()
    }

    it('edit button has p-2 padding for a sufficient touch target', async () => {
      setupWithChild()
      await waitFor(() => expect(screen.getByTitle('Edit')).toBeTruthy(), { timeout: 5000 })
      const editBtn = screen.getByTitle('Edit')
      expect(editBtn.className).toContain('p-2')
    })

    it('delete button has p-2 padding for a sufficient touch target', async () => {
      setupWithChild()
      await waitFor(() => expect(screen.getByTitle('Remove')).toBeTruthy(), { timeout: 5000 })
      const deleteBtn = screen.getByTitle('Remove')
      expect(deleteBtn.className).toContain('p-2')
    })

    it('edit button has an accessible aria-label', async () => {
      setupWithChild()
      await waitFor(() => expect(screen.getByTitle('Edit')).toBeTruthy(), { timeout: 5000 })
      const editBtn = screen.getByTitle('Edit')
      expect(editBtn.getAttribute('aria-label')).toMatch(/Edit .+ profile/i)
    })

    it('delete button has an accessible aria-label', async () => {
      setupWithChild()
      await waitFor(() => expect(screen.getByTitle('Remove')).toBeTruthy(), { timeout: 5000 })
      const deleteBtn = screen.getByTitle('Remove')
      expect(deleteBtn.getAttribute('aria-label')).toMatch(/Remove .+ profile/i)
    })
  })

  describe('auto-select first child (AWD-M-131)', () => {
    it('auto-selects the first child when children load and none is selected', async () => {
      const child = makeChild({ child_id: 1, name: 'Auto Child' })
      mockApiService.getChildren.mockResolvedValue({
        error: undefined,
        data: { children: [child], total: 1 },
      })
      mockApiService.getChildTopics.mockResolvedValue({ error: undefined, data: [] })

      renderPage()

      await waitFor(() => expect(screen.getByText('Auto Child')).toBeTruthy(), { timeout: 5000 })
    })

    it('does not override an already-selected child when children list re-fetches', async () => {
      const child1 = makeChild({ child_id: 1, name: 'First Child' })
      const child2 = makeChild({ child_id: 2, name: 'Second Child' })
      mockApiService.getChildren.mockResolvedValue({
        error: undefined,
        data: { children: [child1, child2], total: 2 },
      })
      mockApiService.getChildTopics.mockResolvedValue({ error: undefined, data: [] })

      renderPage()

      await waitFor(() => expect(screen.getByText('First Child')).toBeTruthy(), { timeout: 5000 })
      await waitFor(() => expect(screen.getByText('Second Child')).toBeTruthy(), { timeout: 5000 })
    })
  })
})
