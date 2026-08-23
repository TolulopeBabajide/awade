// Direction A — "Command Center"
// Single-page dashboard. Hero is the org chart by department.
// "Needs you" decisions queue prominent on left. Live stream on right.

const { useState, useEffect, useMemo, useRef } = React;

/* ---------- Tiny helpers ---------- */
const cnA = (...xs) => xs.filter(Boolean).join(' ');
const STATUS_COLOR = {
  healthy:   { fill:'#10b981', label:'OK' },
  warning:   { fill:'#f59e0b', label:'Warn' },
  critical:  { fill:'#ef4444', label:'Crit' },
  idle:      { fill:'#a1a1aa', label:'Idle' },
  'on-demand':{fill:'#60a5fa', label:'On-demand' },
};
const URGENCY_COLOR = { high:'#ef4444', medium:'#f59e0b', low:'#10b981' };
const DECISION_ICON = {
  approve: (p)=> <svg width="14" height="14" viewBox="0 0 24 24" fill="none" {...p}><path d="M20 6L9 17l-5-5" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/></svg>,
  decide:  (p)=> <svg width="14" height="14" viewBox="0 0 24 24" fill="none" {...p}><path d="M9 5H4v14h16V5h-5M9 5a3 3 0 116 0M9 5h6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/></svg>,
  review:  (p)=> <svg width="14" height="14" viewBox="0 0 24 24" fill="none" {...p}><circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="2"/><path d="M21 21l-4.3-4.3" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/></svg>,
  respond: (p)=> <svg width="14" height="14" viewBox="0 0 24 24" fill="none" {...p}><path d="M3 12a9 9 0 109-9 9 9 0 00-7.5 4M3 4v4h4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>,
};

/* ---------- Top-level component ---------- */
function CommandCenter({ theme, liveMode, setLiveMode }) {
  const [tab, setTab] = useState('overview');
  const [events, setEvents] = useState(EVENTS);
  const [runs24h, setRuns24h] = useState(STATS.runs24h);
  const [runningAgent, setRunningAgent] = useState(null);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [selectedDecision, setSelectedDecision] = useState(null);
  const [selectedOutput, setSelectedOutput] = useState(null);
  const [filter, setFilter] = useState({ status:'all', q:'' });
  const [now, setNow] = useState(Date.now());
  const [toast, setToast] = useState(null);
  const [dismissed, setDismissed] = useState(new Set());
  // liveMode is lifted to the parent App so both directions share it.
  // OFF (default) = command-console mode: action buttons copy a Claude
  // prompt. ON = one-click: action buttons POST to /api/action.

  // Live ticking — fire a fresh event every ~6s, bump counters every 1s
  useEffect(()=>{
    const tickClock = setInterval(()=> setNow(Date.now()), 1000);
    const tickEvent = setInterval(()=>{
      const fresh = [
        { who:'dev-agent',          kind:'run', status:'done', summary:'Picked up next item from ready' },
        { who:'qa-agent',           kind:'run', status:'done', summary:'Test run passed in 14.2s' },
        { who:'dashboard-refresh',  kind:'run', status:'done', summary:'Rebuilt dashboard in 1.3s' },
        { who:'improvement-agent',  kind:'run', status:'done', summary:'Audit log synced — 12 entries' },
        { who:'analytics-agent',    kind:'run', status:'done', summary:'Daily metrics rolled up' },
      ];
      const e = fresh[Math.floor(Math.random()*fresh.length)];
      setEvents(prev => [{ id:'live-'+Date.now(), ...e, age:'just now', fresh:true }, ...prev].slice(0,40));
      setRuns24h(r => r+1);
    }, 6000);
    return ()=> { clearInterval(tickClock); clearInterval(tickEvent); };
  },[]);

  // Toast helpers
  function showToast(msg){ setToast(msg); setTimeout(()=> setToast(null), 2000); }
  function copyToClipboard(txt){
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(txt);
      else {
        const ta = document.createElement('textarea');
        ta.value = txt; document.body.appendChild(ta); ta.select();
        try { document.execCommand('copy'); } catch(e) {}
        document.body.removeChild(ta);
      }
    } catch(e) {}
  }
  // The single action handler used by every button on every artifact card:
  // - OFF: copy the prompt to the clipboard, leave the inbox item alone
  // - ON:  pretend to POST to /api/action, dismiss the item
  function executeAction({ prompt, api, label, itemId, dismissOnRun = true }){
    if (!liveMode) {
      copyToClipboard(prompt);
      showToast('⎘ Copied — paste into Claude');
      return;
    }
    showToast(`Running … ${label || api?.type || ''}`);
    setTimeout(()=>{
      if (itemId && dismissOnRun) setDismissed(s => new Set(s).add(itemId));
      showToast(`✓ ${label || 'Done'}`);
    }, 700);
  }
  function runAgent(name){
    setRunningAgent(name);
    showToast(`Running ${name}…`);
    setTimeout(()=>{
      setRunningAgent(null);
      setEvents(prev => [{ id:'manual-'+Date.now(), who:name, kind:'run', status:'done', summary:'Manual run completed', age:'just now', fresh:true }, ...prev].slice(0,40));
      setRuns24h(r => r+1);
      showToast(`✓ ${name} ran successfully`);
    }, 1400);
  }

  /* ---------- Theme tokens ---------- */
  const T = theme === 'dark' ? {
    bg:'#0c0d11', panel:'#15171d', panel2:'#1a1d24', border:'#262934', borderStrong:'#363a48',
    text:'#ededee', sub:'#a3a4ad', mute:'#71727a', faint:'#52535b',
    accent:'#818cf8', accentSoft:'rgba(129,140,248,.16)', accentBorder:'rgba(129,140,248,.5)',
    shadow:'0 1px 2px rgba(0,0,0,.4),0 8px 24px rgba(0,0,0,.35)',
    shadowSm:'0 1px 2px rgba(0,0,0,.3)',
    pillBg:'#1a1d24',
    chartBg:'#15171d',
  } : {
    bg:'#f7f7f9', panel:'#ffffff', panel2:'#fafafb', border:'#e7e7ec', borderStrong:'#d4d4dc',
    text:'#15161a', sub:'#54555c', mute:'#82838a', faint:'#a3a4ab',
    accent:'#5b5bf0', accentSoft:'rgba(91,91,240,.08)', accentBorder:'rgba(91,91,240,.4)',
    shadow:'0 1px 2px rgba(20,20,30,.04),0 8px 22px rgba(20,20,30,.06)',
    shadowSm:'0 1px 2px rgba(20,20,30,.05)',
    pillBg:'#ffffff',
    chartBg:'#ffffff',
  };

  const visibleDecisions = useMemo(()=> DECISIONS.filter(d => !dismissed.has(d.id)), [dismissed]);
  const visibleAgents = useMemo(()=>{
    let xs = AGENTS;
    if (filter.status !== 'all') xs = xs.filter(a => a.status === filter.status);
    if (filter.q) {
      const q = filter.q.toLowerCase();
      xs = xs.filter(a => a.name.toLowerCase().includes(q) || a.dept.toLowerCase().includes(q));
    }
    return xs;
  }, [filter]);

  return (
    <div style={{
      width:'100%', height:'100%', background:T.bg, color:T.text,
      fontFamily:'-apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", system-ui, sans-serif',
      fontSize:13, lineHeight:1.45, display:'flex', flexDirection:'column', overflow:'hidden',
    }}>
      <Header T={T} runs24h={runs24h} pending={visibleDecisions.length} liveMode={liveMode} setLiveMode={setLiveMode}/>
      <Tabs T={T} tab={tab} setTab={setTab}/>
      <div style={{flex:1, overflow:'auto', padding:'18px 24px 28px'}}>
        {tab==='overview' && (
          <OverviewView
            T={T} now={now}
            decisions={visibleDecisions}
            onDismiss={(id)=> setDismissed(s=> new Set(s).add(id))}
            onSelectDecision={setSelectedDecision}
            events={events}
            runs24h={runs24h}
            runAgent={runAgent}
            runningAgent={runningAgent}
            onSelectAgent={setSelectedAgent}
          />
        )}
        {tab==='roster' && (
          <RosterView T={T} agents={visibleAgents} filter={filter} setFilter={setFilter}
            onSelectAgent={setSelectedAgent} runAgent={runAgent} runningAgent={runningAgent}/>
        )}
        {tab==='outputs' && (
          <OutputsView T={T} onSelectOutput={setSelectedOutput}/>
        )}
        {tab==='backlog' && (
          <BacklogView T={T} />
        )}
      </div>

      {selectedAgent && (
        <DetailDrawer T={T} title={selectedAgent.name} onClose={()=> setSelectedAgent(null)}>
          <AgentDetail T={T} agent={selectedAgent} runAgent={runAgent} runningAgent={runningAgent}/>
        </DetailDrawer>
      )}
      {selectedDecision && (
        <DetailDrawer T={T} title={selectedDecision.title} onClose={()=> setSelectedDecision(null)}>
          <DecisionDetail T={T} d={selectedDecision} liveMode={liveMode} executeAction={executeAction}
            onClose={()=> setSelectedDecision(null)}/>
        </DetailDrawer>
      )}
      {selectedOutput && (
        <DetailDrawer T={T} title={selectedOutput.path.split('/').pop()} onClose={()=> setSelectedOutput(null)}>
          <OutputDetail T={T} o={selectedOutput} liveMode={liveMode} executeAction={executeAction}/>
        </DetailDrawer>
      )}
      {toast && <Toast T={T}>{toast}</Toast>}
    </div>
  );
}

/* ---------- Header ---------- */
function Header({ T, runs24h, pending, liveMode, setLiveMode }) {
  return (
    <div style={{
      padding:'16px 24px 14px', borderBottom:`1px solid ${T.border}`,
      display:'flex', alignItems:'center', gap:14, background:T.panel,
    }}>
      <div style={{
        width:30, height:30, borderRadius:8, background:`linear-gradient(135deg, ${T.accent}, #a78bfa)`,
        display:'flex', alignItems:'center', justifyContent:'center', color:'#fff', fontWeight:700, fontSize:13,
      }}>AT</div>
      <div>
        <div style={{fontWeight:700, fontSize:15, letterSpacing:-0.2}}>Agentic Team</div>
        <div style={{color:T.sub, fontSize:11.5, marginTop:1}}>33 agents · 23 scheduled · self-healing</div>
      </div>
      <div style={{flex:1}}/>
      {/* Live mode toggle — mirrors dashboard-server.py /api/ping handshake */}
      <ModeToggle T={T} liveMode={liveMode} setLiveMode={setLiveMode}/>
      {/* Quick stats */}
      <div style={{display:'flex', alignItems:'center', gap:8, marginLeft:4}}>
        <HeaderStat T={T} label="Runs / 24h" value={runs24h} accent />
        <HeaderStat T={T} label="Needs you" value={pending} warn={pending>0}/>
      </div>
    </div>
  );
}
function ModeToggle({ T, liveMode, setLiveMode }) {
  return (
    <div onClick={()=> setLiveMode(!liveMode)}
      title={liveMode ? 'One-click mode — actions hit /api/action' : 'Command-console mode — actions copy a prompt for Claude'}
      style={{
        display:'inline-flex', alignItems:'center', gap:7, padding:'4px 11px', borderRadius:999,
        border:`1px solid ${liveMode ? 'rgba(16,185,129,.45)' : T.border}`,
        background: liveMode ? 'rgba(16,185,129,.08)' : T.panel2,
        cursor:'pointer', fontSize:11.5, fontWeight:600,
        color: liveMode ? '#10b981' : T.sub,
      }}>
      <span style={{
        width:7, height:7, borderRadius:'50%',
        background: liveMode ? '#10b981' : T.mute,
        boxShadow: liveMode ? '0 0 0 4px rgba(16,185,129,.16)' : 'none',
      }}/>
      <span>{liveMode ? 'One-click' : 'Command console'}</span>
    </div>
  );
}
function HeaderStat({ T, label, value, accent, warn }) {
  const color = warn ? '#ef4444' : accent ? T.accent : T.text;
  return (
    <div style={{
      padding:'5px 11px', border:`1px solid ${warn?'rgba(239,68,68,.4)':T.border}`, borderRadius:8,
      background: warn ? 'rgba(239,68,68,.06)' : T.panel2,
      display:'flex', alignItems:'center', gap:8,
    }}>
      <span style={{fontSize:10.5, color:T.sub, textTransform:'uppercase', letterSpacing:.04, fontWeight:600}}>{label}</span>
      <span style={{fontWeight:700, color, fontSize:13.5, fontVariantNumeric:'tabular-nums'}}>{value}</span>
    </div>
  );
}

/* ---------- Tabs ---------- */
function Tabs({ T, tab, setTab }) {
  const tabs = [
    { id:'overview', label:'Overview' },
    { id:'roster',   label:'Roster' },
    { id:'outputs',  label:'Outputs to review' },
    { id:'backlog',  label:'Backlog' },
  ];
  return (
    <div style={{
      padding:'0 24px', borderBottom:`1px solid ${T.border}`, background:T.panel, display:'flex', gap:0,
    }}>
      {tabs.map(t => {
        const active = tab === t.id;
        return (
          <div key={t.id} onClick={()=> setTab(t.id)} style={{
            padding:'9px 14px', fontSize:12.5, fontWeight:600, cursor:'pointer',
            color: active ? T.accent : T.sub,
            borderBottom: `2px solid ${active ? T.accent : 'transparent'}`,
            marginBottom:-1, transition:'color .15s',
          }}>{t.label}</div>
        );
      })}
    </div>
  );
}

/* ---------- Overview ---------- */
function OverviewView({ T, now, decisions, onDismiss, onSelectDecision, events, runs24h, runAgent, runningAgent, onSelectAgent }) {
  return (
    <div style={{display:'grid', gridTemplateColumns:'320px 1fr 290px', gap:16, alignItems:'start'}}>
      {/* LEFT — Needs you queue */}
      <NeedsYouPanel T={T} decisions={decisions} onDismiss={onDismiss} onSelectDecision={onSelectDecision}/>

      {/* CENTER — Org chart hero + KPIs + hourly loop */}
      <div style={{display:'flex', flexDirection:'column', gap:16}}>
        <KpiRow T={T} runs24h={runs24h}/>
        <OrgChart T={T} onSelectAgent={onSelectAgent} runAgent={runAgent} runningAgent={runningAgent}/>
        <HourlyLoop T={T} now={now}/>
      </div>

      {/* RIGHT — Live activity */}
      <LivePanel T={T} events={events}/>
    </div>
  );
}

/* ---------- Needs you ---------- */
function NeedsYouPanel({ T, decisions, onDismiss, onSelectDecision }) {
  const groups = [
    { key:'high',   label:'Urgent',   bg:'rgba(239,68,68,.06)',  border:'rgba(239,68,68,.3)', tint:'#ef4444' },
    { key:'medium', label:'This week', bg:'rgba(245,158,11,.06)', border:'rgba(245,158,11,.3)', tint:'#f59e0b' },
    { key:'low',    label:'Whenever',  bg:T.panel2,               border:T.border,             tint:T.sub },
  ];
  return (
    <Panel T={T} title="Needs you" sub={`${decisions.length} pending`} accent>
      {decisions.length === 0 ? (
        <div style={{padding:'28px 14px', textAlign:'center', color:T.sub, fontSize:12.5}}>
          <div style={{fontSize:22, marginBottom:6}}>✓</div>
          Inbox zero. Nice.
        </div>
      ) : (
        <div style={{display:'flex', flexDirection:'column', gap:14}}>
          {groups.map(g => {
            const items = decisions.filter(d => d.urgency === g.key);
            if (!items.length) return null;
            return (
              <div key={g.key}>
                <div style={{
                  fontSize:10.5, fontWeight:700, color:g.tint, textTransform:'uppercase',
                  letterSpacing:.06, marginBottom:7, padding:'0 2px',
                }}>{g.label} · {items.length}</div>
                <div style={{display:'flex', flexDirection:'column', gap:7}}>
                  {items.map(d => (
                    <DecisionCard key={d.id} T={T} d={d} tint={g.tint}
                      onClick={()=> onSelectDecision(d)}
                      onDismiss={()=> onDismiss(d.id)}/>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </Panel>
  );
}

function DecisionCard({ T, d, tint, onClick, onDismiss }) {
  const Icon = DECISION_ICON[d.kind] || DECISION_ICON.review;
  return (
    <div onClick={onClick} style={{
      border:`1px solid ${T.border}`, borderRadius:9, padding:'10px 11px',
      background:T.panel2, cursor:'pointer', position:'relative',
      transition:'border-color .15s, transform .12s',
    }}
    onMouseEnter={e=> e.currentTarget.style.borderColor = T.accentBorder}
    onMouseLeave={e=> e.currentTarget.style.borderColor = T.border}>
      <div style={{display:'flex', alignItems:'center', gap:8, marginBottom:5}}>
        <span style={{
          width:20, height:20, borderRadius:5, background:tint+'22', color:tint,
          display:'inline-flex', alignItems:'center', justifyContent:'center', flexShrink:0,
        }}><Icon/></span>
        <span style={{fontSize:10.5, color:T.mute, fontWeight:600, textTransform:'uppercase', letterSpacing:.04, flex:1}}>{d.kind}</span>
        <span style={{fontSize:10.5, color:T.faint}}>{d.age}</span>
      </div>
      <div style={{fontSize:12.5, fontWeight:600, color:T.text, marginBottom:5, lineHeight:1.35}}>{d.title}</div>
      {d.originPath && (
        <div style={{
          fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:10.5, color:T.mute,
          background:T.panel, border:`1px solid ${T.border}`, borderRadius:5,
          padding:'3px 6px', marginBottom:5, overflow:'hidden', textOverflow:'ellipsis',
          whiteSpace:'nowrap',
        }} title={d.originPath}>{d.originPath}</div>
      )}
      <div style={{display:'flex', alignItems:'center', gap:6, fontSize:11, color:T.sub}}>
        <span style={{color:T.faint}}>via</span>
        <code style={{fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:10.5, color:T.text}}>{d.via || d.from}</code>
        <span style={{flex:1}}/>
        <span style={{fontSize:10.5, color:T.mute}}>~{d.est}</span>
      </div>
    </div>
  );
}

/* ---------- KPIs ---------- */
function KpiRow({ T, runs24h }) {
  const items = [
    { label:'Healthy',  value:STATS.agentsHealthy,   total:STATS.agentsTotal, color:'#10b981', icon:'✓' },
    { label:'Warning',  value:STATS.agentsWarning,   total:STATS.agentsTotal, color:'#f59e0b', icon:'!' },
    { label:'Idle',     value:STATS.agentsIdle + STATS.agentsOnDemand, total:STATS.agentsTotal, color:T.sub, icon:'·' },
    { label:'Runs · 24h', value:runs24h, color:T.accent, icon:'↗' },
    { label:'Backlog open', value:STATS.backlogOpen, color:T.text, icon:'≡' },
  ];
  return (
    <div style={{display:'grid', gridTemplateColumns:'repeat(5, 1fr)', gap:10}}>
      {items.map((it,i) => (
        <div key={i} style={{
          background:T.panel, border:`1px solid ${T.border}`, borderRadius:10,
          padding:'12px 13px', boxShadow:T.shadowSm,
        }}>
          <div style={{display:'flex', alignItems:'center', gap:6, marginBottom:5}}>
            <span style={{
              width:18, height:18, borderRadius:5, background:it.color+'1a', color:it.color,
              display:'inline-flex', alignItems:'center', justifyContent:'center',
              fontSize:11, fontWeight:700,
            }}>{it.icon}</span>
            <span style={{fontSize:10.5, color:T.sub, fontWeight:600, textTransform:'uppercase', letterSpacing:.05}}>{it.label}</span>
          </div>
          <div style={{display:'flex', alignItems:'baseline', gap:5}}>
            <span style={{fontSize:22, fontWeight:700, color:T.text, fontVariantNumeric:'tabular-nums', letterSpacing:-0.5}}>{it.value}</span>
            {it.total && <span style={{fontSize:11, color:T.faint}}>/ {it.total}</span>}
          </div>
        </div>
      ))}
    </div>
  );
}

/* ---------- Org chart ---------- */
function OrgChart({ T, onSelectAgent, runAgent, runningAgent }) {
  return (
    <Panel T={T} title="The team" sub="33 agents · 9 departments" pad>
      <div style={{display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap:10}}>
        {DEPARTMENTS.map(d => (
          <DeptCard key={d.id} T={T} dept={d} onSelectAgent={onSelectAgent} runAgent={runAgent} runningAgent={runningAgent}/>
        ))}
      </div>
    </Panel>
  );
}

function DeptCard({ T, dept, onSelectAgent, runAgent, runningAgent }) {
  const agents = dept.agents.map(name => AGENTS.find(a => a.name === name)).filter(Boolean);
  const counts = agents.reduce((acc,a) => { acc[a.status] = (acc[a.status]||0)+1; return acc; }, {});
  const hasIssue = (counts.warning||0) + (counts.critical||0) > 0;
  return (
    <div style={{
      border:`1px solid ${hasIssue ? 'rgba(245,158,11,.4)' : T.border}`, borderRadius:9, padding:'10px 11px',
      background: T.panel2,
    }}>
      <div style={{display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:8}}>
        <span style={{fontWeight:600, fontSize:12, color:T.text}}>{dept.name}</span>
        <span style={{fontSize:10.5, color:T.mute, fontVariantNumeric:'tabular-nums'}}>{agents.length}</span>
      </div>
      <div style={{display:'flex', flexWrap:'wrap', gap:5}}>
        {agents.map(a => {
          const c = STATUS_COLOR[a.status];
          const running = runningAgent === a.name;
          return (
            <div key={a.name} title={`${a.name} · ${a.status}`}
              onClick={()=> onSelectAgent(a)}
              style={{
                display:'inline-flex', alignItems:'center', gap:5,
                padding:'4px 8px 4px 7px', borderRadius:6,
                background: T.panel, border:`1px solid ${T.border}`,
                fontSize:11, cursor:'pointer', maxWidth:'100%', overflow:'hidden',
              }}
              onMouseEnter={e=> e.currentTarget.style.borderColor = T.accentBorder}
              onMouseLeave={e=> e.currentTarget.style.borderColor = T.border}>
              <span style={{
                width:6, height:6, borderRadius:'50%', background:c.fill, flexShrink:0,
                boxShadow: running ? `0 0 0 3px ${c.fill}55` : 'none',
                animation: running ? 'pulseDot 1s infinite' : 'none',
              }}/>
              <span style={{overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap', color:T.text, fontSize:10.5}}>
                {a.name.replace('-agent','').replace('agent-','')}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ---------- Hourly loop ---------- */
function HourlyLoop({ T, now }) {
  const min = new Date(now).getMinutes();
  // Find which step is "active" based on the current minute
  const stepIndex = min < 15 ? 0 : min < 30 ? 1 : min < 45 ? 2 : 3;
  return (
    <Panel T={T} title="Hourly self-healing loop" sub="dev → review → qa → refresh" pad>
      <div style={{display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap:10, position:'relative'}}>
        {HOURLY_LOOP.map((step, i) => {
          const active = i === stepIndex;
          return (
            <div key={i} style={{
              border:`1px solid ${active ? T.accentBorder : T.border}`, borderRadius:9, padding:'10px 12px',
              background: active ? T.accentSoft : T.panel2,
              position:'relative',
            }}>
              <div style={{display:'flex', alignItems:'center', gap:7, marginBottom:5}}>
                <span style={{
                  fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:11, fontWeight:700,
                  color: active ? T.accent : T.mute,
                  padding:'2px 6px', borderRadius:4, background: active ? T.accentSoft : T.panel,
                }}>{step.at}</span>
                <span style={{fontSize:12, fontWeight:600, color:T.text}}>{step.name}</span>
                {active && <span style={{
                  marginLeft:'auto', fontSize:10, color:T.accent, fontWeight:600,
                  display:'inline-flex', alignItems:'center', gap:4,
                }}>
                  <span style={{width:5, height:5, borderRadius:'50%', background:T.accent, animation:'pulseDot 1s infinite'}}/>now
                </span>}
              </div>
              <div style={{fontSize:11, color:T.sub, lineHeight:1.4}}>{step.desc}</div>
              <div style={{fontSize:10.5, color:T.mute, marginTop:5, display:'flex', justifyContent:'space-between'}}>
                <code style={{fontFamily:'"SF Mono",ui-monospace,monospace'}}>{step.agent}</code>
                <span style={{color: step.status==='done' ? '#10b981' : T.sub}}>{step.result}</span>
              </div>
            </div>
          );
        })}
      </div>
    </Panel>
  );
}

/* ---------- Live activity ---------- */
function LivePanel({ T, events }) {
  return (
    <Panel T={T} title="Live activity" sub="streaming" liveDot>
      <div style={{display:'flex', flexDirection:'column', gap:0, maxHeight:760, overflow:'auto', margin:'-4px -2px'}}>
        {events.slice(0,30).map(e => <EventRow key={e.id} T={T} e={e}/>)}
      </div>
    </Panel>
  );
}

function EventRow({ T, e }) {
  const statusColor = e.status === 'fail' ? '#ef4444' : e.status === 'done' ? '#10b981' : T.sub;
  return (
    <div style={{
      padding:'8px 6px', borderBottom:`1px solid ${T.border}`, display:'flex', gap:8, alignItems:'flex-start',
      animation: e.fresh ? 'fadeIn .5s ease-out' : 'none',
    }}>
      <div style={{
        width:6, height:6, borderRadius:'50%', background:statusColor,
        marginTop:5, flexShrink:0,
      }}/>
      <div style={{flex:1, minWidth:0}}>
        <div style={{display:'flex', alignItems:'baseline', gap:6, marginBottom:1}}>
          <code style={{fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:10.5, fontWeight:600, color:T.text, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis'}}>{e.who}</code>
          <span style={{fontSize:10, color:T.faint, marginLeft:'auto', whiteSpace:'nowrap'}}>{e.age}</span>
        </div>
        <div style={{fontSize:11, color:T.sub, lineHeight:1.35}}>{e.summary}</div>
      </div>
    </div>
  );
}

/* ---------- Roster view ---------- */
function RosterView({ T, agents, filter, setFilter, onSelectAgent, runAgent, runningAgent }) {
  const statuses = ['all','healthy','warning','critical','idle','on-demand'];
  return (
    <div style={{display:'flex', flexDirection:'column', gap:12}}>
      <div style={{display:'flex', gap:8, alignItems:'center', flexWrap:'wrap'}}>
        {statuses.map(s => (
          <button key={s} onClick={()=> setFilter(f=>({...f, status:s}))} style={{
            padding:'5px 11px', borderRadius:7, fontSize:11.5, fontWeight:600,
            border:`1px solid ${filter.status===s ? T.accentBorder : T.border}`,
            background: filter.status===s ? T.accentSoft : T.panel,
            color: filter.status===s ? T.accent : T.sub,
            cursor:'pointer', textTransform:'capitalize',
          }}>{s}</button>
        ))}
        <div style={{flex:1}}/>
        <input
          placeholder="Search agents…" value={filter.q} onChange={e=> setFilter(f=>({...f, q:e.target.value}))}
          style={{
            padding:'6px 11px', borderRadius:7, fontSize:12, minWidth:220,
            border:`1px solid ${T.border}`, background:T.panel, color:T.text, outline:'none',
          }}/>
      </div>
      <Panel T={T} title={`Agents — ${agents.length}`}>
        <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(240px, 1fr))', gap:8}}>
          {agents.map(a => (
            <AgentRosterCard key={a.name} T={T} a={a} onSelect={()=> onSelectAgent(a)}
              run={()=> runAgent(a.name)} running={runningAgent===a.name}/>
          ))}
        </div>
      </Panel>
    </div>
  );
}

function AgentRosterCard({ T, a, onSelect, run, running }) {
  const c = STATUS_COLOR[a.status];
  const dept = DEPARTMENTS.find(d => d.id === a.dept);
  return (
    <div onClick={onSelect} style={{
      border:`1px solid ${T.border}`, borderLeft:`3px solid ${c.fill}`,
      borderRadius:8, padding:'10px 12px', background:T.panel2, cursor:'pointer',
    }}
    onMouseEnter={e=> e.currentTarget.style.borderColor = T.accentBorder}
    onMouseLeave={e=> e.currentTarget.style.borderColor = T.border}>
      <div style={{display:'flex', alignItems:'center', gap:6, marginBottom:4}}>
        <span style={{
          width:7, height:7, borderRadius:'50%', background:c.fill,
          boxShadow: running ? `0 0 0 3px ${c.fill}55` : 'none',
          animation: running ? 'pulseDot 1s infinite' : 'none',
        }}/>
        <span style={{fontWeight:600, fontSize:12, color:T.text, flex:1, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap'}}>{a.name}</span>
        <span style={{fontSize:10, color:T.faint}}>{a.lastRun}</span>
      </div>
      <div style={{display:'flex', alignItems:'center', gap:6, fontSize:10.5, color:T.mute}}>
        <span>{dept?.short}</span>
        <span style={{color:T.faint}}>·</span>
        <span>{a.cadence}</span>
        <span style={{flex:1}}/>
        <span style={{
          fontSize:9.5, padding:'1px 5px', borderRadius:3,
          background: a.runtime==='Claude Code' ? 'rgba(167,139,250,.18)' : T.panel,
          color: a.runtime==='Claude Code' ? '#a78bfa' : T.mute,
          border:`1px solid ${T.border}`,
        }}>{a.runtime}</span>
      </div>
    </div>
  );
}

/* ---------- Backlog view ---------- */
function BacklogView({ T }) {
  const [stageFilter, setStageFilter] = useState('all');
  const [selectedItem, setSelectedItem] = useState(null);
  const stages = ['all', ...PIPELINE_STAGES, 'done'];
  const items = BACKLOG.filter(b => stageFilter==='all' || b.stage===stageFilter);
  return (
    <div style={{display:'flex', flexDirection:'column', gap:12}}>
      <div style={{display:'flex', gap:8, flexWrap:'wrap'}}>
        {stages.map(s => (
          <button key={s} onClick={()=> setStageFilter(s)} style={{
            padding:'5px 11px', borderRadius:7, fontSize:11.5, fontWeight:600,
            border:`1px solid ${stageFilter===s ? T.accentBorder : T.border}`,
            background: stageFilter===s ? T.accentSoft : T.panel,
            color: stageFilter===s ? T.accent : T.sub,
            cursor:'pointer', textTransform:'capitalize',
          }}>{s}</button>
        ))}
      </div>
      <Panel T={T} title={`Pipeline — ${items.length}`}>
        <div style={{overflow:'auto'}}>
          <table style={{width:'100%', borderCollapse:'collapse', fontSize:12.5}}>
            <thead>
              <tr style={{textAlign:'left'}}>
                {['ID','Severity','Title','Area','Stage','Owner','Age'].map(h => (
                  <th key={h} style={{padding:'8px 10px', borderBottom:`1px solid ${T.border}`, fontSize:10.5, color:T.mute, textTransform:'uppercase', letterSpacing:.05, fontWeight:600}}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {items.map(b => (
                <tr key={b.id} onClick={()=> setSelectedItem(b)} style={{cursor:'pointer'}}
                  onMouseEnter={e=> e.currentTarget.style.background = T.panel2}
                  onMouseLeave={e=> e.currentTarget.style.background = 'transparent'}>
                  <td style={{padding:'9px 10px', borderBottom:`1px solid ${T.border}`}}>
                    <code style={{fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:11, color:T.text}}>{b.id}</code>
                  </td>
                  <td style={{padding:'9px 10px', borderBottom:`1px solid ${T.border}`}}>
                    <SevBadge T={T} sev={b.sev}/>
                  </td>
                  <td style={{padding:'9px 10px', borderBottom:`1px solid ${T.border}`, color:T.text}}>{b.title}</td>
                  <td style={{padding:'9px 10px', borderBottom:`1px solid ${T.border}`, color:T.sub}}>{b.area}</td>
                  <td style={{padding:'9px 10px', borderBottom:`1px solid ${T.border}`}}>
                    <span style={{
                      padding:'2px 7px', borderRadius:4, fontSize:10.5,
                      background:T.panel2, color:T.sub, border:`1px solid ${T.border}`,
                    }}>{b.stage}</span>
                  </td>
                  <td style={{padding:'9px 10px', borderBottom:`1px solid ${T.border}`, color:T.sub, fontSize:11}}>
                    <code style={{fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:10.5}}>{b.owner}</code>
                  </td>
                  <td style={{padding:'9px 10px', borderBottom:`1px solid ${T.border}`, color:T.mute, fontSize:11}}>{b.age}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
      {selectedItem && (
        <DetailDrawer T={T} title={`${selectedItem.id} · ${selectedItem.area}`} onClose={()=> setSelectedItem(null)}>
          <BacklogDetail T={T} item={selectedItem}/>
        </DetailDrawer>
      )}
    </div>
  );
}
function SevBadge({ T, sev }) {
  const c = { high:'#ef4444', medium:'#f59e0b', low:'#10b981', critical:'#dc2626' }[sev] || T.sub;
  return <span style={{
    fontSize:10, fontWeight:700, color:c, background:c+'1a',
    padding:'2px 7px', borderRadius:4, textTransform:'uppercase', letterSpacing:.05,
  }}>{sev}</span>;
}

/* ---------- Panel container ---------- */
function Panel({ T, title, sub, children, accent, pad, liveDot }) {
  return (
    <div style={{
      background:T.panel, border:`1px solid ${accent ? T.accentBorder : T.border}`,
      borderRadius:11, boxShadow:T.shadow,
      padding:pad ? 14 : 12,
    }}>
      {(title || sub) && (
        <div style={{display:'flex', alignItems:'center', gap:8, marginBottom:11, padding:'0 1px'}}>
          {accent && <span style={{
            width:3, height:14, borderRadius:2, background:T.accent, marginRight:2,
          }}/>}
          <span style={{fontWeight:700, fontSize:12.5, color:T.text, letterSpacing:-0.1}}>{title}</span>
          {sub && (
            <span style={{fontSize:11, color:T.mute, marginLeft:2}}>· {sub}</span>
          )}
          {liveDot && <span style={{
            marginLeft:'auto', display:'inline-flex', alignItems:'center', gap:5, fontSize:10.5, color:'#10b981', fontWeight:600,
          }}>
            <span style={{width:6, height:6, borderRadius:'50%', background:'#10b981', boxShadow:'0 0 0 3px rgba(16,185,129,.2)'}}/>
            live
          </span>}
        </div>
      )}
      {children}
    </div>
  );
}

/* ---------- Detail drawer ---------- */
function DetailDrawer({ T, title, children, onClose }) {
  return (
    <div style={{
      position:'absolute', inset:0, background:'rgba(0,0,0,.35)', backdropFilter:'blur(2px)',
      display:'flex', justifyContent:'flex-end', zIndex:20, animation:'fadeIn .15s ease-out',
    }} onClick={onClose}>
      <div onClick={e=> e.stopPropagation()} style={{
        width:420, height:'100%', background:T.panel, borderLeft:`1px solid ${T.border}`,
        boxShadow:'-12px 0 40px rgba(0,0,0,.2)', display:'flex', flexDirection:'column',
        animation:'slideInRight .22s cubic-bezier(.2,.7,.3,1)',
      }}>
        <div style={{padding:'14px 16px', borderBottom:`1px solid ${T.border}`, display:'flex', alignItems:'center', gap:10}}>
          <span style={{fontWeight:700, fontSize:13.5, color:T.text, flex:1, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap'}}>{title}</span>
          <span onClick={onClose} style={{
            cursor:'pointer', color:T.mute, padding:'4px 8px', borderRadius:5,
            fontSize:14, lineHeight:1,
          }}>✕</span>
        </div>
        <div style={{flex:1, overflow:'auto', padding:18}}>{children}</div>
      </div>
    </div>
  );
}

function AgentDetail({ T, agent, runAgent, runningAgent }) {
  const c = STATUS_COLOR[agent.status];
  const dept = DEPARTMENTS.find(d => d.id === agent.dept);
  const running = runningAgent === agent.name;
  return (
    <div style={{display:'flex', flexDirection:'column', gap:14}}>
      <div style={{display:'flex', alignItems:'center', gap:10}}>
        <span style={{
          width:14, height:14, borderRadius:'50%', background:c.fill,
          boxShadow: running ? `0 0 0 5px ${c.fill}33` : 'none',
          animation: running ? 'pulseDot 1s infinite' : 'none',
        }}/>
        <span style={{fontWeight:600, color:T.text, fontSize:13}}>{c.label}</span>
        <span style={{color:T.mute}}>·</span>
        <span style={{color:T.sub, fontSize:12}}>{dept?.name}</span>
      </div>
      <DL T={T} pairs={[
        ['Runtime', agent.runtime],
        ['Cadence', agent.cadence],
        ['Schedule', agent.schedule],
        ['Last run', agent.lastRun],
        ['Runs / 24h', String(agent.runs24h)],
      ]}/>
      <div style={{display:'flex', gap:8, marginTop:4}}>
        <button onClick={()=> runAgent(agent.name)} disabled={running} style={{
          padding:'7px 14px', borderRadius:7, border:`1px solid ${T.accent}`,
          background: running ? T.panel2 : T.accent,
          color: running ? T.sub : '#fff', fontWeight:600, fontSize:12, cursor: running ? 'default' : 'pointer',
          display:'inline-flex', alignItems:'center', gap:6,
        }}>
          {running ? <><span style={{width:6, height:6, borderRadius:'50%', background:T.accent, animation:'pulseDot 1s infinite'}}/> Running…</> : '▶  Run now'}
        </button>
        <button style={{
          padding:'7px 14px', borderRadius:7, border:`1px solid ${T.border}`,
          background:T.panel, color:T.text, fontWeight:600, fontSize:12, cursor:'pointer',
        }}>Pause</button>
        <button style={{
          padding:'7px 14px', borderRadius:7, border:`1px solid ${T.border}`,
          background:T.panel, color:T.text, fontWeight:600, fontSize:12, cursor:'pointer',
        }}>Reschedule</button>
      </div>
      <div style={{marginTop:6, padding:'10px 12px', background:T.panel2, border:`1px solid ${T.border}`, borderRadius:8, fontSize:11.5, color:T.sub, lineHeight:1.5}}>
        Skills follow a permission-check, idempotency-guard, work, validate, audit, heartbeat harness. <span style={{color:T.text}}>Running now</span> refreshes its heartbeat.
      </div>
    </div>
  );
}

function DecisionDetail({ T, d, liveMode, executeAction, onClose }) {
  const Icon = DECISION_ICON[d.kind] || DECISION_ICON.review;
  const tint = URGENCY_COLOR[d.urgency];
  const [expandedAction, setExpandedAction] = useState(null);
  return (
    <div style={{display:'flex', flexDirection:'column', gap:14}}>
      <div style={{display:'flex', alignItems:'center', gap:10}}>
        <span style={{
          width:30, height:30, borderRadius:7, background:tint+'22', color:tint,
          display:'inline-flex', alignItems:'center', justifyContent:'center',
        }}><Icon/></span>
        <div style={{flex:1}}>
          <div style={{fontSize:10.5, color:tint, fontWeight:700, textTransform:'uppercase', letterSpacing:.04}}>{d.urgency} · {d.kind}</div>
          <div style={{color:T.sub, fontSize:11.5}}>drafted by <code style={{fontFamily:'"SF Mono",ui-monospace,monospace', color:T.text}}>{d.from}</code> <span style={{color:T.faint}}>·</span> {d.via}</div>
        </div>
      </div>

      {/* Origin file — the real artifact on disk */}
      {d.originPath && (
        <div style={{
          padding:'8px 10px', background:T.panel2, border:`1px solid ${T.border}`, borderRadius:7,
          display:'flex', alignItems:'center', gap:7,
        }}>
          <span style={{fontSize:10.5, color:T.mute, fontWeight:600, textTransform:'uppercase', letterSpacing:.05, flexShrink:0}}>Source</span>
          <code style={{fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:11, color:T.text, flex:1, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap'}} title={d.originPath}>{d.originPath}</code>
        </div>
      )}

      <div style={{padding:12, background:T.panel, border:`1px solid ${T.border}`, borderRadius:8, fontSize:12.5, color:T.text, lineHeight:1.55, boxShadow:T.shadowSm}}>
        {d.detail}
      </div>

      <DL T={T} pairs={[
        ['Impact',          d.impact],
        ['Estimated time',  d.est],
        ['Age',             d.age],
        ...(d.relatedBacklog ? [['Backlog item', d.relatedBacklog]] : []),
      ]}/>

      {/* Console-mode note */}
      <ConsoleNote T={T} liveMode={liveMode}/>

      {/* Actions — each renders a button plus an expandable prompt block */}
      <div style={{display:'flex', flexDirection:'column', gap:7}}>
        {(d.actions || []).map((a, i) => (
          <ActionRow key={i} T={T} action={a} liveMode={liveMode}
            expanded={expandedAction === i}
            onToggle={()=> setExpandedAction(expandedAction === i ? null : i)}
            onExecute={()=> {
              executeAction({
                prompt: a.prompt, api: a.api, label: a.verb, itemId: d.id,
                dismissOnRun: a.color !== undefined,
              });
              if (liveMode && a.color !== undefined) onClose && onClose();
            }}/>
        ))}
      </div>
    </div>
  );
}

function ConsoleNote({ T, liveMode }) {
  return (
    <div style={{
      padding:'8px 11px', borderRadius:7, fontSize:11, lineHeight:1.5,
      background: liveMode ? 'rgba(16,185,129,.07)' : T.panel2,
      border:`1px solid ${liveMode ? 'rgba(16,185,129,.25)' : T.border}`,
      color: liveMode ? '#10b981' : T.sub,
    }}>
      {liveMode
        ? <><b>One-click mode active</b> — buttons POST to <code style={{fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:10.5}}>/api/action</code>. Toggle off in the header to copy prompts instead.</>
        : <><b>Command console</b> — buttons copy a prompt to paste into Claude. Toggle the header pill on (or run <code style={{fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:10.5}}>scripts/dashboard-server.py</code>) for one-click actions.</>}
    </div>
  );
}

function ActionRow({ T, action, liveMode, expanded, onToggle, onExecute }) {
  const color = action.color === 'green' ? '#10b981' : action.color === 'red' ? '#ef4444' : null;
  const isPrimary = action.primary;
  return (
    <div style={{
      border:`1px solid ${expanded ? T.accentBorder : T.border}`,
      borderRadius:8, background: expanded ? T.panel : T.panel2, overflow:'hidden',
    }}>
      <div style={{display:'flex', alignItems:'center', gap:7, padding:'7px 8px 7px 10px'}}>
        <button onClick={onExecute} style={{
          flex:1, padding:'5px 11px', borderRadius:6, border: color ? `1px solid ${color}` : isPrimary ? `1px solid ${T.accent}` : `1px solid ${T.border}`,
          background: color ? color : isPrimary ? T.accent : T.panel,
          color: color || isPrimary ? '#fff' : T.text,
          fontWeight:600, fontSize:12, cursor:'pointer', textAlign:'left',
          display:'inline-flex', alignItems:'center', gap:7,
        }}>
          <span style={{flex:1}}>{action.verb}</span>
          <span style={{
            fontSize:10, opacity:.75, padding:'1px 5px', borderRadius:3,
            background: color || isPrimary ? 'rgba(255,255,255,.18)' : T.panel2,
            border: color || isPrimary ? 'none' : `1px solid ${T.border}`,
          }}>{liveMode ? 'Run' : '⌘C'}</span>
        </button>
        <button onClick={onToggle} title="Show prompt" style={{
          padding:'5px 8px', borderRadius:6, border:`1px solid ${T.border}`,
          background:T.panel, color:T.sub, fontWeight:600, fontSize:11, cursor:'pointer',
        }}>{expanded ? '\u2212' : '\u2026'}</button>
      </div>
      {expanded && (
        <div style={{padding:'4px 10px 10px'}}>
          <div style={{
            fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:11, color:T.text,
            background: T.bg, border:`1px solid ${T.border}`, borderRadius:6,
            padding:'8px 10px', whiteSpace:'pre-wrap', wordBreak:'break-word', lineHeight:1.5,
          }}>{action.prompt}</div>
          {action.api && (
            <div style={{marginTop:5, fontSize:10.5, color:T.faint, fontFamily:'"SF Mono",ui-monospace,monospace'}}>
              POST /api/action {JSON.stringify(action.api)}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/* ---------- Outputs view ---------- */
function OutputsView({ T, onSelectOutput }) {
  const [groupFilter, setGroupFilter] = useState('all');
  const [reviewFilter, setReviewFilter] = useState('all');
  const groups = ['all', ...Array.from(new Set(OUTPUTS.map(o => o.group)))];
  const reviewStates = ['all','pending','flagged','approved','standing'];
  const list = OUTPUTS.filter(o => {
    if (groupFilter !== 'all' && o.group !== groupFilter) return false;
    if (reviewFilter !== 'all' && o.review !== reviewFilter) return false;
    return true;
  });
  const counts = OUTPUTS.reduce((acc,o)=>{ acc[o.review] = (acc[o.review]||0)+1; return acc; }, {});
  return (
    <div style={{display:'flex', flexDirection:'column', gap:12}}>
      {/* Status strip */}
      <div style={{display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap:10}}>
        <ReviewKpi T={T} label="Pending"  value={counts.pending||0}  color="#f59e0b"/>
        <ReviewKpi T={T} label="Flagged"  value={counts.flagged||0}  color="#ef4444"/>
        <ReviewKpi T={T} label="Approved" value={counts.approved||0} color="#10b981"/>
        <ReviewKpi T={T} label="Standing" value={counts.standing||0} color={T.sub}/>
      </div>

      {/* Filters */}
      <div style={{display:'flex', gap:7, alignItems:'center', flexWrap:'wrap'}}>
        {reviewStates.map(s => (
          <button key={s} onClick={()=> setReviewFilter(s)} style={{
            padding:'4px 10px', borderRadius:6, fontSize:11.5, fontWeight:600,
            border:`1px solid ${reviewFilter===s ? T.accentBorder : T.border}`,
            background: reviewFilter===s ? T.accentSoft : T.panel,
            color: reviewFilter===s ? T.accent : T.sub,
            cursor:'pointer', textTransform:'capitalize',
          }}>{s}</button>
        ))}
        <div style={{flex:1}}/>
        <select value={groupFilter} onChange={e=> setGroupFilter(e.target.value)} style={{
          padding:'5px 10px', borderRadius:6, fontSize:11.5,
          border:`1px solid ${T.border}`, background:T.panel, color:T.text, outline:'none', fontFamily:'inherit',
        }}>
          {groups.map(g => <option key={g} value={g}>{g === 'all' ? 'All groups' : g}</option>)}
        </select>
      </div>

      {/* Grouped list */}
      <Panel T={T} title={`Outputs \u2014 ${list.length}`} sub="agent-authored artifacts">
        <div style={{display:'flex', flexDirection:'column', gap:14}}>
          {Array.from(new Set(list.map(o => o.group))).map(g => {
            const items = list.filter(o => o.group === g);
            return (
              <div key={g}>
                <div style={{fontSize:10.5, fontWeight:700, color:T.mute, textTransform:'uppercase', letterSpacing:.06, marginBottom:7, padding:'0 2px'}}>{g}</div>
                <div style={{display:'flex', flexDirection:'column', gap:5}}>
                  {items.map(o => <OutputRow key={o.path} T={T} o={o} onClick={()=> onSelectOutput(o)}/>)}
                </div>
              </div>
            );
          })}
        </div>
      </Panel>
    </div>
  );
}
function ReviewKpi({ T, label, value, color }) {
  return (
    <div style={{
      background:T.panel, border:`1px solid ${T.border}`, borderRadius:9, padding:'10px 12px',
      display:'flex', alignItems:'center', gap:10, boxShadow:T.shadowSm,
    }}>
      <span style={{width:8, height:8, borderRadius:'50%', background:color}}/>
      <div style={{flex:1}}>
        <div style={{fontSize:10.5, color:T.sub, fontWeight:600, textTransform:'uppercase', letterSpacing:.05}}>{label}</div>
        <div style={{fontSize:20, fontWeight:700, color:T.text, fontVariantNumeric:'tabular-nums', letterSpacing:-0.3, marginTop:1}}>{value}</div>
      </div>
    </div>
  );
}
function OutputRow({ T, o, onClick }) {
  const reviewColor = { pending:'#f59e0b', flagged:'#ef4444', approved:'#10b981', standing:T.sub }[o.review] || T.sub;
  return (
    <div onClick={onClick} style={{
      display:'flex', alignItems:'center', gap:10, padding:'8px 11px',
      background:T.panel2, border:`1px solid ${T.border}`, borderRadius:7, cursor:'pointer',
    }}
    onMouseEnter={e=> e.currentTarget.style.borderColor = T.accentBorder}
    onMouseLeave={e=> e.currentTarget.style.borderColor = T.border}>
      <span style={{
        fontSize:9.5, fontWeight:700, padding:'2px 7px', borderRadius:4,
        background: reviewColor+'1f', color: reviewColor, textTransform:'uppercase', letterSpacing:.05,
        flexShrink:0, minWidth:64, textAlign:'center',
      }}>{o.review}</span>
      <code style={{
        fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:11, color:T.text,
        flex:1, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap',
      }} title={o.path}>{o.path}</code>
      <span style={{fontSize:11, color:T.sub, whiteSpace:'nowrap'}}>{o.agent}</span>
      <span style={{fontSize:10.5, color:T.faint, whiteSpace:'nowrap', minWidth:50, textAlign:'right'}}>{o.age}</span>
    </div>
  );
}

function OutputDetail({ T, o, liveMode, executeAction }) {
  const reviewColor = { pending:'#f59e0b', flagged:'#ef4444', approved:'#10b981', standing:T.sub }[o.review] || T.sub;
  const actions = o.review === 'standing' ? [
    { verb:'Open file', prompt:`Show me ${o.path}.`, api:{type:'open',path:o.path}, primary:true },
  ] : [
    { verb:'Open file',  prompt:`Show me ${o.path}.`, api:{type:'open',path:o.path}, primary:true },
    { verb:'Approve',    prompt:`Approve ${o.path} and log the verdict.`, api:{type:'output-approve',path:o.path}, color:'green' },
    { verb:'Revise',     prompt:`Rewrite ${o.path} with these changes: `, api:null },
    { verb:'Reject',     prompt:`Reject ${o.path} \u2014 delete it and log a Rejected row.`, api:{type:'output-reject',path:o.path}, color:'red' },
  ];
  const [expandedAction, setExpandedAction] = useState(null);
  return (
    <div style={{display:'flex', flexDirection:'column', gap:14}}>
      <div style={{display:'flex', alignItems:'center', gap:8}}>
        <span style={{
          fontSize:10, fontWeight:700, padding:'2px 8px', borderRadius:4,
          background: reviewColor+'1f', color: reviewColor, textTransform:'uppercase', letterSpacing:.05,
        }}>{o.review}</span>
        <span style={{fontSize:11.5, color:T.sub}}>{o.group}</span>
      </div>
      <div style={{padding:'10px 12px', background:T.panel2, border:`1px solid ${T.border}`, borderRadius:8}}>
        <code style={{fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:12, color:T.text, wordBreak:'break-all'}}>{o.path}</code>
      </div>
      <DL T={T} pairs={[
        ['Author', o.agent],
        ['Via',    o.via],
        ['Age',    o.age],
      ]}/>
      <ConsoleNote T={T} liveMode={liveMode}/>
      <div style={{display:'flex', flexDirection:'column', gap:7}}>
        {actions.map((a, i) => (
          <ActionRow key={i} T={T} action={a} liveMode={liveMode}
            expanded={expandedAction === i}
            onToggle={()=> setExpandedAction(expandedAction === i ? null : i)}
            onExecute={()=> executeAction({ prompt:a.prompt, api:a.api, label:a.verb, itemId:null, dismissOnRun:false })}/>
        ))}
      </div>
    </div>
  );
}

function BacklogDetail({ T, item }) {
  return (
    <div style={{display:'flex', flexDirection:'column', gap:14}}>
      <div>
        <div style={{display:'flex', alignItems:'center', gap:8, marginBottom:6}}>
          <SevBadge T={T} sev={item.sev}/>
          <span style={{fontSize:11, color:T.mute, padding:'2px 7px', borderRadius:4, background:T.panel2, border:`1px solid ${T.border}`}}>{item.stage}</span>
          <span style={{fontSize:11, color:T.mute, marginLeft:'auto'}}>{item.age}</span>
        </div>
        <div style={{fontSize:14, fontWeight:600, color:T.text, lineHeight:1.4}}>{item.title}</div>
      </div>
      <DL T={T} pairs={[
        ['ID', item.id],
        ['Area', item.area],
        ['Owner', item.owner],
        ['File(s)', item.files],
      ]}/>
      <div style={{display:'flex', gap:8, flexWrap:'wrap'}}>
        <button style={{padding:'7px 14px', borderRadius:7, border:`1px solid ${T.accent}`, background:T.accent, color:'#fff', fontWeight:600, fontSize:12, cursor:'pointer'}}>Send to dev-agent</button>
        <button style={{padding:'7px 14px', borderRadius:7, border:`1px solid ${T.border}`, background:T.panel, color:T.text, fontWeight:600, fontSize:12, cursor:'pointer'}}>Move stage</button>
        <button style={{padding:'7px 14px', borderRadius:7, border:`1px solid ${T.border}`, background:T.panel, color:T.text, fontWeight:600, fontSize:12, cursor:'pointer'}}>Mark done</button>
      </div>
    </div>
  );
}

function DL({ T, pairs }) {
  return (
    <div style={{display:'grid', gridTemplateColumns:'110px 1fr', gap:'5px 14px', fontSize:12}}>
      {pairs.map(([k,v]) => (
        <React.Fragment key={k}>
          <div style={{color:T.mute, fontSize:11}}>{k}</div>
          <div style={{color:T.text}}>{v}</div>
        </React.Fragment>
      ))}
    </div>
  );
}

/* ---------- Toast ---------- */
function Toast({ T, children }) {
  return (
    <div style={{
      position:'absolute', bottom:20, left:'50%', transform:'translateX(-50%)',
      background:T.text, color:T.bg, padding:'9px 16px', borderRadius:8,
      fontSize:12, fontWeight:600, boxShadow:'0 10px 28px rgba(0,0,0,.3)', zIndex:30,
      animation:'fadeIn .18s ease-out',
    }}>{children}</div>
  );
}

window.CommandCenter = CommandCenter;
