import http from 'http';
import fs from 'fs';
import path from 'path';

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.url === '/' || req.url === '/index.html') {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(`
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI-Seed Frontend</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; }
        .status { background: #e8f5e8; padding: 10px; border-radius: 4px; margin: 10px 0; }
        .api-test { background: #f0f0f0; padding: 15px; border-radius: 4px; margin: 10px 0; }
        button { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin: 5px; }
        button:hover { background: #2980b9; }
        .result { margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 4px; font-family: monospace; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌱 AI-Seed Frontend</h1>
        <div class="status">
            <strong>Status:</strong> Frontend service is running!
        </div>
        
        <div class="api-test">
            <h3>API Connectivity Tests</h3>
            <button onclick="testAPI()">Test API Health</button>
            <button onclick="testAI()">Test AI Engine</button>
            <div id="results"></div>
        </div>
        
        <div class="api-test">
            <h3>System Information</h3>
            <p><strong>Environment:</strong> Development</p>
            <p><strong>API URL:</strong> ${process.env.API_URL || 'http://localhost:8000'}</p>
            <p><strong>AI Engine URL:</strong> ${process.env.AI_ENGINE_URL || 'http://localhost:5001'}</p>
        </div>
    </div>

    <script>
        async function testAPI() {
            try {
                const response = await fetch('/api/health');
                const data = await response.json();
                document.getElementById('results').innerHTML = '<div class="result"><strong>API Health:</strong> ' + JSON.stringify(data, null, 2) + '</div>';
            } catch (error) {
                document.getElementById('results').innerHTML = '<div class="result"><strong>API Error:</strong> ' + error.message + '</div>';
            }
        }

        async function testAI() {
            try {
                const response = await fetch('/ai/health');
                const data = await response.json();
                document.getElementById('results').innerHTML = '<div class="result"><strong>AI Engine Health:</strong> ' + JSON.stringify(data, null, 2) + '</div>';
            } catch (error) {
                document.getElementById('results').innerHTML = '<div class="result"><strong>AI Engine Error:</strong> ' + error.message + '</div>';
            }
        }
    </script>
</body>
</html>
    `);
  } else if (req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      status: 'healthy',
      service: 'frontend',
      timestamp: new Date().toISOString(),
      uptime: process.uptime()
    }));
  } else {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('Not Found');
  }
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 AI-Seed Frontend server running on http://0.0.0.0:${PORT}`);
  console.log(`📱 Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`🔗 API URL: ${process.env.API_URL || 'http://localhost:8000'}`);
  console.log(`🤖 AI Engine URL: ${process.env.AI_ENGINE_URL || 'http://localhost:5001'}`);
});
