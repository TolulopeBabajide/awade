/**
 * Shared fixtures and render helper for GuideViewPage tests (AWD-M-140).
 *
 * Consumed by:
 *   GuideViewPage.render.test.tsx
 *   GuideViewPage.interactions.test.tsx
 *
 * NOTE: vi.mock() calls must remain in each test file (they are hoisted at
 * compile time and cannot be delegated to a shared helper).
 */

import { render } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import GuideViewPage from '../GuideViewPage'

// ── Shared test data ──────────────────────────────────────────────────────

export const GUIDE_CONTENT = {
  topic_header: {
    topic: 'Fractions',
    subject: 'Mathematics',
    grade_level: 'Grade 5',
    country: 'Nigeria',
    curriculum: 'NERDC',
  },
  simple_explanation: {
    what_it_is: 'A fraction represents a part of a whole.',
    why_it_matters: 'Essential for everyday maths.',
  },
  home_activity: {
    title: 'Pizza Fraction Game',
    description: 'Use paper to show fractions.',
    materials_needed: ['paper', 'pencil'],
    steps: ['Draw a circle', 'Divide it in half'],
    what_to_look_for: 'Child correctly names the parts.',
  },
  conversation_starters: ['What is half of 8?'],
  common_mistakes: [
    {
      mistake: 'Adding denominators directly',
      why_it_happens: 'Treats fractions like whole numbers.',
      how_to_help: 'Show with real objects.',
    },
  ],
  curriculum_context: {
    what_came_before: 'Division',
    what_comes_next: 'Decimals',
    how_long_in_school: '3 weeks',
  },
  encouragement_tips: ['Celebrate small wins!'],
}

export const MOCK_GUIDE = {
  guide_id: 42,
  child_id: 1,
  topic_id: 10,
  topic_title: 'Fractions',
  subject_name: 'Mathematics',
  ai_generated_content: JSON.stringify(GUIDE_CONTENT),
  user_edited_content: null,
  is_bookmarked: false,
  created_at: '2026-04-25T00:00:00Z',
  updated_at: '2026-04-25T00:00:00Z',
}

// ── Render helper ─────────────────────────────────────────────────────────

export function renderPage(url = '/guides?guide=42') {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })
  const result = render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter
        initialEntries={[url]}
        future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
      >
        <GuideViewPage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
  return { ...result, queryClient }
}
