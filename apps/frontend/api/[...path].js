// Vercel Serverless Function for API Proxy
export default async function handler(req, res) {
  // Get the origin from the request
  const origin = req.headers.origin || req.headers.referer;
  
  // Define allowed origins for security
  const allowedOrigins = [
    'https://awade-test.vercel.app',
    'https://awade.vercel.app',
    'http://localhost:3000',
    'http://localhost:5173'
  ];
  
  // Check if origin is allowed
  const isAllowedOrigin = allowedOrigins.some(allowed => 
    origin && origin.includes(allowed)
  );
  
  // Set CORS headers based on origin
  if (isAllowedOrigin) {
    res.setHeader('Access-Control-Allow-Origin', origin);
  } else {
    res.setHeader('Access-Control-Allow-Origin', 'https://awade-test.vercel.app');
  }
  
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.setHeader('Access-Control-Max-Age', '3600'); // Cache preflight for 1 hour

  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  // Get the path from the URL
  const path = req.url.replace('/api/', '').split('/');
  
  // Validate path for security
  if (!path || path.length === 0 || path.some(segment => !segment || segment.includes('..'))) {
    return res.status(400).json({ error: 'Invalid API path' });
  }
  
  const backendUrl = 'https://awade-backend-test.onrender.com';
  
  // Construct the full URL
  const fullUrl = `${backendUrl}/api/${path.join('/')}`;
  
  // Validate URL for security
  if (!fullUrl.startsWith(backendUrl)) {
    return res.status(400).json({ error: 'Invalid backend URL' });
  }
  
  console.log(`🚀 API Proxy: ${req.method} ${req.url} -> ${fullUrl}`);
  
  try {
    // Prepare headers for backend request
    const headers = {
      'Content-Type': req.headers['content-type'] || 'application/json',
      'Accept': req.headers['accept'] || 'application/json',
    };

    // Add authorization header if present
    if (req.headers.authorization) {
      headers['Authorization'] = req.headers.authorization;
    }

    // Prepare request options
    const requestOptions = {
      method: req.method,
      headers,
    };

    // Add body for non-GET requests
    if (req.method !== 'GET' && req.method !== 'HEAD' && req.body) {
      // Check request size limit (10MB)
      const contentLength = req.headers['content-length'];
      if (contentLength && parseInt(contentLength) > 10 * 1024 * 1024) {
        return res.status(413).json({ error: 'Request too large' });
      }
      
      requestOptions.body = JSON.stringify(req.body);
    }

    // Forward the request to the backend
    const response = await fetch(fullUrl, requestOptions);
    
    console.log(`📡 Backend response: ${response.status} ${response.statusText}`);
    
    // Get the response data
    let data;
    const contentType = response.headers.get('content-type');
    
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }
    
    // Return the response with the same status code
    res.status(response.status).json(data);
  } catch (error) {
    console.error('❌ Proxy error:', error);
    
    // Secure error response - don't expose internal details in production
    const isProduction = process.env.NODE_ENV === 'production';
    
    res.status(500).json({ 
      error: 'Internal Server Error',
      ...(isProduction ? {} : {
        details: error.message,
        path: req.url,
        method: req.method
      })
    });
  }
}
