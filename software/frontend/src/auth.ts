// Keycloak browser-session helpers.

import Keycloak, { type KeycloakInstance } from 'keycloak-js';

import { config } from './config';

export const authClient = new Keycloak({
  url: config.keycloakUrl,
  realm: config.keycloakRealm,
  clientId: config.keycloakClientId,
});

let initialization: Promise<boolean> | undefined;

export async function initializeAuth(
  client: KeycloakInstance = authClient,
  origin: string = window.location.origin,
): Promise<boolean> {
  const start = (): Promise<boolean> => client.init({
    onLoad: 'check-sso',
    pkceMethod: 'S256',
    checkLoginIframe: false,
    silentCheckSsoRedirectUri: `${origin}/silent-check-sso.html`,
    silentCheckSsoFallback: false,
  });
  if (client !== authClient) {
    return start();
  }
  initialization ??= start();
  return initialization;
}

export async function freshAccessToken(
  client: KeycloakInstance = authClient,
): Promise<string> {
  if (!client.authenticated) {
    throw new Error('User is not authenticated');
  }
  await client.updateToken(30);
  if (!client.token) {
    throw new Error('Authenticated session has no access token');
  }
  return client.token;
}

export async function login(
  client: KeycloakInstance = authClient,
  origin: string = window.location.origin,
): Promise<void> {
  await client.login({ redirectUri: `${origin}/` });
}

export async function logout(
  client: KeycloakInstance = authClient,
  origin: string = window.location.origin,
): Promise<void> {
  await client.logout({ redirectUri: `${origin}/` });
}
