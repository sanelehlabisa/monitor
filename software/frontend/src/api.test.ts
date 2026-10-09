import { afterEach, describe, expect, it, vi } from 'vitest';

import {
  createMeter,
  deleteMeter,
  getCurrentUser,
  getMeter,
  listMeters,
  logout,
  requestOtp,
  renameMeter,
  verifyOtp,
} from './api';

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
        new Response(
          JSON.stringify({
            id: 7,
            email: 'user@example.test',
            is_admin: false,
          }),
          { status: 200 },
        ),
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
    expect(user).toEqual({
      id: 7,
      email: 'user@example.test',
      is_admin: false,
    });
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

  it('lists, creates and retrieves meters through relative cookie APIs', async () => {
    const meter = {
      id: '00000000-0000-0000-0000-000000000001',
      name: 'Home',
      owner_email: 'user@example.test',
      created_at: '2026-10-09T10:00:00Z',
      updated_at: '2026-10-09T10:00:00Z',
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        new Response(JSON.stringify([meter]), { status: 200 }),
      )
      .mockResolvedValueOnce(new Response(JSON.stringify(meter), { status: 201 }))
      .mockResolvedValueOnce(new Response(JSON.stringify(meter), { status: 200 }))
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ ...meter, name: 'Main home' }), {
          status: 200,
        }),
      )
      .mockResolvedValueOnce(new Response(null, { status: 204 }));
    vi.stubGlobal('fetch', fetchMock);

    expect(await listMeters()).toEqual([meter]);
    expect(await createMeter('Home')).toEqual(meter);
    expect(await getMeter(meter.id)).toEqual(meter);
    expect(await renameMeter(meter.id, 'Main home')).toEqual({
      ...meter,
      name: 'Main home',
    });
    await deleteMeter(meter.id);

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      '/api/meters',
      expect.objectContaining({ credentials: 'include' }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      '/api/meters',
      expect.objectContaining({
        body: JSON.stringify({ name: 'Home' }),
        credentials: 'include',
        method: 'POST',
      }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      `/api/meters/${meter.id}`,
      expect.objectContaining({ credentials: 'include' }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      4,
      `/api/meters/${meter.id}`,
      expect.objectContaining({
        body: JSON.stringify({ name: 'Main home' }),
        credentials: 'include',
        method: 'PATCH',
      }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      5,
      `/api/meters/${meter.id}`,
      expect.objectContaining({ credentials: 'include', method: 'DELETE' }),
    );
  });
});
