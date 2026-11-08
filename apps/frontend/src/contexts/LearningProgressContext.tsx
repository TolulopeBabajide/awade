import { createContext, useContext, useState, type ReactNode } from 'react'
import { useAuth } from './AuthContext'
import type { ConceptId } from '../components/learning/concepts'

interface LearningProgress {
  discoveries: ConceptId[]
  recordDiscovery: (id: ConceptId) => void
}

const LearningProgressContext = createContext<LearningProgress | null>(null)

export function LearningProgressProvider({ children }: { children: ReactNode }) {
  const [discoveries, setDiscoveries] = useState<ConceptId[]>([])
  const recordDiscovery = (id: ConceptId) => {
    setDiscoveries(current => current.includes(id) ? current : [...current, id])
  }
  return <LearningProgressContext.Provider value={{ discoveries, recordDiscovery }}>{children}</LearningProgressContext.Provider>
}

/** Keying the provider isolates discoveries when an account logs in, changes or logs out. */
export function LearningSession({ children }: { children: ReactNode }) {
  const { user } = useAuth()
  return <LearningProgressProvider key={user?.user_id ?? 'guest'}>{children}</LearningProgressProvider>
}

export function useLearningProgress() {
  return useContext(LearningProgressContext)
}
