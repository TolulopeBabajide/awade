// Direction C — "Hybrid" — the redesign per agentic-dashboard-redesign-spec.md
// Direction B's three-pane Inbox shell + Direction A's department org chart,
// shipped as one app with all P0 (and the easier P1) fixes from the gap review.

const {
  useState: useStateC, useEffect: useEffectC, useMemo: useMemoC,
  useRef: useRefC, useCallback: useCallbackC,
} = React;

/* ──────────────────────────────────────────────────────────────────────
   Helpers & tokens
   ────────────────────────────────────────────────────────────────────── */
const STATUS_C = {
  healthy:    '#10b981',
  warning:    '#f59e0b',
  critical:   '#ef4444',
  idle:       '#a1a1aa',
  'on-demand':'#60a5fa',
};
// Render variants (R-P1.5, R-P1.6) — visual treatment override.
const RENDER_STYLE = {
  'scheduled-monthly':{ ring:'#7c7cb7', dot:'#a1a1aa', label:'monthly' },   // distinct from grey idle
  'standby':          { ring:'#10b981', dot:'#10b981', label:'standby' },   // never ran = healthy
  'unused':           { ring:'#a1a1aa', dot:'#a1a1aa', label:'on-demand' },
};
const URGENCY_C = { high:'#ef4444', medium:'#f59e0b', low:'#10b981' };
const KIND_GLYPH_C = { approve:'✓', decide:'?', review:'◔', respond:'↩' };

/* ──────────────────────────────────────────────────────────────────────
   Persistence (R9)
   ────────────────────────────────────────────────────────────────────── */
function useLS(key, initial) {
  const [v, setV] = useStateC(() => {
    try {
      const s = localStorage.getItem(key);
      return s != null ? JSON.parse(s) : initial;
    } catch { return initial; }
  });
  useEffectC(() => {
    try { localStorage.setItem(key, JSON.stringify(v)); } catch {}
  }, [key, v]);
  return [v, setV];
}

/* ──────────────────────────────────────────────────────────────────────
   Markdown renderer (R2, R4) — small but covers what the agents write:
   #/##/### headings, paragraphs, - bullets, ``` code blocks, > blockquotes,
   **bold** + `code` inline, and | tables (rendered as <pre>).
   ────────────────────────────────────────────────────────────────────── */
function renderInlineC(text, T) {
  const parts = []; let last = 0; let key = 0;
  const re = /(\*\*[^*]+\*\*|`[^`]+`)/g;
  let m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) parts.push(text.slice(last, m.index));
    if (m[0].startsWith('**')) {
      parts.push(<strong key={key++} style={{color:T.text, fontWeight:600}}>{m[0].slice(2,-2)}</strong>);
    } else {
      parts.push(<code key={key++} style={{
        fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:'92%',
        background:T.panel2, color:T.text, padding:'1px 5px', borderRadius:3,
        border:`1px solid ${T.border}`,
      }}>{m[0].slice(1,-1)}</code>);
    }
    last = m.index + m[0].length;
  }
  if (last < text.length) parts.push(text.slice(last));
  return parts;
}

function MarkdownC({ text, T }) {
  if (!text) return <div style={{color:T.mute, fontSize:12, fontStyle:'italic'}}>(no content)</div>;
  const lines = text.split('\n');
  const out = [];
  let inCode = false, codeLines = [], codeLang = '';
  let listItems = [];
  let tableLines = [];

  const flushList = () => {
    if (listItems.length) {
      out.push(
        <ul key={'l'+out.length} style={{margin:'4px 0 10px', paddingLeft:18, listStyle:'disc'}}>
          {listItems.map((li, i) => (
            <li key={i} style={{color:T.text, fontSize:13, lineHeight:1.55, marginBottom:3}}>
              {renderInlineC(li, T)}
            </li>
          ))}
        </ul>
      );
      listItems = [];
    }
  };
  const flushTable = () => {
    if (tableLines.length) {
      out.push(
        <pre key={'t'+out.length} style={{
          margin:'4px 0 12px', padding:'10px 12px', background:T.panel2,
          border:`1px solid ${T.border}`, borderRadius:7, fontSize:11.5,
          fontFamily:'"SF Mono",ui-monospace,monospace', color:T.text,
          overflow:'auto', lineHeight:1.5,
        }}>{tableLines.join('\n')}</pre>
      );
      tableLines = [];
    }
  };

  lines.forEach((raw, i) => {
    const line = raw;
    // fenced code
    if (line.startsWith('```')) {
      flushList(); flushTable();
      if (inCode) {
        out.push(
          <pre key={'c'+i} style={{
            margin:'4px 0 12px', padding:'10px 12px',
            background:T.bg, border:`1px solid ${T.border}`, borderRadius:7,
            fontSize:11.5, fontFamily:'"SF Mono",ui-monospace,monospace',
            color:T.text, overflow:'auto', lineHeight:1.55,
          }}>{codeLines.join('\n')}</pre>
        );
        codeLines = []; codeLang = ''; inCode = false;
      } else {
        codeLang = line.slice(3).trim(); inCode = true;
      }
      return;
    }
    if (inCode) { codeLines.push(line); return; }

    // tables — collect contiguous |-lines, render as pre
    if (line.trim().startsWith('|')) { flushList(); tableLines.push(line); return; }
    if (tableLines.length) flushTable();

    if (line.startsWith('# ')) {
      flushList();
      out.push(<h2 key={i} style={{fontSize:18, fontWeight:700, color:T.text, letterSpacing:-0.3, margin:'18px 0 6px'}}>{renderInlineC(line.slice(2), T)}</h2>);
    } else if (line.startsWith('## ')) {
      flushList();
      out.push(<h3 key={i} style={{fontSize:15, fontWeight:700, color:T.text, margin:'18px 0 6px', letterSpacing:-0.2}}>{renderInlineC(line.slice(3), T)}</h3>);
    } else if (line.startsWith('### ')) {
      flushList();
      out.push(<h4 key={i} style={{fontSize:12.5, fontWeight:700, color:T.text, textTransform:'uppercase', letterSpacing:.04, margin:'14px 0 5px'}}>{renderInlineC(line.slice(4), T)}</h4>);
    } else if (line.startsWith('---')) {
      flushList();
      out.push(<hr key={i} style={{border:'none', borderTop:`1px solid ${T.border}`, margin:'14px 0'}}/>);
    } else if (line.startsWith('> ')) {
      flushList();
      out.push(<blockquote key={i} style={{
        margin:'8px 0', padding:'8px 12px', borderLeft:`3px solid ${T.accent}`,
        background:T.accentSoft, color:T.text, fontSize:12.5, lineHeight:1.5, borderRadius:'0 6px 6px 0',
      }}>{renderInlineC(line.slice(2), T)}</blockquote>);
    } else if (line.startsWith('- ') || line.startsWith('* ')) {
      listItems.push(line.slice(2));
    } else if (line.trim() === '') {
      flushList();
    } else {
      flushList();
      out.push(<p key={i} style={{margin:'0 0 8px', color:T.text, fontSize:13, lineHeight:1.6}}>{renderInlineC(line, T)}</p>);
    }
  });
  flushList(); flushTable();
  if (inCode && codeLines.length) {
    out.push(<pre key="c-final" style={{padding:'10px 12px', background:T.bg, border:`1px solid ${T.border}`, borderRadius:7, fontSize:11.5, fontFamily:'"SF Mono",ui-monospace,monospace', color:T.text}}>{codeLines.join('\n')}</pre>);
  }
  return <div>{out}</div>;
}

/* ──────────────────────────────────────────────────────────────────────
   Theme tokens
   ────────────────────────────────────────────────────────────────────── */
function tokensC(theme) {
  return theme === 'dark' ? {
    bg:'#0a0b0e', appShell:'#0f1015', panel:'#15171c', panel2:'#1a1d24', panelHover:'#1d2028',
    border:'#23252e', borderStrong:'#33363f',
    text:'#ededee', sub:'#a3a4ad', mute:'#74757d', faint:'#52535b',
    accent:'#818cf8', accentSoft:'rgba(129,140,248,.14)', accentBorder:'rgba(129,140,248,.5)',
    selectedBg:'rgba(129,140,248,.14)',
    shadow:'0 1px 2px rgba(0,0,0,.4), 0 8px 24px rgba(0,0,0,.32)',
    shadowSm:'0 1px 2px rgba(0,0,0,.3)',
    headerBg:'#0d0e13',
  } : {
    bg:'#fbfbfc', appShell:'#f1f1f4', panel:'#ffffff', panel2:'#f7f7fa', panelHover:'#f1f1f5',
    border:'#e8e8ec', borderStrong:'#d5d5dc',
    text:'#15161a', sub:'#54555c', mute:'#7d7e85', faint:'#a8a9b0',
    accent:'#5b5bf0', accentSoft:'rgba(91,91,240,.07)', accentBorder:'rgba(91,91,240,.4)',
    selectedBg:'rgba(91,91,240,.08)',
    shadow:'0 1px 2px rgba(20,20,30,.04), 0 8px 22px rgba(20,20,30,.06)',
    shadowSm:'0 1px 2px rgba(20,20,30,.05)',
    headerBg:'#fafafb',
  };
}

/* ──────────────────────────────────────────────────────────────────────
   Top-level
   ────────────────────────────────────────────────────────────────────── */
function HybridApp({ theme, liveMode, setLiveMode }) {
  const T = tokensC(theme);

  // Persisted UI state (R9)
  const [view, setView] = useLS('hybrid:view', 'inbox');
  const [dismissedArr, setDismissedArr] = useLS('hybrid:dismissed', []);
  const dismissed = useMemoC(() => new Set(dismissedArr), [dismissedArr]);
  const setDismissed = (next) => setDismissedArr(Array.from(next));
  const [resolved, setResolved] = useLS('hybrid:resolved', {});

  // Session state
  const [filter, setFilter] = useStateC('all');
  const [selectedId, setSelectedId] = useStateC(INBOX[0]?.id);
  const [search, setSearch] = useStateC('');
  const [toast, setToast] = useStateC(null);
  const [events] = useStateC(EVENTS);
  const [runningAgent, setRunningAgent] = useStateC(null);
  const [selectedAgent, setSelectedAgent] = useStateC(null);
  const [selectedBacklog, setSelectedBacklog] = useStateC(null);
  const [outputSelectedPath, setOutputSelectedPath] = useStateC(OUTPUTS[0]?.path);
  const [agentFilter, setAgentFilter] = useStateC('all');
  const [agentQuery, setAgentQuery] = useStateC('');

  function showToast(msg){ setToast(msg); setTimeout(()=> setToast(null), 1800); }
  function copyText(t){
    try {
      if (navigator.clipboard?.writeText) navigator.clipboard.writeText(t);
      else {
        const ta = document.createElement('textarea');
        ta.value = t; document.body.appendChild(ta); ta.select();
        try { document.execCommand('copy'); } catch(_) {}
        document.body.removeChild(ta);
      }
    } catch(_) {}
  }
  // R3 — note appended to the prompt for open-ended actions
  function executeAction({ prompt, api, note, label, itemId, dismissOnRun }){
    const fullPrompt = note ? `${prompt}${note}` : prompt;
    if (!liveMode) {
      copyText(fullPrompt);
      showToast('⎘ Prompt copied — paste into Claude');
      return;
    }
    showToast(`Running … ${label || api?.type || ''}`);
    setTimeout(() => {
      if (itemId && dismissOnRun) {
        const next = new Set(dismissed); next.add(itemId); setDismissed(next);
        setResolved({ ...resolved, [itemId]: label });
      }
      showToast(`✓ ${label || 'Done'}`);
    }, 700);
  }
  function dismissItem(id){
    const next = new Set(dismissed); next.add(id); setDismissed(next);
    if (selectedId === id) {
      const nextItem = visibleDecisions.find(d => d.id !== id);
      if (nextItem) setSelectedId(nextItem.id);
    }
  }
  function undismissAll(){ setDismissed(new Set()); setResolved({}); }
  function runAgent(name){
    setRunningAgent(name); showToast(`Running ${name}…`);
    setTimeout(() => { setRunningAgent(null); showToast(`✓ ${name} ran`); }, 1100);
  }

  // Visibility / search
  const visibleDecisions = useMemoC(() => {
    let xs = INBOX.filter(d => !dismissed.has(d.id));
    if (filter === 'urgent')  xs = xs.filter(d => d.urgency === 'high');
    if (filter === 'approve') xs = xs.filter(d => d.kind === 'approve');
    if (filter === 'decide')  xs = xs.filter(d => d.kind === 'decide');
    if (filter === 'review')  xs = xs.filter(d => d.kind === 'review');
    if (filter === 'respond') xs = xs.filter(d => d.kind === 'respond');
    if (search) {
      const q = search.toLowerCase();
      xs = xs.filter(d => (d.title + ' ' + d.from + ' ' + d.detail + ' ' + d.originPath).toLowerCase().includes(q));
    }
    return xs;
  }, [dismissed, filter, search]);

  // Keep selected valid
  useEffectC(() => {
    if (!visibleDecisions.find(d => d.id === selectedId)) {
      setSelectedId(visibleDecisions[0]?.id);
    }
  }, [visibleDecisions, selectedId]);

  const selected = INBOX.find(d => d.id === selectedId);

  // R-P1.8 — keyboard triage. j/k navigate; ↵ primary action; gi/go/gp/gr inbox/outputs/pulse/roster.
  useEffectC(() => {
    const onKey = (e) => {
      if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA')) return;
      if (e.key === 'j') {
        if (view !== 'inbox') return;
        const idx = visibleDecisions.findIndex(d => d.id === selectedId);
        const next = visibleDecisions[Math.min(visibleDecisions.length - 1, idx + 1)];
        if (next) setSelectedId(next.id);
      } else if (e.key === 'k') {
        if (view !== 'inbox') return;
        const idx = visibleDecisions.findIndex(d => d.id === selectedId);
        const prev = visibleDecisions[Math.max(0, idx - 1)];
        if (prev) setSelectedId(prev.id);
      } else if (e.key === 'Enter' && selected && view === 'inbox') {
        const primary = (selected.actions || []).find(a => a.primary) || selected.actions?.[0];
        if (primary) executeAction({
          prompt:primary.prompt, api:primary.api, label:primary.verb,
          itemId:selected.id, dismissOnRun: primary.color !== undefined,
        });
      } else if (e.key === 'Escape') {
        if (selectedAgent) setSelectedAgent(null);
        else if (selectedBacklog) setSelectedBacklog(null);
      } else if (e.key === 'e' && selected && view === 'inbox') {
        dismissItem(selected.id);
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [view, visibleDecisions, selectedId, selected, selectedAgent, selectedBacklog, dismissed, liveMode]);

  // R8 — Critical bucket counts. Always surfaced even when 0.
  const statusCounts = useMemoC(() => {
    const c = { healthy:0, warning:0, critical:0, idle:0, 'on-demand':0 };
    AGENTS.forEach(a => { c[a.status] = (c[a.status] || 0) + 1; });
    return c;
  }, []);
  const outputsBadge = OUTPUTS.filter(o => o.review === 'pending' || o.review === 'flagged').length;
  const failures24h = useMemoC(() => events.filter(e => e.status === 'fail'), [events]);

  return (
    <div style={{
      width:'100%', height:'100%', background:T.appShell, color:T.text,
      fontFamily:'-apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", system-ui, sans-serif',
      fontSize:13, lineHeight:1.45, display:'flex', overflow:'hidden',
    }}>
      <SidebarC T={T} view={view} setView={setView}
        pendingCount={visibleDecisions.length}
        outputsBadge={outputsBadge}
        failuresCount={failures24h.length}
        critical={statusCounts.critical}
        warning={statusCounts.warning}/>

      <div style={{flex:1, display:'flex', flexDirection:'column', minWidth:0}}>
        <TopBarC T={T} view={view} search={search} setSearch={setSearch} liveMode={liveMode} setLiveMode={setLiveMode}/>
        <div style={{flex:1, display:'flex', minHeight:0, position:'relative'}}>
          {view === 'inbox' && (
            <InboxViewC T={T} decisions={visibleDecisions} filter={filter} setFilter={setFilter}
              selectedId={selectedId} setSelectedId={setSelectedId}
              selected={selected} liveMode={liveMode}
              executeAction={executeAction}
              onDismiss={dismissItem}
              onUndismissAll={undismissAll}
              resolved={resolved}
              statusCounts={statusCounts}
              search={search}/>
          )}
          {view === 'outputs' && (
            <OutputsViewC T={T} liveMode={liveMode} executeAction={executeAction}
              selectedPath={outputSelectedPath} setSelectedPath={setOutputSelectedPath}
              search={search}/>
          )}
          {view === 'pulse' && (
            <PulseViewC T={T} events={events} failures={failures24h}/>
          )}
          {view === 'roster' && (
            <RosterViewC T={T} statusCounts={statusCounts}
              agentFilter={agentFilter} setAgentFilter={setAgentFilter}
              agentQuery={agentQuery} setAgentQuery={setAgentQuery}
              onSelectAgent={setSelectedAgent} runAgent={runAgent} runningAgent={runningAgent}
              search={search}/>
          )}
          {view === 'pipeline' && (
            <PipelineViewC T={T} onSelectBacklog={setSelectedBacklog} search={search}/>
          )}
        </div>
      </div>

      {selectedAgent && (
        <AgentPanel T={T} agent={selectedAgent} onClose={() => setSelectedAgent(null)}
          runAgent={runAgent} runningAgent={runningAgent} events={events}/>
      )}
      {selectedBacklog && (
        <BacklogPanel T={T} item={selectedBacklog} onClose={() => setSelectedBacklog(null)}/>
      )}
      {toast && (
        <div style={{
          position:'absolute', bottom:18, left:'50%', transform:'translateX(-50%)',
          background:T.text, color:T.bg, padding:'8px 16px', borderRadius:8,
          fontSize:12, fontWeight:600, boxShadow:'0 10px 28px rgba(0,0,0,.3)', zIndex:40,
          animation:'fadeIn .18s ease-out',
        }}>{toast}</div>
      )}
    </div>
  );
}

/* ──────────────────────────────────────────────────────────────────────
   Sidebar
   ────────────────────────────────────────────────────────────────────── */
function SidebarC({ T, view, setView, pendingCount, outputsBadge, failuresCount, critical, warning }) {
  const items = [
    { id:'inbox',    label:'Inbox',    badge:pendingCount,  badgeTone:'accent' },
    { id:'outputs',  label:'Outputs',  badge:outputsBadge,  badgeTone:'neutral' },
    { id:'pulse',    label:'Pulse',    badge:failuresCount, badgeTone: failuresCount > 0 ? 'warn' : 'neutral' },
    { id:'roster',   label:'Roster',   badge: critical > 0 ? critical : (warning > 0 ? warning : null),
                     badgeTone: critical > 0 ? 'crit' : 'warn' },
    { id:'pipeline', label:'Pipeline', badge:null },
  ];
  const iconFor = {
    inbox:    'M3 8l9 6 9-6M3 8v10h18V8M3 8l9-5 9 5',
    outputs:  'M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zM14 2v6h6M9 13h6M9 17h6M9 9h2',
    pulse:    'M3 12h4l3-8 4 16 3-8h4',
    roster:   'M8 11a4 4 0 100-8 4 4 0 000 8zm-7 10a7 7 0 1114 0M16 11a4 4 0 100-8 4 4 0 000 8zm7 10a7 7 0 00-7-7',
    pipeline: 'M3 6h6M3 12h6M3 18h6M15 6h6M15 12h6M15 18h6',
  };
  return (
    <div style={{
      width:200, background:T.headerBg, borderRight:`1px solid ${T.border}`,
      display:'flex', flexDirection:'column', flexShrink:0,
    }}>
      <div style={{padding:'15px 14px 14px', display:'flex', alignItems:'center', gap:9}}>
        <div style={{
          width:26, height:26, borderRadius:7,
          background:`linear-gradient(135deg, ${T.accent}, #8b5cf6)`,
          display:'flex', alignItems:'center', justifyContent:'center',
          color:'#fff', fontWeight:700, fontSize:11,
        }}>AT</div>
        <div>
          <div style={{fontWeight:700, fontSize:12.5, letterSpacing:-0.1}}>Agentic Team</div>
          <div style={{fontSize:10.5, color:T.mute}}>33 agents · {STATS.agentsScheduled} scheduled</div>
        </div>
      </div>
      <div style={{padding:'4px 8px', display:'flex', flexDirection:'column', gap:1}}>
        {items.map(it => {
          const active = view === it.id;
          const tone = it.badge != null && it.badge > 0
            ? (it.badgeTone === 'crit' ? '#ef4444' : it.badgeTone === 'warn' ? '#f59e0b' : it.badgeTone === 'accent' ? T.accent : T.mute)
            : null;
          return (
            <div key={it.id} onClick={() => setView(it.id)} style={{
              display:'flex', alignItems:'center', gap:9, padding:'7px 10px', borderRadius:7,
              background: active ? T.selectedBg : 'transparent',
              color: active ? T.accent : T.sub,
              fontWeight: active ? 600 : 500, fontSize:12.5, cursor:'pointer',
            }}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d={iconFor[it.id]}/>
              </svg>
              <span style={{flex:1}}>{it.label}</span>
              {it.badge != null && it.badge > 0 && (
                <span style={{
                  fontSize:10.5, fontWeight:700, padding:'1px 6px', borderRadius:4,
                  background: tone === T.accent && active ? T.accent : (tone === T.mute ? T.panel2 : tone+'22'),
                  color: (tone === T.accent && active) ? '#fff' : tone,
                  border: tone === T.mute ? `1px solid ${T.border}` : 'none',
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
          <span style={{
            width:6, height:6, borderRadius:'50%',
            background: critical > 0 ? '#ef4444' : '#10b981',
            boxShadow: critical > 0 ? '0 0 0 3px rgba(239,68,68,.18)' : '0 0 0 3px rgba(16,185,129,.2)',
          }}/>
          <span style={{fontWeight:600, color:T.sub}}>
            {critical > 0 ? `${critical} critical` : 'System healthy'}
          </span>
        </div>
        <div>Refreshed 8m ago · hourly</div>
      </div>
    </div>
  );
}

/* ──────────────────────────────────────────────────────────────────────
   Top bar — scoped search per view (R12)
   ────────────────────────────────────────────────────────────────────── */
function TopBarC({ T, view, search, setSearch, liveMode, setLiveMode }) {
  const placeholder = {
    inbox:    'Search inbox… (j/k to navigate, ↵ to take primary action, e to dismiss)',
    outputs:  'Search outputs by path, agent, group…',
    pulse:    'Search activity stream…',
    roster:   'Search agents by name or department…',
    pipeline: 'Search backlog by id, title, area, owner…',
  }[view] || 'Search…';
  return (
    <div style={{
      padding:'10px 16px', background:T.panel, borderBottom:`1px solid ${T.border}`,
      display:'flex', alignItems:'center', gap:12, flexShrink:0,
    }}>
      <div style={{flex:1, maxWidth:560, position:'relative'}}>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={T.mute}
          strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
          style={{position:'absolute', left:11, top:'50%', transform:'translateY(-50%)'}}>
          <circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>
        </svg>
        <input
          placeholder={placeholder}
          value={search} onChange={e => setSearch(e.target.value)}
          style={{
            width:'100%', boxSizing:'border-box',
            padding:'7px 11px 7px 32px', borderRadius:7, fontSize:12.5,
            border:`1px solid ${T.border}`, background:T.panel2, color:T.text, outline:'none',
            fontFamily:'inherit',
          }}/>
      </div>
      <ModeToggleC T={T} liveMode={liveMode} setLiveMode={setLiveMode}/>
      <div style={{
        padding:'4px 10px', borderRadius:6, border:`1px solid ${T.border}`, background:T.panel2,
        fontSize:11, color:T.sub,
      }}>
        <span style={{color:T.mute}}>Runs / 24h </span>
        <span style={{color:T.text, fontWeight:700, fontVariantNumeric:'tabular-nums'}}>{STATS.runs24h}</span>
      </div>
    </div>
  );
}
function ModeToggleC({ T, liveMode, setLiveMode }) {
  return (
    <div onClick={() => setLiveMode(!liveMode)}
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
  );
}

window.HybridApp = HybridApp;
window.useLS = useLS;
window.MarkdownC = MarkdownC;
window.tokensC = tokensC;
window.STATUS_C = STATUS_C;
window.URGENCY_C = URGENCY_C;
window.KIND_GLYPH_C = KIND_GLYPH_C;
window.RENDER_STYLE = RENDER_STYLE;
