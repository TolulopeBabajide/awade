import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import ParentOnboardingPage from './ParentOnboardingPage'

// ── Mocks ──────────────────────────────────────────────────────────────────

vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { user_id: 1, email: 'parent@test.invalid', full_name: 'Test Parent', role: 'PARENT', country: 'ZZ' },
    isAuthenticated: true,
    isLoading: false,
  }),
}))

// vi.mock is hoisted to the top of the file, so the mock factory must not
// reference variables declared in module scope. Use vi.hoisted() to create
// the mock object early enough for the factory to close over it safely.
const mockApiService = vi.hoisted(() => ({
  getChildren: vi.fn(),
  getCountries: vi.fn(),
  getGradeLevels: vi.fn(),
  getSubjects: vi.fn(),
  getCurriculums: vi.fn(),
  createChild: vi.fn(),
}))

vi.mock('../services/api', () => ({ default: mockApiService }))

// ── Helpers ────────────────────────────────────────────────────────────────

function makeQC() {
  return new QueryClient({ defaultOptions: { queries: { retry: false } } })
}

function renderPage(initialPath = '/onboarding') {
  return render(
    <QueryClientProvider client={makeQC()}>
      <MemoryRouter initialEntries={[initialPath]} future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Routes>
          <Route path="/onboarding" element={<ParentOnboardingPage />} />
          <Route path="/dashboard" element={<div data-testid="dashboard-page">Dashboard</div>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

const noChildren = { data: { children: [] }, error: null }
const withChildren = { data: { children: [{ child_id: 1, name: 'Existing Child' }] }, error: null }

const refDataOk = {
  countries: { data: [{ country_id: 1, country_name: 'Nigeria' }], error: null },
  grades: { data: [{ grade_level_id: 1, name: 'JSS 1' }], error: null },
  subjects: { data: [{ subject_id: 1, name: 'Mathematics' }, { subject_id: 2, name: 'English' }], error: null },
}

beforeEach(() => {
  vi.clearAllMocks()
  mockApiService.getChildren.mockResolvedValue(noChildren)
  mockApiService.getCountries.mockResolvedValue(refDataOk.countries)
  mockApiService.getGradeLevels.mockResolvedValue(refDataOk.grades)
  mockApiService.getSubjects.mockResolvedValue(refDataOk.subjects)
  mockApiService.getCurriculums.mockResolvedValue({ data: [], error: null })
  mockApiService.createChild.mockResolvedValue({ data: { child_id: 2, name: 'Test Child 01' }, error: null })
})

// ── Tests ──────────────────────────────────────────────────────────────────

describe('ParentOnboardingPage', () => {
  describe('loading state', () => {
    it('shows a spinner while checking for existing children', () => {
      // Keep ALL async calls pending — prevents any state updates after the
      // synchronous assertion, eliminating act() warnings.
      mockApiService.getChildren.mockReturnValue(new Promise(() => {}))
      mockApiService.getCountries.mockReturnValue(new Promise(() => {}))
      mockApiService.getGradeLevels.mockReturnValue(new Promise(() => {}))
      mockApiService.getSubjects.mockReturnValue(new Promise(() => {}))
      const { container } = renderPage()
      // The spinner is a plain div with animate-spin — no ARIA role
      expect(container.querySelector('.animate-spin')).toBeTruthy()
    })
  })

  describe('redirect when children already exist', () => {
    it('redirects to /dashboard if user already has children', async () => {
      mockApiService.getChildren.mockResolvedValue(withChildren)
      // Keep ref-data calls pending so they cannot trigger state updates after
      // the component unmounts (navigate unmounts ParentOnboardingPage).
      mockApiService.getCountries.mockReturnValue(new Promise(() => {}))
      mockApiService.getGradeLevels.mockReturnValue(new Promise(() => {}))
      mockApiService.getSubjects.mockReturnValue(new Promise(() => {}))
      renderPage()
      await screen.findByTestId('dashboard-page')
    })
  })

  describe('onboarding form (no existing children)', () => {
    it('renders welcome message with first name', async () => {
      renderPage()
      await screen.findByText(/Welcome, Test/i)
      // Wait for all loadRefData state updates to settle (subjects are the last
      // of the three parallel calls to apply state — no pending updates after this).
      await screen.findByText('Mathematics')
    })

    it('renders the child name input', async () => {
      renderPage()
      await screen.findByPlaceholderText(/e\.g\. Amina/i)
      // Drain pending ref-data state updates before the test ends.
      await screen.findByText('Mathematics')
    })

    it('shows subject chips once reference data loads', async () => {
      renderPage()
      await screen.findByText('Mathematics')
      expect(screen.getByText('English')).toBeInTheDocument()
    })

    it('shows validation error if submitted without a name', async () => {
      renderPage()
      // Wait for the full page (incl. ref data) to settle before interacting.
      await screen.findByText('Mathematics')
      fireEvent.click(screen.getByRole('button', { name: /Get Started/i }))
      await screen.findByText(/Please enter your child's name/i)
    })

    it('submits successfully and shows success state', async () => {
      renderPage()
      await screen.findByText('Mathematics')

      // Use fireEvent (synchronous dispatch) + waitFor to avoid the act()
      // mismatch that occurs when userEvent's internal act and React's test-mode
      // act see different async microtask queues in this vitest environment.
      fireEvent.change(
        screen.getByPlaceholderText(/e\.g\. Amina/i),
        { target: { value: 'Test Child 01' } }
      )
      fireEvent.click(screen.getByRole('button', { name: /Get Started/i }))

      // createChild resolves → setDone(true) → "All set!" screen is shown.
      // The waitFor wrapper catches the async state update inside act().
      await waitFor(() => {
        expect(mockApiService.createChild).toHaveBeenCalledWith(
          expect.objectContaining({ name: 'Test Child 01' })
        )
      })
      await screen.findByText('All set!')
    })

    it('shows error message if createChild returns an error', async () => {
      mockApiService.createChild.mockResolvedValue({ data: null, error: 'Server error' })
      renderPage()
      await screen.findByText('Mathematics')

      fireEvent.change(
        screen.getByPlaceholderText(/e\.g\. Amina/i),
        { target: { value: 'Test Child 02' } }
      )
      fireEvent.click(screen.getByRole('button', { name: /Get Started/i }))

      await screen.findByText('Server error')
    })

    it('shows error message when reference data fetch throws', async () => {
      mockApiService.getCountries.mockRejectedValue(new Error('Network error'))
      renderPage()
      await screen.findByText(/Failed to load options\. Please refresh\./i)
    })

    it('shows error message when curriculum fetch throws after country selection', async () => {
      mockApiService.getCurriculums.mockRejectedValue(new Error('Network error'))
      renderPage()
      // Wait for ref data to fully load — 'Nigeria' appears once setCountries runs,
      // and Promise.all means grades/subjects are set in the same flush.
      await screen.findByText('Nigeria')
      // fireEvent.change triggers the country onChange → form.country_id updates →
      // loadCurriculums effect runs → rejects → setError fires in the next waitFor poll.
      fireEvent.change(
        screen.getAllByRole('combobox')[0],
        { target: { value: '1' } }
      )
      await screen.findByText(/Failed to load options\. Please refresh\./i)
    })
  })

  describe('skip link', () => {
    it('navigates to /dashboard when Skip is clicked', async () => {
      renderPage()
      // Wait for the full form (including ref data) to be stable before clicking
      // Skip, so there are no in-flight state updates that could fire after
      // the component unmounts.
      await screen.findByText('Mathematics')
      fireEvent.click(screen.getByText(/Skip for now/i))
      await screen.findByTestId('dashboard-page')
    })
  })
})
