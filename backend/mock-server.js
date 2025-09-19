import http from 'http';
import url from 'url';

const subjects = [
  { id: 1, name: 'Listening', target_score: 400, current_score: 340 },
  { id: 2, name: 'Reading', target_score: 400, current_score: 310 }
];

const server = http.createServer((req, res) => {
  const parsed = url.parse(req.url, true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    return res.end();
  }

  if (parsed.pathname === '/api/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    return res.end(JSON.stringify({ status: 'healthy', service: 'mock-backend' }));
  }

  if (parsed.pathname === '/api/mastery/get-subjects') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    return res.end(JSON.stringify({ subjects }));
  }

  // Generic fallback for /api
  if (parsed.pathname.startsWith('/api')) {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    return res.end(JSON.stringify({ message: 'mock response', path: parsed.pathname }));
  }

  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'not found' }));
});

const PORT = process.env.PORT || 5000;
server.listen(PORT, () => {
  console.log(`Mock backend listening on http://localhost:${PORT}`);
});
