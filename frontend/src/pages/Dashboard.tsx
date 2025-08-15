import React, { useState, useEffect } from 'react';
import { Grid, Paper, Typography, Box, Alert, Slider, TextField, Stack } from '@mui/material';
import ChartContainer from '../components/ChartContainer';
import ChartSelector, { ChartType } from '../components/ChartSelector';
import PerformanceChart from '../components/dashboard/PerformanceChart';
import PositionsTable from '../components/dashboard/PositionsTable';
import { apiService, wsService, PortfolioPosition, PerformanceData, PortfolioSummary } from '../services/api';

const Dashboard: React.FC = () => {
  const [chartType, setChartType] = useState<ChartType>('tradingview');
  const [symbol, setSymbol] = useState('AAPL');
  const [performanceData, setPerformanceData] = useState<any[]>([]);
  const [positions, setPositions] = useState<PortfolioPosition[]>([]);
  const [portfolioSummary, setPortfolioSummary] = useState<PortfolioSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [chartHeight, setChartHeight] = useState<number>(() => {
    const saved = localStorage.getItem('dashboard.chartHeight');
    return saved ? Math.max(300, Math.min(1200, Number(saved))) : 520;
  });

  useEffect(() => {
    // Initial load
    loadDashboardData();

    // Setup WebSocket once
    wsService.connect(
      (data) => {
        console.log('WebSocket data received:', data);
        if (data.type === 'price_update') {
          setPositions(prevPositions => 
            prevPositions.map(pos => 
              pos.symbol === data.symbol 
                ? { 
                    ...pos, 
                    current_price: data.data.price,
                    pnl: (data.data.price - pos.entry_price) * pos.quantity,
                    pnl_percentage: ((data.data.price - pos.entry_price) / pos.entry_price) * 100,
                    market_value: data.data.price * pos.quantity
                  }
                : pos
            )
          );
        }
      },
      () => {
        console.warn('WebSocket connection failed, continuing with polling data');
      }
    );

    return () => {
      wsService.disconnect();
    };
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load portfolio data
      const [positionsData, performanceData, summaryData] = await Promise.all([
        apiService.getPortfolioPositions(),
        apiService.getPortfolioPerformance(30),
        apiService.getPortfolioSummary()
      ]);

      setPositions(positionsData);
      setPortfolioSummary(summaryData);
      
      // Transform performance data for Nivo charts
      const chartData = [{
        id: 'portfolio',
        data: performanceData.map((item: PerformanceData) => ({
          x: new Date(item.date),
          y: item.value
        }))
      }];
      setPerformanceData(chartData);

    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setError('Failed to load dashboard data. Please check if the backend is running.');
      
      // Fallback to mock data if API fails
      setPerformanceData([
        {
          id: 'portfolio',
          data: [
            { x: new Date('2025-08-01'), y: 100000 },
            { x: new Date('2025-08-02'), y: 102500 },
            { x: new Date('2025-08-03'), y: 101300 },
            { x: new Date('2025-08-04'), y: 105800 },
            { x: new Date('2025-08-05'), y: 108000 }
          ]
        }
      ]);
      
      setPositions([
        { 
          id: 1, 
          symbol: 'AAPL', 
          quantity: 100, 
          entry_price: 150.00, 
          current_price: 155.00, 
          pnl: 500.00, 
          pnl_percentage: 3.33,
          market_value: 15500.00,
          entry_date: '2025-07-01T00:00:00Z'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Subscribe whenever positions change
  useEffect(() => {
    if (positions.length > 0) {
      const symbols = positions.map(pos => pos.symbol);
      wsService.subscribe(symbols);
    }
  }, [positions]);

  const handleHeightChange = (_: Event, value: number | number[]) => {
    const v = Array.isArray(value) ? value[0] : value;
    setChartHeight(v);
    localStorage.setItem('dashboard.chartHeight', String(v));
  };

  return (
    <Grid container spacing={2} sx={{ p: 2 }}>
      {error && (
        <Grid item xs={12}>
          <Alert severity="warning" sx={{ mb: 2 }}>
            {error}
          </Alert>
        </Grid>
      )}
      
      {portfolioSummary && (
        <Grid item xs={12}>
          <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
            <Typography variant="h6" gutterBottom>Portfolio Summary</Typography>
            <Box display="flex" gap={4}>
              <Box>
                <Typography variant="body2" color="textSecondary">Total Value</Typography>
                <Typography variant="h5" color="primary">
                  ${portfolioSummary.total_value.toLocaleString()}
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="textSecondary">Total P&L</Typography>
                <Typography 
                  variant="h5" 
                  color={portfolioSummary.total_pnl >= 0 ? 'success.main' : 'error.main'}
                >
                  ${portfolioSummary.total_pnl.toLocaleString()}
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="textSecondary">Return %</Typography>
                <Typography 
                  variant="h5" 
                  color={portfolioSummary.total_return_percentage >= 0 ? 'success.main' : 'error.main'}
                >
                  {portfolioSummary.total_return_percentage.toFixed(2)}%
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>
      )}

      <Grid item xs={12}>
        <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
          <Stack spacing={2} direction={{ xs: 'column', md: 'row' }} alignItems={{ xs: 'stretch', md: 'center' }} justifyContent="space-between">
            <Stack spacing={1} direction={{ xs: 'column', md: 'row' }} alignItems={{ xs: 'stretch', md: 'center' }}>
              <ChartSelector value={chartType} onChange={setChartType} />
              <TextField
                size="small"
                label="Symbol"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                sx={{ width: 140 }}
              />
            </Stack>
            <Box sx={{ minWidth: 240 }}>
              <Typography variant="body2" color="text.secondary">Chart Height: {chartHeight}px</Typography>
              <Slider
                size="small"
                value={chartHeight}
                onChange={handleHeightChange}
                min={300}
                max={1200}
                step={20}
                aria-label="Chart Height"
              />
              <TextField
                size="small"
                type="number"
                label="Height (px)"
                value={chartHeight}
                onChange={(e) => {
                  const v = Math.max(300, Math.min(1200, Number(e.target.value) || 0));
                  setChartHeight(v);
                  localStorage.setItem('dashboard.chartHeight', String(v));
                }}
                sx={{ width: 140, mt: 1 }}
                inputProps={{ min: 300, max: 1200, step: 20 }}
              />
            </Box>
          </Stack>
        </Paper>
      </Grid>
      
      <Grid item xs={12} lg={8}>
        <Paper elevation={3} sx={{ p: 2 }}>
          {loading && (
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              Loading chart and portfolio data...
            </Typography>
          )}
          <ChartContainer 
            chartType={chartType}
            symbol={symbol}
            theme="dark"
            interval="D"
            indicators={{
              sma: true,
              ema: true,
              rsi: true,
              macd: true
            }}
            height={chartHeight}
          />
        </Paper>
      </Grid>
      
      <Grid item xs={12} lg={4}>
        <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
          <PerformanceChart data={performanceData} />
        </Paper>
        <Paper elevation={3} sx={{ p: 2 }}>
          <PositionsTable positions={positions.map(pos => ({
            id: pos.id || Math.random(),
            symbol: pos.symbol,
            quantity: pos.quantity,
            entryPrice: pos.entry_price || 0,
            currentPrice: pos.current_price || 0,
            pnl: pos.pnl || 0
          }))} />
        </Paper>
      </Grid>
    </Grid>
  );
};

export default Dashboard;
