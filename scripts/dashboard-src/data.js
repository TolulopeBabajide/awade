// Adapts window.DASHBOARD_DATA (build-dashboard.py output) to the
// data model the React components expect.

// Task ID → agent name (mirrors build-dashboard.py TASK_AGENT)
const TASK_AGENT = {
  'security-scan': 'security-agent', 'daily-health-check': 'daily-health-check',
  'weekly-review': 'weekly-review', 'sprint-planning': 'sprint-planning',
  'content-calendar': 'content-agent', 'friday-finance': 'finance-agent',
  'nightly-monitor': 'nightly-monitor', 'weekend-ops': 'weekend-ops',
  'marketing-daily': 'marketing-agent', 'dev-execution': 'dev-agent',
  'qa-validation': 'qa-agent', 'analytics-daily': 'analytics-agent',
  'support-digest': 'support-agent', 'seo-weekly': 'seo-agent',
  'improvement-loop': 'improvement-agent', 'code-review-loop': 'code-review-agent',
  'performance-benchmark': 'performance-agent', 'architecture-review': 'architecture-agent',
  'tech-debt-audit': 'tech-debt-agent', 'dependency-security-scan': 'dependency-security-agent',
  'compliance-audit': 'compliance-agent', 'access-control-review': 'access-review-agent',
  'dashboard-refresh': 'dashboard-refresh',
};

const DEPT_DEFS = [
  { id: 'discovery', name: 'Discovery & Product', short: 'Product',
    members: ['discovery-agent', 'pm-agent', 'gtm-agent', 'onboarding-agent'] },
  { id: 'design', name: 'Design', short: 'Design',
    members: ['design-agent'] },
  { id: 'eng', name: 'Engineering', short: 'Eng',
    members: ['dev-agent', 'qa-agent', 'code-review-agent', 'devops-agent'] },
  { id: 'security', name: 'Security & Compliance', short: 'Security',
    members: ['security-agent', 'dependency-security-agent', 'access-review-agent', 'compliance-agent', 'legal-agent'] },
  { id: 'arch', name: 'Architecture & Quality', short: 'Arch',
    members: ['architecture-agent', 'performance-agent', 'tech-debt-agent', 'incident-response-agent'] },
  { id: 'growth', name: 'Growth & Marketing', short: 'Growth',
    members: ['marketing-agent', 'growth-agent', 'content-agent', 'seo-agent'] },
  { id: 'analytics', name: 'Analytics, Finance & Ops', short: 'Ops',
    members: ['analytics-agent', 'finance-agent', 'ops-agent'] },
  { id: 'cs', name: 'Customer Success', short: 'CS',
    members: ['support-agent'] },
  { id: 'orch', name: 'Orchestration & Monitoring', short: 'Orchestration',
    members: ['weekly-review', 'sprint-planning', 'improvement-agent', 'nightly-monitor', 'daily-health-check', 'weekend-ops', 'dashboard-refresh'] },
];

const AGENT_DEPT = {};
DEPT_DEFS.forEach(d => d.members.forEach(m => { AGENT_DEPT[m] = d; }));

function ageLabel(ageMin) {
  if (ageMin == null) return 'never';
  if (ageMin < 60) return `${ageMin}m`;
  if (ageMin < 1440) return `${Math.floor(ageMin / 60)}h ${ageMin % 60}m`;
  return `${Math.floor(ageMin / 1440)}d ${Math.floor((ageMin % 1440) / 60)}h`;
}

export function adaptData(raw) {
  // Build task lookup: agent name → task
  const agentTask = {};
  (raw.tasks || []).forEach(t => {
    const agent = TASK_AGENT[t.id];
    if (agent) agentTask[agent] = t;
  });

  const agents = (raw.agents || []).map(a => {
    const dept = AGENT_DEPT[a.name];
    const task = agentTask[a.name];
    return {
      name: a.name,
      dept: dept?.id || 'other',
      deptName: dept?.name || 'Other',
      scheduled: a.scheduled,
      runtime: a.runtime || '—',
      schedule: a.schedule || 'on-demand',
      cron: task?.cron || null,
      cadence: a.cadence || 'on-demand',
      taskId: task?.id || null,
      lastRun: ageLabel(a.ageMin),
      lastRunIso: a.lastRunIso || null,
      status: a.status || 'on-demand',
      runs24h: a.runs24h || 0,
      windowMin: a.windowMin || 0,
    };
  });

  const events = (raw.timeline || []).map((e, i) => ({
    id: String(i),
    ts: e.ts || '',
    unix: e.unix || 0,
    kind: e.kind || 'run',
    agent: e.agent || '',
    task: e.task || '',
    status: e.status || 'ok',
    note: e.note || '',
  }));

  const outputs = (raw.outputs || []).map(o => ({
    path: o.path || '',
    title: o.title || '',
    category: o.category || '',
    agent: o.agent || '',
    date: o.date || '',
    content: o.content || '',
    review: o.review || 'pending',
  }));

  const inbox = buildInbox(raw);

  const summary = raw.summary || {};
  const agentCounts = summary.agents || {};
  const stats = {
    status: summary.status || 'green',
    agentsTotal: agentCounts.total || agents.length,
    agentsHealthy: agentCounts.healthy || 0,
    agentsWarning: agentCounts.warning || 0,
    agentsCritical: agentCounts.critical || 0,
    agentsIdle: agentCounts.idle || 0,
    agentsOnDemand: agentCounts['on-demand'] || 0,
    agentsScheduled: agents.filter(a => a.scheduled).length,
    runs24h: summary.runs24h || 0,
    backlogOpen: (summary.backlog || {}).open || 0,
    backlogDone: (summary.backlog || {}).done || 0,
    alerts: summary.alerts || 0,
    generated: raw.generated || '',
    project: raw.project || 'Agentic Team',
    brief: raw.brief || null,
  };

  const backlog = raw.backlog || { items: [], severity: {}, stage: {}, done: 0 };
  const tasks = raw.tasks || [];
  const departments = buildDepartments(agents);

  return { agents, events, outputs, inbox, stats, backlog, tasks, departments };
}

function buildDepartments(agents) {
  const byName = Object.fromEntries(agents.map(a => [a.name, a]));
  return DEPT_DEFS.map(d => ({
    ...d,
    agents: d.members.map(name => byName[name]).filter(Boolean),
  }));
}

function buildInbox(raw) {
  const items = [];
  let idSeq = 0;
  const nextId = () => `inbox-${++idSeq}`;

  // 1. Critical backlog items
  const backlogItems = (raw.backlog || {}).items || [];
  for (const item of backlogItems) {
    if (item.severity === 'critical' && item.stage !== 'done') {
      const filePath = item.files
        ? item.files.replace(/`/g, '').split(',')[0].trim()
        : '';
      items.push({
        id: nextId(),
        kind: 'decide',
        urgency: 'high',
        title: `${item.id} — ${item.issue}`,
        detail: `Critical issue in ${item.area}. Stage: ${item.stage}. Effort: ${item.effort}. Review and decide next action.`,
        from: 'security-agent',
        via: 'security-scan',
        originPath: filePath,
        relatedBacklog: item.id,
        age: '—', est: '5 min', impact: 'Open Critical — blocks pipeline',
        actions: [
          { verb: 'View in backlog', prompt: `Show me issue ${item.id} in docs/agentic/backlog.md.`, primary: true },
          { verb: 'Mark resolved', prompt: `Mark backlog issue ${item.id} as done and move it to the Done section with stage=done.` },
        ],
      });
    }
  }

  // 2. Sync failures (push failures from the dev-agent)
  const syncFails = ((raw.alerts || {}).sync || []);
  for (const fail of syncFails.slice(0, 3)) {
    items.push({
      id: nextId(),
      kind: 'decide',
      urgency: 'high',
      title: `Sync failure — ${fail.agent || 'dev-agent'}`,
      detail: fail.note || 'A push to develop failed. Check .agent-health/sync-failures.log for details.',
      from: 'dev-agent',
      via: 'sync.sh',
      originPath: '.agent-health/sync-failures.log',
      relatedBacklog: null,
      age: '—', est: '10 min', impact: 'Git state diverged — dev loop may stall',
      actions: [
        { verb: 'View log', prompt: 'Show me .agent-health/sync-failures.log.', primary: true },
        { verb: 'Retry sync', prompt: 'Run ./scripts/sync.sh push "chore(sync): retry after failure" docs/ .claude/ to retry the failed push.' },
      ],
    });
  }

  // 3. MCP failures
  const mcpFails = ((raw.alerts || {}).mcp || []);
  for (const fail of mcpFails.slice(0, 2)) {
    items.push({
      id: nextId(),
      kind: 'decide',
      urgency: 'medium',
      title: `MCP unavailable — ${fail.tool || 'unknown tool'}`,
      detail: fail.note || 'An MCP tool was unreachable. The agent fell back to degraded mode.',
      from: fail.agent || 'unknown-agent',
      via: 'circuit-breaker.sh',
      originPath: '.agent-health/mcp-failures.log',
      relatedBacklog: null,
      age: '—', est: '5 min', impact: 'Agent running in degraded mode',
      actions: [
        { verb: 'View log', prompt: 'Show me .agent-health/mcp-failures.log.', primary: true },
      ],
    });
  }

  // 4. Recent outputs pending review (most recent 5)
  const pendingOutputs = (raw.outputs || []).filter(o => !o.review || o.review === 'pending').slice(0, 5);
  for (const out of pendingOutputs) {
    items.push({
      id: nextId(),
      kind: 'review',
      urgency: 'low',
      title: `${out.category} ready for review — ${out.title}`,
      detail: `${out.agent} produced this output. Review and approve before it moves downstream.`,
      from: out.agent || 'unknown-agent',
      via: out.category || 'scheduled run',
      originPath: out.path ? out.path.replace('../', 'docs/') : '',
      relatedBacklog: null,
      age: out.date || '—', est: '3 min', impact: 'Pending approval',
      content: out.content || '',
      actions: [
        { verb: 'Open output', prompt: `Open the output file at ${out.path}.`, primary: true },
        { verb: 'Approve', prompt: `Mark the output at ${out.path} as approved.`, color: 'green' },
      ],
    });
  }

  return items;
}
