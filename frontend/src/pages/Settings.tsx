import React, { useEffect, useState } from 'react';
import { Box, Paper, Typography, FormControlLabel, Switch } from '@mui/material';

const Settings: React.FC = () => {
  const [defaultToApi, setDefaultToApi] = useState<boolean>(() => {
    return localStorage.getItem('journal.defaultToApi') === 'true';
  });

  useEffect(() => {
    localStorage.setItem('journal.defaultToApi', String(defaultToApi));
  }, [defaultToApi]);

  return (
    <Box p={2}>
      <Typography variant="h5" gutterBottom>Settings</Typography>
      <Paper sx={{ p: 2 }}>
        <Typography variant="subtitle1" gutterBottom>Journal</Typography>
        <FormControlLabel
          control={<Switch checked={defaultToApi} onChange={(e) => setDefaultToApi(e.target.checked)} />}
          label="Default Journal storage to API after login"
        />
        <Typography variant="body2" color="text.secondary">
          When enabled, after you sign in successfully the Journal will switch to API storage by default.
        </Typography>
      </Paper>
    </Box>
  );
};

export default Settings;
