import { Box, Button, Menu, MenuItem, Stack, Typography } from '@mui/material';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import LogoutIcon from '@mui/icons-material/Logout';
import { useState } from 'react';

import type { User } from './api';

type NavigationProps = {
  user: User | null;
  busy: boolean;
  onLogout: () => void;
  onBack?: () => void;
};

export function Navigation({ user, busy, onLogout, onBack }: NavigationProps) {
  const [anchor, setAnchor] = useState<HTMLElement | null>(null);

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
        <>
          <Button id="account-button" aria-label="Account menu" disabled={busy}
            aria-controls={anchor ? 'account-menu' : undefined}
            aria-haspopup="true" aria-expanded={Boolean(anchor)}
            onClick={(event) => setAnchor(event.currentTarget)} endIcon={<AccountCircleIcon style={{ fontSize: 42 }} />}
            sx={{ justifySelf: 'end', gridColumn: 3, gridRow: 1, minWidth: 0, maxWidth: '100%', textTransform: 'none', color: 'text.primary',
              '& .MuiButton-endIcon': { ml: { xs: 0, sm: 0.5 }, mr: 0, flexShrink: 0 } }}>
            <Typography noWrap variant="body2" title={user.email} sx={{ display: { xs: 'none', sm: 'block' } }}>{user.email}</Typography>
          </Button>
          <Menu id="account-menu" anchorEl={anchor} open={Boolean(anchor)}
            onClose={() => setAnchor(null)}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            transformOrigin={{ vertical: 'top', horizontal: 'right' }}>
            <MenuItem disabled sx={{ opacity: '1 !important', whiteSpace: 'normal', overflowWrap: 'anywhere', maxWidth: 280 }}>
              <Typography variant="body2">{user.email}</Typography>
            </MenuItem>
            <MenuItem disabled={busy} sx={{ color: 'text.primary', fontWeight: 700 }}
              onClick={() => { setAnchor(null); onLogout(); }}>
              <LogoutIcon sx={{ mr: 1 }} />Sign out
            </MenuItem>
          </Menu>
        </>
      )}
    </Box>
  );
}
