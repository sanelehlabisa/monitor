-- Fresh development setup only. Production never mounts this seed.
-- Fictional examples belong to a separate account, never to the real admin.
BEGIN;
INSERT INTO monitor.users (email, type) VALUES
    ('monitor-seed@example.test', 'user');

INSERT INTO monitor.meters (id, user_id, name)
SELECT example.id::uuid, users.id, example.name
FROM monitor.users AS users
CROSS JOIN (VALUES
    ('58000000-0000-4000-8000-000000000001', 'Seed home'),
    ('58000000-0000-4000-8000-000000000002', 'Seed shop')
) AS example(id, name)
WHERE users.email = 'monitor-seed@example.test';

INSERT INTO monitor.user_meters (user_id, meter_id)
SELECT meters.user_id, meters.id
FROM monitor.meters AS meters
JOIN monitor.users AS users ON users.id = meters.user_id
WHERE users.email = 'monitor-seed@example.test'
  AND meters.id IN (
    '58000000-0000-4000-8000-000000000001',
    '58000000-0000-4000-8000-000000000002'
  );

INSERT INTO monitor.balance_entries (id, meter_id, balance_kwh, occurred_at) VALUES
    ('58000000-0000-4000-8000-000000000011', '58000000-0000-4000-8000-000000000001', 240, CURRENT_TIMESTAMP - INTERVAL '14 days'),
    ('58000000-0000-4000-8000-000000000012', '58000000-0000-4000-8000-000000000001', 210, CURRENT_TIMESTAMP - INTERVAL '1 day'),
    ('58000000-0000-4000-8000-000000000021', '58000000-0000-4000-8000-000000000002', 180, CURRENT_TIMESTAMP - INTERVAL '14 days'),
    ('58000000-0000-4000-8000-000000000022', '58000000-0000-4000-8000-000000000002', 165, CURRENT_TIMESTAMP - INTERVAL '1 day');

INSERT INTO monitor.top_up_entries (id, meter_id, top_up_kwh, occurred_at) VALUES
    ('58000000-0000-4000-8000-000000000031', '58000000-0000-4000-8000-000000000001', 100, CURRENT_TIMESTAMP - INTERVAL '7 days'),
    ('58000000-0000-4000-8000-000000000032', '58000000-0000-4000-8000-000000000002', 50, CURRENT_TIMESTAMP - INTERVAL '7 days');
-- No reminder rows: defaults remain disabled, and no mail is sent by setup.
COMMIT;
