import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import BackspaceOutlinedIcon from '@mui/icons-material/BackspaceOutlined';
import BeenhereOutlinedIcon from '@mui/icons-material/BeenhereOutlined';
import CenterFocusStrongIcon from '@mui/icons-material/CenterFocusStrong';
import ClearIcon from '@mui/icons-material/Clear';
import type { FormEvent, ReactNode } from 'react';

import type { Meter } from './api';

export type AdminMeterView = 'mine' | 'all';

type MeterWorkspaceProps = {
  meters: Meter[];
  selectedMeter: Meter | null;
  selectedContent?: ReactNode;
  isAdmin: boolean;
  currentUserEmail: string;
  adminView: AdminMeterView;
  loading: boolean;
  busy: boolean;
  error: string;
  name: string;
  editName: string;
  search: string;
  onNameChange: (name: string) => void;
  onEditNameChange: (name: string) => void;
  onCreate: (event: FormEvent<HTMLFormElement>) => void;
  onRename: (event: FormEvent<HTMLFormElement>) => void;
  onDelete: () => void;
  onSelect: (meter: Meter) => void;
  onBack: () => void;
  onAdminViewChange: (view: AdminMeterView) => void;
  onSearchChange: (value: string) => void;
  onSearch: (event: FormEvent<HTMLFormElement>) => void;
  onClearSearch: () => void;
};

export function MeterWorkspace({
  meters,
  selectedMeter,
  selectedContent,
  isAdmin,
  currentUserEmail,
  adminView,
  loading,
  busy,
  error,
  name,
  editName,
  search,
  onNameChange,
  onEditNameChange,
  onCreate,
  onRename,
  onDelete,
  onSelect,
  onBack,
  onAdminViewChange,
  onSearchChange,
  onSearch,
  onClearSearch,
}: MeterWorkspaceProps) {
  if (selectedMeter) {
    return (
      <Stack spacing={2.5}>
        <Button
          onClick={onBack}
          size="small"
          startIcon={<ArrowBackIcon />}
          sx={{ alignSelf: 'flex-start' }}
        >
          Back to meters
        </Button>
        <Stack
          direction={{ xs: 'column', sm: 'row' }}
          spacing={{ xs: 0.25, sm: 1.5 }}
          sx={{ alignItems: { sm: 'baseline' } }}
        >
          <Typography component="h2" sx={{ fontWeight: 800 }} variant="h4">
            {selectedMeter.name}
          </Typography>
          <Typography color="text.secondary" variant="body2">
            Owner: {selectedMeter.owner_email}
          </Typography>
        </Stack>
        {error && <Alert severity="error">{error}</Alert>}
        {selectedContent}
        <Box component="form" onSubmit={onRename}>
          <Stack spacing={1.25}>
            <TextField
              disabled={busy}
              fullWidth
              label="Rename meter"
              onChange={(event) => onEditNameChange(event.target.value)}
              required
              slotProps={{ htmlInput: { maxLength: 80 } }}
              value={editName}
            />
            <Stack direction="row" spacing={1}>
              <Button
                disabled={busy || !editName.trim() || editName === selectedMeter.name}
                startIcon={<BeenhereOutlinedIcon />}
                type="submit"
                variant="outlined"
              >
                Save name
              </Button>
              <Button
                color="error"
                disabled={busy}
                onClick={onDelete}
                startIcon={<BackspaceOutlinedIcon />}
                type="button"
              >
                Delete meter
              </Button>
            </Stack>
          </Stack>
        </Box>
      </Stack>
    );
  }

  const visibleMeters =
    isAdmin && adminView === 'mine'
      ? meters.filter(
          (meter) =>
            meter.owner_email.trim().toLowerCase() ===
            currentUserEmail.trim().toLowerCase(),
        )
      : meters;
  const emptyTitle = isAdmin
    ? adminView === 'mine'
      ? 'No meters owned by this admin account yet'
      : 'No meters in the system yet'
    : 'No meters yet';

  return (
    <Stack spacing={2.5}>
      <Box component="form" onSubmit={onCreate}>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.25}>
          <TextField
            disabled={busy}
            fullWidth
            label="Meter name"
            onChange={(event) => onNameChange(event.target.value)}
            placeholder="Home"
            required
            slotProps={{ htmlInput: { maxLength: 80 } }}
            value={name}
          />
          <Button
            disabled={busy || !name.trim()}
            startIcon={<AddIcon />}
            type="submit"
            variant="contained"
          >
            {busy ? 'Adding…' : 'Add meter'}
          </Button>
        </Stack>
      </Box>
      {isAdmin && (
        <Stack direction="row" spacing={1}>
          <Button
            fullWidth
            onClick={() => onAdminViewChange('mine')}
            variant={adminView === 'mine' ? 'contained' : 'outlined'}
          >
            My meters
          </Button>
          <Button
            fullWidth
            onClick={() => onAdminViewChange('all')}
            variant={adminView === 'all' ? 'contained' : 'outlined'}
          >
            All meters
          </Button>
        </Stack>
      )}
      <Box component="form" onSubmit={onSearch}>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1}>
          <TextField
            disabled={busy || loading}
            fullWidth
            label="Search meters"
            onChange={(event) => onSearchChange(event.target.value)}
            placeholder={isAdmin ? 'Name or owner email' : 'Meter name'}
            slotProps={{ htmlInput: { maxLength: 254 } }}
            value={search}
          />
          <Button
            disabled={busy || loading}
            startIcon={<CenterFocusStrongIcon />}
            type="submit"
            variant="outlined"
          >
            Search
          </Button>
          <Button
            disabled={busy || loading || !search.trim()}
            onClick={onClearSearch}
            startIcon={<ClearIcon />}
            type="button"
          >
            Clear
          </Button>
        </Stack>
      </Box>
      {error && <Alert severity="error">{error}</Alert>}
      {loading ? (
        <Box sx={{ display: 'grid', minHeight: 140, placeItems: 'center' }}>
          <CircularProgress aria-label="Loading meters" color="inherit" size={28} />
        </Box>
      ) : visibleMeters.length === 0 ? (
        <Box
          sx={{
            bgcolor: 'background.default',
            border: '1px dashed',
            borderColor: 'divider',
            borderRadius: 2,
            p: 3,
            textAlign: 'center',
          }}
        >
          <Typography sx={{ fontWeight: 700 }}>
            {search.trim() ? 'No meters match this search' : emptyTitle}
          </Typography>
          <Typography color="text.secondary" sx={{ mt: 0.75 }} variant="body2">
            Add a simple name such as Home or Shop. No meter number or hardware is
            required.
          </Typography>
        </Box>
      ) : (
        <Stack spacing={1}>
          {visibleMeters.map((meter) => (
            <Button
              key={meter.id}
              onClick={() => onSelect(meter)}
              sx={{
                bgcolor: 'background.default',
                justifyContent: 'space-between',
                p: 2,
                textAlign: 'left',
              }}
              variant="text"
            >
              <span>
                <Typography component="span" sx={{ display: 'block', fontWeight: 700 }}>
                  {meter.name}
                </Typography>
                {isAdmin && adminView === 'all' && (
                  <Typography color="text.secondary" component="span" variant="caption">
                    {meter.owner_email}
                  </Typography>
                )}
              </span>
              <span aria-hidden="true">›</span>
            </Button>
          ))}
        </Stack>
      )}
    </Stack>
  );
}
