import type { ReactNode } from 'react'

export default function ScreenHeader({ title, description, action, label }: { title: string; description: string; action?: ReactNode; label?: string }) {
  return <header className="screen-header"><div>{label && <p className="screen-context">{label}</p>}<h1>{title}</h1><p className="screen-description">{description}</p></div>{action && <div className="screen-header-action">{action}</div>}</header>
}
