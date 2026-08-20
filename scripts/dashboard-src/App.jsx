import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { tokens } from './theme.js';
import { adaptData } from './data.js';
import Sidebar from './Sidebar.jsx';
import TopBar from './TopBar.jsx';
import InboxView from './views/InboxView.jsx';
import OutputsView from './views/OutputsView.jsx';
import PulseView from './views/PulseView.jsx';
import RosterView from './views/RosterView.jsx';
import PipelineView from './views/PipelineView.jsx';

// localStorage persistence with JSON serialisation
function useLS(key, initial) {
  const [v, setV] = useState(() => {
    try {
      const s = localStorage.getItem(key);
      return s != null ? JSON.parse(s) : initial;
    } catch { return initial; }
  });
  useEffect(() => {
    try { localStorage.setItem(key, JSON.stringify(v)); } catch {}
  }, [key, v]);
  return [v, setV];
}

function timeAgo(isoStr) {
  if (!isoStr) return '—';
  try {
    const diff = Math.floor((Date.now() - new Date(isoStr).getTime()) / 1000);
    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
  } catch { return '—'; }
}

export default function App() {
  const rawData = window.DASHBOARD_DATA || {};
  const { agents, events, outputs, inbox, stats, backlog, tasks, departments } = useMemo(
    () => adaptData(rawData), [rawData.generated]
  );

  // Persisted UI state (R9)
  const [theme] = useLS('dash:theme', 'dark');
  const [view, setView] = useLS('dash:view', 'inbox');
  const [liveMode, setLiveMode] = useLS('dash:liveMode', false);
  const [dismissedArr, setDismissedArr] = useLS('dash:dismissed', []);
  const dismissed = useMemo(() => new Set(dismissedArr), [dismissedArr]);
  const setDismissed = (next) => setDismissedArr(Array.from(next));

  const [filter, setFilter] = useState('all');
  const [selectedId, setSelectedId] = useState(inbox[0]?.id || null);
  const [search, setSearch] = useState('');
  const [toast, setToast] = useState(null);

  const T = tokens(theme);

  function showToast(msg) {
    setToast(msg);
    setTimeout(() => setToast(null), 2000);
  }

  function onDismiss(id) {
    const next = new Set(dismissed);
    next.add(id);
    setDismissed(next);
    if (selectedId === id) {
      const next2 = inbox.filter(d => !next.has(d.id) && d.id !== id);
      if (next2[0]) setSelectedId(next2[0].id);
    }
  }

  function onUndismissAll() {
    setDismissed(new Set());
  }

  // Keyboard triage (R-P1.8 partial)
  useEffect(() => {
    const visible = inbox.filter(d => !dismissed.has(d.id));
    const handler = (e) => {
      if (e.target?.tagName === 'INPUT' || e.target?.tagName === 'TEXTAREA') return;
      if (view !== 'inbox') return;
      if (e.key === 'j') {
        const idx = visible.findIndex(d => d.id === selectedId);
        const next = visible[Math.min(visible.length - 1, idx + 1)];
        if (next) setSelectedId(next.id);
      } else if (e.key === 'k') {
        const idx = visible.findIndex(d => d.id === selectedId);
        const prev = visible[Math.max(0, idx - 1)];
        if (prev) setSelectedId(prev.id);
      } else if (e.key === 'e' && selectedId) {
        onDismiss(selectedId);
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [view, inbox, dismissed, selectedId]);

  const statusCounts = useMemo(() => ({
    healthy: stats.agentsHealthy,
    warning: stats.agentsWarning,
    critical: stats.agentsCritical,
    idle: stats.agentsIdle,
    'on-demand': stats.agentsOnDemand,
  }), [stats]);

  const sidebarStats = {
    ...stats,
    inboxCount: inbox.filter(d => !dismissed.has(d.id)).length,
    outputsPending: outputs.filter(o => o.review === 'pending').length,
    fails24h: events.filter(e => e.status === 'fail').length,
    refreshedAgo: timeAgo(stats.generated),
  };

  return (
    <div style={{
      width: '100%', height: '100%', background: T.appShell, color: T.text,
      fontFamily: '-apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", system-ui, sans-serif',
      fontSize: 13, lineHeight: 1.45, display: 'flex', overflow: 'hidden', position: 'relative',
    }}>
      <Sidebar T={T} view={view} setView={setView} stats={sidebarStats} />

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <TopBar
          T={T}
          view={view}
          search={search}
          setSearch={setSearch}
          liveMode={liveMode}
          setLiveMode={setLiveMode}
          runs24h={stats.runs24h}
        />
        <div style={{ flex: 1, display: 'flex', minHeight: 0, position: 'relative', overflow: 'hidden' }}>
          {view === 'inbox' && (
            <InboxView
              T={T}
              inbox={inbox}
              filter={filter}
              setFilter={setFilter}
              selectedId={selectedId}
              setSelectedId={setSelectedId}
              dismissed={dismissed}
              onDismiss={onDismiss}
              onUndismissAll={onUndismissAll}
              liveMode={liveMode}
              onToast={showToast}
              statusCounts={statusCounts}
              search={search}
            />
          )}
          {view === 'outputs' && (
            <OutputsView T={T} outputs={outputs} liveMode={liveMode} search={search} />
          )}
          {view === 'pulse' && (
            <PulseView T={T} events={events} stats={stats} search={search} />
          )}
          {view === 'roster' && (
            <RosterView
              T={T}
              departments={departments}
              agentsCritical={stats.agentsCritical}
              agentsWarning={stats.agentsWarning}
              agentsHealthy={stats.agentsHealthy}
              search={search}
              events={events}
              liveMode={liveMode}
              onToast={showToast}
            />
          )}
          {view === 'pipeline' && (
            <PipelineView T={T} backlog={backlog} search={search} />
          )}
        </div>
      </div>

      {/* Toast */}
      {toast && (
        <div style={{
          position: 'fixed', bottom: 18, left: '50%', transform: 'translateX(-50%)',
          background: T.text, color: T.bg, padding: '8px 16px', borderRadius: 8,
          fontSize: 12, fontWeight: 600, boxShadow: '0 10px 28px rgba(0,0,0,.3)', zIndex: 40,
        }}>{toast}</div>
      )}
    </div>
  );
}
