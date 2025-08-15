import React from 'react';
import { Box, Typography } from '@mui/material';
// Ensure we use the browser-friendly Plotly bundle
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import Plot from 'react-plotly.js';
import { buildPlotlyPayload } from '../../services/charts/plotly';

interface PlotlyChartProps {
  symbol: string;
  interval: string;
  theme?: 'light' | 'dark';
  height?: number;
  data?: any[];
  onDataUpdate?: (data: any[]) => void;
}

const PlotlyChart: React.FC<PlotlyChartProps> = ({ symbol, interval, theme = 'light', height = 400, data = [], onDataUpdate }) => {
  const baseLayout = {
    title: `Plotly Chart - ${symbol} (${interval})`,
    paper_bgcolor: theme === 'dark' ? '#1e1e1e' : '#ffffff',
    plot_bgcolor: theme === 'dark' ? '#1e1e1e' : '#ffffff',
    font: { color: theme === 'dark' ? '#ffffff' : '#000000' },
    autosize: true,
    height,
    margin: { l: 40, r: 20, t: 40, b: 40 }
  } as Partial<Plotly.Layout>;
  const payload = buildPlotlyPayload(data as any, baseLayout);

  return (
    <Box sx={{ width: '100%' }}>
  <Plot data={payload.data as any} layout={payload.layout as any} config={payload.config as any} style={{ width: '100%' }} useResizeHandler />
    </Box>
  );
};

export default PlotlyChart;
