import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';

import App from './App';
import { LoginPanel, SignedInPanel } from './AuthPanels';
import { MeterWorkspace } from './MeterWorkspace';

const noAction = () => undefined;

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
    expect(selectedMarkup).toContain('balance and purchased-kWh history');
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
});
