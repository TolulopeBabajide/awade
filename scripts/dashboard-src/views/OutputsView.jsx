import React, { useState, useMemo, useRef } from 'react';
import MarkdownRenderer from '../MarkdownRenderer.jsx';

const REVIEW_COLOR = {
  pending:  { bg: 'rgba(156,163,175,.15)', fg: '#9ca3af', label: 'pending' },
  approved: { bg: 'rgba(16,185,129,.12)',  fg: '#10b981', label: 'approved' },
  rejected: { bg: 'rgba(239,68,68,.10)',   fg: '#ef4444', label: 'rejected' },
  revised:  { bg: 'rgba(245,158,11,.10)',  fg: '#f59e0b', label: 'revised'  },
};

function ReviewBadge({ state }) {
  const c = REVIEW_COLOR[state] || REVIEW_COLOR.pending;
  return (
    <span style={{
      fontSize: 9.5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: .04,
      padding: '1px 5px', borderRadius: 4, background: c.bg, color: c.fg, flexShrink: 0,
    }}>{c.label}</span>
  );
}

export default function OutputsView({ T, outputs, liveMode, search }) {
  const [selectedPath, setSelectedPath] = useState(outputs[0]?.path || null);
  const [reviewStates, setReviewStates] = useState(() =>
    Object.fromEntries(outputs.map(o => [o.path, o.review || 'pending']))
  );
  // Tracks whether the reading pane has been scrolled past threshold for each path
  const [scrolledPaths, setScrolledPaths] = useState({});
  const paneRef = useRef(null);

  const filtered = useMemo(() => {
    if (!search) return outputs;
    const q = search.toLowerCase();
    return outputs.filter(o =>
      (o.path + ' ' + o.agent + ' ' + o.category + ' ' + o.title).toLowerCase().includes(q)
    );
  }, [outputs, search]);

  // Group by category, preserving insertion order (outputs already sorted by date desc)
  const grouped = useMemo(() => {
    const map = new Map();
    for (const o of filtered) {
      const key = o.category || 'Other';
      if (!map.has(key)) map.set(key, []);
      map.get(key).push(o);
    }
    return Array.from(map.entries());
  }, [filtered]);

  const selected = outputs.find(o => o.path === selectedPath);

  function handleSelect(path) {
    if (path === selectedPath) return;
    setSelectedPath(path);
    if (paneRef.current) paneRef.current.scrollTop = 0;
  }

  function handlePaneScroll(e) {
    if (!selectedPath || scrolledPaths[selectedPath]) return;
    if (e.currentTarget.scrollTop > 80) {
      setScrolledPaths(prev => ({ ...prev, [selectedPath]: true }));
    }
  }

  function handleVerb(verb) {
    if (!selectedPath) return;
    const state = verb === 'Approve' ? 'approved' : verb === 'Reject' ? 'rejected' : 'revised';
    setReviewStates(prev => ({ ...prev, [selectedPath]: state }));
  }

  const showScrollTip = selected?.content && !scrolledPaths[selectedPath];

  return (
    <div style={{ display: 'flex', flex: 1, minWidth: 0, minHeight: 0 }}>
      {/* List — grouped by category */}
      <div style={{
        width: 300, background: T.panel, borderRight: `1px solid ${T.border}`,
        display: 'flex', flexDirection: 'column', flexShrink: 0, overflowY: 'auto',
      }}>
        <div style={{ padding: '12px 14px', borderBottom: `1px solid ${T.border}`, fontSize: 12, fontWeight: 700, color: T.text }}>
          Outputs <span style={{ color: T.mute, fontWeight: 400 }}>({filtered.length})</span>
        </div>

        {grouped.length === 0 && (
          <div style={{ padding: 20, color: T.mute, fontSize: 12, textAlign: 'center' }}>
            {search ? 'No outputs match your search.' : 'No outputs found.'}
          </div>
        )}

        {grouped.map(([category, items]) => (
          <div key={category}>
            <div style={{
              padding: '7px 14px 5px', fontSize: 10, fontWeight: 700, textTransform: 'uppercase',
              letterSpacing: .07, color: T.mute, background: T.headerBg,
              borderBottom: `1px solid ${T.border}`, position: 'sticky', top: 0, zIndex: 1,
            }}>{category}</div>
            {items.map(o => {
              const rState = reviewStates[o.path] || 'pending';
              return (
                <div key={o.path} onClick={() => handleSelect(o.path)} style={{
                  padding: '10px 14px', borderBottom: `1px solid ${T.border}`, cursor: 'pointer',
                  background: selectedPath === o.path ? T.selectedBg : 'transparent',
                }}>
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: 6, marginBottom: 3 }}>
                    <div style={{
                      fontSize: 12.5, fontWeight: 600, color: T.text, flex: 1,
                      overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                    }}>
                      {o.title}
                    </div>
                    <ReviewBadge state={rState} />
                  </div>
                  <div style={{ fontSize: 11, color: T.mute }}>
                    {o.agent} · {o.date}
                  </div>
                </div>
              );
            })}
          </div>
        ))}
      </div>

      {/* Reading pane */}
      <div
        ref={paneRef}
        onScroll={handlePaneScroll}
        style={{ flex: 1, padding: '20px 24px', overflowY: 'auto', background: T.panel2 }}
      >
        {selected ? (
          <>
            <div style={{ marginBottom: 16 }}>
              <div style={{ fontSize: 11, color: T.mute, marginBottom: 6, textTransform: 'uppercase', letterSpacing: .06 }}>
                {selected.category} · {selected.agent} · {selected.date}
              </div>
              <h2 style={{ fontSize: 17, fontWeight: 700, color: T.text, margin: 0 }}>{selected.title}</h2>
              <div style={{ fontSize: 11, color: T.faint, marginTop: 4 }}>{selected.path}</div>
            </div>

            {/* Action row with non-blocking scroll tip (R4) */}
            <div style={{ marginBottom: 20 }}>
              {showScrollTip && (
                <div style={{
                  fontSize: 11, color: T.mute, marginBottom: 8,
                  padding: '4px 10px', background: T.panel, borderRadius: 6,
                  border: `1px solid ${T.border}`, display: 'inline-block',
                }}>
                  Scroll through the content before approving
                </div>
              )}
              <div style={{ display: 'flex', gap: 8 }}>
                {['Approve', 'Reject', 'Revise'].map(verb => (
                  <button key={verb} onClick={() => handleVerb(verb)} style={{
                    padding: '6px 14px', borderRadius: 7, border: `1px solid ${T.border}`,
                    background: verb === 'Approve' ? 'rgba(16,185,129,.08)' : T.panel,
                    color: verb === 'Approve' ? '#10b981' : verb === 'Reject' ? '#ef4444' : T.sub,
                    fontSize: 12, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit',
                  }}>
                    {verb}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ borderTop: `1px solid ${T.border}`, paddingTop: 20 }}>
              {selected.content ? (
                <MarkdownRenderer text={selected.content} T={T} />
              ) : (
                <div style={{ color: T.mute, fontSize: 12, fontStyle: 'italic' }}>
                  No content available for this output. Open the source file to view.
                </div>
              )}
            </div>
          </>
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: T.mute, fontSize: 12 }}>
            Select an output to read it inline
          </div>
        )}
      </div>
    </div>
  );
}
