/**
 * Tests for ConsentModal (AWD-GRC-01)
 *
 * Covers:
 * - Modal renders with disclosure text
 * - "I Agree" button is disabled until checkbox is ticked
 * - "I Agree" button is enabled once checkbox is ticked
 * - onConsented is called when "I Agree" is clicked (with checkbox ticked)
 * - onCancel is called when "Cancel" is clicked
 * - Displays error message when error prop is non-null
 * - Shows "Saving…" text and disables buttons while isSubmitting
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, act, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ConsentModal from './ConsentModal'

function renderModal(overrides: Partial<React.ComponentProps<typeof ConsentModal>> = {}) {
  const defaults = {
    onConsented: vi.fn(),
    onCancel: vi.fn(),
    isSubmitting: false,
    error: null,
  }
  const props = { ...defaults, ...overrides }
  return { ...render(<ConsentModal {...props} />), props }
}

describe('ConsentModal', () => {
  it('renders the disclosure heading', () => {
    renderModal()
    expect(screen.getByRole('heading', { name: /before you add a child/i })).toBeInTheDocument()
  })

  it('renders key disclosure bullet points', () => {
    renderModal()
    expect(screen.getByText(/what we collect about your child/i)).toBeInTheDocument()
    expect(screen.getByText(/how we use it/i)).toBeInTheDocument()
  })

  it('"I Agree" button is disabled before checkbox is ticked', () => {
    renderModal()
    const btn = screen.getByRole('button', { name: /i agree/i })
    expect(btn).toBeDisabled()
  })

  it('"I Agree" button becomes enabled after ticking the checkbox', async () => {
    // Root cause (AWD-M-60): userEvent.click on a controlled <input type="checkbox">
    // triggers React 18's internal controlled-input synchronisation in a micro-task
    // that escapes the userEvent act() boundary, producing the act() warning.
    // Neither await act(async()=>{}) before the click nor userEvent.setup() prevents
    // this — it is a React 18 + jsdom interaction bug.
    // Fix: use fireEvent.change (which only fires the change event synchronously,
    // no focus simulation) wrapped in act() so all resulting state updates are
    // fully flushed before assertions run.
    renderModal()
    const checkbox = screen.getByRole('checkbox')
    await act(async () => { fireEvent.click(checkbox) })
    expect(screen.getByRole('button', { name: /i agree/i })).not.toBeDisabled()
  })

  it('calls onConsented when "I Agree" is clicked with checkbox ticked', async () => {
    // Same fireEvent.click-in-act pattern to avoid React 18 act() warning (AWD-M-60).
    const { props } = renderModal()
    const checkbox = screen.getByRole('checkbox')
    await act(async () => { fireEvent.click(checkbox) })
    const btn = screen.getByRole('button', { name: /i agree/i })
    expect(btn).not.toBeDisabled()
    await userEvent.click(btn)
    expect(props.onConsented).toHaveBeenCalledOnce()
  })

  it('calls onCancel when "Cancel" is clicked', async () => {
    const { props } = renderModal()
    const cancelBtn = screen.getByRole('button', { name: /cancel/i })
    await userEvent.click(cancelBtn)
    expect(props.onCancel).toHaveBeenCalledOnce()
  })

  it('displays error message when error prop is non-null', () => {
    renderModal({ error: 'Something went wrong. Please try again.' })
    expect(screen.getByRole('alert')).toHaveTextContent('Something went wrong.')
  })

  it('shows "Saving…" label and disables buttons while submitting', () => {
    renderModal({ isSubmitting: true })
    expect(screen.getByRole('button', { name: /saving/i })).toBeDisabled()
    expect(screen.getByRole('button', { name: /cancel/i })).toBeDisabled()
  })

  // AWD-M-56: focus trap and Escape handling
  describe('focus trap (AWD-M-56)', () => {
    const FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'

    it('calls onCancel when Escape is pressed', () => {
      const { props } = renderModal()
      fireEvent.keyDown(document, { key: 'Escape' })
      expect(props.onCancel).toHaveBeenCalledOnce()
    })

    it('does NOT call onCancel for other keys', () => {
      const { props } = renderModal()
      fireEvent.keyDown(document, { key: 'Enter' })
      expect(props.onCancel).not.toHaveBeenCalled()
    })

    it('wraps Tab forward from the last focusable element back to the first', () => {
      renderModal()
      const dialog = screen.getByRole('dialog')
      const focusables = Array.from(dialog.querySelectorAll<HTMLElement>(FOCUSABLE))
      expect(focusables.length).toBeGreaterThan(1)

      const last = focusables[focusables.length - 1]
      last.focus()
      expect(document.activeElement).toBe(last)

      fireEvent.keyDown(document, { key: 'Tab', shiftKey: false })
      expect(document.activeElement).toBe(focusables[0])
    })

    it('wraps Shift+Tab backward from the first focusable element to the last', () => {
      renderModal()
      const dialog = screen.getByRole('dialog')
      const focusables = Array.from(dialog.querySelectorAll<HTMLElement>(FOCUSABLE))
      expect(focusables.length).toBeGreaterThan(1)

      const first = focusables[0]
      first.focus()
      expect(document.activeElement).toBe(first)

      fireEvent.keyDown(document, { key: 'Tab', shiftKey: true })
      expect(document.activeElement).toBe(focusables[focusables.length - 1])
    })

    it('does not prevent default Tab on a middle element', () => {
      renderModal()
      const dialog = screen.getByRole('dialog')
      const focusables = Array.from(dialog.querySelectorAll<HTMLElement>(FOCUSABLE))
      if (focusables.length >= 3) {
        focusables[1].focus()
        const tabEvent = new KeyboardEvent('keydown', { key: 'Tab', bubbles: true, cancelable: true })
        document.dispatchEvent(tabEvent)
        expect(tabEvent.defaultPrevented).toBe(false)
      }
    })

    it('focuses the first focusable element when no element inside is already focused', () => {
      // Blur any active element so the hook sets initial focus
      if (document.activeElement instanceof HTMLElement) {
        document.activeElement.blur()
      }
      renderModal()
      const dialog = screen.getByRole('dialog')
      const focusables = Array.from(dialog.querySelectorAll<HTMLElement>(FOCUSABLE))
      // After hook activates, activeElement should be within the dialog
      expect(dialog.contains(document.activeElement)).toBe(true)
      expect(document.activeElement).toBe(focusables[0])
    })
  })
})
