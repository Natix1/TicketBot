CREATE TABLE IF NOT EXISTS tickets (
    ticket_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id  BIGINT NOT NULL,
    creator_id  BIGINT NOT NULL,
    claimed_by  BIGINT,
    status      TEXT NOT NULL DEFAULT 'open',
    reason      TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS greetings (
    user_id   BIGINT PRIMARY KEY,
    greeting  TEXT NOT NULL DEFAULT 'Hello, how can I assist you today?'
);

CREATE TABLE IF NOT EXISTS transcripts (
    creator_id BIGINT NOT NULL,
    url VARCHAR(255) NOT NULL,
    reason TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)