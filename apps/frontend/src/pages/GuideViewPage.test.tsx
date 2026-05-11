import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import GuideViewPage from './GuideViewPage'

// ── Lightweight stand-ins for layout components ───────────────────────────
vi.mock('../components/Sidebar', () => ({ default: () => <div data-testid="sidebar" /> }))
vi.mock('../components/MobileNavigation', () => ({
  default: () => <div data-testid="mobile-nav" />,
}))

// ── Mock API service ──────────────────────────────────────────────────────
vi.mock('../services/api', () => ({
  default: {
    getGuide: vi.fn(),
    generateGuide: vi.fn(),
    toggleGuideBookmark: vi.fn(),
    exportGuidePdf: vi.fn(),
  },
}))

import apiService from '../services/api'
const mockGetGuide = vi.mocked(apiService.getGuide)
const mockGenerateGuide = vi.mocked(apiService.generateGuide)
const mockToggleBookmark = vi.mocked(apiService.toggleGuideBookmark)
const mockExportGuidePdf = vi.mocked(apiService.exportGuidePdf)

// ── Test fixtures ─────────────────────────────────────────────────────────
const GUIDE_CONTENT = {
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

const MOCK_GUIDE = {
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
function renderPage(url = '/guides?guide=42') {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })
  const result = render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[url]} future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <GuideViewPage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
  return { ...result, queryClient }
}

// ── Tests ─────────────────────────────────────────────────────────────────
describe('GuideViewPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  // ── Loading state ───────────────────────────────────────────────────────
  it('shows loading spinner while guide is fetching', () => {
    // Never-resolving promise → stays in loading state
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
    })
  })

  it('shows fallback error when AI content is malformed JSON', async () => {
    const brokenGuide = { ...MOCK_GUIDE, ai_generated_content: 'not-valid-json' }
    mockGetGuide.mockResolvedValue({ data: brokenGuide, error: undefined })
    renderPage()
    await waitFor(() => {
      expect(screen.getByText('Could not load guide')).toBeInTheDocument()
    })
  })

  // ── Success state ───────────────────────────────────────────────────────
  it('renders guide topic title and subject in success state', async () => {
    mockGetGuide.mockResolvedValue({ data: MOCK_GUIDE, error: undefined })
    renderPage()
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /Fractions/i })).toBeInTheDocument()
    })
    expect(screen.getByText('A fraction represents a part of a whole.')).toBeInTheDocument()
  })

  it('renders guide via generateGuide when child+topic params are supplied (no guide ID)', async () => {
    mockGenerateGuide.mockResolvedValue({ data: MOCK_GUIDE, error: undefined })
    renderPage('/guides?child=1&topic=10')
    await waitFor(() => {
      expect(mockGenerateGuide).toHaveBeenCalledWith(1, 10)
    })
    await waitFor(() => {
      expect(
        screen.getByRole('heading', { name: /Fractions/i }),
      ).toBeInTheDocument()
    })
  })

  // ── WhatsApp share (AWD-M-05) ───────────────────────────────────────────
  it('renders the WhatsApp share button', async () => {
    mockGetGuide.mockResolvedValue({ data: MOCK_GUIDE, error: undefined })
    renderPage()
    await waitFor(() => {
      expect(screen.getByLabelText('Share this guide on WhatsApp')).toBeInTheDocument()
    })
  })

  it('opens the correct WhatsApp share URL when the button is clicked', async () => {
    const openSpy = vi.spyOn(window, 'open').mockReturnValue(null)
    mockGetGuide.mockResolvedValue({ data: MOCK_GUIDE, error: undefined })
    renderPage()

    const shareBtn = await screen.findByLabelText('Share this guide on WhatsApp')
    await userEvent.click(shareBtn)

    expect(openSpy).toHaveBeenCalledOnce()
    const [url, target, features] = openSpy.mock.calls[0]
    expect(url).toMatch(/^https:\/\/wa\.me\/\?text=/)
    expect(target).toBe('_blank')
    expect(features).toBe('noopener,noreferrer')

    const decoded = decodeURIComponent((url as string).replace('https://wa.me/?text=', ''))
    expect(decoded).toContain('Fractions')
    expect(decoded).toContain('Mathematics')
    expect(decoded).toContain('Grade 5')
    expect(decoded).toContain('Pizza Fraction Game')
    expect(decoded).toContain('awade.app')

    openSpy.mockRestore()
  })

  it('does not call window.open when content is null', () => {
    const openSpy = vi.spyOn(window, 'open').mockReturnValue(null)
    // Never resolves → loading state; share button not rendered
    mockGetGuide.mockReturnValue(new Promise(() => {}))
    renderPage()
    expect(openSpy).not.toHaveBeenCalled()
    openSpy.mockRestore()
  })

  // ── Unauthenticated / disabled query ────────────────────────────────────
  it('does not fetch when neither guide ID nor child+topic params are provided', () => {
    renderPage('/guides')
    expect(mockGetGuide).not.toHaveBeenCalled()
    expect(mockGenerateGuide).not.toHaveBeenCalled()
  })

  // ── AWD-M-79 + AWD-H-79: handleDownloadPdf error paths ──────────────────
  describe('handleDownloadPdf error banner (AWD-M-79)', () => {
    it('shows inline error banner when exportGuidePdf returns an API error', async () => {
      mockGetGuide.mockResolvedValue({ data: MOCK_GUIDE, error: undefined })
      mockExportGuidePdf.mockResolvedValue({ error: 'PDF generation failed' })

      renderPage()
      const downloadBtn = await screen.findByLabelText('Download this guide as a PDF')
      await userEvent.click(downloadBtn)

      await waitFor(() => {
        expect(screen.getByRole('alert')).toHaveTextContent(
          'Could not download PDF: PDF generation failed',
        )
      })
    })

    it('shows inline error banner when exportGuidePdf throws unexpectedly', async () => {
      mockGetGuide.mockResolvedValue({ data: MOCK_GUIDE, error: undefined })
      mockExportGuidePdf.mockRejectedValue(new Error('Network abort'))

      renderPage()
      const downloadBtn = await screen.findByLabelText('Download this guide as a PDF')
      await userEvent.click(downloadBtn)

      await waitFor(() => {
        expect(screen.getByRole('alert')).toHaveTextContent(
          'Could not download PDF: Network abort',
        )
      })
    })

    it('clears the error banner on a subsequent download attempt', async () => {
      mockGetGuide.mockResolvedValue({ data: MOCK_GUIDE, error: undefined })
      // First call fails, second call resolves successfully
      mockExportGuidePdf
        .mockRejectedValueOnce(new Error('Timeout'))
        .mockResolvedValueOnce({ blob: new Blob(), filename: 'guide.pdf' })

      // jsdom does not implement blob URL APIs — define stubs so the success path completes
      URL.createObjectURL = vi.fn().mockReturnValue('blob:mock')
      URL.revokeObjectURL = vi.fn()

      renderPage()
      const downloadBtn = await screen.findByLabelText('Download this guide as a PDF')

      // Trigger failure
      await userEvent.click(downloadBtn)
      await waitFor(() => {
        expect(screen.getByRole('alert')).toHaveTextContent('Could not download PDF')
      })

      // Trigger successful retry — error should disappear
      await userEvent.click(downloadBtn)
      await waitFor(() => {
        expect(screen.queryByRole('alert')).not.toBeInTheDocument()
      })

      // Restore to undefined so other tests are not affected
      ;(URL as { createObjectURL?: unknown }).createObjectURL = undefined
      ;(URL as { revokeObjectURL?: unknown }).revokeObjectURL = undefined
    })

    it('re-enables the download button after an unexpected throw', async () => {
      mockGetGuide.mockResolvedValue({ data: MOCK_GUIDE, error: undefined })
      mockExportGuidePdf.mockRejectedValue(new Error('Timeout'))

      renderPage()
      const downloadBtn = await screen.findByLabelText('Download this guide as a PDF')
      await userEvent.click(downloadBtn)

      // After catch + finally the button must be re-enabled (not stuck in disabled state)
      await waitFor(() => {
        expect(downloadBtn).not.toBeDisabled()
      })
    })
  })

  // ── AWD-L-33: downloadError dismiss button ──────────────────────────────
  describe('downloadError dismiss button (AWD-L-33)', () => {
    it('renders a dismiss button inside the error banner', async () => {
      mockGetGuide.mockResolvedValue({ data: MOCK_GUIDE, error: undefined })
      mockExportGuidePdf.mockResolvedValue({ error: 'PDF generation failed' })

      renderPage()
      const downloadBtn = await screen.findByLabelText('Download this guide as a PDF')
      await userEvent.click(downloadBtn)

      await waitFor(() => {
        expect(screen.getByRole('alert')).toBeInTheDocument()
      })
      expect(screen.getByLabelText('Dismiss error')).toBeInTheDocument()
    })

    it('clears the error banner when the dismiss button is clicked', async () => {
      mockGetGuide.mockResolvedValue({ data: MOCK_GUIDE, error: undefined })
      mockExportGuidePdf.mockResolvedValue({ error: 'PDF generation failed' })

      renderPage()
      const downloadBtn = await screen.findByLabelText('Download this guide as a PDF')
      await userEvent.click(downloadBtn)

      await waitFor(() => {
        expect(screen.getByRole('alert')).toBeInTheDocument()
      })

      const dismissBtn = screen.getByLabelText('Dismiss error')
      await userEvent.click(dismissBtn)

      await waitFor(() => {
        expect(screen.queryByRole('alert')).not.toBeInTheDocument()
      })
    })
  })

  // ── AWD-L-32: PDF anchor appended to DOM before click ──────────────────
  describe('handleDownloadPdf anchor DOM lifecycle (AWD-L-32)', () => {
    it('appends the anchor to document.body before clicking and removes it after', async () => {
      mockGetGuide.mockResolvedValue({ data: MOCK_GUIDE, error: undefined })
      mockExportGuidePdf.mockResolvedValue({
        blob: new Blob(),
        filename: 'guide.pdf',
      })

      // jsdom does not implement blob URL APIs — define stubs so the success path completes
      URL.createObjectURL = vi.fn().mockReturnValue('blob:mock')
      URL.revokeObjectURL = vi.fn()

      // Spy real DOM methods so we can verify the click is sandwiched between append/remove.
      // React itself uses appendChild during initial mount, so we filter to anchor elements only.
      const appendSpy = vi.spyOn(document.body, 'appendChild')
      const removeSpy = vi.spyOn(document.body, 'removeChild')
      let anchorWasInDomAtClick = false
      const originalCreateElement = document.createElement.bind(document)
      const createElementSpy = vi
        .spyOn(document, 'createElement')
        .mockImplementation((tag: string) => {
          const el = originalCreateElement(tag) as HTMLElement
          if (tag === 'a') {
            const realClick = el.click.bind(el)
            el.click = () => {
              anchorWasInDomAtClick = document.body.contains(el)
              realClick()
            }
          }
          return el as unknown as HTMLElement
        })

      try {
        renderPage()
        const downloadBtn = await screen.findByLabelText('Download this guide as a PDF')
        await userEvent.click(downloadBtn)

        await waitFor(() => {
          expect(mockExportGuidePdf).toHaveBeenCalledWith(42)
        })

        // The anchor must be in the live DOM at the moment .click() fires
        expect(anchorWasInDomAtClick).toBe(true)

        // Count only anchor appends/removes (React uses appendChild during mount too).
        const anchorAppends = appendSpy.mock.calls.filter(
          (args) => (args[0] as HTMLElement).tagName === 'A',
        )
        const anchorRemoves = removeSpy.mock.calls.filter(
          (args) => (args[0] as HTMLElement).tagName === 'A',
        )
        expect(anchorAppends).toHaveLength(1)
        expect(anchorRemoves).toHaveLength(1)
        // Anchor is gone after the download completes
        expect(document.body.querySelectorAll('a[download]').length).toBe(0)
      } finally {
        appendSpy.mockRestore()
        removeSpy.mockRestore()
        createElementSpy.mockRestore()
        ;(URL as { createObjectURL?: unknown }).createObjectURL = undefined
        ;(URL as { revokeObjectURL?: unknown }).revokeObjectURL = undefined
      }
    })
  })

  // ── AWD-M-83: bookmarkMutation onError — cache invalidation on failure ──
  describe('bookmarkMutation onError (AWD-M-83)', () => {
    it('invalidates parentGuide query when bookmark toggle fails', async () => {
      mockGetGuide.mockResolvedValue({ data: MOCK_GUIDE, error: undefined })
      mockToggleBookmark.mockRejectedValue(new Error('Network error'))

      const { queryClient } = renderPage()
      const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries')

      const bookmarkBtn = await screen.findByTitle('Bookmark this guide')
      await userEvent.click(bookmarkBtn)

      await waitFor(() => {
        expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['parentGuide'] })
      })
    })

    it('invalidates childGuides query when bookmark toggle fails', async () => {
      mockGetGuide.mockResolvedValue({ data: MOCK_GUIDE, error: undefined })
      mockToggleBookmark.mockRejectedValue(new Error('Network error'))

      const { queryClient } = renderPage()
      const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries')

      const bookmarkBtn = await screen.findByTitle('Bookmark this guide')
      await userEvent.click(bookmarkBtn)

      await waitFor(() => {
        expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['childGuides'] })
      })
    })
  })

  // ── AWD-M-130: invalidateBookmarkQueries shared callback ──────────────────
  // Verifies onSuccess also invalidates both cache keys through the extracted
  // shared callback — ensuring the deduplication is exercised end-to-end.
  describe('bookmarkMutation onSuccess (AWD-M-130)', () => {
    it('invalidates parentGuide query when bookmark toggle succeeds', async () => {
      mockGetGuide.mockResolvedValue({ data: MOCK_GUIDE, error: undefined })
      mockToggleBookmark.mockResolvedValue({ data: { ...MOCK_GUIDE, is_bookmarked: true }, error: undefined })

      const { queryClient } = renderPage()
      const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries')

      const bookmarkBtn = await screen.findByTitle('Bookmark this guide')
      await userEvent.click(bookmarkBtn)

      await waitFor(() => {
        expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['parentGuide'] })
      })
    })

    it('invalidates childGuides query when bookmark toggle succeeds', async () => {
      mockGetGuide.mockResolvedValue({ data: MOCK_GUIDE, error: undefined })
      mockToggleBookmark.mockResolvedValue({ data: { ...MOCK_GUIDE, is_bookmarked: true }, error: undefined })

      const { queryClient } = renderPage()
      const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries')

      const bookmarkBtn = await screen.findByTitle('Bookmark this guide')
      await userEvent.click(bookmarkBtn)

      await waitFor(() => {
        expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['childGuides'] })
      })
    })
  })
})
