import React, { useState } from 'react';
import {
  Box, Paper, Typography, Grid, Card, CardContent, Stack, 
  Table, TableHead, TableBody, TableRow, TableCell, Chip,
  LinearProgress, Alert, Divider, IconButton, Tooltip
} from '@mui/material';
import {
  Warning, Security, Speed, Timeline, TrendingUp, TrendingDown,
  Shield, AccountBalance, ShowChart, Error, CheckCircle, Info
} from '@mui/icons-material';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, LineChart, Line, Area, AreaChart } from 'recharts';

interface RiskMetric {
  name: string;
  current: number;
  limit: number;
  status: 'safe' | 'warning' | 'danger';
  unit: string;
  description: string;
}

interface Position {
  symbol: string;
  exposure: number;
  var95: number;
  var99: number;
  beta: number;
  correlation: number;
  concentration: number;
  sector: string;
}

const RiskDashboard: React.FC = () => {
  const [riskMetrics] = useState<RiskMetric[]>([
    {
      name: 'Portfolio VaR (95%)',
      current: 45230,
      limit: 75000,
      status: 'safe',
      unit: '$',
      description: '1-day Value at Risk with 95% confidence'
    },
    {
      name: 'Portfolio VaR (99%)',
      current: 67890,
      limit: 100000,
      status: 'warning',
      unit: '$',
      description: '1-day Value at Risk with 99% confidence'
    },
    {
      name: 'Maximum Drawdown',
      current: 8.5,
      limit: 15.0,
      status: 'safe',
      unit: '%',
      description: 'Maximum peak-to-trough decline'
    },
    {
      name: 'Leverage Ratio',
      current: 1.34,
      limit: 2.0,
      status: 'safe',
      unit: 'x',
      description: 'Total exposure / Net capital'
    },
    {
      name: 'Concentration Risk',
      current: 23.4,
      limit: 25.0,
      status: 'warning',
      unit: '%',
      description: 'Largest single position as % of portfolio'
    },
    {
      name: 'Sector Concentration',
      current: 67.8,
      limit: 60.0,
      status: 'danger',
      unit: '%',
      description: 'Technology sector exposure'
    }
  ]);

  const [positions] = useState<Position[]>([
    {
      symbol: 'AAPL',
      exposure: 346742,
      var95: 15234,
      var99: 23456,
      beta: 1.05,
      correlation: 0.78,
      concentration: 23.4,
      sector: 'Technology'
    },
    {
      symbol: 'MSFT',
      exposure: 217802,
      var95: 12890,
      var99: 19845,
      beta: 0.89,
      correlation: 0.82,
      concentration: 14.7,
      sector: 'Technology'
    },
    {
      symbol: 'GOOGL',
      exposure: 125568,
      var95: 8934,
      var99: 14567,
      beta: 1.15,
      correlation: 0.75,
      concentration: 8.5,
      sector: 'Technology'
    },
    {
      symbol: 'TSLA',
      exposure: 96265,
      var95: 18234,
      var99: 28901,
      beta: 2.01,
      correlation: 0.45,
      concentration: 6.5,
      sector: 'Consumer'
    }
  ]);

  const correlationMatrix = [
    { asset1: 'AAPL', asset2: 'MSFT', correlation: 0.82 },
    { asset1: 'AAPL', asset2: 'GOOGL', correlation: 0.75 },
    { asset1: 'AAPL', asset2: 'TSLA', correlation: 0.45 },
    { asset1: 'MSFT', asset2: 'GOOGL', correlation: 0.78 },
    { asset1: 'MSFT', asset2: 'TSLA', correlation: 0.38 },
    { asset1: 'GOOGL', asset2: 'TSLA', correlation: 0.42 }
  ];

  const stressTestScenarios = [
    {
      scenario: '2008 Financial Crisis',
      portfolioImpact: -42.3,
      probability: 'Low',
      description: 'Severe market downturn scenario'
    },
    {
      scenario: 'Tech Bubble Burst',
      portfolioImpact: -38.7,
      probability: 'Medium',
      description: 'Technology sector specific crash'
    },
    {
      scenario: 'Interest Rate Shock',
      portfolioImpact: -18.9,
      probability: 'Medium',
      description: 'Rapid interest rate increase'
    },
    {
      scenario: 'Flash Crash',
      portfolioImpact: -15.2,
      probability: 'Low',
      description: 'Sudden market liquidity crisis'
    }
  ];

  const varHistory = [
    { date: '2024-01-01', var95: 38000, var99: 52000 },
    { date: '2024-01-02', var95: 41000, var99: 58000 },
    { date: '2024-01-03', var95: 39000, var99: 55000 },
    { date: '2024-01-04', var95: 43000, var99: 61000 },
    { date: '2024-01-05', var95: 45230, var99: 67890 }
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'safe': return <CheckCircle sx={{ color: '#00C853', fontSize: 20 }} />;
      case 'warning': return <Warning sx={{ color: '#FFB300', fontSize: 20 }} />;
      case 'danger': return <Error sx={{ color: '#FF1744', fontSize: 20 }} />;
      default: return <Info sx={{ color: '#2196F3', fontSize: 20 }} />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'safe': return '#00C853';
      case 'warning': return '#FFB300';
      case 'danger': return '#FF1744';
      default: return '#2196F3';
    }
  };

  const formatCurrency = (amount: number) => `$${amount.toLocaleString()}`;
  
  const getCorrelationColor = (correlation: number) => {
    if (correlation > 0.8) return '#FF1744';
    if (correlation > 0.6) return '#FFB300';
    if (correlation > 0.4) return '#FFC107';
    return '#00C853';
  };

  return (
    <Box sx={{ width: '100%', p: 2 }}>
      {/* Risk Alerts */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12}>
          <Alert severity="warning" sx={{ mb: 2 }}>
            <strong>Risk Alert:</strong> Technology sector concentration exceeds limit (67.8% > 60.0%)
          </Alert>
        </Grid>
      </Grid>

      {/* Risk Metrics Overview */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {riskMetrics.map((metric, index) => (
          <Grid item xs={12} sm={6} md={4} key={index}>
            <Card sx={{ height: '100%', border: `2px solid ${getStatusColor(metric.status)}` }}>
              <CardContent>
                <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1 }}>
                  {getStatusIcon(metric.status)}
                  <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                    {metric.name}
                  </Typography>
                </Stack>
                
                <Typography variant="h4" sx={{ 
                  fontWeight: 'bold', 
                  color: getStatusColor(metric.status),
                  mb: 1 
                }}>
                  {metric.unit === '$' ? formatCurrency(metric.current) : 
                   `${metric.current.toFixed(metric.unit === '%' ? 1 : 2)}${metric.unit}`}
                </Typography>
                
                <Box sx={{ mb: 2 }}>
                  <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 0.5 }}>
                    <Typography variant="caption">Current</Typography>
                    <Typography variant="caption">
                      Limit: {metric.unit === '$' ? formatCurrency(metric.limit) : 
                              `${metric.limit}${metric.unit}`}
                    </Typography>
                  </Stack>
                  <LinearProgress
                    variant="determinate"
                    value={(metric.current / metric.limit) * 100}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: '#f0f0f0',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: getStatusColor(metric.status)
                      }
                    }}
                  />
                </Box>
                
                <Typography variant="caption" color="textSecondary">
                  {metric.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        {/* Position Risk Analysis */}
        <Grid item xs={12} lg={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
              <Security sx={{ mr: 1 }} />
              Position Risk Analysis
            </Typography>
            
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Symbol</TableCell>
                  <TableCell align="right">Exposure</TableCell>
                  <TableCell align="right">VaR 95%</TableCell>
                  <TableCell align="right">VaR 99%</TableCell>
                  <TableCell align="right">Beta</TableCell>
                  <TableCell align="right">Correlation</TableCell>
                  <TableCell align="right">% Portfolio</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {positions.map((position) => (
                  <TableRow key={position.symbol} hover>
                    <TableCell sx={{ fontWeight: 'bold' }}>
                      <Stack>
                        <Typography variant="body2">{position.symbol}</Typography>
                        <Chip 
                          label={position.sector} 
                          size="small" 
                          variant="outlined"
                          sx={{ fontSize: '0.6rem', height: 16 }}
                        />
                      </Stack>
                    </TableCell>
                    <TableCell align="right" sx={{ fontWeight: 'bold' }}>
                      {formatCurrency(position.exposure)}
                    </TableCell>
                    <TableCell align="right" sx={{ color: '#FFB300' }}>
                      {formatCurrency(position.var95)}
                    </TableCell>
                    <TableCell align="right" sx={{ color: '#FF1744' }}>
                      {formatCurrency(position.var99)}
                    </TableCell>
                    <TableCell align="right">
                      <Chip
                        label={position.beta.toFixed(2)}
                        size="small"
                        color={position.beta > 1.5 ? 'error' : position.beta > 1 ? 'warning' : 'success'}
                        sx={{ minWidth: 50 }}
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Chip
                        label={position.correlation.toFixed(2)}
                        size="small"
                        sx={{
                          backgroundColor: getCorrelationColor(position.correlation),
                          color: 'white',
                          minWidth: 50
                        }}
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        {position.concentration.toFixed(1)}%
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Paper>
        </Grid>

        {/* VaR History Chart */}
        <Grid item xs={12} lg={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
              <ShowChart sx={{ mr: 1 }} />
              VaR Trend
            </Typography>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={varHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" hide />
                <YAxis />
                <Line 
                  type="monotone" 
                  dataKey="var95" 
                  stroke="#FFB300" 
                  strokeWidth={2}
                  name="VaR 95%"
                />
                <Line 
                  type="monotone" 
                  dataKey="var99" 
                  stroke="#FF1744" 
                  strokeWidth={2}
                  name="VaR 99%"
                />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Stress Test Results */}
        <Grid item xs={12} lg={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
              <Timeline sx={{ mr: 1 }} />
              Stress Test Scenarios
            </Typography>
            
            <Stack spacing={2}>
              {stressTestScenarios.map((scenario, index) => (
                <Card key={index} variant="outlined">
                  <CardContent sx={{ p: 2 }}>
                    <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                        {scenario.scenario}
                      </Typography>
                      <Chip 
                        label={scenario.probability}
                        size="small"
                        color={scenario.probability === 'High' ? 'error' : 
                               scenario.probability === 'Medium' ? 'warning' : 'success'}
                      />
                    </Stack>
                    
                    <Typography variant="caption" color="textSecondary" display="block" sx={{ mb: 1 }}>
                      {scenario.description}
                    </Typography>
                    
                    <Stack direction="row" alignItems="center" spacing={1}>
                      <TrendingDown sx={{ color: '#FF1744', fontSize: 16 }} />
                      <Typography 
                        variant="h6" 
                        sx={{ 
                          color: '#FF1744', 
                          fontWeight: 'bold' 
                        }}
                      >
                        {scenario.portfolioImpact.toFixed(1)}%
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        Portfolio Impact
                      </Typography>
                    </Stack>
                  </CardContent>
                </Card>
              ))}
            </Stack>
          </Paper>
        </Grid>

        {/* Correlation Matrix */}
        <Grid item xs={12} lg={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
              <AccountBalance sx={{ mr: 1 }} />
              Asset Correlation Matrix
            </Typography>
            
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Asset 1</TableCell>
                  <TableCell>Asset 2</TableCell>
                  <TableCell align="right">Correlation</TableCell>
                  <TableCell align="center">Risk Level</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {correlationMatrix.map((corr, index) => (
                  <TableRow key={index}>
                    <TableCell sx={{ fontWeight: 'bold' }}>{corr.asset1}</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>{corr.asset2}</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 'bold' }}>
                      {corr.correlation.toFixed(2)}
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label={corr.correlation > 0.8 ? 'High' : 
                               corr.correlation > 0.6 ? 'Medium' : 
                               corr.correlation > 0.4 ? 'Low' : 'Very Low'}
                        size="small"
                        sx={{
                          backgroundColor: getCorrelationColor(corr.correlation),
                          color: 'white'
                        }}
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default RiskDashboard;