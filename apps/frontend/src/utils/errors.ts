/**
 * Error message helpers.
 *
 * AWD-L-25: shared utility replacing the duplicated
 * `err instanceof Error ? err.message : 'Something went wrong...'`
 * ternary that recurred across pages. Use this in any `catch (err)` block
 * that needs to surface a user-facing message.
 */

const DEFAULT_FALLBACK = 'Something went wrong. Please try again.'

/**
 * Returns a user-facing string for an unknown caught value.
 *
 * If `err` is an `Error` instance, returns `err.message`; otherwise returns
 * the provided `fallback` (or a generic default). Use this in `catch (err)`
 * blocks where `err` is typed as `unknown` and you need a string to show
 * the user.
 *
 * @param err     The caught value (usually `unknown` from `catch (err)`)
 * @param fallback Message to return when `err` is not an Error instance
 * @returns       A string safe to render in UI
 *
 * @example
 *   try { ... } catch (err) {
 *     setError(getErrorMessage(err, 'Failed to save profile.'))
 *   }
 */
export function getErrorMessage(
  err: unknown,
  fallback: string = DEFAULT_FALLBACK,
): string {
  return err instanceof Error ? err.message : fallback
}
