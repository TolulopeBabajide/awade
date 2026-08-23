// Direction C — views (Inbox, Outputs, Pulse, Roster, Pipeline + panels)
// Loaded after direction-c.jsx; reads helpers off window.

const { useState: useStV, useEffect: useEfV, useMemo: useMmV, useRef: useRfV } = React;

/* ──────────────────────────────────────────────────────────────────────
   INBOX view (R1, R2, R3, R11)
   ────────────────────────────────────────────────────────────────────── */
function InboxViewC({ T, decisions, filter, setFilter, selectedId, setSelectedId, selected,
                     liveMode, executeAction, onDismiss, onUndismissAll, resolved, statusCounts, search }) {
  return (
    <>
      <InboxRail T={T} filter={filter} setFilter={setFilter} statusCounts={statusCounts}
        dismissedCount={Object.keys(resolved).length} onUndismissAll={onUndismissAll}/>
      <InboxList T={T} decisions={decisions} selectedId={selectedId} setSelectedId={setSelectedId}
        filter={filter} onDismiss={onDismiss} search={search}/>
      <div style={{flex:1, background:T.panel2, minWidth:0, overflow:'auto'}}>
        {selected
          ? <DecisionReaderC T={T} d={selected} liveMode={liveMode} executeAction={executeAction} onDismiss={onDismiss}/>
          : <EmptyState T={T}
              title={search ? 'Nothing matches' : 'Inbox zero'}
              detail={search ? 'No items match your search. Clear the filter to see everything.' : 'You\u2019re all caught up. The agents will surface anything new here.'}/>
        }
      </div>
    </>
  );
}

function InboxRail({ T, filter, setFilter, statusCounts, dismissedCount, onUndismissAll }) {
  const items = [
    { id:'all',     label:'Everything', count:INBOX.length },
    { id:'urgent',  label:'Urgent',     count:INBOX.filter(d=>d.urgency==='high').length,   tint:'#ef4444' },
    { id:'approve', label:'Approvals',  count:INBOX.filter(d=>d.kind==='approve').length },
    { id:'decide',  label:'Decisions',  count:INBOX.filter(d=>d.kind==='decide').length },
    { id:'review',  label:'Reviews',    count:INBOX.filter(d=>d.kind==='review').length },
    { id:'respond', label:'Responses',  count:INBOX.filter(d=>d.kind==='respond').length },
  ];
  return (
    <div style={{
      width:160, background:T.headerBg, borderRight:`1px solid ${T.border}`,
      padding:'14px 10px', display:'flex', flexDirection:'column', gap:1, flexShrink:0,
    }}>
      <div style={{padding:'2px 8px 6px', fontSize:10.5, fontWeight:700, color:T.mute, textTransform:'uppercase', letterSpacing:.06}}>Triage</div>
      {items.map(c => {
        const active = filter === c.id;
        return (
          <div key={c.id} onClick={() => setFilter(c.id)} style={{
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

      <div style={{padding:'14px 8px 6px', fontSize:10.5, fontWeight:700, color:T.mute, textTransform:'uppercase', letterSpacing:.06}}>Fleet</div>
      <StatusRow T={T} tint="#ef4444" label="critical" n={statusCounts.critical}/>
      <StatusRow T={T} tint="#f59e0b" label="warning"  n={statusCounts.warning}/>
      <StatusRow T={T} tint="#10b981" label="healthy"  n={statusCounts.healthy}/>
      <StatusRow T={T} tint={T.mute}  label="idle"     n={statusCounts.idle + statusCounts['on-demand']}/>

      {dismissedCount > 0 && (
        <>
          <div style={{flex:1}}/>
          <div onClick={onUndismissAll} title="Restore all dismissed items" style={{
            padding:'6px 10px', borderRadius:6, fontSize:11, color:T.mute, cursor:'pointer',
            border:`1px dashed ${T.border}`, textAlign:'center', marginTop:8,
          }}>
            ↺ restore {dismissedCount}
          </div>
        </>
      )}
    </div>
  );
}
function StatusRow({ T, tint, label, n }) {
  return (
    <div style={{padding:'5px 10px', fontSize:11.5, color:T.sub, display:'flex', alignItems:'center', gap:6}}>
      <span style={{width:5, height:5, borderRadius:'50%', background:tint, flexShrink:0}}/>
      <span style={{flex:1, textTransform:'capitalize'}}>{label}</span>
      <span style={{fontVariantNumeric:'tabular-nums', color: n > 0 ? T.text : T.faint}}>{n}</span>
    </div>
  );
}

function InboxList({ T, decisions, selectedId, setSelectedId, filter, onDismiss, search }) {
  const titleLabel = filter === 'all'
    ? (search ? 'Results' : 'Inbox')
    : filter.charAt(0).toUpperCase() + filter.slice(1);
  return (
    <div style={{
      width:340, background:T.panel, borderRight:`1px solid ${T.border}`,
      display:'flex', flexDirection:'column', flexShrink:0,
    }}>
      <div style={{padding:'12px 14px 10px', borderBottom:`1px solid ${T.border}`}}>
        <div style={{display:'flex', alignItems:'baseline', justifyContent:'space-between'}}>
          <span style={{fontWeight:700, fontSize:13.5, color:T.text}}>{titleLabel}</span>
          <span style={{fontSize:11, color:T.mute, fontVariantNumeric:'tabular-nums'}}>{decisions.length} pending</span>
        </div>
        <div style={{fontSize:11, color:T.sub, marginTop:2}}>
          {decisions.length === 0
            ? 'Nothing waiting on you.'
            : <span><kbd style={kbdStyle(T)}>j</kbd>/<kbd style={kbdStyle(T)}>k</kbd> nav · <kbd style={kbdStyle(T)}>↵</kbd> act · <kbd style={kbdStyle(T)}>e</kbd> dismiss</span>}
        </div>
      </div>
      <div style={{flex:1, overflow:'auto'}}>
        {decisions.length === 0 ? (
          <div style={{padding:'40px 24px', textAlign:'center', color:T.sub}}>
            <div style={{fontSize:30, color:'#10b981', marginBottom:8}}>✓</div>
            <div style={{fontWeight:600, color:T.text, marginBottom:3}}>Inbox zero</div>
            <div style={{fontSize:11.5}}>The agents are still running. They\u2019ll surface anything new.</div>
          </div>
        ) : decisions.map(d => (
          <InboxRow key={d.id} T={T} d={d}
            selected={selectedId === d.id}
            onSelect={() => setSelectedId(d.id)}
            onDismiss={() => onDismiss(d.id)}/>
        ))}
      </div>
    </div>
  );
}
function kbdStyle(T){ return {
  fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:9.5,
  padding:'1px 5px', borderRadius:3, background:T.panel2, color:T.text,
  border:`1px solid ${T.border}`,
}; }

function InboxRow({ T, d, selected, onSelect, onDismiss }) {
  const [hover, setHover] = useStV(false);
  const tint = URGENCY_C[d.urgency];
  return (
    <div onClick={onSelect} onMouseEnter={()=>setHover(true)} onMouseLeave={()=>setHover(false)} style={{
      padding:'11px 14px 11px 11px', borderBottom:`1px solid ${T.border}`,
      background: selected ? T.selectedBg : hover ? T.panelHover : 'transparent',
      borderLeft:`3px solid ${selected ? T.accent : 'transparent'}`,
      cursor:'pointer', position:'relative',
    }}>
      <div style={{display:'flex', alignItems:'center', gap:7, marginBottom:3}}>
        <span style={{
          width:16, height:16, borderRadius:4, background:tint+'22', color:tint,
          display:'inline-flex', alignItems:'center', justifyContent:'center',
          fontSize:10, fontWeight:700,
        }}>{KIND_GLYPH_C[d.kind]}</span>
        <code style={{fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:10.5, color:T.text, fontWeight:600}}>{d.from}</code>
        <span style={{flex:1}}/>
        <span style={{fontSize:10.5, color:T.faint}}>{d.age}</span>
        {/* R11 — working dismiss control on the card */}
        {hover && (
          <span onClick={(e)=>{ e.stopPropagation(); onDismiss(); }} title="Dismiss (e)"
            style={{
              position:'absolute', right:8, top:8, width:22, height:22, borderRadius:5,
              background:T.panel, border:`1px solid ${T.border}`, color:T.mute,
              display:'inline-flex', alignItems:'center', justifyContent:'center',
              fontSize:12, lineHeight:1, cursor:'pointer',
            }}>✕</span>
        )}
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
}

/* ──────────────────────────────────────────────────────────────────────
   Reading pane (R2 — inline source artifact; R3 — note input; R4 mirror)
   ────────────────────────────────────────────────────────────────────── */
function DecisionReaderC({ T, d, liveMode, executeAction, onDismiss }) {
  const tint = URGENCY_C[d.urgency];
  // R3 — open-ended action picks the note input; "armed" action highlights.
  const [armedIdx, setArmedIdx] = useStV(null);
  const [note, setNote] = useStV('');
  useEfV(() => { setArmedIdx(null); setNote(''); }, [d.id]);

  const openEndedIdx = (d.actions || []).findIndex(a => a.api === null);
  const needsNote = openEndedIdx >= 0;

  return (
    <div style={{padding:'24px 28px 32px', maxWidth:760, margin:'0 auto'}}>
      <div style={{display:'flex', alignItems:'center', gap:8, marginBottom:12}}>
        <span style={{
          fontSize:10, padding:'2px 7px', borderRadius:4, fontWeight:700,
          textTransform:'uppercase', letterSpacing:.05,
          background:tint+'18', color:tint,
        }}>{d.urgency} · {d.kind}</span>
        <span style={{color:T.faint}}>·</span>
        <span style={{fontSize:11, color:T.sub}}>{d.via}</span>
        <span style={{flex:1}}/>
        <span style={{fontSize:11, color:T.mute}}>{d.age} · ~{d.est} read</span>
        <span onClick={() => onDismiss(d.id)} title="Dismiss (e)" style={{
          marginLeft:6, padding:'3px 8px', borderRadius:5,
          background:T.panel, color:T.mute, border:`1px solid ${T.border}`,
          fontSize:11, cursor:'pointer',
        }}>Dismiss</span>
      </div>

      <h1 style={{fontSize:22, fontWeight:700, color:T.text, lineHeight:1.25, marginBottom:8, letterSpacing:-0.4}}>
        {d.title}
      </h1>

      <div style={{display:'flex', alignItems:'center', gap:6, marginBottom:14, fontSize:12, color:T.sub, flexWrap:'wrap'}}>
        <span>Drafted by</span>
        <code style={inlineCode(T)}>{d.from}</code>
        {d.relatedBacklog && <>
          <span style={{color:T.faint}}>·</span>
          <span>filed</span><code style={inlineCode(T)}>{d.relatedBacklog}</code>
        </>}
      </div>

      {/* AGENT summary */}
      <div style={{
        padding:'12px 14px', background:T.panel, border:`1px solid ${T.border}`, borderRadius:8,
        fontSize:12.5, color:T.text, lineHeight:1.55, marginBottom:14,
      }}>{d.detail}</div>

      {/* Impact callout */}
      <div style={{
        padding:'10px 14px', background:tint+'10', border:`1px solid ${tint}33`, borderRadius:8,
        fontSize:12, color:T.text, lineHeight:1.5, marginBottom:18,
        display:'flex', alignItems:'center', gap:8,
      }}>
        <span style={{
          width:18, height:18, borderRadius:4, background:tint+'22', color:tint,
          display:'inline-flex', alignItems:'center', justifyContent:'center',
          flexShrink:0, fontSize:11, fontWeight:700,
        }}>!</span>
        <span><b style={{color:tint}}>Impact:</b> <span style={{color:T.sub}}>{d.impact}</span></span>
      </div>

      {/* R2 — source artifact rendered inline */}
      {d.originPath && (
        <div style={{
          background:T.panel, border:`1px solid ${T.border}`, borderRadius:9,
          marginBottom:18, overflow:'hidden',
        }}>
          <div style={{
            padding:'8px 12px', borderBottom:`1px solid ${T.border}`,
            background:T.panel2, display:'flex', alignItems:'center', gap:8,
          }}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke={T.mute}
              strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z"/>
              <path d="M14 2v6h6"/>
            </svg>
            <code style={{fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:11, color:T.text, flex:1, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap'}}>
              {d.originPath}
            </code>
            <span style={{fontSize:10, color:T.mute, fontWeight:600, textTransform:'uppercase', letterSpacing:.05}}>source</span>
          </div>
          <div style={{padding:'14px 18px', maxHeight:420, overflow:'auto'}}>
            <MarkdownC text={SOURCE_CONTENT[d.originPath]} T={T}/>
          </div>
        </div>
      )}

      {/* Mode hint */}
      <div style={{
        padding:'8px 11px', borderRadius:7, fontSize:11, lineHeight:1.5, marginBottom:12,
        background: liveMode ? 'rgba(16,185,129,.07)' : T.panel,
        border:`1px solid ${liveMode ? 'rgba(16,185,129,.25)' : T.border}`,
        color: liveMode ? '#10b981' : T.sub,
      }}>
        {liveMode
          ? <><b>One-click mode</b> — buttons POST to <code style={inlineCode(T)}>/api/action</code>.</>
          : <><b>Command console</b> — buttons copy a Claude prompt to paste.</>}
      </div>

      {/* Actions */}
      <div style={{display:'flex', flexDirection:'column', gap:7, marginBottom: needsNote ? 12 : 0}}>
        {(d.actions || []).map((a, i) => {
          const isOpenEnded = a.api === null;
          const isArmed = armedIdx === i;
          return (
            <ActionRowC key={i} T={T} action={a} liveMode={liveMode}
              isOpenEnded={isOpenEnded}
              isArmed={isArmed}
              note={note}
              onArm={() => { setArmedIdx(i); setNote(''); }}
              onExecute={() => {
                executeAction({
                  prompt:a.prompt, api:a.api, note: isOpenEnded ? note : '',
                  label:a.verb, itemId:d.id,
                  dismissOnRun: a.color !== undefined,
                });
                if (isOpenEnded) { setArmedIdx(null); setNote(''); }
              }}/>
          );
        })}
      </div>

      {/* R3 — note input shown when an open-ended action is armed */}
      {needsNote && armedIdx !== null && (d.actions[armedIdx]?.api === null) && (
        <NoteInput T={T} value={note} setValue={setNote}
          label={`Your note for "${d.actions[armedIdx].verb}"`}
          hint={d.actions[armedIdx].prompt}
          onSubmit={() => {
            executeAction({
              prompt:d.actions[armedIdx].prompt, api:null, note,
              label:d.actions[armedIdx].verb, itemId:d.id, dismissOnRun:false,
            });
            setArmedIdx(null); setNote('');
          }}
          onCancel={() => { setArmedIdx(null); setNote(''); }}/>
      )}
    </div>
  );
}
function inlineCode(T){ return {
  fontFamily:'"SF Mono",ui-monospace,monospace', color:T.text, padding:'1px 6px',
  borderRadius:4, background:T.panel, border:`1px solid ${T.border}`, fontSize:11,
}; }

function ActionRowC({ T, action, liveMode, isOpenEnded, isArmed, note, onArm, onExecute }) {
  const [expanded, setExpanded] = useStV(false);
  const color = action.color === 'green' ? '#10b981' : action.color === 'red' ? '#ef4444' : null;
  const isPrimary = action.primary;
  // For open-ended actions: arm first, then execute when note typed.
  const handleClick = () => {
    if (isOpenEnded && !isArmed) { onArm(); return; }
    if (isOpenEnded && isArmed && !note.trim()) { onArm(); return; } // focus the input
    onExecute();
  };
  const buttonLabel = isOpenEnded && isArmed
    ? (note.trim() ? `${action.verb} →` : 'Type your note below')
    : action.verb;
  const buttonDisabled = isOpenEnded && isArmed && !note.trim();
  return (
    <div style={{
      border:`1px solid ${(isArmed || expanded) ? T.accentBorder : T.border}`,
      borderRadius:8, background: (isArmed || expanded) ? T.panel : T.panel2, overflow:'hidden',
    }}>
      <div style={{display:'flex', alignItems:'center', gap:7, padding:'7px 8px 7px 10px'}}>
        <button onClick={handleClick} disabled={buttonDisabled} style={{
          flex:1, padding:'6px 11px', borderRadius:6,
          border: color ? `1px solid ${color}` : isPrimary ? `1px solid ${T.accent}` : `1px solid ${T.border}`,
          background: color ? color : isPrimary ? T.accent : T.panel,
          color: (color || isPrimary) ? '#fff' : T.text,
          fontWeight:600, fontSize:12.5, cursor: buttonDisabled ? 'default' : 'pointer',
          textAlign:'left', display:'inline-flex', alignItems:'center', gap:7,
          opacity: buttonDisabled ? .6 : 1,
        }}>
          <span style={{flex:1}}>{buttonLabel}</span>
          {isOpenEnded && <span style={{
            fontSize:9.5, padding:'1px 5px', borderRadius:3,
            background:(color || isPrimary) ? 'rgba(255,255,255,.22)' : T.panel2,
            color:(color || isPrimary) ? '#fff' : T.mute,
            border:(color || isPrimary) ? 'none' : `1px solid ${T.border}`,
            textTransform:'uppercase', letterSpacing:.04, fontWeight:700,
          }}>needs note</span>}
          {!isOpenEnded && (
            <span style={{
              fontSize:10, opacity:.78, padding:'1px 5px', borderRadius:3,
              background:(color || isPrimary) ? 'rgba(255,255,255,.2)' : T.panel2,
              border:(color || isPrimary) ? 'none' : `1px solid ${T.border}`,
              color:(color || isPrimary) ? '#fff' : T.mute,
            }}>{liveMode ? 'Run' : '⌘C'}</span>
          )}
        </button>
        <button onClick={() => setExpanded(x => !x)} title="Show prompt" style={{
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
          }}>{action.prompt}{isOpenEnded && <span style={{color:T.accent}}>[your note appended here]</span>}</div>
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

function NoteInput({ T, value, setValue, label, hint, onSubmit, onCancel }) {
  return (
    <div style={{
      background:T.panel, border:`1px solid ${T.accentBorder}`, borderRadius:8,
      padding:'10px 12px',
    }}>
      <div style={{display:'flex', alignItems:'center', gap:8, marginBottom:6}}>
        <span style={{fontSize:10.5, fontWeight:700, color:T.accent, textTransform:'uppercase', letterSpacing:.05}}>{label}</span>
        <span style={{flex:1}}/>
        <span onClick={onCancel} style={{fontSize:11, color:T.mute, cursor:'pointer'}}>cancel</span>
      </div>
      <div style={{fontSize:10.5, color:T.mute, marginBottom:6, fontFamily:'"SF Mono",ui-monospace,monospace', lineHeight:1.5}}>
        will append to: <span style={{color:T.sub}}>{hint}</span>
      </div>
      <textarea
        autoFocus
        value={value} onChange={e => setValue(e.target.value)}
        placeholder="Type your changes / decision / scope here…"
        rows={3}
        style={{
          width:'100%', boxSizing:'border-box',
          padding:'8px 10px', borderRadius:6, fontSize:12.5, lineHeight:1.5,
          border:`1px solid ${T.border}`, background:T.panel2, color:T.text,
          outline:'none', resize:'vertical', fontFamily:'inherit',
        }}/>
      <div style={{display:'flex', gap:7, marginTop:7}}>
        <button onClick={onSubmit} disabled={!value.trim()} style={{
          padding:'5px 12px', borderRadius:6, border:`1px solid ${T.accent}`,
          background: value.trim() ? T.accent : T.panel2,
          color: value.trim() ? '#fff' : T.mute, fontWeight:600, fontSize:12,
          cursor: value.trim() ? 'pointer' : 'default',
        }}>Send</button>
        <button onClick={onCancel} style={{
          padding:'5px 12px', borderRadius:6, border:`1px solid ${T.border}`,
          background:T.panel, color:T.text, fontWeight:600, fontSize:12, cursor:'pointer',
        }}>Cancel</button>
      </div>
    </div>
  );
}

/* Reusable empty state */
function EmptyState({ T, title, detail }) {
  return (
    <div style={{padding:'60px 30px', textAlign:'center', color:T.sub}}>
      <div style={{fontSize:30, color:'#10b981', marginBottom:8}}>✓</div>
      <div style={{fontSize:14, fontWeight:600, color:T.text}}>{title}</div>
      <div style={{fontSize:12, marginTop:6, maxWidth:380, margin:'6px auto 0', lineHeight:1.5}}>{detail}</div>
    </div>
  );
}

/* ──────────────────────────────────────────────────────────────────────
   OUTPUTS view (R4 — inline document content)
   ────────────────────────────────────────────────────────────────────── */
function OutputsViewC({ T, liveMode, executeAction, selectedPath, setSelectedPath, search }) {
  const [reviewFilter, setReviewFilter] = useStV('pending');
  const [groupFilter, setGroupFilter] = useStV('all');
  const groups = ['all', ...Array.from(new Set(OUTPUTS.map(o => o.group)))];
  const counts = OUTPUTS.reduce((acc,o)=>{ acc[o.review] = (acc[o.review]||0)+1; return acc; }, {});

  const list = useMmV(() => OUTPUTS.filter(o => {
    if (reviewFilter !== 'all' && o.review !== reviewFilter) return false;
    if (groupFilter !== 'all' && o.group !== groupFilter) return false;
    if (search) {
      const q = search.toLowerCase();
      if (!(o.path + ' ' + o.agent + ' ' + o.group).toLowerCase().includes(q)) return false;
    }
    return true;
  }), [reviewFilter, groupFilter, search]);

  const selected = OUTPUTS.find(o => o.path === selectedPath) || list[0];
  useEfV(() => {
    if (!list.find(o => o.path === selectedPath)) setSelectedPath(list[0]?.path);
  }, [list, selectedPath]);

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
        width:170, background:T.headerBg, borderRight:`1px solid ${T.border}`,
        padding:'14px 10px', display:'flex', flexDirection:'column', gap:1, flexShrink:0,
      }}>
        <div style={{padding:'2px 8px 6px', fontSize:10.5, fontWeight:700, color:T.mute, textTransform:'uppercase', letterSpacing:.06}}>Review</div>
        {states.map(s => {
          const active = reviewFilter === s.id;
          return (
            <div key={s.id} onClick={() => setReviewFilter(s.id)} style={{
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
            <div key={g} onClick={() => setGroupFilter(g)} style={{
              padding:'6px 10px', borderRadius:6,
              background: active ? T.selectedBg : 'transparent',
              color: active ? T.accent : T.sub,
              fontWeight: active ? 600 : 500, fontSize:12, cursor:'pointer',
            }}>{g === 'all' ? 'All groups' : g}</div>
          );
        })}
      </div>

      {/* List */}
      <div style={{
        width:330, background:T.panel, borderRight:`1px solid ${T.border}`,
        display:'flex', flexDirection:'column', flexShrink:0,
      }}>
        <div style={{padding:'12px 14px 10px', borderBottom:`1px solid ${T.border}`}}>
          <div style={{display:'flex', alignItems:'baseline', justifyContent:'space-between'}}>
            <span style={{fontWeight:700, fontSize:13.5, color:T.text}}>
              {reviewFilter === 'all' ? 'All outputs' : reviewFilter.charAt(0).toUpperCase()+reviewFilter.slice(1)}
            </span>
            <span style={{fontSize:11, color:T.mute, fontVariantNumeric:'tabular-nums'}}>{list.length}</span>
          </div>
        </div>
        <div style={{flex:1, overflow:'auto'}}>
          {list.length === 0 ? (
            <div style={{padding:30, textAlign:'center', color:T.sub, fontSize:12}}>Nothing in this view.</div>
          ) : list.map(o => (
            <OutputRowC key={o.path} T={T} o={o}
              selected={selected?.path === o.path}
              onSelect={() => setSelectedPath(o.path)}/>
          ))}
        </div>
      </div>

      {/* Reader */}
      <div style={{flex:1, background:T.panel2, minWidth:0, overflow:'auto'}}>
        {selected
          ? <OutputReader T={T} o={selected} liveMode={liveMode} executeAction={executeAction}/>
          : <EmptyState T={T} title="No outputs" detail="Adjust filters to see artifacts."/>}
      </div>
    </>
  );
}
function OutputRowC({ T, o, selected, onSelect }) {
  const reviewColor = { pending:'#f59e0b', flagged:'#ef4444', approved:'#10b981', standing:T.sub }[o.review] || T.sub;
  return (
    <div onClick={onSelect} style={{
      padding:'10px 14px', borderBottom:`1px solid ${T.border}`,
      background: selected ? T.selectedBg : 'transparent',
      borderLeft:`3px solid ${selected ? T.accent : 'transparent'}`,
      cursor:'pointer',
    }}>
      <div style={{display:'flex', alignItems:'center', gap:7, marginBottom:4}}>
        <span style={{
          fontSize:9.5, fontWeight:700, padding:'2px 7px', borderRadius:3,
          background:reviewColor+'1f', color:reviewColor, textTransform:'uppercase', letterSpacing:.05,
        }}>{o.review}</span>
        <span style={{flex:1}}/>
        <span style={{fontSize:10.5, color:T.faint}}>{o.age}</span>
      </div>
      <code style={{
        fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:10.5, color:T.text,
        display:'block', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap', marginBottom:3,
      }} title={o.path}>{o.path.split('/').pop()}</code>
      <div style={{fontSize:10.5, color:T.sub}}>
        <code style={{fontFamily:'"SF Mono",ui-monospace,monospace'}}>{o.agent}</code>
      </div>
    </div>
  );
}
function OutputReader({ T, o, liveMode, executeAction }) {
  const reviewColor = { pending:'#f59e0b', flagged:'#ef4444', approved:'#10b981', standing:T.sub }[o.review] || T.sub;
  const content = OUTPUT_CONTENT[o.path];
  const [scrolled, setScrolled] = useStV(false);  // R4 — gentle hint, not gating
  const [armedIdx, setArmedIdx] = useStV(null);
  const [note, setNote] = useStV('');
  useEfV(() => { setArmedIdx(null); setNote(''); setScrolled(false); }, [o.path]);

  const actions = o.review === 'standing'
    ? [
        { verb:'Open file',     prompt:`Show me ${o.path}.`, api:{type:'open',path:o.path}, primary:true },
        { verb:'Stop watching', prompt:`Stop including ${o.path} in standing outputs.`, api:{type:'output-unwatch',path:o.path} },
      ]
    : [
        { verb:'Approve',  prompt:`Approve ${o.path} and log the verdict.`, api:{type:'output-approve',path:o.path}, color:'green', primary:true },
        { verb:'Revise',   prompt:`Rewrite ${o.path} with these changes: `, api:null },
        { verb:'Reject',   prompt:`Reject ${o.path} — delete it and log a Rejected row.`, api:{type:'output-reject',path:o.path}, color:'red' },
      ];

  return (
    <div style={{padding:'24px 28px 32px', maxWidth:820, margin:'0 auto'}}>
      <div style={{display:'flex', alignItems:'center', gap:8, marginBottom:12}}>
        <span style={{
          fontSize:10, padding:'2px 7px', borderRadius:4, fontWeight:700, textTransform:'uppercase', letterSpacing:.05,
          background:reviewColor+'1f', color:reviewColor,
        }}>{o.review}</span>
        <span style={{fontSize:11.5, color:T.sub}}>{o.group}</span>
        <span style={{color:T.faint}}>·</span>
        <span style={{fontSize:11, color:T.sub}}>via <code style={inlineCode(T)}>{o.via}</code></span>
        <span style={{flex:1}}/>
        <span style={{fontSize:11, color:T.mute}}>{o.age} ago</span>
      </div>
      <h1 style={{fontSize:20, fontWeight:700, color:T.text, lineHeight:1.3, marginBottom:6, letterSpacing:-0.3}}>
        {o.path.split('/').pop()}
      </h1>
      <div style={{
        padding:'7px 11px', background:T.panel, border:`1px solid ${T.border}`, borderRadius:7,
        marginBottom:16, display:'flex', alignItems:'center', gap:7,
      }}>
        <code style={{fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:11.5, color:T.text, flex:1, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap'}}>{o.path}</code>
        <code style={{fontFamily:'"SF Mono",ui-monospace,monospace', fontSize:10.5, color:T.mute}}>{o.agent}</code>
      </div>

      {/* R4 — content inline */}
      <div style={{
        background:T.panel, border:`1px solid ${T.border}`, borderRadius:9, overflow:'hidden',
        marginBottom:18,
      }}>
        <div style={{padding:'8px 12px', borderBottom:`1px solid ${T.border}`, background:T.panel2, fontSize:10.5, color:T.mute, fontWeight:600, textTransform:'uppercase', letterSpacing:.05}}>
          Content
        </div>
        <div onScroll={e => { if (e.target.scrollTop > 40) setScrolled(true); }}
          style={{padding:'14px 18px', maxHeight:460, overflow:'auto'}}>
          {content
            ? <MarkdownC text={content} T={T}/>
            : <div style={{color:T.mute, fontSize:12, fontStyle:'italic'}}>(content not baked — build-dashboard.py would inline this from {o.path})</div>}
        </div>
      </div>

      {/* mode hint */}
      <div style={{
        padding:'8px 11px', borderRadius:7, fontSize:11, lineHeight:1.5, marginBottom:12,
        background: liveMode ? 'rgba(16,185,129,.07)' : T.panel,
        border:`1px solid ${liveMode ? 'rgba(16,185,129,.25)' : T.border}`,
        color: liveMode ? '#10b981' : T.sub,
      }}>
        {liveMode
          ? <><b>One-click mode</b> — actions POST to <code style={inlineCode(T)}>/api/action</code>.</>
          : <><b>Command console</b> — actions copy a Claude prompt.</>}
      </div>

      {/* R4 — actions, with non-blocking hint to read first */}
      {!scrolled && o.review !== 'standing' && content && (
        <div style={{
          padding:'7px 11px', borderRadius:7, fontSize:11, lineHeight:1.5, marginBottom:8,
          background:T.panel2, border:`1px dashed ${T.border}`, color:T.mute,
        }}>
          Tip: scroll the content above before approving. (Not blocking — fast-approve still works.)
        </div>
      )}

      <div style={{display:'flex', flexDirection:'column', gap:7}}>
        {actions.map((a, i) => {
          const isOpenEnded = a.api === null;
          return (
            <ActionRowC key={i} T={T} action={a} liveMode={liveMode}
              isOpenEnded={isOpenEnded}
              isArmed={armedIdx === i}
              note={note}
              onArm={() => { setArmedIdx(i); setNote(''); }}
              onExecute={() => {
                executeAction({
                  prompt:a.prompt, api:a.api, note: isOpenEnded ? note : '',
                  label:a.verb, itemId:null, dismissOnRun:false,
                });
                if (isOpenEnded) { setArmedIdx(null); setNote(''); }
              }}/>
          );
        })}
      </div>
      {armedIdx !== null && actions[armedIdx]?.api === null && (
        <div style={{marginTop:12}}>
          <NoteInput T={T} value={note} setValue={setNote}
            label={`Your note for "${actions[armedIdx].verb}"`}
            hint={actions[armedIdx].prompt}
            onSubmit={() => {
              executeAction({
                prompt:actions[armedIdx].prompt, api:null, note,
                label:actions[armedIdx].verb, itemId:null, dismissOnRun:false,
              });
              setArmedIdx(null); setNote('');
            }}
            onCancel={() => { setArmedIdx(null); setNote(''); }}/>
        </div>
      )}
    </div>
  );
}

window.InboxViewC = InboxViewC;
window.OutputsViewC = OutputsViewC;
window.EmptyState = EmptyState;
window.inlineCode = inlineCode;
