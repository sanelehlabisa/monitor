import { Box, Button, Stack, Typography } from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import LogoutIcon from '@mui/icons-material/Logout';

import type { User } from '../lib/api';

type NavigationProps = {
  user: User | null;
  busy: boolean;
  onLogout: () => void;
  onBack?: () => void;
};

export function Navigation({ user, busy, onLogout, onBack }: NavigationProps) {
  return (
    <Box component={user ? 'nav' : 'header'} aria-label={user ? 'Main navigation' : undefined}
      sx={{ display: 'grid', alignItems: 'center', gridTemplateColumns: 'minmax(0, 1fr) auto minmax(0, 1fr)', gap: 1 }}>
      {user && onBack && (
        <Button disabled={busy} onClick={onBack} size="small" startIcon={<ArrowBackIcon />}
          sx={{ gridColumn: 1, gridRow: 1, justifySelf: 'start', textTransform: 'none' }}>Back</Button>
      )}
      <Stack spacing={0.5} sx={{ gridColumn: 2, gridRow: 1, alignItems: 'center' }}>
        <Box component="img" src="/monitor-logo.png" alt="Monitor logo" width={48} height={48} sx={{ display: 'block' }} />
        <Typography component="span" variant="h4" color="primary" sx={{ fontWeight: 700 }}>Monitor</Typography>
      </Stack>
      {user && (
        <Stack direction="row" spacing={0.5} sx={{ alignItems: 'center', justifySelf: 'end', gridColumn: 3, gridRow: 1, minWidth: 0, maxWidth: '100%' }}>
          <Typography noWrap variant="body2" title={user.email} sx={{ minWidth: 0 }}>{user.email}</Typography>
          <Button color="error" variant="contained" disabled={busy} onClick={onLogout} startIcon={<LogoutIcon />}
            sx={{ flexShrink: 0, minWidth: 0, px: { xs: 0.5, sm: 1 }, whiteSpace: 'nowrap', '& .MuiButton-startIcon': { mr: 0.5 } }}>
            Sign out
          </Button>
        </Stack>
      )}
    </Box>
  );
}
