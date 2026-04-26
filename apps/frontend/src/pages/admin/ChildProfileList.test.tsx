import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ChildProfileList from './ChildProfileList'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const API_URL = 'http://localhost:8000'

beforeEach(() => {
    // Provide VITE_API_URL in import.meta.env shim used by the component
    vi.stubEnv('VITE_API_URL', API_URL)
})

const MOCK_CHILDREN = [
    {
        child_id: 1,
        parent_id: 42,
        name: 'Amara Okafor',
        age: 9,
        school_name: 'Lagos Primary',
        country_id: 1,
        curricula_id: 2,
        grade_level_id: 3,
        subjects: '[1, 2, 3]',
        created_at: '2026-01-10T08:00:00Z',
        updated_at: '2026-01-10T08:00:00Z',
    },
    {
        child_id: 2,
        parent_id: 99,
        name: 'Kofi Mensah',
        age: 11,
        school_name: null,
        country_id: 2,
        curricula_id: null,
        grade_level_id: null,
        subjects: null,
        created_at: '2026-02-14T08:00:00Z',
        updated_at: '2026-02-14T08:00:00Z',
    },
]

function mockFetchSuccess(data: unknown) {
    vi.stubGlobal(
        'fetch',
        vi.fn().mockResolvedValue({
            ok: true,
            json: async () => data,
        })
    )
}

function mockFetchError() {
    vi.stubGlobal(
        'fetch',
        vi.fn().mockRejectedValue(new Error('Network error'))
    )
}

function renderComponent() {
    return render(
        <MemoryRouter>
            <ChildProfileList />
        </MemoryRouter>
    )
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('ChildProfileList', () => {
    it('shows loading spinner while fetching', () => {
        vi.stubGlobal(
            'fetch',
            vi.fn().mockReturnValue(new Promise(() => { /* never resolves */ }))
        )
        renderComponent()
        expect(screen.getByRole('status', { name: /loading/i })).toBeInTheDocument()
    })

    it('renders child profiles on success', async () => {
        mockFetchSuccess(MOCK_CHILDREN)
        renderComponent()
        await waitFor(() => {
            expect(screen.getByText('Amara Okafor')).toBeInTheDocument()
            expect(screen.getByText('Kofi Mensah')).toBeInTheDocument()
        })
    })

    it('shows COPPA audit badge', async () => {
        mockFetchSuccess(MOCK_CHILDREN)
        renderComponent()
        await waitFor(() => {
            expect(screen.getByText(/coppa audited/i)).toBeInTheDocument()
        })
    })

    it('shows error state and retry button when fetch fails', async () => {
        mockFetchError()
        renderComponent()
        await waitFor(() => {
            expect(screen.getByRole('alert')).toBeInTheDocument()
            expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument()
        })
    })

    it('shows empty state when no children returned', async () => {
        mockFetchSuccess([])
        renderComponent()
        await waitFor(() => {
            expect(screen.getByText(/no child profiles found/i)).toBeInTheDocument()
        })
    })

    it('filters children by name search', async () => {
        mockFetchSuccess(MOCK_CHILDREN)
        renderComponent()
        await waitFor(() => expect(screen.getByText('Amara Okafor')).toBeInTheDocument())

        const searchInput = screen.getByRole('textbox', { name: /search/i })
        fireEvent.change(searchInput, { target: { value: 'Amara' } })

        expect(screen.getByText('Amara Okafor')).toBeInTheDocument()
        expect(screen.queryByText('Kofi Mensah')).not.toBeInTheDocument()
    })

    it('shows subject count badge for children with subjects', async () => {
        mockFetchSuccess(MOCK_CHILDREN)
        renderComponent()
        await waitFor(() => {
            expect(screen.getByText('3 subjects')).toBeInTheDocument()
        })
    })

    it('shows dash for children with no school or subjects', async () => {
        mockFetchSuccess([MOCK_CHILDREN[1]])
        renderComponent()
        await waitFor(() => {
            expect(screen.getByText('Kofi Mensah')).toBeInTheDocument()
        })
        // School name and subjects are null → em-dashes rendered
        const dashes = screen.getAllByText('—')
        expect(dashes.length).toBeGreaterThanOrEqual(2)
    })
})
