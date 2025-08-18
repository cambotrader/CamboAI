import React, { useState, useEffect } from 'react';
import {
  Paper, Typography, Box, Grid, Table, TableHead, TableBody, TableRow, 
  TableCell, Chip, TextField, Select, MenuItem, FormControl, InputLabel,
  Stack, IconButton, Tooltip, LinearProgress, Card, CardContent
} from '@mui/material';
import { 
  CallMade, CallReceived, ShowChart, Timeline, 
  Info, TrendingUp, TrendingDown 
} from '@mui/icons-material';

interface OptionData {
  strike: number;
  call: {
    bid: number;
    ask: number;
    last: number;
    volume: number;
    openInterest: number;
    iv: number;
    delta: number;
    gamma: number;
    theta: number;
    vega: number;
    intrinsic: number;
  };
  put: {
    bid: number;
    ask: number;
    last: number;
    volume: number;
    openInterest: number;
    iv: number;
    delta: number;
    gamma: number;
    theta: number;
    vega: number;
    intrinsic: number;
  };
}

const OptionsChain: React.FC = () => {
  const [symbol, setSymbol] = useState('AAPL');
  const [expiration, setExpiration] = useState('2024-01-19');
  const [underlyingPrice] = useState(192.53);
  const [maxPain] = useState(190);
  
  const [optionsData, setOptionsData] = useState<OptionData[]>([
    {
      strike: 180,
      call: { bid: 13.20, ask: 13.40, last: 13.30, volume: 1250, openInterest: 5400, 
              iv: 0.285, delta: 0.85, gamma: 0.012, theta: -0.045, vega: 0.089, intrinsic: 12.53 },
      put: { bid: 0.15, ask: 0.20, last: 0.18, volume: 890, openInterest: 2100, 
             iv: 0.310, delta: -0.15, gamma: 0.012, theta: -0.025, vega: 0.089, intrinsic: 0 }
    },
    {
      strike: 185,
      call: { bid: 8.60, ask: 8.80, last: 8.70, volume: 2340, openInterest: 8900, 
              iv: 0.275, delta: 0.72, gamma: 0.018, theta: -0.052, vega: 0.125, intrinsic: 7.53 },
      put: { bid: 0.45, ask: 0.55, last: 0.50, volume: 1560, openInterest: 4200, 
             iv: 0.290, delta: -0.28, gamma: 0.018, theta: -0.032, vega: 0.125, intrinsic: 0 }
    },
    {
      strike: 190,
      call: { bid: 4.20, ask: 4.40, last: 4.30, volume: 5670, openInterest: 15200, 
              iv: 0.260, delta: 0.58, gamma: 0.025, theta: -0.058, vega: 0.156, intrinsic: 2.53 },
      put: { bid: 1.85, ask: 2.05, last: 1.95, volume: 4230, openInterest: 12800, 
             iv: 0.275, delta: -0.42, gamma: 0.025, theta: -0.038, vega: 0.156, intrinsic: 0 }
    },
    {
      strike: 195,
      call: { bid: 1.20, ask: 1.40, last: 1.30, volume: 8900, openInterest: 22400, 
              iv: 0.245, delta: 0.35, gamma: 0.028, theta: -0.062, vega: 0.178, intrinsic: 0 },
      put: { bid: 3.95, ask: 4.15, last: 4.05, volume: 6780, openInterest: 18900, 
             iv: 0.255, delta: -0.65, gamma: 0.028, theta: -0.042, vega: 0.178, intrinsic: 2.47 }
    },
    {
      strike: 200,
      call: { bid: 0.25, ask: 0.35, last: 0.30, volume: 12340, openInterest: 28900, 
              iv: 0.235, delta: 0.18, gamma: 0.022, theta: -0.055, vega: 0.145, intrinsic: 0 },
      put: { bid: 7.80, ask: 8.00, last: 7.90, volume: 3450, openInterest: 11200, 
             iv: 0.245, delta: -0.82, gamma: 0.022, theta: -0.035, vega: 0.145, intrinsic: 7.47 }
    }
  ]);

  const getVolumeColor = (volume: number): string => {
    if (volume > 5000) return '#00C853';
    if (volume > 2000) return '#FFB300';
    return '#666';
  };

  const getIVColor = (iv: number): string => {
    if (iv > 0.30) return '#FF5722';
    if (iv > 0.25) return '#FFB300';
    return '#00C853';
  };

  return (
    <Box sx={{ width: '100%', p: 2 }}>
      {/* Header Controls */}
      <Grid container spacing={2} sx={{ mb: 3 }} alignItems="center">
        <Grid item xs={12} md={3}>
          <TextField
            label="Symbol"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            size="small"
            fullWidth
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <FormControl fullWidth size="small">
            <InputLabel>Expiration</InputLabel>
            <Select value={expiration} onChange={(e) => setExpiration(e.target.value)}>
              <MenuItem value="2024-01-19">Jan 19, 2024 (7 days)</MenuItem>
              <MenuItem value="2024-01-26">Jan 26, 2024 (14 days)</MenuItem>
              <MenuItem value="2024-02-16">Feb 16, 2024 (monthly)</MenuItem>
              <MenuItem value="2024-03-15">Mar 15, 2024 (quarterly)</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={6}>
          <Stack direction="row" spacing={2} alignItems="center">
            <Chip 
              label={`${symbol} $${underlyingPrice.toFixed(2)}`} 
              color="primary" 
              variant="outlined"
              sx={{ fontWeight: 'bold' }}
            />
            <Chip 
              label={`Max Pain: $${maxPain}`} 
              color="warning" 
              variant="outlined"
            />
            <Chip 
              label="IV Rank: 45%" 
              color="info" 
              variant="outlined"
            />
          </Stack>
        </Grid>
      </Grid>

      {/* Summary Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #00C853, #4CAF50)' }}>
            <CardContent sx={{ color: 'white', textAlign: 'center', p: 2 }}>
              <CallMade sx={{ fontSize: 32, mb: 1 }} />
              <Typography variant="h6">Total Call Volume</Typography>
              <Typography variant="h4">30,550</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #FF5722, #F44336)' }}>
            <CardContent sx={{ color: 'white', textAlign: 'center', p: 2 }}>
              <CallReceived sx={{ fontSize: 32, mb: 1 }} />
              <Typography variant="h6">Total Put Volume</Typography>
              <Typography variant="h4">17,910</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #2196F3, #1976D2)' }}>
            <CardContent sx={{ color: 'white', textAlign: 'center', p: 2 }}>
              <ShowChart sx={{ fontSize: 32, mb: 1 }} />
              <Typography variant="h6">Put/Call Ratio</Typography>
              <Typography variant="h4">0.59</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #9C27B0, #7B1FA2)' }}>
            <CardContent sx={{ color: 'white', textAlign: 'center', p: 2 }}>
              <Timeline sx={{ fontSize: 32, mb: 1 }} />
              <Typography variant="h6">Avg IV</Typography>
              <Typography variant="h4">26.3%</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Options Chain Table */}
      <Paper sx={{ width: '100%', overflow: 'hidden' }}>
        <Typography variant="h6" sx={{ p: 2, borderBottom: '1px solid #ddd' }}>
          Options Chain - {symbol} ${underlyingPrice.toFixed(2)}
        </Typography>
        
        <Box sx={{ overflow: 'auto', maxHeight: '600px' }}>
          <Table stickyHeader size="small">
            <TableHead>
              <TableRow>
                {/* Calls */}
                <TableCell align="center" colSpan={6} sx={{ backgroundColor: '#e8f5e8', fontWeight: 'bold' }}>
                  CALLS
                </TableCell>
                <TableCell align="center" sx={{ backgroundColor: '#f5f5f5', fontWeight: 'bold' }}>
                  STRIKE
                </TableCell>
                {/* Puts */}
                <TableCell align="center" colSpan={6} sx={{ backgroundColor: '#ffe8e8', fontWeight: 'bold' }}>
                  PUTS
                </TableCell>
              </TableRow>
              <TableRow>
                {/* Call headers */}
                <TableCell sx={{ minWidth: 60 }}>Bid</TableCell>
                <TableCell sx={{ minWidth: 60 }}>Ask</TableCell>
                <TableCell sx={{ minWidth: 60 }}>Last</TableCell>
                <TableCell sx={{ minWidth: 80 }}>Volume</TableCell>
                <TableCell sx={{ minWidth: 60 }}>IV</TableCell>
                <TableCell sx={{ minWidth: 80 }}>Greeks</TableCell>
                
                {/* Strike */}
                <TableCell align="center" sx={{ minWidth: 80, fontWeight: 'bold' }}>Price</TableCell>
                
                {/* Put headers */}
                <TableCell sx={{ minWidth: 80 }}>Greeks</TableCell>
                <TableCell sx={{ minWidth: 60 }}>IV</TableCell>
                <TableCell sx={{ minWidth: 80 }}>Volume</TableCell>
                <TableCell sx={{ minWidth: 60 }}>Last</TableCell>
                <TableCell sx={{ minWidth: 60 }}>Ask</TableCell>
                <TableCell sx={{ minWidth: 60 }}>Bid</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {optionsData.map((option) => (
                <TableRow 
                  key={option.strike}
                  sx={{
                    backgroundColor: option.strike === Math.round(underlyingPrice / 5) * 5 ? '#fff3e0' : 'inherit'
                  }}
                >
                  {/* Call Data */}
                  <TableCell sx={{ color: '#00C853', fontWeight: 'bold' }}>
                    {option.call.bid.toFixed(2)}
                  </TableCell>
                  <TableCell sx={{ color: '#00C853', fontWeight: 'bold' }}>
                    {option.call.ask.toFixed(2)}
                  </TableCell>
                  <TableCell sx={{ color: '#00C853', fontWeight: 'bold' }}>
                    {option.call.last.toFixed(2)}
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Typography 
                        variant="body2" 
                        sx={{ color: getVolumeColor(option.call.volume), fontWeight: 'bold' }}
                      >
                        {option.call.volume.toLocaleString()}
                      </Typography>
                      {option.call.volume > 5000 && (
                        <TrendingUp sx={{ fontSize: 14, color: '#00C853', ml: 0.5 }} />
                      )}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={`${(option.call.iv * 100).toFixed(1)}%`}
                      size="small"
                      sx={{
                        backgroundColor: getIVColor(option.call.iv),
                        color: 'white',
                        fontSize: '0.7rem'
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <Tooltip title={`Delta: ${option.call.delta.toFixed(3)}, Gamma: ${option.call.gamma.toFixed(3)}, Theta: ${option.call.theta.toFixed(3)}, Vega: ${option.call.vega.toFixed(3)}`}>
                      <Box sx={{ fontSize: '0.7rem' }}>
                        Δ{option.call.delta.toFixed(2)}
                      </Box>
                    </Tooltip>
                  </TableCell>

                  {/* Strike Price */}
                  <TableCell align="center" sx={{ 
                    fontWeight: 'bold', 
                    fontSize: '1rem',
                    backgroundColor: option.strike === Math.round(underlyingPrice / 5) * 5 ? '#ffecb3' : '#f5f5f5'
                  }}>
                    {option.strike}
                  </TableCell>

                  {/* Put Data */}
                  <TableCell>
                    <Tooltip title={`Delta: ${option.put.delta.toFixed(3)}, Gamma: ${option.put.gamma.toFixed(3)}, Theta: ${option.put.theta.toFixed(3)}, Vega: ${option.put.vega.toFixed(3)}`}>
                      <Box sx={{ fontSize: '0.7rem' }}>
                        Δ{option.put.delta.toFixed(2)}
                      </Box>
                    </Tooltip>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={`${(option.put.iv * 100).toFixed(1)}%`}
                      size="small"
                      sx={{
                        backgroundColor: getIVColor(option.put.iv),
                        color: 'white',
                        fontSize: '0.7rem'
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Typography 
                        variant="body2" 
                        sx={{ color: getVolumeColor(option.put.volume), fontWeight: 'bold' }}
                      >
                        {option.put.volume.toLocaleString()}
                      </Typography>
                      {option.put.volume > 5000 && (
                        <TrendingUp sx={{ fontSize: 14, color: '#00C853', ml: 0.5 }} />
                      )}
                    </Box>
                  </TableCell>
                  <TableCell sx={{ color: '#FF5722', fontWeight: 'bold' }}>
                    {option.put.last.toFixed(2)}
                  </TableCell>
                  <TableCell sx={{ color: '#FF5722', fontWeight: 'bold' }}>
                    {option.put.ask.toFixed(2)}
                  </TableCell>
                  <TableCell sx={{ color: '#FF5722', fontWeight: 'bold' }}>
                    {option.put.bid.toFixed(2)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Box>
      </Paper>
    </Box>
  );
};

export default OptionsChain;