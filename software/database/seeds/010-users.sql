-- Fresh development and production setup only; never replay to change roles.
-- This provisions an account, not credentials or an authenticated session.
BEGIN;
INSERT INTO monitor.users (email, type) VALUES
    ('hlabisasanele730@gmail.com', 'admin');
COMMIT;
