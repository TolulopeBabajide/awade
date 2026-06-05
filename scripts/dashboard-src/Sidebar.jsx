import React from 'react';
import { STATUS_COLOR } from './theme.js';

const ICON_PATHS = {
  inbox: 'M3 8l9 6 9-6M3 8v10h18V8M3 8l9-5 9 5',
  outputs: 'M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zM14 2v6h6M9 13h6M9 17h6M9 9h2',
  pulse: 'M3 12h4l3-8 4 16 3-8h4',
  roster: 'M8 11a4 4 0 100-8 4 4 0 000 8zm-7 10a7 7 0 1114 0M16 11a4 4 0 100-8 4 4 0 000 8zm7 10a7 7 0 00-7-7',
  pipeline: 'M3 6h6M3 12h6M3 18h6M15 6h6M15 12h6M15 18h6',
};

function SvgIcon({ path, size = 15 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d={path} />
    </svg>
  );
}

export default function Sidebar({ T, view, setView, stats }) {
  const { agentsCritical: critical = 0, agentsWarning: warning = 0, agentsScheduled = 0 } = stats;

  const items = [
    { id: 'inbox', label: 'Inbox', badge: stats.inboxCount, badgeTone: 'accent' },
    { id: 'outputs', label: 'Outputs', badge: stats.outputsPending, badgeTone: 'neutral' },
    { id: 'pulse', label: 'Pulse', badge: stats.fails24h > 0 ? stats.fails24h : null, badgeTone: 'warn' },
    {
      id: 'roster', label: 'Roster',
      badge: critical > 0 ? critical : (warning > 0 ? warning : null),
      badgeTone: critical > 0 ? 'crit' : 'warn',
    },
    { id: 'pipeline', label: 'Pipeline', badge: null },
  ];

  return (
    <div style={{
      width: 200, background: T.headerBg, borderRight: `1px solid ${T.border}`,
      display: 'flex', flexDirection: 'column', flexShrink: 0,
    }}>
      <div style={{ padding: '15px 14px 14px', display: 'flex', alignItems: 'center', gap: 9 }}>
        <div style={{
          width: 26, height: 26, borderRadius: 7,
          background: `linear-gradient(135deg, ${T.accent}, #8b5cf6)`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: '#fff', fontWeight: 700, fontSize: 11,
        }}>AT</div>
        <div>
          <div style={{ fontWeight: 700, fontSize: 12.5, letterSpacing: -0.1 }}>Agentic Team</div>
          <div style={{ fontSize: 10.5, color: T.mute }}>33 agents · {agentsScheduled} scheduled</div>
        </div>
      </div>

      <div style={{ padding: '4px 8px', display: 'flex', flexDirection: 'column', gap: 1 }}>
        {items.map(it => {
          const active = view === it.id;
          const tone = it.badge != null && it.badge > 0
            ? (it.badgeTone === 'crit' ? '#ef4444'
              : it.badgeTone === 'warn' ? '#f59e0b'
              : it.badgeTone === 'accent' ? T.accent
              : T.mute)
            : null;
          return (
            <div key={it.id} onClick={() => setView(it.id)} style={{
              display: 'flex', alignItems: 'center', gap: 9, padding: '7px 10px', borderRadius: 7,
              background: active ? T.selectedBg : 'transparent',
              color: active ? T.accent : T.sub,
              fontWeight: active ? 600 : 500, fontSize: 12.5, cursor: 'pointer',
            }}>
              <SvgIcon path={ICON_PATHS[it.id]} />
              <span style={{ flex: 1 }}>{it.label}</span>
              {it.badge != null && it.badge > 0 && (
                <span style={{
                  fontSize: 10.5, fontWeight: 700, padding: '1px 6px', borderRadius: 4,
                  background: (tone === T.accent && active) ? T.accent : (tone === T.mute ? T.panel2 : `${tone}22`),
                  color: (tone === T.accent && active) ? '#fff' : tone,
                  border: tone === T.mute ? `1px solid ${T.border}` : 'none',
                  minWidth: 18, textAlign: 'center',
                }}>{it.badge}</span>
              )}
            </div>
          );
        })}
      </div>

      <div style={{ flex: 1 }} />
      <div style={{ padding: '10px 14px', borderTop: `1px solid ${T.border}`, fontSize: 10.5, color: T.mute }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 5, marginBottom: 3 }}>
          <span style={{
            width: 6, height: 6, borderRadius: '50%',
            background: critical > 0 ? '#ef4444' : '#10b981',
            boxShadow: critical > 0 ? '0 0 0 3px rgba(239,68,68,.18)' : '0 0 0 3px rgba(16,185,129,.2)',
          }} />
          <span style={{ fontWeight: 600, color: T.sub }}>
            {critical > 0 ? `${critical} critical` : 'System healthy'}
          </span>
        </div>
        <div>Refreshed {stats.refreshedAgo} · hourly</div>
      </div>
    </div>
  );
}
