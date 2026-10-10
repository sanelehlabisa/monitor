import { describe, expect, it } from 'vitest';

import {
  localDateDisplay,
  localDateTimeDisplay,
  localDateTimeInputValue,
  utcDateTimeValue,
} from './dateTime';

describe('browser-local date and time helpers', () => {
  it('converts local datetime input into the UTC API representation', () => {
    const localValue = '2026-10-10T14:30';

    expect(utcDateTimeValue(localValue)).toBe(new Date(localValue).toISOString());
  });

  it('renders returned UTC values with browser-local formatters', () => {
    const utcValue = '2026-10-10T12:30:00Z';

    expect(localDateTimeDisplay(utcValue)).toBe(
      new Date(utcValue).toLocaleString(),
    );
    expect(localDateDisplay(utcValue)).toBe(
      new Date(utcValue).toLocaleDateString(),
    );
  });

  it('formats an existing UTC instant for a local datetime input', () => {
    const date = new Date('2026-10-10T12:30:00Z');
    const local = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);

    expect(localDateTimeInputValue(date)).toBe(local.toISOString().slice(0, 16));
  });
});
