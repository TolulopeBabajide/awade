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
import { render, screen } from '@testing-library/react'
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
    renderModal()
    const checkbox = screen.getByRole('checkbox')
    await userEvent.click(checkbox)
    const btn = screen.getByRole('button', { name: /i agree/i })
    expect(btn).not.toBeDisabled()
  })

  it('calls onConsented when "I Agree" is clicked with checkbox ticked', async () => {
    const { props } = renderModal()
    const checkbox = screen.getByRole('checkbox')
    await userEvent.click(checkbox)
    const btn = screen.getByRole('button', { name: /i agree/i })
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
})
