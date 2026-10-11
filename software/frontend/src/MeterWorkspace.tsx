import {
  Alert,
  Box,
  Button,
  CircularProgress,
  IconButton,
  InputAdornment,
  Stack,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteOutlinedIcon from '@mui/icons-material/DeleteOutlined';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import SearchIcon from '@mui/icons-material/Search';
import SaveOutlinedIcon from '@mui/icons-material/SaveOutlined';
import ClearIcon from '@mui/icons-material/Clear';
import type { FormEvent, ReactNode } from 'react';
import { useEffect, useRef, useState } from 'react';

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
  onRename: (meter: Meter, name: string) => Promise<boolean>;
  onDelete: (meter: Meter) => void;
  onSelect: (meter: Meter) => void;
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
  onSearchChange,
  onSearch,
  onClearSearch,
}: MeterWorkspaceProps) {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [rowName, setRowName] = useState('');
  const selectedNameInput = useRef<HTMLInputElement>(null);
  useEffect(() => {
    if (selectedMeter && editingId === selectedMeter.id) selectedNameInput.current?.focus();
  }, [editingId, selectedMeter?.id]);
  function startEditing(meter: Meter) {
    setEditingId(meter.id);
    setRowName(meter.name);
    onEditNameChange(meter.name);
  }
  async function saveName(event: FormEvent<HTMLFormElement>, meter: Meter, value: string) {
    event.preventDefault();
    if (editingId === meter.id && await onRename(meter, value)) setEditingId(null);
  }
  if (selectedMeter) {
    return (
      <Stack spacing={2.5}>
        <Box component="form" aria-label="Meter details"
          onSubmit={(event) => void saveName(event, selectedMeter, editName)}
          onKeyDown={(event) => { if (event.key === 'Escape' && !busy) { setEditingId(null); onEditNameChange(selectedMeter.name); } }}
          sx={{ display: 'grid', gridTemplateColumns: 'auto minmax(0, 1fr) auto', gap: 1, alignItems: 'center', bgcolor: 'background.default', borderRadius: 2, p: 2 }}>
          <Typography component="label" htmlFor="selected-meter-name" sx={{ fontWeight: 700 }}>Name:</Typography>
            <TextField
              id="selected-meter-name"
              inputRef={selectedNameInput}
              disabled={busy}
              fullWidth
              size="small"
              onChange={(event) => onEditNameChange(event.target.value)}
              required
              slotProps={{ htmlInput: { maxLength: 80, readOnly: editingId !== selectedMeter.id } }}
              value={editingId === selectedMeter.id ? editName : selectedMeter.name}
            />
          <IconButton aria-label={editingId === selectedMeter.id ? `Save name for ${selectedMeter.name}` : `Rename ${selectedMeter.name}`}
            title={editingId === selectedMeter.id ? 'Save name' : 'Rename meter'} type={editingId === selectedMeter.id ? 'submit' : 'button'}
            onClick={editingId === selectedMeter.id ? undefined : (event) => { event.preventDefault(); startEditing(selectedMeter); }}
            disabled={busy || (editingId === selectedMeter.id && (!editName.trim() || editName === selectedMeter.name))}>
            {editingId === selectedMeter.id ? <SaveOutlinedIcon /> : <EditOutlinedIcon />}</IconButton>
          <Typography sx={{ fontWeight: 700 }}>Owner:</Typography>
          <Typography sx={{ gridColumn: '2 / 4', overflowWrap: 'anywhere' }}>{selectedMeter.owner_email}</Typography>
        </Box>
        {error && <Alert severity="error">{error}</Alert>}
        {selectedContent}
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
      <Box component="form" onSubmit={onSearch}>
          <TextField
            disabled={busy || loading}
            fullWidth
            label="Search meters"
            onChange={(event) => onSearchChange(event.target.value)}
            placeholder={isAdmin ? 'Name or owner email' : 'Meter name'}
            slotProps={{ htmlInput: { maxLength: 254 }, input: { endAdornment: (
              <InputAdornment position="end">
                <Tooltip title="Search"><span><IconButton aria-label="Search meters" disabled={busy || loading} type="submit"><SearchIcon /></IconButton></span></Tooltip>
                <Tooltip title="Clear search"><span><IconButton aria-label="Clear search" disabled={busy || loading || !search.trim()} onClick={onClearSearch} type="button"><ClearIcon /></IconButton></span></Tooltip>
              </InputAdornment>
            ) } }}
            value={search}
          />
      </Box>
      <Stack spacing={1} aria-label="Meter list">
        <Box component="form" onSubmit={onCreate} sx={{ display: 'flex', gap: 0.5, alignItems: 'center', bgcolor: 'background.default', borderRadius: 2, p: 1 }}>
          <TextField disabled={busy || loading} fullWidth label="Meter name" placeholder="Home" required value={name}
            onChange={(event) => onNameChange(event.target.value)} slotProps={{ htmlInput: { maxLength: 80 } }} />
          <Tooltip title="Add meter"><span><IconButton aria-label="Add meter" disabled={busy || loading || !name.trim()} type="submit"><AddIcon /></IconButton></span></Tooltip>
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
            <Stack direction="row" key={meter.id} spacing={0.5}
              sx={{ alignItems: 'center', bgcolor: 'background.default', borderRadius: 2, p: 1 }}>
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
                    {meter.owner_email}
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
