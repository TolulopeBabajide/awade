import { Link } from 'react-router-dom'
import { FaCompass } from 'react-icons/fa'
import { useAuth } from '../contexts/AuthContext'

export default function NotFoundPage() {
  const { user } = useAuth()
  return <main className="screen-not-found"><Link to="/" className="screen-wordmark">awade<span>.</span></Link><div className="screen-not-found-content"><FaCompass aria-hidden="true" /><p className="screen-context">Page not found</p><h1>Let’s find your way back.</h1><p>This link may have moved or no longer be available. Your next learning moment is still close by.</p><div className="flex flex-wrap gap-3 mt-6"><Link className="learning-button" to={user ? '/dashboard' : '/'}>{user ? 'Go to dashboard' : 'Back to Awade'}</Link><Link className="learning-button-secondary" to={user ? '/explore' : '/login'}>{user ? 'Explore a concept' : 'Sign in'}</Link></div></div></main>
}
