/**
 * Tests for Sidebar (AWD-M-57)
 *
 * Focused on the "Skip to main content" accessibility link added to satisfy
 * WCAG 2.1 SC 2.4.1 (Bypass Blocks, Level A).
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Sidebar from './Sidebar'

// Minimal AuthContext mock — Sidebar only reads user.role
vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({ user: { role: 'PARENT' }, logout: vi.fn() }),
}))

const renderSidebar = () =>
  render(
    <MemoryRouter>
      <Sidebar currentPage="dashboard" />
    </MemoryRouter>,
  )

describe('Sidebar — skip-to-main-content (AWD-M-57)', () => {
  it('renders a skip link targeting #main-content', () => {
    renderSidebar()
    const link = screen.getByRole('link', { name: /skip to main content/i })
    expect(link).toBeInTheDocument()
    expect(link).toHaveAttribute('href', '#main-content')
  })

  it('skip link is visually hidden by default (sr-only)', () => {
    renderSidebar()
    const link = screen.getByRole('link', { name: /skip to main content/i })
    // sr-only is always reachable by assistive tech; confirm it exists in the DOM
    expect(link).toBeInTheDocument()
    expect(link.className).toMatch(/sr-only/)
  })

  it('skip link appears before the navigation in DOM order', () => {
    renderSidebar()
    const link = screen.getByRole('link', { name: /skip to main content/i })
    const nav = screen.getByRole('navigation', { hidden: true })
    // compareDocumentPosition flag 4 = "link precedes nav"
    expect(link.compareDocumentPosition(nav) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
  })
})
