import { Alert, Button, Stack, Typography } from '@mui/material';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutlined';
import RefreshIcon from '@mui/icons-material/Refresh';
import { useEffect, useRef, useState } from 'react';
import { MeterDetailsPage } from '../meters/MeterDetailsPage';
import { ForecastPanel } from '../meters/components/ForecastPanel';
import { LedgerPanel } from '../meters/components/LedgerPanel';
import { forecastLocally } from './forecast';
import { emptyGuestMeter, GUEST_KEY, loadGuestMeter, recordGuestEntry, saveGuestMeter } from './localMeter';
import type { GuestMeter } from './localMeter';

/** Local-only workspace; authenticated pages continue using the existing API. */
export function GuestPage() {
  const [initial] = useState(loadGuestMeter);
  const [data, setData] = useState(initial.data);
  const [name, setName] = useState(initial.data.meter.name);
  const [warning, setWarning] = useState(initial.warning);
  const [error, setError] = useState('');
  const [now, setNow] = useState(() => new Date());
  const raw = useRef(initial.raw);
  const protectedData = useRef(initial.protected);

  useEffect(() => {
    const refresh = () => setNow(new Date());
    const changed = (event: StorageEvent) => {
      if (event.key !== GUEST_KEY && event.key !== null) return;
      protectedData.current = true;
      setWarning('Records changed in another tab. Current edits stay in this tab; reload before saving.');
    };
    const timer = window.setInterval(refresh, 60_000);
    window.addEventListener('focus', refresh);
    document.addEventListener('visibilitychange', refresh);
    window.addEventListener('storage', changed);
    return () => {
      window.clearInterval(timer);
      window.removeEventListener('focus', refresh);
      document.removeEventListener('visibilitychange', refresh);
      window.removeEventListener('storage', changed);
    };
  }, []);

  function persist(next: GuestMeter): void {
    if (protectedData.current) return;
    try {
      raw.current = saveGuestMeter(next, raw.current);
      setWarning('');
    } catch (failure) {
      if (failure instanceof Error && failure.message.includes('another tab')) protectedData.current = true;
      setWarning(failure instanceof Error && failure.message.includes('another tab')
        ? failure.message : 'Not saved to this browser. Changes remain only in this tab. Try saving again or free browser storage.');
    }
  }

  async function change(update: () => GuestMeter): Promise<boolean> {
    try {
      const next = update();
      setData(next);
      setError('');
      setNow(new Date());
      persist(next);
      return true;
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : 'That change could not be completed.');
      return false;
    }
  }

  function clear(): void {
    if (!window.confirm('Clear all meter records saved in this browser, including any unreadable data?')) return;
    try {
      localStorage.removeItem(GUEST_KEY);
      raw.current = null;
      protectedData.current = false;
      setWarning('');
      const next = emptyGuestMeter();
      setData(next);
      setName(next.meter.name);
      setError('');
      persist(next);
    } catch {
      setWarning('Browser data could not be cleared. Your current records have been kept.');
    }
  }

  return (
    <Stack spacing={2.5}>
      <Typography component="h1" variant="h4">Meter</Typography>
      {warning && <Alert severity="warning" action={protectedData.current
        ? <Button color="inherit" size="small" onClick={() => {
          if (window.confirm('Reload and discard changes that are only in this tab?')) window.location.reload();
        }}>Reload</Button>
        : <Button color="inherit" size="small" onClick={() => persist(data)}>Retry save</Button>}>
        {warning}
      </Alert>}
      <MeterDetailsPage selectedMeter={data.meter} showOwner={false}
        busy={false} error={error} editName={name} onEditNameChange={setName}
        onRename={async (_, value) => change(() => {
          if (!value.trim() || value.trim().length > 80) throw new Error('Use a meter name of 1–80 characters.');
          return { ...data, meter: { ...data.meter, name: value.trim(), updated_at: new Date().toISOString() } };
        })}
        selectedContent={<Stack spacing={2.5}>
          <ForecastPanel forecast={forecastLocally(data.balances, data.topUps, now)} loading={false} />
          <LedgerPanel key={data.meter.id} balances={data.balances} topUps={data.topUps}
            busy={false} loading={false} error=""
            onCreateBalance={(kwh, at) => change(() => recordGuestEntry(data, 'balance', kwh, at))}
            onCreateTopUp={(kwh, at) => change(() => recordGuestEntry(data, 'top-up', kwh, at))}
            onUpdate={(item, kwh, at) => change(() => recordGuestEntry(data, item.kind, kwh, at, item.entry.id))}
            onDelete={item => change(() => item.kind === 'balance'
              ? { ...data, balances: data.balances.filter(entry => entry.id !== item.entry.id) }
              : { ...data, topUps: data.topUps.filter(entry => entry.id !== item.entry.id) })} />
          <Stack direction="row" sx={{ justifyContent: 'space-between', flexWrap: 'wrap', gap: 1 }}>
            <Button size="small" startIcon={<RefreshIcon />} onClick={() => setNow(new Date())}>Refresh</Button>
            <Button size="small" color="error" startIcon={<DeleteOutlineIcon />} onClick={clear}>Clear local data</Button>
          </Stack>
        </Stack>} />
    </Stack>
  );
}
