-- Minimal schema for RED->GREEN exercise
CREATE TABLE IF NOT EXISTS example_items (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

