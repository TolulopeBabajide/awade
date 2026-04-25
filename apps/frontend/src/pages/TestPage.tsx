import React, { useState, useEffect } from 'react';
import apiService from '../services/api';

const TestPage: React.FC = () => {
  const [aiHealth, setAiHealth] = useState<any>(null);
  const [countries, setCountries] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    testApiConnection();
  }, []);

  const testApiConnection = async () => {
    setLoading(true);
    setError('');

    try {
      // Test AI health
      const healthResponse = await apiService.checkAiHealth();
      if (healthResponse.data) {
        setAiHealth(healthResponse.data);
      }

      // Test countries endpoint
      const countriesResponse = await apiService.getCountries();
      if (countriesResponse.data) {
        setCountries(countriesResponse.data);
      }

      if (healthResponse.error || countriesResponse.error) {
        setError('Some API calls failed. Check console for details.');
        console.error('Health error:', healthResponse.error);
        console.error('Countries error:', countriesResponse.error);
      }
    } catch (err: any) {
      setError(err.message || 'API test failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">API Integration Test</h1>
        
        {loading && (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto"></div>
            <p className="mt-4 text-gray-600">Testing API connection...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* AI Health Status */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">AI Service Health</h2>
            {aiHealth ? (
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Status:</span>
                  <span className={`font-medium ${aiHealth.status === 'healthy' ? 'text-green-600' : 'text-red-600'}`}>
                    {aiHealth.status}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Service:</span>
                  <span className="text-gray-900">{aiHealth.service}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Timestamp:</span>
                  <span className="text-gray-900">{new Date(aiHealth.timestamp).toLocaleString()}</span>
                </div>
              </div>
            ) : (
              <p className="text-gray-500">No health data available</p>
            )}
          </div>

          {/* Countries Data */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Countries Data</h2>
            {countries.length > 0 ? (
              <div className="space-y-2">
                <p className="text-sm text-gray-600 mb-3">Found {countries.length} countries:</p>
                {countries.map((country) => (
                  <div key={country.country_id} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                    <span className="font-medium">{country.country_name}</span>
                    <span className="text-sm text-gray-500">{country.iso_code}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No countries data available</p>
            )}
          </div>
        </div>

        <div className="mt-8">
          <button
            onClick={testApiConnection}
            disabled={loading}
            className="px-6 py-3 bg-orange-500 text-white rounded-md hover:bg-orange-600 disabled:opacity-50"
          >
            {loading ? 'Testing...' : 'Test API Connection'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default TestPage; 