import React, { useMemo } from 'react';

const STAGE_ORDER = ['discover', 'define', 'gtm', 'design', 'ready', 'in-progress'];
const STAGE_LABEL = {
  discover: 'Discover', define: 'Define', gtm: 'GTM',
  design: 'Design', ready: 'Ready', 'in-progress': 'In Progress',
};
const SEV_COLOR = { critical: '#ef4444', high: '#f59e0b', medium: '#818cf8', low: '#a1a1aa', grc: '#10b981' };

export default function PipelineView({ T, backlog, search }) {
  const items = backlog.items || [];

  const grouped = useMemo(() => {
    const q = search ? search.toLowerCase() : '';
    const filtered = q
      ? items.filter(it => (it.id + ' ' + it.issue + ' ' + it.area + ' ' + it.stage).toLowerCase().includes(q))
      : items;
    const map = {};
    STAGE_ORDER.forEach(s => { map[s] = []; });
    filtered.forEach(it => {
      if (map[it.stage]) map[it.stage].push(it);
    });
    return map;
  }, [items, search]);

  return (
    <div style={{ flex: 1, overflowX: 'auto', display: 'flex', padding: 16, gap: 12, alignItems: 'flex-start' }}>
      {STAGE_ORDER.map(stage => (
        <div key={stage} style={{
          minWidth: 220, maxWidth: 260, background: T.panel, border: `1px solid ${T.border}`,
          borderRadius: 10, overflow: 'hidden', flexShrink: 0,
        }}>
          <div style={{
            padding: '10px 14px', borderBottom: `1px solid ${T.border}`,
            display: 'flex', alignItems: 'center', gap: 8,
          }}>
            <span style={{ fontSize: 12, fontWeight: 700, color: T.text }}>{STAGE_LABEL[stage]}</span>
            <span style={{
              fontSize: 10.5, fontWeight: 700, background: T.panel2, color: T.mute,
              padding: '1px 6px', borderRadius: 4,
            }}>{grouped[stage].length}</span>
          </div>
          <div style={{ padding: '8px 10px', display: 'flex', flexDirection: 'column', gap: 6 }}>
            {grouped[stage].map(it => (
              <div key={it.id} style={{
                background: T.panel2, border: `1px solid ${T.border}`, borderRadius: 7,
                padding: '8px 10px',
                borderLeft: `3px solid ${SEV_COLOR[it.severity] || T.border}`,
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                  <span style={{ fontSize: 10.5, fontWeight: 700, color: SEV_COLOR[it.severity] || T.mute }}>{it.id}</span>
                  <span style={{ fontSize: 10.5, color: T.mute }}>{it.area}</span>
                  <span style={{ marginLeft: 'auto', fontSize: 10, color: T.faint }}>{it.effort}</span>
                </div>
                <div style={{ fontSize: 12, color: T.text, lineHeight: 1.4 }}>{it.issue}</div>
              </div>
            ))}
            {grouped[stage].length === 0 && (
              <div style={{ color: T.faint, fontSize: 11, padding: '8px 4px' }}>No items</div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
