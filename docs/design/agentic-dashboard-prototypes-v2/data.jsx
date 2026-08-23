// Mock data — GROUNDED to the actual agentic team template.
// Every agent, schedule, cron, runtime is sourced from docs/SCHEDULED-TASKS.md
// and README.md. Inbox items are real-looking artifacts that the agents
// actually write to disk — each carries an originPath the founder can open.

/* ──────────────────────────────────────────────────────────────────────
   1. Scheduled tasks (verbatim from docs/SCHEDULED-TASKS.md)
   ────────────────────────────────────────────────────────────────────── */
const SCHEDULED_TASKS = [
  { num:1,  id:'security-scan',             agent:'security-agent',           cron:'0 6 * * *',     schedule:'Daily 6am',                runtime:'Claude Code', cadence:'daily',     desc:'OWASP Web + LLM Top 10 audit. Auto-adds Critical findings to backlog.' },
  { num:2,  id:'daily-health-check',        agent:'daily-health-check',       cron:'0 8 * * 1-5',   schedule:'Weekdays 8am',             runtime:'Cowork',      cadence:'weekdays',  desc:'Morning code health scan — type check, lint, tests, CI, open blockers.' },
  { num:3,  id:'weekly-review',             agent:'weekly-review',            cron:'0 9 * * 1',     schedule:'Mondays 9am',              runtime:'Cowork',      cadence:'weekly',    desc:'Full department status report.' },
  { num:4,  id:'sprint-planning',           agent:'sprint-planning',          cron:'30 9 * * 1',    schedule:'Mondays 9:30am',           runtime:'Cowork',      cadence:'weekly',    desc:'Selects this week\u2019s backlog issues after the weekly review.' },
  { num:5,  id:'content-calendar',          agent:'content-agent',            cron:'0 9 * * 3',     schedule:'Wednesdays 9am',           runtime:'Cowork',      cadence:'weekly',    desc:'Weekly social content plan for the upcoming week.' },
  { num:6,  id:'friday-finance',            agent:'finance-agent',            cron:'0 17 * * 5',    schedule:'Fridays 5pm',              runtime:'Cowork',      cadence:'weekly',    desc:'Weekly MRR / burn / runway / unit-economics snapshot.' },
  { num:7,  id:'nightly-monitor',           agent:'nightly-monitor',          cron:'0 23 * * *',    schedule:'Daily 11pm',               runtime:'Cowork',      cadence:'daily',     desc:'End-of-day health scan. Writes morning-brief.md.' },
  { num:8,  id:'weekend-ops',               agent:'weekend-ops',              cron:'0 10 * * 6',    schedule:'Saturdays 10am',           runtime:'Cowork',      cadence:'weekly',    desc:'Weekly retro + backlog grooming + Monday prep.' },
  { num:9,  id:'marketing-daily',           agent:'marketing-agent',          cron:'0 15 * * 1-5',  schedule:'Weekdays 3pm',             runtime:'Cowork',      cadence:'weekdays',  desc:'One publish-ready piece every weekday afternoon.' },
  { num:10, id:'dev-execution',             agent:'dev-agent',                cron:'0 * * * *',     schedule:'Hourly :00',               runtime:'Claude Code', cadence:'hourly',    desc:'Picks top backlog item, ships it. Self-skips if recent commit or CI red.' },
  { num:11, id:'qa-validation',             agent:'qa-agent',                 cron:'30 * * * *',   schedule:'Hourly :30',               runtime:'Claude Code', cadence:'hourly',    desc:'Validates what dev shipped, checks CI, auto-files failures.' },
  { num:12, id:'analytics-daily',           agent:'analytics-agent',          cron:'0 16 * * 1-5',  schedule:'Weekdays 4pm',             runtime:'Cowork',      cadence:'weekdays',  desc:'Tracks north star + key inputs, flags anomalies.' },
  { num:13, id:'support-digest',            agent:'support-agent',            cron:'0 9 * * 2,4',   schedule:'Tue/Thu 9am',              runtime:'Cowork',      cadence:'biweekly',  desc:'Synthesises support messages; surfaces escalations + patterns.' },
  { num:14, id:'seo-weekly',                agent:'seo-agent',                cron:'0 9 * * 5',     schedule:'Fridays 9am',              runtime:'Cowork',      cadence:'weekly',    desc:'Tracks rankings, flags pages losing traffic.' },
  { num:15, id:'improvement-loop',          agent:'improvement-agent',        cron:'0 */3 * * *',   schedule:'Every 3 hours',            runtime:'Cowork',      cadence:'hourly',    desc:'The system improves itself — implements top ready item from improvement-backlog.' },
  { num:16, id:'code-review-loop',          agent:'code-review-agent',        cron:'15 * * * *',   schedule:'Hourly :15',               runtime:'Claude Code', cadence:'hourly',    desc:'Structural review on every new commit — SOLID, complexity, security.' },
  { num:17, id:'performance-benchmark',     agent:'performance-agent',        cron:'0 7 * * 1',     schedule:'Mondays 7am',              runtime:'Cowork',      cadence:'weekly',    desc:'Weekly perf audit — API, bundle, N+1, deps, RUM.' },
  { num:18, id:'architecture-review',       agent:'architecture-agent',       cron:'0 7 * * 2',     schedule:'Tuesdays 7am · biweekly',  runtime:'Cowork',      cadence:'biweekly',  desc:'Drift detection, ADR log, tech-debt clusters, codebase-map sync.' },
  { num:19, id:'tech-debt-audit',           agent:'tech-debt-agent',          cron:'0 7 * * 5',     schedule:'Fridays 7am',              runtime:'Cowork',      cadence:'weekly',    desc:'Catalogue debt by churn + size + coverage gaps. Files Tier 1 wins.' },
  { num:20, id:'dependency-security-scan',  agent:'dependency-security-agent',cron:'30 6 * * 3',    schedule:'Wednesdays 6:30am',        runtime:'Cowork',      cadence:'weekly',    desc:'CVE scan + license audit + SBOM snapshot.' },
  { num:21, id:'compliance-audit',          agent:'compliance-agent',         cron:'30 6 1-7 * 1',  schedule:'1st Mon of month 6:30am',  runtime:'Cowork',      cadence:'monthly',   desc:'GDPR/CCPA/PII/retention. GRC-## prefix.' },
  { num:22, id:'access-control-review',     agent:'access-review-agent',      cron:'30 6 1-7 * 2',  schedule:'1st Tue of month 6:30am',  runtime:'Cowork',      cadence:'monthly',   desc:'Route auth + agent-permissions.json + key rotation + IDOR.' },
  { num:23, id:'dashboard-refresh',         agent:'dashboard-refresh',        cron:'45 * * * *',   schedule:'Hourly :45',               runtime:'Cowork',      cadence:'hourly',    desc:'Rebuilds this dashboard from heartbeats + logs + backlog + outputs.' },
];

/* ──────────────────────────────────────────────────────────────────────
   2. Departments (verbatim from README.md)
   ────────────────────────────────────────────────────────────────────── */
const DEPARTMENTS = [
  { id:'discovery', name:'Discovery & Product',          short:'Product', agents:['discovery-agent','pm-agent','gtm-agent','onboarding-agent'] },
  { id:'design',    name:'Design',                       short:'Design',  agents:['design-agent'] },
  { id:'eng',       name:'Engineering',                  short:'Eng',     agents:['dev-agent','qa-agent','code-review-agent','devops-agent'] },
  { id:'security',  name:'Security & Compliance',        short:'Security',agents:['security-agent','dependency-security-agent','access-review-agent','compliance-agent','legal-agent'] },
  { id:'arch',      name:'Architecture & Quality',       short:'Arch',    agents:['architecture-agent','performance-agent','tech-debt-agent','incident-response-agent'] },
  { id:'growth',    name:'Growth & Marketing',           short:'Growth',  agents:['marketing-agent','growth-agent','content-agent','seo-agent'] },
  { id:'analytics', name:'Analytics, Finance & Ops',     short:'Ops',     agents:['analytics-agent','finance-agent','ops-agent'] },
  { id:'cs',        name:'Customer Success',             short:'CS',      agents:['support-agent'] },
  { id:'orch',      name:'Orchestration & Monitoring',   short:'Orchestration', agents:['weekly-review','sprint-planning','improvement-agent','nightly-monitor','daily-health-check','weekend-ops','dashboard-refresh'] },
];

/* ──────────────────────────────────────────────────────────────────────
   3. Build agent roster from departments + scheduled-task index.
   On-demand agents have no scheduled task — there are exactly 10:
   discovery, pm, gtm, onboarding, design, devops, legal,
   incident-response, growth, ops.
   ────────────────────────────────────────────────────────────────────── */
const TASK_BY_AGENT = Object.fromEntries(SCHEDULED_TASKS.map(t => [t.agent, t]));

// Last-run mtimes (simulated — in the real system these come from
// .agent-health/<name>.last-run). Picked to give a healthy / busy state with
// a couple of warnings.
const LAST_RUN_AGE = {
  'security-agent':            '5h 12m',
  'daily-health-check':        '3h 41m',
  'weekly-review':             '1d 4h',
  'sprint-planning':           '1d 4h',
  'content-agent':             '2d 5h',          // last ran at content-calendar Wed
  'finance-agent':             '3d 8h',
  'nightly-monitor':           '11h 14m',
  'weekend-ops':               '4d 22h',
  'marketing-agent':           '21h 36m',
  'dev-agent':                 '11m',
  'qa-agent':                  '41m',
  'analytics-agent':           '20h 8m',
  'support-agent':             '18h 23m',
  'seo-agent':                 '4d 1h',
  'improvement-agent':         '1h 12m',
  'code-review-agent':         '26m',
  'performance-agent':         '1d 6h',
  'architecture-agent':        '8d 6h',
  'tech-debt-agent':           '3d 7h',
  'dependency-security-agent': '1d 6h',
  'compliance-agent':          '21d',
  'access-review-agent':       '18d',
  'dashboard-refresh':         '8m',
  // on-demand
  'discovery-agent':           '2h 14m',
  'pm-agent':                  '1h 47m',
  'gtm-agent':                 '6d 4h',
  'onboarding-agent':          '12d',
  'design-agent':              '6h 22m',
  'devops-agent':              '4h 56m',
  'legal-agent':               '9d 3h',
  'incident-response-agent':   'never',
  'growth-agent':              '3d 11h',
  'ops-agent':                 '1d 4h',
};

// Status: derive from cadence vs. last-run age.
// healthy = ran inside its window; warning = overdue by < 2x window;
// critical = overdue by > 2x; idle = scheduled but window is very long
// (monthly/biweekly) and hasn't fired yet this cycle. on-demand = no schedule.
const AGENT_STATUS_OVERRIDES = {
  'code-review-agent': 'warning',  // filed an H-## on its last run
  'tech-debt-agent':   'warning',  // surfaced a Tier-1 cluster waiting on a decision
  'support-agent':     'warning',  // 2 escalations pending
};
function statusOf(name, hasTask){
  if (!hasTask) return 'on-demand';
  if (AGENT_STATUS_OVERRIDES[name]) return AGENT_STATUS_OVERRIDES[name];
  const task = TASK_BY_AGENT[name];
  const cadence = task.cadence;
  if (cadence === 'monthly' || cadence === 'biweekly') return 'idle'; // long window, no fresh action
  if (cadence === 'weekly') {
    const age = LAST_RUN_AGE[name] || '';
    if (/^\d+d/.test(age) && parseInt(age) > 7) return 'warning';
    return 'healthy';
  }
  return 'healthy';
}

const AGENTS = DEPARTMENTS.flatMap(d => d.agents.map(name => {
  const task = TASK_BY_AGENT[name];
  const hasTask = !!task;
  return {
    name,
    dept: d.id,
    deptName: d.name,
    scheduled: hasTask,
    runtime: hasTask ? task.runtime : '\u2014',
    schedule: hasTask ? task.schedule : 'on-demand',
    cron: hasTask ? task.cron : null,
    cadence: hasTask ? task.cadence : 'on-demand',
    taskId: hasTask ? task.id : null,
    lastRun: LAST_RUN_AGE[name] || 'never',
    status: statusOf(name, hasTask),
  };
}));
const AGENT_BY_NAME = Object.fromEntries(AGENTS.map(a => [a.name, a]));

/* ──────────────────────────────────────────────────────────────────────
   4. INBOX — the union of real artifacts that need the founder.
   Each item carries:
     - originPath: the file the agent wrote to disk
     - via: the scheduled task that produced it
     - actions: each has a `prompt` (paste into Claude) and an `api`
                payload (POSTed to /api/action when dashboard-server.py runs)
   ────────────────────────────────────────────────────────────────────── */
const INBOX = [

  /* Source: docs/sprints/qa-log.md last entry == STOP — explicit founder gate */
  {
    id: 'inbox-qa-stop',
    kind: 'decide',
    urgency: 'high',
    title: 'QA verdict STOP — dev loop is paused',
    detail: 'qa-validation found a regression in /api/users strict-null. Filed H-128 in backlog. dev-execution at :00 will refuse to start new work until this clears.',
    from: 'qa-agent',
    via: 'qa-validation @ :30',
    originPath: 'docs/sprints/qa-log.md',
    relatedBacklog: 'H-128',
    age: '14m', est: '5 min', impact: 'Blocks every :00 dev run',
    actions: [
      { verb:'Open log',         prompt:'Show me the last QA entry from docs/sprints/qa-log.md.', api:{type:'open',path:'docs/sprints/qa-log.md'}, primary:true },
      { verb:'Fix H-128 now',    prompt:'Fix issue H-128.', api:{type:'request',action:'implement',target:'H-128'}, color:'green' },
      { verb:'Override STOP',    prompt:'Override the QA STOP verdict in docs/sprints/qa-log.md and let dev-execution resume.', api:{type:'qa-override'} },
    ],
  },

  /* Source: docs/audits/security-report-[DATE].md — Critical finding writes C-## */
  {
    id: 'inbox-c-12',
    kind: 'decide',
    urgency: 'high',
    title: 'C-12 — Rotate expired GCP service-account key',
    detail: 'security-scan flagged a key past its 90d window. Founder action required: rotate the credential, then security-agent can mark resolved. No secret value in the report.',
    from: 'security-agent',
    via: 'security-scan @ 06:00',
    originPath: 'docs/audits/security-report-2026-05-22.md',
    relatedBacklog: 'C-12',
    age: '6h 22m', est: '8 min', impact: 'Open Critical — blocks compliance audit',
    actions: [
      { verb:'Open report',      prompt:'Show me docs/audits/security-report-2026-05-22.md.', api:{type:'open',path:'docs/audits/security-report-2026-05-22.md'}, primary:true },
      { verb:'I rotated it',     prompt:'I rotated the GCP key. Mark backlog issue C-12 done — move it to the Done section with stage=done.', api:{type:'backlog-done',id:'C-12'}, color:'green' },
      { verb:'Snooze 24h',       prompt:'Snooze backlog issue C-12 for 24 hours.', api:{type:'backlog-snooze',id:'C-12',until:'24h'} },
    ],
  },

  /* Source: docs/content/drafts/[YYYY-MM-DD]-[platform].md — marketing-daily output */
  {
    id: 'inbox-content-linkedin',
    kind: 'approve',
    urgency: 'high',
    title: 'LinkedIn post drafted for v2.4 launch',
    detail: 'marketing-daily wrote a thread-style post tied to today\u2019s content pillar. Tone follows the brand voice in project-config.md §brand. Pre-cleared by marketing-agent.',
    from: 'marketing-agent',
    via: 'marketing-daily @ 15:02',
    originPath: 'docs/content/drafts/2026-05-22-linkedin.md',
    age: '12m', est: '2 min', impact: 'Blocks Tuesday launch window',
    actions: [
      { verb:'Open draft',       prompt:'Show me docs/content/drafts/2026-05-22-linkedin.md.', api:{type:'open',path:'docs/content/drafts/2026-05-22-linkedin.md'}, primary:true },
      { verb:'Approve & log',    prompt:'Approve docs/content/drafts/2026-05-22-linkedin.md — append an Approved row to docs/content/content-log.md.', api:{type:'output-approve',path:'docs/content/drafts/2026-05-22-linkedin.md'}, color:'green' },
      { verb:'Revise',           prompt:'Rewrite docs/content/drafts/2026-05-22-linkedin.md with these changes: ', api:null },
      { verb:'Reject',           prompt:'Reject docs/content/drafts/2026-05-22-linkedin.md — delete it and log a Rejected row in docs/content/content-log.md.', api:{type:'output-reject',path:'docs/content/drafts/2026-05-22-linkedin.md'}, color:'red' },
    ],
  },

  /* Source: docs/sprint-plans/sprint-[DATE].md § "Decisions needed from founder" */
  {
    id: 'inbox-sprint-decisions',
    kind: 'decide',
    urgency: 'medium',
    title: 'Sprint plan ready — 3 founder decisions inside',
    detail: 'sprint-planning has 12 items at 34 pts queued. Three are blocked on you: pricing-tier call, /billing refactor scope, and whether to promote H-119 over H-118.',
    from: 'sprint-planning',
    via: 'sprint-planning @ 09:30 Mon',
    originPath: 'docs/sprint-plans/sprint-2026-05-18.md',
    age: '1d 4h', est: '10 min', impact: 'Sprint starts when these clear',
    actions: [
      { verb:'Open plan',        prompt:'Show me docs/sprint-plans/sprint-2026-05-18.md.', api:{type:'open',path:'docs/sprint-plans/sprint-2026-05-18.md'}, primary:true },
      { verb:'Accept plan',      prompt:'Acknowledge docs/sprint-plans/sprint-2026-05-18.md as approved.', api:{type:'output-approve',path:'docs/sprint-plans/sprint-2026-05-18.md'}, color:'green' },
      { verb:'Send back',        prompt:'Rewrite docs/sprint-plans/sprint-2026-05-18.md addressing these concerns: ', api:null },
    ],
  },

  /* Source: docs/support/digest-[DATE].md § "Escalations Pending" */
  {
    id: 'inbox-support-escalations',
    kind: 'respond',
    urgency: 'medium',
    title: '2 customer threads need your voice',
    detail: 'Enterprise lead asking about SSO timeline; second is a renewal at risk. support-agent did not draft responses (per its SKILL.md it surfaces only — drafts on demand).',
    from: 'support-agent',
    via: 'support-digest @ Tue 09:00',
    originPath: 'docs/support/digest-2026-05-21.md',
    age: '18h', est: '6 min', impact: '1 renewal at risk',
    actions: [
      { verb:'Open digest',      prompt:'Show me docs/support/digest-2026-05-21.md.', api:{type:'open',path:'docs/support/digest-2026-05-21.md'}, primary:true },
      { verb:'Draft replies',    prompt:'Draft replies for the two escalations in docs/support/digest-2026-05-21.md.', api:{type:'request',action:'draft',target:'support-replies'}, color:'green' },
    ],
  },

  /* Source: docs/architecture/arch-review-[DATE].md — bi-weekly */
  {
    id: 'inbox-arch-h-127',
    kind: 'review',
    urgency: 'medium',
    title: 'H-127 — BillingFlow.tsx complexity 18 (refactor required)',
    detail: 'code-review-loop scored BillingFlow.tsx at 🛑 Refactor Required. Architecture call needed before dev-agent picks it up — split into hooks or extract submachine?',
    from: 'code-review-agent',
    via: 'code-review-loop @ :15',
    originPath: 'docs/code-reviews/review-2026-05-22-a1b2c3d.md',
    relatedBacklog: 'H-127',
    age: '26m', est: '5 min', impact: '2 PRs queued behind this',
    actions: [
      { verb:'Open review',      prompt:'Show me docs/code-reviews/review-2026-05-22-a1b2c3d.md.', api:{type:'open',path:'docs/code-reviews/review-2026-05-22-a1b2c3d.md'}, primary:true },
      { verb:'Send to dev',      prompt:'Move backlog issue H-127 to stage=ready so the dev-agent picks it up.', api:{type:'backlog-stage',id:'H-127',stage:'ready'}, color:'green' },
      { verb:'Move to define',   prompt:'Move backlog issue H-127 to stage=define and write a refactor spec.', api:{type:'backlog-stage',id:'H-127',stage:'define'} },
    ],
  },

  /* Source: docs/legal/compliance-audit-[DATE].md — monthly */
  {
    id: 'inbox-grc-08',
    kind: 'review',
    urgency: 'medium',
    title: 'GRC-08 — Cookie consent banner missing for EU users',
    detail: 'compliance-audit on the 1st Mon found tracking scripts firing pre-consent. Flagged 🔴 under GDPR. Needs spec before dev — what regions, which scripts, which CMP.',
    from: 'compliance-agent',
    via: 'compliance-audit · 1st Mon',
    originPath: 'docs/legal/compliance-audit-2026-05-04.md',
    relatedBacklog: 'GRC-08',
    age: '18d', est: '12 min', impact: 'Regulatory exposure',
    actions: [
      { verb:'Open audit',       prompt:'Show me docs/legal/compliance-audit-2026-05-04.md.', api:{type:'open',path:'docs/legal/compliance-audit-2026-05-04.md'}, primary:true },
      { verb:'Approve scope',    prompt:'Move backlog issue GRC-08 to stage=ready with this scope: ', api:null, color:'green' },
    ],
  },

  /* Source: docs/finance/snapshot-[DATE].md */
  {
    id: 'inbox-finance-approval',
    kind: 'approve',
    urgency: 'medium',
    title: 'Approve Q3 spend on observability stack',
    detail: 'finance-agent priced three tools at $840/mo combined. Cheaper bundled plan available at $520/mo if you sign before Friday.',
    from: 'finance-agent',
    via: 'friday-finance @ 17:00',
    originPath: 'docs/finance/snapshot-2026-05-16.md',
    age: '3d', est: '3 min', impact: 'Renewal lapses Friday',
    actions: [
      { verb:'Open snapshot',    prompt:'Show me docs/finance/snapshot-2026-05-16.md.', api:{type:'open',path:'docs/finance/snapshot-2026-05-16.md'}, primary:true },
      { verb:'Approve $520',     prompt:'Approve the $520/mo bundled observability plan in docs/finance/snapshot-2026-05-16.md.', api:{type:'output-approve',path:'docs/finance/snapshot-2026-05-16.md'}, color:'green' },
      { verb:'Decline',          prompt:'Decline the observability renewal in docs/finance/snapshot-2026-05-16.md.', api:{type:'output-reject',path:'docs/finance/snapshot-2026-05-16.md'}, color:'red' },
    ],
  },

  /* Source: docs/discovery/queue.md — fed by analytics-daily anomaly */
  {
    id: 'inbox-discovery-activation',
    kind: 'review',
    urgency: 'low',
    title: 'Activation \u201322% day-over-day — discovery queue updated',
    detail: 'analytics-daily flagged a 22% drop on yesterday\u2019s activation. Filed in discovery queue with source=analytics. discovery-agent will pick it up on demand.',
    from: 'analytics-agent',
    via: 'analytics-daily @ 16:00',
    originPath: 'docs/discovery/queue.md',
    age: '20h', est: '4 min', impact: 'Signal — not yet a blocker',
    actions: [
      { verb:'Open queue',       prompt:'Show me docs/discovery/queue.md.', api:{type:'open',path:'docs/discovery/queue.md'}, primary:true },
      { verb:'Run discovery now',prompt:'Run the discovery-agent now to investigate the activation drop in docs/discovery/queue.md.', api:{type:'request',action:'run',target:'discovery-agent'}, color:'green' },
    ],
  },

  /* Source: docs/weekly-reviews/review-[DATE].md */
  {
    id: 'inbox-weekly-review',
    kind: 'approve',
    urgency: 'low',
    title: 'Weekly review ready — ack to clear',
    detail: 'weekly-review compiled the dept rollup from dev-log, qa-log, audits, content-log, and the last 7 days of CI runs.',
    from: 'weekly-review',
    via: 'weekly-review @ 09:00 Mon',
    originPath: 'docs/weekly-reviews/review-2026-05-18.md',
    age: '1d', est: '5 min', impact: 'Informational',
    actions: [
      { verb:'Open review',      prompt:'Show me docs/weekly-reviews/review-2026-05-18.md.', api:{type:'open',path:'docs/weekly-reviews/review-2026-05-18.md'}, primary:true },
      { verb:'Acknowledge',      prompt:'Acknowledge docs/weekly-reviews/review-2026-05-18.md.', api:{type:'output-approve',path:'docs/weekly-reviews/review-2026-05-18.md'}, color:'green' },
    ],
  },
];

/* ──────────────────────────────────────────────────────────────────────
   5. Outputs — full list of recent reviewable artifacts.
   Maps 1:1 to the markdown files the agents write per SCHEDULED-TASKS.md.
   ────────────────────────────────────────────────────────────────────── */
const OUTPUTS = [
  { group:'Content',          path:'docs/content/drafts/2026-05-22-linkedin.md',     agent:'marketing-agent',           via:'marketing-daily',          age:'12m',   review:'pending' },
  { group:'Content',          path:'docs/content/drafts/2026-05-21-twitter.md',      agent:'marketing-agent',           via:'marketing-daily',          age:'1d',    review:'approved' },
  { group:'Content',          path:'docs/content/content-calendar-2026-05-20.md',    agent:'content-agent',             via:'content-calendar',         age:'2d',    review:'approved' },
  { group:'Plans',            path:'docs/sprint-plans/sprint-2026-05-18.md',         agent:'sprint-planning',           via:'sprint-planning',          age:'1d 4h', review:'pending' },
  { group:'Plans',            path:'docs/weekly-reviews/review-2026-05-18.md',       agent:'weekly-review',             via:'weekly-review',            age:'1d',    review:'pending' },
  { group:'Plans',            path:'docs/weekly-reviews/retro-2026-05-16.md',        agent:'weekend-ops',               via:'weekend-ops',              age:'6d',    review:'approved' },
  { group:'Plans',            path:'docs/daily-briefs/morning-brief.md',             agent:'nightly-monitor',           via:'nightly-monitor',          age:'11h',   review:'standing' },
  { group:'Plans',            path:'docs/daily-briefs/monday-prep.md',               agent:'weekend-ops',               via:'weekend-ops',              age:'6d',    review:'standing' },
  { group:'Audits',           path:'docs/audits/security-report-2026-05-22.md',      agent:'security-agent',            via:'security-scan',            age:'6h',    review:'flagged' },
  { group:'Audits',           path:'docs/audits/dep-security-2026-05-21.md',         agent:'dependency-security-agent', via:'dependency-security-scan', age:'1d',    review:'approved' },
  { group:'Audits',           path:'docs/audits/access-review-2026-05-05.md',        agent:'access-review-agent',       via:'access-control-review',    age:'17d',   review:'approved' },
  { group:'Audits',           path:'docs/legal/compliance-audit-2026-05-04.md',      agent:'compliance-agent',          via:'compliance-audit',         age:'18d',   review:'flagged' },
  { group:'Architecture',     path:'docs/architecture/arch-review-2026-05-13.md',    agent:'architecture-agent',        via:'architecture-review',      age:'9d',    review:'approved' },
  { group:'Architecture',     path:'docs/architecture/adr-014-billing-split.md',     agent:'architecture-agent',        via:'architecture-review',      age:'9d',    review:'approved' },
  { group:'Architecture',     path:'docs/code-reviews/review-2026-05-22-a1b2c3d.md', agent:'code-review-agent',         via:'code-review-loop',         age:'26m',   review:'pending' },
  { group:'Quality',          path:'docs/performance/benchmark-2026-05-18.md',       agent:'performance-agent',         via:'performance-benchmark',    age:'4d',    review:'approved' },
  { group:'Quality',          path:'docs/tech-debt/debt-report-2026-05-15.md',       agent:'tech-debt-agent',           via:'tech-debt-audit',          age:'7d',    review:'pending' },
  { group:'Growth & metrics', path:'docs/seo/weekly-2026-05-15.md',                  agent:'seo-agent',                 via:'seo-weekly',               age:'7d',    review:'approved' },
  { group:'Growth & metrics', path:'docs/analytics/daily-log.md',                    agent:'analytics-agent',           via:'analytics-daily',          age:'20h',   review:'standing' },
  { group:'Growth & metrics', path:'docs/support/digest-2026-05-21.md',              agent:'support-agent',             via:'support-digest',           age:'18h',   review:'pending' },
  { group:'Growth & metrics', path:'docs/finance/snapshot-2026-05-16.md',            agent:'finance-agent',             via:'friday-finance',           age:'3d',    review:'pending' },
];

/* ──────────────────────────────────────────────────────────────────────
   6. Audit log — `docs/agent-audit.log` style entries.
   Format: ISO timestamp + agent + kind + status + summary.
   ────────────────────────────────────────────────────────────────────── */
const EVENTS = [
  { who:'dev-agent',                 kind:'run',    status:'done',   summary:'Merged H-118 — fix race in BillingFlow useEffect (3f9a2c1)',                  age:'1m' },
  { who:'dashboard-refresh',         kind:'run',    status:'done',   summary:'Rebuilt docs/dashboard/index.html in 1.4s',                                    age:'8m' },
  { who:'dev-agent',                 kind:'run',    status:'done',   summary:'Picked top stage=ready: H-119 \u2014 typed strict-null on /api/users',         age:'12m' },
  { who:'qa-agent',                  kind:'run',    status:'fail',   summary:'Verdict STOP \u2014 regression in /api/users. Filed H-128 in backlog.',         age:'14m' },
  { who:'code-review-agent',         kind:'run',    status:'fail',   summary:'Filed H-127 \u2014 complexity 18 in BillingFlow.tsx (verdict: refactor required)', age:'26m' },
  { who:'marketing-agent',           kind:'run',    status:'done',   summary:'Wrote docs/content/drafts/2026-05-22-linkedin.md (pillar: launch)',            age:'12m' },
  { who:'qa-agent',                  kind:'run',    status:'done',   summary:'Type check + lint + tests all green for 3f9a2c1',                              age:'41m' },
  { who:'improvement-agent',         kind:'run',    status:'done',   summary:'Promoted 4 items from improvement-backlog \u2192 ready',                       age:'1h 12m' },
  { who:'pm-agent',                  kind:'action', status:'done',   summary:'Updated docs/discovery/specs/pricing.md from WTP survey n=42',                 age:'1h 47m' },
  { who:'discovery-agent',           kind:'run',    status:'done',   summary:'Summarised 5 customer calls \u2192 3 themes appended to discovery/queue.md',    age:'2h 14m' },
  { who:'analytics-agent',           kind:'run',    status:'done',   summary:'Activation \u221222% DoD \u2014 anomaly filed in discovery/queue.md',           age:'20h' },
  { who:'support-agent',             kind:'run',    status:'done',   summary:'docs/support/digest-2026-05-21.md \u2014 2 escalations surfaced',              age:'18h' },
  { who:'security-agent',            kind:'run',    status:'fail',   summary:'C-12 filed \u2014 GCP service-account key past 90d window',                    age:'6h 22m' },
  { who:'design-agent',              kind:'action', status:'done',   summary:'Exported 3 onboarding-V2 directions to docs/design/onboarding-v2/',            age:'6h 22m' },
  { who:'finance-agent',             kind:'run',    status:'done',   summary:'docs/finance/snapshot-2026-05-16.md \u2014 needs sign-off on observability',   age:'3d' },
  { who:'devops-agent',              kind:'action', status:'done',   summary:'Deploy preview built for PR #1247 (preview-1247.staging)',                     age:'4h 56m' },
  { who:'nightly-monitor',           kind:'run',    status:'done',   summary:'Overnight watch clean \u2014 no incidents, agents healthy, CI green',           age:'11h' },
  { who:'dependency-security-agent', kind:'run',    status:'done',   summary:'SBOM snapshot saved \u2014 0 new CVEs vs last week',                            age:'1d' },
  { who:'performance-agent',         kind:'run',    status:'done',   summary:'API P95 within baseline \u2014 bundle size flat',                              age:'1d 6h' },
  { who:'daily-health-check',        kind:'run',    status:'done',   summary:'\ud83d\udfe2 Code health: type \u2713 lint \u2713 tests \u2713 CI \u2713',         age:'3h 41m' },
].map((e,i) => ({...e, id:'e-'+i}));

/* ──────────────────────────────────────────────────────────────────────
   7. Hourly loop (verbatim from README §Self-Healing Loop)
   ────────────────────────────────────────────────────────────────────── */
const HOURLY_LOOP = [
  { at:':00', name:'dev-execution',     agent:'dev-agent',         desc:'pick top stage=ready \u2192 implement \u2192 CI mirror \u2192 merge', status:'done', result:'Merged 3f9a2c1' },
  { at:':15', name:'code-review-loop',  agent:'code-review-agent', desc:'SOLID + complexity + render-path + security patterns',                status:'fail', result:'Filed H-127' },
  { at:':30', name:'qa-validation',     agent:'qa-agent',          desc:'type check + lint + tests + CI gate',                                  status:'fail', result:'Verdict STOP \u2192 H-128' },
  { at:':45', name:'dashboard-refresh', agent:'dashboard-refresh', desc:'rebuild this view from the audit log',                                 status:'done', result:'1.4s' },
];

/* ──────────────────────────────────────────────────────────────────────
   8. Backlog — 6-column row format (per docs/BACKLOG-FORMAT.md).
   ID prefixes: C-## Critical, H-## High, M-## Medium, L-## Low, GRC-## Compliance.
   Stages: discover \u2192 define \u2192 gtm \u2192 design \u2192 ready \u2192 in-progress (\u2192 done).
   ────────────────────────────────────────────────────────────────────── */
const BACKLOG = [
  { id:'C-12',   sev:'critical',area:'Security',     stage:'ready',       title:'Rotate expired GCP service-account key',           owner:'security-agent',            files:'.env.prod, ci/deploy.yml',         age:'6h',     filedBy:'security-scan' },
  { id:'H-128',  sev:'high',    area:'Engineering',  stage:'ready',       title:'Regression in /api/users strict-null \u2014 QA STOP', owner:'qa-agent',                  files:'app/api/users/route.ts',           age:'14m',    filedBy:'qa-validation' },
  { id:'H-127',  sev:'high',    area:'Architecture', stage:'discover',    title:'Cyclomatic complexity 18 in BillingFlow.tsx',      owner:'code-review-agent',         files:'app/billing/BillingFlow.tsx',      age:'26m',    filedBy:'code-review-loop' },
  { id:'H-126',  sev:'high',    area:'Performance',  stage:'define',      title:'/api/orders P95 over 800ms under burst',           owner:'performance-agent',         files:'app/api/orders/*',                 age:'1d',     filedBy:'performance-benchmark' },
  { id:'H-125',  sev:'high',    area:'GTM',          stage:'gtm',         title:'Pricing tier decision blocks launch',              owner:'pm-agent',                  files:'docs/gtm/pricing.md',              age:'2h',     filedBy:'pm-agent' },
  { id:'M-44',   sev:'medium',  area:'UX',           stage:'design',      title:'Onboarding step 3 drop-off 38%',                   owner:'design-agent',              files:'app/onboarding/*',                 age:'1d',     filedBy:'discovery-agent' },
  { id:'M-43',   sev:'medium',  area:'Engineering',  stage:'in-progress', title:'Type strict-null on /api/users',                   owner:'dev-agent',                 files:'app/api/users/*',                  age:'12m',    filedBy:'tech-debt-audit' },
  { id:'M-42',   sev:'medium',  area:'Tech Debt',    stage:'ready',       title:'Remove deprecated dateFmt() helper',               owner:'tech-debt-agent',           files:'app/utils/*',                      age:'3d',     filedBy:'tech-debt-audit' },
  { id:'L-21',   sev:'low',     area:'SEO',          stage:'ready',       title:'Add meta descriptions to docs pages',              owner:'seo-agent',                 files:'app/docs/*',                       age:'4d',     filedBy:'seo-weekly' },
  { id:'GRC-08', sev:'medium',  area:'Compliance',   stage:'define',      title:'Cookie consent banner missing for EU users',       owner:'compliance-agent',          files:'app/layout.tsx',                   age:'18d',    filedBy:'compliance-audit' },
];
const PIPELINE_STAGES = ['discover','define','gtm','design','ready','in-progress'];

/* ──────────────────────────────────────────────────────────────────────
   9. Top-line stats
   ────────────────────────────────────────────────────────────────────── */
const STATS = {
  agentsTotal:     AGENTS.length,                                                  // 33
  agentsScheduled: SCHEDULED_TASKS.length,                                         // 23
  agentsHealthy:   AGENTS.filter(a => a.status === 'healthy').length,
  agentsWarning:   AGENTS.filter(a => a.status === 'warning').length,
  agentsCritical:  AGENTS.filter(a => a.status === 'critical').length,
  agentsIdle:      AGENTS.filter(a => a.status === 'idle').length,
  agentsOnDemand:  AGENTS.filter(a => a.status === 'on-demand').length,
  inboxPending:    INBOX.length,
  inboxUrgent:     INBOX.filter(i => i.urgency === 'high').length,
  backlogOpen:     BACKLOG.length,
  backlogDone24h:  7,                                                              // from dev-log + audit-log line counts
  runs24h:         87,                                                             // 18+18+24+8+1+1+1+1+1+...
  alerts:          1,                                                              // QA STOP
};

/* ──────────────────────────────────────────────────────────────────────
   Globals
   ────────────────────────────────────────────────────────────────────── */
Object.assign(window, {
  DEPARTMENTS, AGENTS, AGENT_BY_NAME, SCHEDULED_TASKS, TASK_BY_AGENT,
  INBOX, OUTPUTS, EVENTS, HOURLY_LOOP, BACKLOG, PIPELINE_STAGES, STATS,
  // Backwards-compat alias for code that still imports DECISIONS
  DECISIONS: INBOX,
});
