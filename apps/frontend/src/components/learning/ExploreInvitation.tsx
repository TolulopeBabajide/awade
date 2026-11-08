import { Link } from 'react-router-dom'
import { FaArrowRight, FaShapes } from 'react-icons/fa'

export default function ExploreInvitation({ educator = false }: { educator?: boolean }) {
  return <section className="explore-invitation" aria-label="Interactive concept activities">
    <div className="explore-invitation-icon"><FaShapes aria-hidden="true" /></div>
    <div className="flex-1 min-w-0"><h2>Some ideas are easier to see.</h2><p>{educator ? 'Bring fractions, place value, measurement and circuits into your next lesson.' : 'Explore fractions, build numbers, resize shapes and light up a circuit together.'}</p></div>
    <Link className="learning-button" to="/explore">Explore concepts <FaArrowRight aria-hidden="true" /></Link>
  </section>
}
