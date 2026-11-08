import { useId } from 'react'
import { FaLightbulb } from 'react-icons/fa'
import { getConcept, matchConcept, type ConceptId } from './concepts'
import FractionsModel from './FractionsModel'
import PlaceValueModel from './PlaceValueModel'
import AreaModel from './AreaModel'
import CircuitModel from './CircuitModel'

const models = { fractions: FractionsModel, 'place-value': PlaceValueModel, 'area-perimeter': AreaModel, circuits: CircuitModel }

export default function ConceptExplorer({ conceptId, audience = 'parent' }: { conceptId: ConceptId; audience?: 'parent' | 'educator' }) {
  const id = useId()
  const concept = getConcept(conceptId)
  if (!concept) return null
  const Model = models[conceptId]
  return <section className="concept-explorer" aria-labelledby={id}>
    <header className="learning-heading"><span className="learning-icon"><FaLightbulb aria-hidden="true" /></span><div><p className="text-sm text-primary-700">Explore the concept</p><h2 id={id}>{concept.title}</h2></div></header>
    <p className="text-gray-600 mt-3">{concept.description}</p>
    <p className="learning-question">{audience === 'educator' ? 'Ask your class: ' : 'Wonder together: '}{concept.question}</p>
    <Model key={conceptId} />
    <details className="learning-physical"><summary>Try it away from the screen</summary><p>{concept.physicalAlternative}</p></details>
  </section>
}

export function TopicConcept({ topic, subject, audience = 'parent' }: { topic: string; subject: string; audience?: 'parent' | 'educator' }) {
  const conceptId = matchConcept(topic, subject)
  return conceptId ? <ConceptExplorer key={`${topic}-${subject}`} conceptId={conceptId} audience={audience} /> : null
}
