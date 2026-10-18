/** Recognise list URLs, including the legacy entry link. */
export function isMeterListPath(path: string): boolean {
  return path === '/' || path === '/meters' || path === '/meters/';
}

/** Parse only supported meter URLs; the API still checks ownership. */
export function meterIdFromPath(path: string): string | null {
  return /^\/meters\/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\/?$/i.exec(path)?.[1] ?? null;
}
