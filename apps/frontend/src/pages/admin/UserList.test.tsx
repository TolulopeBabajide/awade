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
        // Initial load succeeds; role-change PATCH fails with 403
        vi.stubGlobal(
            'fetch',
            vi.fn()
                .mockResolvedValueOnce({ ok: true, json: async () => MOCK_USERS })    // fetchUsers on mount
                .mockResolvedValueOnce({ ok: false, status: 403, json: async () => ({}) }) // PATCH fails
        )
        vi.stubGlobal('confirm', vi.fn().mockReturnValue(true))

        renderComponent()
        await waitFor(() => screen.getByText('Ada Okonkwo'))

        // Click the role-cycle button (FiMoreVertical)
        fireEvent.click(screen.getByTitle('Manage Role'))

        await waitFor(() => {
            expect(screen.getByRole('alert')).toBeInTheDocument()
            expect(screen.getByRole('alert')).toHaveTextContent('HTTP 403')
        })
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
