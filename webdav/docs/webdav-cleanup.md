# Cleanup WebDAV Docker Setup

Reset the Raspberry Pi back to a clean state, ready to follow the setup guide from scratch.

## 1. Stop and remove the container and image

```bash
cd ~/webdav
docker compose down --rmi all
```

## 2. Remove any leftover containers and images

```bash
docker rm $(docker ps -aq)
docker rmi $(docker images -q)
```

## 3. Remove the webdav directory

The data directory is owned by `www-data` inside the container, so `sudo` is required:

```bash
cd ~
sudo rm -rf ~/webdav
```

## 4. Verify

```bash
docker ps -a
docker images
ls ~/webdav
```

- `docker ps -a` — should return nothing
- `docker images` — should return nothing
- `ls ~/webdav` — should say `No such file or directory`

The Pi is clean and ready to follow [webdav-docker.md](webdav-docker.md) from step 1.
