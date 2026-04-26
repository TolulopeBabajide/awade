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
      user_id: 10,
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
})
