import React, { useState } from 'react';
import { Typography, Box, Paper, Button, TextField } from '@mui/material';
import { apiService } from '../services/api';

const Analysis: React.FC = () => {
  const [series, setSeries] = useState<string>('100,101,102,101,103,104,103,105,106,107,106');
  const [result, setResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  const runAnalysis = async () => {
    try {
      setError(null);
      const close = series
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean)
        .map((v) => Number(v));
      const data = await apiService.post('/api/analysis/technical', { close });
      setResult(data);
    } catch (e: any) {
      setError(e?.message || 'Failed to run analysis');
    }
  };

  return (
    <Box p={2}>
      <Typography variant="h5" gutterBottom>Analysis</Typography>
      <Paper sx={{ p: 2, mb: 2, display: 'flex', gap: 2, alignItems: 'center' }}>
        <TextField label="Close series (comma-separated)" fullWidth value={series} onChange={(e) => setSeries(e.target.value)} />
        <Button variant="contained" onClick={runAnalysis}>Run</Button>
      </Paper>
      {error && <Typography color="error" sx={{ mb: 2 }}>{error}</Typography>}
      {result && (
        <Paper sx={{ p: 2 }}>
          <Typography variant="subtitle1">Results</Typography>
          <Box component="pre" sx={{ m: 0, whiteSpace: 'pre-wrap' }}>{JSON.stringify(result, null, 2)}</Box>
        </Paper>
      )}
    </Box>
  );
};

export default Analysis;
