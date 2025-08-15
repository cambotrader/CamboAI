import React, { useState, useEffect } from 'react';
import { Box, FormControl, InputLabel, Select, MenuItem, Paper, Typography, Alert } from '@mui/material';
import TradingViewChart from './TradingViewChart';
import HighchartsChart from './HighchartsChart';
import PlotlyChart from './PlotlyChart';

export type AdvancedChartType = 'tradingview' | 'highcharts' | 'plotly' | 'custom';

interface AdvancedChartContainerProps {
  symbol: string;
  chartType: AdvancedChartType;
  theme?: 'light' | 'dark';
  height?: number;
  onChartTypeChange?: (chartType: AdvancedChartType) => void;
  onSymbolChange?: (symbol: string) => void;
}

const AdvancedChartContainer: React.FC<AdvancedChartContainerProps> = ({
  symbol,
  chartType,
  theme = 'dark',
  height = 600,
  onChartTypeChange,
  onSymbolChange
}) => {
  const [currentSymbol, setCurrentSymbol] = useState(symbol);
  const [currentChartType, setCurrentChartType] = useState(chartType);
  const [interval, setInterval] = useState('D');
  const [error, setError] = useState<string | null>(null);

  const chartTypes = [
    { value: 'tradingview', label: 'TradingView', description: 'Professional charting with advanced tools' },
    { value: 'highcharts', label: 'Highcharts', description: 'Fast and responsive charts' },
    { value: 'plotly', label: 'Plotly', description: 'Interactive data visualization' },
    { value: 'custom', label: 'Custom', description: 'Custom chart implementation' }
  ];

  const popularSymbols = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
    'SPY', 'QQQ', 'IWM', 'GLD', 'SLV', 'TLT', 'VIX'
  ];

  useEffect(() => {
    setCurrentSymbol(symbol);
  }, [symbol]);

  useEffect(() => {
    setCurrentChartType(chartType);
  }, [chartType]);

  const handleChartTypeChange = (newChartType: AdvancedChartType) => {
    setCurrentChartType(newChartType);
    setError(null);
    if (onChartTypeChange) {
      onChartTypeChange(newChartType);
    }
  };

  const handleSymbolChange = (newSymbol: string) => {
    setCurrentSymbol(newSymbol);
    setError(null);
    if (onSymbolChange) {
      onSymbolChange(newSymbol);
    }
  };

  const renderChart = () => {
    try {
      switch (currentChartType) {
        case 'tradingview':
          return (
            <TradingViewChart
              symbol={currentSymbol}
              interval={interval}
              theme={theme}
              height={height}
              onIntervalChange={setInterval}
            />
          );
        
        case 'highcharts':
          return (
            <HighchartsChart
              symbol={currentSymbol}
              interval={interval}
              theme={theme}
              height={height}
            />
          );
        
        case 'plotly':
          return (
            <PlotlyChart
              symbol={currentSymbol}
              interval={interval}
              theme={theme}
              height={height}
            />
          );
        
        case 'custom':
          return (
            <Box
              display="flex"
              justifyContent="center"
              alignItems="center"
              height={height}
              bgcolor="grey.100"
              borderRadius={1}
            >
              <Typography variant="h6" color="textSecondary">
                Custom Chart Implementation Coming Soon
              </Typography>
            </Box>
          );
        
        default:
          return (
            <Box
              display="flex"
              justifyContent="center"
              alignItems="center"
              height={height}
              bgcolor="grey.100"
              borderRadius={1}
            >
              <Typography variant="h6" color="error">
                Unsupported chart type: {currentChartType}
              </Typography>
            </Box>
          );
      }
    } catch (err) {
      console.error('Chart rendering error:', err);
      setError(`Failed to render ${currentChartType} chart: ${err instanceof Error ? err.message : 'Unknown error'}`);
      return null;
    }
  };

  return (
    <Paper elevation={2} sx={{ p: 2 }}>
      {/* Chart Controls */}
      <Box display="flex" gap={2} mb={2} flexWrap="wrap" alignItems="center">
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Chart Type</InputLabel>
          <Select
            value={currentChartType}
            label="Chart Type"
            onChange={(e) => handleChartTypeChange(e.target.value as AdvancedChartType)}
          >
            {chartTypes.map((type) => (
              <MenuItem key={type.value} value={type.value}>
                <Box>
                  <Typography variant="body2">{type.label}</Typography>
                  <Typography variant="caption" color="textSecondary">
                    {type.description}
                  </Typography>
                </Box>
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Symbol</InputLabel>
          <Select
            value={currentSymbol}
            label="Symbol"
            onChange={(e) => handleSymbolChange(e.target.value)}
          >
            {popularSymbols.map((sym) => (
              <MenuItem key={sym} value={sym}>
                {sym}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <Typography variant="body2" color="textSecondary">
          Current: {currentSymbol} | {chartTypes.find(t => t.value === currentChartType)?.label}
        </Typography>
      </Box>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Chart Display */}
      <Box sx={{ position: 'relative' }}>
        {renderChart()}
      </Box>

      {/* Chart Info */}
      <Box mt={2} display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="caption" color="textSecondary">
          Chart Provider: {chartTypes.find(t => t.value === currentChartType)?.label}
        </Typography>
        <Typography variant="caption" color="textSecondary">
          Symbol: {currentSymbol} | Interval: {interval}
        </Typography>
      </Box>
    </Paper>
  );
};

export default AdvancedChartContainer;
