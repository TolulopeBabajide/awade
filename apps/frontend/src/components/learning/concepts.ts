export type ConceptId = 'fractions' | 'place-value' | 'area-perimeter' | 'circuits'

export interface Concept {
  id: ConceptId
  title: string
  subject: string
  description: string
  question: string
  physicalAlternative: string
}

export const concepts: Concept[] = [
  { id: 'fractions', title: 'Parts of a whole', subject: 'Mathematics',
    description: 'Shade equal parts and discover why different fractions can mean the same amount.',
    question: 'What changes when you split every part in two?',
    physicalAlternative: 'Fold a sheet of paper into four equal parts. Shade two, then fold each part in half again. Compare the shaded amount.' },
  { id: 'place-value', title: 'Build a number', subject: 'Mathematics',
    description: 'Exchange ten units for one ten and see why the total stays the same.',
    question: 'Can you regroup a number without changing its value?',
    physicalAlternative: 'Use small sticks or counters. Bundle ten together, and compare one bundle with ten loose counters.' },
  { id: 'area-perimeter', title: 'Inside and around', subject: 'Mathematics',
    description: 'Resize a rectangle to compare its area with the distance around its edge.',
    question: 'Can two rectangles have the same area but different perimeters?',
    physicalAlternative: 'Draw rectangles on squared paper. Count the squares inside and the unit lengths around each edge.' },
  { id: 'circuits', title: 'Complete the circuit', subject: 'Basic science',
    description: 'Open and close a simple circuit to see why a lamp needs a complete path.',
    question: 'What happens to the lamp when there is a gap in the path?',
    physicalAlternative: 'Draw a battery, lamp and connecting wires on paper. Trace a complete loop with your finger, then erase a short section of wire.' },
]

export function getConcept(id: string | null | undefined): Concept | undefined {
  return concepts.find(concept => concept.id === id)
}

/** Only explicitly supported topics match. Generated prose never selects executable code. */
export function matchConcept(topic: string, subject: string): ConceptId | null {
  if (typeof topic !== 'string' || typeof subject !== 'string') return null
  const title = topic.toLowerCase().replace(/[–—-]/g, ' ').replace(/[^a-z0-9 ]/g, '').replace(/\s+/g, ' ').trim()
  const mathematics = /\b(mathematics|maths|math|numeracy|arithmetic)\b/i.test(subject)
  if (mathematics) {
    if (/^(fractions?( i{1,3})?|equivalent fractions|fractions around us|introduction to fractions|common fractions)$/.test(title)) return 'fractions'
    if (/^(place value|place value of (whole )?numbers|whole numbers and place value)$/.test(title)) return 'place-value'
    if (/^(area and perimeter|perimeter and area|area of rectangles?|perimeter of rectangles?|area and perimeter of rectangles?|perimeter and area of plane shapes)$/.test(title)) return 'area-perimeter'
  }
  if (/\b(science|physics|technology)\b/i.test(subject) && /^(simple (electric |electrical )?circuits?|electric circuits?|electrical circuits?|open and closed circuits?)$/.test(title)) return 'circuits'
  return null
}

export function greatestCommonDivisor(a: number, b: number): number {
  return b === 0 ? a : greatestCommonDivisor(b, a % b)
}

export function simplifyFraction(numerator: number, denominator: number): string {
  const divisor = greatestCommonDivisor(numerator, denominator)
  return denominator / divisor === 1 ? String(numerator / divisor) : `${numerator / divisor}/${denominator / divisor}`
}
