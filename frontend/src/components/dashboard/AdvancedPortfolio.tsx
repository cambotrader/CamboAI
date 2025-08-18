import React, { useState, useEffect } from 'react';
import {
  Grid, Paper, Typography, Box, Card, CardContent, Tab, Tabs,
  Table, TableHead, TableBody, TableRow, TableCell, Chip, IconButton,
  LinearProgress, Stack, Divider, Avatar, Tooltip, Button
} from '@mui/material';
import {
  AccountBalance, TrendingUp, TrendingDown, DonutLarge, 
  Timeline, Assessment, Security, Speed, Warning,
  MoreVert, Edit, Delete, Add
} from '@mui/icons-material';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, LineChart, Line, Area, AreaChart } from 'recharts';

interface Position {
  id: string;
  symbol: string;
  name: string;
  quantity: number;
  avgCost: number;
  currentPrice: number;
  marketValue: number;
  dayChange: number;
  dayChangePercent: number;
  totalGainLoss: number;
  totalGainLossPercent: number;
  sector: string;
  beta: number;
  dividend: number;
  peRatio: number;
  marketCap: string;
}

interface PortfolioMetrics {
  totalValue: number;
  dayChange: number;
  dayChangePercent: number;
  totalGainLoss: number;
  totalGainLossPercent: number;
  cashBalance: number;
  buyingPower: number;
  marginUsed: number;
  annualizedReturn: number;
  sharpeRatio: number;
  maxDrawdown: number;
  beta: number;
  alpha: number;
}

const AdvancedPortfolio: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  
  const [portfolioMetrics] = useState<PortfolioMetrics>({
    totalValue: 1247832.45,
    dayChange: 15647.32,
    dayChangePercent: 1.27,
    totalGainLoss: 247832.45,
    totalGainLossPercent: 24.78,
    cashBalance: 125000.00,
    buyingPower: 250000.00,
    marginUsed: 75000.00,
    annualizedReturn: 18.4,
    sharpeRatio: 1.47,
    maxDrawdown: -12.3,
    beta: 1.12,
    alpha: 6.2
  });

  const [positions] = useState<Position[]>([
    {
      id: '1', symbol: 'AAPL', name: 'Apple Inc.', quantity: 500, avgCost: 175.23,
      currentPrice: 192.53, marketValue: 96265.00, dayChange: 1.70, dayChangePercent: 0.89,
      totalGainLoss: 8650.00, totalGainLossPercent: 9.86, sector: 'Technology',
      beta: 1.05, dividend: 0.96, peRatio: 28.4, marketCap: '2.98T'
    },
    {
      id: '2', symbol: 'MSFT', name: 'Microsoft Corporation', quantity: 300, avgCost: 385.67,
      currentPrice: 418.56, marketValue: 125568.00, dayChange: -5.67, dayChangePercent: -1.34,
      totalGainLoss: 9867.00, totalGainLossPercent: 8.53, sector: 'Technology',
      beta: 0.89, dividend: 3.00, peRatio: 32.1, marketCap: '3.10T'
    },
    {
      id: '3', symbol: 'GOOGL', name: 'Alphabet Inc.', quantity: 150, avgCost: 2456.78,
      currentPrice: 2734.23, marketValue: 410134.50, dayChange: 23.45, dayChangePercent: 0.87,
      totalGainLoss: 41617.50, totalGainLossPercent: 11.29, sector: 'Technology',
      beta: 1.15, dividend: 0.00, peRatio: 25.8, marketCap: '1.75T'
    },
    {
      id: '4', symbol: 'TSLA', name: 'Tesla Inc.', quantity: 200, avgCost: 945.32,
      currentPrice: 1089.01, marketValue: 217802.00, dayChange: 67.89, dayChangePercent: 6.65,
      totalGainLoss: 28738.00, totalGainLossPercent: 15.19, sector: 'Consumer Discretionary',
      beta: 2.01, dividend: 0.00, peRatio: 89.3, marketCap: '352B'
    },
    {
      id: '5', symbol: 'AMZN', name: 'Amazon.com Inc.', quantity: 100, avgCost: 3256.89,
      currentPrice: 3467.42, marketValue: 346742.00, dayChange: 89.23, dayChangePercent: 2.64,
      totalGainLoss: 21053.00, totalGainLossPercent: 6.46, sector: 'Consumer Discretionary',
      beta: 1.33, dividend: 0.00, peRatio: 54.2, marketCap: '1.78T'
    }
  ]);

  const sectorAllocation = [
    { name: 'Technology', value: 65.2, color: '#0088FE' },
    { name: 'Consumer Discretionary', value: 25.8, color: '#00C49F' },
    { name: 'Healthcare', value: 5.5, color: '#FFBB28' },
    { name: 'Financials', value: 2.3, color: '#FF8042' },
    { name: 'Cash', value: 1.2, color: '#8884d8' }
  ];

  const performanceData = [
    { date: '2024-01-01', value: 1000000 },
    { date: '2024-02-01', value: 1045000 },
    { date: '2024-03-01', value: 1123000 },
    { date: '2024-04-01', value: 1089000 },
    { date: '2024-05-01', value: 1156000 },
    { date: '2024-06-01', value: 1198000 },
    { date: '2024-07-01', value: 1234000 },
    { date: '2024-08-01', value: 1247832 }
  ];

  const riskMetrics = [
    { metric: 'VaR (1-day, 95%)', value: '-$23,456', color: '#FF5722' },
    { metric: 'VaR (1-day, 99%)', value: '-$45,234', color: '#D32F2F' },
    { metric: 'Expected Shortfall', value: '-$67,890', color: '#B71C1C' },
    { metric: 'Maximum Drawdown', value: '-12.3%', color: '#FF9800' }
  ];

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatPercent = (percent: number): string => {
    return `${percent >= 0 ? '+' : ''}${percent.toFixed(2)}%`;
  };

  return (
    <Box sx={{ width: '100%', p: 2 }}>
      {/* Portfolio Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
            <CardContent>
              <Stack direction="row" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="subtitle2" sx={{ opacity: 0.8 }}>Total Portfolio Value</Typography>
                  <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                    {formatCurrency(portfolioMetrics.totalValue)}
                  </Typography>
                  <Stack direction="row" alignItems="center" spacing={0.5} sx={{ mt: 1 }}>
                    <TrendingUp sx={{ fontSize: 16 }} />
                    <Typography variant="body2">
                      {formatCurrency(portfolioMetrics.dayChange)} ({formatPercent(portfolioMetrics.dayChangePercent)})
                    </Typography>
                  </Stack>
                </Box>
                <AccountBalance sx={{ fontSize: 40, opacity: 0.7 }} />
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
            <CardContent>
              <Stack direction="row" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="subtitle2" sx={{ opacity: 0.8 }}>Total Gain/Loss</Typography>
                  <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                    {formatCurrency(portfolioMetrics.totalGainLoss)}
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    {formatPercent(portfolioMetrics.totalGainLossPercent)} Total Return
                  </Typography>
                </Box>
                <Assessment sx={{ fontSize: 40, opacity: 0.7 }} />
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', color: 'white' }}>
            <CardContent>
              <Stack direction="row" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="subtitle2" sx={{ opacity: 0.8 }}>Cash & Buying Power</Typography>
                  <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                    {formatCurrency(portfolioMetrics.cashBalance)}
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    {formatCurrency(portfolioMetrics.buyingPower)} Available
                  </Typography>
                </Box>
                <Speed sx={{ fontSize: 40, opacity: 0.7 }} />
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', color: 'white' }}>
            <CardContent>
              <Stack direction="row" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="subtitle2" sx={{ opacity: 0.8 }}>Performance Metrics</Typography>
                  <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                    {portfolioMetrics.annualizedReturn}%
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Sharpe: {portfolioMetrics.sharpeRatio} | β: {portfolioMetrics.beta}
                  </Typography>
                </Box>
                <Timeline sx={{ fontSize: 40, opacity: 0.7 }} />
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Holdings" />
          <Tab label="Performance" />
          <Tab label="Asset Allocation" />
          <Tab label="Risk Analysis" />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && (
        <Paper sx={{ width: '100%' }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Symbol</TableCell>
                <TableCell align="right">Shares</TableCell>
                <TableCell align="right">Avg Cost</TableCell>
                <TableCell align="right">Current Price</TableCell>
                <TableCell align="right">Market Value</TableCell>
                <TableCell align="right">Day Change</TableCell>
                <TableCell align="right">Total G/L</TableCell>
                <TableCell align="right">Beta</TableCell>
                <TableCell align="right">Dividend</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {positions.map((position) => (
                <TableRow key={position.id} hover>
                  <TableCell>
                    <Stack direction="row" alignItems="center" spacing={2}>
                      <Avatar sx={{ width: 32, height: 32, fontSize: '0.875rem' }}>
                        {position.symbol[0]}
                      </Avatar>
                      <Box>
                        <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                          {position.symbol}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {position.name}
                        </Typography>
                      </Box>
                    </Stack>
                  </TableCell>
                  <TableCell align="right">{position.quantity.toLocaleString()}</TableCell>
                  <TableCell align="right">{formatCurrency(position.avgCost)}</TableCell>
                  <TableCell align="right">{formatCurrency(position.currentPrice)}</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 'bold' }}>
                    {formatCurrency(position.marketValue)}
                  </TableCell>
                  <TableCell align="right">
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                      {position.dayChangePercent > 0 ? (
                        <TrendingUp sx={{ fontSize: 16, color: '#00C853', mr: 0.5 }} />
                      ) : (
                        <TrendingDown sx={{ fontSize: 16, color: '#FF1744', mr: 0.5 }} />
                      )}
                      <Typography
                        variant="body2"
                        sx={{
                          color: position.dayChangePercent > 0 ? '#00C853' : '#FF1744',
                          fontWeight: 'bold'
                        }}
                      >
                        {formatPercent(position.dayChangePercent)}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell align="right">
                    <Box>
                      <Typography
                        variant="body2"
                        sx={{
                          color: position.totalGainLoss > 0 ? '#00C853' : '#FF1744',
                          fontWeight: 'bold'
                        }}
                      >
                        {formatCurrency(position.totalGainLoss)}
                      </Typography>
                      <Typography
                        variant="caption"
                        sx={{
                          color: position.totalGainLoss > 0 ? '#00C853' : '#FF1744'
                        }}
                      >
                        {formatPercent(position.totalGainLossPercent)}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell align="right">
                    <Chip
                      label={position.beta.toFixed(2)}
                      size="small"
                      color={position.beta > 1.5 ? 'error' : position.beta > 1 ? 'warning' : 'success'}
                    />
                  </TableCell>
                  <TableCell align="right">
                    {position.dividend > 0 ? (
                      <Typography variant="body2" sx={{ color: '#00C853' }}>
                        {position.dividend.toFixed(2)}%
                      </Typography>
                    ) : (
                      <Typography variant="body2" color="textSecondary">
                        N/A
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell align="center">
                    <IconButton size="small">
                      <MoreVert />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      )}

      {activeTab === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>Portfolio Performance</Typography>
              <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={performanceData}>
                  <defs>
                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#8884d8" stopOpacity={0.1}/>
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="date" />
                  <YAxis />
                  <CartesianGrid strokeDasharray="3 3" />
                  <RechartsTooltip formatter={(value: any) => [formatCurrency(value), 'Portfolio Value']} />
                  <Area type="monotone" dataKey="value" stroke="#8884d8" fillOpacity={1} fill="url(#colorValue)" />
                </AreaChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        </Grid>
      )}

      {activeTab === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>Sector Allocation</Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={sectorAllocation}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry) => `${entry.name}: ${entry.value}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {sectorAllocation.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                </PieChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>Top Holdings</Typography>
              <Stack spacing={2}>
                {positions.slice(0, 5).map((position, index) => (
                  <Box key={position.id}>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Typography variant="body2">{position.symbol}</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        {((position.marketValue / portfolioMetrics.totalValue) * 100).toFixed(1)}%
                      </Typography>
                    </Stack>
                    <LinearProgress
                      variant="determinate"
                      value={(position.marketValue / portfolioMetrics.totalValue) * 100}
                      sx={{ height: 6, borderRadius: 3, mt: 0.5 }}
                    />
                  </Box>
                ))}
              </Stack>
            </Paper>
          </Grid>
        </Grid>
      )}

      {activeTab === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>Risk Metrics</Typography>
              <Grid container spacing={2}>
                {riskMetrics.map((risk, index) => (
                  <Grid item xs={12} sm={6} key={index}>
                    <Card sx={{ border: `2px solid ${risk.color}` }}>
                      <CardContent>
                        <Typography variant="subtitle2" color="textSecondary">
                          {risk.metric}
                        </Typography>
                        <Typography variant="h5" sx={{ color: risk.color, fontWeight: 'bold' }}>
                          {risk.value}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>Risk Assessment</Typography>
              <Stack spacing={2}>
                <Box>
                  <Typography variant="body2">Portfolio Beta</Typography>
                  <Typography variant="h4" sx={{ color: portfolioMetrics.beta > 1.2 ? '#FF1744' : '#00C853' }}>
                    {portfolioMetrics.beta}
                  </Typography>
                </Box>
                <Divider />
                <Box>
                  <Typography variant="body2">Alpha</Typography>
                  <Typography variant="h4" sx={{ color: '#2196F3' }}>
                    {portfolioMetrics.alpha}%
                  </Typography>
                </Box>
                <Divider />
                <Box>
                  <Typography variant="body2">Sharpe Ratio</Typography>
                  <Typography variant="h4" sx={{ color: portfolioMetrics.sharpeRatio > 1 ? '#00C853' : '#FF9800' }}>
                    {portfolioMetrics.sharpeRatio}
                  </Typography>
                </Box>
              </Stack>
            </Paper>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default AdvancedPortfolio;