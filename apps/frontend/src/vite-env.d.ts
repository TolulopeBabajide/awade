/// <reference types="vite/client" />

// Ambient stub for @sentry/react — provides types when the package is not yet
// installed locally (e.g. fresh checkout before `npm ci`). The real package
// types take precedence once `npm ci` / `npm install` runs.
declare module '@sentry/react' {
  export interface BrowserOptions {
    dsn?: string;
    environment?: string;
    integrations?: unknown[];
    tracesSampleRate?: number;
    replaysSessionSampleRate?: number;
    replaysOnErrorSampleRate?: number;
    sendDefaultPii?: boolean;
    [key: string]: unknown;
  }
  export function init(options: BrowserOptions): void;
  export function browserTracingIntegration(): unknown;
  export function replayIntegration(options?: { maskAllText?: boolean; blockAllMedia?: boolean }): unknown;
}
