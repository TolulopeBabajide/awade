import { useLayoutEffect, useRef, useState } from 'react';
import { GoogleLogin, type CredentialResponse } from '@react-oauth/google';

export const googleAuthClientId = (import.meta.env.VITE_GOOGLE_CLIENT_ID || '').trim();
export const isGoogleAuthConfigured = googleAuthClientId.length > 0;

interface ResponsiveGoogleLoginProps {
  onSuccess: (credentialResponse: CredentialResponse) => void | Promise<void>;
  onError: () => void;
}

const ResponsiveGoogleLogin = ({ onSuccess, onError }: ResponsiveGoogleLoginProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(0);

  useLayoutEffect(() => {
    if (!isGoogleAuthConfigured) return;

    const container = containerRef.current;
    if (!container) return;

    const updateWidth = () => setWidth(Math.floor(container.getBoundingClientRect().width));
    updateWidth();

    if (typeof ResizeObserver === 'undefined') {
      window.addEventListener('resize', updateWidth);
      return () => window.removeEventListener('resize', updateWidth);
    }

    const observer = new ResizeObserver(updateWidth);
    observer.observe(container);
    return () => observer.disconnect();
  }, []);

  if (!isGoogleAuthConfigured) return null;

  return (
    <div ref={containerRef} className="min-h-10 w-full overflow-hidden" data-testid="google-login-container">
      {width > 0 && (
        <GoogleLogin
          onSuccess={onSuccess}
          onError={onError}
          width={String(width)}
          useOneTap
        />
      )}
    </div>
  );
};

export default ResponsiveGoogleLogin;
