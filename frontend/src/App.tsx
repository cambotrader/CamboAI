import React, { useEffect, useMemo, useState } from 'react';
import { AppBar, Toolbar, Typography, Button, Box, Toolbar as MuiToolbar } from '@mui/material';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { getTheme, AppThemeMode } from './theme';
import Dashboard from './pages/Dashboard';
import Login from './components/Login';
import SideNav from './components/layout/SideNav';
import Charts from './pages/Charts';
import Analysis from './pages/Analysis';
import Risk from './pages/Risk';
import Education from './pages/Education';
import Journal from './pages/Journal';
import Settings from './pages/Settings';
import CoachTherapy from './pages/CoachTherapy';
import WarRoom from './pages/WarRoom';
import Community from './pages/Community';
import LessonView from './pages/LessonView';
import ThemeToggle, { ThemePreference } from './components/ThemeToggle';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Theme state
  const [pref, setPref] = useState<ThemePreference>(() => (localStorage.getItem('theme.pref') as ThemePreference) || 'system');
  const [mode, setMode] = useState<AppThemeMode>('light');

  useEffect(() => {
    const applySystem = () => {
      const mql = window.matchMedia('(prefers-color-scheme: dark)');
      setMode((pref === 'system' ? (mql.matches ? 'dark' : 'light') : (pref as AppThemeMode)));
    };
    applySystem();
    const listener = (e: MediaQueryListEvent) => {
      if (pref === 'system') setMode(e.matches ? 'dark' : 'light');
    };
    const mql = window.matchMedia('(prefers-color-scheme: dark)');
    mql.addEventListener('change', listener);
    return () => mql.removeEventListener('change', listener);
  }, [pref]);

  useEffect(() => {
    localStorage.setItem('theme.pref', pref);
  }, [pref]);

  const theme = useMemo(() => getTheme(mode), [mode]);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) { verifyToken(token); } else { setLoading(false); }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const verifyToken = async (token: string) => {
    try {
      const controller = new AbortController();
      const timeoutId = window.setTimeout(() => controller.abort(), 5000);
      const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
        headers: { 'Authorization': `Bearer ${token}` },
        signal: controller.signal
      });
      window.clearTimeout(timeoutId);

      if (response.ok) {
        setIsAuthenticated(true);
        const preferApi = localStorage.getItem('journal.defaultToApi') === 'true';
        if (preferApi) localStorage.setItem('journalStorageMode', 'api');
      } else {
        localStorage.removeItem('access_token');
        setIsAuthenticated(false);
      }
    } catch (error) {
      console.error('Token verification failed:', error);
      localStorage.removeItem('access_token');
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (_token: string) => {
    setIsAuthenticated(true);
    const preferApi = localStorage.getItem('journal.defaultToApi') === 'true';
    if (preferApi) localStorage.setItem('journalStorageMode', 'api');
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    setIsAuthenticated(false);
  };

  if (loading) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
          <Typography>Loading...</Typography>
        </Box>
      </ThemeProvider>
    );
  }

  const debugBypass =
    process.env.REACT_APP_DEBUG_MODE === 'true' ||
    window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1';
  if (!isAuthenticated && !debugBypass) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Login onLogin={handleLogin} />
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <AppBar position="fixed">
          <Toolbar>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flexGrow: 1 }}>
              <img src="/logo.png" alt="CamboAI" style={{ width: 28, height: 28 }} />
              <Typography variant="h6" component="div">Cambo AI</Typography>
            </Box>
            <Box sx={{ mr: 2, display: 'flex', alignItems: 'center', gap: 1.5 }}>
              {/* Live status widget for API + WebSocket */}
              {/* eslint-disable-next-line @typescript-eslint/no-var-requires */}
              {(() => {
                const StatusWidget = require('./components/StatusWidget').default;
                return <StatusWidget />;
              })()}
              <ThemeToggle value={pref} onChange={setPref} />
            </Box>
            <Button color="inherit" onClick={handleLogout}>Logout</Button>
          </Toolbar>
        </AppBar>
        <Box sx={{ display: 'flex' }}>
          <SideNav />
          <Box component="main" sx={{ flexGrow: 1, p: 2 }}>
            <MuiToolbar />
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/charts" element={<Charts />} />
              <Route path="/analysis" element={<Analysis />} />
              <Route path="/risk" element={<Risk />} />
              <Route path="/education" element={<Education />} />
              <Route path="/education/lesson/:lessonId" element={<LessonView />} />
              <Route path="/journal" element={<Journal />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/coach" element={<CoachTherapy />} />
              <Route path="/war-room" element={<WarRoom />} />
              <Route path="/community" element={<Community />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
