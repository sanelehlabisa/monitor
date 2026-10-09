import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { useMemo, useState } from 'react';
import type { FormEvent } from 'react';

import type { BalanceEntry, TopUpEntry } from './api';

export type LedgerItem =
  | { kind: 'balance'; entry: BalanceEntry }
  | { kind: 'top-up'; entry: TopUpEntry };

type LedgerPanelProps = {
  balances: BalanceEntry[];
  topUps: TopUpEntry[];
  loading: boolean;
  busy: boolean;
  error: string;
  onCreateBalance: (kwh: string, occurredAt: string) => Promise<boolean>;
  onCreateTopUp: (kwh: string, occurredAt: string) => Promise<boolean>;
  onUpdate: (
    item: LedgerItem,
    kwh: string,
    occurredAt: string,
  ) => Promise<boolean>;
  onDelete: (item: LedgerItem) => Promise<boolean>;
};

function localDateTimeValue(date = new Date()): string {
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);
  return local.toISOString().slice(0, 16);
}

function apiDateTime(localValue: string): string {
  return new Date(localValue).toISOString();
}

function entryTime(item: LedgerItem): string {
  return item.entry.occurred_at;
}

export function LedgerPanel({
  balances,
  topUps,
  loading,
  busy,
  error,
  onCreateBalance,
  onCreateTopUp,
  onUpdate,
  onDelete,
}: LedgerPanelProps) {
  const [mode, setMode] = useState<'balance' | 'top-up'>('balance');
  const [kwh, setKwh] = useState('');
  const [occurredAt, setOccurredAt] = useState(localDateTimeValue);
  const [editing, setEditing] = useState<LedgerItem | null>(null);
  const [editKwh, setEditKwh] = useState('');
  const [editOccurredAt, setEditOccurredAt] = useState('');
  const history = useMemo(
    () =>
      [
        ...balances.map((entry): LedgerItem => ({ kind: 'balance', entry })),
        ...topUps.map((entry): LedgerItem => ({ kind: 'top-up', entry })),
      ].sort(
        (left, right) =>
          entryTime(right).localeCompare(entryTime(left)) ||
          right.entry.id.localeCompare(left.entry.id),
      ),
    [balances, topUps],
  );
  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const saved =
      mode === 'balance'
        ? await onCreateBalance(kwh, apiDateTime(occurredAt))
        : await onCreateTopUp(kwh, apiDateTime(occurredAt));
    if (saved) {
      setKwh('');
      setOccurredAt(localDateTimeValue());
    }
  }

  function beginEdit(item: LedgerItem) {
    setEditing(item);
    setEditKwh(
      item.kind === 'balance' ? item.entry.balance_kwh : item.entry.top_up_kwh,
    );
    setEditOccurredAt(localDateTimeValue(new Date(item.entry.occurred_at)));
  }

  async function handleUpdate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (
      editing &&
      (await onUpdate(editing, editKwh, apiDateTime(editOccurredAt)))
    ) {
      setEditing(null);
    }
  }

  async function handleDelete(item: LedgerItem) {
    const label = item.kind === 'balance' ? 'actual balance' : 'purchased top-up';
    if (window.confirm(`Delete this ${label}?`) && (await onDelete(item))) {
      if (editing?.entry.id === item.entry.id) setEditing(null);
    }
  }

  if (loading) {
    return (
      <Box sx={{ display: 'grid', minHeight: 160, placeItems: 'center' }}>
        <CircularProgress
          aria-label="Loading meter history"
          color="inherit"
          size={28}
        />
      </Box>
    );
  }

  return (
    <Stack spacing={2.5}>
      <Stack direction="row" spacing={1}>
        <Button
          fullWidth
          onClick={() => setMode('balance')}
          variant={mode === 'balance' ? 'contained' : 'outlined'}
        >
          Record balance
        </Button>
        <Button
          fullWidth
          onClick={() => setMode('top-up')}
          variant={mode === 'top-up' ? 'contained' : 'outlined'}
        >
          Record top-up
        </Button>
      </Stack>

      <Box component="form" onSubmit={handleCreate}>
        <Stack spacing={1.5}>
          <TextField
            disabled={busy}
            fullWidth
            label={
              mode === 'balance'
                ? 'Remaining balance (kWh)'
                : 'Purchased top-up (kWh)'
            }
            onChange={(event) => setKwh(event.target.value)}
            required
            slotProps={{
              htmlInput: {
                inputMode: 'decimal',
                min: mode === 'balance' ? '0' : '0.001',
                step: '0.001',
              },
            }}
            type="number"
            value={kwh}
          />
          <TextField
            disabled={busy}
            fullWidth
            label={mode === 'balance' ? 'Observed at' : 'Purchased at'}
            onChange={(event) => setOccurredAt(event.target.value)}
            required
            slotProps={{ inputLabel: { shrink: true } }}
            type="datetime-local"
            value={occurredAt}
          />
          <Button disabled={busy || !kwh} type="submit" variant="contained">
            {busy ? 'Saving…' : mode === 'balance' ? 'Save balance' : 'Save top-up'}
          </Button>
        </Stack>
      </Box>

      {error && <Alert severity="error">{error}</Alert>}

      {editing && (
        <Box
          component="form"
          onSubmit={handleUpdate}
          sx={{ bgcolor: 'background.default', borderRadius: 2, p: 2 }}
        >
          <Stack spacing={1.5}>
            <Typography sx={{ fontWeight: 700 }}>
              Edit {editing.kind === 'balance' ? 'actual balance' : 'purchased top-up'}
            </Typography>
            <TextField
              disabled={busy}
              label="kWh"
              onChange={(event) => setEditKwh(event.target.value)}
              required
              slotProps={{
                htmlInput: {
                  inputMode: 'decimal',
                  min: editing.kind === 'balance' ? '0' : '0.001',
                  step: '0.001',
                },
              }}
              type="number"
              value={editKwh}
            />
            <TextField
              disabled={busy}
              label="Date and time"
              onChange={(event) => setEditOccurredAt(event.target.value)}
              required
              slotProps={{ inputLabel: { shrink: true } }}
              type="datetime-local"
              value={editOccurredAt}
            />
            <Stack direction="row" spacing={1}>
              <Button disabled={busy} type="submit" variant="contained">
                Save correction
              </Button>
              <Button disabled={busy} onClick={() => setEditing(null)} type="button">
                Cancel
              </Button>
            </Stack>
          </Stack>
        </Box>
      )}

      <Box>
        <Typography component="h3" sx={{ fontWeight: 800 }} variant="h6">
          History
        </Typography>
        {history.length === 0 ? (
          <Typography color="text.secondary" sx={{ mt: 1 }} variant="body2">
            No balance or top-up entries yet.
          </Typography>
        ) : (
          <Stack spacing={1} sx={{ mt: 1.5 }}>
            {history.map((item) => {
              const isBalance = item.kind === 'balance';
              const value = isBalance
                ? item.entry.balance_kwh
                : item.entry.top_up_kwh;
              return (
                <Box
                  key={`${item.kind}-${item.entry.id}`}
                  sx={{
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 2,
                    p: 1.75,
                  }}
                >
                  <Stack direction="row" sx={{ justifyContent: 'space-between' }}>
                    <Box>
                      <Typography sx={{ fontWeight: 700 }}>
                        {isBalance ? 'Actual balance' : 'Purchased top-up'}
                      </Typography>
                      <Typography>{value} kWh</Typography>
                      <Typography color="text.secondary" variant="caption">
                        {new Date(item.entry.occurred_at).toLocaleString()}
                      </Typography>
                    </Box>
                    <Stack sx={{ alignItems: 'flex-end' }}>
                      <Button disabled={busy} onClick={() => beginEdit(item)} size="small">
                        Edit
                      </Button>
                      <Button
                        color="error"
                        disabled={busy}
                        onClick={() => handleDelete(item)}
                        size="small"
                      >
                        Delete
                      </Button>
                    </Stack>
                  </Stack>
                </Box>
              );
            })}
          </Stack>
        )}
      </Box>
    </Stack>
  );
}
