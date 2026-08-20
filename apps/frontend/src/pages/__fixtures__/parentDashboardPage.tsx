/**
 * Shared fixtures and render helper for ParentDashboardPage tests (AWD-M-141).
 *
 * Consumed by:
 *   ParentDashboardPage.render.test.tsx
 *   ParentDashboardPage.delete.test.tsx
 *
 * NOTE: vi.mock() calls must remain in each test file (they are hoisted at
 * compile time and cannot be delegated to a shared helper).
 */

import { render } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import ParentDashboardPage from '../ParentDashboardPage'
import type { ChildProfile, ChildTopic } from '../../types/children'

// ── Factory helpers ───────────────────────────────────────────────────────

export function makeChild(overrides: Partial<ChildProfile> = {}): ChildProfile {
  return {
    child_id: 1,
    parent_id: 10,
    name: 'Test Child 01',
    age: 8,
    school_name: 'Test Primary School',
    country_id: 1,
    country_name: 'TestLand',
    curricula_id: 2,
    curriculum_title: 'Test Curriculum',
    grade_level_id: 3,
    grade_level_name: 'Grade 3',
    subjects: [1],
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    ...overrides,
  }
}

export function makeTopic(overrides: Partial<ChildTopic> = {}): ChildTopic {
  return {
    topic_id: 101,
    topic_title: 'Test Topic',
    subject_name: 'Mathematics',
    subject_id: null,
    ...overrides,
  }
}

// ── Render helper ─────────────────────────────────────────────────────────

export function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false, staleTime: 0 },
    },
  })
  return render(
    <MemoryRouter
      initialEntries={['/dashboard']}
      future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
    >
      <QueryClientProvider client={queryClient}>
        <ParentDashboardPage />
      </QueryClientProvider>
    </MemoryRouter>,
  )
}
