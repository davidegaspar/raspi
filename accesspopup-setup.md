# Raspberry Pi 4 — Fallback WiFi Hotspot (AccessPopup)

Concise steps to replace Comitup with AccessPopup on the Pi 4, avoiding the brcmfmac AP+scan conflict that broke Comitup on this hardware. See `pi-fallback-hotspot-requirements.md` for the original requirements and blocker.

## Why AccessPopup

Comitup fails on this hardware because the onboard brcmfmac chip can't scan for networks while running in AP mode — a driver/firmware limitation, not a Comitup bug. AccessPopup avoids the conflict by doing a full sequential swap (deactivate AP → scan as station → reconnect or reactivate AP) via NetworkManager on a timer, rather than scanning in the background while hostapd stays up.

- FOSS (GPL-3.0), self-hosted, no telemetry or account
- Built for NetworkManager + systemd — matches this Pi's stack directly
- Skips the switch entirely if a client is already connected to the AP, so it doesn't drop active sessions

## 1. Install AccessPopup

```bash
sudo apt update
sudo apt install -y git
git clone https://github.com/RaspberryConnect/AccessPopup.git
cd AccessPopup
sudo chmod +x ./installconfig.sh
sudo ./installconfig.sh
```

Menu options used:

| Option | What it does |
|---|---|
| 1 | Install AccessPopup, start the 2-minute checks |
| 2 | Change AP SSID and password (default `AccessPopup` / `1234567890` — change both) |
| 3 | Change AP IP address (default `192.168.50.5`) |
| 6 | Change hostname (only useful once connected to a WiFi network, not the AP) |
| 9 | Exit |

WPA2-AES cipher (`proto=rsn`, `pairwise=ccmp`, `group=ccmp`) was already the default on this install — no manual hardening needed. Confirmed with:

```bash
sudo cat /etc/NetworkManager/system-connections/AccessPopup.nmconnection
```

## 2. Test

Force AP mode (also stops the timer, so it stays up for testing):

```bash
sudo accesspopup -a
```

Connect from a phone/laptop and check:
- SSH works: `ssh <user>@192.168.50.5`
- Real DHCP lease, not a self-assigned `169.254.x.x` address
- No "weak security" warning
- Connected clients can reach each other

Watch for the original blocker while the AP sits idle:

```bash
sudo dmesg -w | grep -i brcmf
```

`brcmf_escan_timeout` / `vndr ie set error : -52` bursts would mean the check is scanning while the AP is still up, not tearing it down first — not seen on this setup.

Return to normal switching:

```bash
sudo accesspopup
```

Same result as rebooting, or using installer option 4 ("Live Switch between: Network WiFi <> Access Point").

## Notes

**"Is this a local access point? n"** — a status line the script prints after each run, not a prompt. It reports whether the now-active profile is the AP one. `n` after switching to a home network is correct — it confirms the switch worked.

**Internet sharing** — AP clients only get internet if an Ethernet cable is plugged into the Pi with a working connection; the WiFi radio can't provide uplink while it's busy running the AP. No Ethernet, no internet for AP clients — but they can still reach the Pi and each other. Devices on the Ethernet side can reach the Pi but not the AP clients (one-way). A USB WiFi dongle doesn't change this — AP clients still can't route through whatever network the dongle connects to.

**Bad known-network passwords** — if a saved WiFi profile has the wrong password, NetworkManager still lists it as "known," so every 2-minute check tries it, fails, and disrupts the AP. Fix or delete the profile via installer option 5.

**USB dongle caveat** — if one's added later, WiFi profiles bound to `wlan0` need recreating against the dongle's interface name.

## References

- [AccessPopup — GitHub](https://github.com/RaspberryConnect/AccessPopup)
- [AccessPopup — RaspberryConnect.com](https://www.raspberryconnect.com/projects/65-raspberrypi-hotspot-accesspoints/203-automated-switching-accesspoint-wifi-network)
- `pi-fallback-hotspot-requirements.md` — original requirements and Comitup blocker
