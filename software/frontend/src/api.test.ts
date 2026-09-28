import { describe, expect, it, vi } from 'vitest';

import { fetchIdentity } from './api';

describe('Monitor API client', () => {
  it('sends the access token and returns validated identity data', async () => {
    const request = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          sub: 'development-user-id',
          username: 'monitor.developer',
          email: 'developer@example.test',
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      ),
    );

    await expect(
      fetchIdentity('access-token', 'http://api.test', request),
    ).resolves.toMatchObject({ username: 'monitor.developer' });
    expect(request).toHaveBeenCalledWith('http://api.test/auth/me', {
      headers: { Authorization: 'Bearer access-token' },
    });
  });

  it('rejects an unsuccessful identity response', async () => {
    const request = vi.fn().mockResolvedValue(new Response(null, { status: 401 }));

    await expect(fetchIdentity('bad-token', 'http://api.test', request)).rejects.toThrow(
      'Identity request failed with HTTP 401',
    );
  });
});
