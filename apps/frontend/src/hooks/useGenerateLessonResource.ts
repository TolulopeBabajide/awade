import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import apiService from '../services/api';
import { sanitizeInput } from '../utils/sanitizer';
import type { LessonPlanData, ResourceStatus } from '../types/lesson-plans';

// ── Module-level helpers ────────────────────────────────────────────────────
// Extracted from LessonPlanDetailPage (AWD-M-134, AWD-M-133) and moved here
// as part of AWD-L-29 hook extraction.

/**
 * Submits teacher-provided context for a lesson plan if any was given.
 * Returns cleanly when context is empty.  Throws on API error.
 * Calls `signal.throwIfAborted()` post-await so the caller aborts on unmount (AWD-M-137).
 */
async function submitContextIfProvided(
  lessonPlanId: string,
  sanitizedContext: string,
  signal: AbortSignal,
  setCurrentGenerationStep: (step: string) => void,
): Promise<void> {
  if (!sanitizedContext) return;
  setCurrentGenerationStep('submit-context');
  const contextResponse = await apiService.submitContext(lessonPlanId, sanitizedContext);
  signal.throwIfAborted();
  if (contextResponse.error) {
    throw new Error(contextResponse.error);
  }
}

/**
 * Polls `getLessonResource` every 2 s until the resource leaves the
 * "processing" state.  Calls `signal.throwIfAborted()` at each async
 * suspension point so unmount aborts polling cleanly (AWD-M-137).
 *
 * Throws on timeout (60 polls ≈ 2 minutes) or AI failure.
 * Returns cleanly when the resource completes successfully.
 */
async function pollUntilComplete(
  resourceId: string,
  signal: AbortSignal,
): Promise<void> {
  let status: ResourceStatus = 'processing';
  let attempts = 0;
  const maxAttempts = 60;

  while (status === 'processing' && attempts < maxAttempts) {
    await new Promise<void>(resolve => setTimeout(resolve, 2000));
    signal.throwIfAborted();
    attempts++;

    const pollResponse = await apiService.getLessonResource(resourceId);
    signal.throwIfAborted();
    if (pollResponse.error || !pollResponse.data) {
      if (import.meta.env.DEV) {
        console.warn('Polling failed temporarily', pollResponse.error);
      }
      continue;
    }
    status = pollResponse.data.status as ResourceStatus;
  }

  signal.throwIfAborted();
  // AWD-M-136: lookup collapses the 3-branch status check to ≤10 cyclomatic complexity
  const statusErrors: Partial<Record<ResourceStatus, string>> = {
    processing: 'Generation timed out. Please check back later.',
    failed: 'AI generation failed. Please try again.',
  };
  if (status !== 'complete') {
    throw new Error(statusErrors[status] ?? `Unexpected resource status: ${status}`);
  }
}

// ── Hook ────────────────────────────────────────────────────────────────────

export interface UseGenerateLessonResourceReturn {
  isGeneratingLessonResource: boolean;
  contextFeedback: { type: 'success' | 'error'; message: string } | null;
  currentGenerationStep: string;
  handleGenerateLessonResource: () => Promise<void>;
  /** Called by AIGenerationLoading.onComplete to dismiss the loading overlay. */
  resetGenerating: () => void;
}

/**
 * AWD-L-29 — Encapsulates the lesson-resource generation workflow extracted
 * from LessonPlanDetailPage.
 *
 * @param lessonPlan     - current lesson plan (null while loading)
 * @param context        - teacher-provided context string (from page textarea)
 * @param onClearContext - called after successful generation to clear the textarea
 */
export function useGenerateLessonResource(
  lessonPlan: LessonPlanData | null,
  context: string,
  onClearContext: () => void,
): UseGenerateLessonResourceReturn {
  const navigate = useNavigate();
  const [isGeneratingLessonResource, setIsGeneratingLessonResource] = useState(false);
  const [contextFeedback, setContextFeedback] = useState<{
    type: 'success' | 'error';
    message: string;
  } | null>(null);
  const [currentGenerationStep, setCurrentGenerationStep] = useState<string>('');

  // AbortController ref — abort() is called on unmount to cancel in-flight generation (AWD-M-137)
  const abortControllerRef = useRef<AbortController | null>(null);
  useEffect(() => {
    return () => {
      abortControllerRef.current?.abort();
    };
  }, []);

  /**
   * Handles post-generation success: sets success feedback, clears the context
   * input, schedules feedback dismissal, and navigates to the edit page.
   */
  const handleGenerationSuccess = () => {
    setContextFeedback({
      type: 'success',
      message: 'Lesson resource generated successfully! You can now view and edit the generated content.',
    });
    onClearContext();
    // Clear feedback after 5 seconds — check signal so unmount after timeout is safe (AWD-M-137)
    const signal = abortControllerRef.current?.signal;
    setTimeout(() => {
      if (!signal?.aborted) setContextFeedback(null);
    }, 5000);
    navigate(`/lesson-plans/${lessonPlan!.lesson_id}/resources/edit`);
  };

  const handleGenerateLessonResource = async (): Promise<void> => {
    if (!lessonPlan) return;

    const controller = new AbortController();
    abortControllerRef.current = controller;
    const { signal } = controller;

    setIsGeneratingLessonResource(true);
    setContextFeedback(null);
    setCurrentGenerationStep('validate-lesson-plan');

    try {
      // Sanitize context input
      const sanitizedContext = sanitizeInput(context);

      // Step 1: Submit context if provided (AWD-M-134: extracted to reduce complexity)
      await submitContextIfProvided(
        lessonPlan.lesson_id.toString(),
        sanitizedContext,
        signal,
        setCurrentGenerationStep,
      );
      signal.throwIfAborted();

      // Step 2: Fetch curriculum data (simulated pause to show step)
      setCurrentGenerationStep('fetch-curriculum-data');
      await new Promise<void>(resolve => setTimeout(resolve, 500));
      signal.throwIfAborted();

      // Step 3: Initiate AI generation
      setCurrentGenerationStep('ai-generation');
      const response = await apiService.generateLessonResource(
        lessonPlan.lesson_id.toString(),
        sanitizedContext || 'Generate a comprehensive lesson resource for this lesson plan',
      );
      signal.throwIfAborted();
      if (response.error || !response.data) {
        throw new Error(response.error || 'Failed to initiate resource generation');
      }

      // Step 4: Poll until complete (only when initially processing)
      if (response.data.status === 'processing') {
        await pollUntilComplete(response.data.lesson_resources_id.toString(), signal);
      }

      // Step 5: Brief completion pause, then navigate
      setCurrentGenerationStep('complete');
      await new Promise<void>(resolve => setTimeout(resolve, 500));
      signal.throwIfAborted();

      handleGenerationSuccess();
    } catch (err) {
      if (signal.aborted) return;
      const message = err instanceof Error ? err.message : String(err);
      setContextFeedback({
        type: 'error',
        message: message || 'Failed to generate lesson resource. Please try again.',
      });
    } finally {
      if (!signal.aborted) {
        setIsGeneratingLessonResource(false);
        setCurrentGenerationStep('');
      }
    }
  };

  return {
    isGeneratingLessonResource,
    contextFeedback,
    currentGenerationStep,
    handleGenerateLessonResource,
    resetGenerating: () => setIsGeneratingLessonResource(false),
  };
}
