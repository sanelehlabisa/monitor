CREATE TABLE monitor.meters (
    id UUID PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES monitor.users (id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT meters_name_valid CHECK (
        name = BTRIM(name) AND CHAR_LENGTH(name) BETWEEN 1 AND 80
    )
);

CREATE UNIQUE INDEX meters_user_name_unique_idx
    ON monitor.meters (user_id, LOWER(name));

CREATE INDEX meters_user_created_idx
    ON monitor.meters (user_id, created_at, id);
