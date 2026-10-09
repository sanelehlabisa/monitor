CREATE TABLE monitor.user_sessions (
    id UUID PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES monitor.users(id) ON DELETE CASCADE,
    token_digest TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    CONSTRAINT user_sessions_digest_is_sha256_hex CHECK (
        token_digest ~ '^[0-9a-f]{64}$'
    ),
    CONSTRAINT user_sessions_expiry_after_creation CHECK (
        expires_at > created_at
    ),
    CONSTRAINT user_sessions_revocation_after_creation CHECK (
        revoked_at IS NULL OR revoked_at >= created_at
    )
);

CREATE INDEX user_sessions_user_created_idx
    ON monitor.user_sessions (user_id, created_at DESC);
