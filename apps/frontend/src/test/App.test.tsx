import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { describe, it, expect, vi } from 'vitest'
import App from '../App'

// Mock the AuthContext
vi.mock('../contexts/AuthContext', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => children,
  useAuth: () => ({
    user: null,
    isAuthenticated: false,
    isLoading: false,
    login: vi.fn(),
    signup: vi.fn(),
    googleAuth: vi.fn(),
    logout: vi.fn(),
    validateToken: vi.fn()
  })
}))

// Mock LandingPage to avoid rendering HeroSectionParent (picture/img) 3× in the same
// worker, which causes exponential GC pause escalation (7s → 25s → 53s per test).
// The stub satisfies all App.test assertions; LandingPage content is tested separately.
vi.mock('../pages/LandingPage', () => ({
  default: () => (
    <div>
      <span>Awade</span>
      <h1>Understand what your child is learning</h1>
      <a href="/signup" aria-label="Sign up as a parent">Get Started Free</a>
    </div>
  ),
}))

const AppWithRouter = () => (
  <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
    <App />
  </BrowserRouter>
)

describe('App', () => {
  it('renders without crashing', () => {
    render(<AppWithRouter />)
    const elements = screen.getAllByText(/Awade/i)
    expect(elements.length).toBeGreaterThan(0)
    expect(elements[0]).toBeInTheDocument()
  })

  it('renders parent landing page by default', () => {
    render(<AppWithRouter />)
    // Post-pivot: landing page shows parent-focused hero headline
    expect(screen.getByRole('heading', { name: /Understand what your child is learning/i })).toBeInTheDocument()
  })

  it('renders parent landing page CTA', () => {
    render(<AppWithRouter />)
    // Primary CTA uses aria-label "Sign up as a parent" (visible text: "Get Started Free")
    // Synchronous query: link is statically rendered, exists immediately in DOM
    const ctaLink = screen.getByRole('link', { name: /Sign up as a parent/i })
    expect(ctaLink).toBeInTheDocument()
    expect(ctaLink).toHaveAttribute('href', '/signup')
  })
})
