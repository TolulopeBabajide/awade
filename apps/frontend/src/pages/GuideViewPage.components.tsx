/**
 * GuideViewPage.components.tsx
 * Reusable presentational sub-components used by GuideViewPage.
 * Extracted from GuideViewPage.tsx (AWD-M-132) to keep the page file under
 * the 400-line threshold while preserving co-location in the pages/ directory.
 */
import React from 'react'
import Sidebar from '../components/Sidebar'
import MobileNavigation from '../components/MobileNavigation'

// ── GuidePageShell ─────────────────────────────────────────────────────────
// AWD-M-139: common layout wrapper shared by loading, error, and success paths.
// Eliminates the three-way duplication of <div.flex.min-h-screen> + <Sidebar>
// + <MobileNavigation> that previously appeared identically in each branch.

export interface GuidePageShellProps {
  /** Content to render inside <main>. */
  children: React.ReactNode
  /**
   * Additional classes appended to `flex-1 lg:ml-64` on <main>.
   * Loading/error paths use the centred default; the success path passes
   * `'pb-20 lg:pb-0 outline-none'` to match its original class list.
   */
  mainClassName?: string
  /** Forwarded to <main id=…>. Used by the success path for skip-nav. */
  mainId?: string
  /** Forwarded to <main tabIndex=…>. Used by the success path for skip-nav. */
  mainTabIndex?: number
}

export const GuidePageShell: React.FC<GuidePageShellProps> = ({
  children,
  mainClassName = 'flex items-center justify-center',
  mainId,
  mainTabIndex,
}) => (
  <div className="flex min-h-screen bg-background-50">
    <Sidebar currentPage="dashboard" />
    <main
      id={mainId}
      tabIndex={mainTabIndex}
      className={`flex-1 lg:ml-64 ${mainClassName}`}
    >
      {children}
    </main>
    <MobileNavigation currentPage="dashboard" />
  </div>
)

// ── Section ────────────────────────────────────────────────────────────────

export interface SectionProps {
  icon: React.ReactNode
  title: string
  subtitle?: string
  children: React.ReactNode
}

export const Section: React.FC<SectionProps> = ({ icon, title, subtitle, children }) => (
  <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
    <div className="px-5 py-4 border-b border-gray-100 flex items-center gap-3">
      {icon}
      <div>
        <h2 className="font-semibold text-gray-800">{title}</h2>
        {subtitle && <p className="text-xs text-gray-400">{subtitle}</p>}
      </div>
    </div>
    <div className="px-5 py-4">{children}</div>
  </div>
)

// ── InfoCard ───────────────────────────────────────────────────────────────

export interface InfoCardProps {
  label: string
  value: string
}

export const InfoCard: React.FC<InfoCardProps> = ({ label, value }) => (
  <div className="bg-background-50 rounded-xl p-3">
    <p className="text-xs font-medium text-gray-500 mb-1">{label}</p>
    <p className="text-gray-700 text-sm leading-relaxed">{value}</p>
  </div>
)
