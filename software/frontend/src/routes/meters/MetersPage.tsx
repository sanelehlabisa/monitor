import {
  Alert,
  Box,
  Button,
  CircularProgress,
  IconButton,
  Stack,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteOutlinedIcon from '@mui/icons-material/DeleteOutlined';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import SaveOutlinedIcon from '@mui/icons-material/SaveOutlined';
import type { FormEvent } from 'react';
import { useState } from 'react';

import type { Meter } from '../../lib/api';

export type AdminMeterView = 'mine' | 'all';

type MetersPageProps = {
  meters: Meter[];
  isAdmin: boolean;
  adminView: AdminMeterView;
  loading: boolean;
  busy: boolean;
  error: string;
  name: string;
  search: string;
  onNameChange: (name: string) => void;
  onEditNameChange: (name: string) => void;
  onCreate: (event: FormEvent<HTMLFormElement>) => void;
  onRename: (meter: Meter, name: string) => Promise<boolean>;
  onDelete: (meter: Meter) => void;
  onSelect: (meter: Meter) => void;
  onRetry?: () => void;
};

export function MetersPage({
  meters,
  isAdmin,
  adminView,
  loading,
  busy,
  error,
  name,
  search,
  onNameChange,
  onEditNameChange,
  onCreate,
  onRename,
  onDelete,
  onSelect,
  onRetry,
}: MetersPageProps) {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [rowName, setRowName] = useState('');
  function startEditing(meter: Meter) {
    setEditingId(meter.id);
    setRowName(meter.name);
    onEditNameChange(meter.name);
  }
  async function saveName(event: FormEvent<HTMLFormElement>, meter: Meter, value: string) {
    event.preventDefault();
    if (editingId === meter.id && await onRename(meter, value)) setEditingId(null);
  }
  const emptyTitle = isAdmin
    ? adminView === 'mine'
      ? 'No meters linked to this account yet'
      : 'No meters in the system yet'
    : 'No meters yet';

  return (
    <Stack spacing={2.5}>
      <Stack spacing={1} aria-label="Meter list">
        <Box component="form" onSubmit={onCreate} sx={{ display: 'flex', gap: 0.5, alignItems: 'center', borderBottom: '1px solid', borderColor: 'divider', py: 1, px: 0.5 }}>
          <TextField disabled={busy || loading} fullWidth label="Meter name" placeholder="Home" required value={name}
            onChange={(event) => onNameChange(event.target.value)} slotProps={{ htmlInput: { maxLength: 80 } }} />
          <Tooltip title="Add meter"><span><IconButton aria-label="Add meter" disabled={busy || loading || !name.trim()} type="submit"><AddIcon /></IconButton></span></Tooltip>
        </Box>
      {error && <Alert severity="error" action={onRetry && <Button disabled={busy || loading} onClick={onRetry} size="small">Retry</Button>}>{error}</Alert>}
      {loading ? (
        <Box sx={{ display: 'grid', minHeight: 140, placeItems: 'center' }}>
          <CircularProgress aria-label="Loading meters" color="inherit" size={28} />
        </Box>
      ) : meters.length === 0 ? (
        <Box
          sx={{
            bgcolor: 'background.default',
            border: '1px dashed',
            borderColor: 'divider',
            borderRadius: '12px',
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
        <Stack component="ol" spacing={1} sx={{ m: 0, p: 0, listStyle: 'none' }}>
          {meters.map((meter, index) => (
            <Stack component="li" direction="row" key={meter.id} spacing={0.5}
              sx={{ alignItems: 'center', borderBottom: '1px solid', borderColor: 'divider', py: 1, px: 0.5,
                '&:hover, &:focus-within': { bgcolor: 'primary.light' } }}>
              <Typography component="span" color="text.secondary" sx={{ minWidth: 28, fontVariantNumeric: 'tabular-nums' }}>{index + 1}.</Typography>
              {editingId === meter.id ? (
                <Box component="form" sx={{ display: 'flex', flex: 1, minWidth: 0 }}
                  onKeyDown={(event) => { if (event.key === 'Escape' && !busy) setEditingId(null); }}
                  onSubmit={async (event) => {
                    await saveName(event, meter, rowName);
                  }}>
                  <TextField autoFocus disabled={busy} fullWidth required size="small" value={rowName}
                    onChange={(event) => setRowName(event.target.value)}
                    slotProps={{ htmlInput: { maxLength: 80, 'aria-label': `Rename ${meter.name}` } }} />
                  <IconButton aria-label={`Save name for ${meter.name}`} title="Save name" type="submit"
                    disabled={busy || !rowName.trim() || rowName === meter.name}><SaveOutlinedIcon /></IconButton>
                </Box>
              ) : <Button
              disabled={busy || loading}
              onClick={() => onSelect(meter)}
              sx={{
                flex: 1, minWidth: 0,
                justifyContent: 'space-between',
                p: 1,
                textAlign: 'left',
              }}
              variant="text"
            >
              <span>
                <Typography component="span" sx={{ display: 'block', fontWeight: 700, overflowWrap: 'anywhere' }}>
                  {meter.name}
                </Typography>
                {isAdmin && adminView === 'all' && (
                  <Typography color="text.secondary" component="span" variant="caption" sx={{ overflowWrap: 'anywhere' }}>
                    Created by: {meter.owner_email}
                  </Typography>
                )}
              </span>
              <span aria-hidden="true">›</span>
            </Button>}
              {editingId !== meter.id && <IconButton aria-label={`Rename ${meter.name}`} title="Rename meter" disabled={busy || loading}
                onClick={() => startEditing(meter)}><EditOutlinedIcon /></IconButton>}
              <IconButton aria-label={`Delete ${meter.name}`} title="Delete meter" color="error" disabled={busy || loading}
                onClick={() => onDelete(meter)}><DeleteOutlinedIcon /></IconButton>
            </Stack>
          ))}
        </Stack>
      )}
      </Stack>
    </Stack>
  );
}
