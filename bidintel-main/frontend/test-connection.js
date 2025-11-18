/**
 * Test script to verify frontend-backend connection
 * Run with: node test-connection.js
 */

const API_URL = process.env.VITE_API_URL || 'http://localhost:8000/api';
const BASE_URL = API_URL.replace('/api', '');

async function testEndpoint(name, url) {
  try {
    const response = await fetch(url);
    const data = await response.json();

    if (response.ok) {
      console.log(`✅ ${name}: SUCCESS`);
      console.log(`   Status: ${response.status}`);
      console.log(`   Data:`, JSON.stringify(data, null, 2).substring(0, 200) + '...\n');
      return true;
    } else {
      console.log(`❌ ${name}: FAILED`);
      console.log(`   Status: ${response.status}`);
      console.log(`   Error:`, data);
      return false;
    }
  } catch (error) {
    console.log(`❌ ${name}: ERROR`);
    console.log(`   ${error.message}\n`);
    return false;
  }
}

async function main() {
  console.log('='.repeat(60));
  console.log('Frontend-Backend Connection Test');
  console.log('='.repeat(60));
  console.log(`Backend URL: ${BASE_URL}`);
  console.log(`API URL: ${API_URL}\n`);

  let passed = 0;
  let total = 0;

  // Test 1: Health check
  total++;
  if (await testEndpoint('Health Check', `${BASE_URL}/health`)) passed++;

  // Test 2: Root endpoint
  total++;
  if (await testEndpoint('Root Endpoint', `${BASE_URL}/`)) passed++;

  // Test 3: Stats endpoint
  total++;
  if (await testEndpoint('Stats Endpoint', `${API_URL}/stats`)) passed++;

  // Test 4: Bids endpoint
  total++;
  if (await testEndpoint('Bids Endpoint', `${API_URL}/bids?limit=1`)) passed++;

  // Test 5: Analytics endpoint
  total++;
  if (await testEndpoint('Analytics Endpoint', `${API_URL}/analytics?time_range=7d`)) passed++;

  console.log('='.repeat(60));
  console.log(`Results: ${passed}/${total} tests passed`);
  console.log('='.repeat(60));

  if (passed === total) {
    console.log('✅ All tests passed! Frontend can connect to backend.');
    process.exit(0);
  } else {
    console.log('❌ Some tests failed. Check the backend is running on port 8000.');
    process.exit(1);
  }
}

main();
