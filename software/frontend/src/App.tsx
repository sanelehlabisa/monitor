import {
  AppBar,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Container,
  CssBaseline,
  Stack,
  TextField,
  ThemeProvider,
  Toolbar,
  Typography,
  createTheme,
} from '@mui/material';

const theme = createTheme({
  palette: {
    primary: { main: '#0b4f6c' },
    background: { default: '#f4f7f9' },
  },
});

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Roventics Monitor
          </Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="sm">
        <Box component="main" sx={{ py: 8 }}>
          <Card>
            <CardContent>
              <Stack spacing={2}>
                <Chip label="Software-only V1" sx={{ alignSelf: 'flex-start' }} />
                <Typography variant="h4" component="h1">
                  Plan electricity with simple kWh entries
                </Typography>
                <Typography color="text.secondary">
                  V1 will let you record balances and top-ups in kWh, then use that
                  history for clearly labelled estimates of how much electricity
                  you may need and when.
                </Typography>
                <Typography color="text.secondary">
                  Passwordless email access is planned but is not active in this
                  build.
                </Typography>
                <TextField
                  disabled
                  fullWidth
                  label="Email address"
                  type="email"
                  helperText="Email verification will be implemented in a follow-up ticket."
                />
                <Button disabled variant="contained">
                  Send one-time code
                </Button>
                <Typography variant="body2" color="text.secondary">
                  Balance entry, top-up entry and forecasts are not active in this
                  build. Hardware and OCR are not required for V1.
                </Typography>
              </Stack>
            </CardContent>
          </Card>
        </Box>
      </Container>
    </ThemeProvider>
  );
}
