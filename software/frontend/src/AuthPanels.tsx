import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Stack,
  Tab,
  Tabs,
  TextField,
  Typography,
} from '@mui/material';
import AlternateEmailIcon from '@mui/icons-material/AlternateEmail';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import BorderColorOutlinedIcon from '@mui/icons-material/BorderColorOutlined';
import CachedIcon from '@mui/icons-material/Cached';
import type { FormEvent, ReactNode } from 'react';

import type { User } from './api';
import type { AdminMeterView } from './MeterWorkspace';

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
      </CardContent>
    </Card>
  );
}

type SignedInPanelProps = {
  user: User;
  error: string;
  children?: ReactNode;
  meterId?: string;
  adminView?: AdminMeterView;
  busy?: boolean;
  onAdminViewChange?: (view: AdminMeterView) => void;
};

export function SignedInPanel({
  user,
  error,
  children,
  meterId,
  adminView = 'mine',
  busy = false,
  onAdminViewChange,
}: SignedInPanelProps) {
  return (
    <Card>
      <Stack component="header" direction="row" sx={{ alignItems: 'center', bgcolor: 'common.black', color: 'common.white', borderRadius: '12px 12px 0 0', px: 2, pt: 1 }}>
        <Typography variant="h4" component="h1" sx={{ flex: 1, minWidth: 0, overflowWrap: 'anywhere', pb: 1 }}>
          {meterId ? `Meter ${meterId}` : 'Meters'}
        </Typography>
        {!meterId && user.is_admin && (
          <Tabs value={adminView} onChange={(_, value: AdminMeterView) => onAdminViewChange?.(value)} aria-label="Meter scope" textColor="inherit"
            sx={{ minHeight: 36, '& .MuiTabs-indicator': { display: 'none' }, '& .MuiTab-root': { minWidth: 48, minHeight: 36, p: 1, textTransform: 'none', opacity: 1, borderRadius: '6px 6px 0 0', '&.Mui-selected': { bgcolor: 'common.white', color: 'common.black' } } }}>
            <Tab id="meter-tab-mine" aria-controls="meter-workspace-content" aria-label="My meters" label="My" value="mine" disabled={busy} />
            <Tab id="meter-tab-all" aria-controls="meter-workspace-content" aria-label="All meters" label="All" value="all" disabled={busy} />
          </Tabs>
        )}
      </Stack>
      <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
        <Stack id="meter-workspace-content" spacing={2} role={!meterId && user.is_admin ? 'tabpanel' : undefined}
          aria-labelledby={!meterId && user.is_admin ? `meter-tab-${adminView}` : undefined}>
          {error && <Alert severity="error">{error}</Alert>}
          {children}
        </Stack>
      </CardContent>
    </Card>
  );
}
