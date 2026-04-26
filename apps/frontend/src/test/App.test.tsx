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
    const ctaLink = screen.getByRole('link', { name: /Sign up as a parent/i })
    expect(ctaLink).toBeInTheDocument()
    expect(ctaLink).toHaveAttribute('href', '/signup')
  })
})
