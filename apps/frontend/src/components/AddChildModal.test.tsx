/**
 * Tests for AddChildModal (AWD-H-54 + AWD-M-56)
 *
 * Focused on the dialog ARIA attributes (AWD-H-54) and focus trap / Escape
 * handling (AWD-M-56). Other behavioural coverage lives alongside the
 * consuming pages.
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

  // AWD-L-16: all form labels programmatically associated with their controls via htmlFor/id
  describe('label association a11y (AWD-L-16)', () => {
    it('associates the Age label with its input via htmlFor/id', async () => {
      render(<AddChildModal isOpen onClose={vi.fn()} onSuccess={vi.fn()} />)
      await screen.findByRole('dialog')
      const ageInput = screen.getByPlaceholderText(/e\.g\. 12/i)
      expect(ageInput).toHaveAttribute('id', 'modal-age')
      const label = screen.getByText(/^age$/i)
      expect(label.closest('label')).toHaveAttribute('for', 'modal-age')
    })

    it('associates the School Name label with its input via htmlFor/id', async () => {
      render(<AddChildModal isOpen onClose={vi.fn()} onSuccess={vi.fn()} />)
      await screen.findByRole('dialog')
      const schoolInput = screen.getByPlaceholderText(/Federal Government College/i)
      expect(schoolInput).toHaveAttribute('id', 'modal-school')
      const label = screen.getByText(/^school name$/i)
      expect(label.closest('label')).toHaveAttribute('for', 'modal-school')
    })

    it('associates the Country label with its select via htmlFor/id', async () => {
      render(<AddChildModal isOpen onClose={vi.fn()} onSuccess={vi.fn()} />)
      await screen.findByRole('dialog')
      const countrySelect = screen.getByRole('combobox', { name: /country/i })
      expect(countrySelect).toHaveAttribute('id', 'modal-country')
      const label = screen.getByText(/^country$/i)
      expect(label.closest('label')).toHaveAttribute('for', 'modal-country')
    })

    it('associates the Grade Level label with its select via htmlFor/id', async () => {
      render(<AddChildModal isOpen onClose={vi.fn()} onSuccess={vi.fn()} />)
      await screen.findByRole('dialog')
      const gradeSelect = screen.getByRole('combobox', { name: /grade level/i })
      expect(gradeSelect).toHaveAttribute('id', 'modal-grade')
      const label = screen.getByText(/^grade level$/i)
      expect(label.closest('label')).toHaveAttribute('for', 'modal-grade')
    })
  })

  // AWD-M-56: focus trap and Escape handling
  describe('focus trap (AWD-M-56)', () => {
    const FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'

    it('calls onClose when Escape is pressed', async () => {
      const onClose = vi.fn()
      render(<AddChildModal isOpen onClose={onClose} onSuccess={vi.fn()} />)
      await screen.findByRole('dialog')
      fireEvent.keyDown(document, { key: 'Escape' })
      expect(onClose).toHaveBeenCalledOnce()
    })

    it('does NOT call onClose for other keys', async () => {
      const onClose = vi.fn()
      render(<AddChildModal isOpen onClose={onClose} onSuccess={vi.fn()} />)
      await screen.findByRole('dialog')
      fireEvent.keyDown(document, { key: 'Enter' })
      expect(onClose).not.toHaveBeenCalled()
    })

    it('wraps Tab forward from the last focusable element back to the first', async () => {
      render(<AddChildModal isOpen onClose={vi.fn()} onSuccess={vi.fn()} />)
      const dialog = await screen.findByRole('dialog')
      const focusables = Array.from(dialog.querySelectorAll<HTMLElement>(FOCUSABLE))
      expect(focusables.length).toBeGreaterThan(1)

      const last = focusables[focusables.length - 1]
      last.focus()
      expect(document.activeElement).toBe(last)

      fireEvent.keyDown(document, { key: 'Tab', shiftKey: false })
      expect(document.activeElement).toBe(focusables[0])
    })

    it('wraps Shift+Tab backward from the first focusable element to the last', async () => {
      render(<AddChildModal isOpen onClose={vi.fn()} onSuccess={vi.fn()} />)
      const dialog = await screen.findByRole('dialog')
      const focusables = Array.from(dialog.querySelectorAll<HTMLElement>(FOCUSABLE))
      expect(focusables.length).toBeGreaterThan(1)

      const first = focusables[0]
      first.focus()
      expect(document.activeElement).toBe(first)

      fireEvent.keyDown(document, { key: 'Tab', shiftKey: true })
      expect(document.activeElement).toBe(focusables[focusables.length - 1])
    })

    it('does not trap Tab when focus is on a middle element', async () => {
      render(<AddChildModal isOpen onClose={vi.fn()} onSuccess={vi.fn()} />)
      const dialog = await screen.findByRole('dialog')
      const focusables = Array.from(dialog.querySelectorAll<HTMLElement>(FOCUSABLE))
      // Focus a middle element — Tab should not be intercepted
      if (focusables.length >= 3) {
        const middle = focusables[1]
        middle.focus()
        // The handler should not call preventDefault for a mid-element Tab
        const tabEvent = new KeyboardEvent('keydown', { key: 'Tab', bubbles: true, cancelable: true })
        document.dispatchEvent(tabEvent)
        expect(tabEvent.defaultPrevented).toBe(false)
      }
    })

    it('Escape does not fire onClose when modal is closed', () => {
      const onClose = vi.fn()
      render(<AddChildModal isOpen={false} onClose={onClose} onSuccess={vi.fn()} />)
      fireEvent.keyDown(document, { key: 'Escape' })
      expect(onClose).not.toHaveBeenCalled()
    })
  })
})
