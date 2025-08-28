#!/usr/bin/env node

// Test Frontend Configuration for Awade
console.log('🧪 Testing Frontend Configuration...\n');

// Test environment variables
console.log('🔍 Environment Variables:');
const envVars = [
  'NODE_ENV',
  'VITE_ENVIRONMENT',
  'VITE_API_BASE_URL',
  'VITE_BACKEND_URL'
];

envVars.forEach(varName => {
  const value = process.env[varName];
  console.log(`  ${varName}: ${value || '❌ Not set'}`);
});

// Test API connectivity
const testApiConnectivity = async () => {
  try {
    console.log('\n🌐 Testing API Connectivity...');
    
    // Test backend health
    const healthResponse = await fetch('https://awade-backend-test.onrender.com/health');
    const healthData = await healthResponse.json();
    console.log('✅ Backend Health:', healthData);
    
    // Test signup endpoint
    const signupData = {
      email: `test${Date.now()}@example.com`,
      password: 'TestPassword123',
      full_name: 'Test User',
      role: 'EDUCATOR',
      country: 'Nigeria'
    };
    
    console.log('📝 Testing signup with data:', { ...signupData, password: '[REDACTED]' });
    
    const signupResponse = await fetch('https://awade-backend-test.onrender.com/api/auth/signup', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Origin': 'https://awade-test.vercel.app'
      },
      body: JSON.stringify(signupData)
    });
    
    if (signupResponse.ok) {
      const signupResult = await signupResponse.json();
      console.log('✅ Signup successful:', { 
        user_id: signupResult.user?.user_id,
        email: signupResult.user?.email,
        has_token: !!signupResult.access_token
      });
      
      // Test login with the created user
      const loginResponse = await fetch('https://awade-backend-test.onrender.com/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Origin': 'https://awade-test.vercel.app'
        },
        body: JSON.stringify({
          email: signupData.email,
          password: signupData.password
        })
      });
      
      if (loginResponse.ok) {
        const loginResult = await loginResponse.json();
        console.log('✅ Login successful:', { 
          user_id: loginResult.user?.user_id,
          has_token: !!loginResult.access_token
        });
      } else {
        console.log('❌ Login failed:', loginResponse.status, loginResponse.statusText);
      }
      
    } else {
      const errorData = await signupResponse.json().catch(() => ({}));
      console.log('❌ Signup failed:', signupResponse.status, errorData);
    }
    
  } catch (error) {
    console.error('❌ API test failed:', error.message);
  }
};

// Test CORS
const testCORS = async () => {
  try {
    console.log('\n🔒 Testing CORS...');
    
    const corsResponse = await fetch('https://awade-backend-test.onrender.com/health', {
      method: 'OPTIONS',
      headers: {
        'Origin': 'https://awade-test.vercel.app',
        'Access-Control-Request-Method': 'GET',
        'Access-Control-Request-Headers': 'Content-Type'
      }
    });
    
    console.log('✅ CORS preflight status:', corsResponse.status);
    console.log('✅ CORS headers:', {
      'access-control-allow-origin': corsResponse.headers.get('access-control-allow-origin'),
      'access-control-allow-methods': corsResponse.headers.get('access-control-allow-methods'),
      'access-control-allow-headers': corsResponse.headers.get('access-control-allow-headers')
    });
    
  } catch (error) {
    console.error('❌ CORS test failed:', error.message);
  }
};

// Run tests
const runTests = async () => {
  await testApiConnectivity();
  await testCORS();
  
  console.log('\n🎯 Frontend Configuration Summary:');
  console.log('  Backend: https://awade-backend-test.onrender.com');
  console.log('  Frontend: https://awade-test.vercel.app');
  console.log('  Environment: Test');
  
  console.log('\n📋 Next Steps:');
  console.log('  1. Check Vercel environment variables');
  console.log('  2. Verify frontend is using correct backend URL');
  console.log('  3. Check browser console for errors');
  console.log('  4. Test login/signup in deployed frontend');
  
  console.log('\n✅ Frontend Configuration Test Complete!');
};

runTests().catch(console.error);
