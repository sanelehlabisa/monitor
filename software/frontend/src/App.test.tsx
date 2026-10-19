import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';

import App from './App';
import { LoginPage } from './routes/login/LoginPage';
import { MeterSearch } from './routes/meters/components/MeterSearch';
import { MeterSection } from './routes/meters/components/MeterSection';
import { ForecastPanel } from './routes/meters/components/ForecastPanel';
import { LedgerPanel } from './routes/meters/components/LedgerPanel';
import { SharingPanel } from './routes/meters/components/SharingPanel';
import { MetersPage } from './routes/meters/MetersPage';
import { MeterDetailsPage } from './routes/meters/MeterDetailsPage';
import { Navigation } from './components/Navigation';
import type { Forecast } from './lib/api';

const noAction = () => undefined;
const yes = async () => true;
const notEnoughForecast: Forecast = {
  status: 'not_enough_data',
  as_of: '2026-10-09T12:00:00Z',
  latest_actual_balance_kwh: null,
  latest_actual_at: null,
  daily_usage_kwh: null,
  estimated_balance_kwh: null,
  remaining_days: null,
  run_out_at: null,
  recommended_top_up_30_days_kwh: null,
  intervals_used: 0,
};
describe('Monitor authentication UI', () => {
  it('combines stacked branding, Back, email and direct red sign out in one row', () => {
    const markup = renderToStaticMarkup(
      <Navigation busy={false} onBack={noAction} onLogout={noAction}
        user={{ id: 7, email: 'admin@example.test', is_admin: true }} />,
    );
    expect(markup).toContain('<nav');
    expect(markup).toContain('>Sign out</button>');
    expect(markup).toContain('MuiButton-colorError');
    expect(markup).toContain('LogoutIcon');
    expect(markup).toContain('admin@example.test');
    expect(markup).not.toContain('AccountCircleIcon');
    expect(markup).not.toContain('Account menu');
    expect(markup).not.toContain('aria-haspopup');
    expect(markup).toContain('>Back</button>');
    expect(markup).toContain('ArrowBackIcon');
    expect(markup).toContain('minmax(0, 1fr) auto minmax(0, 1fr)');
    expect(markup).toContain('src="/monitor-logo.png"');
    expect(markup).toContain('>Monitor</span>');
    expect(markup.indexOf('>Back</button>')).toBeLessThan(markup.indexOf('src="/monitor-logo.png"'));
    expect(markup.indexOf('src="/monitor-logo.png"')).toBeLessThan(markup.indexOf('>Monitor</span>'));
    expect(markup.indexOf('>Monitor</span>')).toBeLessThan(markup.indexOf('title="admin@example.test"'));
    expect(markup.indexOf('title="admin@example.test"')).toBeLessThan(markup.indexOf('>Sign out</button>'));
    expect(markup).not.toContain('Admin');
    expect(markup).not.toContain('roventics-logo.png');
    expect(markup).not.toContain('Roventics Monitor');
    const signedOut = renderToStaticMarkup(
      <Navigation busy={false} onBack={noAction} onLogout={noAction} user={null} />,
    );
    expect(signedOut).not.toContain('Account menu');
    expect(signedOut).not.toContain('Sign out');
    expect(signedOut).not.toContain('LogoutIcon');
    expect(signedOut).not.toContain('>Back</button>');
    expect(signedOut).not.toContain('<nav');
    expect(signedOut).toContain('<header');
    expect(signedOut).toContain('src="/monitor-logo.png"');
    expect(signedOut).toContain('>Monitor</span>');
  });

  it('keeps list branding without Back and disables navigation during pending work', () => {
    const user = { id: 7, email: 'owner@example.test', is_admin: false };
    const list = renderToStaticMarkup(<Navigation busy={false} onLogout={noAction} user={user} />);
    expect(list).not.toContain('>Back</button>');
    expect(list).toContain('src="/monitor-logo.png"');
    expect(list).toContain('>Sign out</button>');
    const busy = renderToStaticMarkup(<Navigation busy onBack={noAction} onLogout={noAction} user={user} />);
    expect(busy.match(/<button\b[^>]*disabled=""/g)).toHaveLength(2);
  });

  it('renders Monitor identity and the separate Roventics credit without claiming data exists', () => {
    const markup = renderToStaticMarkup(<App />);

    expect(markup).toContain('src="/monitor-logo.png"');
    expect(markup).toContain('alt="Monitor logo"');
    expect(markup).toContain('width="48"');
    expect(markup).toContain('src="/roventics-logo.png"');
    expect(markup).toContain('href="https://roventics.com"');
    expect(markup).toContain('rel="noopener noreferrer"');
    expect(markup).toContain('by Roventics');
    expect(markup).toContain('#005aae');
    expect(markup).toContain('#ffffff');
    expect(markup).toContain('Segoe UI');
    expect(markup).toContain('system-ui');
    expect(markup).not.toContain('Roventics Monitor');
    expect(markup).toContain('Loading your session');
  });

  it('renders the email and code steps as one compact flow', () => {
    const emailMarkup = renderToStaticMarkup(
      <LoginPage
        busy={false}
        code=""
        email=""
        error=""
        notice=""
        onChangeEmail={noAction}
        onCodeChange={noAction}
        onEmailChange={noAction}
        onResend={noAction}
        onSubmit={noAction}
        step="email"
      />,
    );
    const codeMarkup = renderToStaticMarkup(
      <LoginPage
        busy={false}
        code="123456"
        email="user@example.test"
        error=""
        notice="Code sent"
        onChangeEmail={noAction}
        onCodeChange={noAction}
        onEmailChange={noAction}
        onResend={noAction}
        onSubmit={noAction}
        step="code"
      />,
    );

    expect(emailMarkup).toContain('Welcome to Monitor');
    expect(emailMarkup).toContain('Send sign-in code');
    expect(emailMarkup).not.toContain('MuiCard-root');
    expect(codeMarkup).not.toContain('MuiCard-root');
    expect(codeMarkup).toContain('Check your email');
    expect(codeMarkup).toContain('user@example.test');
    expect(codeMarkup).toContain('Resend code');
  });

  it('renders an honest signed-in meter empty state and name-only form', () => {
    const markup = renderToStaticMarkup(
      <MeterSection
        error=""
        user={{ id: 7, email: 'user@example.test', is_admin: false }}
      >
        <MetersPage
          adminView="mine"
          busy={false}
          error=""
          isAdmin={false}
          loading={false}
          meters={[]}
          name=""
          onCreate={noAction}
          onDelete={noAction}
          onEditNameChange={noAction}
          onNameChange={noAction}
          onRename={yes}
          onSelect={noAction}
          search=""
        />
      </MeterSection>,
    );

    expect(markup).toContain('Meters');
    expect(markup).toContain('No meters yet');
    expect(markup).not.toContain('MuiCard-root');
    expect(markup).toContain('Meter name');
    expect(markup).toContain('Add meter');
    expect(markup).not.toContain('Search meters');
    expect(markup).not.toContain('Clear search');
    expect(markup).not.toContain('Sign out');
    expect(markup).not.toContain('estimated balance');
  });

  it('keeps header search clearable with an active filter and an empty draft', () => {
    const search = <MeterSearch busy={false} value="" active onChange={noAction} onSubmit={noAction} onClear={noAction} />;
    const markup = renderToStaticMarkup(<MeterSection error="" search={search} user={{ id: 7, email: 'admin@example.test', is_admin: true }} />);
    expect(markup).toContain('Search meters');
    expect(markup).toContain('Name or member email');
    expect(markup).toContain('aria-label="Search meters"');
    expect(markup).toContain('SearchIcon');
    expect(markup).toContain('aria-label="Clear search"');
    expect(markup).toContain('ClearIcon');
    expect(markup).not.toMatch(/<button\b[^>]*disabled=""/);
    const detail = renderToStaticMarkup(<MeterSection error="" meterId="meter-id" search={search} user={{ id: 7, email: 'user@example.test', is_admin: false }} />);
    expect(detail).not.toContain('Search meters');
    const pending = renderToStaticMarkup(<MeterSearch busy value="Home" active onChange={noAction} onSubmit={noAction} onClear={noAction} />);
    expect(pending.match(/<button\b[^>]*disabled=""/g)).toHaveLength(2);
  });

  it('renders a selectable list and honest selected-meter state', () => {
    const meter = {
      id: '00000000-0000-0000-0000-000000000001',
      name: 'Home',
      owner_email: 'user@example.test',
      created_at: '2026-10-09T10:00:00Z',
      updated_at: '2026-10-09T10:00:00Z',
    };
    const listMarkup = renderToStaticMarkup(
      <MetersPage
        adminView="mine"
        busy={false}
        error=""
        isAdmin={false}
        loading={false}
        meters={[meter]}
        name=""
        onCreate={noAction}
        onDelete={noAction}
        onEditNameChange={noAction}
        onNameChange={noAction}
        onRename={yes}
        onSelect={noAction}
        search=""
      />,
    );
    const selectedMarkup = renderToStaticMarkup(
      <MeterDetailsPage
        busy={false}
        editName="Home"
        error=""
        onEditNameChange={noAction}
        onRename={yes}
        selectedContent={
          <ForecastPanel forecast={notEnoughForecast} loading={false} />
        }
        selectedMeter={meter}
      />,
    );

    expect(listMarkup).toContain('Home');
    expect(listMarkup).toContain('<ol');
    expect(listMarkup).toContain('<li');
    expect(listMarkup).toContain('>1.</span>');
    expect(listMarkup).toContain('aria-label="Rename Home"');
    expect(listMarkup).toContain('aria-label="Delete Home"');
    expect(listMarkup).toContain('EditOutlinedIcon');
    expect(listMarkup).toContain('DeleteOutlinedIcon');
    expect(selectedMarkup).not.toContain('Back to meters');
    expect(selectedMarkup).toContain('Meter details');
    expect(selectedMarkup).toContain('Name:');
    expect(selectedMarkup).toContain('Created by:');
    expect(selectedMarkup).toContain('user@example.test');
    expect(selectedMarkup).toContain('value="Home"');
    expect(selectedMarkup).toContain('Not enough data');
    expect(selectedMarkup).toContain('at least two actual balances');
    expect(selectedMarkup).toContain('aria-label="Rename Home"');
    expect(selectedMarkup).toContain('readOnly=""');
    expect(selectedMarkup).not.toContain('SaveOutlinedIcon');
    expect(selectedMarkup).not.toContain('Delete meter');
    expect(selectedMarkup).not.toContain('Meter settings');
  });

  it('renders server-scoped My memberships without filtering by creator email', () => {
    const otherMeter = {
      id: '00000000-0000-0000-0000-000000000002',
      name: 'Shop',
      owner_email: 'owner@example.test',
      created_at: '2026-10-09T10:00:00Z',
      updated_at: '2026-10-09T10:00:00Z',
    };
    const ownMeter = {
      ...otherMeter,
      id: '00000000-0000-0000-0000-000000000003',
      name: 'Admin home',
      owner_email: 'admin@example.test',
    };
    const sharedMeter = {
      ...otherMeter,
      id: '00000000-0000-0000-0000-000000000004',
      name: 'Shared home',
    };
    const renderAdminView = (adminView: 'mine' | 'all') => renderToStaticMarkup(
      <MeterSection
        adminView={adminView}
        onAdminViewChange={noAction}
        error=""
        user={{ id: 9, email: 'admin@example.test', is_admin: true }}
      >
        <MetersPage
          adminView={adminView}
          busy={false}
          error=""
          isAdmin
          loading={false}
          meters={adminView === 'mine' ? [ownMeter, sharedMeter] : [ownMeter, sharedMeter, otherMeter]}
          name=""
          onCreate={noAction}
          onDelete={noAction}
          onEditNameChange={noAction}
          onNameChange={noAction}
          onRename={yes}
          onSelect={noAction}
          search=""
        />
      </MeterSection>,
    );
    const mineMarkup = renderAdminView('mine');
    const allMarkup = renderAdminView('all');

    expect(mineMarkup).toContain('Meters');
    expect(mineMarkup).not.toContain('Meter profiles');
    expect(mineMarkup).toContain('My meters');
    expect(mineMarkup).toContain('All meters');
    expect(mineMarkup).toContain('Admin home');
    expect(mineMarkup).toContain('Shared home');
    expect(mineMarkup).not.toContain('Shop');
    expect(allMarkup).toContain('Admin home');
    expect(allMarkup).toContain('Shop');
    expect(allMarkup).toContain('admin@example.test');
    expect(allMarkup).toContain('owner@example.test');
    expect(allMarkup).toContain('Created by');
    expect(mineMarkup).not.toContain('aria-label="Delete Shop"');
    expect(allMarkup).toContain('aria-label="Rename Shop"');
    expect(allMarkup).toContain('aria-label="Delete Shop"');
    expect(mineMarkup).toContain('role="tab"');
    expect(mineMarkup).toContain('aria-selected="true"');
    expect(mineMarkup).not.toContain('aria-label="Search meters"');
    expect(mineMarkup).toContain('aria-label="Add meter"');
  });

  it('renders two primary record actions with forms and history initially closed', () => {
    const balance = {
      id: '00000000-0000-0000-0000-000000000010',
      meter_id: '00000000-0000-0000-0000-000000000001',
      balance_kwh: '42.125',
      occurred_at: '2026-10-09T10:00:00Z',
      created_at: '2026-10-09T10:01:00Z',
      updated_at: '2026-10-09T10:01:00Z',
    };
    const topUp = {
      id: '00000000-0000-0000-0000-000000000020',
      meter_id: balance.meter_id,
      top_up_kwh: '20.500',
      occurred_at: '2026-10-09T11:00:00Z',
      created_at: '2026-10-09T11:01:00Z',
      updated_at: '2026-10-09T11:01:00Z',
    };
    const markup = renderToStaticMarkup(
      <LedgerPanel
        balances={[balance]}
        busy={false}
        error=""
        loading={false}
        onCreateBalance={yes}
        onCreateTopUp={yes}
        onDelete={yes}
        onUpdate={yes}
        topUps={[topUp]}
      />,
    );

    expect(markup).toContain('42.125 kWh');
    expect(markup).toContain('Record balance');
    expect(markup).toContain('Record top-up');
    expect(markup).not.toContain('Remaining balance (kWh)');
    expect(markup).toContain('<details');
    expect(markup).not.toMatch(/<details[^>]*\sopen(?:[\s=>])/);
    expect(markup).toContain('Balance records');
    expect(markup).toContain('Top-up records');
    expect(markup).toContain('Balance history');
    expect(markup).toContain('Actual balance');
    expect(markup).not.toContain('Purchased top-up');
    expect(markup).not.toContain('20.500 kWh');
    expect(markup).toContain('Edit');
    expect(markup).toContain('Delete');
  });

  it('keeps sharing collapsed without invented member rows or invitation controls', () => {
    const markup = renderToStaticMarkup(
      <SharingPanel meterId="00000000-0000-0000-0000-000000000001"
        user={{ id: 7, email: 'member@example.test', is_admin: false }}
        busy={false} onChanged={async () => undefined} onUnavailable={noAction} onPendingChange={noAction} />,
    );
    expect(markup).toContain('Sharing');
    expect(markup).toContain('<details');
    expect(markup).not.toMatch(/<details[^>]*\sopen(?:[\s=>])/);
    expect(markup).not.toContain('Member email');
    expect(markup).not.toContain('Leave meter');
    expect(markup).not.toContain('Invite');
  });

  it('renders an honest empty ledger without estimates', () => {
    const markup = renderToStaticMarkup(
      <LedgerPanel
        balances={[]}
        busy={false}
        error=""
        loading={false}
        onCreateBalance={yes}
        onCreateTopUp={yes}
        onDelete={yes}
        onUpdate={yes}
        topUps={[]}
      />,
    );

    expect(markup).toContain('No balance records yet');
    expect(markup).not.toContain('remaining days');
  });

  it('renders available forecast estimates and their factual basis', () => {
    const forecast: Forecast = {
      status: 'available',
      as_of: '2026-10-09T12:00:00Z',
      latest_actual_balance_kwh: '42.125',
      latest_actual_at: '2026-10-09T10:00:00Z',
      daily_usage_kwh: '5.000000',
      estimated_balance_kwh: '41.708',
      remaining_days: '8.34',
      run_out_at: '2026-10-17T20:09:36Z',
      recommended_top_up_30_days_kwh: '108.292',
      intervals_used: 2,
    };

    const markup = renderToStaticMarkup(
      <ForecastPanel forecast={forecast} loading={false} />,
    );

    expect(markup).toContain('Latest actual balance');
    expect(markup).toContain('42.125 kWh');
    expect(markup).toContain('Planning estimate');
    expect(markup).toContain('41.708 kWh');
    expect(markup).toContain('5.000000 kWh/day');
    expect(markup).toContain('8.34 days');
    expect(markup).toContain('Top up by');
    expect(markup).toContain('108.292 kWh');
    expect(markup).toContain('Monthly purchase recommendation');
    expect(markup).toContain('font-variant-numeric:tabular-nums');
    expect(markup).toContain('aria-label="Planning estimate"');
    expect(markup).toContain('repeat(2, minmax(0, 1fr))');
    expect(markup).toContain('repeat(3, minmax(0, 1fr))');
    expect(markup).toContain('border-top:1px solid');
    expect(markup).not.toContain('linear-gradient(');
    expect(markup).not.toContain('rgba(255, 255, 255, 0.75)');
    expect(markup).toContain('Additional kWh for the next 30 days');
    expect(markup).toContain('Calculation details');
    expect(markup).toContain('Calculated');
    expect(markup).not.toMatch(/<details[^>]*\sopen(?:[\s=>])/);
    expect(markup).toContain('No safety buffer applied');
  });

  it('withholds numbers for inconsistent forecast history', () => {
    const markup = renderToStaticMarkup(
      <ForecastPanel
        forecast={{ ...notEnoughForecast, status: 'inconsistent_history' }}
        loading={false}
      />,
    );

    expect(markup).toContain('Inconsistent history');
    expect(markup).toContain('withheld estimates');
    expect(markup).not.toContain('Planning estimate');
  });

  it('shows a retry state rather than loading forever without a forecast', () => {
    const markup = renderToStaticMarkup(
      <ForecastPanel forecast={null} loading={false} />,
    );

    expect(markup).toContain('Estimates unavailable');
    expect(markup).toContain('Refresh to try again');
    expect(markup).not.toContain('Loading forecast');
    expect(markup).not.toContain('Planning estimate');
    expect(markup).not.toContain('Not enough data');
  });

  it('shows loading only while a forecast request is pending', () => {
    const markup = renderToStaticMarkup(
      <ForecastPanel forecast={notEnoughForecast} loading={true} />,
    );

    expect(markup).toContain('Loading forecast');
    expect(markup).not.toContain('Refresh to try again');
    expect(markup).not.toContain('Not enough data');
  });

  it('explains a valid zero-use forecast without a fake run-out', () => {
    const markup = renderToStaticMarkup(
      <ForecastPanel
        forecast={{
          ...notEnoughForecast,
          status: 'available',
          latest_actual_balance_kwh: '10.000',
          latest_actual_at: '2026-10-09T10:00:00Z',
          daily_usage_kwh: '0.000000',
          estimated_balance_kwh: '10.000',
          recommended_top_up_30_days_kwh: '0.000',
          intervals_used: 1,
        }}
        loading={false}
      />,
    );

    expect(markup).toContain('No finite run-out');
    expect(markup).toContain('No run-out at observed use');
    expect(markup).toContain('0.000 kWh');
  });

});
