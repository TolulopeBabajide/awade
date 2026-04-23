import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
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
      <MemoryRouter initialEntries={[initialPath]}>
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
      // Never resolves within this test
      mockApiService.getChildren.mockReturnValue(new Promise(() => {}))
      const { container } = renderPage()
      // The spinner is a plain div with animate-spin — no ARIA role
      expect(container.querySelector('.animate-spin')).toBeTruthy()
    })
  })

  describe('redirect when children already exist', () => {
    it('redirects to /dashboard if user already has children', async () => {
      mockApiService.getChildren.mockResolvedValue(withChildren)
      renderPage()
      await waitFor(() => {
        expect(screen.getByTestId('dashboard-page')).toBeInTheDocument()
      })
    })
  })

  describe('onboarding form (no existing children)', () => {
    it('renders welcome message with first name', async () => {
      renderPage()
      await waitFor(() => {
        expect(screen.getByText(/Welcome, Test/i)).toBeInTheDocument()
      })
    })

    it('renders the child name input', async () => {
      renderPage()
      await waitFor(() => {
        expect(screen.getByPlaceholderText(/e\.g\. Amina/i)).toBeInTheDocument()
      })
    })

    it('shows subject chips once reference data loads', async () => {
      renderPage()
      await waitFor(() => {
        expect(screen.getByText('Mathematics')).toBeInTheDocument()
        expect(screen.getByText('English')).toBeInTheDocument()
      })
    })

    it('shows validation error if submitted without a name', async () => {
      renderPage()
      await waitFor(() => screen.getByText(/Get Started/i))
      fireEvent.click(screen.getByRole('button', { name: /Get Started/i }))
      await waitFor(() => {
        expect(screen.getByText(/Please enter your child's name/i)).toBeInTheDocument()
      })
    })

    it('submits successfully and redirects to /dashboard', async () => {
      const user = userEvent.setup()
      renderPage()
      await waitFor(() => screen.getByPlaceholderText(/e\.g\. Amina/i))

      await user.type(screen.getByPlaceholderText(/e\.g\. Amina/i), 'Test Child 01')
      await user.click(screen.getByRole('button', { name: /Get Started/i }))

      await waitFor(() => {
        expect(mockApiService.createChild).toHaveBeenCalledWith(
          expect.objectContaining({ name: 'Test Child 01' })
        )
      })
      await waitFor(() => {
        expect(screen.getByTestId('dashboard-page')).toBeInTheDocument()
      }, { timeout: 3000 })
    })

    it('shows error message if createChild returns an error', async () => {
      mockApiService.createChild.mockResolvedValue({ data: null, error: 'Server error' })
      const user = userEvent.setup()
      renderPage()
      await waitFor(() => screen.getByPlaceholderText(/e\.g\. Amina/i))

      await user.type(screen.getByPlaceholderText(/e\.g\. Amina/i), 'Test Child 02')
      await user.click(screen.getByRole('button', { name: /Get Started/i }))

      await waitFor(() => {
        expect(screen.getByText('Server error')).toBeInTheDocument()
      })
    })
  })

  describe('skip link', () => {
    it('navigates to /dashboard when Skip is clicked', async () => {
      const user = userEvent.setup()
      renderPage()
      await waitFor(() => screen.getByText(/Skip for now/i))
      await user.click(screen.getByText(/Skip for now/i))
      expect(screen.getByTestId('dashboard-page')).toBeInTheDocument()
    })
  })
})
