-- Base seed data (idempotent demo)
INSERT INTO example_items (name)
SELECT 'ping'
WHERE NOT EXISTS (SELECT 1 FROM example_items WHERE name = 'ping');

