import {
  Box,
  CircularProgress,
  Container,
  CssBaseline,
  Stack,
  ThemeProvider,
  Typography,
  createTheme,
} from '@mui/material';
import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';

import { LoginPanel, SignedInPanel, type LoginStep } from './AuthPanels';
import { LedgerPanel, type LedgerItem } from './LedgerPanel';
import { MeterWorkspace } from './MeterWorkspace';
import {
  ApiError,
  createBalance,
  createMeter,
  createTopUp,
  deleteBalance,
  deleteMeter,
  deleteTopUp,
  getCurrentUser,
  getMeter,
  listBalances,
  listMeters,
  listTopUps,
  logout,
  renameMeter,
  requestOtp,
  updateBalance,
  updateTopUp,
  verifyOtp,
  type BalanceEntry,
  type Meter,
  type TopUpEntry,
  type User,
} from './api';

function newestFirst<T extends { occurred_at: string; id: string }>(items: T[]): T[] {
  return [...items].sort(
    (left, right) =>
      right.occurred_at.localeCompare(left.occurred_at) ||
      right.id.localeCompare(left.id),
  );
}

function ledgerFailure(error: unknown, action: string): string {
  if (error instanceof ApiError && error.status === 409) {
    return 'An actual balance already exists at that date and time.';
  }
  if (error instanceof ApiError && error.status === 422) {
    return 'Check the kWh value and date. Future dates are not allowed.';
  }
  if (error instanceof ApiError && error.status === 404) {
    return 'That entry or meter is no longer available. Return to the meter list.';
  }
  return `The ${action} could not be completed. Try again.`;
}

const theme = createTheme({
  palette: {
    primary: { main: '#1c1e21' },
    secondary: { main: '#b8860b' },
    background: { default: '#f2f4f7' },
  },
  shape: { borderRadius: 12 },
  components: {
    MuiCard: {
      styleOverrides: {
        root: { boxShadow: '0 1px 4px rgba(0, 0, 0, 0.1)' },
      },
    },
    MuiButton: { defaultProps: { disableElevation: true } },
  },
});

export default function App() {
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [step, setStep] = useState<LoginStep>('email');
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');
  const [user, setUser] = useState<User | null>(null);
  const [meters, setMeters] = useState<Meter[]>([]);
  const [selectedMeter, setSelectedMeter] = useState<Meter | null>(null);
  const [meterName, setMeterName] = useState('');
  const [editMeterName, setEditMeterName] = useState('');
  const [metersLoading, setMetersLoading] = useState(false);
  const [meterBusy, setMeterBusy] = useState(false);
  const [meterError, setMeterError] = useState('');
  const [balances, setBalances] = useState<BalanceEntry[]>([]);
  const [topUps, setTopUps] = useState<TopUpEntry[]>([]);
  const [ledgerLoading, setLedgerLoading] = useState(false);
  const [ledgerBusy, setLedgerBusy] = useState(false);
  const [ledgerError, setLedgerError] = useState('');

  useEffect(() => {
    let active = true;
    getCurrentUser()
      .then((currentUser) => {
        if (active) setUser(currentUser);
      })
      .catch(() => {
        if (active) setError('Monitor could not be reached. Please try again.');
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (!user) {
      setMeters([]);
      setSelectedMeter(null);
      setBalances([]);
      setTopUps([]);
      return;
    }
    let active = true;
    setMetersLoading(true);
    setMeterError('');
    listMeters()
      .then((items) => {
        if (active) setMeters(items);
      })
      .catch(() => {
        if (active) setMeterError('Your meters could not be loaded. Try again.');
      })
      .finally(() => {
        if (active) setMetersLoading(false);
      });
    return () => {
      active = false;
    };
  }, [user]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError('');
    setNotice('');
    try {
      if (step === 'email') {
        await requestOtp(email);
        setStep('code');
        setNotice('If the address can receive email, a sign-in code was sent.');
      } else {
        setUser(await verifyOtp(email, code));
        setCode('');
      }
    } catch (requestError) {
      setError(
        requestError instanceof ApiError && requestError.status === 401
          ? 'That code is invalid or expired. Request a new code and try again.'
          : 'Something went wrong. Please try again.',
      );
    } finally {
      setBusy(false);
    }
  }

  async function handleResend() {
    setBusy(true);
    setError('');
    try {
      await requestOtp(email);
      setNotice('If the address can receive email, a new sign-in code was sent.');
    } catch {
      setError('Something went wrong. Please try again.');
    } finally {
      setBusy(false);
    }
  }

  function handleChangeEmail() {
    setStep('email');
    setCode('');
    setNotice('');
    setError('');
  }

  async function handleLogout() {
    setBusy(true);
    setError('');
    try {
      await logout();
      setUser(null);
      setStep('email');
      setEmail('');
    } catch {
      setError('Sign out failed. Please try again.');
    } finally {
      setBusy(false);
    }
  }

  async function handleCreateMeter(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMeterBusy(true);
    setMeterError('');
    try {
      const meter = await createMeter(meterName);
      setMeters((current) =>
        [...current, meter].sort((left, right) =>
          left.name.localeCompare(right.name, undefined, { sensitivity: 'base' }),
        ),
      );
      setMeterName('');
    } catch (requestError) {
      setMeterError(
        requestError instanceof ApiError && requestError.status === 409
          ? 'You already have a meter with that name.'
          : 'The meter could not be added. Check the name and try again.',
      );
    } finally {
      setMeterBusy(false);
    }
  }

  async function handleSelectMeter(meter: Meter) {
    setMeterBusy(true);
    setLedgerLoading(true);
    setMeterError('');
    setLedgerError('');
    setBalances([]);
    setTopUps([]);
    try {
      const selected = await getMeter(meter.id);
      const [actualBalances, purchasedTopUps] = await Promise.all([
        listBalances(selected.id),
        listTopUps(selected.id),
      ]);
      setSelectedMeter(selected);
      setEditMeterName(selected.name);
      setBalances(actualBalances);
      setTopUps(purchasedTopUps);
    } catch {
      setMeterError('That meter or its history could not be opened. Try again.');
    } finally {
      setMeterBusy(false);
      setLedgerLoading(false);
    }
  }

  async function handleCreateBalance(kwh: string, occurredAt: string) {
    if (!selectedMeter) return false;
    setLedgerBusy(true);
    setLedgerError('');
    try {
      const entry = await createBalance(selectedMeter.id, kwh, occurredAt);
      setBalances((current) => newestFirst([...current, entry]));
      return true;
    } catch (requestError) {
      setLedgerError(ledgerFailure(requestError, 'balance'));
      return false;
    } finally {
      setLedgerBusy(false);
    }
  }

  async function handleCreateTopUp(kwh: string, occurredAt: string) {
    if (!selectedMeter) return false;
    setLedgerBusy(true);
    setLedgerError('');
    try {
      const entry = await createTopUp(selectedMeter.id, kwh, occurredAt);
      setTopUps((current) => newestFirst([...current, entry]));
      return true;
    } catch (requestError) {
      setLedgerError(ledgerFailure(requestError, 'top-up'));
      return false;
    } finally {
      setLedgerBusy(false);
    }
  }

  async function handleUpdateEntry(
    item: LedgerItem,
    kwh: string,
    occurredAt: string,
  ) {
    if (!selectedMeter) return false;
    setLedgerBusy(true);
    setLedgerError('');
    try {
      if (item.kind === 'balance') {
        const entry = await updateBalance(
          selectedMeter.id,
          item.entry.id,
          kwh,
          occurredAt,
        );
        setBalances((current) =>
          newestFirst(
            current.map((existing) =>
              existing.id === entry.id ? entry : existing,
            ),
          ),
        );
      } else {
        const entry = await updateTopUp(
          selectedMeter.id,
          item.entry.id,
          kwh,
          occurredAt,
        );
        setTopUps((current) =>
          newestFirst(
            current.map((existing) =>
              existing.id === entry.id ? entry : existing,
            ),
          ),
        );
      }
      return true;
    } catch (requestError) {
      setLedgerError(ledgerFailure(requestError, 'correction'));
      return false;
    } finally {
      setLedgerBusy(false);
    }
  }

  async function handleDeleteEntry(item: LedgerItem) {
    if (!selectedMeter) return false;
    setLedgerBusy(true);
    setLedgerError('');
    try {
      if (item.kind === 'balance') {
        await deleteBalance(selectedMeter.id, item.entry.id);
        setBalances((current) =>
          current.filter((entry) => entry.id !== item.entry.id),
        );
      } else {
        await deleteTopUp(selectedMeter.id, item.entry.id);
        setTopUps((current) =>
          current.filter((entry) => entry.id !== item.entry.id),
        );
      }
      return true;
    } catch (requestError) {
      setLedgerError(ledgerFailure(requestError, 'entry'));
      return false;
    } finally {
      setLedgerBusy(false);
    }
  }

  async function handleRenameMeter(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedMeter) return;
    setMeterBusy(true);
    setMeterError('');
    try {
      const renamed = await renameMeter(selectedMeter.id, editMeterName);
      setSelectedMeter(renamed);
      setEditMeterName(renamed.name);
      setMeters((current) =>
        current
          .map((meter) => (meter.id === renamed.id ? renamed : meter))
          .sort((left, right) =>
            left.name.localeCompare(right.name, undefined, { sensitivity: 'base' }),
          ),
      );
    } catch (requestError) {
      setMeterError(
        requestError instanceof ApiError && requestError.status === 409
          ? 'That owner already has a meter with this name.'
          : 'The meter could not be renamed. Try again.',
      );
    } finally {
      setMeterBusy(false);
    }
  }

  async function handleDeleteMeter() {
    if (!selectedMeter || !window.confirm(`Delete ${selectedMeter.name}?`)) return;
    setMeterBusy(true);
    setMeterError('');
    try {
      await deleteMeter(selectedMeter.id);
      setMeters((current) =>
        current.filter((meter) => meter.id !== selectedMeter.id),
      );
      setSelectedMeter(null);
      setEditMeterName('');
      setBalances([]);
      setTopUps([]);
    } catch {
      setMeterError('The meter could not be deleted. Try again.');
    } finally {
      setMeterBusy(false);
    }
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="xs">
        <Box component="main" sx={{ minHeight: '100vh', py: { xs: 4, sm: 7 } }}>
          <Stack spacing={3}>
            <Stack spacing={1} sx={{ alignItems: 'center' }}>
              <Box
                alt="Roventics"
                component="img"
                src="/roventics-logo.png"
                sx={{ height: 64, width: 64 }}
              />
              <Typography sx={{ fontWeight: 800 }} variant="h6">
                Roventics Monitor
              </Typography>
            </Stack>
            {loading ? (
              <Box sx={{ display: 'grid', minHeight: 240, placeItems: 'center' }}>
                <CircularProgress aria-label="Loading your session" color="inherit" />
              </Box>
            ) : user ? (
              <SignedInPanel
                busy={busy}
                error={error}
                onLogout={handleLogout}
                user={user}
              >
                <MeterWorkspace
                  busy={meterBusy}
                  editName={editMeterName}
                  error={meterError}
                  isAdmin={user.is_admin}
                  loading={metersLoading}
                  meters={meters}
                  name={meterName}
                  onBack={() => {
                    setSelectedMeter(null);
                    setMeterError('');
                    setLedgerError('');
                    setBalances([]);
                    setTopUps([]);
                  }}
                  onCreate={handleCreateMeter}
                  onDelete={handleDeleteMeter}
                  onEditNameChange={setEditMeterName}
                  onNameChange={setMeterName}
                  onRename={handleRenameMeter}
                  onSelect={handleSelectMeter}
                  selectedContent={
                    selectedMeter ? (
                      <LedgerPanel
                        key={selectedMeter.id}
                        balances={balances}
                        busy={ledgerBusy}
                        error={ledgerError}
                        loading={ledgerLoading}
                        onCreateBalance={handleCreateBalance}
                        onCreateTopUp={handleCreateTopUp}
                        onDelete={handleDeleteEntry}
                        onUpdate={handleUpdateEntry}
                        topUps={topUps}
                      />
                    ) : undefined
                  }
                  selectedMeter={selectedMeter}
                />
              </SignedInPanel>
            ) : (
              <LoginPanel
                busy={busy}
                code={code}
                email={email}
                error={error}
                notice={notice}
                onChangeEmail={handleChangeEmail}
                onCodeChange={setCode}
                onEmailChange={setEmail}
                onResend={handleResend}
                onSubmit={handleSubmit}
                step={step}
              />
            )}
            <Typography
              align="center"
              color="text.secondary"
              sx={{ display: 'block', px: 2 }}
              variant="caption"
            >
              Manual kWh planning. No hardware or meter modification required.
            </Typography>
          </Stack>
        </Box>
      </Container>
    </ThemeProvider>
  );
}
