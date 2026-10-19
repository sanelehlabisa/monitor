/** Format a Date for a browser-local datetime input. */
export function localDateTimeInputValue(date = new Date()): string {
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);
  return local.toISOString().slice(0, 16);
}

/** Convert a browser-local datetime input into the UTC API representation. */
export function utcDateTimeValue(localValue: string): string {
  return new Date(localValue).toISOString();
}

/** Render an API timestamp using the calling browser's local timezone. */
export function localDateTimeDisplay(value: string): string {
  return new Date(value).toLocaleString();
}

/** Render an API date using the calling browser's local timezone. */
export function localDateDisplay(value: string): string {
  return new Date(value).toLocaleDateString();
}

/** Keep the planning month's UTC 1st from shifting to a browser's previous day. */
export function utcDateDisplay(value: string): string {
  return new Date(value).toLocaleDateString(undefined, { timeZone: 'UTC' });
}
