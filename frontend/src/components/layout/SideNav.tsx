import React from 'react';
import { Drawer, List, ListItemButton, ListItemIcon, ListItemText, Toolbar, Box, Typography, Divider } from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import InsightsIcon from '@mui/icons-material/Insights';
import SchoolIcon from '@mui/icons-material/School';
import BookIcon from '@mui/icons-material/Book';
import SecurityIcon from '@mui/icons-material/Security';
import SettingsIcon from '@mui/icons-material/Settings';
import { Link, useLocation } from 'react-router-dom';

const drawerWidth = 220;

export const SideNav: React.FC = () => {
  const location = useLocation();

  const items = [
    { label: 'Dashboard', to: '/dashboard', icon: <DashboardIcon /> },
    { label: 'Charts', to: '/charts', icon: <ShowChartIcon /> },
    { label: 'Analysis', to: '/analysis', icon: <InsightsIcon /> },
    { label: 'Risk', to: '/risk', icon: <SecurityIcon /> },
    { label: 'Education', to: '/education', icon: <SchoolIcon /> },
    { label: 'Journal', to: '/journal', icon: <BookIcon /> },
    { label: 'Coach/Therapy', to: '/coach', icon: <InsightsIcon /> },
    { label: 'War Room', to: '/war-room', icon: <InsightsIcon /> },
    { label: 'Community', to: '/community', icon: <ShowChartIcon /> },
    { label: 'Settings', to: '/settings', icon: <SettingsIcon /> },
  ];

  const isActive = (to: string) => location.pathname === to || (to === '/dashboard' && location.pathname === '/');

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        ['& .MuiDrawer-paper']: {
          width: drawerWidth,
          boxSizing: 'border-box',
          backgroundColor: (theme) => theme.palette.mode === 'dark' ? '#0F2243' : '#fff',
          color: (theme) => theme.palette.mode === 'dark' ? '#fff' : 'inherit',
        },
      }}
    >
      <Toolbar />
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, px: 2, py: 1.5 }}>
        <Box sx={{ width: 28, height: 28, borderRadius: 1, background: 'linear-gradient(135deg, #34D399 0%, #3B82F6 100%)' }} />
        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
          CamboAI
        </Typography>
      </Box>
      <Divider />
      <List>
        {items.map((item) => (
          <ListItemButton
            key={item.to}
            component={Link}
            to={item.to}
            selected={isActive(item.to)}
            sx={{
              '&.Mui-selected': {
                backgroundColor: 'rgba(59, 130, 246, 0.12)',
              },
            }}
          >
            <ListItemIcon sx={{ color: 'inherit' }}>{item.icon}</ListItemIcon>
            <ListItemText primary={item.label} />
          </ListItemButton>
        ))}
      </List>
    </Drawer>
  );
};

export default SideNav;
