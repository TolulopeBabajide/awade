/**
 * GuideViewPage — interaction tests (AWD-M-140)
 *
 * Covers: WhatsApp share (AWD-M-05), PDF download error banner (AWD-M-79 /
 * AWD-H-79), download-error dismiss button (AWD-L-33), anchor DOM lifecycle
 * (AWD-L-32), and bookmark mutation cache invalidation (AWD-M-83 / AWD-M-130).
 *
 * Render-state tests live in GuideViewPage.render.test.tsx.
 */

import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
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
const mockToggleBookmark = vi.mocked(apiService.toggleGuideBookmark)
const mockExportGuidePdf = vi.mocked(apiService.exportGuidePdf)

// ── Tests ─────────────────────────────────────────────────────────────────

describe('GuideViewPage — interactions', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  // ── WhatsApp share (AWD-M-05) ───────────────────────────────────────────
  it('renders the WhatsApp share button', async () => {
    mockGetGuide.mockResolvedValue({ data: MOCK_GUIDE, error: undefined })
    renderPage()
    await waitFor(() => {
      expect(screen.getByLabelText('Share this guide on WhatsApp')).toBeInTheDocument()
    }, { timeout: 5000 })
  })

  it('opens the correct WhatsApp share URL when the button is clicked', async () => {
    const openSpy = vi.spyOn(window, 'open').mockReturnValue(null)
    mockGetGuide.mockResolvedValue({ data: MOCK_GUIDE, error: undefined })
    renderPage()

    const shareBtn = await screen.findByLabelText('Share this guide on WhatsApp', undefined, { timeout: 5000 })
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
    mockGetGuide.mockReturnValue(new Promise(() => {}))
    renderPage()
    expect(openSpy).not.toHaveBeenCalled()
    openSpy.mockRestore()
  })

  // ── AWD-M-79 + AWD-H-79: handleDownloadPdf error paths ──────────────────
  describe('handleDownloadPdf error banner (AWD-M-79)', () => {
    it('shows inline error banner when exportGuidePdf returns an API error', async () => {
      mockGetGuide.mockResolvedValue({ data: MOCK_GUIDE, error: undefined })
      mockExportGuidePdf.mockResolvedValue({ error: 'PDF generation failed' })

      renderPage()
      const downloadBtn = await screen.findByLabelText('Download this guide as a PDF', undefined, { timeout: 5000 })
      await userEvent.click(downloadBtn)

      await waitFor(() => {
        expect(screen.getByRole('alert')).toHaveTextContent(
          'Could not download PDF: PDF generation failed',
        )
      }, { timeout: 5000 })
    })

    it('shows inline error banner when exportGuidePdf throws unexpectedly', async () => {
      mockGetGuide.mockResolvedValue({ data: MOCK_GUIDE, error: undefined })
      mockExportGuidePdf.mockRejectedValue(new Error('Network abort'))

      renderPage()
      const downloadBtn = await screen.findByLabelText('Download this guide as a PDF', undefined, { timeout: 5000 })
      await userEvent.click(downloadBtn)

      await waitFor(() => {
        expect(screen.getByRole('alert')).toHaveTextContent(
          'Could not download PDF: Network abort',
        )
      }, { timeout: 5000 })
    })

    it('clears the error banner on a subsequent download attempt', async () => {
      mockGetGuide.mockResolvedValue({ data: MOCK_GUIDE, error: undefined })
      mockExportGuidePdf
        .mockRejectedValueOnce(new Error('Timeout'))
        .mockResolvedValueOnce({ blob: new Blob(), filename: 'guide.pdf' })

      URL.createObjectURL = vi.fn().mockReturnValue('blob:mock')
      URL.revokeObjectURL = vi.fn()

      renderPage()
      const downloadBtn = await screen.findByLabelText('Download this guide as a PDF', undefined, { timeout: 5000 })

      await userEvent.click(downloadBtn)
      await waitFor(() => {
        expect(screen.getByRole('alert')).toHaveTextContent('Could not download PDF')
      }, { timeout: 5000 })

      await userEvent.click(downloadBtn)
      await waitFor(() => {
        expect(screen.queryByRole('alert')).not.toBeInTheDocument()
      }, { timeout: 5000 })

      ;(URL as { createObjectURL?: unknown }).createObjectURL = undefined
      ;(URL as { revokeObjectURL?: unknown }).revokeObjectURL = undefined
    })

    it('re-enables the download button after an unexpected throw', async () => {
      mockGetGuide.mockResolvedValue({ data: MOCK_GUIDE, error: undefined })
      mockExportGuidePdf.mockRejectedValue(new Error('Timeout'))

      renderPage()
      const downloadBtn = await screen.findByLabelText('Download this guide as a PDF', undefined, { timeout: 5000 })
      await userEvent.click(downloadBtn)

      await waitFor(() => {
        expect(downloadBtn).not.toBeDisabled()
      }, { timeout: 5000 })
    })
  })

  // ── AWD-L-33: downloadError dismiss button ──────────────────────────────
  describe('downloadError dismiss button (AWD-L-33)', () => {
    it('renders a dismiss button inside the error banner', async () => {
      mockGetGuide.mockResolvedValue({ data: MOCK_GUIDE, error: undefined })
      mockExportGuidePdf.mockResolvedValue({ error: 'PDF generation failed' })

      renderPage()
      const downloadBtn = await screen.findByLabelText('Download this guide as a PDF', undefined, { timeout: 5000 })
      await userEvent.click(downloadBtn)

      await waitFor(() => {
        expect(screen.getByRole('alert')).toBeInTheDocument()
      }, { timeout: 5000 })
      expect(screen.getByLabelText('Dismiss error')).toBeInTheDocument()
    })

    it('clears the error banner when the dismiss button is clicked', async () => {
      mockGetGuide.mockResolvedValue({ data: MOCK_GUIDE, error: undefined })
      mockExportGuidePdf.mockResolvedValue({ error: 'PDF generation failed' })

      renderPage()
      const downloadBtn = await screen.findByLabelText('Download this guide as a PDF', undefined, { timeout: 5000 })
      await userEvent.click(downloadBtn)

      await waitFor(() => {
        expect(screen.getByRole('alert')).toBeInTheDocument()
      }, { timeout: 5000 })

      const dismissBtn = screen.getByLabelText('Dismiss error')
      await userEvent.click(dismissBtn)

      await waitFor(() => {
        expect(screen.queryByRole('alert')).not.toBeInTheDocument()
      }, { timeout: 5000 })
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

      URL.createObjectURL = vi.fn().mockReturnValue('blob:mock')
      URL.revokeObjectURL = vi.fn()

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
        const downloadBtn = await screen.findByLabelText('Download this guide as a PDF', undefined, { timeout: 5000 })
        await userEvent.click(downloadBtn)

        await waitFor(() => {
          expect(mockExportGuidePdf).toHaveBeenCalledWith(42)
        }, { timeout: 5000 })

        expect(anchorWasInDomAtClick).toBe(true)

        const anchorAppends = appendSpy.mock.calls.filter(
          (args) => (args[0] as HTMLElement).tagName === 'A',
        )
        const anchorRemoves = removeSpy.mock.calls.filter(
          (args) => (args[0] as HTMLElement).tagName === 'A',
        )
        expect(anchorAppends).toHaveLength(1)
        expect(anchorRemoves).toHaveLength(1)
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
    it.each<[string]>([['parentGuide'], ['childGuides']])(
      'invalidates %s query when bookmark toggle fails',
      async (queryKey) => {
        mockGetGuide.mockResolvedValue({ data: MOCK_GUIDE, error: undefined })
        mockToggleBookmark.mockRejectedValue(new Error('Network error'))

        const { queryClient } = renderPage()
        const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries')

        const bookmarkBtn = await screen.findByTitle('Bookmark this guide', undefined, { timeout: 5000 })
        await userEvent.click(bookmarkBtn)

        await waitFor(() => {
          expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: [queryKey] })
        }, { timeout: 5000 })
      }
    )
  })

  // ── AWD-M-130: invalidateBookmarkQueries shared callback ──────────────────
  describe('bookmarkMutation onSuccess (AWD-M-130)', () => {
    it.each<[string]>([['parentGuide'], ['childGuides']])(
      'invalidates %s query when bookmark toggle succeeds',
      async (queryKey) => {
        mockGetGuide.mockResolvedValue({ data: MOCK_GUIDE, error: undefined })
        mockToggleBookmark.mockResolvedValue({ data: { ...MOCK_GUIDE, is_bookmarked: true }, error: undefined })

        const { queryClient } = renderPage()
        const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries')

        const bookmarkBtn = await screen.findByTitle('Bookmark this guide', undefined, { timeout: 5000 })
        await userEvent.click(bookmarkBtn)

        await waitFor(() => {
          expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: [queryKey] })
        }, { timeout: 5000 })
      }
    )
  })
})
