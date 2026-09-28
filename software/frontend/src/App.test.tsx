import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';

import App from './App';

describe('Monitor application shell', () => {
  it('shows the planned email authentication direction without a working login', () => {
    const markup = renderToStaticMarkup(<App />);

    expect(markup).toContain('Passwordless access planned');
    expect(markup).toContain('Authentication is not active in this build.');
    expect(markup).toContain('disabled');
  });
});
