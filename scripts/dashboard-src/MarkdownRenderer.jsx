import React from 'react';

function renderInline(text, T) {
  const parts = [];
  let last = 0;
  let key = 0;
  const re = /(\*\*[^*]+\*\*|`[^`]+`)/g;
  let m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) parts.push(text.slice(last, m.index));
    if (m[0].startsWith('**')) {
      parts.push(<strong key={key++} style={{ color: T.text, fontWeight: 600 }}>{m[0].slice(2, -2)}</strong>);
    } else {
      parts.push(<code key={key++} style={{
        fontFamily: '"SF Mono",ui-monospace,monospace', fontSize: '92%',
        background: T.panel2, color: T.text, padding: '1px 5px', borderRadius: 3,
        border: `1px solid ${T.border}`,
      }}>{m[0].slice(1, -1)}</code>);
    }
    last = m.index + m[0].length;
  }
  if (last < text.length) parts.push(text.slice(last));
  return parts;
}

export default function MarkdownRenderer({ text, T }) {
  if (!text) {
    return <div style={{ color: T.mute, fontSize: 12, fontStyle: 'italic' }}>(no content)</div>;
  }
  const lines = text.split('\n');
  const out = [];
  let inCode = false;
  let codeLines = [];
  let listItems = [];
  let tableLines = [];

  const flushList = () => {
    if (!listItems.length) return;
    out.push(
      <ul key={`l${out.length}`} style={{ margin: '4px 0 10px', paddingLeft: 18, listStyle: 'disc' }}>
        {listItems.map((li, i) => (
          <li key={i} style={{ color: T.text, fontSize: 13, lineHeight: 1.55, marginBottom: 3 }}>
            {renderInline(li, T)}
          </li>
        ))}
      </ul>
    );
    listItems = [];
  };

  const flushTable = () => {
    if (!tableLines.length) return;
    out.push(
      <pre key={`t${out.length}`} style={{
        margin: '4px 0 12px', padding: '10px 12px', background: T.panel2,
        border: `1px solid ${T.border}`, borderRadius: 7, fontSize: 11.5,
        fontFamily: '"SF Mono",ui-monospace,monospace', color: T.text,
        overflow: 'auto', lineHeight: 1.5,
      }}>{tableLines.join('\n')}</pre>
    );
    tableLines = [];
  };

  lines.forEach((line, i) => {
    if (line.startsWith('```')) {
      flushList(); flushTable();
      if (inCode) {
        out.push(
          <pre key={`c${i}`} style={{
            margin: '4px 0 12px', padding: '10px 12px',
            background: T.bg, border: `1px solid ${T.border}`, borderRadius: 7,
            fontSize: 11.5, fontFamily: '"SF Mono",ui-monospace,monospace',
            color: T.text, overflow: 'auto', lineHeight: 1.55,
          }}>{codeLines.join('\n')}</pre>
        );
        codeLines = []; inCode = false;
      } else {
        inCode = true;
      }
      return;
    }
    if (inCode) { codeLines.push(line); return; }

    if (line.trim().startsWith('|')) { flushList(); tableLines.push(line); return; }
    if (tableLines.length) flushTable();

    if (line.startsWith('# ')) {
      flushList();
      out.push(<h2 key={i} style={{ fontSize: 18, fontWeight: 700, color: T.text, letterSpacing: -0.3, margin: '18px 0 6px' }}>{renderInline(line.slice(2), T)}</h2>);
    } else if (line.startsWith('## ')) {
      flushList();
      out.push(<h3 key={i} style={{ fontSize: 15, fontWeight: 700, color: T.text, margin: '18px 0 6px', letterSpacing: -0.2 }}>{renderInline(line.slice(3), T)}</h3>);
    } else if (line.startsWith('### ')) {
      flushList();
      out.push(<h4 key={i} style={{ fontSize: 12.5, fontWeight: 700, color: T.text, textTransform: 'uppercase', letterSpacing: .04, margin: '14px 0 5px' }}>{renderInline(line.slice(4), T)}</h4>);
    } else if (line.startsWith('---')) {
      flushList();
      out.push(<hr key={i} style={{ border: 'none', borderTop: `1px solid ${T.border}`, margin: '14px 0' }} />);
    } else if (line.startsWith('> ')) {
      flushList();
      out.push(<blockquote key={i} style={{
        margin: '8px 0', padding: '8px 12px', borderLeft: `3px solid ${T.accent}`,
        background: T.accentSoft, color: T.text, fontSize: 12.5, lineHeight: 1.5, borderRadius: '0 6px 6px 0',
      }}>{renderInline(line.slice(2), T)}</blockquote>);
    } else if (line.startsWith('- ') || line.startsWith('* ')) {
      listItems.push(line.slice(2));
    } else if (line.trim() === '') {
      flushList();
    } else {
      flushList();
      out.push(<p key={i} style={{ margin: '0 0 8px', color: T.text, fontSize: 13, lineHeight: 1.6 }}>{renderInline(line, T)}</p>);
    }
  });
  flushList(); flushTable();
  if (inCode && codeLines.length) {
    out.push(<pre key="c-final" style={{ padding: '10px 12px', background: T.bg, border: `1px solid ${T.border}`, borderRadius: 7, fontSize: 11.5, fontFamily: '"SF Mono",ui-monospace,monospace', color: T.text }}>{codeLines.join('\n')}</pre>);
  }
  return <div>{out}</div>;
}
