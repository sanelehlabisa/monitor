import { Alert, Box, CircularProgress, Stack, Typography } from '@mui/material';

import type { Forecast } from './api';

type ForecastPanelProps = {
  forecast: Forecast | null;
  loading: boolean;
};

function EstimateCard({ label, value }: { label: string; value: string }) {
  return (
    <Box
      sx={{
        bgcolor: 'background.default',
        borderRadius: 2,
        minWidth: 0,
        p: 1.75,
      }}
    >
      <Typography color="text.secondary" variant="caption">
        {label}
      </Typography>
      <Typography sx={{ fontWeight: 800 }} variant="h6">
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
            Observed {new Date(forecast.latest_actual_at!).toLocaleString()}
          </Typography>
        </Box>
      ) : (
        <Typography color="text.secondary" variant="body2">
          No actual balance recorded yet.
        </Typography>
      )}

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
        <Box>
          <Typography component="h3" sx={{ fontWeight: 800 }} variant="h6">
            Planning estimate
          </Typography>
          <Box
            sx={{
              display: 'grid',
              gap: 1,
              gridTemplateColumns: {
                xs: '1fr',
                sm: 'repeat(2, minmax(0, 1fr))',
              },
              mt: 1.25,
            }}
          >
            <EstimateCard
              label="Estimated balance now"
              value={`${forecast.estimated_balance_kwh} kWh`}
            />
            <EstimateCard
              label="Estimated daily use"
              value={`${forecast.daily_usage_kwh} kWh/day`}
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
              label="Estimated run-out"
              value={
                forecast.run_out_at === null
                  ? 'No run-out at observed use'
                  : new Date(forecast.run_out_at).toLocaleDateString()
              }
            />
            <Box sx={{ gridColumn: { sm: '1 / -1' } }}>
              <EstimateCard
                label="Recommended top-up for 30 days"
                value={`${forecast.recommended_top_up_30_days_kwh} kWh`}
              />
            </Box>
          </Box>
          <Typography color="text.secondary" sx={{ mt: 1.25 }} variant="caption">
            Calculated {new Date(forecast.as_of).toLocaleString()} from{' '}
            {forecast.intervals_used} valid interval(s). No safety buffer applied.
          </Typography>
        </Box>
      )}
    </Stack>
  );
}
