import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { LearningProgressProvider, useLearningProgress } from '../../contexts/LearningProgressContext'
import ConceptExplorer, { TopicConcept } from './ConceptExplorer'

function DiscoveryCount() {
  return <span aria-label="Session discoveries">{useLearningProgress()?.discoveries.length}</span>
}

describe('concept exploration', () => {
  it('preserves shaded amount and number-line position when repartitioning', async () => {
    render(<ConceptExplorer conceptId="fractions" />)
    await userEvent.click(screen.getByRole('button', { name: 'Split every part in two' }))
    expect(screen.getByText('4/8 = 1/2 of one whole')).toBeInTheDocument()
    expect(screen.getByRole('img', { name: '4 of 8 equal parts shaded' }).firstElementChild).toHaveStyle({ width: '50%' })
    expect(screen.getByRole('button', { name: 'Split every part in two' })).toBeDisabled()
  })

  it('keeps the model and number line consistent across all supported fractions', () => {
    render(<ConceptExplorer conceptId="fractions" />)
    for (const denominator of [2, 3, 4, 6, 8, 12]) {
      fireEvent.change(screen.getByLabelText('Equal parts in one whole'), { target: { value: denominator } })
      for (let numerator = 0; numerator <= denominator; numerator++) {
        fireEvent.change(screen.getByRole('slider'), { target: { value: numerator } })
        const whole = screen.getByRole('img', { name: `${numerator} of ${denominator} equal parts shaded` })
        expect(whole.firstElementChild).toHaveStyle({ width: `${numerator / denominator * 100}%` })
        expect(whole.lastElementChild?.childElementCount).toBe(denominator)
        expect(screen.getByRole('img', { name: new RegExp(`^${numerator}/${denominator} is`) })).toBeInTheDocument()
      }
    }
  })

  it('explains an incorrect attempt and records a discovery only once', async () => {
    render(<LearningProgressProvider><DiscoveryCount /><ConceptExplorer conceptId="fractions" /></LearningProgressProvider>)
    const check = screen.getByRole('button', { name: 'Check my model' })
    await userEvent.click(check)
    expect(screen.getByRole('status')).toHaveTextContent('Choose six equal parts first')
    expect(screen.getByLabelText('Session discoveries')).toHaveTextContent('0')
    await userEvent.selectOptions(screen.getByLabelText('Equal parts in one whole'), '6')
    fireEvent.change(screen.getByRole('slider'), { target: { value: 3 } })
    await userEvent.click(check)
    await userEvent.click(check)
    expect(screen.getByLabelText('Session discoveries')).toHaveTextContent('1')
    expect(screen.getByText(/Discovery collected this visit/)).toBeInTheDocument()
  })

  it('exchanges ten ones without changing the number', async () => {
    render(<ConceptExplorer conceptId="place-value" />)
    fireEvent.change(screen.getByRole('slider'), { target: { value: 32 } })
    await userEvent.click(screen.getByRole('button', { name: 'Exchange one ten for ten ones' }))
    expect(screen.getByText('2 tens + 12 ones = 32')).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Check my model' }))
    expect(screen.getByRole('status')).toHaveTextContent('You found it')
    await userEvent.click(screen.getByRole('button', { name: 'Bundle ten ones into one ten' }))
    expect(screen.getByText('3 tens + 2 ones = 32')).toBeInTheDocument()
  })

  it('distinguishes rectangle area from perimeter', async () => {
    render(<ConceptExplorer conceptId="area-perimeter" />)
    expect(screen.getByText('Area: 12 square units · Perimeter: 14 units')).toBeInTheDocument()
    fireEvent.change(screen.getByLabelText('Width: 4 units'), { target: { value: 6 } })
    fireEvent.change(screen.getByLabelText('Height: 3 units'), { target: { value: 2 } })
    expect(screen.getByText('Area: 12 square units · Perimeter: 16 units')).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Check my model' }))
    expect(screen.getByRole('status')).toHaveTextContent('You found it')
  })

  it('requires a prediction followed by an actual circuit experiment', async () => {
    render(<ConceptExplorer conceptId="circuits" audience="educator" />)
    expect(screen.getByText(/^Ask your class:/)).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Close the switch' }))
    expect(screen.getByText('Closed path. The lamp is on.')).toBeInTheDocument()
    await userEvent.selectOptions(screen.getByLabelText('My prediction'), 'on')
    await userEvent.click(screen.getByRole('button', { name: 'Check my model' }))
    expect(screen.getByRole('status')).toHaveTextContent('Open the switch')
    await userEvent.click(screen.getByRole('button', { name: 'Open the switch' }))
    await userEvent.click(screen.getByRole('button', { name: 'Close the switch' }))
    await userEvent.click(screen.getByRole('button', { name: 'Check my model' }))
    expect(screen.getByRole('status')).toHaveTextContent('You found it')
  })

  it('provides physical alternatives and omits unsupported topics', async () => {
    const { rerender } = render(<TopicConcept topic="Fractions" subject="Mathematics" />)
    await userEvent.click(screen.getByText('Try it away from the screen'))
    expect(screen.getByText(/Fold a sheet of paper/)).toBeInTheDocument()
    rerender(<TopicConcept topic="Algebraic fractions" subject="Mathematics" />)
    expect(screen.queryByText('Explore the concept')).not.toBeInTheDocument()
  })
})
