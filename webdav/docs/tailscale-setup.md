# Tailscale Setup

Extend your WebDAV server to be reachable from anywhere — not just your local network — using Tailscale's encrypted WireGuard mesh.

**Assumes the WebDAV server is running and working on your local network.** See [webdav-docker.md](webdav-docker.md) if not.

## What Tailscale does

Tailscale creates a WireGuard mesh VPN between your devices. Each device gets a stable private IP in the `100.x.x.x` range that works regardless of where you are. Traffic between devices is encrypted end-to-end and never passes through Tailscale's servers.

> [!NOTE]
> Tailscale's free personal plan supports up to 100 devices — more than enough for this setup.

## 1. Create a Tailscale account

Go to [tailscale.com](https://tailscale.com) and sign up. You can use a Google, GitHub, or Microsoft account, or a passkey.

## 2. Install on the Raspberry Pi

SSH into the Pi and run the official install script:

```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

Then start Tailscale and authenticate:

```bash
sudo tailscale up
```

This outputs a URL — open it in a browser, log in to your Tailscale account, and authorise the device. The Pi will appear in your [Tailscale admin console](https://login.tailscale.com/admin/machines).

Verify it's connected and get the Pi's Tailscale IP:

```bash
tailscale ip
# Returns something like: 100.x.x.x
```

## 3. Disable key expiry on the Pi

By default Tailscale requires periodic re-authentication, which would disconnect a headless server. For devices that should remain continuously connected, such as servers and Raspberry Pis, disable key expiry to avoid unnecessary disruptions.

In the [Tailscale admin console](https://login.tailscale.com/admin/machines):

1. Find your Pi in the machine list
2. Click the **⋯** menu next to it
3. Select **Disable key expiry**

## 4. Install on Mac

```bash
brew install tailscale
```

Or download from [tailscale.com/download](https://tailscale.com/download). Sign in with the same account — the Mac will appear in your tailnet automatically.

## 5. Install on iPhone

Install from the [App Store](https://apps.apple.com/app/tailscale/id1470499037). Sign in with the same account.

## 6. Test connectivity

From your Mac or iPhone, ping the Pi using its Tailscale IP:

```bash
ping 100.x.x.x
```

Then test the WebDAV server is reachable over Tailscale:

```bash
curl -u webdav:yourpassword http://100.x.x.x:8090/dav/
```

A directory listing confirms everything is working end-to-end.

## 7. Update Super Productivity sync settings

The WebDAV guide uses your Pi's local IP — update the Base URL to use the Tailscale IP instead so sync works from anywhere:

| Field            | Value                        |
| ---------------- | ---------------------------- |
| Sync provider    | WebDAV                       |
| Base URL         | `http://100.x.x.x:8090/dav/` |
| Username         | `webdav`                     |
| Password         | your password                |
| Sync Folder Path | `super-productivity`         |

Replace `100.x.x.x` with the Pi's Tailscale IP from step 2.

## Notes

- **Do not expose port 8090 on your router.** Tailscale is the only intended access path.
- **MagicDNS** — Tailscale optionally gives devices hostnames (e.g. `your-pi-name`) so you can use `http://your-pi-name:8090/dav/` instead of the IP. Enable it in the admin console under DNS → MagicDNS.
- **Always-on** — Tailscale starts automatically on boot on the Pi. No action needed after a reboot.
- **Auto-shutdown** — if your Pi shuts down on a cron schedule, Tailscale disconnects with it. Adjust or remove the shutdown job if you need always-on sync.
