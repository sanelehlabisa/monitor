import { createTheme } from '@mui/material';

export const theme = createTheme({
  // Deeper logo-inspired colours keep text readable on the light surfaces.
  palette: {
    primary: { main: '#005aae', light: '#e2f0ff', contrastText: '#ffffff' },
    secondary: { main: '#007782', dark: '#005d7a', light: '#e7f6f5', contrastText: '#ffffff' },
    background: { default: '#ffffff', paper: '#ffffff' },
    text: { primary: '#16324b', secondary: '#4b6173' },
    divider: '#cee1ed',
  },
  typography: {
    fontFamily: '"Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, Arial, sans-serif',
    body1: { fontSize: '0.875rem', lineHeight: 1.5 },
    body2: { fontSize: '0.875rem', lineHeight: 1.5 },
    caption: { fontSize: '0.875rem', lineHeight: 1.5 },
    subtitle1: { fontSize: '0.875rem' },
    subtitle2: { fontSize: '0.875rem' },
    button: { fontSize: '0.875rem' },
    h4: { fontSize: '1.125rem', fontWeight: 600, lineHeight: 1.4 },
    h5: { fontSize: '1.25rem', fontWeight: 700, lineHeight: 1.4 },
    h6: { fontSize: '1.125rem', fontWeight: 600, lineHeight: 1.4 },
  },
  shape: { borderRadius: 12 },
  components: {
    MuiButton: {
      defaultProps: { disableElevation: true, size: 'small' },
      styleOverrides: {
        root: ({ theme }) => ({ textTransform: 'none', fontWeight: 600,
          '&.Mui-focusVisible': { outline: `2px solid ${theme.palette.primary.main}`, outlineOffset: 3 } }),
        sizeSmall: { fontSize: '0.875rem' },
        sizeMedium: { fontSize: '0.875rem' },
        sizeLarge: { fontSize: '0.875rem' },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: ({ theme }) => ({ '&.Mui-focusVisible': { outline: `2px solid ${theme.palette.primary.main}`, outlineOffset: 2 } }),
      },
    },
    MuiTextField: { defaultProps: { size: 'small' } },
    MuiOutlinedInput: { styleOverrides: { root: { borderRadius: '10px', backgroundColor: '#ffffff' }, notchedOutline: { borderColor: '#6a8194' } } },
    MuiTab: { styleOverrides: { root: { textTransform: 'none' } } },
  },
});
