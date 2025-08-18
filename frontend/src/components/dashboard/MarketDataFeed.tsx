import React, { useState, useEffect } from 'react';
import {
  Box, Paper, Typography, Grid, Card, CardContent, Stack, 
  Table, TableHead, TableBody, TableRow, TableCell, Chip,
  LinearProgress, IconButton, Tooltip, Divider
} from '@mui/material';
import {
  TrendingUp, TrendingDown, Speed, Timeline, Visibility,
  VolumeUp, AccountBalance, ShowChart, FlashOn, Radio
} from '@mui/icons-material';

interface LiveQuote {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  avgVolume: number;
  bid: number;
  ask: number;
  bidSize: number;
  askSize: number;
  high52: number;
  low52: number;
  marketCap: string;
  pe: number;
  lastTrade: string;
  exchange: string;
}

interface MarketBreadth {
  advancing: number;
  declining: number;
  unchanged: number;
  newHighs: number;
  newLows: number;
  upVolume: number;
  downVolume: number;
  totalVolume: number;
}

const MarketDataFeed: React.FC = () => {
  const [isLive, setIsLive] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  
  const [topWatchlist] = useState<LiveQuote[]>([
    {
      symbol: 'SPY', price: 461.23, change: 2.45, changePercent: 0.53,
      volume: 45678900, avgVolume: 78900000, bid: 461.21, ask: 461.25,
      bidSize: 800, askSize: 1200, high52: 478.50, low52: 348.10,
      marketCap: '420.5B', pe: 19.2, lastTrade: '16:00:01', exchange: 'NYSE'
    },
    {
      symbol: 'QQQ', price: 396.78, change: -1.23, changePercent: -0.31,
      volume: 32145600, avgVolume: 45600000, bid: 396.75, ask: 396.80,
      bidSize: 1500, askSize: 900, high52: 408.71, low52: 269.28,
      marketCap: '198.4B', pe: 25.6, lastTrade: '16:00:01', exchange: 'NASDAQ'
    },
    {
      symbol: 'IWM', price: 223.45, change: 1.89, changePercent: 0.85,
      volume: 28934500, avgVolume: 35400000, bid: 223.43, ask: 223.47,
      bidSize: 600, askSize: 750, high52: 244.90, low52: 158.71,
      marketCap: '34.2B', pe: 22.1, lastTrade: '16:00:01', exchange: 'NYSE'
    },
    {
      symbol: 'GLD', price: 198.67, change: 0.34, changePercent: 0.17,
      volume: 4567800, avgVolume: 8900000, bid: 198.65, ask: 198.69,
      bidSize: 450, askSize: 520, high52: 205.45, low52: 162.32,
      marketCap: '73.1B', pe: 0, lastTrade: '16:00:01', exchange: 'NYSE'
    },
    {
      symbol: 'VIX', price: 18.45, change: -0.78, changePercent: -4.06,
      volume: 0, avgVolume: 0, bid: 18.20, ask: 18.70,
      bidSize: 0, askSize: 0, high52: 65.54, low52: 12.01,
      marketCap: 'N/A', pe: 0, lastTrade: '16:00:01', exchange: 'CBOE'
    }
  ]);

  const [marketBreadth] = useState<MarketBreadth>({
    advancing: 1847,
    declining: 1203,
    unchanged: 156,
    newHighs: 234,
    newLows: 67,
    upVolume: 2.4e9,
    downVolume: 1.6e9,
    totalVolume: 4.0e9
  });

  const [economicIndicators] = useState([
    { name: 'Fed Funds Rate', value: '5.25%', change: '↑', status: 'neutral' },
    { name: '10Y Treasury', value: '4.68%', change: '↑ 0.03', status: 'up' },
    { name: 'USD Index', value: '103.45', change: '↓ 0.12', status: 'down' },
    { name: 'Oil (WTI)', value: '$87.23', change: '↑ 1.45', status: 'up' },
    { name: 'Gold', value: '$2,034', change: '↑ 12.30', status: 'up' },
    { name: 'Bitcoin', value: '$67,845', change: '↑ 892', status: 'up' }
  ]);

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setLastUpdate(new Date());
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const formatNumber = (num: number): string => {
    if (num >= 1e9) return `${(num / 1e9).toFixed(1)}B`;
    if (num >= 1e6) return `${(num / 1e6).toFixed(1)}M`;
    if (num >= 1e3) return `${(num / 1e3).toFixed(1)}K`;
    return num.toString();
  };

  const formatCurrency = (num: number) => `$${num.toFixed(2)}`;

  const getVolumeIndicator = (volume: number, avgVolume: number) => {
    const ratio = volume / avgVolume;
    if (ratio > 1.5) return { color: '#FF5722', label: 'High' };
    if (ratio > 1.2) return { color: '#FFB300', label: 'Above Avg' };
    if (ratio < 0.5) return { color: '#9E9E9E', label: 'Low' };
    return { color: '#4CAF50', label: 'Normal' };
  };

  return (
    <Box sx={{ width: '100%', p: 2 }}>
      {/* Live Data Header */}
      <Paper sx={{ p: 2, mb: 3, background: 'linear-gradient(135deg, #1a237e 0%, #283593 100%)', color: 'white' }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Stack direction="row" alignItems="center" spacing={2}>
            <Radio sx={{ color: isLive ? '#00E676' : '#FF5722' }} />
            <Typography variant="h6">
              Live Market Data Feed
            </Typography>
            <Chip 
              label={isLive ? 'LIVE' : 'DELAYED'} 
              size="small"
              sx={{ 
                backgroundColor: isLive ? '#00E676' : '#FF5722',
                color: 'black',
                fontWeight: 'bold'
              }}
            />
          </Stack>
          <Stack direction="row" alignItems="center" spacing={1}>
            <FlashOn sx={{ fontSize: 16 }} />
            <Typography variant="caption">
              Last Update: {lastUpdate.toLocaleTimeString()}
            </Typography>
          </Stack>
        </Stack>
      </Paper>

      <Grid container spacing={3}>
        {/* Market Breadth */}
        <Grid item xs={12} lg={4}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
              <AccountBalance sx={{ mr: 1 }} />
              Market Breadth
            </Typography>
            
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={6}>
                <Card sx={{ textAlign: 'center', background: '#e8f5e8' }}>
                  <CardContent sx={{ p: 1.5 }}>
                    <Typography variant="h4" sx={{ color: '#00C853', fontWeight: 'bold' }}>
                      {marketBreadth.advancing}
                    </Typography>
                    <Typography variant="caption">Advancing</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6}>
                <Card sx={{ textAlign: 'center', background: '#ffebee' }}>
                  <CardContent sx={{ p: 1.5 }}>
                    <Typography variant="h4" sx={{ color: '#FF1744', fontWeight: 'bold' }}>
                      {marketBreadth.declining}
                    </Typography>
                    <Typography variant="caption">Declining</Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            <Stack spacing={1.5}>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2">Advance/Decline Ratio</Typography>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                  {(marketBreadth.advancing / marketBreadth.declining).toFixed(2)}
                </Typography>
              </Stack>
              <LinearProgress
                variant="determinate"
                value={(marketBreadth.advancing / (marketBreadth.advancing + marketBreadth.declining)) * 100}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  backgroundColor: '#ffcdd2',
                  '& .MuiLinearProgress-bar': { backgroundColor: '#00C853' }
                }}
              />
              
              <Divider />
              
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2">New Highs</Typography>
                <Typography variant="body2" sx={{ color: '#00C853', fontWeight: 'bold' }}>
                  {marketBreadth.newHighs}
                </Typography>
              </Stack>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2">New Lows</Typography>
                <Typography variant="body2" sx={{ color: '#FF1744', fontWeight: 'bold' }}>
                  {marketBreadth.newLows}
                </Typography>
              </Stack>
              
              <Divider />
              
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2">Up Volume</Typography>
                <Typography variant="body2" sx={{ color: '#00C853', fontWeight: 'bold' }}>
                  {formatNumber(marketBreadth.upVolume)}
                </Typography>
              </Stack>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2">Down Volume</Typography>
                <Typography variant="body2" sx={{ color: '#FF1744', fontWeight: 'bold' }}>
                  {formatNumber(marketBreadth.downVolume)}
                </Typography>
              </Stack>
            </Stack>
          </Paper>
        </Grid>

        {/* Live Quotes */}
        <Grid item xs={12} lg={5}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
              <Speed sx={{ mr: 1 }} />
              Level II Quotes
            </Typography>
            
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Symbol</TableCell>
                  <TableCell align="right">Last</TableCell>
                  <TableCell align="right">Bid×Size</TableCell>
                  <TableCell align="right">Ask×Size</TableCell>
                  <TableCell align="right">Volume</TableCell>
                  <TableCell align="right">Change</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {topWatchlist.map((quote) => {
                  const volumeInfo = getVolumeIndicator(quote.volume, quote.avgVolume);
                  return (
                    <TableRow key={quote.symbol} hover>
                      <TableCell sx={{ fontWeight: 'bold' }}>
                        <Stack>
                          <Typography variant="body2">{quote.symbol}</Typography>
                          <Typography variant="caption" color="textSecondary">
                            {quote.exchange}
                          </Typography>
                        </Stack>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                          {formatCurrency(quote.price)}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {quote.lastTrade}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" sx={{ color: '#00C853' }}>
                          {formatCurrency(quote.bid)}×{formatNumber(quote.bidSize)}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" sx={{ color: '#FF1744' }}>
                          {formatCurrency(quote.ask)}×{formatNumber(quote.askSize)}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Stack alignItems="flex-end">
                          <Typography 
                            variant="body2" 
                            sx={{ color: volumeInfo.color, fontWeight: 'bold' }}
                          >
                            {formatNumber(quote.volume)}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            {volumeInfo.label}
                          </Typography>
                        </Stack>
                      </TableCell>
                      <TableCell align="right">
                        <Stack alignItems="flex-end">
                          <Typography 
                            variant="body2"
                            sx={{ 
                              color: quote.change > 0 ? '#00C853' : '#FF1744',
                              fontWeight: 'bold'
                            }}
                          >
                            {quote.change > 0 ? '+' : ''}{quote.change.toFixed(2)}
                          </Typography>
                          <Typography 
                            variant="caption"
                            sx={{ color: quote.change > 0 ? '#00C853' : '#FF1744' }}
                          >
                            {quote.changePercent > 0 ? '+' : ''}{quote.changePercent.toFixed(2)}%
                          </Typography>
                        </Stack>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </Paper>
        </Grid>

        {/* Economic Indicators */}
        <Grid item xs={12} lg={3}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
              <Timeline sx={{ mr: 1 }} />
              Economic Data
            </Typography>
            
            <Stack spacing={2}>
              {economicIndicators.map((indicator, index) => (
                <Card key={index} variant="outlined">
                  <CardContent sx={{ p: 1.5 }}>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Typography variant="body2" sx={{ fontSize: '0.8rem' }}>
                        {indicator.name}
                      </Typography>
                      {indicator.status === 'up' && <TrendingUp sx={{ fontSize: 16, color: '#00C853' }} />}
                      {indicator.status === 'down' && <TrendingDown sx={{ fontSize: 16, color: '#FF1744' }} />}
                    </Stack>
                    <Typography variant="h6" sx={{ fontWeight: 'bold', mt: 0.5 }}>
                      {indicator.value}
                    </Typography>
                    <Typography 
                      variant="caption" 
                      sx={{ 
                        color: indicator.status === 'up' ? '#00C853' : 
                               indicator.status === 'down' ? '#FF1744' : '#666'
                      }}
                    >
                      {indicator.change}
                    </Typography>
                  </CardContent>
                </Card>
              ))}
            </Stack>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default MarketDataFeed;