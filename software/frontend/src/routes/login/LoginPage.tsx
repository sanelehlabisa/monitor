import { Alert, Box, Button, Chip, Stack, TextField, Typography } from '@mui/material';
import AlternateEmailIcon from '@mui/icons-material/AlternateEmail';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import BorderColorOutlinedIcon from '@mui/icons-material/BorderColorOutlined';
import CachedIcon from '@mui/icons-material/Cached';
import type { FormEvent } from 'react';

export type LoginStep = 'email' | 'code';

type LoginPageProps = {
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

export function LoginPage({
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
}: LoginPageProps) {
  const requestingCode = step === 'email';

  return (
    <Box component="section">
      <Box sx={{ py: 1 }}>
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
              startIcon={requestingCode ? <AlternateEmailIcon /> : <ArrowForwardIcon />}
              type="submit"
              variant="contained"
            >
              {busy ? 'Please wait…' : requestingCode ? 'Send sign-in code' : 'Sign in'}
            </Button>
            {!requestingCode && (
              <Stack direction="row" sx={{ justifyContent: 'space-between' }}>
                <Button
                  disabled={busy}
                  onClick={onChangeEmail}
                  size="small"
                  startIcon={<BorderColorOutlinedIcon />}
                >
                  Change email
                </Button>
                <Button
                  disabled={busy}
                  onClick={onResend}
                  size="small"
                  startIcon={<CachedIcon />}
                >
                  Resend code
                </Button>
              </Stack>
            )}
          </Stack>
        </Box>
      </Box>
    </Box>
  );
}
