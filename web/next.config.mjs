import withPWA from 'next-pwa';

const withPWAPlugin = withPWA({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV !== 'production',
});

const nextConfig = {
  reactStrictMode: true,
  experimental: { serverActions: true },
};

export default withPWAPlugin(nextConfig);
