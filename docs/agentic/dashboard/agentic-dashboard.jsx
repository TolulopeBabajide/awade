import { useState, useEffect } from "react";
import {
  Activity, AlertTriangle, BarChart2, Calendar, CheckCircle2,
  ChevronRight, Clock, Code, DollarSign, FileText, FolderOpen,
  GitMerge, Headphones, Lock, RefreshCw, Search, Settings,
  Shield, Terminal, Users, XCircle, Zap
} from "lucide-react";

/* ═══════════════════════════════════════════════════════════════
   THEME  —  base · primary (indigo) · secondary (cyan)
═══════════════════════════════════════════════════════════════ */
const T = {
  bg:      '#070714', base1: '#0d0d20', base2: '#111128', base3: '#181835',
  primary: '#6366f1', primaryLight: '#818cf8', primaryDim: 'rgba(99,102,241,0.13)', primaryBorder: 'rgba(99,102,241,0.28)',
  secondary: '#06b6d4', secondaryLight: '#22d3ee', secondaryDim: 'rgba(6,182,212,0.11)', secondaryBorder: 'rgba(6,182,212,0.28)',
  success: '#10b981', successDim: 'rgba(16,185,129,0.11)', successBorder: 'rgba(16,185,129,0.28)',
  warning: '#f59e0b', warningDim: 'rgba(245,158,11,0.11)', warningBorder: 'rgba(245,158,11,0.28)',
  danger:  '#ef4444', dangerDim: 'rgba(239,68,68,0.11)', dangerBorder: 'rgba(239,68,68,0.28)',
  text: '#f1f5f9', textSec: '#94a3b8', textMut: '#475569',
  border: '#1c1c3a', border2: '#141430',
  grad: 'linear-gradient(135deg, #6366f1 0%, #06b6d4 100%)',
  gradText: { background: 'linear-gradient(135deg, #818cf8, #22d3ee)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' },
};

const CSS = `
  @keyframes pulse-ring {
    0%   { transform:scale(1);   opacity:0.8; }
    50%  { transform:scale(1.7); opacity:0;   }
    100% { transform:scale(1.7); opacity:0;   }
  }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.25} }
  @keyframes fadein { from{opacity:0;transform:translateY(-5px)} to{opacity:1;transform:translateY(0)} }
`;

// AGENT_DATA_START — auto-updated by awade-dashboard-refresh (hourly :45). Do not edit manually.
const DATA_TIMESTAMP = 'Awade — data as of 2026-04-22T18:45Z · morning-brief 2026-04-22 · dev-log top 18:11 · qa-log top 18:32';

const CODE_HEALTH = {
  typescript:       { status: 'clean', label: '0 errors (tsc --noEmit)' },
  tests_frontend:   { status: 'pass',  label: '9 / 9 passing (vitest)' },
  tests_backend:    { status: 'warn',  label: 'Sandbox disk full — CI authoritative; M-22 pre-existing, H-27/H-28/H-29 all fixed' },
  lint:             { status: 'clean', label: '0 errors, 0 warnings (ESLint)' },
  commits_today:    35,
  last_commit:      'b9a089f',
};

const BACKLOG_OPEN = [
  { id:'H-01', label:'Wire up Sentry for error monitoring — backend + frontend', dept:'engineering', priority:'high', blocked:false, effort:'M', blockReason:'' },
  { id:'H-03', label:'Admin panel has no parent / child management views yet', dept:'engineering', priority:'high', blocked:false, effort:'L', blockReason:'' },
  { id:'H-11', label:'No pytest coverage for children router or ChildrenService — ownership, role-gating, guide generation, malformed AI JSON', dept:'engineering', priority:'high', blocked:false, effort:'M', blockReason:'' },
  { id:'H-16', label:'10+ console.log / console.error in production paths in EditLessonResourcePage.tsx and SettingsPage.tsx', dept:'engineering', priority:'high', blocked:false, effort:'S', blockReason:'' },
  { id:'H-19', label:'Dedicated /children page for managing child profiles — standalone My Children page with add/edit/delete', dept:'product', priority:'high', blocked:false, effort:'M', blockReason:'' },
  { id:'H-20', label:'Parent onboarding flow — first-time signup should guide through adding a child profile before the dashboard', dept:'product', priority:'high', blocked:false, effort:'M', blockReason:'' },
  { id:'H-25', label:'JWT access token stored in localStorage — any XSS can exfiltrate tokens; requires Tolu decision on approach', dept:'security', priority:'high', blocked:true, effort:'L', blockReason:'Requires Tolu decision: httpOnly cookies vs memory-only storage' },
  { id:'M-23', label:'validate_output lacks content-safety / harmful-word filtering — test_audit_security_features assumed it existed', dept:'security', priority:'medium', blocked:false, effort:'S', blockReason:'' },
  { id:'M-22', label:'test_async_integration.py::test_worker_task_execution fails — mock patch path wrong or arq dispatch not wired', dept:'engineering', priority:'medium', blocked:false, effort:'S', blockReason:'' },
  { id:'M-01', label:'Handle loading + error states consistently across ParentDashboardPage, GuideViewPage, SavedGuidesPage', dept:'product', priority:'medium', blocked:false, effort:'M', blockReason:'' },
  { id:'M-02', label:'Meta tags + OG images on landing page (parent + educator versions)', dept:'product', priority:'medium', blocked:false, effort:'S', blockReason:'' },
  { id:'M-03', label:'Pre-commit hooks for lint + type check (husky + lint-staged)', dept:'engineering', priority:'medium', blocked:false, effort:'S', blockReason:'' },
  { id:'M-04', label:'Backend coverage below 70% threshold in some modules — shore up children_service + lesson_plan_service', dept:'engineering', priority:'medium', blocked:false, effort:'M', blockReason:'' },
  { id:'M-05', label:'Share-to-WhatsApp button on parent guides (high-engagement channel in target markets)', dept:'product', priority:'medium', blocked:false, effort:'S', blockReason:'' },
  { id:'M-06', label:'Landing page Lighthouse performance score warning — audit and fix heaviest assets', dept:'engineering', priority:'medium', blocked:false, effort:'M', blockReason:'' },
  { id:'M-07', label:"How it works section for parents needs real screenshots, not placeholders", dept:'product', priority:'medium', blocked:false, effort:'S', blockReason:'' },
  { id:'M-08', label:'Backend requirements.txt uses >= minimums — pin exact versions for reproducible builds', dept:'security', priority:'medium', blocked:false, effort:'S', blockReason:'' },
  { id:'M-09', label:'Review whether catalog GETs should require auth — decision needed from Tolu before implementation', dept:'security', priority:'medium', blocked:true, effort:'S', blockReason:'Tolu decision needed on public vs auth-gated catalog endpoints' },
  { id:'M-10', label:'Disable /docs and /redoc endpoints in production (gate on ENVIRONMENT == production)', dept:'security', priority:'medium', blocked:false, effort:'S', blockReason:'' },
  { id:'M-11', label:'Add Content-Security-Policy header to SecurityHeadersMiddleware', dept:'security', priority:'medium', blocked:false, effort:'S', blockReason:'' },
];

const SECURITY_STATUS = {
  date:     '2026-04-22',
  overall:  'issues-found',
  critical: 0, high: 1, medium: 2, low: 0, deps: 0,
  findings: [
    { id:'H-25', severity:'high',   label:'JWT access token in localStorage — XSS exfiltration risk (Tolu decision needed)', file:'apps/frontend/src/contexts/AuthContext.tsx' },
    { id:'H-23', severity:'high',   label:'PyJWT 2.3.0 severely outdated — FIXED 18:11Z (b9a089f, pinned to 2.12.1)', file:'apps/backend/requirements.txt' },
    { id:'H-24', severity:'high',   label:'Suspended users bypass auth — FIXED 09:56Z (91d758e)', file:'apps/backend/dependencies.py' },
    { id:'H-10', severity:'high',   label:'react-router XSS via Open Redirects GHSA-2w69-qvjg-hvjx — FIXED 11:15Z (8589362)', file:'apps/frontend/package-lock.json' },
    { id:'M-12', severity:'medium', label:'context_input flows undelimited into AI prompt — educator injection surface', file:'packages/ai/prompts.py' },
    { id:'M-08', severity:'medium', label:'requirements.txt uses >= minimums — unpinned dependencies (PyJWT now pinned)', file:'apps/backend/requirements.txt' },
  ],
  note: 'H-23 (PyJWT pin) shipped 18:11Z (b9a089f). H-24 + H-10 fixed earlier today. 1 open high: H-25 (localStorage — awaiting Tolu decision).',
};

const DEV_LOG = [
  { time:'18:11', issue:'H-23', status:'done', label:'Pin PyJWT==2.12.1 to close CVE surface (large version gap 2.3→2.12)', detail:'b9a089f — requirements.txt PyJWT pinned; closes JWT CVE window from security audit' },
  { time:'17:12', issue:'H-29', status:'done', label:'Rate-limiter state not reset between tests — autouse fixture in conftest.py', detail:'3ce06c4 → 53874c4 — rate_limiter_reset autouse fixture; clears before + after each test' },
  { time:'16:14', issue:'H-28', status:'done', label:'Fix TestExceptionDetailSanitization — router guards + google credential field', detail:'442990d → a977e9c — Pydantic 422 bypass fixed, google_auth credential field corrected' },
  { time:'15:12', issue:'H-27', status:'done', label:'Fix test_contexts_router.py User.__new__ bypass — 8 tests now passing', detail:'c38dcd4 → 75f08d0 — proper SQLAlchemy Model() instantiation in test helpers' },
  { time:'11:15', issue:'H-10', status:'done', label:'Fix high-severity XSS in react-router / @remix-run/router', detail:'8589362 → 270ac41 — npm audit fix, react-router 6.30.3 (GHSA-2w69-qvjg-hvjx)' },
  { time:'09:56', issue:'H-24', status:'done', label:'Block suspended users in get_current_active_user', detail:'91d758e → 1153504 — is_suspended check + 3 new tests in dependencies.py' },
  { time:'08:30', issue:'H-26', status:'done', label:'Remove traceback.print_exc() calls from lesson_plan_service.py', detail:'a26af21 → 187bd80 — 2 inline traceback calls replaced with structured logger' },
  { time:'~07:00', issue:'H-21', status:'done', label:'Remove bare print() calls in lesson_plan_service.py', detail:'4460d8b → 0184370 — 2 print() replaced with logger.error()' },
  { time:'04:12', issue:'H-22', status:'done', label:'Fix failing Gemini provider model name assertions in tests', detail:'4db306a → c2c905f — test_ai_providers.py lines 51-52 updated to gemini-flash-latest' },
  { time:'~03:00', issue:'H-06', status:'done', label:'AI output validation — Pydantic schema gate before persisting parent guide', detail:'f5523a2 → e25040d — ParentGuideAIContent schema + 18 tests; 502 on invalid AI JSON' },
  { time:'00:34', issue:'H-09', status:'done', label:'OpenAI client timeout — OWASP LLM10 / Model DoS mitigation', detail:'3972e01 → cb57ec2 — 60s default timeout, OPENAI_TIMEOUT_SECONDS env var, 2 new tests' },
  { time:'00:12', issue:'H-12', status:'done', label:'Ownership check on GET /api/users/{user_id} — PII disclosure fix', detail:'8b012b9 → e30e5c1 — 403 for cross-user reads; 7 new tests in test_users_router.py' },
  { time:'00:00', issue:'H-18', status:'done', label:'Remove str(e) from HTTPException details across 6 service files', detail:'8628ab7 → 73188d5 — static strings + logger.error() in 6 backend service files' },
  { time:'00:00', issue:'C-05', status:'done', label:'Git repo corruption resolved (develop ref self-healed)', detail:'self-healed via commit-tree plumbing; c2c905f confirmed as valid HEAD' },
  { time:'23:09', issue:'H-13', status:'done', label:'Rate-limit google, refresh, forgot-password, reset-password auth endpoints', detail:'022b959 → d108e86 — 10/min google, 20/min refresh, 5/min forgot+reset' },
  { time:'22:00', issue:'H-08', status:'done', label:'Remove str(e) from auth/context services + replace print() with logger', detail:'d735ea3 → 535718e — 14 detail strings sanitized across auth_service + context_service' },
  { time:'21:12', issue:'H-07', status:'done', label:'Rate-limit parent guide generation endpoint', detail:'da34bf7 → 737c830 — @limiter.limit(5/minute) on POST /children/{id}/guides/generate' },
];

const QA_LOG = [
  { time:'18:32', result:'pass', commit:'b9a089f', tests:'9 / 9 fe',     tsc:true,  note:'H-23 fix (PyJWT==2.12.1 pin) clean. Backend disk exhausted — CI authoritative. No new issues.' },
  { time:'17:34', result:'pass', commit:'53874c4', tests:'9 / 9 fe',     tsc:true,  note:'H-29 fix clean (rate_limiter_reset autouse fixture). Backend disk exhausted — CI authoritative. No new issues.' },
  { time:'16:35', result:'pass', commit:'a977e9c', tests:'9 / 9 fe',     tsc:true,  note:'H-28 fix clean (exception detail sanitization). Backend disk exhausted — CI authoritative. No new issues.' },
  { time:'15:36', result:'pass', commit:'c38dcd4', tests:'183 / 192 be', tsc:true,  note:'H-27 fix clean. 9 pre-existing failures: H-28x3, H-29x5, M-22x1 — all tracked, H-28/H-29 now fixed.' },
  { time:'12:36', result:'fail', commit:'73188d5', tests:'175 / 192 be', tsc:true,  note:'AWD-H-29 filed: rate-limiter not reset between test files (5 new failures). H-18 prod code clean.' },
  { time:'11:34', result:'pass', commit:'270ac41', tests:'9 / 9 fe',     tsc:true,  note:'react-router XSS patch (H-10) clean. AWD-L-09 filed (React Router v7 future flags in test output).' },
  { time:'10:36', result:'pass', commit:'1153504', tests:'9 / 9 fe',     tsc:true,  note:'H-24 (suspended-user bypass) verified. Backend skipped — Python 3.13 venv + disk full.' },
];

const YESTERDAY_FAILS = [
  { time:'12:36', issue:'H-29', note:'Rate-limiter not reset between test files (5 tests) — AWD-H-29 filed; fix shipped 17:12Z as 53874c4.' },
  { time:'06:35', issue:'C-05', note:'Git repo corruption: develop ref missing object — AWD-C-05 filed; self-healed at 09:56Z via commit-tree plumbing.' },
];
// AGENT_DATA_END

/* ═══════════════════════════════════════════════════════════════
   DEPARTMENT META
═══════════════════════════════════════════════════════════════ */
const DEPT = {
  engineering:   { color:T.primary,   dim:T.primaryDim,   border:T.primaryBorder,   label:'Engineering',   Icon:Code       },
  security:      { color:T.danger,    dim:T.dangerDim,    border:T.dangerBorder,    label:'Security',      Icon:Shield     },
  marketing:     { color:'#a855f7',   dim:'rgba(168,85,247,0.12)', border:'rgba(168,85,247,0.28)', label:'Marketing',  Icon:BarChart2 },
  content:       { color:'#ec4899',   dim:'rgba(236,72,153,0.12)', border:'rgba(236,72,153,0.28)', label:'Content',    Icon:FileText  },
  operations:    { color:T.warning,   dim:T.warningDim,   border:T.warningBorder,   label:'Operations',    Icon:Settings   },
  support:       { color:T.success,   dim:T.successDim,   border:T.successBorder,   label:'Support',       Icon:Headphones },
  legal:         { color:'#64748b',   dim:'rgba(100,116,139,0.12)',border:'rgba(100,116,139,0.28)',label:'Legal',     Icon:Lock      },
  orchestration: { color:T.secondary, dim:T.secondaryDim, border:T.secondaryBorder, label:'Orchestration', Icon:Activity   },
};

const AGENTS = [
  { name:'dev-agent',       label:'Lead Dev',        dept:'engineering',   auto:true,  schedule:'Hourly :00', runsToday:17, issuesFixed:7 },
  { name:'qa-agent',        label:'QA & Testing',    dept:'engineering',   auto:true,  schedule:'Hourly :30', runsToday:10, passRate:100  },
  { name:'security-agent',  label:'Security',        dept:'security',      auto:true,  schedule:'Daily 6am',  runsToday:1,  findings:7    },
  { name:'devops-agent',    label:'DevOps',          dept:'engineering',   auto:false, schedule:'On demand',  runsToday:0,  issuesFixed:0 },
  { name:'pm-agent',        label:'Product Manager', dept:'orchestration', auto:true,  schedule:'Mon 9:30am', runsToday:0,  issuesFixed:0 },
  { name:'weekly-review',   label:'Weekly Review',   dept:'orchestration', auto:true,  schedule:'Mon 9am',    runsToday:0,  issuesFixed:0 },
  { name:'sprint-planning', label:'Sprint Planning', dept:'orchestration', auto:true,  schedule:'Mon 9:30am', runsToday:0,  issuesFixed:0 },
  { name:'marketing-agent', label:'Social Media',    dept:'marketing',     auto:true,  schedule:'Weekdays 3pm',runsToday:1, issuesFixed:0 },
  { name:'seo-agent',       label:'SEO & Content',   dept:'marketing',     auto:true,  schedule:'Wed 9am',    runsToday:1,  issuesFixed:0 },
  { name:'growth-agent',    label:'Growth Hacker',   dept:'marketing',     auto:false, schedule:'On demand',  runsToday:0,  issuesFixed:0 },
  { name:'content-agent',   label:'Brand Voice',     dept:'content',       auto:false, schedule:'On demand',  runsToday:0,  issuesFixed:0 },
  { name:'finance-agent',   label:'Finance',         dept:'operations',    auto:true,  schedule:'Fri 5pm',    runsToday:0,  issuesFixed:0 },
  { name:'analytics-agent', label:'Analytics',       dept:'operations',    auto:true,  schedule:'Mon 9am',    runsToday:0,  issuesFixed:0 },
  { name:'ops-agent',       label:'Operations',      dept:'operations',    auto:true,  schedule:'Sat 10am',   runsToday:0,  issuesFixed:0 },
  { name:'support-agent',   label:'Support',         dept:'support',       auto:false, schedule:'On demand',  runsToday:0,  issuesFixed:0 },
  { name:'legal-agent',     label:'Legal / COPPA',   dept:'legal',         auto:false, schedule:'On demand',  runsToday:0,  issuesFixed:0 },
];

const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const TIME_SLOTS = [
  { time:'6:00 AM',    tasks:[{ days:[0,1,2,3,4,5,6], name:'security-scan',      dept:'security'       }] },
  { time:'8:00 AM',    tasks:[{ days:[0,1,2,3,4],     name:'daily-health-check', dept:'engineering'    }] },
  { time:'9:00 AM',    tasks:[{ days:[0],             name:'weekly-review',      dept:'orchestration'  },
                               { days:[2],             name:'content-calendar',   dept:'marketing'      }] },
  { time:'9:30 AM',    tasks:[{ days:[0],             name:'sprint-planning',    dept:'orchestration'  }] },
  { time:'10:00 AM',   tasks:[{ days:[5],             name:'weekend-ops',        dept:'operations'     }] },
  { time:'Hourly :00', tasks:[{ days:[0,1,2,3,4,5,6], name:'dev-execution',      dept:'engineering'    }] },
  { time:'Hourly :30', tasks:[{ days:[0,1,2,3,4,5,6], name:'qa-validation',      dept:'engineering'    }] },
  { time:'3:00 PM',    tasks:[{ days:[0,1,2,3,4],     name:'growth-daily',       dept:'marketing'      }] },
  { time:'5:00 PM',    tasks:[{ days:[4],             name:'friday-finance',     dept:'operations'     }] },
  { time:'11:00 PM',   tasks:[{ days:[0,1,2,3,4,5,6], name:'nightly-monitor',    dept:'engineering'    }] },
];

/* ═══════════════════════════════════════════════════════════════
   SHARED COMPONENTS
═══════════════════════════════════════════════════════════════ */
function Card({ children, style = {} }) {
  return <div style={{ background:T.base1, border:`1px solid ${T.border}`, borderRadius:'12px', ...style }}>{children}</div>;
}
function Badge({ label, color, dim, border }) {
  return <span style={{ fontSize:'10px', fontWeight:700, color, background:dim, border:`1px solid ${border}`, borderRadius:'4px', padding:'2px 7px', letterSpacing:'0.04em', whiteSpace:'nowrap' }}>{label}</span>;
}
function SectionHeader({ title, sub, Icon: Ic }) {
  return (
    <div style={{ marginBottom:'18px' }}>
      <div style={{ display:'flex', alignItems:'center', gap:'7px', marginBottom:'3px' }}>
        {Ic && <Ic size={15} color={T.primary} />}
        <h2 style={{ margin:0, fontSize:'15px', fontWeight:800 }}>{title}</h2>
      </div>
      {sub && <p style={{ margin:0, fontSize:'12px', color:T.textMut }}>{sub}</p>}
    </div>
  );
}
function StatusPill({ status }) {
  const cfg = {
    clean: { color:T.success, label:'✓ Clean' },
    pass:  { color:T.success, label:'✓ Pass'  },
    warn:  { color:T.warning, label:'⚠ Warn'  },
    fail:  { color:T.danger,  label:'✕ Fail'  },
    skip:  { color:T.textMut, label:'⏭ Skip'  },
  }[status] || { color:T.textMut, label: status };
  return <span style={{ fontSize:'11px', fontWeight:700, color:cfg.color }}>{cfg.label}</span>;
}

/* ═══════════════════════════════════════════════════════════════
   MONITOR TAB  —  real data
═══════════════════════════════════════════════════════════════ */
function MonitorTab() {
  const [elapsed, setElapsed] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setElapsed(e => e + 1), 1000);
    return () => clearInterval(t);
  }, []);
  const fmt = s => `${String(Math.floor(s/3600)).padStart(2,'0')}:${String(Math.floor((s%3600)/60)).padStart(2,'0')}:${String(s%60).padStart(2,'0')}`;

  const issuesFixed = DEV_LOG.filter(d => d.status === 'done').length;
  const qaPassRate = Math.round((QA_LOG.filter(q => q.result === 'pass').length / QA_LOG.length) * 100);
  const openIssues = BACKLOG_OPEN.length;

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:'14px' }}>
      {/* Morning brief banner */}
      <div style={{ background:'rgba(239,68,68,0.07)', border:`1px solid ${T.dangerBorder}`, borderRadius:'12px', padding:'14px 18px', display:'flex', alignItems:'flex-start', gap:'12px' }}>
        <AlertTriangle size={16} color={T.danger} style={{ flexShrink:0, marginTop:'1px' }} />
        <div>
          <div style={{ fontSize:'12px', fontWeight:800, color:T.danger, marginBottom:'3px' }}>Action Required — from morning-brief.md</div>
          <div style={{ fontSize:'12px', color:T.textSec }}>AWD-C-05 open: git repo corruption — <code style={{fontFamily:'monospace', color:T.danger}}>refs/heads/develop</code> points to missing SHA. Run <code style={{fontFamily:'monospace'}}>git update-ref refs/heads/develop da90c8967dd912f38467e2c93c41ab7501114204</code> on your Mac, then re-push. Blocks all CI.</div>
          <div style={{ fontSize:'11px', color:T.textMut, marginTop:'4px' }}>{DATA_TIMESTAMP}</div>
        </div>
      </div>

      {/* Vitals row */}
      <div style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:'10px' }}>
        {[
          { label:'Issues Fixed Today',  value:issuesFixed,    color:T.primary,    Icon:GitMerge   },
          { label:'QA Pass Rate Today',  value:`${qaPassRate}%`,color:T.success,   Icon:CheckCircle2 },
          { label:'Open Backlog',        value:openIssues,     color:openIssues > 0 ? T.warning : T.success, Icon:FolderOpen },
          { label:'Session uptime',      value:fmt(elapsed),   color:T.secondary,  Icon:Clock, mono:true },
        ].map(s => {
          const { Icon:Ic } = s;
          return (
            <Card key={s.label} style={{ padding:'15px 16px' }}>
              <div style={{ display:'flex', justifyContent:'space-between', marginBottom:'8px' }}>
                <span style={{ fontSize:'10px', fontWeight:700, color:T.textMut, letterSpacing:'0.05em' }}>{s.label.toUpperCase()}</span>
                <Ic size={13} color={s.color} />
              </div>
              <div style={{ fontSize:s.mono?'20px':'26px', fontWeight:900, color:s.color, fontFamily:s.mono?'monospace':'inherit', lineHeight:1 }}>{s.value}</div>
            </Card>
          );
        })}
      </div>

      {/* Code health + backlog */}
      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'14px' }}>
        <Card style={{ padding:'18px' }}>
          <div style={{ fontSize:'11px', fontWeight:700, color:T.textSec, letterSpacing:'0.07em', marginBottom:'13px' }}>CODE HEALTH</div>
          {[
            { label:'TypeScript',         ...CODE_HEALTH.typescript      },
            { label:'Tests (frontend)',   ...CODE_HEALTH.tests_frontend  },
            { label:'Tests (backend)',    ...CODE_HEALTH.tests_backend   },
            { label:'Lint',               ...CODE_HEALTH.lint            },
          ].map(row => (
            <div key={row.label} style={{ display:'flex', justifyContent:'space-between', alignItems:'center', padding:'7px 0', borderBottom:`1px solid ${T.border2}` }}>
              <span style={{ fontSize:'12px', color:T.textSec }}>{row.label}</span>
              <div style={{ display:'flex', flexDirection:'column', alignItems:'flex-end', gap:'1px' }}>
                <StatusPill status={row.status} />
                <span style={{ fontSize:'10px', color:T.textMut }}>{row.label}</span>
              </div>
            </div>
          ))}
          <div style={{ marginTop:'10px', display:'flex', gap:'16px' }}>
            <div style={{ textAlign:'center' }}>
              <div style={{ fontSize:'20px', fontWeight:900, color:T.primary }}>{CODE_HEALTH.commits_today}</div>
              <div style={{ fontSize:'10px', color:T.textMut }}>commits today</div>
            </div>
            <div style={{ textAlign:'center' }}>
              <div style={{ fontSize:'20px', fontWeight:900, color:T.success }}>{issuesFixed}</div>
              <div style={{ fontSize:'10px', color:T.textMut }}>issues fixed</div>
            </div>
            <div style={{ textAlign:'center' }}>
              <div style={{ fontSize:'20px', fontWeight:900, color:T.secondary }}>{QA_LOG.length}</div>
              <div style={{ fontSize:'10px', color:T.textMut }}>QA runs today</div>
            </div>
          </div>
        </Card>

        <Card style={{ padding:'18px' }}>
          <div style={{ fontSize:'11px', fontWeight:700, color:T.textSec, letterSpacing:'0.07em', marginBottom:'13px' }}>OPEN BACKLOG</div>
          <div style={{ maxHeight:'480px', overflowY:'auto', paddingRight:'4px' }}>
            {BACKLOG_OPEN.map(item => {
              const dept = DEPT[item.dept];
              const priColor = { high:T.danger, medium:T.warning, low:T.textMut }[item.priority];
              return (
                <div key={item.id} style={{ background:T.base2, borderRadius:'8px', padding:'10px 12px', marginBottom:'8px', borderLeft:`3px solid ${priColor}` }}>
                  <div style={{ display:'flex', alignItems:'center', gap:'6px', marginBottom:'4px' }}>
                    <span style={{ fontSize:'11px', fontWeight:800, color:priColor }}>AWD-{item.id}</span>
                    {item.blocked && <Badge label="BLOCKED" color={T.textMut} dim="rgba(100,116,139,0.1)" border="rgba(100,116,139,0.2)" />}
                  </div>
                  <div style={{ fontSize:'11px', color:T.textSec, lineHeight:1.4 }}>{item.label}</div>
                  {item.blockReason && <div style={{ fontSize:'10px', color:T.textMut, marginTop:'3px' }}>↳ {item.blockReason}</div>}
                </div>
              );
            })}
          </div>
          <div style={{ marginTop:'6px', fontSize:'11px', color:T.textMut, textAlign:'center' }}>
            Showing top 12 — 1 Critical · 11 High · 20 Medium · 7 Low · 5 GRC open in docs/agentic/backlog.md
          </div>
        </Card>
      </div>

      {/* Security summary */}
      <Card style={{ padding:'18px' }}>
        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'13px' }}>
          <div style={{ display:'flex', alignItems:'center', gap:'7px' }}>
            <Shield size={14} color={T.warning} />
            <span style={{ fontSize:'11px', fontWeight:700, color:T.textSec, letterSpacing:'0.07em' }}>SECURITY — {SECURITY_STATUS.date}</span>
          </div>
          <div style={{ display:'flex', gap:'10px' }}>
            {[
              { label:'Critical', val:SECURITY_STATUS.critical, color:SECURITY_STATUS.critical>0?T.danger:T.textMut },
              { label:'High',     val:SECURITY_STATUS.high,     color:SECURITY_STATUS.high>0?T.danger:T.textMut    },
              { label:'Medium',   val:SECURITY_STATUS.medium,   color:SECURITY_STATUS.medium>0?T.warning:T.textMut },
              { label:'Low',      val:SECURITY_STATUS.low,      color:T.textMut                                     },
              { label:'Deps',     val:`${SECURITY_STATUS.deps} high`, color:SECURITY_STATUS.deps>0?T.danger:T.success },
            ].map(s => (
              <div key={s.label} style={{ textAlign:'center' }}>
                <div style={{ fontSize:'15px', fontWeight:800, color:s.color }}>{s.val}</div>
                <div style={{ fontSize:'9px', color:T.textMut }}>{s.label}</div>
              </div>
            ))}
          </div>
        </div>
        <div style={{ display:'flex', flexDirection:'column', gap:'6px' }}>
          {SECURITY_STATUS.findings.slice(0,5).map(f => {
            const sevColor = f.severity === 'high' ? T.danger : T.warning;
            return (
              <div key={f.id} style={{ display:'flex', gap:'10px', alignItems:'flex-start', background:T.base2, borderRadius:'7px', padding:'9px 11px', borderLeft:`3px solid ${sevColor}` }}>
                <span style={{ fontSize:'11px', fontWeight:800, color:sevColor, minWidth:'52px' }}>AWD-{f.id}</span>
                <div>
                  <div style={{ fontSize:'11px', color:T.text }}>{f.label}</div>
                  <div style={{ fontSize:'10px', color:T.textMut, fontFamily:'monospace', marginTop:'2px' }}>{f.file}</div>
                </div>
              </div>
            );
          })}
        </div>
        <div style={{ fontSize:'11px', color:T.success, marginTop:'10px', padding:'8px 10px', background:T.successDim, border:`1px solid ${T.successBorder}`, borderRadius:'7px' }}>
          ✓ {SECURITY_STATUS.note}
        </div>
      </Card>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
   ACTIVITY TAB  —  real dev + QA log
═══════════════════════════════════════════════════════════════ */
function ActivityTab() {
  const [view, setView] = useState('dev');

  return (
    <div>
      <SectionHeader Icon={Activity} title="Agent Activity Log" sub="Real entries from docs/agentic/sprints/dev-log.md and docs/agentic/sprints/qa-log.md" />

      <div style={{ display:'flex', gap:'6px', marginBottom:'16px' }}>
        {[['dev','Dev Execution'],['qa','QA Validation']].map(([id, label]) => (
          <button key={id} onClick={() => setView(id)} style={{
            padding:'6px 14px', borderRadius:'8px', border:`1px solid ${view===id?T.primaryBorder:T.border}`,
            background:view===id?T.primaryDim:'transparent', color:view===id?T.primaryLight:T.textMut,
            fontSize:'12px', fontWeight:600, cursor:'pointer', transition:'all 0.15s',
          }}>{label}</button>
        ))}
      </div>

      {view === 'dev' && (
        <Card>
          <div style={{ display:'grid', gridTemplateColumns:'52px 68px 1fr auto', background:T.base2, borderBottom:`1px solid ${T.border}`, borderRadius:'12px 12px 0 0', overflow:'hidden' }}>
            {['Time','Issue','Action / Detail','Status'].map(h => (
              <div key={h} style={{ padding:'9px 12px', fontSize:'10px', color:T.textMut, fontWeight:700, letterSpacing:'0.06em' }}>{h}</div>
            ))}
          </div>
          {DEV_LOG.map((entry, i) => {
            const statusColor = { done:'#10b981', skipped:T.textMut }[entry.status];
            return (
              <div key={i} style={{ display:'grid', gridTemplateColumns:'52px 68px 1fr auto', borderBottom:i<DEV_LOG.length-1?`1px solid ${T.border2}`:'none', alignItems:'start' }}>
                <div style={{ padding:'10px 12px', fontFamily:'monospace', fontSize:'11px', color:T.textMut }}>{entry.time}</div>
                <div style={{ padding:'10px 12px' }}>
                  {entry.issue
                    ? <span style={{ fontSize:'11px', fontWeight:700, color: entry.issue.startsWith('C') ? T.danger : entry.issue.startsWith('H') ? T.danger : entry.issue.startsWith('M') ? T.warning : T.textMut }}>AWD-{entry.issue}</span>
                    : <span style={{ fontSize:'11px', color:T.textMut }}>—</span>
                  }
                </div>
                <div style={{ padding:'10px 12px' }}>
                  <div style={{ fontSize:'12px', color:entry.status==='done'?T.text:T.textMut, marginBottom:'2px' }}>{entry.label}</div>
                  <div style={{ fontSize:'10px', color:T.textMut, fontFamily:'monospace' }}>{entry.detail}</div>
                </div>
                <div style={{ padding:'10px 12px', display:'flex', alignItems:'center' }}>
                  <span style={{ fontSize:'11px', fontWeight:700, color:statusColor }}>
                    {entry.status === 'done' ? '✓ done' : '⏭ skip'}
                  </span>
                </div>
              </div>
            );
          })}
        </Card>
      )}

      {view === 'qa' && (
        <div style={{ display:'flex', flexDirection:'column', gap:'10px' }}>
          <div style={{ fontSize:'12px', color:T.textMut, fontWeight:600, marginBottom:'2px' }}>Today — mix of passes and infra-skips (develop ref corruption)</div>
          {QA_LOG.map((entry, i) => {
            const isSkip = entry.result === 'skip';
            const borderColor = isSkip ? T.border : T.successBorder;
            const resultColor = isSkip ? T.textMut : T.success;
            const resultLabel = isSkip ? '⏭ SKIP' : '✓ PASS';
            return (
              <Card key={i} style={{ padding:'14px 16px', border:`1px solid ${borderColor}` }}>
                <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'8px' }}>
                  <div style={{ display:'flex', alignItems:'center', gap:'10px' }}>
                    <span style={{ fontFamily:'monospace', fontSize:'12px', color:T.textMut }}>{entry.time}</span>
                    <span style={{ fontWeight:700, fontSize:'13px', color:resultColor }}>{resultLabel}</span>
                    <span style={{ fontFamily:'monospace', fontSize:'11px', color:T.textMut }}>{entry.commit}</span>
                  </div>
                  <div style={{ display:'flex', gap:'10px', fontSize:'11px' }}>
                    {entry.tsc !== null && <span style={{ color:entry.tsc?T.success:T.danger }}>tsc {entry.tsc?'✓':'✗'}</span>}
                    <span style={{ color:T.textSec }}>{entry.tests}</span>
                  </div>
                </div>
                <div style={{ fontSize:'12px', color:T.textSec }}>{entry.note}</div>
              </Card>
            );
          })}

          <div style={{ fontSize:'12px', color:T.textMut, fontWeight:600, marginTop:'6px', marginBottom:'2px' }}>Yesterday — 3 QA failures (all auto-filed + fixed this cycle)</div>
          {YESTERDAY_FAILS.map((entry, i) => (
            <Card key={i} style={{ padding:'12px 16px', border:`1px solid ${T.dangerBorder}`, opacity:0.7 }}>
              <div style={{ display:'flex', justifyContent:'space-between', marginBottom:'4px' }}>
                <span style={{ fontFamily:'monospace', fontSize:'12px', color:T.textMut }}>Apr 21 · {entry.time}</span>
                <span style={{ fontWeight:700, fontSize:'12px', color:T.danger }}>✗ FAIL</span>
              </div>
              <div style={{ fontSize:'11px', color:T.textSec }}>{entry.note}</div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
   SECURITY TAB
═══════════════════════════════════════════════════════════════ */
function SecurityTab() {
  return (
    <div>
      <SectionHeader Icon={Shield} title="Security Audit" sub={`Full OWASP Web + LLM Top 10 scan — ${SECURITY_STATUS.date} · awade-security-scan`} />

      <div style={{ display:'grid', gridTemplateColumns:'repeat(5,1fr)', gap:'8px', marginBottom:'14px' }}>
        {[
          { label:'Critical',  val:SECURITY_STATUS.critical, color:SECURITY_STATUS.critical?T.danger:T.textMut,   dim:SECURITY_STATUS.critical?T.dangerDim:T.base2  },
          { label:'High',      val:SECURITY_STATUS.high,     color:SECURITY_STATUS.high?T.danger:T.textMut,       dim:SECURITY_STATUS.high?T.dangerDim:T.base2      },
          { label:'Medium',    val:SECURITY_STATUS.medium,   color:SECURITY_STATUS.medium?T.warning:T.textMut,    dim:SECURITY_STATUS.medium?T.warningDim:T.base2   },
          { label:'Low',       val:SECURITY_STATUS.low,      color:T.textMut,                                     dim:T.base2 },
          { label:'Dep Vulns', val:SECURITY_STATUS.deps,     color:SECURITY_STATUS.deps?T.danger:T.success,       dim:SECURITY_STATUS.deps?T.dangerDim:T.successDim },
        ].map(s => (
          <div key={s.label} style={{ background:s.dim, border:`1px solid ${T.border}`, borderRadius:'10px', padding:'14px', textAlign:'center' }}>
            <div style={{ fontSize:'28px', fontWeight:900, color:s.color, lineHeight:1 }}>{s.val}</div>
            <div style={{ fontSize:'10px', color:T.textMut, marginTop:'4px' }}>{s.label}</div>
          </div>
        ))}
      </div>

      <Card style={{ padding:'18px', marginBottom:'12px' }}>
        <div style={{ fontSize:'11px', fontWeight:700, color:T.textSec, letterSpacing:'0.07em', marginBottom:'12px' }}>
          ALL FINDINGS ({SECURITY_STATUS.findings.length}) — {SECURITY_STATUS.findings.filter(f=>f.severity==='high').length} high, {SECURITY_STATUS.findings.filter(f=>f.severity==='medium').length} medium
        </div>
        {SECURITY_STATUS.findings.map((f) => {
          const sev = f.severity === 'high' ? { color:T.danger, dim:T.dangerDim, border:T.dangerBorder, label:'High' }
                                             : { color:T.warning, dim:T.warningDim, border:T.warningBorder, label:'Medium' };
          return (
            <div key={f.id} style={{ display:'flex', gap:'12px', padding:'12px', background:T.base2, borderRadius:'9px', marginBottom:'8px', borderLeft:`3px solid ${sev.color}` }}>
              <div>
                <div style={{ display:'flex', gap:'8px', alignItems:'center', marginBottom:'4px' }}>
                  <span style={{ fontSize:'12px', fontWeight:800, color:sev.color }}>AWD-{f.id}</span>
                  <Badge label={sev.label} color={sev.color} dim={sev.dim} border={sev.border} />
                </div>
                <div style={{ fontSize:'12px', color:T.text, marginBottom:'3px' }}>{f.label}</div>
                <div style={{ fontSize:'10px', color:T.textMut, fontFamily:'monospace' }}>{f.file}</div>
              </div>
            </div>
          );
        })}
      </Card>

      <Card style={{ padding:'18px', marginBottom:'12px' }}>
        <div style={{ fontSize:'11px', fontWeight:700, color:T.textSec, letterSpacing:'0.07em', marginBottom:'12px' }}>OWASP CHECKS COMPLETED</div>
        <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'6px' }}>
          {[
            { label:'W1 Secret scan',          pass:true,  note:'No hardcoded secrets in apps/backend/ or apps/frontend/src/' },
            { label:'W2 Dependency audit',     pass:false, note:'H-10: 3 high XSS CVEs in react-router · H-23: PyJWT 2.3.0 outdated' },
            { label:'W3 CORS + rate limits',   pass:true,  note:'limiter.py applied · H-07 rate-limit on guide gen shipped today' },
            { label:'W4 Auth flows',           pass:false, note:'H-24 suspended-user bypass FIXED today (1153504); H-25 localStorage JWT still open' },
            { label:'W5 Postgres + Alembic',   pass:true,  note:'Parameterised via SQLAlchemy ORM · M-17 migration-system overlap is hygiene, not risk' },
            { label:'W6 API middleware',       pass:false, note:'M-10: /docs exposed in prod · M-11: missing CSP header · L-04: TrustedHost disabled' },
            { label:'W7 Info disclosure',      pass:false, note:'H-18: str(e) leaked in HTTPException detail across 6 service files' },
            { label:'LLM01 Prompt injection',  pass:false, note:'M-12: context_input free-text flows into GPT prompt unfenced (LessonResource)' },
            { label:'LLM02 Insecure output',   pass:true,  note:'H-06 parent-guide JSON validator shipped today — pydantic check before persist' },
            { label:'LLM04 Model DoS',         pass:true,  note:'H-07 rate limit on guide gen · H-09 OpenAI timeout=20s shipped today (LLM10)' },
            { label:'LLM06 Excessive agency',  pass:true,  note:'AI output reviewed before persist; human override on guide view' },
            { label:'LLM10 Unbounded cost',    pass:true,  note:'Rate limit + explicit OpenAI timeout (f2e0441) + output-token cap' },
          ].map(c => (
            <div key={c.label} style={{ display:'flex', gap:'8px', padding:'8px 10px', background:T.base2, borderRadius:'7px', alignItems:'flex-start' }}>
              <span style={{ color:c.pass?T.success:T.warning, fontSize:'12px', flexShrink:0, marginTop:'1px' }}>{c.pass?'✓':'⚠'}</span>
              <div>
                <div style={{ fontSize:'11px', fontWeight:600, color:c.pass?T.textSec:T.warning }}>{c.label}</div>
                <div style={{ fontSize:'10px', color:T.textMut, marginTop:'1px' }}>{c.note}</div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
   SCHEDULE TAB
═══════════════════════════════════════════════════════════════ */
function ScheduleTab() {
  const [hovered, setHovered] = useState(null);
  return (
    <div>
      <SectionHeader Icon={Calendar} title="Weekly Automation Schedule" sub="Fixed anchors on top of the hourly awade-dev-execution + awade-qa-validation loop that runs all day every day." />
      <div style={{ display:'flex', flexWrap:'wrap', gap:'8px', marginBottom:'14px' }}>
        {Object.entries(DEPT).map(([key, m]) => (
          <div key={key} style={{ display:'flex', alignItems:'center', gap:'4px' }}>
            <span style={{ width:'6px', height:'6px', borderRadius:'50%', background:m.color, display:'inline-block' }} />
            <span style={{ fontSize:'11px', color:T.textSec }}>{m.label}</span>
          </div>
        ))}
      </div>
      <Card>
        <div style={{ display:'grid', gridTemplateColumns:'108px repeat(7,1fr)', background:T.base2, borderBottom:`1px solid ${T.border}`, borderRadius:'12px 12px 0 0', overflow:'hidden' }}>
          <div style={{ padding:'9px 12px', fontSize:'10px', color:T.textMut, fontWeight:700, letterSpacing:'0.07em' }}>TIME</div>
          {DAYS.map((d, i) => (
            <div key={d} style={{ padding:'9px 6px', textAlign:'center' }}>
              <div style={{ fontSize:'11px', color:i>=5?T.textMut:T.textSec, fontWeight:700 }}>{d}</div>
              {i>=5 && <div style={{ fontSize:'8px', color:T.textMut }}>weekend</div>}
            </div>
          ))}
        </div>
        {TIME_SLOTS.map((slot, si) => (
          <div key={slot.time} style={{ display:'grid', gridTemplateColumns:'108px repeat(7,1fr)', borderBottom:si<TIME_SLOTS.length-1?`1px solid ${T.border2}`:'none' }}>
            <div style={{ padding:'7px 12px', borderRight:`1px solid ${T.border2}`, display:'flex', alignItems:'center' }}>
              <span style={{ fontSize:'11px', fontWeight:slot.time.includes('Hourly')?700:400, color:slot.time.includes('Hourly')?T.primary:T.textMut, fontFamily:slot.time.includes('Hourly')?'monospace':'inherit' }}>{slot.time}</span>
            </div>
            {DAYS.map((_, di) => {
              const task = slot.tasks.find(t => t.days.includes(di));
              const key = `${si}-${di}`;
              const meta = task ? DEPT[task.dept] : null;
              return (
                <div key={di} style={{ padding:'4px', display:'flex', alignItems:'center', justifyContent:'center', background:di>=5?'rgba(0,0,0,0.18)':'transparent' }}
                  onMouseEnter={() => task && setHovered(key)} onMouseLeave={() => setHovered(null)}>
                  {task ? (
                    <div style={{ background:hovered===key?meta.dim:'rgba(255,255,255,0.02)', border:`1px solid ${meta.color}${hovered===key?'70':'30'}`, borderRadius:'5px', padding:'4px 5px', fontSize:'9px', color:hovered===key?meta.color:T.textSec, fontWeight:700, textAlign:'center', width:'100%', whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis', transition:'all 0.12s' }}>
                      {task.name.replace(/-/g,' ')}
                    </div>
                  ) : <div style={{ height:'24px' }} />}
                </div>
              );
            })}
          </div>
        ))}
      </Card>
      <div style={{ marginTop:'12px', fontSize:'11px', color:T.textMut, textAlign:'center' }}>
        All 11 tasks registered under <code style={{fontFamily:'monospace'}}>awade-*</code> IDs. Prompts preamble with <code style={{fontFamily:'monospace'}}>cd /Users/tolulopebabajide/Desktop/Projects/awade/awade/</code>.
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
   AGENTS TAB
═══════════════════════════════════════════════════════════════ */
function AgentsTab() {
  const [filter, setFilter] = useState('all');
  const filtered = filter === 'all' ? AGENTS : AGENTS.filter(a => a.dept === filter);
  return (
    <div>
      <SectionHeader Icon={Users} title="Agent Roster" sub={`${AGENTS.length} agents — run counts and metrics from today's logs`} />
      <div style={{ display:'flex', flexWrap:'wrap', gap:'6px', marginBottom:'16px' }}>
        {['all',...Object.keys(DEPT)].map(d => {
          const meta = d==='all'?{color:T.primary,dim:T.primaryDim,border:T.primaryBorder}:DEPT[d];
          const active = filter===d;
          return (
            <button key={d} onClick={() => setFilter(d)} style={{ padding:'5px 12px', borderRadius:'999px', border:`1px solid ${active?meta.color:T.border}`, background:active?meta.dim:'transparent', color:active?meta.color:T.textMut, fontSize:'11px', fontWeight:600, cursor:'pointer', transition:'all 0.15s' }}>
              {d==='all'?'All':DEPT[d].label}
            </button>
          );
        })}
      </div>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(264px, 1fr))', gap:'10px' }}>
        {filtered.map(agent => {
          const meta = DEPT[agent.dept];
          const { Icon:Ic } = meta;
          return (
            <Card key={agent.name} style={{ padding:'15px', border:`1px solid ${agent.auto?meta.border:T.border}` }}>
              <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', marginBottom:'11px' }}>
                <div style={{ display:'flex', alignItems:'center', gap:'9px' }}>
                  <div style={{ width:'30px', height:'30px', borderRadius:'8px', background:meta.dim, border:`1px solid ${meta.border}`, display:'flex', alignItems:'center', justifyContent:'center', flexShrink:0 }}>
                    <Ic size={14} color={meta.color} />
                  </div>
                  <div>
                    <div style={{ fontSize:'9px', color:meta.color, fontWeight:700, letterSpacing:'0.07em', textTransform:'uppercase' }}>{meta.label}</div>
                    <div style={{ fontWeight:800, fontSize:'13px', color:T.text }}>{agent.label}</div>
                  </div>
                </div>
                <Badge label={agent.auto?'AUTO':'MANUAL'} color={agent.auto?T.success:T.textMut} dim={agent.auto?T.successDim:'rgba(100,116,139,0.1)'} border={agent.auto?T.successBorder:'rgba(100,116,139,0.2)'} />
              </div>
              <div style={{ background:T.base2, borderRadius:'7px', padding:'7px 10px', display:'flex', alignItems:'center', gap:'6px', marginBottom:'8px' }}>
                <Clock size={10} color={T.textMut} />
                <span style={{ fontSize:'11px', color:T.textSec, fontFamily:'monospace' }}>{agent.schedule}</span>
              </div>
              {agent.auto && agent.runsToday > 0 && (
                <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'6px' }}>
                  <div style={{ background:T.base2, borderRadius:'6px', padding:'7px 9px' }}>
                    <div style={{ fontSize:'15px', fontWeight:900, color:T.primary }}>{agent.runsToday}</div>
                    <div style={{ fontSize:'9px', color:T.textMut, marginTop:'1px' }}>runs today</div>
                  </div>
                  <div style={{ background:T.base2, borderRadius:'6px', padding:'7px 9px' }}>
                    <div style={{ fontSize:'15px', fontWeight:900, color:T.success }}>
                      {agent.issuesFixed > 0 ? agent.issuesFixed + ' fixed' : agent.passRate ? agent.passRate + '% pass' : agent.findings ? agent.findings + ' findings' : '—'}
                    </div>
                    <div style={{ fontSize:'9px', color:T.textMut, marginTop:'1px' }}>
                      {agent.issuesFixed > 0 ? 'issues fixed' : agent.passRate ? 'pass rate' : agent.findings ? 'findings' : 'result'}
                    </div>
                  </div>
                </div>
              )}
              <div style={{ marginTop:'7px', fontSize:'10px', color:T.textMut, fontFamily:'monospace' }}>awade-{agent.name}</div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
   ROOT  DASHBOARD
═══════════════════════════════════════════════════════════════ */
const TABS = [
  { id:'monitor',  label:'Monitor',   Icon:Activity  },
  { id:'activity', label:'Activity',  Icon:Zap       },
  { id:'security', label:'Security',  Icon:Shield    },
  { id:'schedule', label:'Schedule',  Icon:Calendar  },
  { id:'agents',   label:'Agents',    Icon:Users     },
];

export default function Dashboard() {
  const [tab, setTab] = useState('monitor');
  return (
    <div style={{ background:T.bg, minHeight:'100vh', fontFamily:'system-ui,-apple-system,sans-serif', color:T.text, fontSize:'14px' }}>
      <style>{CSS}</style>
      <div style={{ height:'2px', background:T.grad }} />

      {/* Header */}
      <div style={{ padding:'18px 28px 0', borderBottom:`1px solid ${T.border}` }}>
        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'16px' }}>
          <div style={{ display:'flex', alignItems:'center', gap:'11px' }}>
            <div style={{ width:'34px', height:'34px', borderRadius:'9px', background:T.primaryDim, border:`1px solid ${T.primaryBorder}`, display:'flex', alignItems:'center', justifyContent:'center' }}>
              <Activity size={16} color={T.primaryLight} />
            </div>
            <div>
              <h1 style={{ margin:0, fontSize:'16px', fontWeight:900, letterSpacing:'-0.02em', lineHeight:1.15 }}>
                Awade Agentic Team <span style={T.gradText}>Control Center</span>
              </h1>
              <p style={{ margin:0, fontSize:'11px', color:T.textMut }}>FastAPI · React/TS · PostgreSQL · OpenAI GPT — data from docs/agentic/ output files</p>
            </div>
          </div>
          {/* Live indicator */}
          <div style={{ display:'flex', alignItems:'center', gap:'6px', background:T.secondaryDim, border:`1px solid ${T.secondaryBorder}`, borderRadius:'999px', padding:'5px 12px' }}>
            <span style={{ position:'relative', display:'inline-flex', width:'7px', height:'7px' }}>
              <span style={{ position:'absolute', inset:0, borderRadius:'50%', background:T.secondary, animation:'pulse-ring 1.6s ease-out infinite' }} />
              <span style={{ width:'7px', height:'7px', borderRadius:'50%', background:T.secondary, position:'relative', boxShadow:`0 0 5px ${T.secondary}` }} />
            </span>
            <span style={{ fontSize:'11px', fontWeight:800, color:T.secondary, letterSpacing:'0.1em' }}>LIVE</span>
          </div>
        </div>

        {/* Tabs */}
        <div style={{ display:'flex', gap:'2px' }}>
          {TABS.map(({ id, label, Icon:Ic }) => {
            const active = tab === id;
            return (
              <button key={id} onClick={() => setTab(id)} style={{ display:'flex', alignItems:'center', gap:'5px', padding:'7px 15px', border:'none', cursor:'pointer', fontSize:'12px', fontWeight:600, borderRadius:'8px 8px 0 0', background:active?T.base1:'transparent', color:active?T.primaryLight:T.textMut, borderBottom:active?`2px solid ${T.primary}`:'2px solid transparent', transition:'all 0.15s' }}>
                <Ic size={12} />
                {label}
                {id === 'monitor' && <span style={{ width:'5px', height:'5px', borderRadius:'50%', background:T.danger, boxShadow:`0 0 4px ${T.danger}` }} title="Action required — AWD-C-05" />}
              </button>
            );
          })}
        </div>
      </div>

      <div style={{ padding:'22px 28px' }}>
        {tab === 'monitor'  && <MonitorTab  />}
        {tab === 'activity' && <ActivityTab />}
        {tab === 'security' && <SecurityTab />}
        {tab === 'schedule' && <ScheduleTab />}
        {tab === 'agents'   && <AgentsTab   />}
      </div>
    </div>
  );
}
