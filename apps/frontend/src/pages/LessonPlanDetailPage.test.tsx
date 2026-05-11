// AWD-L-30: This file has been split into two focused test files:
//   LessonPlanDetailPage.load.test.tsx     — fetch / load / error / nav-state (8 tests)
//   LessonPlanDetailPage.generate.test.tsx — generation workflow / AbortController / polling (10 tests)
//
// The virtiofs FUSE sandbox cannot delete files (same constraint as AWD-H-78).
// Tolu: run `git rm apps/frontend/src/pages/LessonPlanDetailPage.test.tsx` on
// your dev machine after CI confirms green, then commit the removal.
import { describe } from 'vitest'

// Skipped placeholder — satisfies Vitest's "No test suite found" guard.
// Remove alongside git rm above.
describe.skip('LessonPlanDetailPage (stub — split to .load + .generate by AWD-L-30)', () => {})
