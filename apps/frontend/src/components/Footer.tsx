import { Link } from 'react-router-dom'

export default function Footer() {
  return <footer className="public-footer"><div><Link to="/" className="screen-wordmark" aria-label="Awade homepage">awade<span>.</span></Link><p>A helping hand for the people who help children learn.</p></div><nav aria-label="Footer navigation"><a href="#features">How Awade helps</a><Link to="/signup">Get started</Link><Link to="/login">Sign in</Link><Link to="/terms">Terms & Conditions</Link><Link to="/privacy-policy">Privacy Policy</Link><Link to="/disclaimer">About AI content</Link></nav><p className="public-footer-copyright">© {new Date().getFullYear()} Awade. Little moments. Lasting learning.</p></footer>
}
