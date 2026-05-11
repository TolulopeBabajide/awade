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
 * If `err` is an `Error` instance with a non-empty message, returns
 * `err.message`; otherwise returns the provided `fallback` (or a generic
 * default). The empty-message guard (AWD-M-138) prevents banner-style
 * consumers from rendering blank strings when an `Error` is thrown without
 * a message (rare but legal — e.g. some fetch failures or third-party SDKs
 * that re-throw a stripped Error).
 *
 * Use this in `catch (err)` blocks where `err` is typed as `unknown` and
 * you need a string to show the user.
 *
 * @param err     The caught value (usually `unknown` from `catch (err)`)
 * @param fallback Message to return when `err` is not an Error instance
 *                 or when it is an Error with an empty message
 * @returns       A string safe to render in UI (never empty)
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
  return err instanceof Error && err.message ? err.message : fallback
}
