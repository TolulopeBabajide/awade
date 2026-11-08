import { useState } from 'react'
import { FaCheckCircle, FaSeedling } from 'react-icons/fa'
import { useLearningProgress } from '../../contexts/LearningProgressContext'
import type { ConceptId } from './concepts'

interface Props {
  conceptId: ConceptId
  prompt: string
  correct: boolean
  feedback: string
  children?: React.ReactNode
}

export default function Challenge({ conceptId, prompt, correct, feedback, children }: Props) {
  const progress = useLearningProgress()
  const [attempt, setAttempt] = useState<{ correct: boolean; feedback: string } | null>(null)
  const [discovered, setDiscovered] = useState(false)
  const complete = discovered || progress?.discoveries.includes(conceptId)
  const check = () => {
    setAttempt({ correct, feedback })
    if (correct) {
      setDiscovered(true)
      progress?.recordDiscovery(conceptId)
    }
  }
  return (
    <section className="learning-challenge" aria-label="Discovery challenge">
      <div className="flex items-center gap-2 text-primary-800"><FaSeedling aria-hidden="true" /><h3>Try a discovery</h3></div>
      <p className="mt-2">{prompt}</p>
      {children}
      <button type="button" className="learning-button mt-4" onClick={check}>Check my model</button>
      <p role="status" className="learning-feedback">{attempt && attempt.correct === correct && attempt.feedback === feedback
        ? correct ? 'You found it. Explain what you noticed to someone learning with you.' : feedback
        : ''}</p>
      {complete && <p className="learning-earned"><FaCheckCircle aria-hidden="true" /> Discovery collected this visit. Keep exploring at your own pace.</p>}
    </section>
  )
}
