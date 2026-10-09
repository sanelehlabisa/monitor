export type User = {
  id: number;
  email: string;
  is_admin: boolean;
};

export type Meter = {
  id: string;
  name: string;
  owner_email: string;
  created_at: string;
  updated_at: string;
};

export type BalanceEntry = {
  id: string;
  meter_id: string;
  balance_kwh: string;
  occurred_at: string;
  created_at: string;
  updated_at: string;
};

export type TopUpEntry = {
  id: string;
  meter_id: string;
  top_up_kwh: string;
  occurred_at: string;
  created_at: string;
  updated_at: string;
};

export type Forecast = {
  status: 'available' | 'not_enough_data' | 'inconsistent_history';
  as_of: string;
  latest_actual_balance_kwh: string | null;
  latest_actual_at: string | null;
  daily_usage_kwh: string | null;
  estimated_balance_kwh: string | null;
  remaining_days: string | null;
  run_out_at: string | null;
  recommended_top_up_30_days_kwh: string | null;
  intervals_used: number;
};

export type Dashboard = {
  latest_actual_balance: BalanceEntry | null;
  balances: BalanceEntry[];
  top_ups: TopUpEntry[];
  history: Array<{
    kind: 'balance' | 'top_up';
    id: string;
    kwh: string;
    occurred_at: string;
  }>;
  forecast: Forecast;
};

export class ApiError extends Error {
  constructor(public readonly status: number) {
    super(`Monitor API returned ${status}`);
  }
}

async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(path, {
    ...init,
    credentials: 'include',
    headers: init.body ? { 'Content-Type': 'application/json' } : undefined,
  });
  if (!response.ok) {
    throw new ApiError(response.status);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export async function requestOtp(email: string): Promise<void> {
  await apiRequest('/api/auth/request-otp', {
    method: 'POST',
    body: JSON.stringify({ email }),
  });
}

export function verifyOtp(email: string, code: string): Promise<User> {
  return apiRequest('/api/auth/verify-otp', {
    method: 'POST',
    body: JSON.stringify({ email, code }),
  });
}

export async function getCurrentUser(): Promise<User | null> {
  try {
    return await apiRequest<User>('/api/me');
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      return null;
    }
    throw error;
  }
}

export async function logout(): Promise<void> {
  await apiRequest('/api/auth/logout', { method: 'POST' });
}

export function listMeters(): Promise<Meter[]> {
  return apiRequest('/api/meters');
}

export function createMeter(name: string): Promise<Meter> {
  return apiRequest('/api/meters', {
    method: 'POST',
    body: JSON.stringify({ name }),
  });
}

export function getMeter(id: string): Promise<Meter> {
  return apiRequest(`/api/meters/${id}`);
}

export function renameMeter(id: string, name: string): Promise<Meter> {
  return apiRequest(`/api/meters/${id}`, {
    method: 'PATCH',
    body: JSON.stringify({ name }),
  });
}

export async function deleteMeter(id: string): Promise<void> {
  await apiRequest(`/api/meters/${id}`, { method: 'DELETE' });
}

export function getDashboard(meterId: string): Promise<Dashboard> {
  return apiRequest(`/api/meters/${meterId}/dashboard`);
}

export function listBalances(meterId: string): Promise<BalanceEntry[]> {
  return apiRequest(`/api/meters/${meterId}/balances`);
}

export function createBalance(
  meterId: string,
  balanceKwh: string,
  occurredAt: string,
): Promise<BalanceEntry> {
  return apiRequest(`/api/meters/${meterId}/balances`, {
    method: 'POST',
    body: JSON.stringify({ balance_kwh: balanceKwh, occurred_at: occurredAt }),
  });
}

export function updateBalance(
  meterId: string,
  entryId: string,
  balanceKwh: string,
  occurredAt: string,
): Promise<BalanceEntry> {
  return apiRequest(`/api/meters/${meterId}/balances/${entryId}`, {
    method: 'PATCH',
    body: JSON.stringify({ balance_kwh: balanceKwh, occurred_at: occurredAt }),
  });
}

export async function deleteBalance(
  meterId: string,
  entryId: string,
): Promise<void> {
  await apiRequest(`/api/meters/${meterId}/balances/${entryId}`, {
    method: 'DELETE',
  });
}

export function listTopUps(meterId: string): Promise<TopUpEntry[]> {
  return apiRequest(`/api/meters/${meterId}/top-ups`);
}

export function createTopUp(
  meterId: string,
  topUpKwh: string,
  occurredAt: string,
): Promise<TopUpEntry> {
  return apiRequest(`/api/meters/${meterId}/top-ups`, {
    method: 'POST',
    body: JSON.stringify({ top_up_kwh: topUpKwh, occurred_at: occurredAt }),
  });
}

export function updateTopUp(
  meterId: string,
  entryId: string,
  topUpKwh: string,
  occurredAt: string,
): Promise<TopUpEntry> {
  return apiRequest(`/api/meters/${meterId}/top-ups/${entryId}`, {
    method: 'PATCH',
    body: JSON.stringify({ top_up_kwh: topUpKwh, occurred_at: occurredAt }),
  });
}

export async function deleteTopUp(
  meterId: string,
  entryId: string,
): Promise<void> {
  await apiRequest(`/api/meters/${meterId}/top-ups/${entryId}`, {
    method: 'DELETE',
  });
}
