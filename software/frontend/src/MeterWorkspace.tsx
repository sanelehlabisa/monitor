import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import type { FormEvent } from 'react';

import type { Meter } from './api';

type MeterWorkspaceProps = {
  meters: Meter[];
  selectedMeter: Meter | null;
  loading: boolean;
  busy: boolean;
  error: string;
  name: string;
  onNameChange: (name: string) => void;
  onCreate: (event: FormEvent<HTMLFormElement>) => void;
  onSelect: (meter: Meter) => void;
  onBack: () => void;
};

export function MeterWorkspace({
  meters,
  selectedMeter,
  loading,
  busy,
  error,
  name,
  onNameChange,
  onCreate,
  onSelect,
  onBack,
}: MeterWorkspaceProps) {
  if (selectedMeter) {
    return (
      <Stack spacing={2.5}>
        <Button onClick={onBack} size="small" sx={{ alignSelf: 'flex-start' }}>
          Back to meters
        </Button>
        <Box>
          <Typography component="h2" variant="h5">
            {selectedMeter.name}
          </Typography>
          <Typography color="text.secondary" variant="body2">
            Software meter profile
          </Typography>
        </Box>
        <Box
          sx={{
            bgcolor: 'background.default',
            borderRadius: 2,
            p: 2.5,
          }}
        >
          <Typography sx={{ fontWeight: 800 }}>Not enough data</Typography>
          <Typography color="text.secondary" sx={{ mt: 0.75 }} variant="body2">
            Add balance and purchased-kWh history in the next step before Monitor
            calculates any estimates.
          </Typography>
        </Box>
      </Stack>
    );
  }

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
            type="submit"
            variant="contained"
          >
            {busy ? 'Adding…' : 'Add meter'}
          </Button>
        </Stack>
      </Box>
      {error && <Alert severity="error">{error}</Alert>}
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
            borderRadius: 2,
            p: 3,
            textAlign: 'center',
          }}
        >
          <Typography sx={{ fontWeight: 700 }}>No meters yet</Typography>
          <Typography color="text.secondary" sx={{ mt: 0.75 }} variant="body2">
            Add a simple name such as Home or Shop. No meter number or hardware is
            required.
          </Typography>
        </Box>
      ) : (
        <Stack spacing={1}>
          {meters.map((meter) => (
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
              <span>{meter.name}</span>
              <span aria-hidden="true">›</span>
            </Button>
          ))}
        </Stack>
      )}
    </Stack>
  );
}
