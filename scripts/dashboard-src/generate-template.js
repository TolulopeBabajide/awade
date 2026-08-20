#!/usr/bin/env node
// Reads the built bundle and writes docs/agentic/dashboard/index.html with the bundle
// inlined. The DASHBOARD_DATA sentinel block is kept empty (placeholder) so
// build-dashboard.py can inject real data on each run.
//
// Run this once after rebuilding the components. The resulting index.html
// should be committed; build-dashboard.py only touches the data block.
'use strict';

const fs = require('fs');
const path = require('path');

const BUNDLE = path.join(__dirname, 'dist', 'bundle.js');
const OUT = path.join(__dirname, '../../docs/agentic/dashboard/index.html');

if (!fs.existsSync(BUNDLE)) {
  console.error('generate-template: bundle not found — run `node build.js` first');
  process.exit(1);
}

const bundle = fs.readFileSync(BUNDLE, 'utf8');

const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Agent Dashboard</title>
<style>
  html, body, #dashboard-root { margin: 0; padding: 0; height: 100%; width: 100%; overflow: hidden; }
  body { background: #0a0b0e; }
  @keyframes fadeIn { from { opacity: 0; transform: translateY(-3px); } to { opacity: 1; transform: translateY(0); } }
  @keyframes slideInRight { from { transform: translateX(100%); } to { transform: translateX(0); } }
  *::-webkit-scrollbar { width: 7px; height: 7px; }
  *::-webkit-scrollbar-thumb { background: rgba(127,127,140,.32); border-radius: 4px; }
  *::-webkit-scrollbar-thumb:hover { background: rgba(127,127,140,.55); }
  *::-webkit-scrollbar-track { background: transparent; }
  button { font-family: inherit; }
</style>
</head>
<body>
<div id="dashboard-root"></div>
<script>
/* DASHBOARD_DATA_START */
window.DASHBOARD_DATA = {};
/* DASHBOARD_DATA_END */
</script>
<script>
${bundle}
</script>
</body>
</html>
`;

fs.writeFileSync(OUT, html, 'utf8');
console.log('generate-template: wrote', OUT);
console.log('  size:', Math.round(fs.statSync(OUT).size / 1024) + 'KB');
