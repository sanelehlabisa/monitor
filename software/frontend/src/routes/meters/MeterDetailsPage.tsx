import { Alert, Box, IconButton, Stack, TextField, Typography } from '@mui/material';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import SaveOutlinedIcon from '@mui/icons-material/SaveOutlined';
import type { FormEvent, ReactNode } from 'react';
import { useEffect, useRef, useState } from 'react';

import type { Meter } from '../../lib/api';

type MeterDetailsPageProps = {
  selectedMeter: Meter;
  selectedContent?: ReactNode;
  busy: boolean;
  error: string;
  editName: string;
  onEditNameChange: (name: string) => void;
  onRename: (meter: Meter, name: string) => Promise<boolean>;
};

export function MeterDetailsPage({ selectedMeter, selectedContent, busy, error,
  editName, onEditNameChange, onRename }: MeterDetailsPageProps) {
  const [editingId, setEditingId] = useState<string | null>(null);
  const selectedNameInput = useRef<HTMLInputElement>(null);
  useEffect(() => {
    if (selectedMeter && editingId === selectedMeter.id) selectedNameInput.current?.focus();
  }, [editingId, selectedMeter?.id]);
  function startEditing(meter: Meter) {
    setEditingId(meter.id);
    onEditNameChange(meter.name);
  }
  async function saveName(event: FormEvent<HTMLFormElement>, meter: Meter, value: string) {
    event.preventDefault();
    if (editingId === meter.id && await onRename(meter, value)) setEditingId(null);
  }
  return (
    <Stack spacing={2.5}>
      <Box component="form" aria-label="Meter details"
        onSubmit={(event) => void saveName(event, selectedMeter, editName)}
        onKeyDown={(event) => { if (event.key === 'Escape' && !busy) { setEditingId(null); onEditNameChange(selectedMeter.name); } }}
        sx={{ display: 'grid', gridTemplateColumns: 'auto minmax(0, 1fr) auto', gap: 1, alignItems: 'center', borderBottom: '1px solid', borderColor: 'divider', py: 2 }}>
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
        <Typography sx={{ fontWeight: 700 }}>Created by:</Typography>
        <Typography sx={{ gridColumn: '2 / 4', overflowWrap: 'anywhere' }}>{selectedMeter.owner_email}</Typography>
      </Box>
      {error && <Alert severity="error">{error}</Alert>}
      {selectedContent}
    </Stack>
  );
}
