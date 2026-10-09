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
