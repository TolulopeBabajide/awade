import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import NotFoundPage from './NotFoundPage'

vi.mock('../contexts/AuthContext', () => ({ useAuth: () => ({ user: null }) }))
describe('missing page recovery', () => {
  it('gives signed-out visitors working home and sign-in routes', () => {
    render(<MemoryRouter><NotFoundPage /></MemoryRouter>)
    expect(screen.getByRole('heading', { name: 'Let’s find your way back.' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Back to Awade' })).toHaveAttribute('href', '/')
    expect(screen.getByRole('link', { name: 'Sign in' })).toHaveAttribute('href', '/login')
  })
})
