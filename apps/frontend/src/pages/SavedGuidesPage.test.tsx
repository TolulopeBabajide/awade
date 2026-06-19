import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import SavedGuidesPage from './SavedGuidesPage'

// ---------------------------------------------------------------------------
// Module mocks
// ---------------------------------------------------------------------------

vi.mock('../services/api', () => ({
  default: {
    getChildren: vi.fn(),
    getChildGuides: vi.fn(),
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

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

import apiService from '../services/api'
import type { ChildProfile, ParentGuide } from '../types/children'

const mockApiService = vi.mocked(apiService)

function makeQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false, staleTime: 0 },
    },
  })
}

function renderWithProviders(ui: React.ReactElement) {
  return render(
    <MemoryRouter initialEntries={['/saved-guides']} future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
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
    school_name: 'Test School',
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

function makeGuide(overrides: Partial<ParentGuide> = {}): ParentGuide {
  return {
    guide_id: 201,
    child_id: 1,
    topic_id: 101,
    topic_title: 'Test Topic',
    subject_name: 'Mathematics',
    ai_generated_content: '{}',
    user_edited_content: null,
    is_bookmarked: false,
    created_at: '2026-01-15T00:00:00Z',
    updated_at: '2026-01-15T00:00:00Z',
    ...overrides,
  }
}

function setupChildrenLoaded() {
  mockApiService.getChildren.mockResolvedValue({
    error: undefined,
    data: { children: [makeChild()], total: 1 },
  })
}

// ---------------------------------------------------------------------------
// Setup
// ---------------------------------------------------------------------------

beforeEach(() => {
  vi.clearAllMocks()
})

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('SavedGuidesPage', () => {
  describe('children loading state', () => {
    it('shows a spinner while children are being fetched', async () => {
      mockApiService.getChildren.mockReturnValue(new Promise(() => {}))

      renderWithProviders(<SavedGuidesPage />)

      expect(document.querySelector('.animate-spin')).toBeTruthy()
    })
  })

  describe('children error state', () => {
    it('shows error message and retry button when children fetch fails', async () => {
      mockApiService.getChildren.mockResolvedValue({ error: 'Network error', data: undefined })

      renderWithProviders(<SavedGuidesPage />)

      await waitFor(() => {
        expect(screen.getByText(/Failed to load profiles/i)).toBeTruthy()
        expect(screen.getByText(/Try again/i)).toBeTruthy()
      }, { timeout: 5000 })
    })

    it('does not render child selector when children fetch errors', async () => {
      mockApiService.getChildren.mockResolvedValue({ error: 'Network error', data: undefined })

      renderWithProviders(<SavedGuidesPage />)

      await waitFor(() => {
        // Guides list and child selector should not be rendered
        expect(screen.queryByText(/No guides yet/i)).toBeNull()
      }, { timeout: 5000 })
    })
  })

  describe('guides error state', () => {
    beforeEach(() => {
      setupChildrenLoaded()
    })

    it('shows error message and retry button when guides fetch fails', async () => {
      mockApiService.getChildGuides.mockResolvedValue({ error: 'Server error', data: undefined })

      renderWithProviders(<SavedGuidesPage />)

      await waitFor(() => {
        expect(screen.getByText(/Failed to load guides/i)).toBeTruthy()
        expect(screen.getByText(/Try again/i)).toBeTruthy()
      }, { timeout: 5000 })
    })

    it('does not show empty state when guides fetch errors', async () => {
      mockApiService.getChildGuides.mockResolvedValue({ error: 'Server error', data: undefined })

      renderWithProviders(<SavedGuidesPage />)

      await waitFor(() => {
        expect(screen.queryByText(/No guides yet/i)).toBeNull()
      }, { timeout: 5000 })
    })
  })

  describe('guides loading state', () => {
    it('shows spinner while guides are loading', async () => {
      setupChildrenLoaded()
      mockApiService.getChildGuides.mockReturnValue(new Promise(() => {}))

      renderWithProviders(<SavedGuidesPage />)

      await waitFor(() => {
        // After children load, guides spinner should appear
        expect(document.querySelector('.animate-spin')).toBeTruthy()
      }, { timeout: 5000 })
    })
  })

  describe('empty guides state', () => {
    it('shows empty state message when no guides exist', async () => {
      setupChildrenLoaded()
      mockApiService.getChildGuides.mockResolvedValue({
        error: undefined,
        data: { guides: [], total: 0 },
      })

      renderWithProviders(<SavedGuidesPage />)

      await waitFor(() => {
        expect(screen.getByText(/No guides yet/i)).toBeTruthy()
      }, { timeout: 5000 })
    })
  })

  describe('success state', () => {
    it('renders guide cards when guides load successfully', async () => {
      setupChildrenLoaded()
      mockApiService.getChildGuides.mockResolvedValue({
        error: undefined,
        data: { guides: [makeGuide()], total: 1 },
      })

      renderWithProviders(<SavedGuidesPage />)

      await waitFor(() => {
        expect(screen.getByText('Test Topic')).toBeTruthy()
      }, { timeout: 5000 })
    })
  })

  describe('guide card a11y (AWD-H-55)', () => {
    beforeEach(() => {
      setupChildrenLoaded()
    })

    it('guide card exposes a descriptive aria-label naming the action', async () => {
      mockApiService.getChildGuides.mockResolvedValue({
        error: undefined,
        data: { guides: [makeGuide({ topic_title: 'Fractions' })], total: 1 },
      })

      renderWithProviders(<SavedGuidesPage />)

      const btn = await screen.findByRole('button', {
        name: /Open "How to Help" guide for Fractions/i,
      }, { timeout: 10000 })
      expect(btn).toBeTruthy()
    })

    it('aria-label notes when a guide is bookmarked', async () => {
      mockApiService.getChildGuides.mockResolvedValue({
        error: undefined,
        data: {
          guides: [makeGuide({ topic_title: 'Fractions', is_bookmarked: true })],
          total: 1,
        },
      })

      renderWithProviders(<SavedGuidesPage />)

      const btn = await screen.findByRole('button', {
        name: /Open "How to Help" guide for Fractions \(bookmarked\)/i,
      }, { timeout: 10000 })
      expect(btn).toBeTruthy()
    })
  })
})
