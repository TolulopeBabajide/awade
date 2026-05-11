/**
 * AWD-M-141: This file has been split into focused test files.
 *   - ParentDashboardPage.render.test.tsx  (14 tests: page states, HTML structure, a11y, auto-select)
 *   - ParentDashboardPage.delete.test.tsx  (16 tests: consent gate, delete workflow, DeleteChildConfirmModal)
 *
 * The original 737-line file is kept as a skip stub because the virtiofs
 * sandbox cannot delete files (same constraint as AWD-H-78).
 * Tolu: run `git rm apps/frontend/src/pages/ParentDashboardPage.test.tsx` on
 * the dev machine after CI green.
 */

import { describe, it } from 'vitest'

describe.skip('ParentDashboardPage (AWD-M-141 stub — see .render.test and .delete.test)', () => {
  it('placeholder — all tests live in the split files above', () => {})
})
