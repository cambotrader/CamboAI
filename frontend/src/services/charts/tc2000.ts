export interface TC2000Config {
  containerId: string;
  symbol: string;
  interval?: string;
  studies?: string[];
}

export const initTC2000Widget = (config: TC2000Config): void => {
  // Note: This is a placeholder implementation. 
  // TC2000 requires a proper API key and authentication
  const iframe = document.createElement('iframe');
  iframe.style.width = '100%';
  iframe.style.height = '100%';
  iframe.style.border = 'none';
  
  // Replace this URL with actual TC2000 chart URL
  iframe.src = `https://platform.tc2000.com/chart/${config.symbol}`;
  
  const container = document.getElementById(config.containerId);
  if (container) {
    container.innerHTML = '';
    container.appendChild(iframe);
  }
};

export const cleanupTC2000Widget = (containerId: string): void => {
  const container = document.getElementById(containerId);
  if (container) {
    container.innerHTML = '';
  }
};
