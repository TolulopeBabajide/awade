export function tokens(theme) {
  return theme === 'dark' ? {
    bg: '#0a0b0e', appShell: '#0f1015', panel: '#15171c', panel2: '#1a1d24', panelHover: '#1d2028',
    border: '#23252e', borderStrong: '#33363f',
    text: '#ededee', sub: '#a3a4ad', mute: '#74757d', faint: '#52535b',
    accent: '#818cf8', accentSoft: 'rgba(129,140,248,.14)', accentBorder: 'rgba(129,140,248,.5)',
    selectedBg: 'rgba(129,140,248,.14)',
    shadow: '0 1px 2px rgba(0,0,0,.4), 0 8px 24px rgba(0,0,0,.32)',
    shadowSm: '0 1px 2px rgba(0,0,0,.3)',
    headerBg: '#0d0e13',
  } : {
    bg: '#fbfbfc', appShell: '#f1f1f4', panel: '#ffffff', panel2: '#f7f7fa', panelHover: '#f1f1f5',
    border: '#e8e8ec', borderStrong: '#d5d5dc',
    text: '#15161a', sub: '#54555c', mute: '#7d7e85', faint: '#a8a9b0',
    accent: '#5b5bf0', accentSoft: 'rgba(91,91,240,.07)', accentBorder: 'rgba(91,91,240,.4)',
    selectedBg: 'rgba(91,91,240,.08)',
    shadow: '0 1px 2px rgba(20,20,30,.04), 0 8px 22px rgba(20,20,30,.06)',
    shadowSm: '0 1px 2px rgba(20,20,30,.05)',
    headerBg: '#fafafb',
  };
}

export const URGENCY_COLOR = { high: '#ef4444', medium: '#f59e0b', low: '#10b981' };
export const KIND_GLYPH = { approve: '✓', decide: '?', review: '◔', respond: '↩' };
export const STATUS_COLOR = {
  healthy: '#10b981', warning: '#f59e0b', critical: '#ef4444',
  idle: '#a1a1aa', 'on-demand': '#60a5fa',
};
