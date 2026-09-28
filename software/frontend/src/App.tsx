import {
  Alert,
  AppBar,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Container,
  CssBaseline,
  Stack,
  ThemeProvider,
  Toolbar,
  Typography,
  createTheme,
} from '@mui/material';
import { useEffect, useState } from 'react';

import { type Identity, fetchIdentity } from './api';
import { freshAccessToken, initializeAuth, login, logout } from './auth';

const theme = createTheme({
  palette: {
    primary: { main: '#0b4f6c' },
    background: { default: '#f4f7f9' },
  },
});

type SessionState =
  | { status: 'loading' }
  | { status: 'signed-out' }
  | { status: 'authenticated'; identity: Identity }
  | { status: 'error'; message: string };

export default function App() {
  const [session, setSession] = useState<SessionState>({ status: 'loading' });

  useEffect(() => {
    let active = true;
    const loadSession = async (): Promise<void> => {
      try {
        if (!(await initializeAuth())) {
          if (active) setSession({ status: 'signed-out' });
          return;
        }
        const identity = await fetchIdentity(await freshAccessToken());
        if (active) setSession({ status: 'authenticated', identity });
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unexpected error';
        if (active) setSession({ status: 'error', message });
      }
    };
    void loadSession();
    return () => {
      active = false;
    };
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Roventics Monitor
          </Typography>
          {session.status === 'authenticated' && (
            <Button color="inherit" onClick={() => void logout()}>
              Sign out
            </Button>
          )}
        </Toolbar>
      </AppBar>
      <Container maxWidth="sm">
        <Box component="main" sx={{ py: 8 }}>
          <Card>
            <CardContent>
              <Stack spacing={2}>
                {session.status === 'loading' && (
                  <Stack direction="row" spacing={2} sx={{ alignItems: 'center' }}>
                    <CircularProgress size={24} />
                    <Typography>Checking your session...</Typography>
                  </Stack>
                )}

                {session.status === 'signed-out' && (
                  <>
                    <Chip label="Secure development access" sx={{ alignSelf: 'flex-start' }} />
                    <Typography variant="h4" component="h1">
                      Meter monitoring foundation
                    </Typography>
                    <Typography color="text.secondary">
                      Sign in through the local Monitor realm. Meter readings and
                      dashboard features arrive in later tickets.
                    </Typography>
                    <Button variant="contained" onClick={() => void login()}>
                      Sign in
                    </Button>
                  </>
                )}

                {session.status === 'authenticated' && (
                  <>
                    <Chip
                      color="success"
                      label="API identity verified"
                      sx={{ alignSelf: 'flex-start' }}
                    />
                    <Typography variant="h4" component="h1">
                      Welcome, {session.identity.username}
                    </Typography>
                    <Typography color="text.secondary">
                      {session.identity.email ?? 'No email claim was provided.'}
                    </Typography>
                    <Typography>
                      Authentication is connected. Meter data remains intentionally
                      out of scope for this baseline.
                    </Typography>
                  </>
                )}

                {session.status === 'error' && (
                  <>
                    <Alert severity="error">{session.message}</Alert>
                    <Button variant="outlined" onClick={() => window.location.reload()}>
                      Retry
                    </Button>
                  </>
                )}
              </Stack>
            </CardContent>
          </Card>
        </Box>
      </Container>
    </ThemeProvider>
  );
}
