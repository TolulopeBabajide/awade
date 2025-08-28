#!/usr/bin/env node

// Test Configuration Script for Awade
console.log('🧪 Testing Awade Configuration...\n');

// Test backend connectivity
const testBackend = async () => {
  try {
    console.log('🔍 Testing backend connectivity...');
    
    const healthResponse = await fetch('https://awade-backend-test.onrender.com/health');
    const healthData = await healthResponse.json();
    
    console.log('✅ Health check:', healthData);
    
    const rootResponse = await fetch('https://awade-backend-test.onrender.com/');
    const rootData = await rootResponse.json();
    
    console.log('✅ Root endpoint:', rootData);
    
    // Test CORS
    const corsResponse = await fetch('https://awade-backend-test.onrender.com/health', {
      method: 'OPTIONS',
      headers: {
        'Origin': 'https://awade-test.vercel.app',
        'Access-Control-Request-Method': 'GET'
      }
    });
    
    console.log('✅ CORS preflight:', corsResponse.status);
    
  } catch (error) {
    console.error('❌ Backend test failed:', error.message);
  }
};

// Test environment variables
const testEnvVars = () => {
  console.log('\n🔍 Testing environment variables...');
  
  const envVars = [
    'NODE_ENV',
    'VITE_API_BASE_URL', 
    'VITE_BACKEND_URL',
    'VITE_ENVIRONMENT'
  ];
  
  envVars.forEach(varName => {
    const value = process.env[varName];
    console.log(`  ${varName}: ${value || '❌ Not set'}`);
  });
};

// Run tests
const runTests = async () => {
  await testBackend();
  testEnvVars();
  
  console.log('\n🎯 Configuration Summary:');
  console.log('  Backend: https://awade-backend-test.onrender.com');
  console.log('  Frontend: https://awade-test.vercel.app');
  console.log('  Environment: Testing');
  
  console.log('\n📋 Next Steps:');
  console.log('  1. Ensure Vercel has the correct environment variables');
  console.log('  2. Deploy with: npm run build:vercel');
  console.log('  3. Test the deployed frontend');
};

runTests().catch(console.error);
