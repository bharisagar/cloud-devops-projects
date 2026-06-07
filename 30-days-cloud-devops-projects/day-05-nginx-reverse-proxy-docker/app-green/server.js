const http = require('http');

const appName = process.env.APP_NAME || 'green';
const port = Number(process.env.PORT || 3000);

const server = http.createServer((req, res) => {
  if (req.url === '/health') {
    res.writeHead(200, { 'content-type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', app: appName }));
    return;
  }

  res.writeHead(200, { 'content-type': 'application/json' });
  res.end(JSON.stringify({
    app: appName,
    message: `Hello from ${appName} backend`,
  }));
});

server.listen(port, () => {
  console.log(`${appName} backend listening on ${port}`);
});
