const assert = require('assert');
const { createServer } = require('../server');

async function main() {
  const server = createServer();

  await new Promise((resolve) => {
    server.listen(0, '127.0.0.1', resolve);
  });

  const { port } = server.address();
  const response = await fetch(`http://127.0.0.1:${port}/health`);
  const body = await response.json();

  assert.strictEqual(response.status, 200);
  assert.strictEqual(body.status, 'ok');
  assert.strictEqual(body.service, 'day-06-ci-api');

  await new Promise((resolve) => server.close(resolve));
  console.log('health test passed');
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
