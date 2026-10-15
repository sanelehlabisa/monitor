import {
  Alert,
  Box,
  Button,
  Chip,
  IconButton,
  InputAdornment,
  Stack,
  Tab,
  Tabs,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import AlternateEmailIcon from '@mui/icons-material/AlternateEmail';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import BorderColorOutlinedIcon from '@mui/icons-material/BorderColorOutlined';
import CachedIcon from '@mui/icons-material/Cached';
import SearchIcon from '@mui/icons-material/Search';
import ClearIcon from '@mui/icons-material/Clear';
import type { FormEvent, ReactNode } from 'react';

import type { User } from './api';
import type { AdminMeterView } from './MeterWorkspace';

export type LoginStep = 'email' | 'code';

export function MeterSearch({ busy, value, active, isAdmin, onChange, onSubmit, onClear }: {
  busy: boolean; value: string; active: boolean; isAdmin: boolean;
  onChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onClear: () => void;
}) {
  return (
    <Box component="form" onSubmit={onSubmit}>
      <TextField disabled={busy} fullWidth label="Search meters" value={value}
        onChange={(event) => onChange(event.target.value)} placeholder={isAdmin ? 'Name or owner email' : 'Meter name'}
        slotProps={{ htmlInput: { maxLength: 254 }, input: { endAdornment: (
          <InputAdornment position="end">
            <Tooltip title="Search"><span><IconButton aria-label="Search meters" disabled={busy} type="submit"><SearchIcon /></IconButton></span></Tooltip>
            <Tooltip title="Clear search"><span><IconButton aria-label="Clear search" disabled={busy || (!value.trim() && !active)} onClick={onClear} type="button"><ClearIcon /></IconButton></span></Tooltip>
          </InputAdornment>
        ) } }} />
    </Box>
  );
}

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

type SignedInPanelProps = {
  user: User;
  error: string;
  children?: ReactNode;
  meterId?: string;
  adminView?: AdminMeterView;
  busy?: boolean;
  search?: ReactNode;
  onAdminViewChange?: (view: AdminMeterView) => void;
};

export function SignedInPanel({
  user,
  error,
  children,
  meterId,
  adminView = 'mine',
  busy = false,
  search,
  onAdminViewChange,
}: SignedInPanelProps) {
  return (
    <Box component="section">
      <Box component="header" sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr auto', sm: 'minmax(0, 1fr) minmax(0, 2fr) minmax(0, 1fr)' }, alignItems: 'center', gap: 1, color: 'primary.main', borderBottom: '1px solid', borderColor: 'divider', pb: 1 }}>
        <Typography variant="h4" component="h1" sx={{ minWidth: 0, overflowWrap: 'anywhere', gridColumn: meterId ? '1 / -1' : 1 }}>
          {meterId ? `Meter ${meterId}` : 'Meters'}
        </Typography>
        {!meterId && search && <Box sx={{ minWidth: 0, gridColumn: { xs: '1 / -1', sm: 2 }, gridRow: { xs: 2, sm: 1 } }}>{search}</Box>}
        {!meterId && user.is_admin && (
          <Tabs value={adminView} onChange={(_, value: AdminMeterView) => onAdminViewChange?.(value)} aria-label="Meter scope" textColor="primary"
            sx={{ gridColumn: { xs: 2, sm: 3 }, gridRow: 1, justifySelf: 'end', minHeight: 36, '& .MuiTab-root': { minWidth: 48, minHeight: 36, p: 1, textTransform: 'none', opacity: 1, '&.Mui-selected': { fontWeight: 700 } } }}>
            <Tab id="meter-tab-mine" aria-controls="meter-workspace-content" aria-label="My meters" label="My" value="mine" disabled={busy} />
            <Tab id="meter-tab-all" aria-controls="meter-workspace-content" aria-label="All meters" label="All" value="all" disabled={busy} />
          </Tabs>
        )}
      </Box>
      <Box sx={{ py: { xs: 2, sm: 3 } }}>
        <Stack id="meter-workspace-content" spacing={2} role={!meterId && user.is_admin ? 'tabpanel' : undefined}
          aria-labelledby={!meterId && user.is_admin ? `meter-tab-${adminView}` : undefined}>
          {error && <Alert severity="error">{error}</Alert>}
          {children}
        </Stack>
      </Box>
    </Box>
  );
}
