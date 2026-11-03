import { Box, Button, Stack, Typography } from '@mui/material';
import AccountBalanceWalletOutlinedIcon from '@mui/icons-material/AccountBalanceWalletOutlined';
import BoltOutlinedIcon from '@mui/icons-material/BoltOutlined';
import BeenhereOutlinedIcon from '@mui/icons-material/BeenhereOutlined';

const benefits = [
  { title: 'See what you have left', detail: 'Estimate your current electricity balance.', icon: AccountBalanceWalletOutlinedIcon },
  { title: 'Know when to top up', detail: 'See how many days your units could last.', icon: BoltOutlinedIcon },
  { title: 'Plan your monthly purchase', detail: 'Get a recommended top-up amount in kWh.', icon: BeenhereOutlinedIcon },
];

export function HomePage({ onLogin }: { onLogin: () => void }) {
  return (
    <Stack component="section" spacing={3} sx={{ py: { xs: 1, sm: 2 } }}>
      <Box sx={{ p: { xs: 2.5, sm: 3.5 }, bgcolor: 'primary.light', borderRadius: 3 }}>
        <Typography color="secondary.main" variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
          Prepaid electricity planning
        </Typography>
        <Typography component="h1" sx={{ fontWeight: 700, fontSize: { xs: '1.75rem', sm: '2rem' }, lineHeight: 1.2, letterSpacing: '-0.025em' }}>
          Know how much to buy and when.
        </Typography>
        <Typography color="text.secondary" sx={{ mt: 1.5 }}>
          Add your meter balance and top-ups. Monitor turns your readings into simple estimates.
        </Typography>
      </Box>
      <Box component="ul" sx={{ listStyle: 'none', p: 0, m: 0 }}>
        {benefits.map(({ title, detail, icon: Icon }) => (
          <Stack component="li" key={title} direction="row" spacing={2}
            sx={{ alignItems: 'center', py: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
            <Box sx={{ display: 'grid', placeItems: 'center', width: 40, height: 40, flexShrink: 0,
              borderRadius: 2, bgcolor: 'secondary.light', color: 'secondary.main' }}>
              <Icon fontSize="small" />
            </Box>
            <Box sx={{ minWidth: 0 }}>
              <Typography component="h2" variant="body1" sx={{ fontWeight: 600 }}>{title}</Typography>
              <Typography color="text.secondary" variant="body2">{detail}</Typography>
            </Box>
          </Stack>
        ))}
      </Box>
      <Button fullWidth size="large" variant="contained" onClick={onLogin}>Log in</Button>
    </Stack>
  );
}
