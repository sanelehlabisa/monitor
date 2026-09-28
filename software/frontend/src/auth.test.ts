import type { KeycloakInstance } from 'keycloak-js';
import { describe, expect, it, vi } from 'vitest';

import { freshAccessToken, initializeAuth, login, logout } from './auth';

describe('authentication helpers', () => {
  it('initializes a public-client session with S256 PKCE', async () => {
    const init = vi.fn().mockResolvedValue(false);
    const client = { init } as unknown as KeycloakInstance;

    await expect(initializeAuth(client, 'http://localhost:5173')).resolves.toBe(false);
    expect(init).toHaveBeenCalledWith({
      onLoad: 'check-sso',
      pkceMethod: 'S256',
      checkLoginIframe: false,
      silentCheckSsoRedirectUri: 'http://localhost:5173/silent-check-sso.html',
      silentCheckSsoFallback: false,
    });
  });

  it('refreshes and returns an authenticated access token', async () => {
    const updateToken = vi.fn().mockResolvedValue(true);
    const client = {
      authenticated: true,
      token: 'access-token',
      updateToken,
    } as unknown as KeycloakInstance;

    await expect(freshAccessToken(client)).resolves.toBe('access-token');
    expect(updateToken).toHaveBeenCalledWith(30);
  });

  it('uses an allowed frontend redirect for login and logout', async () => {
    const signIn = vi.fn().mockResolvedValue(undefined);
    const signOut = vi.fn().mockResolvedValue(undefined);
    const client = { login: signIn, logout: signOut } as unknown as KeycloakInstance;

    await login(client, 'http://localhost:5173');
    await logout(client, 'http://localhost:5173');

    expect(signIn).toHaveBeenCalledWith({ redirectUri: 'http://localhost:5173/' });
    expect(signOut).toHaveBeenCalledWith({ redirectUri: 'http://localhost:5173/' });
  });
});
