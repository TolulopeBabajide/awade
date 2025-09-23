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
    expect(screen.getByText(/Awade/i)).toBeInTheDocument()
  })

  it('renders landing page by default', () => {
    render(<AppWithRouter />)
    // The landing page should be rendered when not authenticated
    expect(screen.getByText(/Welcome to Awade/i)).toBeInTheDocument()
  })
})
