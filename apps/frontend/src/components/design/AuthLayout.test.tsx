import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import AuthLayout from './AuthLayout'

describe('account screen layout', () => {
  it('preserves its form while the equal-parts demonstration changes', async () => {
    render(<MemoryRouter><AuthLayout mode="signup"><label>Name<input defaultValue="Test Learner" /></label></AuthLayout></MemoryRouter>)
    await userEvent.click(screen.getByRole('button', { name: 'Split the parts' }))
    expect(screen.getByRole('img')).toHaveAccessibleName('4 of 8 equal parts shaded; one half of the same whole')
    expect(screen.getByLabelText('Name')).toHaveValue('Test Learner')
    expect(screen.getByRole('link', { name: 'Sign in' })).toHaveAttribute('href', '/login')
  })
})
