import React, { useEffect, useRef, useState } from 'react';
import { Box, FormControl, InputLabel, Select, MenuItem, Switch, FormControlLabel, Chip } from '@mui/material';

declare global {
  interface Window {
    TradingView: any;
  }
}

interface TradingViewChartProps {
  symbol: string;
  interval?: string;
  theme?: 'light' | 'dark';
  height?: number;
  width?: number;
  autosize?: boolean;
  studies?: string[];
  onIntervalChange?: (interval: string) => void;
}

const TradingViewChart: React.FC<TradingViewChartProps> = ({
  symbol,
  interval = 'D',
  theme = 'dark',
  height = 600,
  width = 100,
  autosize = true,
  studies = [],
  onIntervalChange
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [widget, setWidget] = useState<any>(null);
  const [currentInterval, setCurrentInterval] = useState(interval);
  const [enabledStudies, setEnabledStudies] = useState<string[]>(studies);
  const [isScriptLoaded, setIsScriptLoaded] = useState(false);

  // Load TradingView script
  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/tv.js';
    script.async = true;
    script.onload = () => setIsScriptLoaded(true);
    document.head.appendChild(script);

    return () => {
      if (document.head.contains(script)) {
        document.head.removeChild(script);
      }
    };
  }, []);

  // Initialize TradingView widget
  useEffect(() => {
    if (!isScriptLoaded || !containerRef.current || !window.TradingView) {
      return;
    }

    const widgetConfig = {
      autosize: autosize,
      width: autosize ? undefined : width,
      height: height,
      symbol: symbol,
      interval: currentInterval,
      timezone: "Etc/UTC",
      theme: theme,
      style: "1",
      locale: "en",
      toolbar_bg: "#f1f3f6",
      enable_publishing: false,
      hide_top_toolbar: false,
      hide_legend: false,
      save_image: false,
      container_id: containerRef.current.id,
      studies: enabledStudies.map(study => ({
        id: study,
        version: "1"
      })),
      overrides: {
        "volumePaneSize": "medium",
        "paneProperties.background": theme === 'dark' ? "#1e1e1e" : "#ffffff",
        "paneProperties.vertGridProperties.color": theme === 'dark' ? "#2a2a2a" : "#e1e1e1",
        "paneProperties.horzGridProperties.color": theme === 'dark' ? "#2a2a2a" : "#e1e1e1",
        "symbolWatermarkProperties.transparency": 90,
        "scalesProperties.textColor": theme === 'dark' ? "#cccccc" : "#333333",
        "mainSeriesProperties.candleStyle.wickUpColor": "#26a69a",
        "mainSeriesProperties.candleStyle.wickDownColor": "#ef5350",
        "mainSeriesProperties.candleStyle.upColor": "#26a69a",
        "mainSeriesProperties.candleStyle.downColor": "#ef5350",
        "mainSeriesProperties.candleStyle.borderUpColor": "#26a69a",
        "mainSeriesProperties.candleStyle.borderDownColor": "#ef5350",
      },
      disabled_features: [
        "use_localstorage_for_settings",
        "volume_force_overlay",
        "create_volume_indicator_by_default"
      ],
      enabled_features: [
        "study_templates",
        "side_toolbar_in_fullscreen_mode"
      ]
    };

    const newWidget = new window.TradingView.widget(widgetConfig);
    setWidget(newWidget);

    newWidget.onChartReady(() => {
      console.log('TradingView chart is ready');
      
      // Add custom studies if specified
      enabledStudies.forEach(studyId => {
        newWidget.chart().createStudy(studyId, false, false);
      });
    });

    return () => {
      if (newWidget && newWidget.remove) {
        newWidget.remove();
      }
    };
  }, [isScriptLoaded, symbol, currentInterval, theme, height, width, autosize]);

  const handleIntervalChange = (newInterval: string) => {
    setCurrentInterval(newInterval);
    if (onIntervalChange) {
      onIntervalChange(newInterval);
    }
    
    if (widget && widget.chart) {
      widget.chart().setResolution(newInterval);
    }
  };

  const handleStudyToggle = (studyId: string) => {
    const newEnabledStudies = enabledStudies.includes(studyId)
      ? enabledStudies.filter(id => id !== studyId)
      : [...enabledStudies, studyId];
    
    setEnabledStudies(newEnabledStudies);
    
    if (widget && widget.chart) {
      if (newEnabledStudies.includes(studyId)) {
        widget.chart().createStudy(studyId, false, false);
      } else {
        // Note: TradingView doesn't provide easy way to remove studies programmatically
        // This would require more complex implementation
      }
    }
  };

  const intervals = [
    { value: '1', label: '1m' },
    { value: '5', label: '5m' },
    { value: '15', label: '15m' },
    { value: '30', label: '30m' },
    { value: '60', label: '1h' },
    { value: '240', label: '4h' },
    { value: 'D', label: '1D' },
    { value: 'W', label: '1W' },
    { value: 'M', label: '1M' }
  ];

  const availableStudies = [
    { id: 'RSI', name: 'RSI' },
    { id: 'MACD', name: 'MACD' },
    { id: 'BB', name: 'Bollinger Bands' },
    { id: 'EMA', name: 'EMA' },
    { id: 'SMA', name: 'SMA' },
    { id: 'Volume', name: 'Volume' },
    { id: 'Stoch', name: 'Stochastic' },
    { id: 'ATR', name: 'ATR' },
    { id: 'ADX', name: 'ADX' },
    { id: 'CCI', name: 'CCI' }
  ];

  return (
    <Box>
      {/* Chart Controls */}
      <Box display="flex" gap={2} mb={2} flexWrap="wrap" alignItems="center">
        <FormControl size="small" sx={{ minWidth: 100 }}>
          <InputLabel>Interval</InputLabel>
          <Select
            value={currentInterval}
            label="Interval"
            onChange={(e) => handleIntervalChange(e.target.value)}
          >
            {intervals.map((int) => (
              <MenuItem key={int.value} value={int.value}>
                {int.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <Box display="flex" gap={1} flexWrap="wrap">
          {availableStudies.map((study) => (
            <Chip
              key={study.id}
              label={study.name}
              onClick={() => handleStudyToggle(study.id)}
              color={enabledStudies.includes(study.id) ? 'primary' : 'default'}
              variant={enabledStudies.includes(study.id) ? 'filled' : 'outlined'}
              size="small"
            />
          ))}
        </Box>
      </Box>

      {/* TradingView Chart Container */}
      <Box
        ref={containerRef}
        id={`tradingview_chart_${Math.random().toString(36).substr(2, 9)}`}
        sx={{
          height: height,
          width: '100%',
          '& iframe': {
            border: 'none',
            borderRadius: 1
          }
        }}
      />

      {!isScriptLoaded && (
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          height={height}
          bgcolor="grey.100"
          borderRadius={1}
        >
          Loading TradingView Chart...
        </Box>
      )}
    </Box>
  );
};

export default TradingViewChart;
