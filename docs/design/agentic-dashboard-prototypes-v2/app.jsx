// Main app — design canvas hosting all three directions side-by-side.

const { useState: useStateApp, useEffect: useEffectApp } = React;

// Tiny localStorage hook — persists themeC + liveMode + themeA + themeB
// across reloads so the prototype matches the redesign's persistence requirement.
function usePersistedApp(key, initial) {
  const [v, setV] = useStateApp(() => {
    try {
      const s = localStorage.getItem(key);
      return s != null ? JSON.parse(s) : initial;
    } catch { return initial; }
  });
  useEffectApp(() => {
    try { localStorage.setItem(key, JSON.stringify(v)); } catch {}
  }, [key, v]);
  return [v, setV];
}

function App() {
  const [themeA, setThemeA] = usePersistedApp('app:themeA', 'light');
  const [themeB, setThemeB] = usePersistedApp('app:themeB', 'dark');
  const [themeC, setThemeC] = usePersistedApp('app:themeC', 'light');
  // liveMode is shared so toggling in one reflects in all three.
  const [liveMode, setLiveMode] = usePersistedApp('app:liveMode', false);

  return (
    <DesignCanvas>
      <DCSection id="dashboards" title="Agentic system dashboard" subtitle="Three directions · click ⤢ to focus an artboard">
        <DCArtboard id="command-center" label="A · Command Center" width={1360} height={920}>
          <ThemeFrame theme={themeA} setTheme={setThemeA}>
            <CommandCenter theme={themeA} liveMode={liveMode} setLiveMode={setLiveMode}/>
          </ThemeFrame>
        </DCArtboard>
        <DCArtboard id="inbox" label="B · Inbox" width={1360} height={920}>
          <ThemeFrame theme={themeB} setTheme={setThemeB}>
            <InboxApp theme={themeB} liveMode={liveMode} setLiveMode={setLiveMode}/>
          </ThemeFrame>
        </DCArtboard>
        <DCArtboard id="hybrid" label="C · Hybrid (per redesign spec)" width={1360} height={920}>
          <ThemeFrame theme={themeC} setTheme={setThemeC}>
            <HybridApp theme={themeC} liveMode={liveMode} setLiveMode={setLiveMode}/>
          </ThemeFrame>
        </DCArtboard>
      </DCSection>
    </DesignCanvas>
  );
}

// Sits over the artboard and renders a small light/dark toggle in the top-right.
function ThemeFrame({ theme, setTheme, children }) {
  return (
    <div style={{width:'100%', height:'100%', position:'relative', overflow:'hidden', borderRadius:6}}>
      {children}
      <div onClick={()=> setTheme(theme === 'light' ? 'dark' : 'light')} style={{
        position:'absolute', top:14, right:18, zIndex:40,
        width:30, height:30, borderRadius:8, cursor:'pointer',
        background: theme === 'dark' ? 'rgba(255,255,255,.08)' : 'rgba(0,0,0,.05)',
        border: `1px solid ${theme === 'dark' ? 'rgba(255,255,255,.12)' : 'rgba(0,0,0,.08)'}`,
        color: theme === 'dark' ? '#ededee' : '#15161a',
        display:'inline-flex', alignItems:'center', justifyContent:'center',
        transition:'background .15s, transform .15s',
      }}
      onMouseEnter={e=> e.currentTarget.style.transform = 'scale(1.06)'}
      onMouseLeave={e=> e.currentTarget.style.transform = 'scale(1)'}
      title={theme === 'light' ? 'Switch to dark' : 'Switch to light'}>
        {theme === 'dark' ? (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="4.5"/>
            <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/>
          </svg>
        ) : (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/>
          </svg>
        )}
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App/>);
