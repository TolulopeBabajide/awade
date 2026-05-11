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

  it('prefers err.message over the fallback even when an Error has an empty message', () => {
    // Empty-string message is still a string from an Error instance.
    const err = new Error('')
    expect(getErrorMessage(err, 'fallback')).toBe('')
  })
})
