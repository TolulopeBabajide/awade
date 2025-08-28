import React from 'react';

const EnvironmentDebug: React.FC = () => {
  const isTestEnvironment = import.meta.env.VITE_ENVIRONMENT === 'test' || 
                           window.location.hostname === 'awade-test.vercel.app' ||
                           window.location.hostname.includes('test');

  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api';
  const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

  return (
    <div className="fixed bottom-4 right-4 bg-gray-900 text-white p-4 rounded-lg shadow-lg text-xs max-w-sm z-50">
      <div className="font-bold mb-2">🔧 Environment Debug</div>
      <div className="space-y-1">
        <div>Hostname: {window.location.hostname}</div>
        <div>Environment: {import.meta.env.VITE_ENVIRONMENT || 'not set'}</div>
        <div>API Base: {apiBaseUrl}</div>
        <div>Backend: {backendUrl}</div>
        <div>Is Test: {isTestEnvironment ? '✅ Yes' : '❌ No'}</div>
        <div>Mode: {import.meta.env.MODE}</div>
      </div>
      <div className="mt-2 pt-2 border-t border-gray-700">
        <div className="text-yellow-300">
          {isTestEnvironment && !apiBaseUrl.includes('awade-backend-test.onrender.com') 
            ? '⚠️ Using fallback URL' 
            : '✅ Configuration OK'}
        </div>
      </div>
    </div>
  );
};

export default EnvironmentDebug;
