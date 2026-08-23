// Direction C — remaining views (Pulse, Roster, Pipeline) and detail panels.

const { useState: useStR, useEffect: useEfR, useMemo: useMmR } = React;

/* ──────────────────────────────────────────────────────────────────────
   PULSE view — activity stream + failure digest + upcoming + hourly loop
   (R-P1.1, R-P1.2, R10)
   ────────────────────────────────────────────────────────────────────── */
function PulseViewC({ T, events, failures }) {
  return (
    <div style={{flex:1, overflow:'auto', padding:'18px 24px 28px'}}>
      <div style={{display:'grid', gridTemplateColumns:'1fr 340px', gap:18, alignItems:'start'}}>

        {/* LEFT — Activity stream */}
        <div>
          <SectionHeaderC T={T} title="Activity stream" subtitle="Newest first" live/>
          <div style={{background:T.panel, border:`1px solid ${T.border}`, borderRadius:10, overflow:'hidden'}}>
            {events.slice(0, 26).map((e, i) => (
              <EventRowC key={e.id} T={T} e={e} last={i === events.slice(0,26).length - 1}/>
            ))}
          </div>
        </div>

        {/* RIGHT */}
        <div style={{display:'flex', flexDirection:'column', gap:16}}>

          {/* R-P1.1 — Failure digest */}
          <div>
            <SectionHeaderC T={T} title="What broke · 24h" subtitle={`${failures.length} event${failures.length === 1 ? '' : 's'}`}/>
            <div style={{
              background:T.panel, border:`1px solid ${failures.length > 0 ? 'rgba(239,68,68,.3)' : T.border}`,
              borderRadius:10, padding: failures.length > 0 ? '4px 0' : 16,
            }}>
              {failures.length === 0 ? (
                <div style={{textAlign:'center', color:T.sub, fontSize:12}}>
                  <span style={{color:'#10b981', fontSize:18, marginRight:5}}>✓</span> Nothing broke in 24h.
                </div>
              ) : failures.map((e, i) => (
                <div key={e.id} style={{
                  padding:'9px 13px', borderBottom: i < failures.length - 1 ? `1px solid ${T.border}` : 'none',
                  display:'flex', gap:8, alignItems:'flex-start',
                }}>
                  <span style={{
                    width:8, height:8, borderRadius:'50%', background:'#ef4444',
                    marginTop:6, flexShrink:0,
                  }}/>
                  <div style={{flex:1, minWidth:0}}>
                    <div style={{display:'flex', alignItems:'baseline', gap:6}}>
                      <code style={{fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:10.5, fontWeight:600, color:T.text}}>{e.who}</code>
                      <span style={{flex:1}}/>
                      <span style={{fontSize:10, color:T.faint}}>{e.age}</span>
                    </div>
                    <div style={{fontSize:11.5, color:T.sub, lineHeight:1.4, marginTop:2}}>{e.summary}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* R10 — Hourly loop reflects real run status (not clock) */}
          <div>
            <SectionHeaderC T={T} title="Hourly self-healing loop" subtitle="dev → review → qa → refresh"/>
            <div style={{background:T.panel, border:`1px solid ${T.border}`, borderRadius:10, padding:10, display:'flex', flexDirection:'column', gap:6}}>
              {HOURLY_LOOP.map((s, i) => {
                const failed = s.status === 'fail';
                const tint = failed ? '#ef4444' : '#10b981';
                return (
                  <div key={i} style={{
                    display:'flex', alignItems:'center', gap:9,
                    padding:'7px 9px', borderRadius:7,
                    background: failed ? 'rgba(239,68,68,.06)' : T.panel2,
                    border:`1px solid ${failed ? 'rgba(239,68,68,.3)' : T.border}`,
                  }}>
                    <code style={{
                      fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:11, fontWeight:700,
                      color:tint, background:tint+'18',
                      padding:'2px 7px', borderRadius:4, flexShrink:0,
                    }}>{s.at}</code>
                    <div style={{flex:1, minWidth:0}}>
                      <div style={{fontSize:12, fontWeight:600, color:T.text}}>{s.name}</div>
                      <div style={{fontSize:10.5, color:T.mute, lineHeight:1.4, marginTop:1, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap'}}>
                        {s.result}
                      </div>
                    </div>
                    {failed && (
                      <span style={{fontSize:9.5, fontWeight:700, color:'#ef4444', padding:'1px 6px', borderRadius:3, background:'rgba(239,68,68,.14)', textTransform:'uppercase', letterSpacing:.05}}>fail</span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* R-P1.2 — Upcoming runs */}
          <div>
            <SectionHeaderC T={T} title="Up next" subtitle="from cron · pre-computed"/>
            <div style={{background:T.panel, border:`1px solid ${T.border}`, borderRadius:10, overflow:'hidden'}}>
              {UPCOMING_RUNS.slice(0, 8).map((u, i) => (
                <div key={i} style={{
                  padding:'7px 13px', borderBottom: i < 7 ? `1px solid ${T.border}` : 'none',
                  display:'flex', alignItems:'center', gap:8,
                  opacity: u.past ? .55 : 1,
                }}>
                  <code style={{
                    fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:10, fontWeight:700,
                    color:T.accent, background:T.accentSoft, padding:'2px 6px', borderRadius:3,
                    flexShrink:0, minWidth:64, textAlign:'center',
                  }}>{u.when}</code>
                  <div style={{flex:1, minWidth:0}}>
                    <code style={{fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:11, color:T.text, fontWeight:600}}>{u.agent}</code>
                    <div style={{fontSize:10, color:T.mute, marginTop:1}}>{u.at}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}

function EventRowC({ T, e, last }) {
  const statusColor = e.status === 'fail' ? '#ef4444' : e.status === 'done' ? '#10b981' : T.sub;
  return (
    <div style={{
      padding:'10px 14px', borderBottom: last ? 'none' : `1px solid ${T.border}`,
      display:'flex', gap:10, alignItems:'flex-start',
    }}>
      <div style={{width:7, height:7, borderRadius:'50%', background:statusColor, marginTop:6, flexShrink:0}}/>
      <div style={{flex:1, minWidth:0}}>
        <div style={{display:'flex', alignItems:'center', gap:6, marginBottom:2}}>
          <code style={{fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:11.5, fontWeight:600, color:T.text}}>{e.who}</code>
          {e.status === 'fail' && (
            <span style={{fontSize:9.5, padding:'1px 6px', borderRadius:3, fontWeight:700, textTransform:'uppercase', letterSpacing:.04, background:'rgba(239,68,68,.16)', color:'#ef4444'}}>fail</span>
          )}
          <span style={{flex:1}}/>
          <span style={{fontSize:10.5, color:T.faint}}>{e.age}</span>
        </div>
        <div style={{fontSize:12, color:T.sub, lineHeight:1.4}}>{e.summary}</div>
      </div>
    </div>
  );
}

function SectionHeaderC({ T, title, subtitle, live }) {
  return (
    <div style={{display:'flex', alignItems:'baseline', gap:8, marginBottom:8}}>
      <span style={{fontWeight:700, fontSize:13, color:T.text, letterSpacing:-0.1}}>{title}</span>
      {subtitle && <span style={{fontSize:11, color:T.mute}}>· {subtitle}</span>}
      {live && (
        <span style={{marginLeft:'auto', display:'inline-flex', alignItems:'center', gap:5, fontSize:10.5, color:'#10b981', fontWeight:600}}>
          <span style={{width:6, height:6, borderRadius:'50%', background:'#10b981', boxShadow:'0 0 0 3px rgba(16,185,129,.2)'}}/>
          live
        </span>
      )}
    </div>
  );
}

/* ──────────────────────────────────────────────────────────────────────
   ROSTER — Direction A's department org chart (R5, R8, R-P1.5, R-P1.6)
   ────────────────────────────────────────────────────────────────────── */
function RosterViewC({ T, statusCounts, agentFilter, setAgentFilter, agentQuery, setAgentQuery,
                      onSelectAgent, runAgent, runningAgent, search }) {
  // top-bar search applies broadly; combine with the in-view filters
  const effectiveQuery = (search || agentQuery || '').toLowerCase();

  const statuses = [
    { id:'all',        label:'All',        n: AGENTS.length },
    { id:'healthy',    label:'Healthy',    n: statusCounts.healthy,    tint:'#10b981' },
    { id:'warning',    label:'Warning',    n: statusCounts.warning,    tint:'#f59e0b' },
    { id:'critical',   label:'Critical',   n: statusCounts.critical,   tint:'#ef4444' },
    { id:'idle',       label:'Idle',       n: statusCounts.idle,       tint:'#a1a1aa' },
    { id:'on-demand',  label:'On-demand',  n: statusCounts['on-demand'], tint:'#60a5fa' },
  ];

  return (
    <div style={{flex:1, overflow:'auto', padding:'18px 24px 28px'}}>
      <SectionHeaderC T={T} title="The team" subtitle="33 agents · 9 departments"/>
      <div style={{display:'flex', gap:7, marginBottom:14, alignItems:'center', flexWrap:'wrap'}}>
        {statuses.map(s => {
          const active = agentFilter === s.id;
          return (
            <button key={s.id} onClick={() => setAgentFilter(s.id)} style={{
              padding:'4px 11px', borderRadius:7, fontSize:11.5, fontWeight:600,
              border:`1px solid ${active ? T.accentBorder : T.border}`,
              background: active ? T.accentSoft : T.panel,
              color: active ? T.accent : T.sub,
              cursor:'pointer', display:'inline-flex', alignItems:'center', gap:6,
            }}>
              {s.tint && <span style={{width:6, height:6, borderRadius:'50%', background:s.tint}}/>}
              <span>{s.label}</span>
              <span style={{fontSize:10.5, opacity:.7, fontVariantNumeric:'tabular-nums'}}>{s.n}</span>
            </button>
          );
        })}
        <div style={{flex:1}}/>
        {!search && (
          <input
            placeholder="Filter within roster…" value={agentQuery} onChange={e => setAgentQuery(e.target.value)}
            style={{
              padding:'5px 11px', borderRadius:7, fontSize:11.5, minWidth:220,
              border:`1px solid ${T.border}`, background:T.panel, color:T.text, outline:'none',
            }}/>
        )}
      </div>

      <div style={{display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap:12}}>
        {DEPARTMENTS.map(d => (
          <DeptCardC key={d.id} T={T} dept={d}
            statusFilter={agentFilter} query={effectiveQuery}
            onSelectAgent={onSelectAgent} runAgent={runAgent} runningAgent={runningAgent}/>
        ))}
      </div>
    </div>
  );
}

function DeptCardC({ T, dept, statusFilter, query, onSelectAgent, runAgent, runningAgent }) {
  const agents = dept.agents.map(name => AGENT_BY_NAME[name]).filter(Boolean).filter(a => {
    if (statusFilter !== 'all' && a.status !== statusFilter) return false;
    if (query && !(a.name + ' ' + dept.name).toLowerCase().includes(query)) return false;
    return true;
  });
  if (agents.length === 0) return null;
  const counts = agents.reduce((acc, a) => { acc[a.status] = (acc[a.status] || 0) + 1; return acc; }, {});
  const hasIssue = (counts.warning || 0) + (counts.critical || 0) > 0;
  return (
    <div style={{
      background:T.panel,
      border:`1px solid ${hasIssue ? 'rgba(245,158,11,.45)' : T.border}`,
      borderRadius:10, padding:'12px 13px', boxShadow:T.shadow,
    }}>
      <div style={{display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:9}}>
        <span style={{fontWeight:700, fontSize:12.5, color:T.text}}>{dept.name}</span>
        <span style={{fontSize:10.5, color:T.mute, fontVariantNumeric:'tabular-nums'}}>{agents.length}/{dept.agents.length}</span>
      </div>
      <div style={{display:'flex', flexDirection:'column', gap:4}}>
        {agents.map(a => <AgentChip key={a.name} T={T} a={a}
          running={runningAgent === a.name}
          onSelect={() => onSelectAgent(a)}
          onRun={() => runAgent(a.name)}/>)}
      </div>
    </div>
  );
}

function AgentChip({ T, a, running, onSelect, onRun }) {
  const [hover, setHover] = useStR(false);
  const render = AGENT_RENDER[a.name];
  const renderStyle = render && RENDER_STYLE[render.renderAs];
  const dotColor = renderStyle ? renderStyle.dot : STATUS_C[a.status];
  const runs = AGENT_RUNS_24H[a.name];
  const isNeverRan = a.lastRun === 'never';
  return (
    <div onMouseEnter={()=>setHover(true)} onMouseLeave={()=>setHover(false)}
      onClick={onSelect} style={{
      display:'flex', alignItems:'center', gap:8, padding:'5px 8px', borderRadius:6,
      cursor:'pointer', background:T.panel2,
      border:`1px solid ${hover ? T.accentBorder : T.border}`,
    }}>
      <span style={{
        width:7, height:7, borderRadius:'50%', background:dotColor, flexShrink:0,
        boxShadow: running ? `0 0 0 3px ${dotColor}55` : (renderStyle?.renderAs === 'standby' ? `0 0 0 2px ${dotColor}22` : 'none'),
        animation: running ? 'pulseDot 1s infinite' : 'none',
      }}/>
      <span style={{flex:1, fontSize:11.5, color:T.text, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap'}}>{a.name}</span>
      {render && (
        <span title={render.label} style={{
          fontSize:9, fontWeight:700, color:T.mute, padding:'1px 5px', borderRadius:3,
          background:T.bg, border:`1px solid ${T.border}`, textTransform:'uppercase', letterSpacing:.04, whiteSpace:'nowrap',
        }}>{renderStyle.label}</span>
      )}
      {!render && runs > 0 && (
        <span title={`${runs} runs in 24h`} style={{
          fontSize:9.5, color:T.mute, padding:'1px 5px', borderRadius:3,
          background:T.panel, border:`1px solid ${T.border}`, fontVariantNumeric:'tabular-nums',
        }}>{runs}×</span>
      )}
      <span style={{fontSize:10, color: isNeverRan ? '#10b981' : T.faint, whiteSpace:'nowrap'}}>
        {isNeverRan ? '— standby —' : a.lastRun}
      </span>
      {hover && (
        <button onClick={(e) => { e.stopPropagation(); onRun(); }} title="Run now" style={{
          padding:'2px 6px', borderRadius:4, border:`1px solid ${T.accent}`, background:T.accent, color:'#fff',
          fontSize:10, fontWeight:600, cursor:'pointer', whiteSpace:'nowrap',
        }}>▶ Run</button>
      )}
    </div>
  );
}

/* ──────────────────────────────────────────────────────────────────────
   PIPELINE — with a Done column (R-P1.4)
   ────────────────────────────────────────────────────────────────────── */
function PipelineViewC({ T, onSelectBacklog, search }) {
  // Synthesise some done items so the column shows life. In the real
  // dashboard, build-dashboard.py reads recent docs/sprints/dev-log.md
  // entries with stage=done.
  const doneRecent = [
    { id:'H-118', sev:'high',   area:'Engineering', stage:'done', title:'Fix race in BillingFlow useEffect', owner:'dev-agent',     files:'app/billing/BillingFlow.tsx', age:'1m',  filedBy:'dev-execution' },
    { id:'M-41',  sev:'medium', area:'Engineering', stage:'done', title:'Normalise /api/users response shape', owner:'dev-agent',   files:'app/api/users/*',             age:'2h',  filedBy:'dev-execution' },
    { id:'L-20',  sev:'low',    area:'SEO',         stage:'done', title:'Add OG cards to docs pages',           owner:'seo-agent', files:'app/docs/*',                  age:'8h',  filedBy:'dev-execution' },
    { id:'M-40',  sev:'medium', area:'Tech Debt',   stage:'done', title:'Drop unused logger transport',          owner:'dev-agent', files:'app/lib/log/*',               age:'18h', filedBy:'dev-execution' },
    { id:'L-19',  sev:'low',    area:'UX',          stage:'done', title:'Fix dark-mode contrast on muted text',  owner:'design-agent', files:'app/styles/*',             age:'20h', filedBy:'dev-execution' },
    { id:'M-39',  sev:'medium', area:'Engineering', stage:'done', title:'Audit log timestamps timezone-aware',    owner:'dev-agent', files:'app/audit/*',                age:'22h', filedBy:'dev-execution' },
    { id:'M-38',  sev:'medium', area:'Engineering', stage:'done', title:'One-click handshake retry on 503',       owner:'dev-agent', files:'scripts/dashboard-server.py', age:'1d', filedBy:'dev-execution' },
  ];
  const allItems = [...BACKLOG, ...doneRecent];
  const stages = [...PIPELINE_STAGES, 'done'];
  const filtered = useMmR(() => {
    if (!search) return allItems;
    const q = search.toLowerCase();
    return allItems.filter(b => (b.id + ' ' + b.title + ' ' + b.area + ' ' + b.owner).toLowerCase().includes(q));
  }, [search]);

  return (
    <div style={{flex:1, overflow:'auto', padding:'18px 24px 28px'}}>
      <SectionHeaderC T={T} title="Pipeline" subtitle={`${BACKLOG.length} open · ${doneRecent.length} done · 24h`}/>
      <div style={{display:'grid', gridTemplateColumns:`repeat(${stages.length}, minmax(170px, 1fr))`, gap:10, minWidth: stages.length * 180}}>
        {stages.map(stage => {
          const items = filtered.filter(b => b.stage === stage);
          const isDone = stage === 'done';
          return (
            <div key={stage} style={{
              background:T.panel,
              border:`1px solid ${isDone ? 'rgba(16,185,129,.3)' : T.border}`,
              borderRadius:9, padding:9,
              display:'flex', flexDirection:'column', gap:7, minHeight:280,
            }}>
              <div style={{display:'flex', alignItems:'center', justifyContent:'space-between', padding:'2px 4px 6px'}}>
                <span style={{fontSize:11, fontWeight:700, color: isDone ? '#10b981' : T.text, textTransform:'capitalize', display:'inline-flex', alignItems:'center', gap:5}}>
                  {isDone && <span>✓</span>}{stage}
                </span>
                <span style={{fontSize:10.5, color:T.mute, fontVariantNumeric:'tabular-nums'}}>{items.length}</span>
              </div>
              {items.map(b => <PipelineCard key={b.id} T={T} b={b} onSelect={() => onSelectBacklog(b)}/>)}
              {items.length === 0 && (
                <div style={{padding:'14px 8px', textAlign:'center', color:T.faint, fontSize:10.5, border:`1px dashed ${T.border}`, borderRadius:6}}>empty</div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
function PipelineCard({ T, b, onSelect }) {
  const sevColor = { critical:'#dc2626', high:'#ef4444', medium:'#f59e0b', low:'#10b981' }[b.sev] || T.sub;
  const isDone = b.stage === 'done';
  return (
    <div onClick={onSelect} style={{
      background:T.panel2, border:`1px solid ${T.border}`, borderRadius:7, padding:'8px 9px',
      cursor:'pointer', borderLeft:`3px solid ${isDone ? '#10b981' : sevColor}`,
      opacity: isDone ? .85 : 1,
    }}
    onMouseEnter={e => e.currentTarget.style.borderColor = T.accentBorder}
    onMouseLeave={e => e.currentTarget.style.borderColor = T.border}>
      <div style={{display:'flex', alignItems:'center', gap:5}}>
        <code style={{fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:10, color:T.mute, fontWeight:600}}>{b.id}</code>
        <span style={{flex:1}}/>
        <span style={{fontSize:9.5, color:T.faint}}>{b.age}</span>
      </div>
      <div style={{fontSize:11.5, color:T.text, marginTop:3, lineHeight:1.35, textDecoration: isDone ? 'line-through' : 'none', textDecorationColor: T.faint}}>{b.title}</div>
      <div style={{display:'flex', alignItems:'center', gap:5, marginTop:5, fontSize:10, color:T.mute}}>
        <span>{b.area}</span>
      </div>
    </div>
  );
}

/* ──────────────────────────────────────────────────────────────────────
   AGENT PANEL (R-P1.3 — per-agent recent runs; R-P1.7 — Pause/Reschedule)
   ────────────────────────────────────────────────────────────────────── */
function AgentPanel({ T, agent, onClose, runAgent, runningAgent, events }) {
  const running = runningAgent === agent.name;
  const render = AGENT_RENDER[agent.name];
  const renderStyle = render && RENDER_STYLE[render.renderAs];
  const dotColor = renderStyle ? renderStyle.dot : STATUS_C[agent.status];
  const runs = AGENT_RUNS_24H[agent.name] ?? 0;
  const dept = DEPARTMENTS.find(d => d.id === agent.dept);

  // Per-agent activity
  const myEvents = events.filter(e => e.who === agent.name);

  return (
    <div onClick={onClose} style={{
      position:'absolute', inset:0, background:'rgba(0,0,0,.4)', backdropFilter:'blur(2px)',
      display:'flex', justifyContent:'flex-end', zIndex:30,
      animation:'fadeIn .14s ease-out',
    }}>
      <div onClick={e => e.stopPropagation()} style={{
        width:460, height:'100%', background:T.panel, borderLeft:`1px solid ${T.border}`,
        boxShadow:'-12px 0 40px rgba(0,0,0,.25)',
        display:'flex', flexDirection:'column',
        animation:'slideInRight .22s cubic-bezier(.2,.7,.3,1)',
      }}>
        {/* Header */}
        <div style={{padding:'14px 18px', borderBottom:`1px solid ${T.border}`, display:'flex', alignItems:'center', gap:10}}>
          <span style={{
            width:12, height:12, borderRadius:'50%', background:dotColor,
            boxShadow: running ? `0 0 0 5px ${dotColor}33` : (renderStyle?.renderAs === 'standby' ? `0 0 0 3px ${dotColor}22` : 'none'),
            animation: running ? 'pulseDot 1s infinite' : 'none',
          }}/>
          <div style={{flex:1, minWidth:0}}>
            <div style={{fontWeight:700, fontSize:13.5, color:T.text, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap'}}>{agent.name}</div>
            <div style={{fontSize:11, color:T.sub, marginTop:1}}>{dept?.name}{render && <> · <span style={{color:T.mute}}>{render.label}</span></>}</div>
          </div>
          <span onClick={onClose} style={{cursor:'pointer', color:T.mute, padding:'4px 8px', borderRadius:5, fontSize:14, lineHeight:1}}>✕</span>
        </div>

        <div style={{flex:1, overflow:'auto', padding:'16px 18px'}}>
          {/* R7 — per-agent runs/24h pulled from data */}
          <div style={{display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap:8, marginBottom:14}}>
            <Stat T={T} label="Runs · 24h" value={runs}/>
            <Stat T={T} label="Last run"   value={agent.lastRun}/>
            <Stat T={T} label="Cadence"    value={agent.cadence}/>
          </div>

          <DLrow T={T} pairs={[
            ['Runtime',  agent.runtime],
            ['Schedule', agent.schedule],
            ['Cron',     agent.cron || '—'],
            ['Status',   agent.status],
          ]}/>

          {/* Controls (R-P1.7 — Pause/Reschedule are real, copy a prompt) */}
          <div style={{display:'flex', gap:7, marginTop:14, flexWrap:'wrap'}}>
            <button onClick={() => runAgent(agent.name)} disabled={running} style={{
              padding:'7px 14px', borderRadius:7, border:`1px solid ${T.accent}`,
              background: running ? T.panel2 : T.accent,
              color: running ? T.sub : '#fff', fontWeight:600, fontSize:12,
              cursor: running ? 'default' : 'pointer',
              display:'inline-flex', alignItems:'center', gap:6,
            }}>
              {running ? <><span style={{width:6, height:6, borderRadius:'50%', background:T.accent, animation:'pulseDot 1s infinite'}}/> Running…</> : '▶  Run now'}
            </button>
            <button onClick={() => {
              const p = `Pause the ${agent.name} schedule and log the pause in docs/agent-audit.log.`;
              try { navigator.clipboard?.writeText(p); } catch(_) {}
            }} title="Copies a pause prompt for Claude" style={{
              padding:'7px 14px', borderRadius:7, border:`1px solid ${T.border}`,
              background:T.panel, color:T.text, fontWeight:600, fontSize:12, cursor:'pointer',
            }}>Pause</button>
            <button onClick={() => {
              const p = `Reschedule ${agent.name}. Current cron: ${agent.cron}. Update it to: `;
              try { navigator.clipboard?.writeText(p); } catch(_) {}
            }} title="Copies a reschedule prompt for Claude" style={{
              padding:'7px 14px', borderRadius:7, border:`1px solid ${T.border}`,
              background:T.panel, color:T.text, fontWeight:600, fontSize:12, cursor:'pointer',
            }}>Reschedule</button>
            <button onClick={() => {
              const p = `Show me .claude/agents/${agent.name}/SKILL.md.`;
              try { navigator.clipboard?.writeText(p); } catch(_) {}
            }} style={{
              padding:'7px 14px', borderRadius:7, border:`1px solid ${T.border}`,
              background:T.panel, color:T.text, fontWeight:600, fontSize:12, cursor:'pointer',
            }}>SKILL.md</button>
          </div>

          {/* R-P1.3 — Recent activity for THIS agent */}
          <div style={{marginTop:18}}>
            <div style={{fontSize:11, fontWeight:700, color:T.mute, textTransform:'uppercase', letterSpacing:.06, marginBottom:6}}>
              Recent activity · this agent
            </div>
            {myEvents.length === 0 ? (
              <div style={{padding:'14px 12px', background:T.panel2, border:`1px solid ${T.border}`, borderRadius:7, fontSize:11.5, color:T.mute, textAlign:'center'}}>
                Nothing in the last 24h.
              </div>
            ) : (
              <div style={{background:T.panel2, border:`1px solid ${T.border}`, borderRadius:7, overflow:'hidden'}}>
                {myEvents.map((e, i) => (
                  <div key={e.id} style={{
                    padding:'8px 11px', borderBottom: i < myEvents.length - 1 ? `1px solid ${T.border}` : 'none',
                    display:'flex', gap:9, alignItems:'flex-start',
                  }}>
                    <span style={{
                      width:6, height:6, borderRadius:'50%',
                      background: e.status === 'fail' ? '#ef4444' : '#10b981',
                      marginTop:5, flexShrink:0,
                    }}/>
                    <div style={{flex:1, minWidth:0}}>
                      <div style={{fontSize:11.5, color:T.text, lineHeight:1.4}}>{e.summary}</div>
                      <div style={{fontSize:10, color:T.faint, marginTop:2}}>{e.age}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div style={{marginTop:14, padding:'10px 12px', background:T.panel2, border:`1px solid ${T.border}`, borderRadius:7, fontSize:11, color:T.sub, lineHeight:1.5}}>
            Skill harness: permission-check → idempotency-guard → work → validate → audit → heartbeat. <span style={{color:T.text}}>Run now</span> refreshes the heartbeat.
          </div>
        </div>
      </div>
    </div>
  );
}

function Stat({ T, label, value }) {
  return (
    <div style={{padding:'8px 10px', background:T.panel2, border:`1px solid ${T.border}`, borderRadius:7}}>
      <div style={{fontSize:9.5, color:T.mute, fontWeight:700, textTransform:'uppercase', letterSpacing:.05}}>{label}</div>
      <div style={{fontSize:15, fontWeight:700, color:T.text, fontVariantNumeric:'tabular-nums', letterSpacing:-0.3, marginTop:2, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap'}}>{value}</div>
    </div>
  );
}
function DLrow({ T, pairs }) {
  return (
    <div style={{display:'grid', gridTemplateColumns:'90px 1fr', gap:'5px 14px', fontSize:12}}>
      {pairs.map(([k,v]) => (
        <React.Fragment key={k}>
          <div style={{color:T.mute, fontSize:11}}>{k}</div>
          <div style={{color:T.text, fontFamily: /^[\w-]+ \*/.test(v) ? '"SF Mono",ui-monospace,monospace' : 'inherit', fontSize: typeof v === 'string' && v.includes(' ') ? 12 : 12}}>
            {v}
          </div>
        </React.Fragment>
      ))}
    </div>
  );
}

/* ──────────────────────────────────────────────────────────────────────
   BACKLOG PANEL
   ────────────────────────────────────────────────────────────────────── */
function BacklogPanel({ T, item, onClose }) {
  return (
    <div onClick={onClose} style={{
      position:'absolute', inset:0, background:'rgba(0,0,0,.4)', backdropFilter:'blur(2px)',
      display:'flex', alignItems:'center', justifyContent:'center', zIndex:30, padding:30,
      animation:'fadeIn .14s ease-out',
    }}>
      <div onClick={e => e.stopPropagation()} style={{
        width:'100%', maxWidth:540, background:T.panel, borderRadius:12, padding:22,
        border:`1px solid ${T.border}`, boxShadow:'0 22px 60px rgba(0,0,0,.4)',
        animation:'slideUp .22s cubic-bezier(.2,.7,.3,1)',
      }}>
        <div style={{display:'flex', alignItems:'center', gap:8, marginBottom:12}}>
          <code style={{fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:11.5, fontWeight:700, color:T.text}}>{item.id}</code>
          <span style={{
            fontSize:10, padding:'2px 7px', borderRadius:4, fontWeight:700, textTransform:'uppercase', letterSpacing:.05,
            background: {critical:'rgba(220,38,38,.16)',high:'rgba(239,68,68,.16)',medium:'rgba(245,158,11,.16)',low:'rgba(16,185,129,.16)'}[item.sev],
            color: {critical:'#dc2626',high:'#ef4444',medium:'#f59e0b',low:'#10b981'}[item.sev],
          }}>{item.sev}</span>
          <span style={{fontSize:11, color:T.mute, padding:'2px 7px', borderRadius:4, background:T.panel2, border:`1px solid ${T.border}`}}>{item.stage}</span>
          <span style={{flex:1}}/>
          <span onClick={onClose} style={{cursor:'pointer', color:T.mute, padding:'4px 8px'}}>✕</span>
        </div>
        <div style={{fontSize:15, fontWeight:600, color:T.text, lineHeight:1.4, marginBottom:14}}>{item.title}</div>
        <DLrow T={T} pairs={[
          ['Area',     item.area],
          ['Owner',    item.owner],
          ['File(s)',  item.files],
          ['Age',      item.age],
          ['Filed by', item.filedBy],
        ]}/>
        <div style={{display:'flex', gap:7, flexWrap:'wrap', marginTop:14}}>
          <button onClick={() => {
            const p = `Move backlog issue ${item.id} to stage=ready so dev-agent picks it up.`;
            try { navigator.clipboard?.writeText(p); } catch(_) {}
          }} style={{padding:'7px 14px', borderRadius:7, border:`1px solid ${T.accent}`, background:T.accent, color:'#fff', fontWeight:600, fontSize:12, cursor:'pointer'}}>Send to dev</button>
          <button onClick={() => {
            const p = `Mark backlog issue ${item.id} done — move it to the Done section with stage=done.`;
            try { navigator.clipboard?.writeText(p); } catch(_) {}
          }} style={{padding:'7px 14px', borderRadius:7, border:`1px solid ${T.border}`, background:T.panel, color:T.text, fontWeight:600, fontSize:12, cursor:'pointer'}}>Mark done</button>
          <button onClick={() => {
            const p = `Snooze backlog issue ${item.id} for 24 hours.`;
            try { navigator.clipboard?.writeText(p); } catch(_) {}
          }} style={{padding:'7px 14px', borderRadius:7, border:`1px solid ${T.border}`, background:T.panel, color:T.text, fontWeight:600, fontSize:12, cursor:'pointer'}}>Snooze 24h</button>
        </div>
      </div>
    </div>
  );
}

window.PulseViewC = PulseViewC;
window.RosterViewC = RosterViewC;
window.PipelineViewC = PipelineViewC;
window.AgentPanel = AgentPanel;
window.BacklogPanel = BacklogPanel;
