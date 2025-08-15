# Build stage
FROM node:20-alpine as build

# Set working directory
WORKDIR /app

# Add package files
COPY package*.json ./

# Install dependencies (prefer npm ci when lockfile exists)
RUN npm config set fund false \
 && npm config set audit false \
 && if [ -f package-lock.json ]; then \
      npm ci --legacy-peer-deps --fetch-retries=5 --fetch-retry-factor=2; \
    else \
      npm install --legacy-peer-deps --fetch-retries=5 --fetch-retry-factor=2; \
    fi

# Copy source files
COPY . .

# Build the application
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=${REACT_APP_API_URL}
RUN echo "Building with REACT_APP_API_URL=$REACT_APP_API_URL" && npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Add nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q --spider http://localhost:80 || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
