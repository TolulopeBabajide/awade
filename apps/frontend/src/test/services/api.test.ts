
import { describe, it, expect, vi, beforeEach } from 'vitest'
import apiService from '../../services/api'

// Mock fetch
global.fetch = vi.fn()

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: vi.fn(() => 'test_token'),
        setItem: vi.fn(),
        removeItem: vi.fn(),
        clear: vi.fn()
      },
      writable: true
    })
  })

  describe('login', () => {
    it('should make a POST request to login endpoint', async () => {
      const mockResponse = {
        ok: true,
        url: '/api/auth/login',
        json: vi.fn().mockResolvedValue({ access_token: 'test_token' })
      }
        ; (global.fetch as any).mockResolvedValue(mockResponse)

      const result = await apiService.login('test@example.com', 'password')

      expect(global.fetch).toHaveBeenCalledWith('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'test@example.com', password: 'password' })
      })
      expect(result.data).toEqual({ access_token: 'test_token' })
    })

    it('should handle login errors', async () => {
      const mockResponse = {
        ok: false,
        status: 401,
        url: '/api/auth/login',
        statusText: 'Unauthorized',
        json: vi.fn().mockResolvedValue({ detail: 'Invalid credentials' })
      }
        ; (global.fetch as any).mockResolvedValue(mockResponse)

      const result = await apiService.login('test@example.com', 'wrong_password')

      expect(result.error).toBe('Invalid credentials')
    })
  })

  describe('signup', () => {
    it('should make a POST request to signup endpoint', async () => {
      const mockResponse = {
        ok: true,
        url: '/api/auth/signup',
        json: vi.fn().mockResolvedValue({ access_token: 'test_token' })
      }
        ; (global.fetch as any).mockResolvedValue(mockResponse)

      const userData = {
        full_name: 'Test User',
        email: 'test@example.com',
        password: 'password123'
      }

      const result = await apiService.signup(userData)

      expect(global.fetch).toHaveBeenCalledWith('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
      })
      expect(result.data).toEqual({ access_token: 'test_token' })
    })
  })

  describe('getCurrentUser', () => {
    it('should make a GET request with auth headers', async () => {
      const mockResponse = {
        ok: true,
        url: '/api/auth/me',
        json: vi.fn().mockResolvedValue({ user_id: 1, email: 'test@example.com' })
      }
        ; (global.fetch as any).mockResolvedValue(mockResponse)

      const result = await apiService.getCurrentUser()

      expect(global.fetch).toHaveBeenCalledWith('/api/auth/me', {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer test_token'
        }
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
        ; (global.fetch as any).mockResolvedValue(mockResponse)

      // Mock window.location.href
      delete (window as any).location
      window.location = { href: '' } as any

      const result = await apiService.getCurrentUser()

      expect(result.error).toBe('Session expired. Please login again.')
      expect(window.location.href).toBe('/login')
    })
  })

  describe('updateProfile', () => {
    it('should make a PUT request to profile endpoint', async () => {
      const mockResponse = {
        ok: true,
        url: '/api/users/1/profile',
        json: vi.fn().mockResolvedValue({ success: true })
      }
        ; (global.fetch as any).mockResolvedValue(mockResponse)

      const profileData = { full_name: 'Updated Name' }
      const result = await apiService.updateProfile(profileData, 1)

      expect(global.fetch).toHaveBeenCalledWith('/api/users/1/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer test_token'
        },
        body: JSON.stringify(profileData)
      })
      expect(result.data).toEqual({ success: true })
    })
  })
})
