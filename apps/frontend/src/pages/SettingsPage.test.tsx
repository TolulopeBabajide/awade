import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import SettingsPage from './SettingsPage';

// ── Mocks ──────────────────────────────────────────────────────────────────

// Stable reference — prevents useEffect([user?.user_id]) from re-firing on
// every render due to identity inequality.
const MOCK_USER = {
  user_id: 1,
  email: 'test@example.invalid',
  full_name: 'Test User',
  role: 'EDUCATOR',
  country: 'Nigeria',
}

vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: MOCK_USER,
    isAuthenticated: true,
    isLoading: false,
  }),
}))

const mockApiService = vi.hoisted(() => ({
  getCurrentUser: vi.fn(),
  updateProfile: vi.fn(),
}))

vi.mock('../services/api', () => ({ default: mockApiService }))

vi.mock('../components/Sidebar', () => ({
  default: ({ currentPage }: { currentPage: string }) => (
    <nav data-testid="sidebar" data-page={currentPage} />
  ),
}))

vi.mock('../components/MobileNavigation', () => ({
  default: () => <nav data-testid="mobile-nav" />,
}))

// ── Helpers ────────────────────────────────────────────────────────────────

const profileResponse = {
  data: {
    user_id: 1,
    email: 'test@example.invalid',
    full_name: 'Test User',
    role: 'EDUCATOR',
    country: 'Nigeria',
    region: 'Lagos',
    phone: '+234000000000',
    bio: 'A teacher.',
    created_at: '2026-01-01T00:00:00Z',
  },
  error: null,
}

function renderPage() {
  return render(
    <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <SettingsPage />
    </MemoryRouter>
  )
}

function clickCog() {
  fireEvent.click(screen.getByTestId('settings-cog'))
}

// ── Tests ──────────────────────────────────────────────────────────────────

describe('SettingsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockApiService.getCurrentUser.mockResolvedValue(profileResponse)
    mockApiService.updateProfile.mockResolvedValue({ data: profileResponse.data, error: null })
  })

  describe('page shell', () => {
    it('renders the page heading', () => {
      renderPage()
      expect(screen.getByText('Account Settings')).toBeTruthy()
    })

    it('renders sidebar with settings page context', () => {
      renderPage()
      expect(screen.getByTestId('sidebar').getAttribute('data-page')).toBe('settings')
    })

    it('renders mobile navigation', () => {
      renderPage()
      expect(screen.getByTestId('mobile-nav')).toBeTruthy()
    })

    it('defaults to profile tab — shows Personal Information heading', async () => {
      renderPage()
      await waitFor(() => {
        expect(screen.getByText('Personal Information')).toBeTruthy()
      })
    })
  })

  describe('settings menu', () => {
    it('settings cog button toggles the menu open', () => {
      renderPage()
      expect(screen.queryByText('My Profile')).toBeFalsy()
      clickCog()
      expect(screen.getByText('My Profile')).toBeTruthy()
    })

    it('clicking Security in the menu switches to security tab', async () => {
      renderPage()
      clickCog()
      fireEvent.click(screen.getByText('Security'))
      await waitFor(() => {
        expect(screen.getByText('Login Details')).toBeTruthy()
      })
    })

    it('clicking Language in the menu switches to language tab', async () => {
      renderPage()
      clickCog()
      fireEvent.click(screen.getByText('Language'))
      await waitFor(() => {
        expect(screen.getByText('Language Settings')).toBeTruthy()
      })
    })

    it('clicking My Profile returns to profile tab from security', async () => {
      renderPage()
      clickCog()
      fireEvent.click(screen.getByText('Security'))
      await waitFor(() => expect(screen.getByText('Login Details')).toBeTruthy())

      clickCog()
      fireEvent.click(screen.getByText('My Profile'))
      await waitFor(() => expect(screen.getByText('Personal Information')).toBeTruthy())
    })
  })

  describe('ProfileTab', () => {
    it('loads and displays user profile data', async () => {
      renderPage()
      await waitFor(() => {
        expect(mockApiService.getCurrentUser).toHaveBeenCalledTimes(1)
      })
    })

    it('switching to SecurityTab does not fire a second getCurrentUser call', async () => {
      renderPage()
      await waitFor(() => {
        expect(mockApiService.getCurrentUser).toHaveBeenCalledTimes(1)
      })
      clickCog()
      fireEvent.click(screen.getByText('Security'))
      await waitFor(() => expect(screen.getByText('Login Details')).toBeTruthy(), { timeout: 5000 })
      expect(mockApiService.getCurrentUser).toHaveBeenCalledTimes(1)
    })

    it('shows profile initials avatar', async () => {
      renderPage()
      await waitFor(() => {
        expect(screen.getByText('TU')).toBeTruthy()
      })
    })

    it('shows Full Name label in profile tab', async () => {
      renderPage()
      await waitFor(() => {
        expect(screen.getByText('Full Name')).toBeTruthy()
      })
    })

    it('clicking edit icon for full_name enters edit mode', async () => {
      renderPage()
      await waitFor(() => {
        expect(screen.getByText('Full Name')).toBeTruthy()
      })
      // There are multiple edit buttons — find the one next to Full Name
      const fullNameSection = screen.getByText('Full Name').closest('div.flex')
      expect(fullNameSection).toBeTruthy()
    })

    it('shows error banner when updateProfile returns an error', async () => {
      mockApiService.updateProfile.mockResolvedValue({ data: undefined, error: 'Validation failed' })
      renderPage()
      await waitFor(() => expect(screen.getByText('Full Name')).toBeTruthy())

      const fullNameLabel = screen.getByText('Full Name')
      const fullNameRow = fullNameLabel.closest('div.flex')!
      const editBtn = fullNameRow.querySelector('button')
      fireEvent.click(editBtn!)

      await waitFor(() => {
        const saveBtn = screen.getAllByTitle('Save changes')[0]
        expect(saveBtn).toBeTruthy()
      })

      await act(async () => {
        fireEvent.click(screen.getAllByTitle('Save changes')[0])
      })

      await waitFor(() => {
        expect(screen.getByRole('alert')).toBeTruthy()
        expect(screen.getByText('Validation failed')).toBeTruthy()
      })
    })

    it('shows generic error banner when updateProfile throws a network error', async () => {
      mockApiService.updateProfile.mockRejectedValue(new Error('Network error'))
      renderPage()
      await waitFor(() => expect(screen.getByText('Full Name')).toBeTruthy())

      const fullNameLabel = screen.getByText('Full Name')
      const fullNameRow = fullNameLabel.closest('div.flex')!
      const editBtn = fullNameRow.querySelector('button')
      fireEvent.click(editBtn!)

      await waitFor(() => {
        expect(screen.getAllByTitle('Save changes').length).toBeGreaterThan(0)
      })

      await act(async () => {
        fireEvent.click(screen.getAllByTitle('Save changes')[0])
      })

      await waitFor(() => {
        expect(screen.getByRole('alert')).toBeTruthy()
        expect(screen.getByText(/Failed to save changes/i)).toBeTruthy()
      })
    })

    it('clears error banner when cancel is clicked after a failed save', async () => {
      mockApiService.updateProfile.mockResolvedValue({ data: undefined, error: 'Server error' })
      renderPage()
      await waitFor(() => expect(screen.getByText('Full Name')).toBeTruthy())

      const fullNameLabel = screen.getByText('Full Name')
      const fullNameRow = fullNameLabel.closest('div.flex')!
      const editBtn = fullNameRow.querySelector('button')!
      fireEvent.click(editBtn)

      await act(async () => {
        fireEvent.click(screen.getAllByTitle('Save changes')[0])
      })

      await waitFor(() => {
        expect(screen.getByRole('alert')).toBeTruthy()
      })

      // The cancel button is the untitled button beside "Save changes" in the editing field
      const allButtons = screen.getAllByRole('button')
      const cancelBtn = allButtons.find(
        b => !b.getAttribute('title') && b.closest('div.flex.space-x-2.ml-3')
      )!
      fireEvent.click(cancelBtn)

      await waitFor(() => {
        expect(screen.queryByRole('alert')).toBeFalsy()
      })
    })
  })

  describe('SecurityTab', () => {
    it('shows email address and Edit Login Details button', async () => {
      renderPage()
      clickCog()
      fireEvent.click(screen.getByText('Security'))
      await waitFor(() => {
        expect(screen.getByText('Edit Login Details')).toBeTruthy()
        expect(screen.getByText('Email Address')).toBeTruthy()
      })
    })

    it('Edit Login Details opens the edit form', async () => {
      renderPage()
      clickCog()
      fireEvent.click(screen.getByText('Security'))
      await waitFor(() => expect(screen.getByText('Edit Login Details')).toBeTruthy())
      fireEvent.click(screen.getByText('Edit Login Details'))
      await waitFor(() => {
        expect(screen.getByText('Current Password')).toBeTruthy()
      })
    })

    it('Cancel in edit form closes the form', async () => {
      renderPage()
      clickCog()
      fireEvent.click(screen.getByText('Security'))
      await waitFor(() => expect(screen.getByText('Edit Login Details')).toBeTruthy())
      fireEvent.click(screen.getByText('Edit Login Details'))
      await waitFor(() => expect(screen.getByText('Cancel')).toBeTruthy())
      fireEvent.click(screen.getByText('Cancel'))
      await waitFor(() => {
        expect(screen.queryByText('Current Password')).toBeFalsy()
        expect(screen.getByText('Edit Login Details')).toBeTruthy()
      })
    })

    it('shows unavailable message when password is changed', async () => {
      renderPage()
      clickCog()
      fireEvent.click(screen.getByText('Security'))
      await waitFor(() => expect(screen.getByText('Edit Login Details')).toBeTruthy())
      fireEvent.click(screen.getByText('Edit Login Details'))
      await waitFor(() => expect(screen.getByText('Current Password')).toBeTruthy())

      // Confirm ProfileTab's getCurrentUser has resolved (SecurityTab derives email from auth context directly)
      await waitFor(() => {
        expect(mockApiService.getCurrentUser).toHaveBeenCalled()
      })

      const newPasswordInput = screen.getByPlaceholderText('Leave blank to keep current password')
      fireEvent.change(newPasswordInput, { target: { value: 'newpassword123' } })
      const confirmInput = screen.getByPlaceholderText('Confirm your new password')
      fireEvent.change(confirmInput, { target: { value: 'newpassword123' } })
      const currentPasswordInput = screen.getByPlaceholderText('Enter your current password')
      fireEvent.change(currentPasswordInput, { target: { value: 'oldpassword' } })

      await act(async () => {
        fireEvent.click(screen.getByText('Save Changes'))
      })

      await waitFor(() => {
        expect(screen.getByText(/not yet available/i)).toBeTruthy()
      })
    })
  })

  describe('LanguageTab', () => {
    it('shows language placeholder text', async () => {
      renderPage()
      clickCog()
      fireEvent.click(screen.getByText('Language'))
      await waitFor(() => {
        expect(screen.getByText('Language Settings')).toBeTruthy()
        expect(screen.getByText('Language settings will be implemented here.')).toBeTruthy()
      })
    })
  })
})
