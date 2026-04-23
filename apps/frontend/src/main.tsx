import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App.tsx'
import './index.css'
import { GoogleOAuthProvider } from '@react-oauth/google';

// ---------------------------------------------------------------------------
// Sentry error monitoring (AWD-H-01)
// Only initialised when VITE_SENTRY_DSN is provided at build time.
// Lazy-imported so the SDK is fully tree-shaken out of builds without a DSN.
// ---------------------------------------------------------------------------
const sentryDsn = import.meta.env.VITE_SENTRY_DSN as string | undefined;
if (sentryDsn) {
  import('@sentry/react').then(({ init, browserTracingIntegration, replayIntegration }) => {
    init({
      dsn: sentryDsn,
      environment: import.meta.env.MODE,
      integrations: [
        browserTracingIntegration(),
        // Session replays: 10 % of sessions, 100 % on errors.
        replayIntegration({ maskAllText: true, blockAllMedia: true }),
      ],
      tracesSampleRate: 0.1,
      replaysSessionSampleRate: 0.1,
      replaysOnErrorSampleRate: 1.0,
      // Never send PII — COPPA / GDPR safety.
      sendDefaultPii: false,
    });
  }).catch(() => {
    // Non-fatal: app still runs without Sentry
  });
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </GoogleOAuthProvider>
    </QueryClientProvider>
  </React.StrictMode>,
) 