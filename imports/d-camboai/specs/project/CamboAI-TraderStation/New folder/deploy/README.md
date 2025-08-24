# Public HTTPS deployment (phone anywhere)

This folder lets you deploy CamboStation-Vision with automatic HTTPS (Let’s Encrypt) so you can access it from your phone anywhere via your own domain.

## What you need

- A domain name you control (e.g., example.com)
- A public server (VPS or cloud VM) with Docker & Docker Compose installed
- DNS A record pointing your domain to the server’s public IP

## One-time setup on your server

1. Copy the project to your server (or git clone).
2. Update DNS: point `yourdomain.com` to your server IP and wait for propagation.
3. On the server, from this `deploy` folder, create an `.env` file with:

```bash
DOMAIN=yourdomain.com
```

4. Build and start the stack:

```bash
docker compose up --build -d
```

This will start three containers:

- frontend (nginx serving the built React app)
- backend (FastAPI)
- caddy (reverse proxy terminating TLS and routing to frontend/backend)

Caddy automatically obtains and renews TLS certificates. Browse to:

- <https://yourdomain.com>

## Notes

- Frontend talks to backend via same-origin `/api` and `/ws` through the proxy.
- To update:

```bash
docker compose pull
# or rebuild locally
# docker compose build

docker compose up -d
```

## Troubleshooting

- SSL issuance requires port 80/443 open to the internet.
- DNS must resolve your domain to your server IP.
- Check logs:

```bash
docker compose logs -f caddy
```

## Free option: run from home with Cloudflare Tunnel (no ports, no VPS)

If you prefer not to rent a server or open ports on your router, you can expose your app securely using a free Cloudflare Tunnel.

### Overview

- Frontend and backend run locally in Docker.
- Cloudflared makes an outbound tunnel to Cloudflare and serves your domain.
- No port forwarding required; you keep 80/443 closed.

### Steps

1. Sign up and add camboai.com to Cloudflare (free plan), point your domain’s nameservers to Cloudflare.
2. In Cloudflare dashboard, create a Tunnel (Zero Trust -> Access -> Tunnels -> Create).
	- Choose Docker as the connector and copy the provided token.
3. In this `deploy` folder, create `.env`:

```bash
DOMAIN=camboai.com
CLOUDFLARE_TUNNEL_TOKEN=paste_the_token_here
```

1. Start the local stack with the tunnel:

```powershell
cd "c:\Users\johnl\CamboAI-TraderStation\New folder\deploy"
docker compose -f docker-compose.tunnel.yml up --build -d
```

2. In the tunnel’s Public Hostname config, set:
	- Hostname: camboai.com
	- Service: HTTP
	- URL: <http://frontend:80>

3. Browse to <https://camboai.com> (Cloudflare will handle TLS).

Notes:

- You can also add `www.camboai.com` as another Public Hostname pointing to `<http://frontend:80>`.
- Note: The frontend’s nginx already proxies `/api` and `/ws` to the backend on the Docker network, so you don’t need extra routes in Cloudflare.
- If you proxy through Cloudflare, same-origin paths `/api` and `/ws` still work since Cloudflare maps to your containers.
