import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import ExplorePage from './ExplorePage'
import { LearningSession } from '../contexts/LearningProgressContext'

const auth = vi.hoisted(() => ({ user: { user_id: 1, role: 'PARENT' } }))
vi.mock('../contexts/AuthContext', () => ({ useAuth: () => ({ user: auth.user, logout: vi.fn() }) }))

function setup(url = '/explore') {
  return render(<MemoryRouter initialEntries={[url]}><LearningSession><ExplorePage /></LearningSession></MemoryRouter>)
}

describe('Explore page', () => {
  it('deep-links to concepts and safely falls back for an invalid selection', async () => {
    setup('/explore?concept=unknown')
    expect(screen.getByRole('heading', { name: 'Parts of a whole' })).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: /Inside and around/ }))
    expect(await screen.findByText('Area: 12 square units · Perimeter: 14 units')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Inside and around/ })).toHaveAttribute('aria-pressed', 'true')
  })

  it('keeps discoveries across navigation but clears them for a different account', async () => {
    auth.user = { user_id: 1, role: 'PARENT' }
    const { rerender } = setup()
    await userEvent.selectOptions(screen.getByLabelText('Equal parts in one whole'), '6')
    fireEvent.change(screen.getByRole('slider'), { target: { value: 3 } })
    await userEvent.click(screen.getByRole('button', { name: 'Check my model' }))
    expect(screen.getByText('1 discovery this visit')).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: /Build a number/ }))
    expect(await screen.findByRole('heading', { name: 'Build a number' })).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: /Parts of a whole/ }))
    expect(await screen.findByText(/Discovery collected this visit/)).toBeInTheDocument()
    auth.user = { user_id: 2, role: 'EDUCATOR' }
    rerender(<MemoryRouter><LearningSession><ExplorePage /></LearningSession></MemoryRouter>)
    expect(screen.getByText('0 discoveries this visit')).toBeInTheDocument()
    expect(screen.getByText(/^Ask your class:/)).toBeInTheDocument()
  })
})
