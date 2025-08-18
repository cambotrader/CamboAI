import React, { useState, useEffect } from 'react';
import {
  Grid, Card, CardContent, Typography, Box, Chip, LinearProgress,
  Table, TableBody, TableCell, TableHead, TableRow, Paper,
  IconButton, Tooltip, Avatar, Divider, Stack
} from '@mui/material';
import {
  TrendingUp, TrendingDown, ShowChart, Timeline,
  AccountBalance, CurrencyExchange, Insights, Speed
} from '@mui/icons-material';

interface MarketData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap?: number;
  pe?: number;
  sector?: string;
}

interface IndexData {
  name: string;
  value: number;
  change: number;
  changePercent: number;
}

const MarketOverview: React.FC = () => {
  const [indices, setIndices] = useState<IndexData[]>([
    { name: 'S&P 500', value: 4618.17, change: 23.45, changePercent: 0.51 },
    { name: 'NASDAQ', value: 15832.80, change: -12.34, changePercent: -0.08 },
    { name: 'DOW', value: 36100.31, change: 156.82, changePercent: 0.44 },
    { name: 'Russell 2000', value: 2234.56, change: 8.92, changePercent: 0.40 },
    { name: 'VIX', value: 18.45, change: -1.23, changePercent: -6.25 }
  ]);

  const [topMovers, setTopMovers] = useState<MarketData[]>([
    { symbol: 'TSLA', price: 1089.01, change: 67.89, changePercent: 6.65, volume: 28934567, sector: 'Technology' },
    { symbol: 'NVDA', price: 298.34, change: -12.45, changePercent: -4.00, volume: 45123890, sector: 'Technology' },
    { symbol: 'AMZN', price: 3467.42, change: 89.23, changePercent: 2.64, volume: 12456789, sector: 'Consumer' },
    { symbol: 'MSFT', price: 418.56, change: -5.67, changePercent: -1.34, volume: 18789456, sector: 'Technology' },
    { symbol: 'AAPL', price: 192.53, change: 3.21, changePercent: 1.70, volume: 34567890, sector: 'Technology' }
  ]);

  const [sectorPerformance, setSectorPerformance] = useState([
    { sector: 'Technology', performance: 2.34, color: '#00C853' },
    { sector: 'Healthcare', performance: 1.89, color: '#00C853' },
    { sector: 'Financials', performance: -0.45, color: '#FF1744' },
    { sector: 'Energy', performance: 3.67, color: '#00C853' },
    { sector: 'Consumer', performance: 0.89, color: '#00C853' },
    { sector: 'Materials', performance: -1.23, color: '#FF1744' }
  ]);

  const formatNumber = (num: number, decimals: number = 2): string => {
    if (num >= 1e9) return `${(num / 1e9).toFixed(1)}B`;
    if (num >= 1e6) return `${(num / 1e6).toFixed(1)}M`;
    if (num >= 1e3) return `${(num / 1e3).toFixed(1)}K`;
    return num.toFixed(decimals);
  };

  return (
    <Box sx={{ width: '100%', p: 2 }}>
      {/* Market Indices */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {indices.map((index) => (
          <Grid item xs={12} sm={6} md={2.4} key={index.name}>
            <Card sx={{ 
              background: 'linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%)',
              color: 'white',
              height: '100%'
            }}>
              <CardContent sx={{ p: 2 }}>
                <Typography variant="caption" sx={{ opacity: 0.8 }}>
                  {index.name}
                </Typography>
                <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                  {index.value.toLocaleString()}
                </Typography>
                <Stack direction="row" alignItems="center" spacing={1}>
                  {index.change > 0 ? (
                    <TrendingUp sx={{ fontSize: 16, color: '#00C853' }} />
                  ) : (
                    <TrendingDown sx={{ fontSize: 16, color: '#FF1744' }} />
                  )}
                  <Typography 
                    variant="caption" 
                    sx={{ 
                      color: index.change > 0 ? '#00C853' : '#FF1744',
                      fontWeight: 'bold'
                    }}
                  >
                    {index.change > 0 ? '+' : ''}{index.change.toFixed(2)} 
                    ({index.changePercent > 0 ? '+' : ''}{index.changePercent.toFixed(2)}%)
                  </Typography>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        {/* Top Movers */}
        <Grid item xs={12} lg={8}>
          <Paper sx={{ p: 2, height: '400px' }}>
            <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
              <ShowChart sx={{ mr: 1 }} />
              Market Movers
            </Typography>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell><strong>Symbol</strong></TableCell>
                  <TableCell align="right"><strong>Price</strong></TableCell>
                  <TableCell align="right"><strong>Change</strong></TableCell>
                  <TableCell align="right"><strong>%</strong></TableCell>
                  <TableCell align="right"><strong>Volume</strong></TableCell>
                  <TableCell><strong>Sector</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {topMovers.map((stock) => (
                  <TableRow key={stock.symbol} hover>
                    <TableCell>
                      <Stack direction="row" alignItems="center" spacing={1}>
                        <Avatar sx={{ width: 24, height: 24, fontSize: '0.75rem' }}>
                          {stock.symbol[0]}
                        </Avatar>
                        <strong>{stock.symbol}</strong>
                      </Stack>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" fontWeight="bold">
                        ${stock.price.toFixed(2)}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography 
                        variant="body2"
                        sx={{ 
                          color: stock.change > 0 ? '#00C853' : '#FF1744',
                          fontWeight: 'bold'
                        }}
                      >
                        {stock.change > 0 ? '+' : ''}${stock.change.toFixed(2)}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Chip
                        label={`${stock.changePercent > 0 ? '+' : ''}${stock.changePercent.toFixed(2)}%`}
                        size="small"
                        color={stock.changePercent > 0 ? 'success' : 'error'}
                        sx={{ fontWeight: 'bold', minWidth: 60 }}
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="caption">
                        {formatNumber(stock.volume)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={stock.sector} 
                        size="small" 
                        variant="outlined"
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Paper>
        </Grid>

        {/* Sector Performance */}
        <Grid item xs={12} lg={4}>
          <Paper sx={{ p: 2, height: '400px' }}>
            <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
              <Insights sx={{ mr: 1 }} />
              Sector Performance
            </Typography>
            <Stack spacing={2}>
              {sectorPerformance.map((sector) => (
                <Box key={sector.sector}>
                  <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 0.5 }}>
                    <Typography variant="body2">{sector.sector}</Typography>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        color: sector.performance > 0 ? '#00C853' : '#FF1744',
                        fontWeight: 'bold'
                      }}
                    >
                      {sector.performance > 0 ? '+' : ''}{sector.performance.toFixed(2)}%
                    </Typography>
                  </Stack>
                  <LinearProgress
                    variant="determinate"
                    value={Math.abs(sector.performance) * 10}
                    sx={{
                      height: 6,
                      borderRadius: 3,
                      backgroundColor: '#f0f0f0',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: sector.color,
                      }
                    }}
                  />
                </Box>
              ))}
            </Stack>

            <Divider sx={{ my: 2 }} />
            
            <Box>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>Market Statistics</Typography>
              <Stack spacing={1}>
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="caption">Advancing</Typography>
                  <Typography variant="caption" sx={{ color: '#00C853' }}>1,847</Typography>
                </Stack>
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="caption">Declining</Typography>
                  <Typography variant="caption" sx={{ color: '#FF1744' }}>1,203</Typography>
                </Stack>
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="caption">New Highs</Typography>
                  <Typography variant="caption">234</Typography>
                </Stack>
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="caption">New Lows</Typography>
                  <Typography variant="caption">67</Typography>
                </Stack>
              </Stack>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default MarketOverview;