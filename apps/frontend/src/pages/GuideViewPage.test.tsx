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
  },
}))

import apiService from '../services/api'
const mockGetGuide = vi.mocked(apiService.getGuide)
const mockGenerateGuide = vi.mocked(apiService.generateGuide)

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
    defaultOptions: { queries: { retry: false } },
  })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[url]}>
        <GuideViewPage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
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
})
