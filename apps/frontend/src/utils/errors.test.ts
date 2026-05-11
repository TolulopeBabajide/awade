import { describe, it, expect } from 'vitest'
import { getErrorMessage } from './errors'

describe('getErrorMessage (AWD-L-25)', () => {
  it('returns err.message when err is an Error instance', () => {
    const err = new Error('Network down')
    expect(getErrorMessage(err)).toBe('Network down')
  })

  it('returns err.message for subclasses of Error', () => {
    class HttpError extends Error {}
    const err = new HttpError('Forbidden')
    expect(getErrorMessage(err)).toBe('Forbidden')
  })

  it('returns the explicit fallback when err is not an Error', () => {
    expect(getErrorMessage('string thrown', 'Failed to save')).toBe(
      'Failed to save',
    )
    expect(getErrorMessage(42, 'Failed to save')).toBe('Failed to save')
    expect(getErrorMessage({ message: 'oops' }, 'Failed to save')).toBe(
      'Failed to save',
    )
    expect(getErrorMessage(null, 'Failed to save')).toBe('Failed to save')
    expect(getErrorMessage(undefined, 'Failed to save')).toBe('Failed to save')
  })

  it('uses the generic default fallback when none is provided', () => {
    expect(getErrorMessage('string thrown')).toBe(
      'Something went wrong. Please try again.',
    )
    expect(getErrorMessage(null)).toBe(
      'Something went wrong. Please try again.',
    )
  })

  it('falls back when an Error has an empty message (AWD-M-138)', () => {
    // An Error with an empty message would otherwise render as a blank banner.
    // The guard ensures consumers always get a meaningful user-facing string.
    const err = new Error('')
    expect(getErrorMessage(err, 'fallback')).toBe('fallback')
  })

  it('produces a complete banner string when composed in a template literal (AWD-M-138)', () => {
    // Regression guard for the consumer pattern in GuideViewPage.handleDownloadPdf —
    // an Error('') would previously yield "Failed: " with no human-readable text.
    const err = new Error('')
    const banner = `Failed: ${getErrorMessage(err, 'unknown error')}`
    expect(banner).toBe('Failed: unknown error')
  })
})
