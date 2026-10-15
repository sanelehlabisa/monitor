import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Stack,
  Tab,
  Tabs,
  TextField,
  Typography,
} from '@mui/material';
import AccountBalanceWalletOutlinedIcon from '@mui/icons-material/AccountBalanceWalletOutlined';
import BackspaceOutlinedIcon from '@mui/icons-material/BackspaceOutlined';
import BeenhereOutlinedIcon from '@mui/icons-material/BeenhereOutlined';
import BoltOutlinedIcon from '@mui/icons-material/BoltOutlined';
import BorderColorOutlinedIcon from '@mui/icons-material/BorderColorOutlined';
import CloseIcon from '@mui/icons-material/Close';
import { useMemo, useState } from 'react';
import type { FormEvent } from 'react';

import type { BalanceEntry, TopUpEntry } from './api';
import {
  localDateTimeDisplay,
  localDateTimeInputValue,
  utcDateTimeValue,
} from './dateTime';

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
  const [formOpen, setFormOpen] = useState(false);
  const [kwh, setKwh] = useState('');
  const [occurredAt, setOccurredAt] = useState(localDateTimeInputValue);
  const [editing, setEditing] = useState<LedgerItem | null>(null);
  const [editKwh, setEditKwh] = useState('');
  const [editOccurredAt, setEditOccurredAt] = useState('');
  const history = useMemo(
    () =>
      (mode === 'balance'
        ? balances.map((entry): LedgerItem => ({ kind: 'balance', entry }))
        : topUps.map((entry): LedgerItem => ({ kind: 'top-up', entry })))
        .sort(
        (left, right) =>
          entryTime(right).localeCompare(entryTime(left)) ||
          right.entry.id.localeCompare(left.entry.id),
      ),
    [balances, mode, topUps],
  );
  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const saved =
      mode === 'balance'
        ? await onCreateBalance(kwh, utcDateTimeValue(occurredAt))
        : await onCreateTopUp(kwh, utcDateTimeValue(occurredAt));
    if (saved) {
      setKwh('');
      setOccurredAt(localDateTimeInputValue());
      setFormOpen(false);
    }
  }

  function beginEdit(item: LedgerItem) {
    setFormOpen(false);
    setEditing(item);
    setEditKwh(
      item.kind === 'balance' ? item.entry.balance_kwh : item.entry.top_up_kwh,
    );
    setEditOccurredAt(localDateTimeInputValue(new Date(item.entry.occurred_at)));
  }

  function beginRecord(kind: 'balance' | 'top-up') {
    setMode(kind);
    setEditing(null);
    setKwh('');
    setOccurredAt(localDateTimeInputValue());
    setFormOpen(true);
  }

  async function handleUpdate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (
      editing &&
      (await onUpdate(editing, editKwh, utcDateTimeValue(editOccurredAt)))
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
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.25}>
        <Button
          aria-expanded={formOpen && mode === 'balance'}
          disabled={busy}
          fullWidth
          onClick={() => beginRecord('balance')}
          size="medium"
          startIcon={<AccountBalanceWalletOutlinedIcon />}
          sx={{ py: 1 }}
          variant="outlined"
        >
          Record balance
        </Button>
        <Button
          aria-expanded={formOpen && mode === 'top-up'}
          disabled={busy}
          fullWidth
          onClick={() => beginRecord('top-up')}
          color="secondary"
          size="medium"
          startIcon={<BoltOutlinedIcon />}
          sx={{ py: 1 }}
          variant="outlined"
        >
          Record top-up
        </Button>
      </Stack>

      {formOpen && (
      <Box
        aria-label={mode === 'balance' ? 'Balance records' : 'Top-up records'}
        component="form"
        onSubmit={handleCreate}
      >
        <Stack spacing={1.5}>
          <TextField
            autoFocus
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
          <Button
            disabled={busy || !kwh}
            startIcon={<BeenhereOutlinedIcon />}
            type="submit"
            variant="contained"
          >
            {busy ? 'Saving…' : mode === 'balance' ? 'Save balance' : 'Save top-up'}
          </Button>
          <Button
            disabled={busy}
            onClick={() => setFormOpen(false)}
            startIcon={<CloseIcon />}
            type="button"
          >
            Cancel
          </Button>
        </Stack>
      </Box>
      )}

      {error && <Alert severity="error">{error}</Alert>}

      <Box component="details" sx={{ borderTop: '1px solid', borderColor: 'divider', pt: 2 }}>
        <Typography component="summary" sx={{ cursor: 'pointer', fontWeight: 700 }}>
          History
        </Typography>
        <Tabs
          aria-label="Manage meter records"
          value={mode}
          variant="fullWidth"
          onChange={(_, value: 'balance' | 'top-up') => {
            setMode(value);
            setEditing(null);
            setFormOpen(false);
          }}
        >
          <Tab icon={<AccountBalanceWalletOutlinedIcon />} iconPosition="start" label="Balance records" value="balance" />
          <Tab icon={<BoltOutlinedIcon />} iconPosition="start" label="Top-up records" value="top-up" />
        </Tabs>
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
              <Button
                disabled={busy}
                startIcon={<BeenhereOutlinedIcon />}
                type="submit"
                variant="contained"
              >
                Save correction
              </Button>
              <Button
                disabled={busy}
                onClick={() => setEditing(null)}
                startIcon={<CloseIcon />}
                type="button"
              >
                Cancel
              </Button>
            </Stack>
          </Stack>
        </Box>
      )}

      <Box>
        <Typography component="h3" sx={{ fontWeight: 800 }} variant="h6">
          {mode === 'balance' ? 'Balance history' : 'Top-up history'}
        </Typography>
        {history.length === 0 ? (
          <Typography color="text.secondary" sx={{ mt: 1 }} variant="body2">
            No {mode === 'balance' ? 'balance' : 'top-up'} records yet.
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
                        {localDateTimeDisplay(item.entry.occurred_at)}
                      </Typography>
                    </Box>
                    <Stack sx={{ alignItems: 'flex-end' }}>
                      <Button
                        disabled={busy}
                        onClick={() => beginEdit(item)}
                        size="small"
                        startIcon={<BorderColorOutlinedIcon />}
                      >
                        Edit
                      </Button>
                      <Button
                        color="error"
                        disabled={busy}
                        onClick={() => handleDelete(item)}
                        size="small"
                        startIcon={<BackspaceOutlinedIcon />}
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
      </Box>
    </Stack>
  );
}
