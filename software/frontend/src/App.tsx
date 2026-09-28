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
                <Chip label="Passwordless access planned" sx={{ alignSelf: 'flex-start' }} />
                <Typography variant="h4" component="h1">
                  Meter monitoring foundation
                </Typography>
                <Typography color="text.secondary">
                  Monitor will use a one-time code sent to an authorised email
                  address. Authentication is not active in this build.
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
                  Meter readings and dashboard features remain intentionally out of
                  scope for this foundation.
                </Typography>
              </Stack>
            </CardContent>
          </Card>
        </Box>
      </Container>
    </ThemeProvider>
  );
}
