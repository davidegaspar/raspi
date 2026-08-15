# Podman on Mac → Connect to Raspberry Pi

## 1. Install Podman (CLI)

```bash
brew install podman
podman machine init
podman machine start
podman version   # confirms client + machine are both working
```

On Apple Silicon this uses the Apple Virtualization Framework automatically — no extra config needed.

## 2. Install Podman Desktop (GUI, optional)

```bash
brew install --cask podman-desktop
```

Or download the installer directly from [podman-desktop.io/downloads](https://podman-desktop.io/downloads).

## 3. Connect to the Pi

On the **Pi**, make sure the Podman socket is running and survives logout:

```bash
systemctl --user enable --now podman.socket
sudo loginctl enable-linger $(whoami)
```

On the **Mac**, register the Pi as a remote connection. `--identity` points to your **private** key (e.g. `~/.ssh/id_ed25519`, no `.pub`) — the matching public key is what's already in the Pi's `authorized_keys`:

```bash
podman system connection add rpi \
  --identity ~/.ssh/<your-existing-private-key> \
  ssh://<pi-user>@<pi-ip-or-hostname>/run/user/1000/podman/podman.sock

podman system connection default rpi   # optional: make it the default target
podman --connection rpi info           # verify it works
```

`1000` is the Pi user's UID — check with `id -u` on the Pi if it's different.

**In Podman Desktop:** Settings → Preferences → **Extension: Podman** → enable "Remote"/"loading remote system connections over SSH." The Pi should then appear as a selectable engine, showing its containers, images, and pods alongside (or instead of) the local Mac machine.

> If you don't see an **Extension: Podman** entry under Preferences at all, your version may expose it under a different label, or it may just not be listed as a distinct preferences page — go straight to **Settings → Resources** instead and look for the remote connection there.

## 4. Access the app's UI

Once your containers are running (via Quadlet, `podman-compose`, or Podman Desktop), the Node UI is just a normal web app reachable from any device on the same network:

```
http://<pi-ip-or-hostname>:3000
```

That's the port published by `ui.container` (`PublishPort=3000:3000`). Get the Pi's IP with `hostname -I` on the Pi, or try `http://<hostname>.local:3000` (mDNS/Bonjour, usually works from a Mac).

If it doesn't load: confirm the container is actually running (`systemctl --user status ui.service` on the Pi, or `podman --connection rpi ps` from the Mac), and check for a firewall blocking port 3000 on the Pi.

## 5. Troubleshooting: Podman Desktop shows no containers

First isolate whether it's a Desktop bug or a real connection problem — run this on the Mac terminal:

```bash
podman system connection list      # confirms 'rpi' is registered
podman --connection rpi ps         # does the CLI see the containers?
```

**If the CLI shows your containers fine**, the connection itself is working and this is a Podman Desktop GUI issue. Check, in order:

1. **Settings → Preferences → Extension: Podman → Remote** is actually toggled on (easy to think it's on when it isn't).
2. **Restart Podman Desktop** after toggling — it often doesn't pick up connections added afterward without a restart.
3. **Confirm you're viewing the right connection** in the Containers/Resources view — Desktop can default to showing the local machine even when a remote connection exists.

**Known open bugs, as of early 2026** — if you've done all of the above and it still doesn't work, you may be hitting one of these unresolved Podman Desktop issues rather than a misconfiguration:

- [podman-desktop/podman-desktop#14869](https://github.com/podman-desktop/podman-desktop/issues/14869) — CLI sees remote containers correctly, but the Containers tab in the GUI stays empty.
- [podman-desktop/podman-desktop#15532](https://github.com/podman-desktop/podman-desktop/issues/15532) — after enabling the Remote option, the remote machine's toggle in Settings → Resources always shows as "OFF," and the Images/Containers views stay empty and unselectable, even though the CLI works.

If you hit either of these, the reliable path meanwhile is the CLI with `--connection rpi`, or `podman system connection default rpi` so you don't need the flag every time.

## 6. Quick reference

| Task | Command |
|---|---|
| List connections | `podman system connection list` |
| Switch default connection | `podman system connection default rpi` |
| Run a command on the Pi | `podman --connection rpi ps` |
| Run a command on the Mac's own VM | `podman --connection podman-machine-default ps` |
| Remove a connection | `podman system connection remove rpi` |

Containers, images, and Quadlet-managed services on the Pi are all visible through this connection — the Mac side is just the control plane, everything actually runs on the Pi.
