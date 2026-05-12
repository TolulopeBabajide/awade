import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ModerationList from './ModerationList'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const API_URL = 'http://localhost:8000'

beforeEach(() => {
    vi.stubEnv('VITE_API_URL', API_URL)
    vi.restoreAllMocks()
})

const MOCK_RESOURCES = [
    {
        lesson_resources_id: 7,
        status: 'flagged',
        ai_generated_content: 'Sample lesson content for review.',
        created_at: '2026-04-01T09:00:00Z',
    },
]

function mockFetchResources(data: unknown = MOCK_RESOURCES) {
    vi.stubGlobal(
        'fetch',
        vi.fn().mockResolvedValue({
            ok: true,
            json: async () => data,
        })
    )
}

function renderComponent() {
    return render(
        <MemoryRouter>
            <ModerationList />
        </MemoryRouter>
    )
}

// ---------------------------------------------------------------------------
// Tests — AWD-M-143: mutation catch blocks surface errors to UI
// ---------------------------------------------------------------------------

describe('ModerationList (AWD-M-143)', () => {
    it('renders flagged resources after successful fetch', async () => {
        mockFetchResources()
        renderComponent()
        await waitFor(() => {
            expect(screen.getByText('Resource ID: 7')).toBeInTheDocument()
        })
    })

    it('shows error banner when handleModerate receives a non-OK response', async () => {
        vi.stubGlobal(
            'fetch',
            vi.fn()
                .mockResolvedValueOnce({ ok: true, json: async () => MOCK_RESOURCES }) // initial load
                .mockResolvedValueOnce({ ok: false, status: 403, json: async () => ({}) }) // PATCH fails
        )

        renderComponent()
        await waitFor(() => screen.getByText('Resource ID: 7'))

        fireEvent.click(screen.getByText('Approve'))

        await waitFor(() => {
            expect(screen.getByRole('alert')).toBeInTheDocument()
            expect(screen.getByRole('alert')).toHaveTextContent('HTTP 403')
        })
    })

    it('shows generic error message on network failure in handleModerate', async () => {
        vi.stubGlobal(
            'fetch',
            vi.fn()
                .mockResolvedValueOnce({ ok: true, json: async () => MOCK_RESOURCES })
                .mockRejectedValueOnce(new Error('Connection refused'))
        )

        renderComponent()
        await waitFor(() => screen.getByText('Resource ID: 7'))

        fireEvent.click(screen.getByText('Reject'))

        await waitFor(() => {
            expect(screen.getByRole('alert')).toHaveTextContent('Connection refused')
        })
    })

    it('dismiss button clears the moderation error banner', async () => {
        vi.stubGlobal(
            'fetch',
            vi.fn()
                .mockResolvedValueOnce({ ok: true, json: async () => MOCK_RESOURCES })
                .mockResolvedValueOnce({ ok: false, status: 500, json: async () => ({}) })
        )

        renderComponent()
        await waitFor(() => screen.getByText('Resource ID: 7'))

        fireEvent.click(screen.getByText('Approve'))
        await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument())

        fireEvent.click(screen.getByLabelText('Dismiss error'))

        expect(screen.queryByRole('alert')).not.toBeInTheDocument()
    })

    it('clears prior error at the start of a new moderation action', async () => {
        vi.stubGlobal(
            'fetch',
            vi.fn()
                .mockResolvedValueOnce({ ok: true, json: async () => MOCK_RESOURCES })
                .mockResolvedValueOnce({ ok: false, status: 503, json: async () => ({}) })
                .mockResolvedValueOnce({ ok: true, json: async () => MOCK_RESOURCES })
        )

        renderComponent()
        await waitFor(() => screen.getByText('Resource ID: 7'))

        // First action fails
        fireEvent.click(screen.getByText('Approve'))
        await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument())

        // Second action succeeds — error cleared
        fireEvent.click(screen.getByText('Approve'))
        await waitFor(() => expect(screen.queryByRole('alert')).not.toBeInTheDocument())
    })
})
