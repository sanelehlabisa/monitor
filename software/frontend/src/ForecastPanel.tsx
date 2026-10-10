import { Alert, Box, CircularProgress, Stack, Typography } from '@mui/material';

import type { Forecast } from './api';
import { localDateDisplay, localDateTimeDisplay } from './dateTime';

type ForecastPanelProps = {
  forecast: Forecast | null;
  loading: boolean;
};

function EstimateCard({ label, value }: { label: string; value: string }) {
  return (
    <Box
      sx={{
        bgcolor: 'rgba(255, 255, 255, 0.1)',
        borderRadius: 2,
        minWidth: 0,
        p: 1.75,
      }}
    >
      <Typography sx={{ color: 'rgba(255, 255, 255, 0.75)' }} variant="caption">
        {label}
      </Typography>
      <Typography sx={{ color: 'common.white', fontWeight: 800 }} variant="h6">
        {value}
      </Typography>
    </Box>
  );
}

export function ForecastPanel({ forecast, loading }: ForecastPanelProps) {
  if (loading || !forecast) {
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

  const hasActual =
    forecast.latest_actual_balance_kwh !== null &&
    forecast.latest_actual_at !== null;

  return (
    <Stack spacing={2}>
      {forecast.status === 'not_enough_data' && (
        <Box sx={{ bgcolor: 'background.default', borderRadius: 2, p: 2.5 }}>
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
          sx={{ bgcolor: 'primary.main', borderRadius: 2.5, p: { xs: 2, sm: 2.5 } }}
        >
          <Typography
            component="h3"
            sx={{ color: 'common.white', fontWeight: 800 }}
            variant="h5"
          >
            Planning estimate
          </Typography>
          <Box
            sx={{
              display: 'grid',
              gap: 1,
              gridTemplateColumns: {
                xs: '1fr',
                sm: 'repeat(2, minmax(0, 1fr))',
                md: 'repeat(4, minmax(0, 1fr))',
              },
              mt: 1.25,
            }}
          >
            <EstimateCard
              label="Estimated balance now"
              value={`${forecast.estimated_balance_kwh} kWh`}
            />
            <EstimateCard
              label="Estimated remaining"
              value={
                forecast.remaining_days === null
                  ? 'No finite run-out'
                  : `${forecast.remaining_days} days`
              }
            />
            <EstimateCard
              label="Top up by"
              value={
                forecast.run_out_at === null
                  ? 'No run-out at observed use'
                  : localDateDisplay(forecast.run_out_at)
              }
            />
            <EstimateCard
              label="Recommended top-up for 30 days"
              value={`${forecast.recommended_top_up_30_days_kwh} kWh`}
            />
          </Box>
          <Typography
            sx={{ color: 'rgba(255, 255, 255, 0.75)', display: 'block', mt: 1.25 }}
            variant="caption"
          >
            Estimated use {forecast.daily_usage_kwh} kWh/day. Calculated{' '}
            {localDateTimeDisplay(forecast.as_of)} from {forecast.intervals_used}{' '}
            valid interval(s). No safety buffer applied.
          </Typography>
        </Box>
      )}

      {hasActual ? (
        <Box
          sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2, p: 2 }}
        >
          <Typography color="text.secondary" variant="caption">
            Latest actual balance
          </Typography>
          <Typography sx={{ fontWeight: 800 }} variant="h5">
            {forecast.latest_actual_balance_kwh} kWh
          </Typography>
          <Typography color="text.secondary" variant="caption">
            Observed {localDateTimeDisplay(forecast.latest_actual_at!)}
          </Typography>
        </Box>
      ) : (
        <Typography color="text.secondary" variant="body2">
          No actual balance recorded yet.
        </Typography>
      )}
    </Stack>
  );
}
