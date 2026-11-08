import { useState, type ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { FaArrowLeft, FaCheck, FaLeaf } from 'react-icons/fa'

export default function AuthLayout({ children, mode }: { children: ReactNode; mode: 'signup' | 'login' | 'reset' }) {
  const [split, setSplit] = useState(false)
  return <div className="account-screen">
    <aside className="account-story" aria-label="Learning with Awade">
      <Link to="/" className="screen-wordmark" aria-label="Awade - Go to homepage">awade<span>.</span></Link>
      <p className="text-sm text-primary-700 mt-3">Learning support for home and school</p>
      <div className="account-story-content">
        <h1>{mode === 'signup' ? 'Big ideas start with small moments.' : mode === 'login' ? 'A little curiosity. A world of possibility.' : 'A fresh start for your next discovery.'}</h1>
        <p>For the people who help children learn. At home, in the classroom, and in the everyday moments in between.</p>
        <div className="account-paper" role="img" aria-label={`${split ? '4 of 8' : '2 of 4'} equal parts shaded; one half of the same whole`} style={{ gridTemplateColumns: `repeat(${split ? 8 : 4}, 1fr)` }}>
          {Array.from({ length: split ? 8 : 4 }, (_, index) => <span key={index} className={index < (split ? 4 : 2) ? 'is-shaded' : ''}>{index < (split ? 4 : 2) ? <FaCheck aria-hidden="true" /> : null}</span>)}
        </div>
        <div className="account-paper-caption"><strong aria-live="polite">{split ? '4/8' : '2/4'} = one half</strong><button type="button" onClick={() => setSplit(!split)}>{split ? 'Join the parts' : 'Split the parts'}</button></div>
        <p className="account-story-note">Different parts. The same whole. Sometimes, seeing it makes all the difference.</p>
      </div>
      <p className="account-footer"><FaLeaf aria-hidden="true" /> Rooted in everyday learning across Africa.</p>
    </aside>
    <main className="account-main" id="main-content">
      <div className="account-topline"><Link to="/" className="account-back"><FaArrowLeft aria-hidden="true" /> Back to Awade</Link><p>{mode === 'signup' ? 'Already a member? ' : 'New to Awade? '}<Link to={mode === 'signup' ? '/login' : '/signup'}>{mode === 'signup' ? 'Sign in' : 'Join us'}</Link></p></div>
      <div className="account-form-region">{children}</div>
      <p className="account-fineprint">A helping hand for every learning journey.</p>
    </main>
  </div>
}
