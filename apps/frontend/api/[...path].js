// AWD-H-57: restrict CORS to a specific origin via env variable.
// Set ALLOWED_ORIGIN in your Vercel project settings (e.g. https://awade.app).
// If unset, the Access-Control-Allow-Origin header is omitted — same-origin
// browser requests from the Vercel frontend work fine without it.
const ALLOWED_ORIGIN = process.env.ALLOWED_ORIGIN || null;

export default async function handler(req, res) {
  // Apply CORS headers before any response (including early returns and errors).
  const requestOrigin = req.headers.origin;
  if (ALLOWED_ORIGIN && requestOrigin === ALLOWED_ORIGIN) {
    res.setHeader('Access-Control-Allow-Origin', ALLOWED_ORIGIN);
    res.setHeader('Vary', 'Origin');
  }
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  // Handle OPTIONS preflight before any async work.
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const { path } = req.query;
  const backendUrl = process.env.BACKEND_URL || 'https://awade-backend-test.onrender.com';
  const fullUrl = `${backendUrl}/api/${path.join('/')}`;

  try {
    const response = await fetch(fullUrl, {
      method: req.method,
      headers: {
        'Content-Type': req.headers['content-type'] || 'application/json',
        'Accept': req.headers['accept'] || 'application/json',
        ...(req.headers.authorization && { 'Authorization': req.headers.authorization })
      },
      body: req.method !== 'GET' && req.method !== 'HEAD' ? JSON.stringify(req.body) : undefined
    });

    const data = await response.json();
    res.status(response.status).json(data);
  } catch (error) {
    console.error('Proxy error:', error);
    // Return a generic message — never expose internal error details (OWASP A09).
    res.status(500).json({ error: 'Internal Server Error' });
  }
}
