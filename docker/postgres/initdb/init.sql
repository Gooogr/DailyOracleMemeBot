CREATE TABLE IF NOT EXISTS items (
    id VARCHAR PRIMARY KEY,
    type VARCHAR(10) NOT NULL,
    upload_dt TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS interactions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    item_id VARCHAR NOT NULL,
    interaction_dt TIMESTAMPTZ NOT NULL,
    FOREIGN KEY (item_id) REFERENCES items(id)
);

CREATE INDEX IF NOT EXISTS idx_interactions_user_id ON interactions (user_id);