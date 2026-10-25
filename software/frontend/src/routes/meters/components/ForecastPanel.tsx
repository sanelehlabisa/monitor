import { Alert, Box, CircularProgress, Stack, Typography } from '@mui/material';

import type { Forecast } from '../../../lib/api';
import { localDateDisplay, localDateTimeDisplay, utcDateDisplay } from '../../../lib/dateTime';

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
        py: { xs: 1.5, sm: 2 },
        borderTop: '1px solid',
        borderColor: 'divider',
      }}
    >
      <Typography color="text.secondary" variant="body2" sx={{ fontWeight: 500, mb: 0.75 }}>
        {label}
      </Typography>
      <Typography sx={{ color: colour, fontWeight: 700, fontSize: { xs: '1.25rem', sm: '1.5rem' }, lineHeight: 1.3, fontVariantNumeric: 'tabular-nums', letterSpacing: '-0.02em', overflowWrap: 'anywhere' }} variant="h5">
        {value}
      </Typography>
      {note && (
        <Typography color="text.secondary" variant="caption" sx={{ display: 'block', mt: 0.75, fontSize: '0.8125rem' }}>
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
  const usesDefault = forecast.status === 'available' && forecast.intervals_used === 0;

  return (
    <Stack spacing={2}>
      <Typography variant="body2">
        Next monthly top-up: {utcDateDisplay(forecast.planning_at)}
      </Typography>
      {forecast.status === 'not_enough_data' && (
        <Box sx={{ borderLeft: '3px solid', borderColor: 'primary.main', pl: 2, py: 1 }}>
          <Typography sx={{ fontWeight: 800 }}>Not enough data</Typography>
          <Typography color="text.secondary" sx={{ mt: 0.75 }} variant="body2">
            Add your first actual balance to see starting estimates.
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
            sx={{ fontWeight: 600, mb: 0.75 }}
            variant="h6"
          >
            Planning estimate
          </Typography>
          {usesDefault && (
            <Typography color="text.secondary" variant="body2">
              Starting estimate using {Number(forecast.daily_usage_kwh)} kWh/day.
              Add another balance to personalise it.
            </Typography>
          )}
          <Box
            sx={{
              display: 'grid',
              columnGap: { xs: 2, sm: 4 },
              rowGap: { xs: 0.5, sm: 1 },
              gridTemplateColumns: 'repeat(2, minmax(0, 1fr))',
              '@media (max-width: 359.95px)': { gridTemplateColumns: '1fr' },
              mt: 2,
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
                  : `Predicted run-out ${localDateDisplay(forecast.run_out_at)}`
              }
            />
            <EstimateMetric
              label="Additional top-up"
              value={`${forecast.recommended_monthly_top_up_kwh} kWh`}
              note="After subtracting estimated balance."
              colour="secondary.main"
            />
            <EstimateMetric
              label="Monthly requirement"
              value={`${forecast.monthly_requirement_kwh} kWh`}
              note={`Total use for the ${forecast.planning_days}-day planning month.`}
              colour="secondary.main"
            />
          </Box>
          <Box component="details" sx={{ color: 'text.secondary', mt: 2 }}>
            <Typography component="summary" sx={{ cursor: 'pointer' }} variant="caption">
              Calculation details
            </Typography>
          <Typography
            sx={{ color: 'text.secondary', display: 'block', mt: 1.25 }}
            variant="caption"
          >
            {usesDefault
              ? `Assumed use ${Number(forecast.daily_usage_kwh)} kWh/day until a measured interval is available.`
              : `Estimated use ${forecast.daily_usage_kwh} kWh/day from ${forecast.intervals_used} valid interval(s).`}
            {' '}No safety buffer applied.
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
