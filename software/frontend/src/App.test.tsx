import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';

import App from './App';
import { LoginPanel, SignedInPanel } from './AuthPanels';
import { LedgerPanel } from './LedgerPanel';
import { MeterWorkspace } from './MeterWorkspace';

const noAction = () => undefined;
const yes = async () => true;

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
          busy={false}
          editName=""
          error=""
          isAdmin={false}
          loading={false}
          meters={[]}
          name=""
          onBack={noAction}
          onCreate={noAction}
          onDelete={noAction}
          onEditNameChange={noAction}
          onNameChange={noAction}
          onRename={noAction}
          onSelect={noAction}
          selectedMeter={null}
        />
      </SignedInPanel>,
    );

    expect(markup).toContain('Your meters');
    expect(markup).toContain('No meters yet');
    expect(markup).toContain('Meter name');
    expect(markup).toContain('Add meter');
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
        busy={false}
        editName=""
        error=""
        isAdmin={false}
        loading={false}
        meters={[meter]}
        name=""
        onBack={noAction}
        onCreate={noAction}
        onDelete={noAction}
        onEditNameChange={noAction}
        onNameChange={noAction}
        onRename={noAction}
        onSelect={noAction}
        selectedMeter={null}
      />,
    );
    const selectedMarkup = renderToStaticMarkup(
      <MeterWorkspace
        busy={false}
        editName="Home"
        error=""
        isAdmin={false}
        loading={false}
        meters={[meter]}
        name=""
        onBack={noAction}
        onCreate={noAction}
        onDelete={noAction}
        onEditNameChange={noAction}
        onNameChange={noAction}
        onRename={noAction}
        onSelect={noAction}
        selectedMeter={meter}
      />,
    );

    expect(listMarkup).toContain('Home');
    expect(selectedMarkup).toContain('Back to meters');
    expect(selectedMarkup).toContain('Not enough data');
    expect(selectedMarkup).toContain('at least two valid actual balances');
    expect(selectedMarkup).toContain('Save name');
    expect(selectedMarkup).toContain('Delete meter');
  });

  it('labels the admin view and identifies meter owners', () => {
    const meter = {
      id: '00000000-0000-0000-0000-000000000002',
      name: 'Shop',
      owner_email: 'owner@example.test',
      created_at: '2026-10-09T10:00:00Z',
      updated_at: '2026-10-09T10:00:00Z',
    };
    const markup = renderToStaticMarkup(
      <SignedInPanel
        busy={false}
        error=""
        onLogout={noAction}
        user={{ id: 9, email: 'admin@example.test', is_admin: true }}
      >
        <MeterWorkspace
          busy={false}
          editName=""
          error=""
          isAdmin
          loading={false}
          meters={[meter]}
          name=""
          onBack={noAction}
          onCreate={noAction}
          onDelete={noAction}
          onEditNameChange={noAction}
          onNameChange={noAction}
          onRename={noAction}
          onSelect={noAction}
          selectedMeter={null}
        />
      </SignedInPanel>,
    );

    expect(markup).toContain('All meters');
    expect(markup).toContain('Admin');
    expect(markup).toContain('owner@example.test');
  });

  it('renders factual manual-entry actions and combined history', () => {
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

    expect(markup).toContain('Latest actual balance');
    expect(markup).toContain('42.125 kWh');
    expect(markup).toContain('Record balance');
    expect(markup).toContain('Record top-up');
    expect(markup).toContain('Actual balance');
    expect(markup).toContain('Purchased top-up');
    expect(markup).toContain('20.500 kWh');
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

    expect(markup).toContain('No actual balance recorded yet');
    expect(markup).toContain('No balance or top-up entries yet');
    expect(markup).not.toContain('remaining days');
  });
});
