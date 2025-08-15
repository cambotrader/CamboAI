import { createTheme, ThemeOptions } from '@mui/material/styles';

export type AppThemeMode = 'light' | 'dark';

const brand = {
  navy: '#0F2243',
  teal: '#34D399',
  blue: '#3B82F6',
  white: '#FFFFFF',
};

const getDesignTokens = (mode: AppThemeMode): ThemeOptions => ({
  palette: {
    mode,
    primary: { main: brand.blue },
    secondary: { main: brand.teal },
    ...(mode === 'light'
      ? {
          background: { default: '#FFFFFF', paper: '#FFFFFF' },
          text: { primary: brand.navy, secondary: '#334155' },
        }
      : {
          background: { default: brand.navy, paper: brand.navy },
          text: { primary: brand.white, secondary: '#CBD5E1' },
        }),
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
  components: {
    MuiAppBar: {
      defaultProps: { color: 'primary' },
      styleOverrides: {
        colorPrimary: {
          backgroundImage:
            'linear-gradient(135deg, #34D399 0%, #3B82F6 100%)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: { textTransform: 'none', borderRadius: 8 },
      },
    },
  },
});

export const getTheme = (mode: AppThemeMode) => createTheme(getDesignTokens(mode));
