import { Alert, Box, Stack, Tab, Tabs, Typography } from '@mui/material';
import type { ReactNode } from 'react';

import type { User } from '../../../lib/api';
import type { AdminMeterView } from '../MetersPage';

type MeterSectionProps = {
  user: User;
  error: string;
  children?: ReactNode;
  meterId?: string;
  adminView?: AdminMeterView;
  busy?: boolean;
  search?: ReactNode;
  onAdminViewChange?: (view: AdminMeterView) => void;
};

export function MeterSection({
  user,
  error,
  children,
  meterId,
  adminView = 'mine',
  busy = false,
  search,
  onAdminViewChange,
}: MeterSectionProps) {
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
