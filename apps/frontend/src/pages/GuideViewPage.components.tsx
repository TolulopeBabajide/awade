/**
 * GuideViewPage.components.tsx
 * Reusable presentational sub-components used by GuideViewPage.
 * Extracted from GuideViewPage.tsx (AWD-M-132) to keep the page file under
 * the 400-line threshold while preserving co-location in the pages/ directory.
 */
import React from 'react'

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
