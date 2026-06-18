CREATE TABLE IF NOT EXISTS healthcheck (
  id integer PRIMARY KEY,
  created_at timestamptz DEFAULT now()
);
