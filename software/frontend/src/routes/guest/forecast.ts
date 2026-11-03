import type { BalanceEntry, Forecast, TopUpEntry } from '../../lib/api';

const DAY_MS = 86_400_000n;
const positive = (value: bigint): bigint => value > 0n ? value : 0n;
const rounded = (value: bigint, divisor: bigint): bigint => (value + divisor / 2n) / divisor;
const timestamp = (value: string): bigint => BigInt(new Date(value).getTime());

function decimal(value: bigint, places: number): string {
  const digits = value.toString().padStart(places + 1, '0');
  return `${digits.slice(0, -places)}.${digits.slice(-places)}`;
}

/** Parse the same non-negative three-decimal energy range as the ledger API. */
export function energyUnits(value: string): bigint {
  if (!/^(?:\d+(?:\.\d{0,3})?|\.\d{1,3})$/.test(value.trim())) {
    throw new Error('Enter kWh using up to three decimal places.');
  }
  const [whole = '', fraction = ''] = value.trim().split('.');
  const units = BigInt(whole || '0') * 1000n + BigInt(fraction.padEnd(3, '0'));
  if (units > 999_999_999_999n) throw new Error('The kWh value is too large.');
  return units;
}

/** Mirror the Python forecast using integer energy/rate units and UTC milliseconds. */
export function forecastLocally(
  balances: BalanceEntry[], topUps: TopUpEntry[], now = new Date(),
): Forecast {
  const planning = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth() + 1, 1));
  const following = new Date(Date.UTC(planning.getUTCFullYear(), planning.getUTCMonth() + 1, 1));
  const planningDays = (following.getTime() - planning.getTime()) / Number(DAY_MS);
  const ordered = [...balances].sort((a, b) =>
    Date.parse(a.occurred_at) - Date.parse(b.occurred_at) || a.id.localeCompare(b.id));
  const latest = ordered.at(-1);
  const result: Forecast = {
    status: 'not_enough_data', as_of: now.toISOString(), planning_at: planning.toISOString(),
    planning_days: planningDays, latest_actual_balance_kwh: latest?.balance_kwh ?? null,
    latest_actual_at: latest?.occurred_at ?? null, daily_usage_kwh: null,
    estimated_balance_kwh: null, remaining_days: null, run_out_at: null,
    recommended_monthly_top_up_kwh: null, monthly_requirement_kwh: null, intervals_used: 0,
  };
  if (!latest) return result;
  result.status = 'inconsistent_history';
  if (Date.parse(latest.occurred_at) > now.getTime()) return result;
  const topUpsBetween = (after: string, until: string): bigint => topUps.reduce((total, entry) =>
    timestamp(after) < timestamp(entry.occurred_at) && timestamp(entry.occurred_at) <= timestamp(until)
      ? total + energyUnits(entry.top_up_kwh) : total, 0n);
  let consumption = 0n;
  let elapsed = 0n;
  for (let index = 1; index < ordered.length; index++) {
    const previous = ordered[index - 1];
    const current = ordered[index];
    const duration = timestamp(current.occurred_at) - timestamp(previous.occurred_at);
    const used = energyUnits(previous.balance_kwh)
      + topUpsBetween(previous.occurred_at, current.occurred_at) - energyUnits(current.balance_kwh);
    if (duration <= 0n || used < 0n) return result;
    elapsed += duration;
    consumption += used;
  }
  // Rates use millionths of kWh/day; energies use thousandths of kWh.
  const rate = elapsed ? rounded(consumption * DAY_MS * 1000n, elapsed) : 10_000_000n;
  const available = energyUnits(latest.balance_kwh) + topUpsBetween(latest.occurred_at, result.as_of);
  const balance = rounded(positive(available * DAY_MS * 1000n
    - rate * (BigInt(now.getTime()) - timestamp(latest.occurred_at))), DAY_MS * 1000n);
  const monthly = rate * BigInt(planningDays);
  let runOut: string | null = null;
  if (rate) {
    const date = new Date(now.getTime() + Number(balance * 1000n * DAY_MS / rate));
    if (Number.isFinite(date.getTime())) runOut = date.toISOString();
  }
  return {
    ...result, status: 'available', daily_usage_kwh: decimal(rate, 6),
    estimated_balance_kwh: decimal(balance, 3),
    remaining_days: rate ? decimal(rounded(balance * 100_000n, rate), 2) : null,
    run_out_at: runOut, intervals_used: ordered.length - 1,
    recommended_monthly_top_up_kwh: rate
      ? decimal(rounded(positive(monthly - balance * 1000n), 1000n), 3) : '0.000',
    monthly_requirement_kwh: decimal(rounded(monthly, 1000n), 3),
  };
}
