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
// Tests — AWD-L-37: fetchResources load errors surfaced to UI
// ---------------------------------------------------------------------------

describe('ModerationList fetchResources error handling (AWD-L-37)', () => {
    it('shows load error banner when initial fetch returns a non-OK response', async () => {
        vi.stubGlobal(
            'fetch',
            vi.fn().mockResolvedValue({
                ok: false,
                status: 500,
                json: async () => ({ detail: 'Internal Server Error' }),
            })
        )

        renderComponent()

        await waitFor(() => {
            expect(screen.getByRole('alert')).toBeInTheDocument()
            expect(screen.getByRole('alert')).toHaveTextContent('HTTP 500')
        }, { timeout: 5000 })
    })

    it('shows load error banner on network failure during initial fetch', async () => {
        vi.stubGlobal(
            'fetch',
            vi.fn().mockRejectedValue(new Error('Network error'))
        )

        renderComponent()

        await waitFor(() => {
            expect(screen.getByRole('alert')).toBeInTheDocument()
            expect(screen.getByRole('alert')).toHaveTextContent('Network error')
        }, { timeout: 5000 })
    })

    it('dismiss load error button clears the load error banner', async () => {
        vi.stubGlobal(
            'fetch',
            vi.fn().mockResolvedValue({
                ok: false,
                status: 503,
                json: async () => ({}),
            })
        )

        renderComponent()
        await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument(), { timeout: 5000 })

        fireEvent.click(screen.getByLabelText('Dismiss load error'))

        expect(screen.queryByRole('alert')).not.toBeInTheDocument()
    })

    it('does not call setResources with error body when response is non-OK', async () => {
        vi.stubGlobal(
            'fetch',
            vi.fn().mockResolvedValue({
                ok: false,
                status: 403,
                json: async () => ({ detail: 'Forbidden' }),
            })
        )

        renderComponent()

        await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument(), { timeout: 5000 })

        // No resource cards should render — error body was not set as resources
        expect(screen.queryByText(/Resource ID:/)).not.toBeInTheDocument()
    })

    it('shows HTTP status error when server returns non-JSON body on error (AWD-M-147)', async () => {
        // Simulates a gateway returning an HTML error page (non-JSON body).
        // Before the fix, response.json() was called first and would throw a
        // SyntaxError; after the fix, !response.ok is checked first so json()
        // is never called and the user sees "HTTP 502" instead of a parse error.
        vi.stubGlobal(
            'fetch',
            vi.fn().mockResolvedValue({
                ok: false,
                status: 502,
                json: async () => { throw new SyntaxError('Unexpected token < in JSON at position 0') },
            })
        )

        renderComponent()

        await waitFor(() => {
            expect(screen.getByRole('alert')).toBeInTheDocument()
            expect(screen.getByRole('alert')).toHaveTextContent('HTTP 502')
        }, { timeout: 5000 })
    })
})

// ---------------------------------------------------------------------------
// Tests — AWD-M-143: mutation catch blocks surface errors to UI
// ---------------------------------------------------------------------------

describe('ModerationList (AWD-M-143)', () => {
    it('renders flagged resources after successful fetch', async () => {
        mockFetchResources()
        renderComponent()
        await waitFor(() => {
            expect(screen.getByText('Resource ID: 7')).toBeInTheDocument()
        }, { timeout: 5000 })
    })

    it('shows error banner when handleModerate receives a non-OK response', async () => {
        vi.stubGlobal(
            'fetch',
            vi.fn()
                .mockResolvedValueOnce({ ok: true, json: async () => MOCK_RESOURCES }) // initial load
                .mockResolvedValueOnce({ ok: false, status: 403, json: async () => ({}) }) // PATCH fails
        )

        renderComponent()
        await waitFor(() => screen.getByText('Resource ID: 7'), { timeout: 5000 })

        fireEvent.click(screen.getByText('Approve'))

        await waitFor(() => {
            expect(screen.getByRole('alert')).toBeInTheDocument()
            expect(screen.getByRole('alert')).toHaveTextContent('HTTP 403')
        }, { timeout: 5000 })
    })

    it('shows generic error message on network failure in handleModerate', async () => {
        vi.stubGlobal(
            'fetch',
            vi.fn()
                .mockResolvedValueOnce({ ok: true, json: async () => MOCK_RESOURCES })
                .mockRejectedValueOnce(new Error('Connection refused'))
        )

        renderComponent()
        await waitFor(() => screen.getByText('Resource ID: 7'), { timeout: 5000 })

        fireEvent.click(screen.getByText('Reject'))

        await waitFor(() => {
            expect(screen.getByRole('alert')).toHaveTextContent('Connection refused')
        }, { timeout: 5000 })
    })

    it('dismiss button clears the moderation error banner', async () => {
        vi.stubGlobal(
            'fetch',
            vi.fn()
                .mockResolvedValueOnce({ ok: true, json: async () => MOCK_RESOURCES })
                .mockResolvedValueOnce({ ok: false, status: 500, json: async () => ({}) })
        )

        renderComponent()
        await waitFor(() => screen.getByText('Resource ID: 7'), { timeout: 5000 })

        fireEvent.click(screen.getByText('Approve'))
        await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument(), { timeout: 5000 })

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
        await waitFor(() => screen.getByText('Resource ID: 7'), { timeout: 5000 })

        // First action fails
        fireEvent.click(screen.getByText('Approve'))
        await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument(), { timeout: 5000 })

        // Second action succeeds — error cleared
        fireEvent.click(screen.getByText('Approve'))
        await waitFor(() => expect(screen.queryByRole('alert')).not.toBeInTheDocument(), { timeout: 5000 })
    })
})

// ---------------------------------------------------------------------------
// Tests — AWD-M-145: ContentPreviewModal replaces alert()
// ---------------------------------------------------------------------------

describe('ContentPreviewModal (AWD-M-145)', () => {
    it('does NOT call window.alert when View is clicked', async () => {
        mockFetchResources()
        const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {})

        renderComponent()
        await waitFor(() => screen.getByText('Resource ID: 7'), { timeout: 5000 })

        fireEvent.click(screen.getByText('View'))

        expect(alertSpy).not.toHaveBeenCalled()
    })

    it('opens the ContentPreviewModal with role="dialog" when View is clicked', async () => {
        mockFetchResources()
        renderComponent()
        await waitFor(() => screen.getByText('Resource ID: 7'), { timeout: 5000 })

        expect(screen.queryByRole('dialog')).not.toBeInTheDocument()

        fireEvent.click(screen.getByText('View'))

        expect(screen.getByRole('dialog')).toBeInTheDocument()
        expect(screen.getByRole('dialog')).toHaveAttribute('aria-modal', 'true')
    })

    it('displays the resource ai_generated_content inside the modal', async () => {
        mockFetchResources()
        renderComponent()
        await waitFor(() => screen.getByText('Resource ID: 7'), { timeout: 5000 })

        fireEvent.click(screen.getByText('View'))

        expect(screen.getByRole('dialog')).toHaveTextContent('Sample lesson content for review.')
    })

    it('shows "AI-Generated Content Preview" heading in the modal', async () => {
        mockFetchResources()
        renderComponent()
        await waitFor(() => screen.getByText('Resource ID: 7'), { timeout: 5000 })

        fireEvent.click(screen.getByText('View'))

        expect(screen.getByText('AI-Generated Content Preview')).toBeInTheDocument()
    })

    it('Close button dismisses the modal', async () => {
        mockFetchResources()
        renderComponent()
        await waitFor(() => screen.getByText('Resource ID: 7'), { timeout: 5000 })

        fireEvent.click(screen.getByText('View'))
        await waitFor(() => expect(screen.getByRole('dialog')).toBeInTheDocument(), { timeout: 5000 })

        fireEvent.click(screen.getByRole('button', { name: 'Close' }))

        expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })
})
