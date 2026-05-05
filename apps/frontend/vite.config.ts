import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    // Split large vendor chunks to improve initial load time (Lighthouse performance)
    rollupOptions: {
      output: {
        // Function form is required for Vite 7 / Rollup 4 to correctly extract
        // CJS-pre-bundled packages (react, react-dom) into separate chunks.
        // The object form silently produces empty chunks for these packages.
        manualChunks(id) {
          // Stable framework core — long-lived cache, changes only on React upgrades
          if (id.includes('node_modules/react/') || id.includes('node_modules/react-dom/') || id.includes('node_modules/scheduler/')) {
            return 'vendor-react';
          }
          // Routing — separate so a router upgrade doesn't bust the React cache
          if (id.includes('node_modules/react-router') || id.includes('node_modules/@remix-run/')) {
            return 'vendor-router';
          }
          // Data fetching — separate so a query-lib upgrade doesn't bust the React cache
          if (id.includes('node_modules/@tanstack/')) {
            return 'vendor-query';
          }
          // Auth — relatively stable; separate so app changes don't bust this chunk
          if (id.includes('node_modules/@react-oauth/')) {
            return 'vendor-auth';
          }
          // Error monitoring — large SDK, updated independently of app code
          if (id.includes('node_modules/@sentry/')) {
            return 'vendor-sentry';
          }
          // Icon libraries — large asset, almost never changes
          if (id.includes('node_modules/@heroicons/') || id.includes('node_modules/react-icons/')) {
            return 'vendor-icons';
          }
        },
      },
    },
    // Inline assets smaller than 4KB to reduce requests
    assetsInlineLimit: 4096,
  },
}) 