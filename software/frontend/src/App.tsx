import {
  Box,
  Button,
  CircularProgress,
  Container,
  CssBaseline,
  Stack,
  ThemeProvider,
  Typography,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import { useEffect, useRef, useState } from 'react';
import type { FormEvent } from 'react';

import { LoginPage, type LoginStep } from './routes/login/LoginPage';
import { MeterSearch } from './routes/meters/components/MeterSearch';
import { MeterSection } from './routes/meters/components/MeterSection';
import { ForecastPanel } from './routes/meters/components/ForecastPanel';
import { LedgerPanel, type LedgerItem } from './routes/meters/components/LedgerPanel';
import { SharingPanel } from './routes/meters/components/SharingPanel';
import { MetersPage, type AdminMeterView } from './routes/meters/MetersPage';
import { MeterDetailsPage } from './routes/meters/MeterDetailsPage';
import { theme } from './lib/theme';
import { Navigation } from './components/Navigation';
import { isMeterListPath, meterIdFromPath } from './routes/meters/meterRoute';
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
} from './lib/api';

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
  const [unfilteredMeters, setUnfilteredMeters] = useState<Meter[]>([]);
  const [selectedMeter, setSelectedMeter] = useState<Meter | null>(null);
  const [meterName, setMeterName] = useState('');
  const [editMeterName, setEditMeterName] = useState('');
  const [metersLoading, setMetersLoading] = useState(false);
  const [meterBusy, setMeterBusy] = useState(false);
  const [meterError, setMeterError] = useState('');
  const [adminMeterView, setAdminMeterView] = useState<AdminMeterView>('mine');
  const [meterSearch, setMeterSearch] = useState('');
  const [appliedMeterSearch, setAppliedMeterSearch] = useState('');
  const meterFilterActive = Boolean(appliedMeterSearch);
  const [balances, setBalances] = useState<BalanceEntry[]>([]);
  const [topUps, setTopUps] = useState<TopUpEntry[]>([]);
  const [ledgerLoading, setLedgerLoading] = useState(false);
  const [ledgerBusy, setLedgerBusy] = useState(false);
  const [sharingBusy, setSharingBusy] = useState(false);
  const [ledgerError, setLedgerError] = useState('');
  const [forecast, setForecast] = useState<Forecast | null>(null);
  const [meterPath, setMeterPath] = useState(() =>
    typeof window === 'undefined' ? '/' : window.location.pathname,
  );
  const dashboardVersion = useRef(0);
  const meterListVersion = useRef(0);
  const reloadOnReturn = useRef(false);
  const rolloverRefresh = useRef('');
  const meterCount = unfilteredMeters.length;

  function listInView(query = '', view = adminMeterView) {
    return listMeters(query, !user?.is_admin || view === 'mine');
  }

  function setFullMeterList(items: Meter[]) {
    setMeters(items);
    setUnfilteredMeters(items);
    setAppliedMeterSearch('');
  }

  useEffect(() => {
    const onPopState = () => { dashboardVersion.current += 1; setMeterPath(window.location.pathname); };
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
    const version = ++meterListVersion.current;
    if (!user) {
      reloadOnReturn.current = false;
      setFullMeterList([]);
      setMetersLoading(false);
      clearMeterWorkspace();
      setMeterSearch('');
      return;
    }
    let active = true;
    setMetersLoading(true);
    setMeterError('');
    listInView()
      .then((items) => {
        if (active && version === meterListVersion.current) setFullMeterList(items);
      })
      .catch(() => {
        if (active && version === meterListVersion.current) setMeterError('Your meters could not be loaded. Try again.');
      })
      .finally(() => {
        if (active && version === meterListVersion.current) setMetersLoading(false);
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
      if (isMeterListPath(meterPath) && reloadOnReturn.current) {
        reloadOnReturn.current = false;
        void reloadMeterList(appliedMeterSearch);
      }
      if (!isMeterListPath(meterPath)) setMeterError('That meter is unavailable. Return to the meter list.');
    }
  }, [user, meterPath]);

  useEffect(() => {
    if (!user || !selectedMeter || !forecast || busy || meterBusy || ledgerBusy || sharingBusy || ledgerLoading || ledgerError) return;
    const deadline = Date.parse(forecast.planning_at);
    if (!Number.isFinite(deadline)) return;
    const version = dashboardVersion.current;
    const meterId = selectedMeter.id;
    const key = `${user.id}:${meterId}:${version}:${deadline}`;
    let active = true;
    let timer: number | undefined;
    function refreshIfDue() {
      if (!active || version !== dashboardVersion.current || rolloverRefresh.current === key) return;
      window.clearTimeout(timer);
      const remaining = deadline - Date.now();
      if (remaining <= 0) {
        // One automatic read per expired cycle; failures keep the manual Retry path.
        rolloverRefresh.current = key;
        void loadDashboard(meterId, false, version);
      } else {
        // Cap long waits to avoid the browser's maximum timeout delay; no API polling.
        timer = window.setTimeout(refreshIfDue, Math.min(remaining, 86_400_000));
      }
    }
    const onVisible = () => { if (document.visibilityState === 'visible') refreshIfDue(); };
    refreshIfDue();
    window.addEventListener('focus', refreshIfDue);
    document.addEventListener('visibilitychange', onVisible);
    return () => {
      active = false;
      window.clearTimeout(timer);
      window.removeEventListener('focus', refreshIfDue);
      document.removeEventListener('visibilitychange', onVisible);
    };
  }, [user?.id, selectedMeter?.id, forecast?.planning_at, busy, meterBusy, ledgerBusy, sharingBusy, ledgerLoading, ledgerError]);

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
    if (window.location.pathname !== path) {
      dashboardVersion.current += 1;
      window.history.pushState(null, '', path);
    }
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
      meterListVersion.current += 1;
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
    const listVersion = meterListVersion.current;
    setMeterBusy(true);
    setMeterError('');
    try {
      const meter = await createMeter(meterName);
      if (listVersion !== meterListVersion.current) return;
      setMeterName('');
      setUnfilteredMeters((current) => [...current, meter]);
      if (meterSearch.trim() || meterFilterActive) {
        setMeterSearch('');
        try {
          const items = await listInView();
          if (listVersion === meterListVersion.current) setFullMeterList(items);
        } catch {
          if (listVersion !== meterListVersion.current) return;
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
      if (listVersion !== meterListVersion.current) return;
      setMeterError(
        requestError instanceof ApiError && requestError.status === 409
          ? 'You already have a meter with that name.'
          : 'The meter could not be added. Check the name and try again.',
      );
    } finally {
      if (listVersion === meterListVersion.current) setMeterBusy(false);
    }
  }

  async function handleSearchMeters(event?: FormEvent<HTMLFormElement>) {
    event?.preventDefault();
    await reloadMeterList(meterSearch);
  }

  async function reloadMeterList(query = appliedMeterSearch, view = adminMeterView, reportError = true, workspace?: number) {
    const version = ++meterListVersion.current;
    const current = () => version === meterListVersion.current && (workspace === undefined || workspace === dashboardVersion.current);
    setMetersLoading(true);
    if (reportError) setMeterError('');
    try {
      const [items, fullList] = await Promise.all([
        listInView(query, view),
        workspace !== undefined && query.trim() ? listInView('', view) : Promise.resolve(null),
      ]);
      if (!current()) return false;
      if (fullList) setUnfilteredMeters(fullList);
      if (query.trim()) { setMeters(items); setAppliedMeterSearch(query.trim()); }
      else setFullMeterList(items);
      return true;
    } catch {
      if (reportError && current()) setMeterError('Meters could not be loaded. Retry to refresh the list.');
      return false;
    } finally {
      // Release only this list request's busy flag, without changing a newer view's data/errors.
      if (version === meterListVersion.current) setMetersLoading(false);
    }
  }

  async function handleClearMeterSearch(view = adminMeterView) {
    setMeterSearch('');
    await reloadMeterList('', view);
  }

  async function handleSharingChanged(left: boolean, meterId: string, workspace: number) {
    if (workspace !== dashboardVersion.current) return;
    if (left) {
      if (!user?.is_admin || adminMeterView === 'mine') {
        setMeters((items) => items.filter((meter) => meter.id !== meterId));
        setUnfilteredMeters((items) => items.filter((meter) => meter.id !== meterId));
      }
      reloadOnReturn.current = true;
      clearMeterWorkspace();
      navigateToMeter(null);
      return;
    }
    const refreshed = await reloadMeterList(appliedMeterSearch, adminMeterView, false, workspace);
    if (!refreshed && workspace === dashboardVersion.current) throw new Error('Meter list refresh failed');
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
    if (meterBusy || ledgerBusy || sharingBusy) return false;
    const listVersion = meterListVersion.current;
    const version = dashboardVersion.current;
    setMeterBusy(true);
    setMeterError('');
    try {
      const renamed = await renameMeter(meter.id, name);
      if (listVersion !== meterListVersion.current) return true;
      setUnfilteredMeters((current) => current.map((item) => item.id === renamed.id ? renamed : item));
      setSelectedMeter((current) => current?.id === renamed.id ? renamed : current);
      if (version === dashboardVersion.current && selectedMeter?.id === meter.id) setEditMeterName(renamed.name);
      setMeters((current) =>
        current
          .map((meter) => (meter.id === renamed.id ? renamed : meter))
          .sort((left, right) =>
            left.name.localeCompare(right.name, undefined, { sensitivity: 'base' }),
          ),
      );
      if (meterSearch.trim() || meterFilterActive) {
        try {
          const items = await listInView(appliedMeterSearch);
          if (listVersion === meterListVersion.current) setMeters(items);
        } catch {
          if (listVersion !== meterListVersion.current) return true;
          setMeterError('Name saved, but the list could not be reloaded. Search again.');
        }
      }
      return true;
    } catch (requestError) {
      if (listVersion !== meterListVersion.current) return false;
      setMeterError(
        requestError instanceof ApiError && requestError.status === 409
          ? 'Meter name is already in use.'
          : 'The meter could not be renamed. Try again.',
      );
      return false;
    } finally {
      if (version === dashboardVersion.current && listVersion === meterListVersion.current) setMeterBusy(false);
    }
  }

  async function handleDeleteMeter(meter: Meter) {
    if (meterBusy || ledgerBusy || sharingBusy || !window.confirm(`Delete ${meter.name}? This also deletes its balance and top-up records.`)) return;
    const listVersion = meterListVersion.current;
    setMeterBusy(true);
    setMeterError('');
    try {
      await deleteMeter(meter.id);
      if (listVersion !== meterListVersion.current) return;
      setUnfilteredMeters((current) => current.filter((item) => item.id !== meter.id));
      setMeters((current) =>
        current.filter((existing) => existing.id !== meter.id),
      );
      if (selectedMeter?.id === meter.id) {
        navigateToMeter(null);
        clearMeterWorkspace();
      }
    } catch {
      if (listVersion !== meterListVersion.current) return;
      setMeterError('The meter could not be deleted. Try again.');
    } finally {
      if (listVersion === meterListVersion.current) setMeterBusy(false);
    }
  }

  const workspace = dashboardVersion.current;
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
              <MeterSection
                error={error}
                meterId={meterIdFromPath(meterPath) ?? undefined}
                adminView={adminMeterView}
                busy={meterBusy || metersLoading || ledgerBusy}
                onAdminViewChange={(view) => { setAdminMeterView(view); setFullMeterList([]); void handleClearMeterSearch(view); }}
                search={(meterCount > 10 || meterFilterActive || meterSearch.trim()) && (
                  <MeterSearch busy={meterBusy || metersLoading || ledgerBusy} value={meterSearch} active={meterFilterActive}
                    onChange={setMeterSearch} onSubmit={handleSearchMeters} onClear={() => void handleClearMeterSearch()} />
                )}
                user={user}
              >
                {meterBusy && !selectedMeter && !isMeterListPath(meterPath) ? (
                  <Box sx={{ display: 'grid', minHeight: 160, placeItems: 'center' }}>
                    <CircularProgress aria-label="Loading meter" color="inherit" />
                  </Box>
                ) : selectedMeter ? (
                  <MeterDetailsPage key={selectedMeter.id}
                    busy={meterBusy || ledgerBusy || sharingBusy}
                    editName={editMeterName}
                    error={meterError}
                    onEditNameChange={setEditMeterName}
                    onRename={handleRenameMeter}
                    selectedContent={
                      selectedMeter ? (
                        <Stack key={selectedMeter.id} spacing={2.5}>
                          <ForecastPanel
                            forecast={forecast}
                            loading={ledgerLoading}
                          />
                          <LedgerPanel
                            balances={balances}
                            busy={ledgerBusy || meterBusy || sharingBusy}
                            error={ledgerError}
                            loading={ledgerLoading}
                            onCreateBalance={handleCreateBalance}
                            onCreateTopUp={handleCreateTopUp}
                            onDelete={handleDeleteEntry}
                            onUpdate={handleUpdateEntry}
                            topUps={topUps}
                          />
                          <SharingPanel key={`${user.id}:${selectedMeter.id}`} meterId={selectedMeter.id} user={user}
                            busy={ledgerBusy || meterBusy || ledgerLoading}
                            onPendingChange={setSharingBusy}
                            onChanged={(left) => handleSharingChanged(left, selectedMeter.id, workspace)}
                            onUnavailable={() => { if (workspace === dashboardVersion.current) void loadMeter(selectedMeter.id); }} />
                          <Button
                            color="secondary"
                            disabled={ledgerLoading || ledgerBusy || meterBusy || sharingBusy}
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
                  />
                ) : (
                  <MetersPage key="list"
                    adminView={adminMeterView}
                    busy={meterBusy || ledgerBusy}
                    error={meterError}
                    isAdmin={user.is_admin}
                    loading={metersLoading}
                    meters={meters}
                    name={meterName}
                    onCreate={handleCreateMeter}
                    onDelete={handleDeleteMeter}
                    onEditNameChange={setEditMeterName}
                    onNameChange={setMeterName}
                    onRename={handleRenameMeter}
                    onRetry={() => void reloadMeterList()}
                    onSelect={(meter) => navigateToMeter(meter.id)}
                    search={appliedMeterSearch}
                  />
                )}
              </MeterSection>
            ) : (
              <LoginPage
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
            <Stack component="footer" spacing={1}>
              <Typography
                align="center"
                color="text.secondary"
                sx={{ display: 'block', px: 2 }}
                variant="caption"
              >
                Manual kWh planning. No hardware or meter modification required.
              </Typography>
              <Box component="a" href="https://roventics.com" target="_blank" rel="noopener noreferrer" aria-label="Visit Roventics"
                sx={{ alignSelf: 'center', display: 'flex', alignItems: 'center', gap: 0.75, color: 'common.black', textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}>
                <Box component="img" src="/roventics-logo.png" alt="Roventics logo" width={24} height={24} sx={{ display: 'block' }} />
                <Typography component="span" variant="caption">by Roventics</Typography>
              </Box>
            </Stack>
          </Stack>
        </Box>
      </Container>
    </ThemeProvider>
  );
}
