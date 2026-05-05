import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import AIGenerationLoading from './AIGenerationLoading';

describe('AIGenerationLoading', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders nothing when isVisible is false', () => {
    const { container } = render(
      <AIGenerationLoading isVisible={false} generationType="lesson-resource" />
    );
    expect(container.firstChild).toBeNull();
  });

  it('renders modal when isVisible is true', () => {
    render(
      <AIGenerationLoading isVisible={true} generationType="lesson-resource" />
    );
    expect(screen.getByText('AI Lesson Resource Generation')).toBeInTheDocument();
  });

  it('shows lesson-plan label for lesson-plan generationType', () => {
    render(
      <AIGenerationLoading isVisible={true} generationType="lesson-plan" />
    );
    expect(screen.getByText('AI Lesson Plan Generation')).toBeInTheDocument();
  });

  it('shows topic/subject/gradeLevel info when all are provided', () => {
    render(
      <AIGenerationLoading
        isVisible={true}
        generationType="lesson-resource"
        topic="Algebra"
        subject="Mathematics"
        gradeLevel="Grade 8"
      />
    );
    expect(screen.getByText('Algebra')).toBeInTheDocument();
    expect(screen.getByText('Mathematics')).toBeInTheDocument();
    // gradeLevel is rendered as "(Grade 8)" inside the sentence
    expect(screen.getByText(/Grade 8/)).toBeInTheDocument();
  });

  it('does not show topic info when props are missing', () => {
    render(
      <AIGenerationLoading
        isVisible={true}
        generationType="lesson-resource"
        topic="Algebra"
        // subject and gradeLevel omitted
      />
    );
    // The "Generating for" sentence requires all three — only generic header shown
    expect(screen.queryByText('Algebra')).not.toBeInTheDocument();
  });

  it('includes submit-context step when hasContext is true', async () => {
    render(
      <AIGenerationLoading
        isVisible={true}
        generationType="lesson-resource"
        hasContext={true}
      />
    );
    expect(screen.getByText('Submitting Context')).toBeInTheDocument();
  });

  it('excludes submit-context step when hasContext is false', async () => {
    render(
      <AIGenerationLoading
        isVisible={true}
        generationType="lesson-resource"
        hasContext={false}
      />
    );
    expect(screen.queryByText('Submitting Context')).not.toBeInTheDocument();
  });

  it('marks step as in-progress when currentStep matches', async () => {
    render(
      <AIGenerationLoading
        isVisible={true}
        generationType="lesson-resource"
        currentStep="ai-generation"
      />
    );
    // The in-progress step title should be styled with orange color class
    const aiStepTitle = screen.getByText('AI Content Generation');
    expect(aiStepTitle).toHaveClass('text-orange-700');
  });

  it('calls onComplete after delay when currentStep is complete', async () => {
    const onComplete = vi.fn();
    render(
      <AIGenerationLoading
        isVisible={true}
        generationType="lesson-resource"
        currentStep="complete"
        onComplete={onComplete}
      />
    );
    expect(onComplete).not.toHaveBeenCalled();
    act(() => {
      vi.advanceTimersByTime(1100);
    });
    expect(onComplete).toHaveBeenCalledTimes(1);
  });

  it('shows progress footer with "AI Generation in Progress"', () => {
    render(
      <AIGenerationLoading isVisible={true} generationType="lesson-resource" />
    );
    expect(screen.getByText('AI Generation in Progress')).toBeInTheDocument();
  });

  // AWD-M-73: lesson-plan generationType must render steps (was empty before fix)
  it('renders 4 steps for lesson-plan generationType', () => {
    render(
      <AIGenerationLoading isVisible={true} generationType="lesson-plan" />
    );
    expect(screen.getByText('Fetching Curriculum Data')).toBeInTheDocument();
    expect(screen.getByText('AI Content Generation')).toBeInTheDocument();
    expect(screen.getByText('Saving Lesson Plan')).toBeInTheDocument();
    expect(screen.getByText('Generation Complete')).toBeInTheDocument();
  });

  it('shows "Step 0 of 4" counter for lesson-plan before any step is active', () => {
    render(
      <AIGenerationLoading isVisible={true} generationType="lesson-plan" />
    );
    expect(screen.getByText('Step 0 of 4')).toBeInTheDocument();
  });

  it('lesson-plan ai-generation step becomes in-progress when currentStep matches', () => {
    render(
      <AIGenerationLoading
        isVisible={true}
        generationType="lesson-plan"
        currentStep="ai-generation"
      />
    );
    const stepTitle = screen.getByText('AI Content Generation');
    expect(stepTitle).toHaveClass('text-orange-700');
  });

  // AWD-M-74: progress must be non-zero on first render when currentStep is provided
  // (stale closure bug caused `steps` to read as [] on mount → NaN/0%)
  it('shows non-zero progress when currentStep is provided on mount (AWD-M-74)', () => {
    render(
      <AIGenerationLoading
        isVisible={true}
        generationType="lesson-plan"
        currentStep="fetch-curriculum-data"
      />
    );
    // fetch-curriculum-data is step 1 of 4 → 25%
    expect(screen.getByText('25%')).toBeInTheDocument();
  });

  it('shows 50% progress when currentStep is ai-generation for lesson-plan (AWD-M-74)', () => {
    render(
      <AIGenerationLoading
        isVisible={true}
        generationType="lesson-plan"
        currentStep="ai-generation"
      />
    );
    // ai-generation is step 2 of 4 → 50%
    expect(screen.getByText('50%')).toBeInTheDocument();
  });

  // AWD-M-75: onComplete must NOT fire if the component unmounts before the 1s delay
  it('does not call onComplete after unmount before timer fires (AWD-M-75)', () => {
    const onComplete = vi.fn();
    const { unmount } = render(
      <AIGenerationLoading
        isVisible={true}
        generationType="lesson-resource"
        currentStep="complete"
        onComplete={onComplete}
      />
    );
    // Unmount before the 1000 ms delay elapses
    unmount();
    act(() => {
      vi.advanceTimersByTime(1100);
    });
    expect(onComplete).not.toHaveBeenCalled();
  });
});
