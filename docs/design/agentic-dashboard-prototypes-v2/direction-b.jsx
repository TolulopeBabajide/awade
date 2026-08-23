// Direction B — "Inbox"
// Three-pane triage app (sidebar / list / reading pane). Inbox-first.
// Everything you need to do is the primary view. Pulse/Roster/Pipeline
// live in the sidebar.

const { useState: useStateB, useEffect: useEffectB, useMemo: useMemoB } = React;

/* ---------- Helpers ---------- */
const STATUS_COLOR_B = {
  healthy:   '#10b981',
  warning:   '#f59e0b',
  critical:  '#ef4444',
  idle:      '#a1a1aa',
  'on-demand':'#60a5fa',
};
const URGENCY_TINT = { high:'#ef4444', medium:'#f59e0b', low:'#10b981' };

const KIND_GLYPH = {
  approve: '✓',
  decide:  '?',
  review:  '◔',
  respond: '↩',
};

function InboxApp({ theme, liveMode, setLiveMode }) {
  const [view, setView] = useStateB('inbox');
  const [filter, setFilter] = useStateB('all'); // inbox filters
  const [selectedId, setSelectedId] = useStateB(DECISIONS[0]?.id);
  const [dismissed, setDismissed] = useStateB(new Set());
  const [resolved, setResolved] = useStateB({}); // id -> verb
  const [events, setEvents] = useStateB(EVENTS);
  const [runs24h, setRuns24h] = useStateB(STATS.runs24h);
  const [search, setSearch] = useStateB('');
  const [toast, setToast] = useStateB(null);
  const [runningAgent, setRunningAgent] = useStateB(null);
  const [selectedAgent, setSelectedAgent] = useStateB(null);
  const [selectedOutput, setSelectedOutput] = useStateB(null);
  // liveMode is lifted to App — shared with Direction A.

  // Live ticker
  useEffectB(()=>{
    const t = setInterval(()=>{
      const fresh = [
        { who:'dev-agent',         summary:'Picked up H-122 from ready' },
        { who:'qa-agent',          summary:'Coverage 87.4%' },
        { who:'dashboard-refresh', summary:'Rebuilt in 1.2s' },
        { who:'improvement-agent', summary:'Promoted 2 backlog items' },
      ];
      const e = fresh[Math.floor(Math.random()*fresh.length)];
      setEvents(prev => [{ id:'b-live-'+Date.now(), ...e, kind:'run', status:'done', age:'just now', fresh:true }, ...prev].slice(0,40));
      setRuns24h(r => r+1);
    }, 6000);
    return ()=> clearInterval(t);
  },[]);

  /* ---------- Theme tokens ---------- */
  const T = theme === 'dark' ? {
    bg:'#0a0b0e', appShell:'#101116', panel:'#15171c', panel2:'#1a1d24', panelHover:'#1d2028',
    border:'#23252e', borderStrong:'#33363f',
    text:'#ededee', sub:'#a3a4ad', mute:'#74757d', faint:'#52535b',
    accent:'#6366f1', accentSoft:'rgba(99,102,241,.16)', accentBorder:'rgba(99,102,241,.55)',
    selectedBg:'rgba(99,102,241,.14)',
    shadow:'0 1px 2px rgba(0,0,0,.4), 0 8px 24px rgba(0,0,0,.32)',
    headerBg:'#0e1014',
  } : {
    bg:'#fbfbfc', appShell:'#f1f1f4', panel:'#ffffff', panel2:'#f8f8fb', panelHover:'#f3f3f6',
    border:'#e8e8ec', borderStrong:'#d5d5dc',
    text:'#15161a', sub:'#54555c', mute:'#7d7e85', faint:'#a8a9b0',
    accent:'#4f46e5', accentSoft:'rgba(79,70,229,.07)', accentBorder:'rgba(79,70,229,.4)',
    selectedBg:'rgba(79,70,229,.08)',
    shadow:'0 1px 2px rgba(20,20,30,.04), 0 8px 22px rgba(20,20,30,.06)',
    headerBg:'#fafafb',
  };

  function showToast(msg){ setToast(msg); setTimeout(()=> setToast(null), 2000); }
  function copyToClipboardB(txt){
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
  function executeAction({ prompt, api, label, itemId, dismissOnRun = true }){
    if (!liveMode) {
      copyToClipboardB(prompt);
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
    setRunningAgent(name); showToast(`Running ${name}…`);
    setTimeout(()=>{
      setRunningAgent(null);
      setEvents(prev => [{ id:'b-manual-'+Date.now(), who:name, kind:'run', status:'done', summary:'Manual run completed', age:'just now', fresh:true }, ...prev].slice(0,40));
      setRuns24h(r => r+1);
      showToast(`✓ ${name} ran successfully`);
    }, 1400);
  }

  const visibleDecisions = useMemoB(()=> {
    let xs = DECISIONS.filter(d => !dismissed.has(d.id));
    if (filter === 'urgent')  xs = xs.filter(d => d.urgency === 'high');
    if (filter === 'approve') xs = xs.filter(d => d.kind === 'approve');
    if (filter === 'decide')  xs = xs.filter(d => d.kind === 'decide');
    if (filter === 'review')  xs = xs.filter(d => d.kind === 'review');
    if (filter === 'respond') xs = xs.filter(d => d.kind === 'respond');
    if (search) {
      const q = search.toLowerCase();
      xs = xs.filter(d => (d.title + ' ' + d.from + ' ' + d.detail).toLowerCase().includes(q));
    }
    return xs;
  }, [dismissed, filter, search]);

  // Keep selected valid
  useEffectB(()=>{
    if (!visibleDecisions.find(d => d.id === selectedId)) {
      setSelectedId(visibleDecisions[0]?.id);
    }
  }, [visibleDecisions, selectedId]);

  const selected = DECISIONS.find(d => d.id === selectedId);

  return (
    <div style={{
      width:'100%', height:'100%', background:T.appShell, color:T.text,
      fontFamily:'-apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", system-ui, sans-serif',
      fontSize:13, lineHeight:1.45, display:'flex', overflow:'hidden',
    }}>
      <SidebarB T={T} view={view} setView={setView}
        pendingCount={visibleDecisions.length}
        outputsBadge={OUTPUTS.filter(o => o.review === 'pending' || o.review === 'flagged').length}/>
      <div style={{flex:1, display:'flex', flexDirection:'column', minWidth:0}}>
        <TopBarB T={T} search={search} setSearch={setSearch} runs24h={runs24h} liveMode={liveMode} setLiveMode={setLiveMode}/>
        <div style={{flex:1, display:'flex', minHeight:0}}>
          {view==='inbox' && (
            <InboxView T={T} decisions={visibleDecisions} filter={filter} setFilter={setFilter}
              selected={selected} setSelectedId={setSelectedId} liveMode={liveMode}
              executeAction={executeAction} resolved={resolved}/>
          )}
          {view==='outputs' && (
            <OutputsViewB T={T} onSelectOutput={setSelectedOutput}/>
          )}
          {view==='pulse' && <PulseView T={T} events={events}/>}
          {view==='roster' && <RosterViewB T={T} runAgent={runAgent} runningAgent={runningAgent}
            onSelectAgent={setSelectedAgent}/>}
          {view==='pipeline' && <PipelineView T={T}/>}
        </div>
      </div>
      {selectedAgent && (
        <AgentSheet T={T} agent={selectedAgent} onClose={()=> setSelectedAgent(null)}
          runAgent={runAgent} runningAgent={runningAgent}/>
      )}
      {selectedOutput && (
        <OutputSheet T={T} o={selectedOutput} onClose={()=> setSelectedOutput(null)}
          liveMode={liveMode} executeAction={executeAction}/>
      )}
      {toast && (
        <div style={{
          position:'absolute', bottom:20, left:'50%', transform:'translateX(-50%)',
          background:T.text, color:T.bg, padding:'9px 16px', borderRadius:8,
          fontSize:12, fontWeight:600, boxShadow:'0 10px 28px rgba(0,0,0,.3)', zIndex:30,
          animation:'fadeIn .18s ease-out',
        }}>{toast}</div>
      )}
    </div>
  );
}

/* ---------- Sidebar ---------- */
function SidebarB({ T, view, setView, pendingCount, outputsBadge }) {
  const items = [
    { id:'inbox',    label:'Inbox',    badge:pendingCount, icon:'M3 8l9 6 9-6M3 8v10h18V8M3 8l9-5 9 5' },
    { id:'outputs',  label:'Outputs',  badge:outputsBadge, icon:'M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zM14 2v6h6M9 13h6M9 17h6M9 9h2' },
    { id:'pulse',    label:'Pulse',    icon:'M3 12h4l3-8 4 16 3-8h4' },
    { id:'roster',   label:'Roster',   icon:'M8 11a4 4 0 100-8 4 4 0 000 8zm-7 10a7 7 0 1114 0M16 11a4 4 0 100-8 4 4 0 000 8zm7 10a7 7 0 00-7-7' },
    { id:'pipeline', label:'Pipeline', icon:'M3 6h6M3 12h6M3 18h6M15 6h6M15 12h6M15 18h6' },
  ];
  return (
    <div style={{
      width:200, background:T.headerBg, borderRight:`1px solid ${T.border}`,
      display:'flex', flexDirection:'column', flexShrink:0,
    }}>
      <div style={{padding:'15px 14px 14px', display:'flex', alignItems:'center', gap:9}}>
        <div style={{
          width:26, height:26, borderRadius:7, background:`linear-gradient(135deg, ${T.accent}, #8b5cf6)`,
          display:'flex', alignItems:'center', justifyContent:'center', color:'#fff', fontWeight:700, fontSize:11,
        }}>AT</div>
        <div>
          <div style={{fontWeight:700, fontSize:12.5, letterSpacing:-0.1}}>Agentic Team</div>
          <div style={{fontSize:10.5, color:T.mute}}>33 agents</div>
        </div>
      </div>
      <div style={{padding:'4px 8px', display:'flex', flexDirection:'column', gap:1}}>
        {items.map(it => {
          const active = view === it.id;
          return (
            <div key={it.id} onClick={()=> setView(it.id)} style={{
              display:'flex', alignItems:'center', gap:9, padding:'7px 10px', borderRadius:7,
              background: active ? T.selectedBg : 'transparent',
              color: active ? T.accent : T.sub,
              fontWeight: active ? 600 : 500, fontSize:12.5, cursor:'pointer',
            }}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d={it.icon}/>
              </svg>
              <span style={{flex:1}}>{it.label}</span>
              {it.badge != null && it.badge > 0 && (
                <span style={{
                  fontSize:10.5, fontWeight:700, padding:'1px 6px', borderRadius:4,
                  background: active ? T.accent : T.panel2,
                  color: active ? '#fff' : T.text,
                  border: active ? 'none' : `1px solid ${T.border}`,
                  minWidth:18, textAlign:'center',
                }}>{it.badge}</span>
              )}
            </div>
          );
        })}
      </div>
      <div style={{flex:1}}/>
      <div style={{padding:'10px 14px', borderTop:`1px solid ${T.border}`, fontSize:10.5, color:T.mute}}>
        <div style={{display:'flex', alignItems:'center', gap:5, marginBottom:3}}>
          <span style={{width:6, height:6, borderRadius:'50%', background:'#10b981', boxShadow:'0 0 0 3px rgba(16,185,129,.2)'}}/>
          <span style={{fontWeight:600, color:T.sub}}>System healthy</span>
        </div>
        <div>Refreshed 8m ago · hourly</div>
      </div>
    </div>
  );
}

/* ---------- Top bar ---------- */
function TopBarB({ T, search, setSearch, runs24h, liveMode, setLiveMode }) {
  return (
    <div style={{
      padding:'10px 16px', background:T.panel, borderBottom:`1px solid ${T.border}`,
      display:'flex', alignItems:'center', gap:12, flexShrink:0,
    }}>
      <div style={{flex:1, maxWidth:480, position:'relative'}}>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={T.mute} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
          style={{position:'absolute', left:11, top:'50%', transform:'translateY(-50%)'}}>
          <circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>
        </svg>
        <input
          placeholder="Search agents, inbox, backlog, outputs…"
          value={search} onChange={e=> setSearch(e.target.value)}
          style={{
            width:'100%', padding:'7px 11px 7px 32px', borderRadius:7, fontSize:12.5,
            border:`1px solid ${T.border}`, background:T.panel2, color:T.text, outline:'none',
          }}/>
      </div>
      {/* Mode toggle */}
      <div onClick={()=> setLiveMode(!liveMode)}
        title={liveMode ? 'One-click — actions POST to /api/action' : 'Command console — actions copy a Claude prompt'}
        style={{
          display:'inline-flex', alignItems:'center', gap:7, padding:'4px 11px', borderRadius:999,
          border:`1px solid ${liveMode ? 'rgba(16,185,129,.4)' : T.border}`,
          background: liveMode ? 'rgba(16,185,129,.08)' : T.panel2,
          cursor:'pointer', fontSize:11.5, fontWeight:600,
          color: liveMode ? '#10b981' : T.sub,
        }}>
        <span style={{
          width:7, height:7, borderRadius:'50%',
          background: liveMode ? '#10b981' : T.mute,
          boxShadow: liveMode ? '0 0 0 4px rgba(16,185,129,.18)' : 'none',
        }}/>
        <span>{liveMode ? 'One-click' : 'Command console'}</span>
      </div>
      <div style={{
        padding:'4px 10px', borderRadius:6, border:`1px solid ${T.border}`, background:T.panel2,
        fontSize:11, color:T.sub,
      }}>
        <span style={{color:T.mute}}>Runs / 24h </span>
        <span style={{color:T.text, fontWeight:700, fontVariantNumeric:'tabular-nums'}}>{runs24h}</span>
      </div>
    </div>
  );
}

/* ---------- Inbox view (three-pane) ---------- */
function InboxView({ T, decisions, filter, setFilter, selected, setSelectedId, liveMode, executeAction, resolved }) {
  return (
    <>
      {/* Categories rail */}
      <div style={{
        width:160, background:T.headerBg, borderRight:`1px solid ${T.border}`,
        padding:'14px 10px', display:'flex', flexDirection:'column', gap:1, flexShrink:0,
      }}>
        <div style={{padding:'2px 8px 6px', fontSize:10.5, fontWeight:700, color:T.mute, textTransform:'uppercase', letterSpacing:.06}}>Triage</div>
        {[
          { id:'all',     label:'Everything',  count:DECISIONS.length },
          { id:'urgent',  label:'Urgent',       count:DECISIONS.filter(d=>d.urgency==='high').length, tint:'#ef4444' },
          { id:'approve', label:'Approvals',   count:DECISIONS.filter(d=>d.kind==='approve').length },
          { id:'decide',  label:'Decisions',   count:DECISIONS.filter(d=>d.kind==='decide').length },
          { id:'review',  label:'Reviews',     count:DECISIONS.filter(d=>d.kind==='review').length },
          { id:'respond', label:'Responses',   count:DECISIONS.filter(d=>d.kind==='respond').length },
        ].map(c => {
          const active = filter === c.id;
          return (
            <div key={c.id} onClick={()=> setFilter(c.id)} style={{
              display:'flex', alignItems:'center', gap:7, padding:'6px 10px', borderRadius:6,
              background: active ? T.selectedBg : 'transparent',
              color: active ? T.accent : T.sub,
              fontWeight: active ? 600 : 500, fontSize:12, cursor:'pointer',
            }}>
              {c.tint && <span style={{width:6, height:6, borderRadius:'50%', background:c.tint, flexShrink:0}}/>}
              <span style={{flex:1, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap'}}>{c.label}</span>
              <span style={{fontSize:10.5, color: active ? T.accent : T.mute, fontVariantNumeric:'tabular-nums'}}>{c.count}</span>
            </div>
          );
        })}
        <div style={{padding:'14px 8px 6px', fontSize:10.5, fontWeight:700, color:T.mute, textTransform:'uppercase', letterSpacing:.06}}>Status</div>
        <div style={{padding:'6px 10px', fontSize:11.5, color:T.sub, display:'flex', alignItems:'center', gap:6}}>
          <span style={{width:5, height:5, borderRadius:'50%', background:'#10b981'}}/>{STATS.agentsHealthy} healthy
        </div>
        <div style={{padding:'6px 10px', fontSize:11.5, color:T.sub, display:'flex', alignItems:'center', gap:6}}>
          <span style={{width:5, height:5, borderRadius:'50%', background:'#f59e0b'}}/>{STATS.agentsWarning} warning
        </div>
        <div style={{padding:'6px 10px', fontSize:11.5, color:T.sub, display:'flex', alignItems:'center', gap:6}}>
          <span style={{width:5, height:5, borderRadius:'50%', background:T.mute}}/>{STATS.agentsIdle + STATS.agentsOnDemand} idle
        </div>
      </div>

      {/* List */}
      <div style={{
        width:340, background:T.panel, borderRight:`1px solid ${T.border}`,
        display:'flex', flexDirection:'column', flexShrink:0,
      }}>
        <div style={{padding:'12px 14px 10px', borderBottom:`1px solid ${T.border}`}}>
          <div style={{display:'flex', alignItems:'baseline', justifyContent:'space-between'}}>
            <span style={{fontWeight:700, fontSize:13.5, color:T.text}}>
              {filter==='all' ? 'Inbox' : filter.charAt(0).toUpperCase()+filter.slice(1)}
            </span>
            <span style={{fontSize:11, color:T.mute, fontVariantNumeric:'tabular-nums'}}>{decisions.length} pending</span>
          </div>
          <div style={{fontSize:11, color:T.sub, marginTop:2}}>
            {decisions.length === 0 ? 'Nothing waiting on you.' : 'Tap to review · ↵ to approve'}
          </div>
        </div>
        <div style={{flex:1, overflow:'auto'}}>
          {decisions.length === 0 ? (
            <div style={{padding:'40px 24px', textAlign:'center', color:T.sub}}>
              <div style={{fontSize:30, color:'#10b981', marginBottom:8}}>✓</div>
              <div style={{fontWeight:600, color:T.text, marginBottom:3}}>Inbox zero</div>
              <div style={{fontSize:11.5}}>The agents will surface anything new here.</div>
            </div>
          ) : decisions.map((d, i) => {
            const isSelected = selected?.id === d.id;
            const tint = URGENCY_TINT[d.urgency];
            return (
              <div key={d.id} onClick={()=> setSelectedId(d.id)} style={{
                padding:'11px 14px', borderBottom:`1px solid ${T.border}`,
                background: isSelected ? T.selectedBg : 'transparent',
                borderLeft: `3px solid ${isSelected ? T.accent : 'transparent'}`,
                cursor:'pointer', position:'relative',
              }}
              onMouseEnter={e=> { if (!isSelected) e.currentTarget.style.background = T.panelHover; }}
              onMouseLeave={e=> { if (!isSelected) e.currentTarget.style.background = 'transparent'; }}>
                <div style={{display:'flex', alignItems:'center', gap:7, marginBottom:3}}>
                  <span style={{
                    width:16, height:16, borderRadius:4, background:tint+'22', color:tint,
                    display:'inline-flex', alignItems:'center', justifyContent:'center',
                    fontSize:10, fontWeight:700,
                  }}>{KIND_GLYPH[d.kind]}</span>
                  <code style={{fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:10.5, color:T.text, fontWeight:600}}>{d.from}</code>
                  <span style={{flex:1}}/>
                  <span style={{fontSize:10.5, color:T.faint}}>{d.age}</span>
                </div>
                <div style={{fontSize:12.5, fontWeight:600, color:T.text, lineHeight:1.35, marginBottom:3}}>{d.title}</div>
                {d.originPath && (
                  <div style={{
                    fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:10, color:T.mute,
                    marginBottom:3, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap',
                  }} title={d.originPath}>{d.originPath}</div>
                )}
                <div style={{fontSize:11, color:T.sub, lineHeight:1.4, overflow:'hidden', display:'-webkit-box', WebkitLineClamp:1, WebkitBoxOrient:'vertical'}}>
                  {d.detail}
                </div>
                <div style={{display:'flex', gap:5, marginTop:5}}>
                  <span style={{
                    fontSize:9.5, padding:'1px 6px', borderRadius:3, fontWeight:600, textTransform:'uppercase', letterSpacing:.04,
                    background:tint+'18', color:tint,
                  }}>{d.urgency}</span>
                  <span style={{fontSize:10, padding:'1px 6px', borderRadius:3, background:T.panel2, color:T.mute, border:`1px solid ${T.border}`}}>~{d.est}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Reading pane */}
      <div style={{flex:1, background:T.panel2, minWidth:0, overflow:'auto'}}>
        {selected ? <DecisionReader T={T} d={selected} liveMode={liveMode} executeAction={executeAction}/> :
          <div style={{padding:60, textAlign:'center', color:T.sub}}>
            <div style={{fontSize:30, color:'#10b981', marginBottom:8}}>✓</div>
            <div style={{fontSize:14, fontWeight:600, color:T.text}}>You're all caught up.</div>
            <div style={{fontSize:12, marginTop:4}}>The agents are running. Nothing needs you right now.</div>
          </div>
        }
      </div>
    </>
  );
}

function DecisionReader({ T, d, liveMode, executeAction }) {
  const tint = URGENCY_TINT[d.urgency];
  const [expandedAction, setExpandedAction] = useStateB(null);
  // Reset expansion when switching items
  useEffectB(()=> { setExpandedAction(null); }, [d.id]);
  return (
    <div style={{padding:'24px 28px 32px', maxWidth:680, margin:'0 auto'}}>
      <div style={{display:'flex', alignItems:'center', gap:8, marginBottom:14}}>
        <span style={{
          fontSize:10, padding:'2px 7px', borderRadius:4, fontWeight:700, textTransform:'uppercase', letterSpacing:.05,
          background:tint+'18', color:tint,
        }}>{d.urgency} · {d.kind}</span>
        <span style={{color:T.faint}}>·</span>
        <span style={{fontSize:11, color:T.sub}}>{d.via}</span>
        <span style={{flex:1}}/>
        <span style={{fontSize:11, color:T.mute}}>{d.age} · ~{d.est} read</span>
      </div>
      <h1 style={{fontSize:21, fontWeight:700, color:T.text, lineHeight:1.25, marginBottom:8, letterSpacing:-0.3}}>
        {d.title}
      </h1>
      <div style={{display:'flex', alignItems:'center', gap:6, marginBottom:14, fontSize:12, color:T.sub, flexWrap:'wrap'}}>
        <span>Drafted by</span>
        <code style={{fontFamily:'"SF Mono",ui-monospace,monospace', color:T.text, padding:'1px 6px', borderRadius:4, background:T.panel, border:`1px solid ${T.border}`, fontSize:11}}>{d.from}</code>
        {d.relatedBacklog && <>
          <span style={{color:T.faint}}>·</span>
          <span>filed</span>
          <code style={{fontFamily:'"SF Mono",ui-monospace,monospace', color:T.text, padding:'1px 6px', borderRadius:4, background:T.panel, border:`1px solid ${T.border}`, fontSize:11}}>{d.relatedBacklog}</code>
        </>}
      </div>

      {/* Source path — the real artifact on disk */}
      {d.originPath && (
        <div style={{
          display:'flex', alignItems:'center', gap:8, marginBottom:18,
          padding:'10px 12px', background:T.panel, border:`1px solid ${T.border}`, borderRadius:8,
        }}>
          <span style={{fontSize:10, fontWeight:700, color:T.mute, textTransform:'uppercase', letterSpacing:.05, flexShrink:0}}>Source</span>
          <code style={{
            fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:11.5, color:T.text,
            flex:1, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap',
          }} title={d.originPath}>{d.originPath}</code>
        </div>
      )}

      <div style={{
        padding:'14px 16px', background:T.panel, border:`1px solid ${T.border}`, borderRadius:9,
        fontSize:13, color:T.text, lineHeight:1.6, marginBottom:14,
      }}>
        {d.detail}
      </div>
      <div style={{
        padding:'10px 14px', background:tint+'10', border:`1px solid ${tint}33`, borderRadius:8,
        fontSize:12, color:T.text, lineHeight:1.5, marginBottom:18, display:'flex', alignItems:'center', gap:8,
      }}>
        <span style={{
          width:18, height:18, borderRadius:4, background:tint+'22', color:tint,
          display:'inline-flex', alignItems:'center', justifyContent:'center',
          flexShrink:0, fontSize:11, fontWeight:700,
        }}>!</span>
        <span><b style={{color:tint}}>Impact:</b> <span style={{color:T.sub}}>{d.impact}</span></span>
      </div>

      {/* Console-mode hint */}
      <div style={{
        padding:'8px 11px', borderRadius:7, fontSize:11, lineHeight:1.5, marginBottom:12,
        background: liveMode ? 'rgba(16,185,129,.07)' : T.panel,
        border:`1px solid ${liveMode ? 'rgba(16,185,129,.25)' : T.border}`,
        color: liveMode ? '#10b981' : T.sub,
      }}>
        {liveMode
          ? <><b>One-click mode</b> — buttons POST to <code style={{fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:10.5}}>/api/action</code>.</>
          : <><b>Command console</b> — buttons copy a Claude prompt; toggle the topbar pill on for one-click.</>}
      </div>

      <div style={{display:'flex', flexDirection:'column', gap:7}}>
        {(d.actions || []).map((a, i) => (
          <ActionRowB key={i} T={T} action={a} liveMode={liveMode}
            expanded={expandedAction === i}
            onToggle={()=> setExpandedAction(expandedAction === i ? null : i)}
            onExecute={()=> executeAction({ prompt:a.prompt, api:a.api, label:a.verb, itemId:d.id, dismissOnRun: a.color !== undefined })}/>
        ))}
      </div>
    </div>
  );
}

function ActionRowB({ T, action, liveMode, expanded, onToggle, onExecute }) {
  const color = action.color === 'green' ? '#10b981' : action.color === 'red' ? '#ef4444' : null;
  const isPrimary = action.primary;
  return (
    <div style={{
      border:`1px solid ${expanded ? T.accentBorder : T.border}`,
      borderRadius:8, background: expanded ? T.panel : T.panel2, overflow:'hidden',
    }}>
      <div style={{display:'flex', alignItems:'center', gap:7, padding:'7px 8px 7px 10px'}}>
        <button onClick={onExecute} style={{
          flex:1, padding:'6px 11px', borderRadius:6, border: color ? `1px solid ${color}` : isPrimary ? `1px solid ${T.accent}` : `1px solid ${T.border}`,
          background: color ? color : isPrimary ? T.accent : T.panel,
          color: color || isPrimary ? '#fff' : T.text,
          fontWeight:600, fontSize:12.5, cursor:'pointer', textAlign:'left',
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
          padding:'6px 9px', borderRadius:6, border:`1px solid ${T.border}`,
          background:T.panel, color:T.sub, fontWeight:600, fontSize:11, cursor:'pointer',
        }}>{expanded ? '−' : '…'}</button>
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

/* ---------- Pulse view ---------- */
function PulseView({ T, events }) {
  return (
    <div style={{flex:1, padding:'18px 24px 28px', overflow:'auto'}}>
      <div style={{display:'grid', gridTemplateColumns:'1fr 320px', gap:16, alignItems:'start'}}>
        <div>
          <SectionHeader T={T} title="Activity stream" subtitle="Newest first · streaming" live/>
          <div style={{background:T.panel, border:`1px solid ${T.border}`, borderRadius:10, overflow:'hidden'}}>
            {events.slice(0, 24).map((e,i) => (
              <div key={e.id} style={{
                padding:'10px 14px', borderBottom: i < 23 ? `1px solid ${T.border}` : 'none',
                display:'flex', gap:10, alignItems:'flex-start',
                animation: e.fresh ? 'fadeIn .5s ease-out' : 'none',
              }}>
                <div style={{
                  width:7, height:7, borderRadius:'50%', flexShrink:0, marginTop:6,
                  background: e.status === 'fail' ? '#ef4444' : '#10b981',
                }}/>
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
            ))}
          </div>
        </div>

        <div style={{display:'flex', flexDirection:'column', gap:14}}>
          <SectionHeader T={T} title="Hourly loop" subtitle="The self-healing cadence"/>
          <div style={{background:T.panel, border:`1px solid ${T.border}`, borderRadius:10, padding:12, display:'flex', flexDirection:'column', gap:8}}>
            {HOURLY_LOOP.map((s,i) => (
              <div key={i} style={{display:'flex', alignItems:'flex-start', gap:9}}>
                <span style={{
                  fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:11, fontWeight:700,
                  color:T.accent, background:T.accentSoft,
                  padding:'2px 6px', borderRadius:4, flexShrink:0,
                }}>{s.at}</span>
                <div style={{flex:1, minWidth:0}}>
                  <div style={{fontSize:12, fontWeight:600, color:T.text}}>{s.name}</div>
                  <div style={{fontSize:11, color:T.sub, lineHeight:1.4}}>{s.desc}</div>
                </div>
              </div>
            ))}
          </div>

          <SectionHeader T={T} title="Today" subtitle="At a glance"/>
          <div style={{background:T.panel, border:`1px solid ${T.border}`, borderRadius:10, padding:12, display:'grid', gridTemplateColumns:'1fr 1fr', gap:10}}>
            <Kpi T={T} label="Runs" value={STATS.runs24h}/>
            <Kpi T={T} label="Backlog open" value={STATS.backlogOpen}/>
            <Kpi T={T} label="Done · 24h" value={STATS.backlogDone24h}/>
            <Kpi T={T} label="Alerts" value={STATS.alerts}/>
          </div>
        </div>
      </div>
    </div>
  );
}
function Kpi({ T, label, value }) {
  return (
    <div style={{padding:'8px 10px', background:T.panel2, borderRadius:7, border:`1px solid ${T.border}`}}>
      <div style={{fontSize:10, color:T.mute, fontWeight:600, textTransform:'uppercase', letterSpacing:.05}}>{label}</div>
      <div style={{fontSize:18, fontWeight:700, color:T.text, fontVariantNumeric:'tabular-nums', letterSpacing:-0.4, marginTop:2}}>{value}</div>
    </div>
  );
}
function SectionHeader({ T, title, subtitle, live }) {
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

/* ---------- Roster view (the org chart hero, in this view) ---------- */
function RosterViewB({ T, runAgent, runningAgent, onSelectAgent }) {
  const [statusFilter, setStatusFilter] = useStateB('all');
  const [q, setQ] = useStateB('');
  return (
    <div style={{flex:1, padding:'18px 24px 28px', overflow:'auto'}}>
      <SectionHeader T={T} title="The team" subtitle="33 agents · 9 departments"/>
      <div style={{display:'flex', gap:7, marginBottom:12, alignItems:'center', flexWrap:'wrap'}}>
        {['all','healthy','warning','idle','on-demand'].map(s => (
          <button key={s} onClick={()=> setStatusFilter(s)} style={{
            padding:'4px 10px', borderRadius:6, fontSize:11.5, fontWeight:600,
            border:`1px solid ${statusFilter===s ? T.accentBorder : T.border}`,
            background: statusFilter===s ? T.accentSoft : T.panel,
            color: statusFilter===s ? T.accent : T.sub,
            cursor:'pointer', textTransform:'capitalize',
          }}>{s}</button>
        ))}
        <div style={{flex:1}}/>
        <input
          placeholder="Search…" value={q} onChange={e=> setQ(e.target.value)}
          style={{
            padding:'5px 10px', borderRadius:6, fontSize:11.5, minWidth:200,
            border:`1px solid ${T.border}`, background:T.panel, color:T.text, outline:'none',
          }}/>
      </div>
      <div style={{display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap:10}}>
        {DEPARTMENTS.map(d => {
          const agents = d.agents.map(n => AGENTS.find(a => a.name === n)).filter(a => {
            if (statusFilter !== 'all' && a.status !== statusFilter) return false;
            if (q && !a.name.includes(q.toLowerCase())) return false;
            return true;
          });
          if (!agents.length) return null;
          const total = d.agents.length;
          return (
            <div key={d.id} style={{
              background:T.panel, border:`1px solid ${T.border}`, borderRadius:10,
              padding:'11px 13px', boxShadow:T.shadow,
            }}>
              <div style={{display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:9}}>
                <span style={{fontWeight:700, fontSize:12.5, color:T.text}}>{d.name}</span>
                <span style={{fontSize:10.5, color:T.mute, fontVariantNumeric:'tabular-nums'}}>{agents.length}/{total}</span>
              </div>
              <div style={{display:'flex', flexDirection:'column', gap:4}}>
                {agents.map(a => {
                  const running = runningAgent === a.name;
                  return (
                    <div key={a.name} onClick={()=> onSelectAgent(a)} style={{
                      display:'flex', alignItems:'center', gap:7, padding:'5px 7px', borderRadius:6,
                      cursor:'pointer', background:T.panel2, border:`1px solid ${T.border}`,
                    }}
                    onMouseEnter={e=> e.currentTarget.style.borderColor = T.accentBorder}
                    onMouseLeave={e=> e.currentTarget.style.borderColor = T.border}>
                      <span style={{
                        width:6, height:6, borderRadius:'50%', background:STATUS_COLOR_B[a.status], flexShrink:0,
                        boxShadow: running ? `0 0 0 3px ${STATUS_COLOR_B[a.status]}55` : 'none',
                        animation: running ? 'pulseDot 1s infinite' : 'none',
                      }}/>
                      <span style={{flex:1, fontSize:11.5, color:T.text, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap'}}>{a.name}</span>
                      <span style={{fontSize:10, color:T.faint, whiteSpace:'nowrap'}}>{a.lastRun}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function AgentSheet({ T, agent, onClose, runAgent, runningAgent }) {
  const dept = DEPARTMENTS.find(d => d.id === agent.dept);
  const running = runningAgent === agent.name;
  return (
    <div style={{
      position:'absolute', inset:0, background:'rgba(0,0,0,.4)',
      display:'flex', alignItems:'flex-end', justifyContent:'center', zIndex:25, padding:30,
      animation:'fadeIn .14s ease-out',
    }} onClick={onClose}>
      <div onClick={e=> e.stopPropagation()} style={{
        width:'100%', maxWidth:500, background:T.panel, borderRadius:12, padding:20,
        boxShadow:'0 22px 60px rgba(0,0,0,.4)', border:`1px solid ${T.border}`,
        animation:'slideUp .24s cubic-bezier(.2,.7,.3,1)',
      }}>
        <div style={{display:'flex', alignItems:'center', gap:10, marginBottom:14}}>
          <span style={{
            width:10, height:10, borderRadius:'50%', background:STATUS_COLOR_B[agent.status],
            boxShadow: running ? `0 0 0 4px ${STATUS_COLOR_B[agent.status]}33` : 'none',
            animation: running ? 'pulseDot 1s infinite' : 'none',
          }}/>
          <div style={{flex:1}}>
            <div style={{fontWeight:700, fontSize:14, color:T.text}}>{agent.name}</div>
            <div style={{fontSize:11.5, color:T.sub, marginTop:1}}>{dept?.name} · {agent.cadence}</div>
          </div>
          <span onClick={onClose} style={{cursor:'pointer', color:T.mute, padding:'4px 8px', borderRadius:5}}>✕</span>
        </div>
        <div style={{display:'grid', gridTemplateColumns:'110px 1fr', gap:'5px 14px', fontSize:12, marginBottom:14}}>
          <div style={{color:T.mute}}>Runtime</div><div>{agent.runtime}</div>
          <div style={{color:T.mute}}>Schedule</div><div>{agent.schedule}</div>
          <div style={{color:T.mute}}>Last run</div><div>{agent.lastRun}</div>
          <div style={{color:T.mute}}>Runs / 24h</div><div>{agent.runs24h}</div>
        </div>
        <div style={{display:'flex', gap:7}}>
          <button onClick={()=> runAgent(agent.name)} disabled={running} style={{
            padding:'7px 14px', borderRadius:7, border:`1px solid ${T.accent}`,
            background: running ? T.panel2 : T.accent,
            color: running ? T.sub : '#fff', fontWeight:600, fontSize:12, cursor: running ? 'default' : 'pointer',
            display:'inline-flex', alignItems:'center', gap:6,
          }}>
            {running ? <><span style={{width:6, height:6, borderRadius:'50%', background:T.accent, animation:'pulseDot 1s infinite'}}/> Running…</> : '▶  Run now'}
          </button>
          <button style={{padding:'7px 14px', borderRadius:7, border:`1px solid ${T.border}`, background:T.panel, color:T.text, fontWeight:600, fontSize:12, cursor:'pointer'}}>Pause</button>
          <button style={{padding:'7px 14px', borderRadius:7, border:`1px solid ${T.border}`, background:T.panel, color:T.text, fontWeight:600, fontSize:12, cursor:'pointer'}}>View logs</button>
        </div>
      </div>
    </div>
  );
}

/* ---------- Pipeline view (kanban-ish) ---------- */
function PipelineView({ T }) {
  const [selectedItem, setSelectedItem] = useStateB(null);
  return (
    <div style={{flex:1, padding:'18px 24px 28px', overflow:'auto'}}>
      <SectionHeader T={T} title="Pipeline" subtitle={`${BACKLOG.length} open · ${STATS.backlogDone24h} done in 24h`}/>
      <div style={{display:'grid', gridTemplateColumns:'repeat(6, minmax(160px, 1fr))', gap:9, minWidth:1100}}>
        {PIPELINE_STAGES.map(stage => {
          const items = BACKLOG.filter(b => b.stage === stage);
          return (
            <div key={stage} style={{
              background:T.panel, border:`1px solid ${T.border}`, borderRadius:9, padding:9,
              display:'flex', flexDirection:'column', gap:7, minHeight:280,
            }}>
              <div style={{display:'flex', alignItems:'center', justifyContent:'space-between', padding:'2px 4px 6px'}}>
                <span style={{fontSize:11, fontWeight:700, color:T.text, textTransform:'capitalize'}}>{stage}</span>
                <span style={{fontSize:10.5, color:T.mute, fontVariantNumeric:'tabular-nums'}}>{items.length}</span>
              </div>
              {items.map(b => {
                const sevColor = { high:'#ef4444', medium:'#f59e0b', low:'#10b981' }[b.sev];
                return (
                  <div key={b.id} onClick={()=> setSelectedItem(b)} style={{
                    background:T.panel2, border:`1px solid ${T.border}`, borderRadius:7, padding:'8px 9px',
                    cursor:'pointer', borderLeft:`3px solid ${sevColor}`,
                  }}
                  onMouseEnter={e=> e.currentTarget.style.borderColor = T.accentBorder}
                  onMouseLeave={e=> e.currentTarget.style.borderColor = T.border}>
                    <code style={{fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:10, color:T.mute, fontWeight:600}}>{b.id}</code>
                    <div style={{fontSize:11.5, color:T.text, marginTop:3, lineHeight:1.35}}>{b.title}</div>
                    <div style={{display:'flex', alignItems:'center', gap:5, marginTop:5, fontSize:10, color:T.mute}}>
                      <span>{b.area}</span>
                      <span style={{marginLeft:'auto'}}>{b.age}</span>
                    </div>
                  </div>
                );
              })}
              {items.length === 0 && (
                <div style={{padding:'14px 8px', textAlign:'center', color:T.faint, fontSize:10.5, border:`1px dashed ${T.border}`, borderRadius:6}}>empty</div>
              )}
            </div>
          );
        })}
      </div>
      {selectedItem && (
        <div style={{
          position:'absolute', inset:0, background:'rgba(0,0,0,.4)',
          display:'flex', alignItems:'center', justifyContent:'center', zIndex:25, padding:30,
        }} onClick={()=> setSelectedItem(null)}>
          <div onClick={e=> e.stopPropagation()} style={{
            width:'100%', maxWidth:520, background:T.panel, borderRadius:12, padding:22,
            border:`1px solid ${T.border}`, boxShadow:'0 22px 60px rgba(0,0,0,.4)',
            animation:'slideUp .24s cubic-bezier(.2,.7,.3,1)',
          }}>
            <div style={{display:'flex', alignItems:'center', gap:8, marginBottom:10}}>
              <code style={{fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:11.5, fontWeight:700, color:T.text}}>{selectedItem.id}</code>
              <span style={{fontSize:10, padding:'2px 7px', borderRadius:4, fontWeight:700, textTransform:'uppercase', letterSpacing:.05,
                background: {high:'rgba(239,68,68,.16)',medium:'rgba(245,158,11,.16)',low:'rgba(16,185,129,.16)'}[selectedItem.sev],
                color: {high:'#ef4444',medium:'#f59e0b',low:'#10b981'}[selectedItem.sev],
              }}>{selectedItem.sev}</span>
              <span style={{fontSize:11, color:T.mute, padding:'2px 7px', borderRadius:4, background:T.panel2, border:`1px solid ${T.border}`}}>{selectedItem.stage}</span>
              <span style={{flex:1}}/>
              <span onClick={()=> setSelectedItem(null)} style={{cursor:'pointer', color:T.mute, padding:'4px 8px'}}>✕</span>
            </div>
            <div style={{fontSize:14, fontWeight:600, color:T.text, lineHeight:1.4, marginBottom:14}}>{selectedItem.title}</div>
            <div style={{display:'grid', gridTemplateColumns:'110px 1fr', gap:'5px 14px', fontSize:12, marginBottom:14}}>
              <div style={{color:T.mute}}>Area</div><div>{selectedItem.area}</div>
              <div style={{color:T.mute}}>Owner</div><div><code style={{fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:11}}>{selectedItem.owner}</code></div>
              <div style={{color:T.mute}}>File(s)</div><div><code style={{fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:11}}>{selectedItem.files}</code></div>
              <div style={{color:T.mute}}>Age</div><div>{selectedItem.age}</div>
            </div>
            <div style={{display:'flex', gap:7, flexWrap:'wrap'}}>
              <button style={{padding:'7px 14px', borderRadius:7, border:`1px solid ${T.accent}`, background:T.accent, color:'#fff', fontWeight:600, fontSize:12, cursor:'pointer'}}>Send to dev</button>
              <button style={{padding:'7px 14px', borderRadius:7, border:`1px solid ${T.border}`, background:T.panel, color:T.text, fontWeight:600, fontSize:12, cursor:'pointer'}}>Move stage</button>
              <button style={{padding:'7px 14px', borderRadius:7, border:`1px solid ${T.border}`, background:T.panel, color:T.text, fontWeight:600, fontSize:12, cursor:'pointer'}}>Mark done</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* ---------- Outputs view (Direction B) ---------- */
// Direction B's outputs view lives in the sidebar as a peer of Inbox.
// Same three-pane feel as the inbox: rail of review states, list of
// artifacts, and a click opens a modal sheet with actions.
function OutputsViewB({ T, onSelectOutput }) {
  const [reviewFilter, setReviewFilter] = useStateB('pending');
  const [groupFilter, setGroupFilter]   = useStateB('all');
  const groups = ['all', ...Array.from(new Set(OUTPUTS.map(o => o.group)))];
  const counts = OUTPUTS.reduce((acc,o)=>{ acc[o.review] = (acc[o.review]||0)+1; return acc; }, {});

  const list = OUTPUTS.filter(o => {
    if (reviewFilter !== 'all' && o.review !== reviewFilter) return false;
    if (groupFilter !== 'all' && o.group !== groupFilter) return false;
    return true;
  });

  const states = [
    { id:'all',      label:'Everything', count:OUTPUTS.length,        tint:T.sub },
    { id:'pending',  label:'Pending',    count:counts.pending  || 0,  tint:'#f59e0b' },
    { id:'flagged',  label:'Flagged',    count:counts.flagged  || 0,  tint:'#ef4444' },
    { id:'approved', label:'Approved',   count:counts.approved || 0,  tint:'#10b981' },
    { id:'standing', label:'Standing',   count:counts.standing || 0,  tint:T.sub },
  ];

  return (
    <>
      {/* Rail */}
      <div style={{
        width:160, background:T.headerBg, borderRight:`1px solid ${T.border}`,
        padding:'14px 10px', display:'flex', flexDirection:'column', gap:1, flexShrink:0,
      }}>
        <div style={{padding:'2px 8px 6px', fontSize:10.5, fontWeight:700, color:T.mute, textTransform:'uppercase', letterSpacing:.06}}>Review</div>
        {states.map(s => {
          const active = reviewFilter === s.id;
          return (
            <div key={s.id} onClick={()=> setReviewFilter(s.id)} style={{
              display:'flex', alignItems:'center', gap:7, padding:'6px 10px', borderRadius:6,
              background: active ? T.selectedBg : 'transparent',
              color: active ? T.accent : T.sub,
              fontWeight: active ? 600 : 500, fontSize:12, cursor:'pointer',
            }}>
              <span style={{width:6, height:6, borderRadius:'50%', background:s.tint, flexShrink:0}}/>
              <span style={{flex:1, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap'}}>{s.label}</span>
              <span style={{fontSize:10.5, color: active ? T.accent : T.mute, fontVariantNumeric:'tabular-nums'}}>{s.count}</span>
            </div>
          );
        })}
        <div style={{padding:'14px 8px 6px', fontSize:10.5, fontWeight:700, color:T.mute, textTransform:'uppercase', letterSpacing:.06}}>Group</div>
        {groups.map(g => {
          const active = groupFilter === g;
          return (
            <div key={g} onClick={()=> setGroupFilter(g)} style={{
              display:'flex', alignItems:'center', gap:7, padding:'6px 10px', borderRadius:6,
              background: active ? T.selectedBg : 'transparent',
              color: active ? T.accent : T.sub,
              fontWeight: active ? 600 : 500, fontSize:12, cursor:'pointer',
              textTransform: g === 'all' ? 'none' : 'capitalize',
            }}>
              <span style={{flex:1, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap'}}>{g === 'all' ? 'All groups' : g}</span>
            </div>
          );
        })}
      </div>

      {/* Main panel */}
      <div style={{flex:1, background:T.panel2, minWidth:0, overflow:'auto'}}>
        <div style={{padding:'18px 24px 28px', maxWidth:920, margin:'0 auto'}}>
          <SectionHeader T={T}
            title={reviewFilter === 'all' ? 'All outputs' : reviewFilter.charAt(0).toUpperCase()+reviewFilter.slice(1)}
            subtitle={`${list.length} artifact${list.length===1?'':'s'} · agent-authored`}/>
          {/* KPI strip */}
          <div style={{display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap:10, marginBottom:14}}>
            <OutputKpiB T={T} label="Pending"  value={counts.pending  || 0} color="#f59e0b"/>
            <OutputKpiB T={T} label="Flagged"  value={counts.flagged  || 0} color="#ef4444"/>
            <OutputKpiB T={T} label="Approved" value={counts.approved || 0} color="#10b981"/>
            <OutputKpiB T={T} label="Standing" value={counts.standing || 0} color={T.sub}/>
          </div>

          {list.length === 0 ? (
            <div style={{padding:'48px 24px', textAlign:'center', color:T.sub, background:T.panel, border:`1px solid ${T.border}`, borderRadius:10}}>
              <div style={{fontSize:30, color:'#10b981', marginBottom:8}}>✓</div>
              <div style={{fontWeight:600, color:T.text, marginBottom:3}}>Nothing in this view</div>
              <div style={{fontSize:11.5}}>Try a different filter on the left.</div>
            </div>
          ) : (
            <div style={{display:'flex', flexDirection:'column', gap:14}}>
              {Array.from(new Set(list.map(o => o.group))).map(g => {
                const items = list.filter(o => o.group === g);
                return (
                  <div key={g}>
                    <div style={{fontSize:10.5, fontWeight:700, color:T.mute, textTransform:'uppercase', letterSpacing:.06, marginBottom:7, padding:'0 2px'}}>{g} · {items.length}</div>
                    <div style={{background:T.panel, border:`1px solid ${T.border}`, borderRadius:9, overflow:'hidden'}}>
                      {items.map((o, i) => (
                        <OutputRowB key={o.path} T={T} o={o} last={i === items.length-1}
                          onClick={()=> onSelectOutput(o)}/>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </>
  );
}

function OutputKpiB({ T, label, value, color }) {
  return (
    <div style={{
      background:T.panel, border:`1px solid ${T.border}`, borderRadius:9, padding:'10px 12px',
      display:'flex', alignItems:'center', gap:10, boxShadow:T.shadow,
    }}>
      <span style={{width:8, height:8, borderRadius:'50%', background:color, flexShrink:0}}/>
      <div style={{flex:1, minWidth:0}}>
        <div style={{fontSize:10.5, color:T.sub, fontWeight:600, textTransform:'uppercase', letterSpacing:.05}}>{label}</div>
        <div style={{fontSize:20, fontWeight:700, color:T.text, fontVariantNumeric:'tabular-nums', letterSpacing:-0.3, marginTop:1}}>{value}</div>
      </div>
    </div>
  );
}

function OutputRowB({ T, o, last, onClick }) {
  const reviewColor = { pending:'#f59e0b', flagged:'#ef4444', approved:'#10b981', standing:T.sub }[o.review] || T.sub;
  return (
    <div onClick={onClick} style={{
      display:'flex', alignItems:'center', gap:10, padding:'10px 13px',
      borderBottom: last ? 'none' : `1px solid ${T.border}`,
      cursor:'pointer', background:'transparent',
    }}
    onMouseEnter={e=> e.currentTarget.style.background = T.panelHover}
    onMouseLeave={e=> e.currentTarget.style.background = 'transparent'}>
      <span style={{
        fontSize:9.5, fontWeight:700, padding:'2px 7px', borderRadius:4,
        background: reviewColor+'1f', color: reviewColor, textTransform:'uppercase', letterSpacing:.05,
        flexShrink:0, minWidth:64, textAlign:'center',
      }}>{o.review}</span>
      <code style={{
        fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:11.5, color:T.text,
        flex:1, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap',
      }} title={o.path}>{o.path}</code>
      <span style={{fontSize:11, color:T.sub, whiteSpace:'nowrap'}}>{o.agent}</span>
      <span style={{fontSize:10.5, color:T.faint, whiteSpace:'nowrap', minWidth:50, textAlign:'right'}}>{o.age}</span>
    </div>
  );
}

function OutputSheet({ T, o, onClose, liveMode, executeAction }) {
  const reviewColor = { pending:'#f59e0b', flagged:'#ef4444', approved:'#10b981', standing:T.sub }[o.review] || T.sub;
  const actions = o.review === 'standing' ? [
    { verb:'Open file', prompt:`Show me ${o.path}.`, api:{type:'open',path:o.path}, primary:true },
  ] : [
    { verb:'Open file', prompt:`Show me ${o.path}.`, api:{type:'open',path:o.path}, primary:true },
    { verb:'Approve',   prompt:`Approve ${o.path} and log the verdict.`, api:{type:'output-approve',path:o.path}, color:'green' },
    { verb:'Revise',    prompt:`Rewrite ${o.path} with these changes: `, api:null },
    { verb:'Reject',    prompt:`Reject ${o.path} \u2014 delete it and log a Rejected row.`, api:{type:'output-reject',path:o.path}, color:'red' },
  ];
  const [expandedAction, setExpandedAction] = useStateB(null);
  return (
    <div style={{
      position:'absolute', inset:0, background:'rgba(0,0,0,.4)',
      display:'flex', alignItems:'center', justifyContent:'center', zIndex:25, padding:30,
      animation:'fadeIn .14s ease-out',
    }} onClick={onClose}>
      <div onClick={e=> e.stopPropagation()} style={{
        width:'100%', maxWidth:560, background:T.panel, borderRadius:12, padding:20,
        boxShadow:'0 22px 60px rgba(0,0,0,.4)', border:`1px solid ${T.border}`,
        animation:'slideUp .24s cubic-bezier(.2,.7,.3,1)',
      }}>
        <div style={{display:'flex', alignItems:'center', gap:8, marginBottom:14}}>
          <span style={{
            fontSize:10, padding:'2px 8px', borderRadius:4, fontWeight:700, textTransform:'uppercase', letterSpacing:.05,
            background: reviewColor+'1f', color: reviewColor,
          }}>{o.review}</span>
          <span style={{fontSize:11.5, color:T.sub}}>{o.group}</span>
          <span style={{flex:1}}/>
          <span onClick={onClose} style={{cursor:'pointer', color:T.mute, padding:'4px 8px', borderRadius:5}}>✕</span>
        </div>
        <div style={{
          padding:'10px 12px', background:T.panel2, border:`1px solid ${T.border}`, borderRadius:8, marginBottom:12,
        }}>
          <code style={{fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:12, color:T.text, wordBreak:'break-all'}}>{o.path}</code>
        </div>
        <div style={{display:'grid', gridTemplateColumns:'90px 1fr', gap:'5px 14px', fontSize:12, marginBottom:14}}>
          <div style={{color:T.mute}}>Author</div><div><code style={{fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:11}}>{o.agent}</code></div>
          <div style={{color:T.mute}}>Via</div><div>{o.via}</div>
          <div style={{color:T.mute}}>Age</div><div>{o.age}</div>
        </div>
        <div style={{
          padding:'8px 11px', borderRadius:7, fontSize:11, lineHeight:1.5, marginBottom:12,
          background: liveMode ? 'rgba(16,185,129,.07)' : T.panel2,
          border:`1px solid ${liveMode ? 'rgba(16,185,129,.25)' : T.border}`,
          color: liveMode ? '#10b981' : T.sub,
        }}>
          {liveMode
            ? <><b>One-click mode</b> — buttons POST to <code style={{fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:10.5}}>/api/action</code>.</>
            : <><b>Command console</b> — buttons copy a Claude prompt; toggle the topbar pill on for one-click.</>}
        </div>
        <div style={{display:'flex', flexDirection:'column', gap:7}}>
          {actions.map((a, i) => (
            <ActionRowB key={i} T={T} action={a} liveMode={liveMode}
              expanded={expandedAction === i}
              onToggle={()=> setExpandedAction(expandedAction === i ? null : i)}
              onExecute={()=> executeAction({ prompt:a.prompt, api:a.api, label:a.verb, itemId:null, dismissOnRun:false })}/>
          ))}
        </div>
      </div>
    </div>
  );
}

window.InboxApp = InboxApp;
