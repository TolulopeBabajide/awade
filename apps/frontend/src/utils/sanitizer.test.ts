import { describe, it, expect } from 'vitest';
import { sanitizeRedirectPath } from './sanitizer';

describe('sanitizeRedirectPath', () => {
    it('returns a valid relative path unchanged', () => {
        expect(sanitizeRedirectPath('/dashboard')).toBe('/dashboard');
        expect(sanitizeRedirectPath('/lesson-plans/42')).toBe('/lesson-plans/42');
        expect(sanitizeRedirectPath('/guides/generate?child=1&topic=2')).toBe('/guides/generate?child=1&topic=2');
    });

    it('returns fallback for protocol-relative paths (open-redirect via //)', () => {
        expect(sanitizeRedirectPath('//evil.com')).toBe('/dashboard');
        expect(sanitizeRedirectPath('//evil.com/steal')).toBe('/dashboard');
    });

    it('normalises backslashes and then validates (GHSA-wrjc-x8rr-h8h6 vector)', () => {
        // \evil.com → /evil.com → starts with /, but after normalisation is //evil.com? No —
        // \evil.com normalises to /evil.com which starts with exactly one /
        // The dangerous form is \\evil.com → //evil.com → rejected
        expect(sanitizeRedirectPath('\\\\evil.com')).toBe('/dashboard');
        // Single backslash that would become /evil.com after normalise — this is NOT protocol-relative,
        // so it would pass. Attackers use // or \\ to trigger external redirect.
        // Valid relative path with backslash-separator (unusual but let's confirm normalisation):
        expect(sanitizeRedirectPath('\\dashboard')).toBe('/dashboard');
    });

    it('returns fallback for missing or empty input', () => {
        expect(sanitizeRedirectPath(null)).toBe('/dashboard');
        expect(sanitizeRedirectPath(undefined)).toBe('/dashboard');
        expect(sanitizeRedirectPath('')).toBe('/dashboard');
    });

    it('returns fallback for non-string input', () => {
        expect(sanitizeRedirectPath(undefined)).toBe('/dashboard');
    });

    it('respects a custom fallback', () => {
        expect(sanitizeRedirectPath('//evil.com', '/login')).toBe('/login');
        expect(sanitizeRedirectPath(null, '/home')).toBe('/home');
    });

    it('returns fallback for paths without leading slash (relative or external)', () => {
        expect(sanitizeRedirectPath('dashboard')).toBe('/dashboard');
        expect(sanitizeRedirectPath('https://evil.com')).toBe('/dashboard');
        expect(sanitizeRedirectPath('javascript:alert(1)')).toBe('/dashboard');
    });
});
