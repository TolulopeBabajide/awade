// AWD-M-140: This file has been split into two focused test files:
//   GuideViewPage.render.test.tsx        — loading, error, success, unauthenticated, layout shell (11 tests)
//   GuideViewPage.interactions.test.tsx  — WhatsApp share, PDF download, bookmark, DOM lifecycle (14 tests)
// Shared fixtures and renderPage helper live in ./__fixtures__/guideViewPage.tsx
//
// The virtiofs FUSE sandbox cannot delete files (same constraint as AWD-H-78).
// Tolu: run `git rm apps/frontend/src/pages/GuideViewPage.test.tsx` on
// your dev machine after CI confirms green, then commit the removal.
import { describe } from 'vitest'

// Skipped placeholder — satisfies Vitest's "No test suite found" guard.
describe.skip('GuideViewPage (split — see AWD-M-140)', () => {})
