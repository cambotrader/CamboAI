import React from 'react';
import { ResponsiveLine } from '@nivo/line';
import { Box, Paper, Typography } from '@mui/material';

interface PerformanceChartProps {
  data: Array<{
    id: string;
    data: Array<{
      x: string | Date;
      y: number;
    }>;
  }>;
}

const PerformanceChart: React.FC<PerformanceChartProps> = ({ data }) => {
  return (
    <Paper elevation={2} sx={{ p: 2, height: '400px' }}>
      <Typography variant="h6" gutterBottom>
        Portfolio Performance
      </Typography>
      <Box sx={{ height: '90%' }}>
        <ResponsiveLine
          data={data}
          margin={{ top: 20, right: 20, bottom: 50, left: 60 }}
          xScale={{ type: 'time' }}
          yScale={{ type: 'linear' }}
          axisBottom={{
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
            format: '%b %d',
            legend: 'Date',
            legendOffset: 36,
            legendPosition: 'middle'
          }}
          axisLeft={{
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
            legend: 'Value',
            legendOffset: -40,
            legendPosition: 'middle'
          }}
          pointSize={10}
          useMesh={true}
          curve="monotoneX"
        />
      </Box>
    </Paper>
  );
};

export default PerformanceChart;
