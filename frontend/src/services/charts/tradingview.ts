// TradingView Widget Integration
export interface TradingViewConfig {
  symbol: string;
  interval?: string;
  theme?: 'light' | 'dark';
  containerId: string;
}

export const initTradingViewWidget = (config: TradingViewConfig): void => {
  const tvSrc = 'https://s3.tradingview.com/tv.js';
  const container = document.getElementById(config.containerId);

  const renderFallback = (message: string) => {
    if (container) {
      container.innerHTML = `\n        <div style="display:flex;align-items:center;justify-content:center;height:100%;color:#94a3b8;text-align:center;padding:16px">\n          <div>\n            <div style="font-weight:600;margin-bottom:8px">Chart unavailable</div>\n            <div style="font-size:12px;opacity:.8">${message}</div>\n          </div>\n        </div>`;
    }
  };

  // If tv.js already present, try to init immediately
  const existing = document.querySelector(`script[src="${tvSrc}"]`) as HTMLScriptElement | null;
  const tryInit = () => {
    const TV = (window as any).TradingView;
    if (TV && typeof TV.widget === 'function') {
      // eslint-disable-next-line new-cap
      new TV.widget({
        width: '100%',
        height: '100%',
        symbol: config.symbol,
        interval: config.interval || 'D',
        timezone: 'exchange',
        theme: config.theme || 'dark',
        style: '1',
        locale: 'en',
        toolbar_bg: '#f1f3f6',
        enable_publishing: false,
        allow_symbol_change: true,
        container_id: config.containerId
      });
      return true;
    }
    return false;
  };

  if (existing) {
    if (!tryInit()) {
      existing.addEventListener('load', () => {
        if (!tryInit()) renderFallback('TradingView failed to initialize.');
      });
      existing.addEventListener('error', () => renderFallback('TradingView script blocked or failed to load.'));
    }
    return;
  }

  const script = document.createElement('script');
  script.src = tvSrc;
  script.async = true;

  const timeoutId = window.setTimeout(() => {
    if (!tryInit()) {
      renderFallback('Loading timed out. Check your network/VPN or try again.');
    }
  }, 8000);

  script.onload = () => {
    window.clearTimeout(timeoutId);
    if (!tryInit()) {
      renderFallback('TradingView failed to initialize.');
    }
  };
  script.onerror = () => {
    window.clearTimeout(timeoutId);
    renderFallback('TradingView script blocked or failed to load.');
  };
  document.head.appendChild(script);
};

// Function to clean up TradingView widget
export const cleanupTradingViewWidget = (containerId: string): void => {
  const container = document.getElementById(containerId);
  if (container) {
    container.innerHTML = '';
  }
};
