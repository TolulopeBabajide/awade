import React, { useMemo } from 'react';

const STATUS_DOT = { ok: '#10b981', fail: '#ef4444', warn: '#f59e0b', run: '#818cf8' };

// The four steps of the hourly dev loop in cron order
const HOURLY_STEPS = [
  { label: 'Dev',     agent: 'dev-agent',          minute: '00' },
  { label: 'Review',  agent: 'code-review-agent',  minute: '15' },
  { label: 'QA',      agent: 'qa-agent',           minute: '30' },
  { label: 'Refresh', agent: 'dashboard-refresh',  minute: '45' },
];

function HourlyLoopStrip({ T, events }) {
  const stepStatus = useMemo(() => {
    const out = {};
    for (const step of HOURLY_STEPS) {
      const ev = events.find(e => e.agent === step.agent && e.kind === 'run');
      out[step.agent] = ev ? { status: ev.status, ts: ev.ts } : null;
    }
    return out;
  }, [events]);

  return (
    <div style={{ padding: '12px 20px', borderBottom: `1px solid ${T.border}`, background: T.panel }}>
      <div style={{ fontSize: 11, fontWeight: 700, color: T.mute, textTransform: 'uppercase', letterSpacing: .06, marginBottom: 10 }}>
        Hourly loop
      </div>
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        {HOURLY_STEPS.map(step => {
          const ev = stepStatus[step.agent];
          const status = ev ? ev.status : 'idle';
          const dotColor = STATUS_DOT[status] || T.mute;
          const labelColor = status === 'fail' ? '#ef4444' : status === 'warn' ? '#f59e0b' : T.sub;
          return (
            <div key={step.agent} style={{
              display: 'flex', alignItems: 'center', gap: 7, padding: '6px 12px',
              background: T.panel2, border: `1px solid ${T.border}`,
              borderLeft: `3px solid ${dotColor}`,
              borderRadius: 7, minWidth: 130,
            }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                  <span style={{
                    width: 7, height: 7, borderRadius: '50%', flexShrink: 0,
                    background: dotColor,
                    boxShadow: status === 'fail' ? '0 0 0 3px rgba(239,68,68,.2)' : 'none',
                  }} />
                  <span style={{ fontSize: 11.5, fontWeight: 600, color: labelColor }}>{step.label}</span>
                  <span style={{ fontSize: 10, color: T.faint, marginLeft: 2 }}>:{step.minute}</span>
                </div>
                {ev ? (
                  <div style={{ fontSize: 10, color: T.faint, marginTop: 2, marginLeft: 12 }}>{ev.ts}</div>
                ) : (
                  <div style={{ fontSize: 10, color: T.faint, marginTop: 2, marginLeft: 12 }}>never ran</div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function PulseView({ T, events, stats, search }) {
  const filtered = useMemo(() => {
    if (!search) return events;
    const q = search.toLowerCase();
    return events.filter(e =>
      (e.agent + ' ' + e.task + ' ' + e.note + ' ' + e.status).toLowerCase().includes(q)
    );
  }, [events, search]);

  const fails24h = useMemo(() => events.filter(e => e.status === 'fail'), [events]);

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflowY: 'auto' }}>
      {/* Hourly-loop strip */}
      <HourlyLoopStrip T={T} events={events} />

      {/* KPI strip */}
      <div style={{
        display: 'flex', gap: 12, padding: '16px 20px', borderBottom: `1px solid ${T.border}`,
        background: T.panel, flexWrap: 'wrap',
      }}>
        {[
          { label: 'Runs / 24h', value: stats.runs24h, color: T.text },
          { label: 'Failures / 24h', value: fails24h.length, color: fails24h.length > 0 ? '#ef4444' : T.text },
          { label: 'Agents healthy', value: stats.agentsHealthy, color: '#10b981' },
          { label: 'Agents warning', value: stats.agentsWarning, color: stats.agentsWarning > 0 ? '#f59e0b' : T.mute },
          { label: 'Agents critical', value: stats.agentsCritical, color: stats.agentsCritical > 0 ? '#ef4444' : T.mute },
        ].map(({ label, value, color }) => (
          <div key={label} style={{ background: T.panel2, border: `1px solid ${T.border}`, borderRadius: 8, padding: '10px 16px', minWidth: 100 }}>
            <div style={{ fontSize: 10.5, color: T.mute, textTransform: 'uppercase', letterSpacing: .06, marginBottom: 4 }}>{label}</div>
            <div style={{ fontSize: 22, fontWeight: 700, color }}>{value}</div>
          </div>
        ))}
      </div>

      {/* Failure digest */}
      {fails24h.length > 0 && (
        <div style={{ padding: '14px 20px', borderBottom: `1px solid ${T.border}`, background: 'rgba(239,68,68,.04)' }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: '#ef4444', textTransform: 'uppercase', letterSpacing: .06, marginBottom: 10 }}>
            Failures in the last 24h
          </div>
          {fails24h.map((e, i) => (
            <div key={i} style={{ display: 'flex', gap: 10, padding: '6px 0', borderBottom: i < fails24h.length - 1 ? `1px solid ${T.border}` : 'none' }}>
              <span style={{ fontSize: 11, color: '#ef4444', flexShrink: 0 }}>✕</span>
              <span style={{ fontSize: 12, color: T.text, flex: 1 }}>{e.agent}</span>
              <span style={{ fontSize: 11, color: T.mute, flexShrink: 0 }}>{e.ts}</span>
              {e.note && <span style={{ fontSize: 11, color: T.mute, flex: 2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{e.note}</span>}
            </div>
          ))}
        </div>
      )}

      {/* Activity stream */}
      <div style={{ padding: '14px 20px' }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: T.mute, textTransform: 'uppercase', letterSpacing: .06, marginBottom: 10 }}>
          Activity stream
        </div>
        {filtered.slice(0, 100).map((e, i) => (
          <div key={i} style={{
            display: 'flex', gap: 10, padding: '5px 0', alignItems: 'center',
            borderBottom: `1px solid ${T.border}`,
          }}>
            <span style={{
              width: 7, height: 7, borderRadius: '50%', flexShrink: 0,
              background: STATUS_DOT[e.status] || T.mute,
            }} />
            <span style={{ fontSize: 11.5, color: T.sub, fontWeight: 600, flexShrink: 0, minWidth: 160 }}>{e.agent}</span>
            <span style={{ fontSize: 11, color: T.mute, flexShrink: 0, minWidth: 100 }}>{e.task}</span>
            <span style={{ fontSize: 11, color: T.faint, flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {e.note}
            </span>
            <span style={{ fontSize: 10.5, color: T.faint, flexShrink: 0 }}>{e.ts}</span>
          </div>
        ))}
        {filtered.length === 0 && (
          <div style={{ color: T.mute, fontSize: 12, padding: '20px 0' }}>
            {search ? 'No events match your search.' : 'No activity recorded yet.'}
          </div>
        )}
      </div>
    </div>
  );
}
