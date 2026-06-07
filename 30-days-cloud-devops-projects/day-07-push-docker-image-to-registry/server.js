const http = require('http');
const os = require('os');

const port = Number(process.env.PORT || 3000);
const imageTag = process.env.IMAGE_TAG || 'local';

const server = http.createServer((req, res) => {
  if (req.url === '/health') {
    res.writeHead(200, { 'content-type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', service: 'day-07-registry-api' }));
    return;
  }

  res.writeHead(200, { 'content-type': 'application/json' });
  res.end(JSON.stringify({
    message: 'Day 7 app is running from a Docker image',
    hostname: os.hostname(),
    imageTag,
  }));
});

server.listen(port, () => {
  console.log(`day-07-registry-api listening on ${port}`);
});
