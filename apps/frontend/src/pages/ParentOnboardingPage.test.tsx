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
      await screen.findByTestId('dashboard-page', undefined, { timeout: 5000 })
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
      await screen.findByTestId('dashboard-page', undefined, { timeout: 5000 })
    })
  })

  // AWD-M-53: required-field a11y — name input must be programmatically required
  describe('required-field a11y (AWD-M-53)', () => {
    it('marks the child name input as required with aria-required', async () => {
      renderPage()
      await screen.findByText('Mathematics')
      const nameInput = screen.getByPlaceholderText(/e\.g\. Amina/i)
      expect(nameInput).toHaveAttribute('required')
      expect(nameInput).toHaveAttribute('aria-required', 'true')
    })

    it('associates the child name label with its input via htmlFor/id', async () => {
      renderPage()
      await screen.findByText('Mathematics')
      const nameInput = screen.getByPlaceholderText(/e\.g\. Amina/i)
      expect(nameInput).toHaveAttribute('id', 'onboarding-name')
      const label = screen.getByText(/child's name/i)
      expect(label.closest('label')).toHaveAttribute('for', 'onboarding-name')
    })
  })

  // AWD-M-55: aria-invalid / aria-describedby wired to name input after validation error
  describe('validation a11y (AWD-M-55)', () => {
    it('sets aria-invalid on the name input after an empty-name submit', async () => {
      renderPage()
      await screen.findByText('Mathematics')
      fireEvent.click(screen.getByRole('button', { name: /Get Started/i }))
      await screen.findByRole('alert')
      const nameInput = screen.getByPlaceholderText(/e\.g\. Amina/i)
      expect(nameInput).toHaveAttribute('aria-invalid', 'true')
    })

    it('points aria-describedby at the error message id after validation failure', async () => {
      renderPage()
      await screen.findByText('Mathematics')
      fireEvent.click(screen.getByRole('button', { name: /Get Started/i }))
      const alert = await screen.findByRole('alert')
      expect(alert).toHaveAttribute('id', 'onboarding-error-msg')
      const nameInput = screen.getByPlaceholderText(/e\.g\. Amina/i)
      expect(nameInput).toHaveAttribute('aria-describedby', 'onboarding-error-msg')
    })

    it('clears aria-invalid once the user starts typing in the name field', async () => {
      renderPage()
      await screen.findByText('Mathematics')
      // trigger validation error
      fireEvent.click(screen.getByRole('button', { name: /Get Started/i }))
      await screen.findByRole('alert')
      // user types a character — error should clear
      fireEvent.change(screen.getByPlaceholderText(/e\.g\. Amina/i), { target: { value: 'A' } })
      const nameInput = screen.getByPlaceholderText(/e\.g\. Amina/i)
      expect(nameInput).not.toHaveAttribute('aria-invalid')
      expect(nameInput).not.toHaveAttribute('aria-describedby')
    })
  })

  // AWD-L-16: all form labels programmatically associated with their controls via htmlFor/id
  describe('label association a11y (AWD-L-16)', () => {
    it('associates the Age label with its input via htmlFor/id', async () => {
      renderPage()
      await screen.findByText('Mathematics')
      const ageInput = screen.getByPlaceholderText(/e\.g\. 12/i)
      expect(ageInput).toHaveAttribute('id', 'onboarding-age')
      const label = screen.getByText(/^age$/i)
      expect(label.closest('label')).toHaveAttribute('for', 'onboarding-age')
    })

    it('associates the School Name label with its input via htmlFor/id', async () => {
      renderPage()
      await screen.findByText('Mathematics')
      const schoolInput = screen.getByPlaceholderText(/Federal Government College/i)
      expect(schoolInput).toHaveAttribute('id', 'onboarding-school')
      const label = screen.getByText(/^school name$/i)
      expect(label.closest('label')).toHaveAttribute('for', 'onboarding-school')
    })

    it('associates the Country label with its select via htmlFor/id', async () => {
      renderPage()
      await screen.findByText('Mathematics')
      const countrySelect = screen.getByRole('combobox', { name: /country/i })
      expect(countrySelect).toHaveAttribute('id', 'onboarding-country')
      const label = screen.getByText(/^country$/i)
      expect(label.closest('label')).toHaveAttribute('for', 'onboarding-country')
    })

    it('associates the Grade Level label with its select via htmlFor/id', async () => {
      renderPage()
      await screen.findByText('Mathematics')
      const gradeSelect = screen.getByRole('combobox', { name: /grade level/i })
      expect(gradeSelect).toHaveAttribute('id', 'onboarding-grade')
      const label = screen.getByText(/^grade level$/i)
      expect(label.closest('label')).toHaveAttribute('for', 'onboarding-grade')
    })
  })
})
