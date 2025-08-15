const webpack = require('webpack');

module.exports = {
  webpack: {
    configure: (config) => {
      config.resolve = config.resolve || {};
      config.resolve.fallback = {
        ...(config.resolve.fallback || {}),
        assert: require.resolve('assert/'),
        buffer: require.resolve('buffer/'),
        stream: require.resolve('stream-browserify'),
        util: require.resolve('util/'),
        process: require.resolve('process/browser'),
        url: require.resolve('url/'),
        path: require.resolve('path-browserify')
      };

      // Helpful aliases for libraries that import node modules in browser
      config.resolve.alias = {
        ...(config.resolve.alias || {}),
        // Use prebuilt Plotly bundle that avoids node deps
        'plotly.js$': require.resolve('plotly.js-dist-min'),
        // Handle imports that reference 'buffer/'
        'buffer/': require.resolve('buffer/'),
        buffer: require.resolve('buffer/')
      };

      config.plugins = [
        ...(config.plugins || []),
        new webpack.ProvidePlugin({
          Buffer: ['buffer', 'Buffer'],
          process: ['process']
        })
      ];

      return config;
    }
  }
};
