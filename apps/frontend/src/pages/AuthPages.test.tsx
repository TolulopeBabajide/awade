import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import LoginPage from './LoginPage';
import SignupPage from './SignupPage';
import LegalPage from './LegalPage';

const login = vi.fn();
const signup = vi.fn();
const googleAuth = vi.fn();

vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({ login, signup, googleAuth }),
}));

vi.mock('../components/ResponsiveGoogleLogin', () => ({
  default: () => null,
  isGoogleAuthConfigured: false,
}));

describe('authentication pages', () => {
  beforeEach(() => {
    login.mockReset();
    signup.mockReset();
    googleAuth.mockReset();
  });

  it('uses inclusive copy and falls back cleanly when Google auth is not configured', () => {
    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>,
    );

    expect(screen.getByText('Learning support for home and school')).toBeInTheDocument();
    expect(screen.getByText('Continue helping learners at home or in the classroom')).toBeInTheDocument();
    expect(screen.queryByText(/Sign in with Google/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/or continue with email/i)).not.toBeInTheDocument();
  });

  it('exposes role selection semantics and real legal routes', async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter initialEntries={['/signup']}>
        <Routes>
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/terms" element={<LegalPage kind="terms" />} />
          <Route path="/privacy-policy" element={<LegalPage kind="privacy" />} />
        </Routes>
      </MemoryRouter>,
    );

    const parentRole = screen.getByRole('radio', { name: /Parent/i });
    const educatorRole = screen.getByRole('radio', { name: /Educator/i });
    expect(parentRole).toHaveAttribute('aria-checked', 'false');
    expect(educatorRole).toHaveAttribute('aria-checked', 'false');

    await user.click(parentRole);
    expect(parentRole).toHaveAttribute('aria-checked', 'true');

    const termsLink = screen.getByRole('link', { name: 'Terms & Conditions' });
    const privacyLink = screen.getByRole('link', { name: 'Privacy Policy' });
    expect(termsLink).toHaveAttribute('href', '/terms');
    expect(privacyLink).toHaveAttribute('href', '/privacy-policy');

    await user.click(termsLink);
    expect(screen.getByRole('heading', { name: 'Terms & Conditions' })).toBeInTheDocument();
  });

  it('uses the in-card error treatment instead of native validation popovers', async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <SignupPage />
      </MemoryRouter>,
    );

    const submitButton = screen.getByRole('button', { name: 'Create Account' });
    expect(submitButton.closest('form')).toHaveAttribute('novalidate');

    await user.click(submitButton);

    expect(screen.getByRole('alert')).toHaveTextContent('All fields are required.');
    expect(signup).not.toHaveBeenCalled();
  });

  it('associates visible labels with login fields', () => {
    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>,
    );

    expect(screen.getByLabelText('Email Address')).toHaveAttribute('id', 'login-email');
    expect(screen.getByLabelText('Password')).toHaveAttribute('id', 'login-password');
  });
});
