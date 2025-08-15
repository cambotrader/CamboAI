import type { Data, Layout, Config, PlotData } from 'plotly.js';
// Helper functions around plotly payloads can remain typed only
import { ChartData } from './index';

export interface PlotlyConfig {
  containerId: string;
  data: ChartData[];
  layout?: Partial<Layout>;
  config?: Partial<Config>;
}

export const buildPlotlyPayload = (data: ChartData[], layout: Partial<Layout> = {}, config: Partial<Config> = {}) => {
  const trace = {
    x: data.map(d => new Date(d.date)),
    open: data.map(d => d.open),
    high: data.map(d => d.high),
    low: data.map(d => d.low),
    close: data.map(d => d.close),
    type: 'candlestick' as const,
    xaxis: 'x',
    yaxis: 'y'
  } as Partial<PlotData>;

  const defaultLayout: Partial<Layout> = {
    dragmode: 'zoom',
    showlegend: false,
    xaxis: { rangeslider: { visible: false } },
    yaxis: { autorange: true, type: 'linear' as const }
  };

  return {
    data: [trace],
    layout: { ...defaultLayout, ...layout },
    config: { responsive: true, ...config }
  };
};
