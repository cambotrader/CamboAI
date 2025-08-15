import React, { useEffect, useMemo, useState } from 'react';
import { Box, Chip, Tooltip, Stack, CircularProgress } from '@mui/material';
import { apiService, wsService } from '../services/api';

// Maps WS readyState to labels/colors
const wsStateMap: Record<number, { label: string; color: 'success' | 'warning' | 'error' | 'default' }> = {
  0: { label: 'WS: Connecting', color: 'warning' },
  1: { label: 'WS: Connected', color: 'success' },
  2: { label: 'WS: Closing', color: 'warning' },
  3: { label: 'WS: Disconnected', color: 'error' },
};

export default function StatusWidget() {
  const [apiStatus, setApiStatus] = useState<'checking' | 'up' | 'down'>('checking');
  const [wsState, setWsState] = useState<number>(WebSocket.CLOSED);
  const [latencyMs, setLatencyMs] = useState<number | null>(null);

  // Ping backend health periodically
  useEffect(() => {
    let mounted = true;
    const ping = async () => {
      try {
        const start = performance.now();
        await apiService.healthCheck();
        const end = performance.now();
        if (!mounted) return;
        setLatencyMs(Math.round(end - start));
        setApiStatus('up');
      } catch (e) {
        if (!mounted) return;
        setApiStatus('down');
      }
    };

    // initial ping and interval
    ping();
    const id = window.setInterval(ping, 10000);
    return () => { mounted = false; window.clearInterval(id); };
  }, []);

  // Track WS connection state without forcing a connection if none yet
  useEffect(() => {
    const unsubscribe = wsService.onStateChange((state) => setWsState(state));
    return () => { unsubscribe && unsubscribe(); };
  }, []);

  const apiChip = useMemo(() => {
    if (apiStatus === 'checking') {
      return (
        <Tooltip title="Checking backend health">
          <Chip
            size="small"
            label={
              <Box display="flex" alignItems="center" gap={1}>
                <CircularProgress size={12} />
                <span>API: Checking</span>
              </Box>
            }
            color="default"
            variant="outlined"
          />
        </Tooltip>
      );
    }

    const color = apiStatus === 'up' ? 'success' : 'error';
    const title = apiStatus === 'up' ? 'Backend is reachable' : 'Backend is not reachable';
    const label = apiStatus === 'up' ? (latencyMs !== null ? `API: ${latencyMs}ms` : 'API: OK') : 'API: DOWN';

    return (
      <Tooltip title={title}>
        <Chip size="small" label={label} color={color as any} variant="filled" />
      </Tooltip>
    );
  }, [apiStatus, latencyMs]);

  const wsChip = useMemo(() => {
    const meta = wsStateMap[wsState] ?? { label: 'WS: Unknown', color: 'default' as const };
    return (
      <Tooltip title="WebSocket connection status to /ws/prices">
        <Chip size="small" label={meta.label} color={meta.color as any} variant="outlined" />
      </Tooltip>
    );
  }, [wsState]);

  return (
    <Stack direction="row" spacing={1} alignItems="center">
      {apiChip}
      {wsChip}
    </Stack>
  );
}