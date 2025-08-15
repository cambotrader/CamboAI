import React, { useState } from 'react';
import { Typography, Box, Paper, TextField, ToggleButton, ToggleButtonGroup } from '@mui/material';
import ChartContainer from '../components/ChartContainer';

const Charts: React.FC = () => {
  const [symbol, setSymbol] = useState('AAPL');
  const [interval, setInterval] = useState('D');
  const [indicators, setIndicators] = useState({ sma: true, ema: true, rsi: true, macd: true });

  return (
    <Box p={2}>
      <Typography variant="h5" gutterBottom>Charts</Typography>
      <Paper sx={{ p: 2, mb: 2, display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
        <TextField label="Symbol" size="small" value={symbol} onChange={(e) => setSymbol(e.target.value.toUpperCase())} />
        <ToggleButtonGroup size="small" value={interval} exclusive onChange={(_, v) => v && setInterval(v)}>
          <ToggleButton value="1">1m</ToggleButton>
          <ToggleButton value="5">5m</ToggleButton>
          <ToggleButton value="60">1h</ToggleButton>
          <ToggleButton value="D">1D</ToggleButton>
          <ToggleButton value="W">1W</ToggleButton>
        </ToggleButtonGroup>
        <ToggleButtonGroup size="small" value={Object.entries(indicators).filter(([_, val]) => val).map(([k]) => k)} onChange={(_, vals) => {
          setIndicators({
            sma: vals.includes('sma'),
            ema: vals.includes('ema'),
            rsi: vals.includes('rsi'),
            macd: vals.includes('macd'),
          });
        }}>
          <ToggleButton value="sma">SMA</ToggleButton>
          <ToggleButton value="ema">EMA</ToggleButton>
          <ToggleButton value="rsi">RSI</ToggleButton>
          <ToggleButton value="macd">MACD</ToggleButton>
        </ToggleButtonGroup>
      </Paper>
      <ChartContainer chartType="tradingview" symbol={symbol} interval={interval} theme="dark" indicators={indicators} />
    </Box>
  );
};

export default Charts;
