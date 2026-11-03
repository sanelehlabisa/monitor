import type { BalanceEntry, Meter, TopUpEntry } from '../../lib/api';
import { energyUnits } from './forecast';

export const GUEST_KEY = 'monitor.guest.v1';
export type GuestMeter = { version: 1; meter: Meter; balances: BalanceEntry[]; topUps: TopUpEntry[] };
export type GuestEntryKind = 'balance' | 'top-up';

export function emptyGuestMeter(): GuestMeter {
  const now = new Date().toISOString();
  return { version: 1, meter: { id: crypto.randomUUID(), name: 'Home', owner_email: 'This browser',
    created_at: now, updated_at: now }, balances: [], topUps: [] };
}

const validTime = (value: unknown): value is string => typeof value === 'string'
  && /^\d{4}-\d\d-\d\dT.*(?:Z|[+-]\d\d:\d\d)$/.test(value) && Number.isFinite(Date.parse(value));
const validId = (value: unknown): value is string => typeof value === 'string'
  && /^[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}$/i.test(value);

/** Reject malformed saved data without deleting or overwriting the original. */
function decode(raw: string): GuestMeter {
  const data = JSON.parse(raw);
  const meter = data?.meter;
  if (data?.version !== 1 || !meter || !validId(meter.id)
    || typeof meter.name !== 'string' || !meter.name.trim() || meter.name.length > 80
    || !validTime(meter.created_at) || !validTime(meter.updated_at)
    || !Array.isArray(data.balances) || !Array.isArray(data.topUps)) throw new Error('Invalid browser data');
  const ids = new Set<string>();
  function entry(value: unknown, kind: GuestEntryKind): BalanceEntry | TopUpEntry {
    if (!value || typeof value !== 'object') throw new Error('Invalid browser entry');
    const item = value as Record<string, unknown>;
    const kwh = kind === 'balance' ? item.balance_kwh : item.top_up_kwh;
    if (!validId(item.id) || ids.has(item.id) || item.meter_id !== meter.id
      || !validTime(item.occurred_at) || !validTime(item.created_at) || !validTime(item.updated_at)
      || typeof kwh !== 'string' || (kind === 'top-up' && energyUnits(kwh) === 0n)) {
      throw new Error('Invalid browser entry');
    }
    energyUnits(kwh);
    ids.add(item.id);
    const common = { id: item.id, meter_id: meter.id as string,
      occurred_at: new Date(item.occurred_at).toISOString(), created_at: item.created_at, updated_at: item.updated_at };
    return kind === 'balance' ? { ...common, balance_kwh: kwh } : { ...common, top_up_kwh: kwh };
  }
  return { version: 1, meter: { id: meter.id, name: meter.name.trim(), owner_email: 'This browser',
    created_at: meter.created_at, updated_at: meter.updated_at },
    balances: data.balances.map((item: unknown) => entry(item, 'balance')) as BalanceEntry[],
    topUps: data.topUps.map((item: unknown) => entry(item, 'top-up')) as TopUpEntry[] };
}

export function loadGuestMeter(): { data: GuestMeter; raw: string | null; protected: boolean; warning: string } {
  let raw: string | null = null;
  try {
    raw = localStorage.getItem(GUEST_KEY);
    return { data: raw === null ? emptyGuestMeter() : decode(raw), raw, protected: false, warning: '' };
  } catch {
    return { data: emptyGuestMeter(), raw, protected: raw !== null,
      warning: raw !== null ? 'Saved browser data could not be read. It has not been replaced. Clear local data to start over.'
        : 'Browser storage is unavailable. Changes will remain only in this tab.' };
  }
}

/** Compare before writing so an old tab cannot silently replace newer records. */
export function saveGuestMeter(data: GuestMeter, expectedRaw: string | null): string {
  if (localStorage.getItem(GUEST_KEY) !== expectedRaw) {
    throw new Error('Records changed in another tab. Reload before saving.');
  }
  const raw = JSON.stringify(data);
  localStorage.setItem(GUEST_KEY, raw);
  return raw;
}

/** Create or edit a local record using the ledger API's field names and rules. */
export function recordGuestEntry(
  data: GuestMeter, kind: GuestEntryKind, kwh: string, occurredAt: string, id?: string,
): GuestMeter {
  const units = energyUnits(kwh);
  if (kind === 'top-up' && units === 0n) throw new Error('Purchased top-up must be greater than zero.');
  if (!validTime(occurredAt) || Date.parse(occurredAt) > Date.now()) {
    throw new Error('Choose a valid date and time that is not in the future.');
  }
  const time = new Date(occurredAt).toISOString();
  if (kind === 'balance' && data.balances.some(item => item.id !== id && Date.parse(item.occurred_at) === Date.parse(time))) {
    throw new Error('An actual balance already exists at that date and time.');
  }
  const list = kind === 'balance' ? data.balances : data.topUps;
  const previous = list.find(item => item.id === id);
  if (id && !previous) throw new Error('That record is no longer available.');
  const energy = `${units / 1000n}.${(units % 1000n).toString().padStart(3, '0')}`;
  const common = { id: id ?? crypto.randomUUID(), meter_id: data.meter.id, occurred_at: time,
    created_at: previous?.created_at ?? new Date().toISOString(), updated_at: new Date().toISOString() };
  return kind === 'balance'
    ? { ...data, balances: [...data.balances.filter(item => item.id !== id), { ...common, balance_kwh: energy }] }
    : { ...data, topUps: [...data.topUps.filter(item => item.id !== id), { ...common, top_up_kwh: energy }] };
}
