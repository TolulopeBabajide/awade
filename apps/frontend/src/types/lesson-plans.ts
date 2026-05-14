/** Types for the lesson-plans feature */

// ── Lesson Resource Status (AWD-M-135) ─────────────────────────────────────

/**
 * Exhaustive union of the status values returned by the lesson-resource API.
 * Using a typed union instead of `as string` ensures TypeScript narrows the
 * value correctly and unknown statuses surface as errors rather than silently
 * triggering navigation.
 */
export type ResourceStatus = 'processing' | 'failed' | 'complete';

// ── Lesson Plan Data (AWD-L-29) ─────────────────────────────────────────────

/**
 * Shape of a lesson plan as returned by the API.
 * Shared between LessonPlanDetailPage and useGenerateLessonResource.
 */
export interface LessonPlanData {
  lesson_id: number;
  title: string;
  subject: string;
  grade_level: string;
  topic: string;
  author_id: number;
  duration_minutes: number;
  created_at: string;
  updated_at: string;
  status: string;
  curriculum_learning_objectives: string[];
  curriculum_contents: string[];
}
