import React from 'react';
import { ToggleButton, ToggleButtonGroup, Tooltip } from '@mui/material';
import LightModeIcon from '@mui/icons-material/LightMode';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import ComputerIcon from '@mui/icons-material/Computer';

export type ThemePreference = 'light' | 'dark' | 'system';

interface ThemeToggleProps {
  value: ThemePreference;
  onChange: (value: ThemePreference) => void;
}

const ThemeToggle: React.FC<ThemeToggleProps> = ({ value, onChange }) => {
  const handleChange = (_: React.MouseEvent<HTMLElement>, newValue: ThemePreference | null) => {
    if (newValue) onChange(newValue);
  };

  return (
    <ToggleButtonGroup
      color="standard"
      value={value}
      exclusive
      size="small"
      onChange={handleChange}
      aria-label="Theme selection"
    >
      <ToggleButton value="light" aria-label="Light mode">
        <Tooltip title="Light"><LightModeIcon fontSize="small" /></Tooltip>
      </ToggleButton>
      <ToggleButton value="dark" aria-label="Dark mode">
        <Tooltip title="Dark"><DarkModeIcon fontSize="small" /></Tooltip>
      </ToggleButton>
      <ToggleButton value="system" aria-label="System mode">
        <Tooltip title="System"><ComputerIcon fontSize="small" /></Tooltip>
      </ToggleButton>
    </ToggleButtonGroup>
  );
};

export default ThemeToggle;
