import { Link } from 'react-router-dom'
import { FaSeedling } from 'react-icons/fa'
import { useLearningProgress } from '../../contexts/LearningProgressContext'

export default function SessionDiscoveries() {
  const progress = useLearningProgress()
  const count = progress?.discoveries.length ?? 0
  return <section className="screen-discoveries" aria-label="This visit's discoveries"><FaSeedling aria-hidden="true" /><div><h2>{count === 0 ? 'There’s always something to discover.' : `${count} ${count === 1 ? 'discovery' : 'discoveries'} collected this visit.`}</h2><p>Try a concept challenge at your own pace. Discoveries reset when you reload or change accounts.</p></div><Link to="/explore">See the activities</Link></section>
}
