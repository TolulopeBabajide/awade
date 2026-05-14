/**
 * Tests for GuideViewPage.components.tsx (AWD-M-132)
 * Covers the Section and InfoCard presentational sub-components extracted
 * from GuideViewPage.tsx.
 */
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { Section, InfoCard } from './GuideViewPage.components'

// ── Section ────────────────────────────────────────────────────────────────

describe('Section (AWD-M-132)', () => {
  it('renders the icon, title, and children', () => {
    render(
      <Section icon={<span data-testid="icon">★</span>} title="What is this topic?">
        <p>Child content</p>
      </Section>,
    )

    expect(screen.getByTestId('icon')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'What is this topic?' })).toBeInTheDocument()
    expect(screen.getByText('Child content')).toBeInTheDocument()
  })

  it('renders optional subtitle when provided', () => {
    render(
      <Section icon={<span />} title="Activity" subtitle="15-30 min">
        <p />
      </Section>,
    )

    expect(screen.getByText('15-30 min')).toBeInTheDocument()
  })

  it('omits subtitle element when not provided', () => {
    render(
      <Section icon={<span />} title="Simple Section">
        <p />
      </Section>,
    )

    // Subtitle paragraph should not be present in the DOM
    expect(screen.queryByText(/min/i)).not.toBeInTheDocument()
  })
})

// ── InfoCard ───────────────────────────────────────────────────────────────

describe('InfoCard (AWD-M-132)', () => {
  it('renders the label and value', () => {
    render(<InfoCard label="Before this topic" value="Division" />)

    expect(screen.getByText('Before this topic')).toBeInTheDocument()
    expect(screen.getByText('Division')).toBeInTheDocument()
  })

  it('renders different label and value without mixing them', () => {
    render(<InfoCard label="Time in school" value="3 weeks" />)

    expect(screen.getByText('Time in school')).toBeInTheDocument()
    expect(screen.getByText('3 weeks')).toBeInTheDocument()
  })
})
