# raspi-webdav

Lightweight WebDAV server for Raspberry Pi 4, running in Docker using a custom `debian:bookworm-slim` image. Designed for syncing [Super Productivity](https://super-productivity.com/) across devices via Tailscale.

## Files

| File                 | Purpose                                   |
| -------------------- | ----------------------------------------- |
| `Dockerfile`         | Builds nginx:alpine with WebDAV extension |
| `nginx.conf`         | WebDAV server configuration               |
| `docker-compose.yml` | Container definition                      |
| `.gitignore`         | Excludes credentials and data from git    |

## Setup guides

1. [Install Docker on Raspberry Pi](docs/docker-install-raspi.md)
2. [Run the WebDAV server](docs/webdav-docker.md)
3. [Set up Tailscale for remote access](docs/tailscale-setup.md)

## Security

- `.htpasswd` and `data/` are excluded from git via `.gitignore` — keep it that way
- Do not expose port 8080 on your router
- Access remotely via [Tailscale](https://tailscale.com/) only
