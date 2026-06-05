#!/usr/bin/env node
// Bundles the React dashboard into a self-contained string that
// build-dashboard.py inlines between the JS sentinels in index.html.
//
// Output: scripts/dashboard-src/dist/bundle.js
// Run:    node scripts/dashboard-src/build.js [--watch]
//         Or via: python3 scripts/build-dashboard.py (calls this automatically)
'use strict';

const esbuild = require('esbuild');
const path = require('path');
const fs = require('fs');

const SRC = path.join(__dirname, 'index.jsx');
const OUT = path.join(__dirname, 'dist', 'bundle.js');

fs.mkdirSync(path.join(__dirname, 'dist'), { recursive: true });

async function build() {
  try {
    await esbuild.build({
      entryPoints: [SRC],
      bundle: true,
      format: 'iife',
      globalName: 'DashboardApp',
      target: ['es2020'],
      jsx: 'automatic',
      minify: process.env.NODE_ENV !== 'development',
      sourcemap: false,
      outfile: OUT,
      define: {
        'process.env.NODE_ENV': '"production"',
      },
      logLevel: 'info',
    });
    console.log('build-dashboard-react: bundle written to', OUT);
    const size = fs.statSync(OUT).size;
    console.log('  size:', Math.round(size / 1024) + 'KB');
  } catch (err) {
    console.error('build-dashboard-react: build failed:', err.message);
    process.exit(1);
  }
}

build();
