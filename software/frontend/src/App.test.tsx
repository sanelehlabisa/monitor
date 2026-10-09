import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';

import App from './App';
import { LoginPanel, SignedInPanel } from './AuthPanels';

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

  it('renders an honest signed-in meter empty state', () => {
    const markup = renderToStaticMarkup(
      <SignedInPanel
        busy={false}
        error=""
        onLogout={noAction}
        user={{ id: 7, email: 'user@example.test' }}
      />,
    );

    expect(markup).toContain('Your meters');
    expect(markup).toContain('No meters yet');
    expect(markup).toContain('Meter setup is next');
    expect(markup).toContain('user@example.test');
    expect(markup).not.toContain('estimated balance');
  });
});
