# WebDAV Server with Docker

Run a lightweight WebDAV server in Docker using a custom `debian:bookworm-slim` image. No third-party images.

> [!NOTE]
> `nginx:alpine` and `nginx:bookworm` official images do not work here — they use nginx.org's own nginx build which is incompatible with distro-packaged WebDAV modules. Use `debian:bookworm-slim` and install nginx from Debian repos instead.

**Assumes Docker is installed and ready.** See [docker-install-raspi.md](docker-install-raspi.md) if not.

## Repo structure

The repo contains both documentation and deployment files. Only the deployment files go to the Pi — docs stay on your Mac.

```
raspi-webdav/
├── README.md
├── .gitignore
├── Dockerfile             ← deploy to Pi
├── nginx.conf             ← deploy to Pi
├── docker-compose.yml     ← deploy to Pi
└── docs/
    ├── docker-install-raspi.md
    └── webdav-docker.md
```

## 1. Prepare the Pi

SSH into the Pi, create the working directory, and fix permissions in one session. The nginx process inside the container runs as `www-data` (uid 33) — ownership must be set before the container starts.

```bash
ssh <user>@<pi-ip>
mkdir -p ~/webdav/data/super-productivity
sudo chown -R 33:33 ~/webdav/data
```

Verify:

```bash
ls -la ~/webdav/data/
# Should show: www-data www-data
exit
```

## 2. Deploy files from your Mac

Run this from the root of the repo on your Mac:

```bash
scp Dockerfile nginx.conf docker-compose.yml <user>@<pi-ip>:~/webdav/
```

## 3. Generate credentials

Still on the Pi, run this from inside `~/webdav`. The `-it` flag is required for the interactive password prompt.

```bash
cd ~/webdav
docker run --rm -it debian:bookworm-slim sh -c \
  "apt-get update -q && apt-get install -y -q apache2-utils && htpasswd -nB webdav" | tee -a .htpasswd
```

The hash will be printed on screen and appended to `.htpasswd` — no separate verification needed.

> [!NOTE]
> `.htpasswd` is excluded from git via `.gitignore`. Generate it directly on the Pi and never commit it.

## 4. Build and run

On the Pi inside `~/webdav`, do a clean build — always use `--no-cache` on first build and after any config changes to ensure updated files are picked up:

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

Check the container is running:

```bash
docker compose ps
```

View logs if something looks wrong:

```bash
docker compose logs -f
```

## 5. Verify the config loaded correctly

```bash
docker compose exec webdav cat /etc/nginx/nginx.conf
```

Confirm `user www-data;` and `client_body_temp_path` are present. If not, the old cached image is still running — repeat the clean build above.

## 6. Test

From the Pi:

```bash
curl -u webdav:yourpassword http://localhost:8090/dav/
```

From another machine on the same network (find your Pi's IP with `hostname -I`):

```bash
curl -u webdav:yourpassword http://<pi-ip>:8090/dav/
```

A directory listing in the response confirms WebDAV is working.

## Redeploying after changes

After updating any file on your Mac, always force a clean rebuild:

```bash
scp Dockerfile nginx.conf docker-compose.yml <user>@<pi-ip>:~/webdav/
ssh <user>@<pi-ip> "cd ~/webdav && docker compose down && docker compose build --no-cache && docker compose up -d"
```

> [!WARNING]
> `docker compose up -d --build` can silently use cached layers and miss config changes. Always use `--no-cache` after editing `nginx.conf` or `Dockerfile`.

## Super Productivity sync settings

Use these values in Super Productivity → Global Settings → Configure Sync:

| Field            | Value                      |
| ---------------- | -------------------------- |
| Sync provider    | WebDAV                     |
| Base URL         | `http://<pi-ip>:8090/dav/` |
| Username         | `webdav`                   |
| Password         | your password              |
| Sync Folder Path | `super-productivity`       |

Find your Pi's local IP with `hostname -I` on the Pi.

This works on your local network only. To access the WebDAV server from outside your home network, see [tailscale-setup.md](tailscale-setup.md).

## Notes

- **Data location** — all WebDAV files live in `~/webdav/data/` on the Pi. Back this up regularly.
- **Auto-shutdown** — if your Pi shuts down on a cron schedule, sync will fail during that window. Adjust or remove the shutdown job if you need always-on sync.
- **Permissions** — if you recreate the data directory, re-run `sudo chown -R 33:33 ~/webdav/data` on the Pi.
- **Do not expose port 8090 on your router** — use Tailscale for remote access instead.
