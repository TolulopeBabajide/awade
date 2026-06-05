import React from 'react';

const VIEW_PLACEHOLDER = {
  inbox: 'Search inbox… (j/k to navigate, ↵ primary action, e to dismiss)',
  outputs: 'Search outputs by path, agent, or category…',
  pulse: 'Search activity stream…',
  roster: 'Search agents by name or department…',
  pipeline: 'Search backlog by id, title, area…',
};

export default function TopBar({ T, view, search, setSearch, liveMode, setLiveMode, runs24h }) {
  return (
    <div style={{
      padding: '10px 16px', background: T.panel, borderBottom: `1px solid ${T.border}`,
      display: 'flex', alignItems: 'center', gap: 12, flexShrink: 0,
    }}>
      <div style={{ flex: 1, maxWidth: 560, position: 'relative' }}>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={T.mute}
          strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
          style={{ position: 'absolute', left: 11, top: '50%', transform: 'translateY(-50%)' }}>
          <circle cx="11" cy="11" r="7" /><path d="M21 21l-4.3-4.3" />
        </svg>
        <input
          placeholder={VIEW_PLACEHOLDER[view] || 'Search…'}
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{
            width: '100%', boxSizing: 'border-box',
            padding: '7px 11px 7px 32px', borderRadius: 7, fontSize: 12.5,
            border: `1px solid ${T.border}`, background: T.panel2, color: T.text, outline: 'none',
            fontFamily: 'inherit',
          }}
        />
      </div>

      <div onClick={() => setLiveMode(!liveMode)}
        title={liveMode ? 'One-click — actions POST to /api/action' : 'Command console — actions copy a Claude prompt'}
        style={{
          display: 'inline-flex', alignItems: 'center', gap: 7, padding: '4px 11px', borderRadius: 999,
          border: `1px solid ${liveMode ? 'rgba(16,185,129,.4)' : T.border}`,
          background: liveMode ? 'rgba(16,185,129,.08)' : T.panel2,
          cursor: 'pointer', fontSize: 11.5, fontWeight: 600,
          color: liveMode ? '#10b981' : T.sub,
        }}>
        <span style={{
          width: 7, height: 7, borderRadius: '50%',
          background: liveMode ? '#10b981' : T.mute,
          boxShadow: liveMode ? '0 0 0 4px rgba(16,185,129,.18)' : 'none',
        }} />
        <span>{liveMode ? 'One-click' : 'Command console'}</span>
      </div>

      <div style={{
        padding: '4px 10px', borderRadius: 6, border: `1px solid ${T.border}`, background: T.panel2,
        fontSize: 11, color: T.sub,
      }}>
        <span style={{ color: T.mute }}>Runs / 24h </span>
        <span style={{ color: T.text, fontWeight: 700, fontVariantNumeric: 'tabular-nums' }}>{runs24h}</span>
      </div>
    </div>
  );
}
