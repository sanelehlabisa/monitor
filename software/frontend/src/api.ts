// Small HTTP client for the current Monitor API surface.

import { config } from './config';

export interface Identity {
  sub: string;
  username: string;
  email: string | null;
}

export async function fetchIdentity(
  token: string,
  apiUrl: string = config.apiUrl,
  request: typeof fetch = fetch,
): Promise<Identity> {
  const response = await request(`${apiUrl}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) {
    throw new Error(`Identity request failed with HTTP ${response.status}`);
  }
  return (await response.json()) as Identity;
}
