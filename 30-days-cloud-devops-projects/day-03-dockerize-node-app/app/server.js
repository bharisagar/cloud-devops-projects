const http = require('http');
const os = require('os');

const port = Number(process.env.PORT || 3000);

const server = http.createServer((req, res) => {
  if (req.url === '/health') {
    res.writeHead(200, { 'content-type': 'application/json' });
    res.end(JSON.stringify({
      status: 'ok',
      service: 'day-03-node-api',
    }));
    return;
  }

  res.writeHead(200, { 'content-type': 'application/json' });
  res.end(JSON.stringify({
    message: 'Hello from Day 3 Dockerized Node.js app',
    hostname: os.hostname(),
    port,
  }));
});

server.listen(port, () => {
  console.log(`day-03-node-api listening on port ${port}`);
});
