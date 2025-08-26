import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.tsx'
import './index.css'
import { GoogleOAuthProvider } from '@react-oauth/google';

// Get Google OAuth client ID from environment variables
const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

// Check if the app can mount
if (!googleClientId) {
  console.warn('VITE_GOOGLE_CLIENT_ID is not set. Google OAuth will not work, but the app should still function.');
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <GoogleOAuthProvider clientId={googleClientId || 'placeholder-client-id'}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </GoogleOAuthProvider>
  </React.StrictMode>,
) 