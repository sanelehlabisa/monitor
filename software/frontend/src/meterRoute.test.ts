import { describe, expect, it } from 'vitest';

import { isMeterListPath, meterIdFromPath } from './meterRoute';

describe('meter URL parsing', () => {
  const id = '01234567-89ab-cdef-0123-456789abcdef';

  it('recognises the canonical list URL and legacy/trailing-slash entry links', () => {
    for (const path of ['/', '/meters', '/meters/']) expect(isMeterListPath(path)).toBe(true);
    for (const path of [`/meters/${id}`, '/meters/bad-id', '/missing', '/api/meters']) expect(isMeterListPath(path)).toBe(false);
  });

  it('accepts a complete meter UUID with an optional trailing slash', () => {
    expect(meterIdFromPath(`/meters/${id}`)).toBe(id);
    expect(meterIdFromPath(`/meters/${id}/`)).toBe(id);
    expect(meterIdFromPath(`/meters/${id.toUpperCase()}`)).toBe(id.toUpperCase());
  });

  it.each(['/', '/meters', '/meters/bad-id', '/meters/../', `/meters/${id}/extra`, `/api/meters/${id}`])(
    'rejects unsupported path %s', (path) => expect(meterIdFromPath(path)).toBeNull(),
  );
});
