const http = require('http');

const port = Number(process.env.PORT || 3000);

const server = http.createServer((req, res) => {
  if (req.url === '/health') {
    res.writeHead(200, { 'content-type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok' }));
    return;
  }

  res.writeHead(200, { 'content-type': 'application/json' });
  res.end(JSON.stringify({
    service: 'private-vpc-ecs-demo',
    message: 'ECS Fargate task is running in a private subnet.',
    timestamp: new Date().toISOString(),
  }));
});

server.listen(port, () => {
  console.log(`private-vpc-ecs-demo listening on ${port}`);
});
