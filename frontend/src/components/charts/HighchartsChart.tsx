import React from 'react';
import { Box, Typography } from '@mui/material';

interface HighchartsChartProps {
  symbol: string;
  interval: string;
  theme?: 'light' | 'dark';
  height?: number;
  data?: any[];
  onDataUpdate?: (data: any[]) => void;
}

const HighchartsChart: React.FC<HighchartsChartProps> = ({ symbol, interval, theme = 'light', height = 400, data, onDataUpdate }) => {
  return (
    <Box 
      sx={{ 
        width: '100%', 
        height: height, 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        border: '1px solid #ccc',
        backgroundColor: theme === 'dark' ? '#1e1e1e' : '#ffffff',
        color: theme === 'dark' ? '#ffffff' : '#000000',
  borderRadius: 1
      }}
    >
      <Typography variant="h6" color="text.secondary">
        Highcharts Chart - {symbol} ({interval})
      </Typography>
    </Box>
  );
};

export default HighchartsChart;
