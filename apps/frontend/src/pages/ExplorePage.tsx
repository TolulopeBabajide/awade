import { useSearchParams } from 'react-router-dom'
import { FaArrowRight, FaCheckCircle, FaCompass, FaSeedling } from 'react-icons/fa'
import Sidebar from '../components/Sidebar'
import MobileNavigation from '../components/MobileNavigation'
import ConceptExplorer from '../components/learning/ConceptExplorer'
import { concepts, getConcept } from '../components/learning/concepts'
import { useAuth } from '../contexts/AuthContext'
import { useLearningProgress } from '../contexts/LearningProgressContext'

export default function ExplorePage() {
  const [params, setParams] = useSearchParams()
  const { user } = useAuth()
  const progress = useLearningProgress()
  const selected = getConcept(params.get('concept')) ?? concepts[0]
  const educator = user?.role !== 'PARENT'
  return <div className="learning-workspace flex min-h-screen">
    <Sidebar currentPage="explore" />
    <main id="main-content" tabIndex={-1} className="flex-1 min-w-0 lg:ml-64 px-4 sm:px-6 lg:px-10 pt-7 pb-28 outline-none">
      <div className="max-w-6xl mx-auto">
        <header className="explore-intro"><p className="flex gap-2 items-center text-primary-700 text-sm"><FaCompass aria-hidden="true" /> A little curiosity goes a long way</p><h1>Make an idea click.</h1><p>{educator ? 'Bring a concept to life with your class. Predict, change something, then explain what happens.' : 'See it, change it, talk about it. Discover an idea together, one small experiment at a time.'}</p></header>
        <div className="explore-layout">
          <div className="explore-picker"><h2>Choose a concept</h2><div className="explore-concepts">
            {concepts.map(concept => <button type="button" key={concept.id} aria-pressed={selected.id === concept.id} className="explore-concept" onClick={() => setParams({ concept: concept.id })}>
              <span className="text-xs text-primary-700">{concept.subject}</span><strong>{concept.title}</strong><span className="text-sm text-gray-600">{concept.description}</span><span className="explore-concept-action">{progress?.discoveries.includes(concept.id) ? <><FaCheckCircle aria-hidden="true" /> Discovery collected</> : <>Explore this idea <FaArrowRight aria-hidden="true" /></>}</span>
            </button>)}
          </div><div className="learning-session"><FaSeedling aria-hidden="true" /><div><strong>{progress?.discoveries.length ?? 0} {progress?.discoveries.length === 1 ? 'discovery' : 'discoveries'} this visit</strong><p>Collected once per concept. Resets when you reload or change accounts. Take your time.</p></div></div></div>
          <ConceptExplorer key={selected.id} conceptId={selected.id} audience={educator ? 'educator' : 'parent'} />
        </div>
      </div>
    </main>
    <MobileNavigation currentPage="explore" />
  </div>
}
