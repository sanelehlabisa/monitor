import { Box, IconButton, InputAdornment, TextField, Tooltip } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ClearIcon from '@mui/icons-material/Clear';
import type { FormEvent } from 'react';

export function MeterSearch({ busy, value, active, onChange, onSubmit, onClear }: {
  busy: boolean; value: string; active: boolean;
  onChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onClear: () => void;
}) {
  return (
    <Box component="form" onSubmit={onSubmit}>
      <TextField disabled={busy} fullWidth label="Search meters" value={value}
        onChange={(event) => onChange(event.target.value)} placeholder="Name or member email"
        slotProps={{ htmlInput: { maxLength: 254 }, input: { endAdornment: (
          <InputAdornment position="end">
            <Tooltip title="Search"><span><IconButton aria-label="Search meters" disabled={busy} type="submit"><SearchIcon /></IconButton></span></Tooltip>
            <Tooltip title="Clear search"><span><IconButton aria-label="Clear search" disabled={busy || (!value.trim() && !active)} onClick={onClear} type="button"><ClearIcon /></IconButton></span></Tooltip>
          </InputAdornment>
        ) } }} />
    </Box>
  );
}
