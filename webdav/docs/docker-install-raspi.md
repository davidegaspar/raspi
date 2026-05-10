# Docker on Raspberry Pi 4

Install Docker on a Raspberry Pi 4 running 64-bit Raspberry Pi OS (Bookworm).

## Prerequisites

- Raspberry Pi 4 with **64-bit Raspberry Pi OS** (Bookworm recommended)
- SSH or terminal access
- A non-root user (the default `pi` user is fine)

Verify you are on 64-bit before continuing:

```bash
uname -m
# Expected: aarch64
```

If you see `armv7l`, you are on 32-bit OS — reinstall with the 64-bit image before proceeding.

## 1. Clean up broken apt sources

If your Pi has a stale Node.js repository, the Docker install script will fail. Remove it first:

```bash
sudo rm -f /etc/apt/sources.list.d/nodesource.list
```

## 2. Update the system

```bash
sudo apt update
sudo apt upgrade -y
sudo reboot
```

SSH back in after the reboot before continuing.

## 3. Install Docker

```bash
curl -fsSL https://get.docker.com | sh
```

## 4. Add your user to the docker group

```bash
sudo usermod -aG docker $USER
```

> [!IMPORTANT]
> Log out of your SSH session and log back in after this step. The group change does not take effect until you do.

## 5. Verify

```bash
groups
# docker should appear in the list

docker run hello-world
# Should print "Hello from Docker!"
```

Docker is ready.
