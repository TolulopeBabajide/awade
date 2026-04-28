/**
 * Tests for HowItWorksSection (AWD-M-07)
 *
 * Verifies that the section renders all three steps with:
 *  - Correct heading and subtitle
 *  - Step number badges (1, 2, 3)
 *  - Step titles
 *  - Phone mockup containers with descriptive aria-labels
 *  - The section landmark id for in-page anchor links
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import HowItWorksSection from './HowItWorksSection'

describe('HowItWorksSection', () => {
  it('renders the section heading', () => {
    render(<HowItWorksSection />)
    expect(screen.getByRole('heading', { name: /how it works/i })).toBeInTheDocument()
  })

  it('renders all three step number badges', () => {
    render(<HowItWorksSection />)
    expect(screen.getByText('1')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()
  })

  it('renders all three step titles', () => {
    render(<HowItWorksSection />)
    expect(screen.getByRole('heading', { name: /add your child/i })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /browse their topics/i })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /get your guide/i })).toBeInTheDocument()
  })

  it('renders phone mockup containers with descriptive aria-labels', () => {
    render(<HowItWorksSection />)
    expect(
      screen.getByRole('img', { name: /screenshot of the add child form/i })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('img', { name: /screenshot of the topics browser/i })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('img', { name: /screenshot of a how to help guide/i })
    ).toBeInTheDocument()
  })

  it('has a section id for anchor navigation', () => {
    const { container } = render(<HowItWorksSection />)
    expect(container.querySelector('#how-it-works')).toBeInTheDocument()
  })
})
