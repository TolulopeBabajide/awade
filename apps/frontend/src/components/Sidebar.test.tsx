/**
 * Tests for Sidebar (AWD-M-57, AWD-L-14)
 *
 * Covers:
 * - "Skip to main content" accessibility link (WCAG 2.1 SC 2.4.1)
 * - Named navigation landmark aria-label (WCAG 2.1 SC 4.1.2)
 * - aria-current="page" on the active nav item (WCAG 2.1 SC 2.4.8)
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Sidebar from './Sidebar'

// Minimal AuthContext mock — Sidebar only reads user.role
vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({ user: { role: 'PARENT' }, logout: vi.fn() }),
}))

const renderSidebar = (currentPage: 'dashboard' | 'children' | 'saved-guides' | 'settings' = 'dashboard') =>
  render(
    <MemoryRouter>
      <Sidebar currentPage={currentPage} />
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

describe('Sidebar — navigation landmark (AWD-L-14)', () => {
  it('nav element has aria-label="Primary navigation"', () => {
    renderSidebar()
    const nav = screen.getByRole('navigation', { hidden: true })
    expect(nav).toHaveAttribute('aria-label', 'Primary navigation')
  })

  it('active nav item has aria-current="page"', () => {
    renderSidebar('children')
    // Find the button for "My Children" — the active page
    const buttons = screen.getAllByRole('button')
    const childrenBtn = buttons.find(b => b.textContent?.includes('My Children'))
    expect(childrenBtn).toBeDefined()
    expect(childrenBtn).toHaveAttribute('aria-current', 'page')
  })

  it('inactive nav items do not have aria-current', () => {
    renderSidebar('dashboard')
    const buttons = screen.getAllByRole('button')
    const nonActiveButtons = buttons.filter(
      b => b.textContent?.includes('My Children') || b.textContent?.includes('Saved Guides') || b.textContent?.includes('Settings')
    )
    nonActiveButtons.forEach(btn => {
      expect(btn).not.toHaveAttribute('aria-current')
    })
  })
})
