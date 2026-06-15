import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import ChildrenPage from './ChildrenPage'

// ---------------------------------------------------------------------------
// Module mocks
// ---------------------------------------------------------------------------

vi.mock('../services/api', () => ({
  default: {
    getChildren: vi.fn(),
    deleteChild: vi.fn(),
  },
}))

vi.mock('../contexts/AuthContext', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  useAuth: vi.fn(),
}))

// Stub heavy sub-components — we only care about ChildrenPage logic
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
import type { ChildProfile } from '../types/children'

const mockApiService = vi.mocked(apiService)
const mockUseAuth = useAuth as ReturnType<typeof vi.fn>

/** Build a fresh QueryClient for each test to avoid cache bleed-through. */
function makeQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,          // fail fast in tests
        staleTime: 0,
      },
    },
  })
}

/** Wrapper that supplies Router + QueryClient context. */
function renderWithProviders(ui: React.ReactElement, { queryClient = makeQueryClient() } = {}) {
  return render(
    <MemoryRouter initialEntries={['/children']} future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <QueryClientProvider client={queryClient}>
        {ui}
      </QueryClientProvider>
    </MemoryRouter>
  )
}

/** Synthetic child profile factory — no real PII. */
function makeChild(overrides: Partial<ChildProfile> = {}): ChildProfile {
  return { ...defaultChild(), ...overrides }
}

function defaultChild(): ChildProfile {
  return {
    child_id: 1,
    parent_id: 10,
    name: 'Test Child 01',
    age: 8,
    school_name: 'Test Primary School',
    country_id: 1,
    country_name: 'TestLand',
    curricula_id: 2,
    curricula_title: 'Test National Curriculum',
    grade_level_id: 3,
    grade_level_name: 'Grade 3',
    subjects: [1, 2],
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  }
}

// ---------------------------------------------------------------------------
// Setup / teardown
// ---------------------------------------------------------------------------

beforeEach(() => {
  vi.clearAllMocks()

  // Default: authenticated PARENT
  mockUseAuth.mockReturnValue({
    user: { user_id: 10, email: 'parent@test.invalid', full_name: 'Test Parent', role: 'PARENT', country: 'ZZ' },
    isAuthenticated: true,
    isLoading: false,
    login: vi.fn(),
    signup: vi.fn(),
    googleAuth: vi.fn(),
    logout: vi.fn(),
    validateToken: vi.fn(),
  })

  // Default: window.confirm returns true
  vi.spyOn(window, 'confirm').mockReturnValue(true)
})

afterEach(() => {
  vi.restoreAllMocks()
})

// ---------------------------------------------------------------------------
// 1. Loading state
// ---------------------------------------------------------------------------

describe('ChildrenPage — loading state', () => {
  it('renders a loading spinner while the query is in flight', async () => {
    // Never resolves so the component stays in loading state
    mockApiService.getChildren.mockReturnValue(new Promise(() => {}))
    renderWithProviders(<ChildrenPage />)

    // The spinner is a div with class animate-spin — no ARIA role on the element
    const spinner = document.querySelector('.animate-spin')
    expect(spinner).toBeInTheDocument()
  })

  it('does not show error or empty state while loading', async () => {
    mockApiService.getChildren.mockReturnValue(new Promise(() => {}))
    renderWithProviders(<ChildrenPage />)

    expect(screen.queryByText(/Unable to load children profiles/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/No children added yet/i)).not.toBeInTheDocument()
  })
})

// ---------------------------------------------------------------------------
// 2. Error state
// ---------------------------------------------------------------------------

describe('ChildrenPage — error state', () => {
  it('shows error message when the query fails', async () => {
    mockApiService.getChildren.mockResolvedValue({ error: 'Network error', data: undefined })
    renderWithProviders(<ChildrenPage />)

    await waitFor(() =>
      expect(screen.getByText(/Unable to load children profiles/i)).toBeInTheDocument()
    )
  })

  it('renders a "Try again" button in the error state', async () => {
    mockApiService.getChildren.mockResolvedValue({ error: 'Timeout', data: undefined })
    renderWithProviders(<ChildrenPage />)

    await waitFor(() =>
      expect(screen.getByRole('button', { name: /Try again/i })).toBeInTheDocument()
    , { timeout: 5000 })
  })

  it('"Try again" refetches the data', async () => {
    mockApiService.getChildren
      .mockResolvedValueOnce({ error: 'Server error', data: undefined })
      .mockResolvedValueOnce({ data: { children: [], total: 0 }, error: undefined })

    renderWithProviders(<ChildrenPage />)

    const retryBtn = await screen.findByRole('button', { name: /Try again/i }, { timeout: 5000 })
    fireEvent.click(retryBtn)

    // After retry, the query should run again — empty state should appear
    await waitFor(() =>
      expect(screen.getByText(/No children added yet/i)).toBeInTheDocument()
    , { timeout: 5000 })
    expect(mockApiService.getChildren).toHaveBeenCalledTimes(2)
  })
})

// ---------------------------------------------------------------------------
// 3. Empty state
// ---------------------------------------------------------------------------

describe('ChildrenPage — empty state', () => {
  beforeEach(() => {
    mockApiService.getChildren.mockResolvedValue({ data: { children: [], total: 0 }, error: undefined })
  })

  it('renders the empty state heading', async () => {
    renderWithProviders(<ChildrenPage />)
    await waitFor(() =>
      expect(screen.getByText(/No children added yet/i)).toBeInTheDocument()
    )
  })

  it('renders the "Add Your First Child" CTA button', async () => {
    renderWithProviders(<ChildrenPage />)
    await waitFor(() =>
      expect(screen.getByRole('button', { name: /Add Your First Child/i })).toBeInTheDocument()
    , { timeout: 5000 })
  })

  it('opens the AddChildModal when the CTA is clicked', async () => {
    renderWithProviders(<ChildrenPage />)
    const cta = await screen.findByRole('button', { name: /Add Your First Child/i }, { timeout: 5000 })
    fireEvent.click(cta)
    expect(screen.getByTestId('add-child-modal')).toBeInTheDocument()
  })

  it('renders the top-bar "Add Child" button in empty state', async () => {
    renderWithProviders(<ChildrenPage />)
    await waitFor(() =>
      // The top-bar button has visible text "Add Child" on sm+ screens
      expect(screen.getAllByRole('button').some(b => b.textContent?.includes('Add Child'))).toBeTruthy()
    )
  })
})

// ---------------------------------------------------------------------------
// 4. Children grid — happy path
// ---------------------------------------------------------------------------

describe('ChildrenPage — children grid', () => {
  const child1 = makeChild({ child_id: 1, name: 'Test Child 01' })
  const child2 = makeChild({ child_id: 2, name: 'Test Child 02', age: 10 })

  beforeEach(() => {
    mockApiService.getChildren.mockResolvedValue({
      data: { children: [child1, child2], total: 2 },
      error: undefined,
    })
  })

  it('renders a card for each child profile', async () => {
    renderWithProviders(<ChildrenPage />)
    await waitFor(() => {
      expect(screen.getByText('Test Child 01')).toBeInTheDocument()
      expect(screen.getByText('Test Child 02')).toBeInTheDocument()
    })
  })

  it('displays child age when available', async () => {
    renderWithProviders(<ChildrenPage />)
    await waitFor(() => expect(screen.getByText(/Age 8/i)).toBeInTheDocument())
    expect(screen.getByText(/Age 10/i)).toBeInTheDocument()
  })

  it('displays school name when available', async () => {
    renderWithProviders(<ChildrenPage />)
    await waitFor(() =>
      expect(screen.getAllByText('Test Primary School').length).toBeGreaterThan(0)
    )
  })

  it('displays grade level and curriculum info', async () => {
    renderWithProviders(<ChildrenPage />)
    await waitFor(() => {
      expect(screen.getAllByText('Grade 3').length).toBeGreaterThan(0)
      expect(screen.getAllByText('Test National Curriculum').length).toBeGreaterThan(0)
    })
  })

  it('renders an "Add another child" card', async () => {
    renderWithProviders(<ChildrenPage />)
    expect(await screen.findByRole('button', { name: /Add another child/i }, { timeout: 5000 })).toBeInTheDocument()
  })

  it('shows "Curriculum not set" nudge for profiles missing curriculum/grade', async () => {
    const incomplete = makeChild({ child_id: 3, name: 'Test Child 03', curricula_id: null, grade_level_id: null })
    mockApiService.getChildren.mockResolvedValue({
      data: { children: [incomplete], total: 1 },
      error: undefined,
    })
    renderWithProviders(<ChildrenPage />)
    await waitFor(() =>
      expect(screen.getByText(/Curriculum not set/i)).toBeInTheDocument()
    )
  })

  it('opens edit modal when the edit button is clicked', async () => {
    renderWithProviders(<ChildrenPage />)
    await waitFor(() => expect(screen.getByText('Test Child 01')).toBeInTheDocument())

    const editBtns = screen.getAllByRole('button', { name: /Edit .+ profile/i })
    fireEvent.click(editBtns[0])

    expect(screen.getByTestId('add-child-modal')).toBeInTheDocument()
  })
})

// ---------------------------------------------------------------------------
// 5. Delete flow
// ---------------------------------------------------------------------------

describe('ChildrenPage — delete flow', () => {
  const child = makeChild({ child_id: 99, name: 'Test Child Delete' })

  beforeEach(() => {
    mockApiService.getChildren.mockResolvedValue({
      data: { children: [child], total: 1 },
      error: undefined,
    })
  })

  it('calls deleteChild after user confirms', async () => {
    mockApiService.deleteChild.mockResolvedValue({ error: undefined, data: null })
    renderWithProviders(<ChildrenPage />)

    await waitFor(() => expect(screen.getByText('Test Child Delete')).toBeInTheDocument())
    const deleteBtn = screen.getByRole('button', { name: /Remove Test Child Delete/i })
    fireEvent.click(deleteBtn)

    expect(window.confirm).toHaveBeenCalledOnce()
    await waitFor(() => expect(mockApiService.deleteChild).toHaveBeenCalledWith(99))
  })

  it('does NOT call deleteChild when user cancels the confirm dialog', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(false)
    renderWithProviders(<ChildrenPage />)

    await waitFor(() => expect(screen.getByText('Test Child Delete')).toBeInTheDocument())
    const deleteBtn = screen.getByRole('button', { name: /Remove Test Child Delete/i })
    fireEvent.click(deleteBtn)

    expect(mockApiService.deleteChild).not.toHaveBeenCalled()
  })

  it('shows a delete error banner when deleteChild returns an error', async () => {
    mockApiService.deleteChild.mockResolvedValue({ error: 'Delete failed', data: undefined })
    renderWithProviders(<ChildrenPage />)

    await waitFor(() => expect(screen.getByText('Test Child Delete')).toBeInTheDocument())
    fireEvent.click(screen.getByRole('button', { name: /Remove Test Child Delete/i }))

    await waitFor(() =>
      expect(screen.getByText(/Delete failed/i)).toBeInTheDocument()
    )
  })

  it('shows a generic error banner when deleteChild throws', async () => {
    mockApiService.deleteChild.mockRejectedValue(new Error('Network down'))
    renderWithProviders(<ChildrenPage />)

    await waitFor(() => expect(screen.getByText('Test Child Delete')).toBeInTheDocument())
    fireEvent.click(screen.getByRole('button', { name: /Remove Test Child Delete/i }))

    await waitFor(() =>
      expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument()
    )
  })

  it('disables the delete button while the delete is in flight', async () => {
    // Slow delete — never resolves during this test
    mockApiService.deleteChild.mockReturnValue(new Promise(() => {}))
    renderWithProviders(<ChildrenPage />)

    await waitFor(() => expect(screen.getByText('Test Child Delete')).toBeInTheDocument())
    const deleteBtn = screen.getByRole('button', { name: /Remove Test Child Delete/i })
    fireEvent.click(deleteBtn)

    await waitFor(() => expect(deleteBtn).toBeDisabled())
  })
})

// ---------------------------------------------------------------------------
// 6. ParentRoute — role gate
// ---------------------------------------------------------------------------

describe('ParentRoute — role gate', () => {
  /**
   * Render the /children route through the full ParentRoute guard so we can
   * assert redirect behaviour without re-testing ChildrenPage internals.
   */
  async function renderViaParentRoute(authOverrides: Partial<ReturnType<typeof mockUseAuth>>) {
    mockUseAuth.mockReturnValue({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      login: vi.fn(),
      signup: vi.fn(),
      googleAuth: vi.fn(),
      logout: vi.fn(),
      validateToken: vi.fn(),
      ...authOverrides,
    })

    // Import lazily to pick up the mock
    const { default: ParentRoute } = await import('../components/ParentRoute')

    return render(
      <QueryClientProvider client={makeQueryClient()}>
        <MemoryRouter initialEntries={['/children']} future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <Routes>
            <Route
              path="/children"
              element={
                <ParentRoute>
                  <div data-testid="children-page-content">children page</div>
                </ParentRoute>
              }
            />
            <Route path="/login" element={<div data-testid="login-page">login</div>} />
            <Route path="/dashboard" element={<div data-testid="dashboard-page">dashboard</div>} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    )
  }

  it('redirects unauthenticated users to /login', async () => {
    await renderViaParentRoute({ user: null, isAuthenticated: false })
    expect(screen.getByTestId('login-page')).toBeInTheDocument()
    expect(screen.queryByTestId('children-page-content')).not.toBeInTheDocument()
  })

  it('redirects authenticated EDUCATORs to /dashboard', async () => {
    await renderViaParentRoute({
      user: { user_id: 5, email: 'edu@test.invalid', full_name: 'Test Educator', role: 'EDUCATOR', country: 'ZZ' },
      isAuthenticated: true,
    })
    expect(screen.getByTestId('dashboard-page')).toBeInTheDocument()
    expect(screen.queryByTestId('children-page-content')).not.toBeInTheDocument()
  })

  it('renders children page content for authenticated PARENTs', async () => {
    await renderViaParentRoute({
      user: { user_id: 10, email: 'parent@test.invalid', full_name: 'Test Parent', role: 'PARENT', country: 'ZZ' },
      isAuthenticated: true,
    })
    expect(screen.getByTestId('children-page-content')).toBeInTheDocument()
  })

  it('shows a loading spinner while auth is resolving', async () => {
    await renderViaParentRoute({ isLoading: true })
    const spinner = document.querySelector('.animate-spin')
    expect(spinner).toBeInTheDocument()
    expect(screen.queryByTestId('children-page-content')).not.toBeInTheDocument()
    expect(screen.queryByTestId('login-page')).not.toBeInTheDocument()
  })
})
