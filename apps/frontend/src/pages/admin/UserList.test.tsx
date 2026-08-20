import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import UserList from './UserList'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const API_URL = 'http://localhost:8000'

beforeEach(() => {
    vi.stubEnv('VITE_API_URL', API_URL)
    vi.restoreAllMocks()
})

const MOCK_USERS = [
    {
        user_id: 1,
        full_name: 'Ada Okonkwo',
        email: 'ada@example.com',
        role: 'EDUCATOR',
        is_suspended: 0,
        created_at: '2026-01-10T08:00:00Z',
        last_login: '2026-05-01T08:00:00Z',
    },
]

function mockFetchUsers(data: unknown = MOCK_USERS) {
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
            <UserList />
        </MemoryRouter>
    )
}

// ---------------------------------------------------------------------------
// Tests — AWD-H-86 + AWD-H-87: fetchUsers response-ok guard and loadError state
// ---------------------------------------------------------------------------

describe('UserList fetchUsers (AWD-H-86 + AWD-H-87)', () => {
    it('surfaces an HTTP status error when the server returns a non-OK non-JSON body', async () => {
        // Simulates a 502 gateway response with an HTML body — response.json() must
        // NOT be called first, otherwise we get a confusing SyntaxError (AWD-H-86).
        vi.stubGlobal(
            'fetch',
            vi.fn().mockResolvedValue({
                ok: false,
                status: 502,
                json: async () => { throw new SyntaxError('Unexpected token < in JSON'); },
            })
        )

        renderComponent()

        await waitFor(() => {
            expect(screen.getByRole('alert')).toBeInTheDocument()
        })
        // Error must say "HTTP 502", not a SyntaxError from the JSON parser.
        expect(screen.getByRole('alert')).toHaveTextContent('HTTP 502')
    })

    it('shows a loadError banner when the users API call fails (AWD-H-87)', async () => {
        vi.stubGlobal(
            'fetch',
            vi.fn().mockRejectedValue(new Error('Network failure'))
        )

        renderComponent()

        await waitFor(() => {
            expect(screen.getByRole('alert')).toBeInTheDocument()
        })
        expect(screen.getByRole('alert')).toHaveTextContent('Network failure')
    })

    it('clears the loadError banner when the dismiss button is clicked', async () => {
        vi.stubGlobal(
            'fetch',
            vi.fn().mockResolvedValue({
                ok: false,
                status: 503,
                json: async () => ({}),
            })
        )

        renderComponent()

        await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument())

        fireEvent.click(screen.getByLabelText('Dismiss error'))

        expect(screen.queryByRole('alert')).not.toBeInTheDocument()
    })
})

// ---------------------------------------------------------------------------
// Tests — AWD-M-143: mutation catch blocks surface errors to UI
// ---------------------------------------------------------------------------

describe('UserList (AWD-M-143)', () => {
    it('renders user list after successful fetch', async () => {
        mockFetchUsers()
        renderComponent()
        await waitFor(() => {
            expect(screen.getByText('Ada Okonkwo')).toBeInTheDocument()
        })
    })

    it('shows error banner when handleRoleChange receives a non-OK response', async () => {
        // Initial load succeeds; role-change PATCH fails with 403.
        // AWD-M-144: role change now goes through ConfirmRoleChangeModal —
        // click "Manage Role" to open the modal, then click "Confirm".
        vi.stubGlobal(
            'fetch',
            vi.fn()
                .mockResolvedValueOnce({ ok: true, json: async () => MOCK_USERS })    // fetchUsers on mount
                .mockResolvedValueOnce({ ok: false, status: 403, json: async () => ({}) }) // PATCH fails
        )

        renderComponent()
        await waitFor(() => screen.getByText('Ada Okonkwo'), { timeout: 5000 })

        // Open the modal
        fireEvent.click(screen.getByTitle('Manage Role'))
        await waitFor(() => screen.getByRole('dialog'), { timeout: 5000 })

        // Confirm the role change through the modal
        fireEvent.click(screen.getByRole('button', { name: 'Confirm' }))

        await waitFor(() => {
            expect(screen.getByRole('alert')).toBeInTheDocument()
            expect(screen.getByRole('alert')).toHaveTextContent('HTTP 403')
        }, { timeout: 5000 })
    })

    it('shows error banner when handleToggleSuspension receives a non-OK response', async () => {
        vi.stubGlobal(
            'fetch',
            vi.fn()
                .mockResolvedValueOnce({ ok: true, json: async () => MOCK_USERS })
                .mockResolvedValueOnce({ ok: false, status: 422, json: async () => ({}) })
        )

        renderComponent()
        await waitFor(() => screen.getByText('Ada Okonkwo'))

        fireEvent.click(screen.getByText('Suspend'))

        await waitFor(() => {
            expect(screen.getByRole('alert')).toBeInTheDocument()
            expect(screen.getByRole('alert')).toHaveTextContent('HTTP 422')
        })
    })

    it('shows generic error message on network failure in handleToggleSuspension', async () => {
        vi.stubGlobal(
            'fetch',
            vi.fn()
                .mockResolvedValueOnce({ ok: true, json: async () => MOCK_USERS })
                .mockRejectedValueOnce(new Error('Network error'))
        )

        renderComponent()
        await waitFor(() => screen.getByText('Ada Okonkwo'))

        fireEvent.click(screen.getByText('Suspend'))

        await waitFor(() => {
            expect(screen.getByRole('alert')).toHaveTextContent('Network error')
        })
    })

    it('dismiss button clears the error banner', async () => {
        vi.stubGlobal(
            'fetch',
            vi.fn()
                .mockResolvedValueOnce({ ok: true, json: async () => MOCK_USERS })
                .mockResolvedValueOnce({ ok: false, status: 500, json: async () => ({}) })
        )

        renderComponent()
        await waitFor(() => screen.getByText('Ada Okonkwo'))

        fireEvent.click(screen.getByText('Suspend'))

        await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument())

        fireEvent.click(screen.getByLabelText('Dismiss error'))

        expect(screen.queryByRole('alert')).not.toBeInTheDocument()
    })

    it('clears a prior error when a subsequent action starts', async () => {
        vi.stubGlobal(
            'fetch',
            vi.fn()
                .mockResolvedValueOnce({ ok: true, json: async () => MOCK_USERS })    // initial load
                .mockResolvedValueOnce({ ok: false, status: 503, json: async () => ({}) }) // first action fails
                .mockResolvedValueOnce({ ok: true, json: async () => MOCK_USERS })    // second action succeeds → fetchUsers
        )

        renderComponent()
        await waitFor(() => screen.getByText('Ada Okonkwo'))

        // First action fails — error banner appears
        fireEvent.click(screen.getByText('Suspend'))
        await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument())

        // Second action succeeds — error banner is cleared before the request
        fireEvent.click(screen.getByText('Suspend'))
        await waitFor(() => expect(screen.queryByRole('alert')).not.toBeInTheDocument())
    })
})

// ---------------------------------------------------------------------------
// Tests — AWD-M-144: ConfirmRoleChangeModal replaces window.confirm()
// ---------------------------------------------------------------------------

describe('UserList role-change modal (AWD-M-144)', () => {
    it('opens ConfirmRoleChangeModal when Manage Role is clicked', async () => {
        mockFetchUsers()
        renderComponent()
        await waitFor(() => screen.getByText('Ada Okonkwo'))

        fireEvent.click(screen.getByTitle('Manage Role'))

        await waitFor(() => {
            expect(screen.getByRole('dialog')).toBeInTheDocument()
        })
        // Modal title mentions the next role (EDUCATOR → ADMIN)
        expect(screen.getByRole('dialog')).toHaveTextContent('ADMIN')
        // Modal body mentions the user name
        expect(screen.getByRole('dialog')).toHaveTextContent('Ada Okonkwo')
    })

    it('closes the modal without calling the API when Cancel is clicked', async () => {
        const fetchMock = vi.fn()
            .mockResolvedValueOnce({ ok: true, json: async () => MOCK_USERS }) // initial load
        vi.stubGlobal('fetch', fetchMock)

        renderComponent()
        await waitFor(() => screen.getByText('Ada Okonkwo'))

        fireEvent.click(screen.getByTitle('Manage Role'))
        await waitFor(() => screen.getByRole('dialog'))

        fireEvent.click(screen.getByRole('button', { name: 'Cancel' }))

        // Modal gone, no second fetch call
        expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
        expect(fetchMock).toHaveBeenCalledTimes(1)
    })

    it('calls the role-change API and closes the modal when Confirm is clicked', async () => {
        vi.stubGlobal(
            'fetch',
            vi.fn()
                .mockResolvedValueOnce({ ok: true, json: async () => MOCK_USERS }) // mount
                .mockResolvedValueOnce({ ok: true, json: async () => ({}) })       // PATCH
                .mockResolvedValueOnce({ ok: true, json: async () => MOCK_USERS }) // refetch
        )

        renderComponent()
        await waitFor(() => screen.getByText('Ada Okonkwo'), { timeout: 5000 })

        fireEvent.click(screen.getByTitle('Manage Role'))
        await waitFor(() => screen.getByRole('dialog'), { timeout: 5000 })

        fireEvent.click(screen.getByRole('button', { name: 'Confirm' }))

        await waitFor(() => {
            expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
        }, { timeout: 5000 })
        // PATCH was called with the correct user ID
        expect(vi.mocked(globalThis.fetch)).toHaveBeenCalledWith(
            expect.stringContaining('/api/admin/users/1'),
            expect.objectContaining({ method: 'PATCH' })
        )
    })

    it('shows an error banner (not dialog) when the role-change API fails after Confirm', async () => {
        vi.stubGlobal(
            'fetch',
            vi.fn()
                .mockResolvedValueOnce({ ok: true, json: async () => MOCK_USERS })
                .mockResolvedValueOnce({ ok: false, status: 500, json: async () => ({}) })
        )

        renderComponent()
        await waitFor(() => screen.getByText('Ada Okonkwo'), { timeout: 5000 })

        fireEvent.click(screen.getByTitle('Manage Role'))
        await waitFor(() => screen.getByRole('dialog'), { timeout: 5000 })

        fireEvent.click(screen.getByRole('button', { name: 'Confirm' }))

        await waitFor(() => {
            expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
            expect(screen.getByRole('alert')).toHaveTextContent('HTTP 500')
        }, { timeout: 5000 })
    })

    it('does not call window.confirm at all during a role change', async () => {
        vi.stubGlobal(
            'fetch',
            vi.fn()
                .mockResolvedValueOnce({ ok: true, json: async () => MOCK_USERS })
                .mockResolvedValueOnce({ ok: true, json: async () => ({}) })
                .mockResolvedValueOnce({ ok: true, json: async () => MOCK_USERS })
        )
        const confirmSpy = vi.spyOn(window, 'confirm')

        renderComponent()
        await waitFor(() => screen.getByText('Ada Okonkwo'))

        fireEvent.click(screen.getByTitle('Manage Role'))
        await waitFor(() => screen.getByRole('dialog'))
        fireEvent.click(screen.getByRole('button', { name: 'Confirm' }))
        await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())

        expect(confirmSpy).not.toHaveBeenCalled()
    })
})
