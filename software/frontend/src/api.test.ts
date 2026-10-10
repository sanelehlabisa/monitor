import { afterEach, describe, expect, it, vi } from 'vitest';

import {
  createBalance,
  createMeter,
  createTopUp,
  deleteBalance,
  deleteMeter,
  deleteTopUp,
  getCurrentUser,
  getDashboard,
  getMeter,
  getReminderSettings,
  listBalances,
  listMeters,
  listTopUps,
  logout,
  requestOtp,
  renameMeter,
  updateBalance,
  updateReminderSettings,
  updateTopUp,
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

  it('uses nested cookie APIs for both manual ledger resources', async () => {
    const meterId = '00000000-0000-0000-0000-000000000001';
    const balance = {
      id: '00000000-0000-0000-0000-000000000010',
      meter_id: meterId,
      balance_kwh: '42.125',
      occurred_at: '2026-10-09T10:00:00Z',
      created_at: '2026-10-09T10:01:00Z',
      updated_at: '2026-10-09T10:01:00Z',
    };
    const topUp = {
      id: '00000000-0000-0000-0000-000000000020',
      meter_id: meterId,
      top_up_kwh: '20.500',
      occurred_at: '2026-10-09T11:00:00Z',
      created_at: '2026-10-09T11:01:00Z',
      updated_at: '2026-10-09T11:01:00Z',
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(new Response(JSON.stringify([balance]), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify(balance), { status: 201 }))
      .mockResolvedValueOnce(new Response(JSON.stringify(balance), { status: 200 }))
      .mockResolvedValueOnce(new Response(null, { status: 204 }))
      .mockResolvedValueOnce(new Response(JSON.stringify([topUp]), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify(topUp), { status: 201 }))
      .mockResolvedValueOnce(new Response(JSON.stringify(topUp), { status: 200 }))
      .mockResolvedValueOnce(new Response(null, { status: 204 }));
    vi.stubGlobal('fetch', fetchMock);

    expect(await listBalances(meterId)).toEqual([balance]);
    await createBalance(meterId, '42.125', balance.occurred_at);
    await updateBalance(meterId, balance.id, '42.125', balance.occurred_at);
    await deleteBalance(meterId, balance.id);
    expect(await listTopUps(meterId)).toEqual([topUp]);
    await createTopUp(meterId, '20.500', topUp.occurred_at);
    await updateTopUp(meterId, topUp.id, '20.500', topUp.occurred_at);
    await deleteTopUp(meterId, topUp.id);

    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      `/api/meters/${meterId}/balances`,
      expect.objectContaining({
        body: JSON.stringify({
          balance_kwh: '42.125',
          occurred_at: balance.occurred_at,
        }),
        credentials: 'include',
        method: 'POST',
      }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      7,
      `/api/meters/${meterId}/top-ups/${topUp.id}`,
      expect.objectContaining({ credentials: 'include', method: 'PATCH' }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      8,
      `/api/meters/${meterId}/top-ups/${topUp.id}`,
      expect.objectContaining({ credentials: 'include', method: 'DELETE' }),
    );
  });

  it('loads the derived dashboard through the relative cookie API', async () => {
    const meterId = '00000000-0000-0000-0000-000000000001';
    const dashboard = {
      latest_actual_balance: null,
      balances: [],
      top_ups: [],
      history: [],
      forecast: {
        status: 'not_enough_data',
        as_of: '2026-10-09T12:00:00Z',
        latest_actual_balance_kwh: null,
        latest_actual_at: null,
        daily_usage_kwh: null,
        estimated_balance_kwh: null,
        remaining_days: null,
        run_out_at: null,
        recommended_top_up_30_days_kwh: null,
        intervals_used: 0,
      },
    };
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(dashboard), { status: 200 }),
    );
    vi.stubGlobal('fetch', fetchMock);

    expect(await getDashboard(meterId)).toEqual(dashboard);
    expect(fetchMock).toHaveBeenCalledWith(
      `/api/meters/${meterId}/dashboard`,
      expect.objectContaining({ credentials: 'include' }),
    );
  });

  it('loads and saves per-meter reminder settings through cookie APIs', async () => {
    const meterId = '00000000-0000-0000-0000-000000000001';
    const settings = {
      meter_id: meterId,
      monthly_enabled: false,
      monthly_day: 1,
      low_balance_enabled: false,
      low_balance_days: '3.00',
      timezone: 'UTC',
      created_at: null,
      updated_at: null,
    };
    const input = {
      monthly_enabled: true,
      monthly_day: 15,
      low_balance_enabled: true,
      low_balance_days: '2.50',
      timezone: 'Africa/Johannesburg',
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(new Response(JSON.stringify(settings), { status: 200 }))
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ ...settings, ...input }), { status: 200 }),
      );
    vi.stubGlobal('fetch', fetchMock);

    expect(await getReminderSettings(meterId)).toEqual(settings);
    expect(await updateReminderSettings(meterId, input)).toEqual({
      ...settings,
      ...input,
    });
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      `/api/meters/${meterId}/reminders`,
      expect.objectContaining({
        body: JSON.stringify(input),
        credentials: 'include',
        method: 'PATCH',
      }),
    );
  });
});
