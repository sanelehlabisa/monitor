import {
  Box,
  Button,
  CircularProgress,
  Container,
  CssBaseline,
  Stack,
  ThemeProvider,
  Typography,
  createTheme,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import { useEffect, useRef, useState } from 'react';
import type { FormEvent } from 'react';

import { LoginPanel, SignedInPanel, type LoginStep } from './AuthPanels';
import { ForecastPanel } from './ForecastPanel';
import { LedgerPanel, type LedgerItem } from './LedgerPanel';
import { MeterWorkspace, type AdminMeterView } from './MeterWorkspace';
import { Navigation } from './Navigation';
import { isMeterListPath, meterIdFromPath } from './meterRoute';
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
  listMeters,
  logout,
  renameMeter,
  requestOtp,
  updateBalance,
  updateTopUp,
  verifyOtp,
  type BalanceEntry,
  type Dashboard,
  type Forecast,
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
  typography: {
    fontFamily: 'Arial, sans-serif',
    body1: { fontSize: '0.875rem', lineHeight: 1.5 },
    body2: { fontSize: '0.875rem', lineHeight: 1.5 },
    caption: { fontSize: '0.875rem', lineHeight: 1.5 },
    subtitle1: { fontSize: '0.875rem' },
    subtitle2: { fontSize: '0.875rem' },
    button: { fontSize: '0.875rem' },
    h4: { fontSize: '1.125rem' },
    h5: { fontSize: '1.25rem' },
    h6: { fontSize: '1.125rem' },
  },
  shape: { borderRadius: 12 },
  components: {
    MuiCard: {
      styleOverrides: {
        root: { boxShadow: '0 1px 4px rgba(0, 0, 0, 0.1)' },
      },
    },
    MuiButton: {
      defaultProps: { disableElevation: true, size: 'small' },
      styleOverrides: {
        root: { textTransform: 'none' },
        sizeSmall: { fontSize: '0.875rem' },
        sizeMedium: { fontSize: '0.875rem' },
        sizeLarge: { fontSize: '0.875rem' },
      },
    },
    MuiTextField: { defaultProps: { size: 'small' } },
    MuiTab: { styleOverrides: { root: { textTransform: 'none' } } },
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
  const [meterSearch, setMeterSearch] = useState('');
  const [balances, setBalances] = useState<BalanceEntry[]>([]);
  const [topUps, setTopUps] = useState<TopUpEntry[]>([]);
  const [ledgerLoading, setLedgerLoading] = useState(false);
  const [ledgerBusy, setLedgerBusy] = useState(false);
  const [ledgerError, setLedgerError] = useState('');
  const [forecast, setForecast] = useState<Forecast | null>(null);
  const [meterPath, setMeterPath] = useState(() =>
    typeof window === 'undefined' ? '/' : window.location.pathname,
  );
  const dashboardVersion = useRef(0);

  useEffect(() => {
    const onPopState = () => setMeterPath(window.location.pathname);
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

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
      clearMeterWorkspace();
      setMeterSearch('');
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

  useEffect(() => {
    if (!user) return;
    if (isMeterListPath(meterPath) && meterPath !== '/meters') {
      window.history.replaceState(null, '', '/meters');
      setMeterPath('/meters');
      return;
    }
    const meterId = meterIdFromPath(meterPath);
    if (meterId) {
      void loadMeter(meterId);
    } else {
      clearMeterWorkspace();
      if (!isMeterListPath(meterPath)) setMeterError('That meter is unavailable. Return to the meter list.');
    }
  }, [user, meterPath]);

  function clearMeterWorkspace() {
    dashboardVersion.current += 1;
    setMeterBusy(false);
    setLedgerLoading(false);
    setSelectedMeter(null);
    setEditMeterName('');
    setMeterError('');
    setLedgerError('');
    setBalances([]);
    setTopUps([]);
    setForecast(null);
  }

  function navigateToMeter(meterId: string | null) {
    const path = meterId ? `/meters/${meterId}` : '/meters';
    if (meterId && path === meterPath) {
      void loadMeter(meterId);
      return;
    }
    if (window.location.pathname !== path) window.history.pushState(null, '', path);
    setMeterPath(path);
  }

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
      dashboardVersion.current += 1;
      setUser(null);
      navigateToMeter(null);
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
      setMeterName('');
      if (meterSearch.trim()) {
        setMeterSearch('');
        try {
          setMeters(await listMeters());
        } catch {
          setMeters((current) => [...current, meter]);
          setMeterError('Meter added, but the full list could not be reloaded.');
        }
      } else {
        setMeters((current) =>
          [...current, meter].sort((left, right) =>
            left.name.localeCompare(right.name, undefined, { sensitivity: 'base' }),
          ),
        );
      }
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

  async function handleSearchMeters(event?: FormEvent<HTMLFormElement>) {
    event?.preventDefault();
    setMetersLoading(true);
    setMeterError('');
    try {
      setMeters(await listMeters(meterSearch));
    } catch {
      setMeterError('Meters could not be searched. Try again.');
    } finally {
      setMetersLoading(false);
    }
  }

  async function handleClearMeterSearch() {
    setMeterSearch('');
    setMetersLoading(true);
    setMeterError('');
    try {
      setMeters(await listMeters());
    } catch {
      setMeterError('Meters could not be loaded. Try again.');
    } finally {
      setMetersLoading(false);
    }
  }

  async function loadMeter(meterId: string) {
    clearMeterWorkspace();
    const version = dashboardVersion.current;
    setMeterBusy(true);
    setLedgerLoading(true);
    try {
      const selected = await getMeter(meterId);
      if (version !== dashboardVersion.current) return;
      setSelectedMeter(selected);
      setEditMeterName(selected.name);
      await loadDashboard(selected.id, false, version);
    } catch (requestError) {
      if (version === dashboardVersion.current) {
        setMeterError(requestError instanceof ApiError && requestError.status === 404
          ? 'That meter is unavailable. Return to the meter list.'
          : 'That meter could not be opened. Try again.');
      }
    } finally {
      if (version === dashboardVersion.current) {
        setMeterBusy(false);
        setLedgerLoading(false);
      }
    }
  }

  function applyDashboard(dashboard: Dashboard) {
    setBalances(dashboard.balances);
    setTopUps(dashboard.top_ups);
    setForecast(dashboard.forecast);
  }

  async function loadDashboard(
    meterId: string,
    saved = false,
    version = dashboardVersion.current,
  ) {
    // Navigation invalidates earlier reads, including a reload after a saved write.
    if (version !== dashboardVersion.current) return;
    setLedgerLoading(true);
    setLedgerError('');
    setForecast(null);
    try {
      const dashboard = await getDashboard(meterId);
      if (version === dashboardVersion.current) applyDashboard(dashboard);
    } catch {
      if (version === dashboardVersion.current) {
        setLedgerError(
          saved
            ? 'The change was saved, but updated estimates could not be loaded. Refresh to try again.'
            : 'This meter history could not be loaded. Refresh to try again.',
        );
      }
    } finally {
      if (version === dashboardVersion.current) setLedgerLoading(false);
    }
  }

  async function handleCreateBalance(kwh: string, occurredAt: string) {
    if (!selectedMeter) return false;
    const version = dashboardVersion.current;
    setLedgerBusy(true);
    setLedgerError('');
    try {
      const entry = await createBalance(selectedMeter.id, kwh, occurredAt);
      if (version !== dashboardVersion.current) return true;
      setBalances((current) => newestFirst([...current, entry]));
      await loadDashboard(selectedMeter.id, true, version);
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
    const version = dashboardVersion.current;
    setLedgerBusy(true);
    setLedgerError('');
    try {
      const entry = await createTopUp(selectedMeter.id, kwh, occurredAt);
      if (version !== dashboardVersion.current) return true;
      setTopUps((current) => newestFirst([...current, entry]));
      await loadDashboard(selectedMeter.id, true, version);
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
    const version = dashboardVersion.current;
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
        if (version !== dashboardVersion.current) return true;
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
        if (version !== dashboardVersion.current) return true;
        setTopUps((current) =>
          newestFirst(
            current.map((existing) =>
              existing.id === entry.id ? entry : existing,
            ),
          ),
        );
      }
      await loadDashboard(selectedMeter.id, true, version);
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
    const version = dashboardVersion.current;
    setLedgerBusy(true);
    setLedgerError('');
    try {
      if (item.kind === 'balance') {
        await deleteBalance(selectedMeter.id, item.entry.id);
        if (version !== dashboardVersion.current) return true;
        setBalances((current) =>
          current.filter((entry) => entry.id !== item.entry.id),
        );
      } else {
        await deleteTopUp(selectedMeter.id, item.entry.id);
        if (version !== dashboardVersion.current) return true;
        setTopUps((current) =>
          current.filter((entry) => entry.id !== item.entry.id),
        );
      }
      await loadDashboard(selectedMeter.id, true, version);
      return true;
    } catch (requestError) {
      setLedgerError(ledgerFailure(requestError, 'entry'));
      return false;
    } finally {
      setLedgerBusy(false);
    }
  }

  async function handleRenameMeter(meter: Meter, name: string) {
    if (meterBusy || ledgerBusy) return false;
    const version = dashboardVersion.current;
    setMeterBusy(true);
    setMeterError('');
    try {
      const renamed = await renameMeter(meter.id, name);
      setSelectedMeter((current) => current?.id === renamed.id ? renamed : current);
      if (version === dashboardVersion.current && selectedMeter?.id === meter.id) setEditMeterName(renamed.name);
      setMeters((current) =>
        current
          .map((meter) => (meter.id === renamed.id ? renamed : meter))
          .sort((left, right) =>
            left.name.localeCompare(right.name, undefined, { sensitivity: 'base' }),
          ),
      );
      if (meterSearch.trim()) {
        try {
          setMeters(await listMeters(meterSearch));
        } catch {
          setMeterError('Name saved, but the list could not be reloaded. Search again.');
        }
      }
      return true;
    } catch (requestError) {
      setMeterError(
        requestError instanceof ApiError && requestError.status === 409
          ? 'That owner already has a meter with this name.'
          : 'The meter could not be renamed. Try again.',
      );
      return false;
    } finally {
      if (version === dashboardVersion.current) setMeterBusy(false);
    }
  }

  async function handleDeleteMeter(meter: Meter) {
    if (meterBusy || ledgerBusy || !window.confirm(`Delete ${meter.name}? This also deletes its balance and top-up records.`)) return;
    setMeterBusy(true);
    setMeterError('');
    try {
      await deleteMeter(meter.id);
      setMeters((current) =>
        current.filter((existing) => existing.id !== meter.id),
      );
      if (selectedMeter?.id === meter.id) {
        navigateToMeter(null);
        clearMeterWorkspace();
      }
    } catch {
      setMeterError('The meter could not be deleted. Try again.');
    } finally {
      setMeterBusy(false);
    }
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth={user ? 'lg' : 'xs'}>
        <Box component="main" sx={{ minHeight: '100vh', py: { xs: 3, sm: 4 } }}>
          <Stack spacing={3}>
            <Navigation user={user} busy={busy || meterBusy || ledgerBusy} onLogout={handleLogout}
              onBack={!isMeterListPath(meterPath) ? () => navigateToMeter(null) : undefined} />
            {loading ? (
              <Box sx={{ display: 'grid', minHeight: 240, placeItems: 'center' }}>
                <CircularProgress aria-label="Loading your session" color="inherit" />
              </Box>
            ) : user ? (
              <SignedInPanel
                error={error}
                meterId={meterIdFromPath(meterPath) ?? undefined}
                adminView={adminMeterView}
                busy={meterBusy || metersLoading || ledgerBusy}
                onAdminViewChange={setAdminMeterView}
                user={user}
              >
                {meterBusy && !selectedMeter && !isMeterListPath(meterPath) ? (
                  <Box sx={{ display: 'grid', minHeight: 160, placeItems: 'center' }}>
                    <CircularProgress aria-label="Loading meter" color="inherit" />
                  </Box>
                ) : <MeterWorkspace key={selectedMeter?.id ?? 'list'}
                  adminView={adminMeterView}
                  busy={meterBusy || ledgerBusy}
                  currentUserEmail={user.email}
                  editName={editMeterName}
                  error={meterError}
                  isAdmin={user.is_admin}
                  loading={metersLoading}
                  meters={meters}
                  name={meterName}
                  onClearSearch={handleClearMeterSearch}
                  onCreate={handleCreateMeter}
                  onDelete={handleDeleteMeter}
                  onEditNameChange={setEditMeterName}
                  onNameChange={setMeterName}
                  onRename={handleRenameMeter}
                  onSearch={handleSearchMeters}
                  onSearchChange={setMeterSearch}
                  onSelect={(meter) => navigateToMeter(meter.id)}
                  selectedContent={
                    selectedMeter ? (
                      <Stack key={selectedMeter.id} spacing={2.5}>
                        <ForecastPanel
                          forecast={forecast}
                          loading={ledgerLoading}
                        />
                        <LedgerPanel
                          balances={balances}
                          busy={ledgerBusy || meterBusy}
                          error={ledgerError}
                          loading={ledgerLoading}
                          onCreateBalance={handleCreateBalance}
                          onCreateTopUp={handleCreateTopUp}
                          onDelete={handleDeleteEntry}
                          onUpdate={handleUpdateEntry}
                          topUps={topUps}
                        />
                        <Button
                          disabled={ledgerLoading || ledgerBusy || meterBusy}
                          onClick={() => loadDashboard(selectedMeter.id)}
                          size="small"
                          startIcon={<RefreshIcon />}
                          sx={{ alignSelf: 'flex-end' }}
                        >
                          Refresh
                        </Button>
                      </Stack>
                    ) : undefined
                  }
                  selectedMeter={selectedMeter}
                  search={meterSearch}
                />}
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
