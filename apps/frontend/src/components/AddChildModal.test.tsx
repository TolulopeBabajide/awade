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

  // AWD-M-53: required-field a11y — name input must be programmatically required
  it('marks the child name input as required with aria-required', async () => {
    render(<AddChildModal isOpen onClose={vi.fn()} onSuccess={vi.fn()} />)
    await screen.findByRole('dialog')
    const nameInput = screen.getByPlaceholderText(/e\.g\. amina/i)
    expect(nameInput).toHaveAttribute('required')
    expect(nameInput).toHaveAttribute('aria-required', 'true')
  })

  it('associates the child name label with its input via htmlFor/id', async () => {
    render(<AddChildModal isOpen onClose={vi.fn()} onSuccess={vi.fn()} />)
    await screen.findByRole('dialog')
    const nameInput = screen.getByPlaceholderText(/e\.g\. amina/i)
    expect(nameInput).toHaveAttribute('id', 'modal-child-name')
    const label = screen.getByText(/child's name/i)
    expect(label.closest('label')).toHaveAttribute('for', 'modal-child-name')
  })

  // AWD-M-55: aria-invalid / aria-describedby wired to name input after validation error
  describe('validation a11y (AWD-M-55)', () => {
    it('sets aria-invalid on the name input after an empty-name submit', async () => {
      render(<AddChildModal isOpen onClose={vi.fn()} onSuccess={vi.fn()} />)
      await screen.findByRole('dialog')
      fireEvent.click(screen.getByRole('button', { name: /add child/i }))
      await screen.findByRole('alert')
      const nameInput = screen.getByPlaceholderText(/e\.g\. amina/i)
      expect(nameInput).toHaveAttribute('aria-invalid', 'true')
    })

    it('points aria-describedby at the error message id after validation failure', async () => {
      render(<AddChildModal isOpen onClose={vi.fn()} onSuccess={vi.fn()} />)
      await screen.findByRole('dialog')
      fireEvent.click(screen.getByRole('button', { name: /add child/i }))
      const alert = await screen.findByRole('alert')
      expect(alert).toHaveAttribute('id', 'modal-error-msg')
      const nameInput = screen.getByPlaceholderText(/e\.g\. amina/i)
      expect(nameInput).toHaveAttribute('aria-describedby', 'modal-error-msg')
    })

    it('clears aria-invalid once the user starts typing in the name field', async () => {
      render(<AddChildModal isOpen onClose={vi.fn()} onSuccess={vi.fn()} />)
      await screen.findByRole('dialog')
      // trigger validation error
      fireEvent.click(screen.getByRole('button', { name: /add child/i }))
      await screen.findByRole('alert')
      // user types a character — error should clear
      fireEvent.change(screen.getByPlaceholderText(/e\.g\. amina/i), { target: { value: 'A' } })
      const nameInput = screen.getByPlaceholderText(/e\.g\. amina/i)
      expect(nameInput).not.toHaveAttribute('aria-invalid')
      expect(nameInput).not.toHaveAttribute('aria-describedby')
    })

    it('resets aria-invalid when the modal is closed and reopened', async () => {
      const { rerender } = render(<AddChildModal isOpen onClose={vi.fn()} onSuccess={vi.fn()} />)
      await screen.findByRole('dialog')
      // trigger validation error
      fireEvent.click(screen.getByRole('button', { name: /add child/i }))
      await screen.findByRole('alert')
      // close and reopen the modal
      rerender(<AddChildModal isOpen={false} onClose={vi.fn()} onSuccess={vi.fn()} />)
      rerender(<AddChildModal isOpen onClose={vi.fn()} onSuccess={vi.fn()} />)
      await screen.findByRole('dialog')
      const nameInput = screen.getByPlaceholderText(/e\.g\. amina/i)
      expect(nameInput).not.toHaveAttribute('aria-invalid')
    })
  })
})
