create table if not exists tasks (
  id serial primary key,
  title text not null,
  status text not null
);

insert into tasks (title, status) values
  ('Understand Docker Compose service names', 'done'),
  ('Connect Node.js API to PostgreSQL', 'done'),
  ('Capture project evidence screenshots', 'pending');
