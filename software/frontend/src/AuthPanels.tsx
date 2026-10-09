import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Divider,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import type { FormEvent, ReactNode } from 'react';

import type { User } from './api';

export type LoginStep = 'email' | 'code';

type LoginPanelProps = {
  step: LoginStep;
  email: string;
  code: string;
  busy: boolean;
  notice: string;
  error: string;
  onEmailChange: (value: string) => void;
  onCodeChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onResend: () => void;
  onChangeEmail: () => void;
};

export function LoginPanel({
  step,
  email,
  code,
  busy,
  notice,
  error,
  onEmailChange,
  onCodeChange,
  onSubmit,
  onResend,
  onChangeEmail,
}: LoginPanelProps) {
  const requestingCode = step === 'email';

  return (
    <Card>
      <CardContent sx={{ p: { xs: 3, sm: 4 } }}>
        <Box component="form" onSubmit={onSubmit}>
          <Stack spacing={2.5}>
            <Chip
              label="Software-only electricity planning"
              size="small"
              sx={{ alignSelf: 'flex-start' }}
            />
            <Box>
              <Typography variant="h4" component="h1" gutterBottom>
                {requestingCode ? 'Welcome to Monitor' : 'Check your email'}
              </Typography>
              <Typography color="text.secondary">
                {requestingCode
                  ? 'Sign in to track prepaid electricity in kWh.'
                  : `Enter the six-digit code sent to ${email}.`}
              </Typography>
            </Box>
            {notice && <Alert severity="success">{notice}</Alert>}
            {error && <Alert severity="error">{error}</Alert>}
            {requestingCode ? (
              <TextField
                autoComplete="email"
                autoFocus
                disabled={busy}
                fullWidth
                label="Email address"
                onChange={(event) => onEmailChange(event.target.value)}
                required
                type="email"
                value={email}
              />
            ) : (
              <TextField
                autoComplete="one-time-code"
                autoFocus
                disabled={busy}
                fullWidth
                label="Six-digit code"
                onChange={(event) =>
                  onCodeChange(event.target.value.replace(/\D/g, '').slice(0, 6))
                }
                required
                slotProps={{ htmlInput: { inputMode: 'numeric', maxLength: 6 } }}
                value={code}
              />
            )}
            <Button
              disabled={busy || (requestingCode ? !email.trim() : code.length !== 6)}
              fullWidth
              size="large"
              type="submit"
              variant="contained"
            >
              {busy ? 'Please wait…' : requestingCode ? 'Send sign-in code' : 'Sign in'}
            </Button>
            {!requestingCode && (
              <Stack direction="row" sx={{ justifyContent: 'space-between' }}>
                <Button disabled={busy} onClick={onChangeEmail} size="small">
                  Change email
                </Button>
                <Button disabled={busy} onClick={onResend} size="small">
                  Resend code
                </Button>
              </Stack>
            )}
          </Stack>
        </Box>
      </CardContent>
    </Card>
  );
}

type SignedInPanelProps = {
  user: User;
  busy: boolean;
  error: string;
  onLogout: () => void;
  children?: ReactNode;
};

export function SignedInPanel({
  user,
  busy,
  error,
  onLogout,
  children,
}: SignedInPanelProps) {
  return (
    <Card>
      <CardContent sx={{ p: { xs: 3, sm: 4 } }}>
        <Stack spacing={2.5}>
          <Stack
            direction="row"
            sx={{ alignItems: 'center', justifyContent: 'space-between' }}
          >
            <Box sx={{ minWidth: 0 }}>
              <Typography variant="h4" component="h1">
                {user.is_admin ? 'All meters' : 'Your meters'}
              </Typography>
              <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
                <Typography color="text.secondary" noWrap variant="body2">
                  {user.email}
                </Typography>
                {user.is_admin && <Chip label="Admin" size="small" />}
              </Stack>
            </Box>
            <Button disabled={busy} onClick={onLogout} variant="outlined">
              Sign out
            </Button>
          </Stack>
          {error && <Alert severity="error">{error}</Alert>}
          <Divider />
          {children}
        </Stack>
      </CardContent>
    </Card>
  );
}
