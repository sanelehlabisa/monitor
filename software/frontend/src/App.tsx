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
import {
  ApiError,
  getCurrentUser,
  logout,
  requestOtp,
  verifyOtp,
  type User,
} from './api';

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
      setStep('email');
      setEmail('');
    } catch {
      setError('Sign out failed. Please try again.');
    } finally {
      setBusy(false);
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
              />
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
