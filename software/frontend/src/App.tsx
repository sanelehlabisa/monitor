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
import { ForecastPanel } from './ForecastPanel';
import { LedgerPanel, type LedgerItem } from './LedgerPanel';
import { MeterWorkspace, type AdminMeterView } from './MeterWorkspace';
import { ReminderSettingsPanel } from './ReminderSettingsPanel';
import {
  ApiError,
  createBalance,
  createMeter,
  createTopUp,
  deleteBalance,
  deleteMeter,
  deleteTopUp,
  getCurrentUser,
  getDashboard,
  getMeter,
  getReminderSettings,
  listMeters,
  logout,
  renameMeter,
  requestOtp,
  updateBalance,
  updateReminderSettings,
  updateTopUp,
  verifyOtp,
  type BalanceEntry,
  type Dashboard,
  type Forecast,
  type Meter,
  type ReminderSettings,
  type ReminderSettingsInput,
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
  const [adminMeterView, setAdminMeterView] = useState<AdminMeterView>('mine');
  const [balances, setBalances] = useState<BalanceEntry[]>([]);
  const [topUps, setTopUps] = useState<TopUpEntry[]>([]);
  const [ledgerLoading, setLedgerLoading] = useState(false);
  const [ledgerBusy, setLedgerBusy] = useState(false);
  const [ledgerError, setLedgerError] = useState('');
  const [forecast, setForecast] = useState<Forecast | null>(null);
  const [reminderSettings, setReminderSettings] =
    useState<ReminderSettings | null>(null);
  const [reminderLoading, setReminderLoading] = useState(false);
  const [reminderBusy, setReminderBusy] = useState(false);
  const [reminderError, setReminderError] = useState('');
  const [reminderNotice, setReminderNotice] = useState('');

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
      setForecast(null);
      setReminderSettings(null);
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
      setAdminMeterView('mine');
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
    setReminderLoading(true);
    setMeterError('');
    setLedgerError('');
    setReminderError('');
    setReminderNotice('');
    setBalances([]);
    setTopUps([]);
    setForecast(null);
    setReminderSettings(null);
    try {
      const selected = await getMeter(meter.id);
      setSelectedMeter(selected);
      setEditMeterName(selected.name);
      await Promise.all([
        getDashboard(selected.id)
          .then(applyDashboard)
          .catch(() => setLedgerError('This meter history could not be loaded. Try again.')),
        getReminderSettings(selected.id)
          .then(setReminderSettings)
          .catch(() => setReminderError('Reminder settings could not be loaded. Try again.')),
      ]);
    } catch {
      setMeterError('That meter could not be opened. Try again.');
    } finally {
      setMeterBusy(false);
      setLedgerLoading(false);
      setReminderLoading(false);
    }
  }

  function applyDashboard(dashboard: Dashboard) {
    setBalances(dashboard.balances);
    setTopUps(dashboard.top_ups);
    setForecast(dashboard.forecast);
  }

  async function refreshDashboardAfterMutation(meterId: string) {
    try {
      applyDashboard(await getDashboard(meterId));
    } catch {
      setLedgerError(
        'The change was saved, but updated estimates could not be loaded. Reopen the meter.',
      );
    }
  }

  async function handleCreateBalance(kwh: string, occurredAt: string) {
    if (!selectedMeter) return false;
    setLedgerBusy(true);
    setLedgerError('');
    try {
      const entry = await createBalance(selectedMeter.id, kwh, occurredAt);
      setBalances((current) => newestFirst([...current, entry]));
      await refreshDashboardAfterMutation(selectedMeter.id);
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
      await refreshDashboardAfterMutation(selectedMeter.id);
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
      await refreshDashboardAfterMutation(selectedMeter.id);
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
      await refreshDashboardAfterMutation(selectedMeter.id);
      return true;
    } catch (requestError) {
      setLedgerError(ledgerFailure(requestError, 'entry'));
      return false;
    } finally {
      setLedgerBusy(false);
    }
  }

  async function handleSaveReminders(input: ReminderSettingsInput) {
    if (!selectedMeter) return false;
    setReminderBusy(true);
    setReminderError('');
    setReminderNotice('');
    try {
      setReminderSettings(await updateReminderSettings(selectedMeter.id, input));
      setReminderNotice('Reminder settings saved.');
      return true;
    } catch (requestError) {
      setReminderError(
        requestError instanceof ApiError && requestError.status === 422
          ? 'Check the reminder day, lead time and timezone.'
          : requestError instanceof ApiError && requestError.status === 404
            ? 'That meter is no longer available. Return to the meter list.'
            : 'Reminder settings could not be saved. Try again.',
      );
      return false;
    } finally {
      setReminderBusy(false);
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
      setForecast(null);
      setReminderSettings(null);
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
                  adminView={adminMeterView}
                  busy={meterBusy}
                  currentUserEmail={user.email}
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
                    setForecast(null);
                    setReminderSettings(null);
                    setReminderError('');
                    setReminderNotice('');
                  }}
                  onAdminViewChange={setAdminMeterView}
                  onCreate={handleCreateMeter}
                  onDelete={handleDeleteMeter}
                  onEditNameChange={setEditMeterName}
                  onNameChange={setMeterName}
                  onRename={handleRenameMeter}
                  onSelect={handleSelectMeter}
                  selectedContent={
                    selectedMeter ? (
                      <Stack key={selectedMeter.id} spacing={2.5}>
                        <ForecastPanel
                          forecast={forecast}
                          loading={ledgerLoading}
                        />
                        <LedgerPanel
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
                        <ReminderSettingsPanel
                          busy={reminderBusy}
                          error={reminderError}
                          loading={reminderLoading}
                          notice={reminderNotice}
                          onSave={handleSaveReminders}
                          settings={reminderSettings}
                        />
                      </Stack>
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
