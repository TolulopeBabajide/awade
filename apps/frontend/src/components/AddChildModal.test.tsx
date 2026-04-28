/**
 * Tests for AddChildModal (AWD-H-54)
 *
 * Focused on the dialog ARIA attributes added to satisfy WCAG 1.3.1 / 4.1.2.
 * Other behavioural coverage lives alongside the consuming pages.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import AddChildModal from './AddChildModal'

vi.mock('../services/api', () => ({
  default: {
    getCountries: vi.fn().mockResolvedValue({ data: [] }),
    getGradeLevels: vi.fn().mockResolvedValue({ data: [] }),
    getSubjects: vi.fn().mockResolvedValue({ data: [] }),
    getCurriculums: vi.fn().mockResolvedValue({ data: [] }),
    createChild: vi.fn().mockResolvedValue({}),
    updateChild: vi.fn().mockResolvedValue({}),
  },
}))

describe('AddChildModal — a11y (AWD-H-54)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the backdrop as a labelled modal dialog', async () => {
    render(<AddChildModal isOpen onClose={vi.fn()} onSuccess={vi.fn()} />)
    const dialog = await screen.findByRole('dialog')
    expect(dialog).toHaveAttribute('aria-modal', 'true')
    expect(dialog).toHaveAttribute('aria-labelledby', 'add-child-modal-title')
    await waitFor(() => expect(screen.getByRole('heading')).toBeInTheDocument())
  })

  it("exposes a heading whose id matches the dialog's aria-labelledby", async () => {
    render(<AddChildModal isOpen onClose={vi.fn()} onSuccess={vi.fn()} />)
    const heading = await screen.findByRole('heading', { name: /add your child/i })
    expect(heading.id).toBe('add-child-modal-title')
  })

  it('reuses the same labelling id in edit mode', async () => {
    render(
      <AddChildModal
        isOpen
        onClose={vi.fn()}
        onSuccess={vi.fn()}
        editData={{ child_id: 1, name: 'Test', subjects: [] }}
      />,
    )
    const heading = await screen.findByRole('heading', { name: /edit child profile/i })
    expect(heading.id).toBe('add-child-modal-title')
    expect(screen.getByRole('dialog')).toHaveAttribute(
      'aria-labelledby',
      'add-child-modal-title',
    )
  })

  it('does not render a dialog when closed', () => {
    render(<AddChildModal isOpen={false} onClose={vi.fn()} onSuccess={vi.fn()} />)
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  // AWD-M-54: form-level error banner is announced to assistive tech
  it('exposes the validation error banner with role="alert"', async () => {
    render(<AddChildModal isOpen onClose={vi.fn()} onSuccess={vi.fn()} />)
    await screen.findByRole('dialog')
    fireEvent.click(screen.getByRole('button', { name: /add child/i }))
    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent(/please enter your child's name/i)
  })
})
