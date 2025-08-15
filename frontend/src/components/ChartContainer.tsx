import React, { useEffect, useRef } from 'react';
import { Box } from '@mui/material';
import { initTradingViewWidget, initHighchartsChart } from '../services/charts';
import type { ChartData } from '../services/charts';
import './ChartContainer.css';

interface ChartContainerProps {
  chartType: 'tradingview' | 'highcharts' | 'plotly' | 'tc2000' | 'thinkorswim' | 'ninjatrader' | 'mt4' | 'mt5' | 'trendspider';
  symbol: string;
  data?: ChartData[];
  interval?: string;
  theme?: 'light' | 'dark';
  height?: number | string;
  indicators?: {
    sma?: boolean;
    ema?: boolean;
    rsi?: boolean;
    macd?: boolean;
  };
  studies?: string[];
}

const ChartContainer: React.FC<ChartContainerProps> = ({
  chartType,
  symbol,
  data,
  interval = 'D',
  theme = 'dark',
  height = 600,
  indicators
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartIdRef = useRef<string>(`chart-${Math.random().toString(36).substr(2, 9)}`);

  useEffect(() => {
  const currentId = chartIdRef.current;
  if (!containerRef.current) {
      return;
    }

    switch (chartType) {
      case 'tradingview':
        initTradingViewWidget({ symbol, interval, theme, containerId: chartIdRef.current });
        break;
      case 'highcharts':
        if (data) {
          initHighchartsChart({ containerId: chartIdRef.current, data, indicators });
        }
        break;
      case 'plotly':
        // With react-plotly handled in PlotlyChart component, this container can no-op or build payload if needed.
        break;
    }

    // Cleanup function
    return () => {
  const container = document.getElementById(currentId);
      if (container) {
        container.innerHTML = '';
      }
    };
  }, [chartType, symbol, data, interval, theme, indicators]);

  return (
    <Box
      ref={containerRef}
  id={chartIdRef.current}
      sx={{
        width: '100%',
  height: typeof height === 'number' ? `${height}px` : height,
        backgroundColor: theme === 'dark' ? '#131722' : '#ffffff'
      }}
    >
      {chartType === 'highcharts' && (!data || data.length === 0) && (
        <div className="chart-fallback">Waiting for chart data...</div>
      )}
    </Box>
  );
};

export default ChartContainer;
