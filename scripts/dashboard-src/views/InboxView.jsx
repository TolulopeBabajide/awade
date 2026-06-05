import React, { useState, useMemo } from 'react';
import { URGENCY_COLOR, KIND_GLYPH, STATUS_COLOR } from '../theme.js';
import MarkdownRenderer from '../MarkdownRenderer.jsx';

function copyText(t) {
  try {
    if (navigator.clipboard?.writeText) navigator.clipboard.writeText(t);
    else {
      const ta = document.createElement('textarea');
      ta.value = t; document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); } catch (_) {}
      document.body.removeChild(ta);
    }
  } catch (_) {}
}

// ─── Inbox rail (triage filter sidebar) ───────────────────────────────────────
function InboxRail({ T, filter, setFilter, statusCounts, allInbox, dismissedCount, onUndismissAll }) {
  const cats = [
    { id: 'all', label: 'Everything', count: allInbox.length },
    { id: 'urgent', label: 'Urgent', count: allInbox.filter(d => d.urgency === 'high').length, tint: '#ef4444' },
    { id: 'approve', label: 'Approvals', count: allInbox.filter(d => d.kind === 'approve').length },
    { id: 'decide', label: 'Decisions', count: allInbox.filter(d => d.kind === 'decide').length },
    { id: 'review', label: 'Reviews', count: allInbox.filter(d => d.kind === 'review').length },
    { id: 'respond', label: 'Responses', count: allInbox.filter(d => d.kind === 'respond').length },
  ];

  return (
    <div style={{
      width: 160, background: T.headerBg, borderRight: `1px solid ${T.border}`,
      padding: '14px 10px', display: 'flex', flexDirection: 'column', gap: 1, flexShrink: 0,
    }}>
      <div style={{ padding: '2px 8px 6px', fontSize: 10.5, fontWeight: 700, color: T.mute, textTransform: 'uppercase', letterSpacing: .06 }}>Triage</div>
      {cats.map(c => {
        const active = filter === c.id;
        return (
          <div key={c.id} onClick={() => setFilter(c.id)} style={{
            display: 'flex', alignItems: 'center', gap: 7, padding: '6px 10px', borderRadius: 6,
            background: active ? T.selectedBg : 'transparent',
            color: active ? T.accent : T.sub,
            fontWeight: active ? 600 : 500, fontSize: 12, cursor: 'pointer',
          }}>
            {c.tint && <span style={{ width: 6, height: 6, borderRadius: '50%', background: c.tint, flexShrink: 0 }} />}
            <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{c.label}</span>
            <span style={{ fontSize: 10.5, color: active ? T.accent : T.mute, fontVariantNumeric: 'tabular-nums' }}>{c.count}</span>
          </div>
        );
      })}

      <div style={{ padding: '14px 8px 6px', fontSize: 10.5, fontWeight: 700, color: T.mute, textTransform: 'uppercase', letterSpacing: .06 }}>Fleet</div>
      {[
        { color: '#ef4444', label: 'critical', n: statusCounts.critical || 0 },
        { color: '#f59e0b', label: 'warning', n: statusCounts.warning || 0 },
        { color: '#10b981', label: 'healthy', n: statusCounts.healthy || 0 },
        { color: T.mute, label: 'idle', n: (statusCounts.idle || 0) + (statusCounts['on-demand'] || 0) },
      ].map(({ color, label, n }) => (
        <div key={label} style={{ padding: '5px 10px', fontSize: 11.5, color: T.sub, display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 5, height: 5, borderRadius: '50%', background: color, flexShrink: 0 }} />
          <span style={{ flex: 1, textTransform: 'capitalize' }}>{label}</span>
          <span style={{ fontVariantNumeric: 'tabular-nums', color: n > 0 ? T.text : T.faint }}>{n}</span>
        </div>
      ))}

      {dismissedCount > 0 && (
        <>
          <div style={{ flex: 1 }} />
          <div onClick={onUndismissAll} style={{
            padding: '6px 10px', borderRadius: 6, fontSize: 11, color: T.mute, cursor: 'pointer',
            border: `1px dashed ${T.border}`, textAlign: 'center', marginTop: 8,
          }}>
            ↺ restore {dismissedCount}
          </div>
        </>
      )}
    </div>
  );
}

// ─── Inbox item row ────────────────────────────────────────────────────────────
function InboxRow({ T, item, selected, onSelect, onDismiss }) {
  const urgColor = URGENCY_COLOR[item.urgency] || T.mute;
  const glyph = KIND_GLYPH[item.kind] || '·';
  return (
    <div onClick={() => onSelect(item.id)} style={{
      padding: '11px 14px', borderBottom: `1px solid ${T.border}`,
      background: selected ? T.selectedBg : 'transparent',
      cursor: 'pointer', position: 'relative',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
        <span style={{
          width: 20, height: 20, borderRadius: 5, background: `${urgColor}20`,
          color: urgColor, fontSize: 10, fontWeight: 700,
          display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
        }}>{glyph}</span>
        <span style={{
          fontSize: 12.5, fontWeight: 600, color: T.text, flex: 1,
          overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
        }}>{item.title}</span>
        {item.urgency === 'high' && (
          <span style={{
            fontSize: 9.5, fontWeight: 700, color: '#ef4444', background: 'rgba(239,68,68,.1)',
            padding: '1px 5px', borderRadius: 4, flexShrink: 0,
          }}>URGENT</span>
        )}
      </div>
      <div style={{ display: 'flex', gap: 12, paddingLeft: 28, fontSize: 11, color: T.mute }}>
        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flex: 1 }}>
          {item.from} · {item.age}
        </span>
        <span style={{ flexShrink: 0 }}>~{item.est}</span>
        <span
          onClick={e => { e.stopPropagation(); onDismiss(item.id); }}
          title="Dismiss"
          style={{ cursor: 'pointer', color: T.faint, flexShrink: 0, lineHeight: 1, padding: '0 2px' }}>✕</span>
      </div>
    </div>
  );
}

// ─── Inbox list column ─────────────────────────────────────────────────────────
function InboxList({ T, items, selectedId, onSelect, onDismiss, filter, search }) {
  const label = filter === 'all'
    ? (search ? 'Results' : 'Inbox')
    : filter.charAt(0).toUpperCase() + filter.slice(1);

  return (
    <div style={{
      width: 340, background: T.panel, borderRight: `1px solid ${T.border}`,
      display: 'flex', flexDirection: 'column', flexShrink: 0,
    }}>
      <div style={{ padding: '12px 14px 10px', borderBottom: `1px solid ${T.border}` }}>
        <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
          <span style={{ fontSize: 12, fontWeight: 700, color: T.text }}>{label}</span>
          <span style={{ fontSize: 10.5, color: T.mute }}>{items.length} item{items.length !== 1 ? 's' : ''}</span>
        </div>
      </div>
      <div style={{ flex: 1, overflowY: 'auto' }}>
        {items.length === 0 ? (
          <div style={{ padding: '24px 14px', textAlign: 'center', color: T.mute, fontSize: 12 }}>
            {search ? 'No items match your search.' : 'Inbox zero — all caught up.'}
          </div>
        ) : items.map(item => (
          <InboxRow
            key={item.id}
            T={T}
            item={item}
            selected={selectedId === item.id}
            onSelect={onSelect}
            onDismiss={onDismiss}
          />
        ))}
      </div>
    </div>
  );
}

// ─── Decision reader (reading pane) ───────────────────────────────────────────
function DecisionReader({ T, item, liveMode, onAction, onDismiss }) {
  const [note, setNote] = useState('');
  const [noteFor, setNoteFor] = useState(null);
  const urgColor = URGENCY_COLOR[item.urgency] || T.mute;

  const openEndedVerbs = new Set(['Revise', 'Send back', 'Approve scope', 'Move to define', 'Draft replies']);

  function handleAction(action) {
    const prompt = note && noteFor === action.verb ? `${action.prompt}\n\n${note}` : action.prompt;
    if (!liveMode) {
      copyText(prompt);
      onAction('Prompt copied — paste into Claude');
    } else {
      onAction(`Running: ${action.verb}`);
      if (action.dismissOnRun) onDismiss(item.id);
    }
    setNote(''); setNoteFor(null);
  }

  return (
    <div style={{ padding: '20px 24px', overflowY: 'auto', height: '100%', boxSizing: 'border-box' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12, marginBottom: 16 }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
            <span style={{
              fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: .08,
              color: urgColor, background: `${urgColor}18`, padding: '2px 7px', borderRadius: 4,
            }}>{item.urgency}</span>
            <span style={{ fontSize: 10, color: T.mute, textTransform: 'uppercase', letterSpacing: .06 }}>
              {item.kind}
            </span>
          </div>
          <h2 style={{ fontSize: 17, fontWeight: 700, color: T.text, lineHeight: 1.3, margin: 0 }}>
            {item.title}
          </h2>
        </div>
        <div onClick={() => onDismiss(item.id)} style={{
          cursor: 'pointer', color: T.faint, fontSize: 18, lineHeight: 1, padding: '2px 4px',
          flexShrink: 0,
        }} title="Dismiss">✕</div>
      </div>

      {/* Meta */}
      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginBottom: 16, fontSize: 11.5, color: T.mute }}>
        <span><strong style={{ color: T.sub }}>From</strong> {item.from}</span>
        <span><strong style={{ color: T.sub }}>Via</strong> {item.via}</span>
        {item.relatedBacklog && <span><strong style={{ color: T.sub }}>Backlog</strong> <span style={{ color: T.accent }}>{item.relatedBacklog}</span></span>}
        <span><strong style={{ color: T.sub }}>Age</strong> {item.age}</span>
        <span><strong style={{ color: T.sub }}>Est</strong> {item.est}</span>
      </div>

      {/* Impact callout */}
      {item.impact && (
        <div style={{
          background: `rgba(239,68,68,.06)`, border: `1px solid rgba(239,68,68,.2)`,
          borderRadius: 7, padding: '8px 12px', marginBottom: 16, fontSize: 12.5, color: '#ef4444',
          display: 'flex', alignItems: 'center', gap: 8,
        }}>
          <span style={{ fontSize: 14 }}>⚠</span>
          <span>{item.impact}</span>
        </div>
      )}

      {/* Detail */}
      <p style={{ fontSize: 13, color: T.text, lineHeight: 1.6, marginBottom: 20 }}>
        {item.detail}
      </p>

      {/* Source artifact — path header + inline content */}
      {item.originPath && (
        <div style={{ marginBottom: 20 }}>
          <div style={{
            padding: '8px 12px', background: T.panel2,
            borderRadius: item.content ? '7px 7px 0 0' : 7,
            border: `1px solid ${T.border}`,
            fontSize: 11.5, color: T.mute, display: 'flex', alignItems: 'center', gap: 8,
          }}>
            <span style={{ fontSize: 13 }}>📄</span>
            <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: T.sub }}>
              {item.originPath}
            </span>
          </div>
          {item.content ? (
            <div style={{
              border: `1px solid ${T.border}`, borderTop: 'none',
              borderRadius: '0 0 7px 7px', padding: '12px 16px',
              maxHeight: 400, overflowY: 'auto', background: T.bg,
            }}>
              <MarkdownRenderer text={item.content} T={T} />
            </div>
          ) : (
            <div style={{
              border: `1px solid ${T.border}`, borderTop: 'none',
              borderRadius: '0 0 7px 7px', padding: '10px 14px',
              fontSize: 11.5, color: T.faint, fontStyle: 'italic', background: T.bg,
            }}>
              Content not embedded — open the file to read it.
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 16 }}>
        {(item.actions || []).map((action, i) => {
          const isOpen = openEndedVerbs.has(action.verb);
          return (
            <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {isOpen && noteFor === action.verb && (
                <textarea
                  value={note}
                  onChange={e => setNote(e.target.value)}
                  placeholder="Type your note to include with the prompt…"
                  rows={3}
                  style={{
                    width: 300, borderRadius: 6, border: `1px solid ${T.border}`,
                    background: T.panel2, color: T.text, fontSize: 12, padding: '6px 10px',
                    fontFamily: 'inherit', resize: 'vertical',
                  }}
                />
              )}
              <button
                onClick={() => {
                  if (isOpen && noteFor !== action.verb) { setNoteFor(action.verb); return; }
                  handleAction(action);
                }}
                style={{
                  padding: '7px 14px', borderRadius: 7, border: `1px solid ${T.border}`,
                  background: action.color === 'green' ? 'rgba(16,185,129,.08)' : T.panel2,
                  color: action.color === 'green' ? '#10b981' : T.sub,
                  fontSize: 12, fontWeight: action.primary ? 600 : 500, cursor: 'pointer',
                  fontFamily: 'inherit',
                }}
              >
                {isOpen && noteFor !== action.verb ? `${action.verb} ›` : action.verb}
                {action.primary && !liveMode && <span style={{ fontSize: 10, color: T.faint, marginLeft: 6 }}>⎘</span>}
              </button>
            </div>
          );
        })}
      </div>

      {!liveMode && (
        <p style={{ fontSize: 11, color: T.faint, marginTop: 8 }}>
          Command console — actions copy a Claude prompt. Switch to One-click when <code>dashboard-server.py</code> is running.
        </p>
      )}
    </div>
  );
}

// ─── Empty state ───────────────────────────────────────────────────────────────
function EmptyState({ T, title, detail }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: 8, padding: 32 }}>
      <div style={{ fontSize: 28 }}>✉</div>
      <div style={{ fontSize: 14, fontWeight: 700, color: T.text }}>{title}</div>
      <div style={{ fontSize: 12, color: T.mute, textAlign: 'center', maxWidth: 280 }}>{detail}</div>
    </div>
  );
}

// ─── InboxView ─────────────────────────────────────────────────────────────────
export default function InboxView({
  T, inbox, filter, setFilter, selectedId, setSelectedId,
  dismissed, onDismiss, onUndismissAll, liveMode, onToast, statusCounts, search,
}) {
  const visibleItems = useMemo(() => {
    let xs = inbox.filter(d => !dismissed.has(d.id));
    if (filter === 'urgent')  xs = xs.filter(d => d.urgency === 'high');
    if (filter === 'approve') xs = xs.filter(d => d.kind === 'approve');
    if (filter === 'decide')  xs = xs.filter(d => d.kind === 'decide');
    if (filter === 'review')  xs = xs.filter(d => d.kind === 'review');
    if (filter === 'respond') xs = xs.filter(d => d.kind === 'respond');
    if (search) {
      const q = search.toLowerCase();
      xs = xs.filter(d =>
        (d.title + ' ' + d.from + ' ' + d.detail + ' ' + d.originPath).toLowerCase().includes(q)
      );
    }
    return xs;
  }, [inbox, dismissed, filter, search]);

  const selected = inbox.find(d => d.id === selectedId);
  const dismissedCount = inbox.length - inbox.filter(d => !dismissed.has(d.id)).length;

  return (
    <>
      <InboxRail
        T={T}
        filter={filter}
        setFilter={setFilter}
        statusCounts={statusCounts}
        allInbox={inbox}
        dismissedCount={dismissedCount}
        onUndismissAll={onUndismissAll}
      />
      <InboxList
        T={T}
        items={visibleItems}
        selectedId={selectedId}
        onSelect={setSelectedId}
        onDismiss={onDismiss}
        filter={filter}
        search={search}
      />
      <div style={{ flex: 1, background: T.panel2, minWidth: 0, overflow: 'auto' }}>
        {selected ? (
          <DecisionReader
            T={T}
            item={selected}
            liveMode={liveMode}
            onAction={onToast}
            onDismiss={onDismiss}
          />
        ) : (
          <EmptyState
            T={T}
            title={search ? 'Nothing matches' : 'Inbox zero'}
            detail={search
              ? 'No items match your search. Clear the filter to see everything.'
              : "You're all caught up. The agents will surface anything new here."
            }
          />
        )}
      </div>
    </>
  );
}
