/**
 * useFocusTrap — AWD-M-56
 *
 * Traps keyboard focus within a container element when active.
 *
 * Behaviours:
 * - Focuses the first focusable descendant on activation (unless one is
 *   already focused inside the container, e.g. via `autoFocus`).
 * - Wraps Tab / Shift+Tab so focus never escapes the container.
 * - Calls `onEscape` when the user presses Escape.
 * - Restores focus to the element that was focused before activation.
 */
import { useEffect, useRef } from 'react'

const FOCUSABLE_SELECTORS = [
  'a[href]',
  'button:not([disabled])',
  'input:not([disabled])',
  'select:not([disabled])',
  'textarea:not([disabled])',
  '[tabindex]:not([tabindex="-1"])',
].join(', ')

function getFocusable(container: HTMLElement): HTMLElement[] {
  return Array.from(container.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTORS))
}

export function useFocusTrap(
  containerRef: React.RefObject<HTMLElement | null>,
  isActive: boolean,
  onEscape?: () => void,
): void {
  // Keep onEscape in a ref so the keydown handler always calls the latest
  // version without needing to re-register on every render.
  const onEscapeRef = useRef(onEscape)
  useEffect(() => {
    onEscapeRef.current = onEscape
  }, [onEscape])

  useEffect(() => {
    if (!isActive || !containerRef.current) return

    const container = containerRef.current
    const previouslyFocused = document.activeElement as HTMLElement | null

    // Focus the first focusable element unless something inside is already
    // focused (e.g. via the `autoFocus` attribute).
    if (!container.contains(document.activeElement)) {
      const focusables = getFocusable(container)
      if (focusables.length > 0) {
        focusables[0].focus()
      }
    }

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault()
        onEscapeRef.current?.()
        return
      }

      if (e.key !== 'Tab') return

      const focusables = getFocusable(container)
      if (focusables.length === 0) return

      const first = focusables[0]
      const last = focusables[focusables.length - 1]

      if (e.shiftKey) {
        // Shift+Tab going backwards — wrap from first to last
        if (document.activeElement === first) {
          e.preventDefault()
          last.focus()
        }
      } else {
        // Tab going forwards — wrap from last to first
        if (document.activeElement === last) {
          e.preventDefault()
          first.focus()
        }
      }
    }

    document.addEventListener('keydown', handleKeyDown)

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      // Restore focus to the element that was active before the trap engaged
      previouslyFocused?.focus()
    }
  }, [isActive, containerRef])
}
