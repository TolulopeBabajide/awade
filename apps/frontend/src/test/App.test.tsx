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
  <BrowserRouter>
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

  it('renders landing page by default', () => {
    render(<AppWithRouter />)
    // The landing page should be rendered when not authenticated
    expect(screen.getByText(/Transform Your Teaching with Awade/i)).toBeInTheDocument()
  })
})
