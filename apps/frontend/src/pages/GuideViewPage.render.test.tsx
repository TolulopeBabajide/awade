/**
 * GuideViewPage — render tests (AWD-M-140)
 *
 * Covers: loading state, error state, success state, unauthenticated / disabled
 * query, and layout-shell presence in each state (AWD-M-139).
 *
 * Interaction tests live in GuideViewPage.interactions.test.tsx.
 */

import { screen, waitFor } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'

// ── Module mocks (must live here — vi.mock is hoisted) ────────────────────

vi.mock('../components/Sidebar', () => ({ default: () => <div data-testid="sidebar" /> }))
vi.mock('../components/MobileNavigation', () => ({
  default: () => <div data-testid="mobile-nav" />,
}))

vi.mock('../services/api', () => ({
  default: {
    getGuide: vi.fn(),
    generateGuide: vi.fn(),
    toggleGuideBookmark: vi.fn(),
    exportGuidePdf: vi.fn(),
  },
}))

// ── Imports after mocks ───────────────────────────────────────────────────

import apiService from '../services/api'
import { MOCK_GUIDE, renderPage } from './__fixtures__/guideViewPage'

const mockGetGuide = vi.mocked(apiService.getGuide)
const mockGenerateGuide = vi.mocked(apiService.generateGuide)

// ── Tests ─────────────────────────────────────────────────────────────────

describe('GuideViewPage — render', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  // ── Loading state ───────────────────────────────────────────────────────
  it('shows loading spinner while guide is fetching', () => {
    mockGetGuide.mockReturnValue(new Promise(() => {}))
    renderPage()
    expect(screen.getByText('Generating your guide...')).toBeInTheDocument()
  })

  // AWD-M-54: loading container is announced to assistive tech via role="status"
  it('exposes the loading container with role="status" and aria-live', () => {
    mockGetGuide.mockReturnValue(new Promise(() => {}))
    renderPage()
    const status = screen.getByRole('status')
    expect(status).toHaveAttribute('aria-live', 'polite')
    expect(status).toHaveTextContent(/generating your guide/i)
  })

  // ── Error state ─────────────────────────────────────────────────────────
  it('shows error message when guide fetch returns an error', async () => {
    mockGetGuide.mockResolvedValue({ data: undefined, error: 'Guide not found' })
    renderPage()
    await waitFor(() => {
      expect(screen.getByText('Guide not found')).toBeInTheDocument()
    }, { timeout: 5000 })
  })

  it('shows fallback error when AI content is malformed JSON', async () => {
    const brokenGuide = { ...MOCK_GUIDE, ai_generated_content: 'not-valid-json' }
    mockGetGuide.mockResolvedValue({ data: brokenGuide, error: undefined })
    renderPage()
    await waitFor(() => {
      expect(screen.getByText('Could not load guide')).toBeInTheDocument()
    }, { timeout: 5000 })
  })

  // ── Success state ───────────────────────────────────────────────────────
  it('renders guide topic title and subject in success state', async () => {
    mockGetGuide.mockResolvedValue({ data: MOCK_GUIDE, error: undefined })
    renderPage()
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /Fractions/i })).toBeInTheDocument()
    }, { timeout: 5000 })
    expect(screen.getByText('A fraction represents a part of a whole.')).toBeInTheDocument()
  })

  it('renders guide via generateGuide when child+topic params are supplied (no guide ID)', async () => {
    mockGenerateGuide.mockResolvedValue({ data: MOCK_GUIDE, error: undefined })
    renderPage('/guides?child=1&topic=10')
    await waitFor(() => {
      expect(mockGenerateGuide).toHaveBeenCalledWith(1, 10)
    }, { timeout: 5000 })
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /Fractions/i })).toBeInTheDocument()
    }, { timeout: 5000 })
  })

  // ── Unauthenticated / disabled query ────────────────────────────────────
  it('does not fetch when neither guide ID nor child+topic params are provided', () => {
    renderPage('/guides')
    expect(mockGetGuide).not.toHaveBeenCalled()
    expect(mockGenerateGuide).not.toHaveBeenCalled()
  })

  // ── AWD-M-139: GuidePageShell renders layout chrome in every render path ──
  describe('GuidePageShell layout shell (AWD-M-139)', () => {
    it('renders sidebar and mobile-nav in loading state', () => {
      mockGetGuide.mockReturnValue(new Promise(() => {}))
      renderPage()
      expect(screen.getByTestId('sidebar')).toBeInTheDocument()
      expect(screen.getByTestId('mobile-nav')).toBeInTheDocument()
    })

    it('renders sidebar and mobile-nav in error state', async () => {
      mockGetGuide.mockResolvedValue({ data: undefined, error: 'Not found' })
      renderPage()
      await waitFor(() => expect(screen.getByText('Not found')).toBeInTheDocument(), { timeout: 5000 })
      expect(screen.getByTestId('sidebar')).toBeInTheDocument()
      expect(screen.getByTestId('mobile-nav')).toBeInTheDocument()
    })

    it('renders sidebar and mobile-nav in success state', async () => {
      mockGetGuide.mockResolvedValue({ data: MOCK_GUIDE, error: undefined })
      renderPage()
      await waitFor(() =>
        expect(screen.getByRole('heading', { name: /Fractions/i })).toBeInTheDocument(),
      { timeout: 5000 })
      expect(screen.getByTestId('sidebar')).toBeInTheDocument()
      expect(screen.getByTestId('mobile-nav')).toBeInTheDocument()
    })

    it('success state <main> has id="main-content" and tabIndex={-1} for skip-nav', async () => {
      mockGetGuide.mockResolvedValue({ data: MOCK_GUIDE, error: undefined })
      renderPage()
      await waitFor(() =>
        expect(screen.getByRole('heading', { name: /Fractions/i })).toBeInTheDocument(),
      { timeout: 5000 })
      const main = document.querySelector('main')
      expect(main).toHaveAttribute('id', 'main-content')
      expect(main).toHaveAttribute('tabindex', '-1')
    })
  })
})
