/** Types for the lesson-plans feature */

// ── Lesson Resource Status (AWD-M-135) ─────────────────────────────────────

/**
 * Exhaustive union of the status values returned by the lesson-resource API.
 * Using a typed union instead of `as string` ensures TypeScript narrows the
 * value correctly and unknown statuses surface as errors rather than silently
 * triggering navigation.
 */
export type ResourceStatus = 'processing' | 'failed' | 'complete';
