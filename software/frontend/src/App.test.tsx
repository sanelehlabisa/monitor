import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';

import App from './App';
import { LoginPanel, SignedInPanel } from './AuthPanels';
import { ForecastPanel } from './ForecastPanel';
import { LedgerPanel } from './LedgerPanel';
import { MeterWorkspace } from './MeterWorkspace';
import type { Forecast } from './api';

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
  it('renders branded session loading without claiming data exists', () => {
    const markup = renderToStaticMarkup(<App />);

    expect(markup).toContain('roventics-logo.png');
    expect(markup).toContain('Roventics Monitor');
    expect(markup).toContain('Loading your session');
  });

  it('renders the email and code steps as one compact flow', () => {
    const emailMarkup = renderToStaticMarkup(
      <LoginPanel
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
      <LoginPanel
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
    expect(codeMarkup).toContain('Check your email');
    expect(codeMarkup).toContain('user@example.test');
    expect(codeMarkup).toContain('Resend code');
  });

  it('renders an honest signed-in meter empty state and name-only form', () => {
    const markup = renderToStaticMarkup(
      <SignedInPanel
        busy={false}
        error=""
        onLogout={noAction}
        user={{ id: 7, email: 'user@example.test', is_admin: false }}
      >
        <MeterWorkspace
          adminView="mine"
          busy={false}
          currentUserEmail="user@example.test"
          editName=""
          error=""
          isAdmin={false}
          loading={false}
          meters={[]}
          name=""
          onBack={noAction}
          onAdminViewChange={noAction}
          onClearSearch={noAction}
          onCreate={noAction}
          onDelete={noAction}
          onEditNameChange={noAction}
          onNameChange={noAction}
          onRename={noAction}
          onSearch={noAction}
          onSearchChange={noAction}
          onSelect={noAction}
          selectedMeter={null}
          search=""
        />
      </SignedInPanel>,
    );

    expect(markup).toContain('Your meters');
    expect(markup).toContain('No meters yet');
    expect(markup).toContain('Meter name');
    expect(markup).toContain('Add meter');
    expect(markup).toContain('Search meters');
    expect(markup).toContain('Clear');
    expect(markup).toContain('user@example.test');
    expect(markup).not.toContain('estimated balance');
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
      <MeterWorkspace
        adminView="mine"
        busy={false}
        currentUserEmail="user@example.test"
        editName=""
        error=""
        isAdmin={false}
        loading={false}
        meters={[meter]}
        name=""
        onBack={noAction}
        onAdminViewChange={noAction}
        onClearSearch={noAction}
        onCreate={noAction}
        onDelete={noAction}
        onEditNameChange={noAction}
        onNameChange={noAction}
        onRename={noAction}
        onSearch={noAction}
        onSearchChange={noAction}
        onSelect={noAction}
        selectedMeter={null}
        search=""
      />,
    );
    const selectedMarkup = renderToStaticMarkup(
      <MeterWorkspace
        adminView="mine"
        busy={false}
        currentUserEmail="user@example.test"
        editName="Home"
        error=""
        isAdmin={false}
        loading={false}
        meters={[meter]}
        name=""
        onBack={noAction}
        onAdminViewChange={noAction}
        onClearSearch={noAction}
        onCreate={noAction}
        onDelete={noAction}
        onEditNameChange={noAction}
        onNameChange={noAction}
        onRename={noAction}
        onSearch={noAction}
        onSearchChange={noAction}
        onSelect={noAction}
        selectedContent={
          <ForecastPanel forecast={notEnoughForecast} loading={false} />
        }
        selectedMeter={meter}
        search=""
      />,
    );

    expect(listMarkup).toContain('Home');
    expect(selectedMarkup).toContain('Back to meters');
    expect(selectedMarkup).toContain('Owner: user@example.test');
    expect(selectedMarkup).toContain('Not enough data');
    expect(selectedMarkup).toContain('at least two actual balances');
    expect(selectedMarkup).toContain('Save name');
    expect(selectedMarkup).toContain('Delete meter');
  });

  it('separates admin-owned meters from the owner-labelled system view', () => {
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
    const renderAdminView = (adminView: 'mine' | 'all') => renderToStaticMarkup(
      <SignedInPanel
        busy={false}
        error=""
        onLogout={noAction}
        user={{ id: 9, email: 'admin@example.test', is_admin: true }}
      >
        <MeterWorkspace
          adminView={adminView}
          busy={false}
          currentUserEmail="admin@example.test"
          editName=""
          error=""
          isAdmin
          loading={false}
          meters={[ownMeter, otherMeter]}
          name=""
          onBack={noAction}
          onAdminViewChange={noAction}
          onClearSearch={noAction}
          onCreate={noAction}
          onDelete={noAction}
          onEditNameChange={noAction}
          onNameChange={noAction}
          onRename={noAction}
          onSearch={noAction}
          onSearchChange={noAction}
          onSelect={noAction}
          selectedMeter={null}
          search=""
        />
      </SignedInPanel>,
    );
    const mineMarkup = renderAdminView('mine');
    const allMarkup = renderAdminView('all');

    expect(mineMarkup).toContain('Meter profiles');
    expect(mineMarkup).toContain('My meters');
    expect(mineMarkup).toContain('All meters');
    expect(mineMarkup).toContain('Admin home');
    expect(mineMarkup).not.toContain('Shop');
    expect(allMarkup).toContain('Admin home');
    expect(allMarkup).toContain('Shop');
    expect(allMarkup).toContain('admin@example.test');
    expect(allMarkup).toContain('owner@example.test');
  });

  it('renders tabbed manual-entry actions and the selected record history', () => {
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
    expect(markup).toContain('Balance records');
    expect(markup).toContain('Top-up records');
    expect(markup).toContain('Balance history');
    expect(markup).toContain('Actual balance');
    expect(markup).not.toContain('Purchased top-up');
    expect(markup).not.toContain('20.500 kWh');
    expect(markup).toContain('Edit');
    expect(markup).toContain('Delete');
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
