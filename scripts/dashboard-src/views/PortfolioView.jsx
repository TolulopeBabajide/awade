import React, { useEffect, useState } from 'react';

const STAGES = ['discover', 'define', 'gtm', 'design', 'ready', 'in-progress', 'done'];
const LABELS = { discover: 'Discover', define: 'Define', gtm: 'GTM', design: 'Design', ready: 'Ready', 'in-progress': 'Building', done: 'Done' };
const COLORS = ['#64748b', '#818cf8', '#c084fc', '#38bdf8', '#22c55e', '#f59e0b', '#10b981'];

function LifecycleRail({ project, T }) {
  const counts = project.stages || {};
  const total = Math.max(1, STAGES.reduce((n, s) => n + (counts[s] || 0), 0));
  return (
    <div>
      <div style={{ height: 7, display: 'flex', overflow: 'hidden', borderRadius: 99, background: T.panel2 }}>
        {STAGES.map((stage, i) => counts[stage] > 0 && (
          <span key={stage} title={`${LABELS[stage]}: ${counts[stage]}`} style={{ width: `${counts[stage] / total * 100}%`, background: COLORS[i] }} />
        ))}
      </div>
      <div style={{ display: 'flex', gap: 12, marginTop: 9, flexWrap: 'wrap' }}>
        {STAGES.filter(s => counts[s]).map((stage, i) => (
          <span key={stage} style={{ fontSize: 10.5, color: T.mute }}><b style={{ color: T.sub }}>{counts[stage]}</b> {LABELS[stage]}</span>
        ))}
      </div>
    </div>
  );
}

function ProjectCard({ project, T }) {
  const tone = project.critical > 0 ? '#ef4444' : project.warning > 0 ? '#f59e0b' : '#10b981';
  return (
    <a href={`/projects/${encodeURIComponent(project.id)}/`} style={{ color: 'inherit', textDecoration: 'none' }}>
      <article style={{ background: T.panel, border: `1px solid ${T.border}`, borderRadius: 12, padding: 18, minHeight: 168, boxShadow: T.shadowSm, transition: 'border-color .16s, transform .16s' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
          <div style={{ width: 38, height: 38, borderRadius: 10, display: 'grid', placeItems: 'center', background: project.color || T.accentSoft, color: T.text, fontWeight: 800, letterSpacing: -.5 }}>{project.name.slice(0, 2).toUpperCase()}</div>
          <div style={{ minWidth: 0, flex: 1 }}>
            <div style={{ fontWeight: 750, fontSize: 15, letterSpacing: -.25 }}>{project.name}</div>
            <div style={{ color: T.mute, fontSize: 11, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', marginTop: 2 }}>{project.path}</div>
          </div>
          <span style={{ width: 8, height: 8, borderRadius: '50%', background: tone, boxShadow: `0 0 0 4px ${tone}1f`, marginTop: 7 }} />
        </div>
        <div style={{ marginTop: 22 }}><LifecycleRail project={project} T={T} /></div>
        <div style={{ display: 'flex', marginTop: 17, paddingTop: 13, borderTop: `1px solid ${T.border}`, color: T.mute, fontSize: 11 }}>
          <span>{project.open || 0} open</span><span style={{ marginLeft: 14 }}>{project.pendingOutputs || 0} to review</span><span style={{ marginLeft: 'auto', color: T.sub, fontWeight: 650 }}>Open workspace →</span>
        </div>
      </article>
    </a>
  );
}

export default function PortfolioView({ T, onToast }) {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [mode, setMode] = useState('new');
  const [name, setName] = useState('');
  const [path, setPath] = useState('');
  const [choosing, setChoosing] = useState(false);
  const [folderPicker, setFolderPicker] = useState(null);
  const [formError, setFormError] = useState('');

  const refresh = () => fetch('/api/projects').then(r => r.json()).then(d => setProjects(d.projects || [])).finally(() => setLoading(false));
  useEffect(refresh, []);

  async function createProject(e) {
    e.preventDefault();
    setFormError('');
    const token = document.querySelector('meta[name="dashboard-csrf-token"]')?.content;
    const response = await fetch('/api/projects', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Dashboard-CSRF': token || '' }, body: JSON.stringify({ mode, name, path }) });
    const data = await response.json();
    if (!response.ok) {
      setFormError(data.error || 'Project could not be added');
      return;
    }
    window.location.href = `/projects/${encodeURIComponent(data.project.id)}/`;
  }

  async function browseFolder(nextPath = '') {
    const token = document.querySelector('meta[name="dashboard-csrf-token"]')?.content;
    if (!token) return onToast?.('Run the local dashboard service to choose a folder');
    setChoosing(true);
    try {
      const response = await fetch('/api/select-folder', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Dashboard-CSRF': token },
        body: JSON.stringify({ path: nextPath }),
      });
      const data = await response.json();
      if (!response.ok) return onToast?.(data.error || 'Folder chooser could not open');
      setFolderPicker(data);
    } catch {
      onToast?.('Folder chooser could not connect to agentOS');
    } finally {
      setChoosing(false);
    }
  }

  function chooseFolder() {
    browseFolder(path);
  }

  return (
    <div style={{ flex: 1, overflow: 'auto', padding: '32px clamp(22px, 5vw, 72px) 60px' }}>
      <header style={{ display: 'flex', alignItems: 'flex-end', gap: 24, marginBottom: 30 }}>
        <div style={{ flex: 1 }}>
          <div style={{ color: T.accent, fontSize: 10.5, fontWeight: 800, letterSpacing: 1.5, textTransform: 'uppercase' }}>Portfolio command</div>
          <h1 style={{ fontSize: 'clamp(28px, 4vw, 48px)', lineHeight: 1, letterSpacing: -2, margin: '10px 0 8px', fontWeight: 780 }}>Every product. One operating view.</h1>
          <p style={{ margin: 0, color: T.mute, maxWidth: 620, fontSize: 13.5 }}>Create, onboard, review, and move software through discovery, design, delivery, and operations.</p>
        </div>
        <button onClick={() => setShowCreate(true)} style={{ border: 0, borderRadius: 8, padding: '10px 15px', background: T.accent, color: '#fff', fontWeight: 750, cursor: 'pointer' }}>＋ Add project</button>
      </header>

      {loading ? <div style={{ color: T.mute }}>Loading portfolio…</div> : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(310px, 1fr))', gap: 14 }}>
          {projects.map(p => <ProjectCard key={p.id} project={p} T={T} />)}
          {!projects.length && <button onClick={() => setShowCreate(true)} style={{ minHeight: 190, border: `1px dashed ${T.borderStrong}`, borderRadius: 12, background: 'transparent', color: T.sub, cursor: 'pointer' }}>Add your first project</button>}
        </div>
      )}

      {showCreate && <div onClick={() => setShowCreate(false)} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,.62)', display: 'grid', placeItems: 'center', zIndex: 50, padding: 20 }}>
        <form onSubmit={createProject} onClick={e => e.stopPropagation()} style={{ position: 'relative', width: 'min(480px, 100%)', background: T.panel, border: `1px solid ${T.borderStrong}`, borderRadius: 14, padding: 22, boxShadow: T.shadow }}>
          <div style={{ fontSize: 18, fontWeight: 760, letterSpacing: -.4 }}>Add a project</div>
          <div style={{ display: 'flex', background: T.panel2, padding: 3, borderRadius: 8, margin: '18px 0' }}>
            {[['new', 'Create new'], ['existing', 'Onboard existing']].map(([id, label]) => <button type="button" key={id} onClick={() => setMode(id)} style={{ flex: 1, border: 0, borderRadius: 6, padding: 8, cursor: 'pointer', background: mode === id ? T.panel : 'transparent', color: mode === id ? T.text : T.mute, fontWeight: 650 }}>{label}</button>)}
          </div>
          <label style={{ display: 'block', color: T.sub, fontSize: 11.5, marginBottom: 6 }}>Project name</label>
          <input value={name} onChange={e => setName(e.target.value)} required placeholder="Example: Atlas" style={{ width: '100%', boxSizing: 'border-box', padding: 10, borderRadius: 7, border: `1px solid ${T.borderStrong}`, background: T.panel2, color: T.text, outline: 'none', marginBottom: 14 }} />
          <label style={{ display: 'block', color: T.sub, fontSize: 11.5, marginBottom: 6 }}>{mode === 'new' ? 'Create in folder' : 'Existing project folder'}</label>
          <div style={{ display: 'flex', gap: 8 }}>
            <input value={path} onChange={e => setPath(e.target.value)} required placeholder="Select a folder or paste its path" style={{ flex: 1, minWidth: 0, boxSizing: 'border-box', padding: 10, borderRadius: 7, border: `1px solid ${T.borderStrong}`, background: T.panel2, color: T.text, outline: 'none' }} />
            <button type="button" onClick={chooseFolder} disabled={choosing} style={{ whiteSpace: 'nowrap', border: `1px solid ${T.borderStrong}`, background: T.panel2, color: T.text, borderRadius: 7, padding: '0 12px', cursor: choosing ? 'wait' : 'pointer', fontWeight: 650 }}>{choosing ? 'Opening…' : 'Choose folder…'}</button>
          </div>
          <p style={{ color: T.mute, fontSize: 11, lineHeight: 1.5 }}>{mode === 'new' ? 'Creates a ready-to-configure agentOS project from this template.' : 'Adds the agentOS control files without replacing existing application files.'}</p>
          {formError && <div role="alert" style={{ marginTop: 12, border: '1px solid rgba(239,68,68,.35)', background: 'rgba(239,68,68,.09)', color: '#fca5a5', borderRadius: 7, padding: '9px 10px', fontSize: 11.5, lineHeight: 1.45 }}>{formError}</div>}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, marginTop: 20 }}><button type="button" onClick={() => setShowCreate(false)} style={{ border: `1px solid ${T.border}`, background: 'transparent', color: T.sub, borderRadius: 7, padding: '8px 12px' }}>Cancel</button><button type="submit" style={{ border: 0, background: T.accent, color: '#fff', borderRadius: 7, padding: '8px 13px', fontWeight: 700 }}>{mode === 'new' ? 'Create project' : 'Onboard project'}</button></div>

          {folderPicker && <div style={{ position: 'fixed', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', width: 'min(580px, calc(100vw - 32px))', height: 'min(620px, calc(100vh - 48px))', zIndex: 70, background: T.panel, border: `1px solid ${T.borderStrong}`, borderRadius: 14, display: 'flex', flexDirection: 'column', overflow: 'hidden', boxShadow: '0 24px 80px rgba(0,0,0,.65)' }}>
            <div style={{ padding: '16px 18px', borderBottom: `1px solid ${T.border}`, display: 'flex', alignItems: 'center', gap: 10 }}>
              <button type="button" disabled={!folderPicker.parent || choosing} onClick={() => folderPicker.parent && browseFolder(folderPicker.parent)} style={{ border: `1px solid ${T.border}`, background: T.panel2, color: folderPicker.parent ? T.text : T.faint, borderRadius: 7, padding: '6px 9px' }}>↑</button>
              <div style={{ minWidth: 0, flex: 1 }}><div style={{ fontSize: 11, color: T.mute }}>Choose a folder</div><div title={folderPicker.path} style={{ fontSize: 12, fontWeight: 650, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{folderPicker.path}</div></div>
              <button type="button" onClick={() => setFolderPicker(null)} style={{ border: 0, background: 'transparent', color: T.mute, fontSize: 18 }}>×</button>
            </div>
            <div style={{ flex: 1, minHeight: 0, overflow: 'auto', padding: 8 }}>
              {(folderPicker.folders || []).map(folder => <div key={folder.path} style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '3px 4px', borderRadius: 7 }}>
                <button type="button" onClick={() => browseFolder(folder.path)} style={{ minWidth: 0, flex: 1, border: 0, background: 'transparent', color: T.text, display: 'flex', alignItems: 'center', gap: 10, padding: '8px 7px', borderRadius: 6, cursor: 'pointer', textAlign: 'left' }}><span style={{ color: T.accent }}>▰</span><span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{folder.name}</span><span style={{ marginLeft: 'auto', color: T.faint }}>›</span></button>
                <button type="button" onClick={() => { setPath(folder.path); setFolderPicker(null); }} style={{ border: `1px solid ${T.border}`, background: T.panel2, color: T.sub, borderRadius: 6, padding: '6px 9px', cursor: 'pointer', fontSize: 11, fontWeight: 650 }}>Select</button>
              </div>)}
              {!folderPicker.folders?.length && <div style={{ color: T.mute, padding: 16, textAlign: 'center' }}>No folders inside this location</div>}
            </div>
            <div style={{ marginTop: 'auto', padding: 14, borderTop: `1px solid ${T.border}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ color: T.mute, fontSize: 11 }}>Select the current folder or open a folder to go deeper.</span>
              <button type="button" onClick={() => { setPath(folderPicker.path); setFolderPicker(null); }} style={{ border: 0, background: T.accent, color: '#fff', borderRadius: 7, padding: '8px 12px', fontWeight: 700 }}>Select this folder</button>
            </div>
          </div>}
        </form>
      </div>}
    </div>
  );
}
