
import { describe, it, expect, vi, beforeEach } from 'vitest'
import apiService from '../../services/api'

// Mock fetch — all calls go through apiFetch which adds credentials: 'include'
globalThis.fetch = vi.fn()

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('login', () => {
    it('should make a POST request to login endpoint with credentials', async () => {
      const mockResponse = {
        ok: true,
        url: '/api/auth/login',
        json: vi.fn().mockResolvedValue({ user: { user_id: 1, email: 'test@example.com' }, token_type: 'bearer' })
      }
      ;(globalThis.fetch as any).mockResolvedValue(mockResponse)

      const result = await apiService.login('test@example.com', 'password')

      // apiFetch always adds credentials: 'include'; no Authorization header
      expect(globalThis.fetch).toHaveBeenCalledWith('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'test@example.com', password: 'password' }),
        credentials: 'include',
      })
      expect(result.data).toBeDefined()
    })

    it('should handle login errors', async () => {
      const mockResponse = {
        ok: false,
        status: 401,
        url: '/api/auth/login',
        statusText: 'Unauthorized',
        json: vi.fn().mockResolvedValue({ detail: 'Invalid credentials' })
      }
      ;(globalThis.fetch as any).mockResolvedValue(mockResponse)

      const result = await apiService.login('test@example.com', 'wrong_password')

      expect(result.error).toBe('Invalid credentials')
    })
  })

  describe('signup', () => {
    it('should make a POST request to signup endpoint with credentials', async () => {
      const mockResponse = {
        ok: true,
        url: '/api/auth/signup',
        json: vi.fn().mockResolvedValue({ user: { user_id: 2 }, token_type: 'bearer' })
      }
      ;(globalThis.fetch as any).mockResolvedValue(mockResponse)

      const userData = {
        full_name: 'Test User',
        email: 'test@example.com',
        password: 'password123'
      }

      const result = await apiService.signup(userData)

      expect(globalThis.fetch).toHaveBeenCalledWith('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
        credentials: 'include',
      })
      expect(result.data).toBeDefined()
    })
  })

  describe('getCurrentUser', () => {
    it('should make a GET request using cookie auth (no Authorization header)', async () => {
      const mockResponse = {
        ok: true,
        url: '/api/auth/me',
        json: vi.fn().mockResolvedValue({ user_id: 1, email: 'test@example.com' })
      }
      ;(globalThis.fetch as any).mockResolvedValue(mockResponse)

      const result = await apiService.getCurrentUser()

      // Cookie is sent automatically — no Authorization header expected
      expect(globalThis.fetch).toHaveBeenCalledWith('/api/auth/me', {
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
      })
      expect(result.data).toEqual({ user_id: 1, email: 'test@example.com' })
    })

    it('should handle 401 errors by redirecting to login', async () => {
      const mockResponse = {
        ok: false,
        status: 401,
        url: '/api/auth/me',
        json: vi.fn().mockResolvedValue({ detail: 'Unauthorized' })
      }
      ;(globalThis.fetch as any).mockResolvedValue(mockResponse)

      // Mock window.location.href
      delete (window as any).location
      window.location = { href: '' } as any

      const result = await apiService.getCurrentUser()

      expect(result.error).toBe('Session expired. Please login again.')
      expect(window.location.href).toBe('/login')
    })

    it('should log refresh errors in DEV mode and return session expired when refreshAccessToken throws', async () => {
      const unauthorizedResponse = {
        ok: false,
        status: 401,
        url: '/api/auth/me',
        json: vi.fn().mockResolvedValue({ detail: 'Unauthorized' })
      }
      ;(globalThis.fetch as any).mockResolvedValueOnce(unauthorizedResponse)

      // Bypass the internal try-catch in refreshAccessToken so the outer catch in
      // handleResponse is reached — the path guarded by `if (import.meta.env.DEV)`
      const refreshSpy = vi.spyOn(apiService as any, 'refreshAccessToken')
        .mockRejectedValueOnce(new Error('Network error during refresh'))

      delete (window as any).location
      window.location = { href: '' } as any

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      const result = await apiService.getCurrentUser()

      // In DEV mode (test env default), the guarded console.error fires
      expect(consoleSpy).toHaveBeenCalledWith('Refresh failed', expect.any(Error))
      // The error is handled gracefully regardless of mode
      expect(result.error).toBe('Session expired. Please login again.')
      expect(window.location.href).toBe('/login')

      consoleSpy.mockRestore()
      refreshSpy.mockRestore()
    })
  })

  describe('updateProfile', () => {
    it('should make a PUT request to profile endpoint with credentials', async () => {
      const mockResponse = {
        ok: true,
        url: '/api/users/1/profile',
        json: vi.fn().mockResolvedValue({ success: true })
      }
      ;(globalThis.fetch as any).mockResolvedValue(mockResponse)

      const profileData = { full_name: 'Updated Name' }
      const result = await apiService.updateProfile(profileData, 1)

      expect(globalThis.fetch).toHaveBeenCalledWith('/api/users/1/profile', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profileData),
        credentials: 'include',
      })
      expect(result.data).toEqual({ success: true })
    })
  })
})
