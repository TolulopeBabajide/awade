import { describe, expect, it } from 'vitest'
import { matchConcept, simplifyFraction } from './concepts'

describe('reviewed concept matching', () => {
  it.each([
    ['Fractions', 'Mathematics', 'fractions'],
    ['Equivalent fractions', 'General Mathematics', 'fractions'],
    ['Place value', 'Numeracy', 'place-value'],
    ['Perimeter and Area of Plane Shapes', 'Mathematics', 'area-perimeter'],
    ['Simple electric circuits', 'Basic Science', 'circuits'],
  ])('matches %s only to a supported foundation', (topic, subject, expected) => {
    expect(matchConcept(topic, subject)).toBe(expected)
  })
  it.each([
    ['Algebraic fractions', 'Mathematics'], ['Fractions', 'English'],
    ['Divisions of fractions', 'Mathematics'], ['Decimal place value', 'Mathematics'],
    ['Area of circles', 'Mathematics'], ['Short circuits and household wiring', 'Science'],
    ['Electricity', 'Basic Science'], ['', 'Mathematics'],
  ])('does not guess a model for %s', (topic, subject) => {
    expect(matchConcept(topic, subject)).toBeNull()
  })
})

describe('fraction equivalence', () => {
  it('keeps every supported equal split equivalent, including empty and whole models', () => {
    for (const denominator of [2, 3, 4, 6]) {
      for (let numerator = 0; numerator <= denominator; numerator++) {
        expect(simplifyFraction(numerator, denominator)).toBe(simplifyFraction(numerator * 2, denominator * 2))
      }
    }
    expect(simplifyFraction(0, 6)).toBe('0')
    expect(simplifyFraction(6, 6)).toBe('1')
  })
})
