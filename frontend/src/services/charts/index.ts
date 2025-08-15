export interface ChartData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface ChartConfig {
  type: 'tradingview' | 'highcharts' | 'plotly' | 'tc2000' | 'thinkorswim' | 'ninjatrader' | 'mt4' | 'mt5' | 'trendspider';
  symbol: string;
  interval?: string;
  theme?: 'light' | 'dark';
  containerId: string;
  data?: ChartData[];
  indicators?: {
    sma?: boolean;
    ema?: boolean;
    rsi?: boolean;
    macd?: boolean;
  };
  studies?: string[];
}

export * from './tradingview';
export * from './highcharts';
export * from './plotly';
export { buildPlotlyPayload as createPlotlyChart } from './plotly';
