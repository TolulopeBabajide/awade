import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import LandingPage from './LandingPage'

vi.mock('../components/HeroSectionParent', () => ({ default: () => <h1>Learn together</h1> }))
vi.mock('../components/FeaturesSectionParent', () => ({ default: () => null }))
vi.mock('../components/HowItWorksSection', () => ({ default: () => null }))
vi.mock('../components/Footer', () => ({ default: () => null }))

describe('public concept preview', () => {
  it('offers a working fractions model without authentication or generation', () => {
    render(<MemoryRouter><LandingPage /></MemoryRouter>)
    expect(screen.getByText('Try this activity. No account needed.')).toBeInTheDocument()
    expect(screen.getByRole('slider')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Split every part in two' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Explore concepts' })).toHaveAttribute('href', '#explore-concepts')
  })
})
