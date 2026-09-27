import {
  AppBar,
  Box,
  Card,
  CardContent,
  Chip,
  Container,
  CssBaseline,
  Stack,
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
          <Typography variant="h6">Roventics Monitor</Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="sm">
        <Box component="main" sx={{ py: 8 }}>
          <Card>
            <CardContent>
              <Stack spacing={2}>
                <Chip
                  color="success"
                  label="Development stack ready"
                  sx={{ alignSelf: 'flex-start' }}
                />
                <Typography variant="h4" component="h1">
                  Meter monitoring foundation
                </Typography>
                <Typography color="text.secondary">
                  This Material UI screen confirms the frontend container is
                  running. Meter data and authentication arrive in later tickets.
                </Typography>
              </Stack>
            </CardContent>
          </Card>
        </Box>
      </Container>
    </ThemeProvider>
  );
}
