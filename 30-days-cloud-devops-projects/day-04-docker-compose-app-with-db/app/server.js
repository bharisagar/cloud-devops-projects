const http = require('http');
const { Client } = require('pg');

const port = Number(process.env.PORT || 3000);

const dbConfig = {
  host: process.env.DB_HOST || 'db',
  port: Number(process.env.DB_PORT || 5432),
  user: process.env.DB_USER || 'devops',
  password: process.env.DB_PASSWORD || 'devops_password',
  database: process.env.DB_NAME || 'devops_tasks',
};

async function queryTasks() {
  const client = new Client(dbConfig);
  await client.connect();
  const result = await client.query('select id, title, status from tasks order by id');
  await client.end();
  return result.rows;
}

function sendJson(res, statusCode, payload) {
  res.writeHead(statusCode, { 'content-type': 'application/json' });
  res.end(JSON.stringify(payload, null, 2));
}

const server = http.createServer(async (req, res) => {
  try {
    if (req.url === '/health') {
      sendJson(res, 200, { status: 'ok', service: 'day-04-compose-api' });
      return;
    }

    if (req.url === '/tasks') {
      const tasks = await queryTasks();
      sendJson(res, 200, { tasks });
      return;
    }

    sendJson(res, 200, {
      message: 'Day 4 app is running. Open /tasks to verify database connectivity.',
      databaseHost: dbConfig.host,
    });
  } catch (error) {
    sendJson(res, 500, {
      error: 'Database query failed',
      detail: error.message,
    });
  }
});

server.listen(port, () => {
  console.log(`day-04-compose-api listening on ${port}`);
});
