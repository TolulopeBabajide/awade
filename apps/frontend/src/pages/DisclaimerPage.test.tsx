import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import DisclaimerPage from './DisclaimerPage'

// ---------------------------------------------------------------------------
// Mock react-router-dom navigate
// ---------------------------------------------------------------------------

const mockNavigate = vi.fn()

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Render DisclaimerPage inside a MemoryRouter at /disclaimer, matching the
 * public route registered in App.tsx — no auth wrapper required.
 */
function renderDisclaimerPage() {
  return render(
    <MemoryRouter
      initialEntries={['/disclaimer']}
      future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
    >
      <Routes>
        <Route path="/disclaimer" element={<DisclaimerPage />} />
      </Routes>
    </MemoryRouter>
  )
}

// ---------------------------------------------------------------------------
// Setup / teardown
// ---------------------------------------------------------------------------

beforeEach(() => {
  vi.clearAllMocks()
  // Reset history length to 1 (direct navigation, no prior history) by default.
  Object.defineProperty(window.history, 'length', {
    configurable: true,
    get: () => 1,
  })
})

// ---------------------------------------------------------------------------
// 1. Renders all four card sections without crashing (AWD-M-84 requirement 1)
// ---------------------------------------------------------------------------

describe('DisclaimerPage — card sections', () => {
  it('renders "What is AI-generated content?" card', () => {
    renderDisclaimerPage()
    expect(
      screen.getByRole('heading', { name: /What is AI-generated content\?/i })
    ).toBeInTheDocument()
  })

  it('renders "Accuracy and limitations" card', () => {
    renderDisclaimerPage()
    expect(
      screen.getByRole('heading', { name: /Accuracy and limitations/i })
    ).toBeInTheDocument()
  })

  it('renders "Transparency notice (EU AI Act Art. 52)" card', () => {
    renderDisclaimerPage()
    expect(
      screen.getByRole('heading', { name: /Transparency notice/i })
    ).toBeInTheDocument()
  })

  it('renders "Your data and privacy" card', () => {
    renderDisclaimerPage()
    expect(
      screen.getByRole('heading', { name: /Your data and privacy/i })
    ).toBeInTheDocument()
  })

  it('renders the page heading "AI Content Disclaimer"', () => {
    renderDisclaimerPage()
    expect(
      screen.getByRole('heading', { name: /AI Content Disclaimer/i })
    ).toBeInTheDocument()
  })
})

// ---------------------------------------------------------------------------
// 2. "Back" button — navigate guard (AWD-M-84 req 2 + AWD-M-87)
// ---------------------------------------------------------------------------

describe('DisclaimerPage — back navigation', () => {
  it('renders a "Back" button', () => {
    renderDisclaimerPage()
    expect(screen.getByRole('button', { name: /Back/i })).toBeInTheDocument()
  })

  it('calls navigate(-1) when the user arrived via in-app navigation (history.length > 1)', () => {
    // Simulate arriving from a prior page (e.g., via the disclosure banner link)
    Object.defineProperty(window.history, 'length', {
      configurable: true,
      get: () => 2,
    })
    renderDisclaimerPage()
    const backBtn = screen.getByRole('button', { name: /Back/i })
    fireEvent.click(backBtn)
    expect(mockNavigate).toHaveBeenCalledOnce()
    expect(mockNavigate).toHaveBeenCalledWith(-1)
  })

  it('calls navigate("/") when the user arrived via direct link (history.length <= 1)', () => {
    // history.length is 1 (set in beforeEach) — direct navigation, no back-stack
    renderDisclaimerPage()
    const backBtn = screen.getByRole('button', { name: /Back/i })
    fireEvent.click(backBtn)
    expect(mockNavigate).toHaveBeenCalledOnce()
    expect(mockNavigate).toHaveBeenCalledWith('/')
  })
})

// ---------------------------------------------------------------------------
// 3. Links are present and point to correct hrefs (AWD-M-84 requirement 3)
// ---------------------------------------------------------------------------

describe('DisclaimerPage — links', () => {
  it('renders the Privacy Policy link pointing to /privacy-policy', () => {
    renderDisclaimerPage()
    const link = screen.getByRole('link', { name: /Privacy Policy/i })
    expect(link).toBeInTheDocument()
    expect(link).toHaveAttribute('href', '/privacy-policy')
  })

  it('renders the contact mailto link pointing to hello@awade.app', () => {
    renderDisclaimerPage()
    const link = screen.getByRole('link', { name: /Contact us/i })
    expect(link).toBeInTheDocument()
    expect(link).toHaveAttribute('href', 'mailto:hello@awade.app')
  })
})

// ---------------------------------------------------------------------------
// 4. Route is public — no auth gate (AWD-M-84 requirement 4)
// ---------------------------------------------------------------------------

describe('DisclaimerPage — public accessibility', () => {
  it('renders without any auth context or protected-route wrapper', () => {
    // No AuthProvider, no ProtectedRoute — the page must render for unauthenticated users
    render(
      <MemoryRouter
        initialEntries={['/disclaimer']}
        future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
      >
        <Routes>
          <Route path="/disclaimer" element={<DisclaimerPage />} />
        </Routes>
      </MemoryRouter>
    )
    // If DisclaimerPage renders the main heading, it is publicly accessible
    expect(
      screen.getByRole('heading', { name: /AI Content Disclaimer/i })
    ).toBeInTheDocument()
  })

  it('does not redirect unauthenticated users', () => {
    render(
      <MemoryRouter
        initialEntries={['/disclaimer']}
        future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
      >
        <Routes>
          <Route path="/disclaimer" element={<DisclaimerPage />} />
          <Route path="/login" element={<div data-testid="login-page" />} />
        </Routes>
      </MemoryRouter>
    )
    expect(screen.queryByTestId('login-page')).not.toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: /AI Content Disclaimer/i })
    ).toBeInTheDocument()
  })
})
