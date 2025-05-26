CREATE TABLE IF NOT EXISTS items (
    id VARCHAR PRIMARY KEY,
    s3_name VARCHAR NOT NULL,
    type VARCHAR(10) NOT NULL, /*image or video*/
    upload_dt TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    item_id VARCHAR NOT NULL,
    interaction_dt TIMESTAMPTZ NOT NULL,
    FOREIGN KEY (item_id) REFERENCES items(id)
);

CREATE INDEX IF NOT EXISTS idx_interactions_user_id ON interactions (user_id);