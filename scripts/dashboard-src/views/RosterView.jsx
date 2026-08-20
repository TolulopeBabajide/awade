import React, { useState, useMemo } from 'react';
import { STATUS_COLOR } from '../theme.js';

const STATUS_LABEL = {
  healthy: 'Healthy', warning: 'Warning', critical: 'Critical',
  idle: 'Idle', 'on-demand': 'On-demand',
};

function AgentDot({ status, size = 8 }) {
  const color = STATUS_COLOR[status] || '#a1a1aa';
  return (
    <span style={{
      display: 'inline-block', width: size, height: size, borderRadius: '50%',
      background: color, flexShrink: 0,
      boxShadow: status === 'critical' ? `0 0 0 3px ${color}33` : 'none',
    }} />
  );
}

function AgentCard({ T, agent, onClick, selected }) {
  return (
    <div onClick={() => onClick && onClick(agent)} style={{
      display: 'flex', alignItems: 'center', gap: 10, padding: '8px 10px',
      borderRadius: 6,
      border: `1px solid ${selected ? T.accentBorder : T.border}`,
      background: selected ? T.selectedBg : T.panel2,
      cursor: 'pointer', marginBottom: 4,
    }}>
      <AgentDot status={agent.status} />
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 12, fontWeight: 600, color: T.text, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {agent.name}
        </div>
        <div style={{ fontSize: 10.5, color: T.mute }}>
          {agent.schedule} · {agent.lastRun}
        </div>
      </div>
      <div style={{ fontSize: 10, color: STATUS_COLOR[agent.status] || T.mute, fontWeight: 600, flexShrink: 0 }}>
        {agent.runs24h > 0 ? `${agent.runs24h}/24h` : '—'}
      </div>
    </div>
  );
}

function DeptCard({ T, dept, agentFilter, search, onSelectAgent, selectedAgent }) {
  const agents = dept.agents.filter(a => {
    if (agentFilter !== 'all' && a.status !== agentFilter) return false;
    if (search) {
      const q = search.toLowerCase();
      if (!(a.name + ' ' + dept.name + ' ' + a.schedule).toLowerCase().includes(q)) return false;
    }
    return true;
  });
  if (agents.length === 0) return null;

  const worstStatus = agents.some(a => a.status === 'critical') ? 'critical'
    : agents.some(a => a.status === 'warning') ? 'warning'
    : 'healthy';

  return (
    <div style={{
      background: T.panel, border: `1px solid ${T.border}`, borderRadius: 10, padding: '14px 14px',
      borderTop: `3px solid ${STATUS_COLOR[worstStatus] || T.border}`,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
        <AgentDot status={worstStatus} size={7} />
        <span style={{ fontSize: 12, fontWeight: 700, color: T.text }}>{dept.short}</span>
        <span style={{ fontSize: 10.5, color: T.mute, flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {dept.name}
        </span>
        <span style={{ fontSize: 10.5, color: T.mute }}>{agents.length}</span>
      </div>
      {agents.map(a => (
        <AgentCard
          key={a.name}
          T={T}
          agent={a}
          onClick={onSelectAgent}
          selected={selectedAgent?.name === a.name}
        />
      ))}
    </div>
  );
}

function AgentDetail({ T, agent, events, liveMode, onClose, onToast }) {
  const recentRuns = useMemo(() =>
    (events || []).filter(e => e.agent === agent.name).slice(-5).reverse(),
    [events, agent.name]
  );

  function copyPrompt(prompt) {
    navigator.clipboard.writeText(prompt)
      .then(() => onToast && onToast('Copied'))
      .catch(() => {});
  }

  function handleAction(action) {
    if (liveMode && action.api) {
      fetch('/api/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(action.api),
      }).then(() => onToast && onToast('Sent')).catch(() => copyPrompt(action.prompt));
    } else if (action.prompt) {
      copyPrompt(action.prompt);
    }
  }

  const actions = [
    {
      verb: 'Run agent',
      prompt: `Run the ${agent.name} agent now. Use the skill at .claude/skills/${agent.name}/SKILL.md.`,
      api: { type: 'request', agent: agent.name, action: 'run' },
      primary: true,
    },
    {
      verb: 'View skill',
      prompt: `Show me the SKILL.md for ${agent.name} at .claude/skills/${agent.name}/SKILL.md.`,
    },
  ];

  const statusColor = STATUS_COLOR[agent.status] || '#a1a1aa';

  const metaRows = [
    ['Status', <span style={{ color: statusColor, fontWeight: 600 }}>{STATUS_LABEL[agent.status] || agent.status}</span>],
    ['Schedule', agent.schedule],
    ['Last run', agent.lastRun],
    ['Runs / 24h', agent.runs24h > 0 ? String(agent.runs24h) : '—'],
  ];
  if (agent.cron) {
    metaRows.push(['Cron', <span style={{ fontFamily: 'monospace', fontSize: 10.5 }}>{agent.cron}</span>]);
  }

  return (
    <div style={{
      width: 296, flexShrink: 0, borderLeft: `1px solid ${T.border}`,
      display: 'flex', flexDirection: 'column', background: T.panel, overflow: 'hidden',
    }}>
      {/* Header */}
      <div style={{ padding: '14px 16px', borderBottom: `1px solid ${T.border}`, display: 'flex', alignItems: 'center', gap: 10 }}>
        <AgentDot status={agent.status} size={10} />
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: T.text, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {agent.name}
          </div>
          <div style={{ fontSize: 11, color: T.mute }}>{agent.deptName}</div>
        </div>
        <button onClick={onClose} style={{
          background: 'none', border: 'none', color: T.mute, cursor: 'pointer',
          fontSize: 18, padding: '0 4px', lineHeight: 1,
        }}>×</button>
      </div>

      {/* Meta rows */}
      <div style={{ padding: '12px 16px', borderBottom: `1px solid ${T.border}` }}>
        {metaRows.map(([label, value]) => (
          <div key={label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <span style={{ fontSize: 11.5, color: T.mute }}>{label}</span>
            <span style={{ fontSize: 11.5, color: T.text }}>{value}</span>
          </div>
        ))}
      </div>

      {/* Recent activity */}
      {recentRuns.length > 0 && (
        <div style={{ padding: '12px 16px', borderBottom: `1px solid ${T.border}` }}>
          <div style={{ fontSize: 10.5, fontWeight: 700, color: T.sub, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 8 }}>
            Recent runs
          </div>
          {recentRuns.map((run, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
              <span style={{
                width: 6, height: 6, borderRadius: '50%', flexShrink: 0,
                background: run.status === 'fail' ? '#ef4444' : run.status === 'ok' ? '#22c55e' : '#a1a1aa',
              }} />
              <span style={{ fontSize: 11, color: T.mute, flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {run.ts || run.task}
              </span>
              <span style={{
                fontSize: 10, fontWeight: run.status === 'fail' ? 600 : 400,
                color: run.status === 'fail' ? '#ef4444' : T.faint,
              }}>
                {run.status}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Actions */}
      <div style={{ padding: '12px 16px' }}>
        <div style={{ fontSize: 10.5, fontWeight: 700, color: T.sub, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 8 }}>
          Actions {!liveMode && <span style={{ color: T.faint, fontWeight: 400, textTransform: 'none', letterSpacing: 0 }}>— copies prompt</span>}
        </div>
        {actions.map(a => (
          <button key={a.verb} onClick={() => handleAction(a)} style={{
            display: 'block', width: '100%', marginBottom: 6,
            padding: '7px 12px', borderRadius: 6, cursor: 'pointer', fontSize: 12,
            fontWeight: a.primary ? 600 : 400, textAlign: 'left',
            background: a.primary ? T.accent : T.panel2,
            color: a.primary ? '#fff' : T.text,
            border: `1px solid ${a.primary ? T.accentBorder : T.border}`,
          }}>
            {a.primary ? '▶ ' : ''}{a.verb}
          </button>
        ))}
      </div>
    </div>
  );
}

export default function RosterView({ T, departments, agentsCritical, agentsWarning, agentsHealthy, search, events, liveMode, onToast }) {
  const [agentFilter, setAgentFilter] = useState('all');
  const [selectedAgent, setSelectedAgent] = useState(null);
  const statusFilters = ['all', 'healthy', 'warning', 'critical', 'idle', 'on-demand'];

  function onSelectAgent(agent) {
    setSelectedAgent(prev => prev?.name === agent.name ? null : agent);
  }

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      {/* Status filter strip */}
      <div style={{ display: 'flex', gap: 6, padding: '12px 16px', borderBottom: `1px solid ${T.border}`, background: T.panel, flexWrap: 'wrap' }}>
        {statusFilters.map(f => (
          <div key={f} onClick={() => setAgentFilter(f)} style={{
            padding: '4px 12px', borderRadius: 6, cursor: 'pointer', fontSize: 12, fontWeight: 500,
            background: agentFilter === f ? T.selectedBg : T.panel2,
            color: agentFilter === f ? T.accent : T.sub,
            border: `1px solid ${agentFilter === f ? T.accentBorder : T.border}`,
          }}>
            {f.charAt(0).toUpperCase() + f.slice(1)}
            {f === 'critical' && agentsCritical > 0 && (
              <span style={{ marginLeft: 5, color: '#ef4444', fontWeight: 700 }}>{agentsCritical}</span>
            )}
            {f === 'warning' && agentsWarning > 0 && (
              <span style={{ marginLeft: 5, color: '#f59e0b', fontWeight: 700 }}>{agentsWarning}</span>
            )}
          </div>
        ))}
      </div>

      {/* Main area: dept grid + optional agent detail pane */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        <div style={{
          flex: 1, overflowY: 'auto', padding: 16,
          display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
          gap: 12, alignContent: 'start',
        }}>
          {departments.map(dept => (
            <DeptCard
              key={dept.id}
              T={T}
              dept={dept}
              agentFilter={agentFilter}
              search={search}
              onSelectAgent={onSelectAgent}
              selectedAgent={selectedAgent}
            />
          ))}
        </div>

        {selectedAgent && (
          <AgentDetail
            T={T}
            agent={selectedAgent}
            events={events || []}
            liveMode={liveMode}
            onClose={() => setSelectedAgent(null)}
            onToast={onToast}
          />
        )}
      </div>
    </div>
  );
}
