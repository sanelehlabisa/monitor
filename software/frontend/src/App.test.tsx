import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';

import App from './App';

describe('Monitor application shell', () => {
  it('shows the manual kWh direction without claiming active features', () => {
    const markup = renderToStaticMarkup(<App />);

    expect(markup).toContain('Software-only V1');
    expect(markup).toContain('record balances and top-ups in kWh');
    expect(markup).toContain('Hardware and OCR are not required for V1.');
    expect(markup).toContain('not active in this build');
    expect(markup).toContain('disabled');
  });
});
