/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  images: {
    domains: ['localhost', 'your-backend-domain.com', 'camboai.com', 'www.camboai.com', 'api.camboai.com'],
  },
  env: {
    CUSTOM_KEY: 'my-value',
  },
  async rewrites() {
    // In development only, if NEXT_PUBLIC_API_BASE isn't set, proxy to local backend
    if (!process.env.NEXT_PUBLIC_API_BASE && process.env.NODE_ENV !== 'production') {
      return [
        {
          source: '/api/:path*',
          destination: 'http://localhost:8000/api/:path*',
        },
      ];
    }
    return [];
  },
  webpack: (config) => {
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
    };
    return config;
  },
};

export default nextConfig;