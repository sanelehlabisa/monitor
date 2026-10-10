import {
  Alert,
  Box,
  Button,
  CircularProgress,
  FormControlLabel,
  Stack,
  Switch,
  TextField,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';

import type { ReminderSettings, ReminderSettingsInput } from './api';

type ReminderSettingsPanelProps = {
  settings: ReminderSettings | null;
  loading: boolean;
  busy: boolean;
  error: string;
  notice: string;
  onSave: (settings: ReminderSettingsInput) => Promise<boolean>;
};

function browserTimezone(): string {
  return Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
}

export function ReminderSettingsPanel({
  settings,
  loading,
  busy,
  error,
  notice,
  onSave,
}: ReminderSettingsPanelProps) {
  const [monthlyEnabled, setMonthlyEnabled] = useState(
    settings?.monthly_enabled ?? false,
  );
  const [monthlyDay, setMonthlyDay] = useState(String(settings?.monthly_day ?? 1));
  const [lowBalanceEnabled, setLowBalanceEnabled] = useState(
    settings?.low_balance_enabled ?? false,
  );
  const [lowBalanceDays, setLowBalanceDays] = useState(
    settings?.low_balance_days ?? '3.00',
  );
  const [timezone, setTimezone] = useState(() =>
    settings?.created_at ? settings.timezone : browserTimezone(),
  );

  useEffect(() => {
    if (!settings) return;
    setMonthlyEnabled(settings.monthly_enabled);
    setMonthlyDay(String(settings.monthly_day));
    setLowBalanceEnabled(settings.low_balance_enabled);
    setLowBalanceDays(settings.low_balance_days);
    setTimezone(settings.created_at ? settings.timezone : browserTimezone());
  }, [settings]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onSave({
      monthly_enabled: monthlyEnabled,
      monthly_day: Number(monthlyDay),
      low_balance_enabled: lowBalanceEnabled,
      low_balance_days: lowBalanceDays,
      timezone,
    });
  }

  if (loading) {
    return (
      <Box sx={{ display: 'grid', minHeight: 120, placeItems: 'center' }}>
        <CircularProgress aria-label="Loading reminder settings" color="inherit" size={28} />
      </Box>
    );
  }

  if (!settings) {
    return <Alert severity="error">{error || 'Reminder settings are unavailable.'}</Alert>;
  }

  return (
    <Box component="form" onSubmit={handleSubmit}>
      <Stack spacing={1.5}>
        <Box>
          <Typography component="h3" sx={{ fontWeight: 800 }} variant="h6">
            Email reminders
          </Typography>
          <Typography color="text.secondary" variant="body2">
            Optional planning prompts only. Monitor never buys electricity or guarantees an estimate.
          </Typography>
        </Box>
        <FormControlLabel
          control={<Switch checked={monthlyEnabled} disabled={busy} onChange={(event) => setMonthlyEnabled(event.target.checked)} />}
          label="Monthly planning email"
        />
        <TextField
          disabled={busy || !monthlyEnabled}
          label="Day of month"
          onChange={(event) => setMonthlyDay(event.target.value)}
          required
          slotProps={{ htmlInput: { min: 1, max: 28, step: 1 } }}
          type="number"
          value={monthlyDay}
        />
        <Typography color="text.secondary" variant="caption">
          Monthly email asks for a fresh reading when no estimate is available.
        </Typography>
        <FormControlLabel
          control={<Switch checked={lowBalanceEnabled} disabled={busy} onChange={(event) => setLowBalanceEnabled(event.target.checked)} />}
          label="Predicted low-balance email"
        />
        <TextField
          disabled={busy || !lowBalanceEnabled}
          label="Warn this many days before run-out"
          onChange={(event) => setLowBalanceDays(event.target.value)}
          required
          slotProps={{ htmlInput: { inputMode: 'decimal', min: '0.01', max: '30', step: '0.01' } }}
          type="number"
          value={lowBalanceDays}
        />
        <Typography color="text.secondary" variant="caption">
          Low-balance email requires a valid forecast. Timezone: {timezone}
        </Typography>
        {error && <Alert severity="error">{error}</Alert>}
        {notice && <Alert severity="success">{notice}</Alert>}
        <Button disabled={busy} type="submit" variant="contained">
          {busy ? 'Saving…' : 'Save reminder settings'}
        </Button>
      </Stack>
    </Box>
  );
}
