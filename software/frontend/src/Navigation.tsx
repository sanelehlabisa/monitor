import { Box, Button, Menu, MenuItem, Typography } from '@mui/material';
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
  if (!user) return null;

  return (
    <Box component="nav" aria-label="Main navigation"
      sx={{ display: 'grid', alignItems: 'center', gridTemplateColumns: 'auto minmax(0, 1fr)', gap: 1 }}>
      {user && onBack && (
        <Button disabled={busy} onClick={onBack} size="small" startIcon={<ArrowBackIcon />} sx={{ textTransform: 'none' }}>Back</Button>
      )}
      {user && (
        <>
          <Button id="account-button" aria-label="Account menu" disabled={busy}
            aria-controls={anchor ? 'account-menu' : undefined}
            aria-haspopup="true" aria-expanded={Boolean(anchor)}
            onClick={(event) => setAnchor(event.currentTarget)} endIcon={<AccountCircleIcon style={{ fontSize: 42 }} />}
            sx={{ justifySelf: 'end', gridColumn: 2, minWidth: 0, maxWidth: { xs: '100%', sm: 320 }, textTransform: 'none', color: 'text.primary' }}>
            <Typography noWrap variant="body2" title={user.email}>{user.email}</Typography>
          </Button>
          <Menu id="account-menu" anchorEl={anchor} open={Boolean(anchor)}
            onClose={() => setAnchor(null)}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            transformOrigin={{ vertical: 'top', horizontal: 'right' }}>
            <MenuItem disabled sx={{ opacity: '1 !important', whiteSpace: 'normal', overflowWrap: 'anywhere', maxWidth: 280 }}>
              <Typography variant="body2">{user.email}</Typography>
            </MenuItem>
            <MenuItem disabled={busy} sx={{ color: 'common.black', fontWeight: 700 }}
              onClick={() => { setAnchor(null); onLogout(); }}>
              <LogoutIcon sx={{ mr: 1 }} />Sign out
            </MenuItem>
          </Menu>
        </>
      )}
    </Box>
  );
}
