import React from 'react';
import { FormControl, InputLabel, Select, MenuItem, SelectChangeEvent } from '@mui/material';

export type ChartType = 'tradingview' | 'highcharts' | 'plotly' | 'tc2000';

interface ChartSelectorProps {
  value: ChartType;
  onChange: (value: ChartType) => void;
}

const ChartSelector: React.FC<ChartSelectorProps> = ({ value, onChange }) => {
  const chartTypes = [
    { value: 'tradingview' as const, label: 'TradingView' },
    { value: 'highcharts' as const, label: 'HighCharts' },
    { value: 'plotly' as const, label: 'Plotly' },
    { value: 'tc2000' as const, label: 'TC2000' }
  ];

  return (
    <FormControl fullWidth>
      <InputLabel>Chart Provider</InputLabel>
      <Select
        value={value}
        label="Chart Provider"
        onChange={(e: SelectChangeEvent<ChartType>) => {
          const newValue = e.target.value as ChartType;
          onChange(newValue);
        }}
      >
        {chartTypes.map((type) => (
          <MenuItem key={type.value} value={type.value}>
            {type.label}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};

export default ChartSelector;
