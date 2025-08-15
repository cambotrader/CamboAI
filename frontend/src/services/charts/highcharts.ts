import Highcharts from 'highcharts/highstock';
import IndicatorsCore from 'highcharts/indicators/indicators';
import IndicatorZigzag from 'highcharts/indicators/zigzag';
import IndicatorMACD from 'highcharts/indicators/macd';
import IndicatorRSI from 'highcharts/indicators/rsi';

// Initialize Highcharts modules
IndicatorsCore(Highcharts);
IndicatorZigzag(Highcharts);
IndicatorMACD(Highcharts);
IndicatorRSI(Highcharts);

export interface HighchartsConfig {
  containerId: string;
  data: any[];
  indicators?: {
    sma?: boolean;
    ema?: boolean;
    rsi?: boolean;
    macd?: boolean;
  };
}

export const initHighchartsChart = (config: HighchartsConfig): void => {
  const { containerId, data, indicators } = config;

  const chartOptions: Highcharts.Options = {
    chart: {
      type: 'candlestick',
      height: '600px'
    },
    title: {
      text: 'Advanced Chart'
    },
    rangeSelector: {
      selected: 1
    },
    series: [{
      type: 'candlestick',
      name: 'Price',
      data: data,
    }]
  };

  // Add indicators if specified
  if (indicators?.sma) {
    chartOptions.series?.push({
      type: 'sma',
      linkedTo: 'price',
      params: {
        period: 14
      }
    } as any);
  }

  if (indicators?.macd) {
    chartOptions.series?.push({
      type: 'macd',
      linkedTo: 'price',
      yAxis: 1
    } as any);
  }

  Highcharts.stockChart(containerId, chartOptions);
};
