/**
 * Tests for MobileNavigation (AWD-L-14)
 *
 * Covers:
 * - Named navigation landmark aria-label (WCAG 2.1 SC 4.1.2)
 * - aria-current="page" on the active nav item (WCAG 2.1 SC 2.4.8)
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import MobileNavigation from './MobileNavigation'

// Minimal AuthContext mock — MobileNavigation only reads user.role
vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({ user: { role: 'PARENT' }, logout: vi.fn() }),
}))

const renderMobileNav = (currentPage?: string) =>
  render(
    <MemoryRouter initialEntries={['/dashboard']}>
      <MobileNavigation currentPage={currentPage} />
    </MemoryRouter>,
  )

describe('MobileNavigation — navigation landmark (AWD-L-14)', () => {
  it('nav element has aria-label="Mobile primary navigation"', () => {
    renderMobileNav('dashboard')
    const nav = screen.getByRole('navigation')
    expect(nav).toHaveAttribute('aria-label', 'Mobile primary navigation')
  })

  it('active nav item has aria-current="page"', () => {
    renderMobileNav('children')
    const buttons = screen.getAllByRole('button')
    const childrenBtn = buttons.find(b => b.getAttribute('aria-label')?.includes('Children'))
    expect(childrenBtn).toBeDefined()
    expect(childrenBtn).toHaveAttribute('aria-current', 'page')
  })

  it('inactive nav items do not have aria-current', () => {
    renderMobileNav('dashboard')
    const buttons = screen.getAllByRole('button')
    // All non-dashboard buttons should not have aria-current
    const nonActiveButtons = buttons.filter(
      b => !b.getAttribute('aria-label')?.toLowerCase().includes('home')
    )
    nonActiveButtons.forEach(btn => {
      expect(btn).not.toHaveAttribute('aria-current')
    })
  })

  it('dashboard button has aria-current="page" when dashboard is active', () => {
    renderMobileNav('dashboard')
    const buttons = screen.getAllByRole('button')
    const homeBtn = buttons.find(b => b.getAttribute('aria-label')?.toLowerCase().includes('home'))
    expect(homeBtn).toBeDefined()
    expect(homeBtn).toHaveAttribute('aria-current', 'page')
  })
})
