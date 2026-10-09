import { afterEach, describe, expect, it, vi } from 'vitest';

import { getCurrentUser, logout, requestOtp, verifyOtp } from './api';

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('authentication API client', () => {
  it('requests and verifies codes with cookie credentials', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ message: 'accepted' }), { status: 202 }),
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ id: 7, email: 'user@example.test' }), {
          status: 200,
        }),
      );
    vi.stubGlobal('fetch', fetchMock);

    await requestOtp('user@example.test');
    const user = await verifyOtp('user@example.test', '123456');

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      '/api/auth/request-otp',
      expect.objectContaining({ credentials: 'include', method: 'POST' }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      '/api/auth/verify-otp',
      expect.objectContaining({ credentials: 'include', method: 'POST' }),
    );
    expect(user).toEqual({ id: 7, email: 'user@example.test' });
  });

  it('treats an unauthenticated me response as no restored user', async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 401 }));
    vi.stubGlobal('fetch', fetchMock);

    expect(await getCurrentUser()).toBeNull();
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/me',
      expect.objectContaining({ credentials: 'include' }),
    );
  });

  it('logs out through the cookie-authenticated API', async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
    vi.stubGlobal('fetch', fetchMock);

    await logout();

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/auth/logout',
      expect.objectContaining({ credentials: 'include', method: 'POST' }),
    );
  });
});
