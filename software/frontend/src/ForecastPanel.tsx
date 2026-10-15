import { Alert, Box, CircularProgress, Stack, Typography } from '@mui/material';

import type { Forecast } from './api';
import { localDateDisplay, localDateTimeDisplay } from './dateTime';

type ForecastPanelProps = {
  forecast: Forecast | null;
  loading: boolean;
};

function EstimateMetric({ label, value, note, colour = 'primary.main' }: {
  label: string;
  value: string;
  note?: string;
  colour?: 'primary.main' | 'secondary.main';
}) {
  return (
    <Box
      sx={{
        minWidth: 0,
        py: 1,
      }}
    >
      <Typography color="text.secondary" variant="body2">
        {label}
      </Typography>
      <Typography sx={{ color: colour, fontWeight: 700, fontVariantNumeric: 'tabular-nums', letterSpacing: '-0.02em' }} variant="h5">
        {value}
      </Typography>
      {note && (
        <Typography color="text.secondary" variant="caption">
          {note}
        </Typography>
      )}
    </Box>
  );
}

export function ForecastPanel({ forecast, loading }: ForecastPanelProps) {
  if (loading) {
    return (
      <Box sx={{ display: 'grid', minHeight: 120, placeItems: 'center' }}>
        <CircularProgress
          aria-label="Loading forecast"
          color="inherit"
          size={28}
        />
      </Box>
    );
  }

  if (!forecast) {
    return <Alert severity="warning">Estimates unavailable. Refresh to try again.</Alert>;
  }

  const hasActual =
    forecast.latest_actual_balance_kwh !== null &&
    forecast.latest_actual_at !== null;

  return (
    <Stack spacing={2}>
      {forecast.status === 'not_enough_data' && (
        <Box sx={{ borderLeft: '3px solid', borderColor: 'primary.main', pl: 2, py: 1 }}>
          <Typography sx={{ fontWeight: 800 }}>Not enough data</Typography>
          <Typography color="text.secondary" sx={{ mt: 0.75 }} variant="body2">
            Add at least two actual balances. Monitor will not guess a forecast.
          </Typography>
        </Box>
      )}

      {forecast.status === 'inconsistent_history' && (
        <Alert severity="warning">
          <Typography sx={{ fontWeight: 800 }}>Inconsistent history</Typography>
          Check balance times and top-ups. The recorded history implies an
          unexplained balance increase, so Monitor has withheld estimates.
        </Alert>
      )}

      {forecast.status === 'available' && (
        <Box
          component="section" aria-label="Planning estimate"
          sx={{ py: 2, borderBottom: '1px solid', borderColor: 'divider' }}
        >
          <Typography
            component="h3"
            sx={{ color: 'text.secondary', fontWeight: 700 }}
            variant="caption"
          >
            Planning estimate
          </Typography>
          <Box
            sx={{
              display: 'grid',
              gap: { xs: 2, sm: 3 },
              gridTemplateColumns: {
                xs: '1fr',
                sm: 'repeat(2, minmax(0, 1fr))',
                md: 'repeat(3, minmax(0, 1fr))',
              },
              mt: 1.25,
            }}
          >
            <EstimateMetric
              label="Estimated balance"
              value={`${forecast.estimated_balance_kwh} kWh`}
            />
            <EstimateMetric
              label="Estimated remaining"
              value={
                forecast.remaining_days === null
                  ? 'No finite run-out'
                  : `${forecast.remaining_days} days`
              }
              note={
                forecast.run_out_at === null
                  ? 'No run-out at observed use'
                  : `Top up by ${localDateDisplay(forecast.run_out_at)}`
              }
            />
            <Box sx={{ gridColumn: { sm: '1 / -1', md: 'auto' }, borderTop: '1px solid', borderColor: 'divider', borderTopWidth: { md: 0 }, pt: { xs: 2, md: 0 } }}>
              <EstimateMetric
                label="Monthly purchase recommendation"
                value={`${forecast.recommended_top_up_30_days_kwh} kWh`}
                colour="secondary.main"
              />
              <Typography color="text.secondary" variant="body2">
                Additional kWh for the next 30 days, based on historical usage.
              </Typography>
            </Box>
          </Box>
          <Box component="details" sx={{ color: 'text.secondary', mt: 2 }}>
            <Typography component="summary" sx={{ cursor: 'pointer' }} variant="caption">
              Calculation details
            </Typography>
          <Typography
            sx={{ color: 'text.secondary', display: 'block', mt: 1.25 }}
            variant="caption"
          >
            Estimated use {forecast.daily_usage_kwh} kWh/day from {forecast.intervals_used}{' '}
            valid interval(s). No safety buffer applied.
          </Typography>
          </Box>
        </Box>
      )}

      {hasActual ? (
        <Typography color="text.secondary" variant="body2">
          Latest actual balance: {forecast.latest_actual_balance_kwh} kWh.
          {' '}Observed {localDateTimeDisplay(forecast.latest_actual_at!)}
        </Typography>
      ) : (
        <Typography color="text.secondary" variant="body2">
          No actual balance recorded yet.
        </Typography>
      )}
      <Typography color="text.secondary" variant="caption">
        Calculated {localDateTimeDisplay(forecast.as_of)}
      </Typography>
    </Stack>
  );
}
