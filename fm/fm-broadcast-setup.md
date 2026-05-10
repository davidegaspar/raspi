# FM Browser Broadcast Station — Project Setup

Stream audio from a web browser to an FM transmitter, controlled remotely from any laptop via VNC.

---

## Hardware

| Item | Notes |
|---|---|
| Raspberry Pi 4 4GB | Main compute unit |
| Official Raspberry Pi USB-C Power Supply (5V 3A) | Do not use cheap/PD chargers |
| MicroSD card (16GB+, Class 10) | OS storage |
| Walfront DSP & PLL FM Transmitter Module 87–108MHz | FM broadcast module |
| USB-A to Micro-USB cable | Pi → FM module (audio + optional power) |
| USB wall charger (any, 5V) + Micro-USB cable | Clean separate power for FM module (recommended) |
| FM antenna, 75cm rod | Connect to ANT port on module |
| Ferrite bead (optional) | Fit on USB cable to reduce noise interference |

> [!NOTE]
> Power the FM module from a separate USB wall charger rather than the Pi's USB port for cleaner audio. Use the Pi's USB port for audio data only (USB audio mode), or use the module's 3.5mm LINE input instead.

---

## Software

| Software | Purpose |
|---|---|
| Raspberry Pi OS (64-bit, with Desktop) | Operating system |
| Raspberry Pi Imager | Flash OS to SD card |
| wayvnc | VNC server for Wayland (pre-installed on Pi OS) |
| TigerVNC Viewer | VNC client for macOS and Windows — open source, GPL |
| Chromium | Browser for audio playback (pre-installed on Pi OS) |

---

## Step 1 — Flash the OS

1. Download and open [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Select **Raspberry Pi OS (64-bit)** with Desktop
3. Click the gear icon ⚙️ and configure:
   - Hostname: `raspberrypi`
   - Enable SSH
   - Set username and password
   - Set your WiFi SSID and password
4. Flash to your MicroSD card and insert into the Pi

---

## Step 2 — First Boot & System Setup

SSH into the Pi from your laptop:

```bash
ssh YOUR_USERNAME@YOUR_PI.local
```

Update the system:

```bash
sudo apt update && sudo apt upgrade -y
```

Confirm the Pi is running Wayland (required for wayvnc):

```bash
loginctl show-session $(loginctl | grep YOUR_USERNAME | awk '{print $1}') -p Type
```

Look for `Type=wayland` in the output — ignore any `tty` or `unspecified` lines, those are SSH sessions. Raspberry Pi OS with Desktop on Pi 4 uses Wayland by default.

---

## Step 3 — Configure wayvnc

wayvnc is pre-installed on Raspberry Pi OS with Desktop. Set a password:

```bash
sudo nano /etc/wayvnc/config
```

Replace the contents with:

```
use_relative_paths=true
address=0.0.0.0
enable_auth=true
username=YOUR_USERNAME
password=YOUR_PASSWORD
```

Enable and start wayvnc:

```bash
sudo systemctl enable wayvnc
sudo systemctl restart wayvnc
```

Confirm it's listening on port 5900:

```bash
sudo ss -tlnp | grep 5900
```

Then reboot:

```bash
sudo reboot
```

---

## Step 4 — Install TigerVNC Viewer & Connect

TigerVNC Viewer is open source (GPL), no telemetry, no account required. Latest release is **1.16.2**, download from:
👉 [sourceforge.net/projects/tigervnc/files/stable/1.16.2](https://sourceforge.net/projects/tigervnc/files/stable/1.16.2)
👉 [github.com/TigerVNC/tigervnc/releases](https://github.com/TigerVNC/tigervnc/releases) (fallback)

### macOS

1. Download `TigerVNC-1.16.2.dmg` from the link above
2. Open the `.dmg` and drag **TigerVNC Viewer** to your Applications folder
3. On first launch, right-click → **Open** to bypass Gatekeeper
4. Enter `YOUR_PI.local:5900` in the address field and click **Connect**
5. Enter the username and password set in `/etc/wayvnc/config`

### Windows

1. Download `tigervnc64-1.16.2.exe` (64-bit installer) from the link above
2. Run the installer — no account or licence required
3. Enter `YOUR_PI.local:5900` in the address field and click **Connect**
4. Enter the username and password set in `/etc/wayvnc/config`

> [!NOTE]
> macOS built-in Screen Sharing does not work with wayvnc. Always use TigerVNC Viewer.

---

## Step 5 — Connect the FM Module

### USB audio mode (recommended)

1. Connect FM module to Pi USB-A port via USB-A to Micro-USB cable
2. Power module separately from a USB wall charger (Micro-USB)
3. The Pi will detect it as audio device **CD002**
4. On the Pi desktop, set **CD002** as the default audio output device:
   ```bash
   # Or set via Pi OS audio settings in the taskbar
   pactl set-default-sink <CD002-sink-name>
   ```

### LINE input mode (alternative)

1. Connect a 3.5mm male-to-male cable from Pi's headphone jack to FM module LINE input
2. Power FM module from a USB wall charger
3. Force Pi audio to the headphone jack:
   ```bash
   sudo raspi-config  # Advanced → Audio → Force 3.5mm jack
   ```

---

## Step 6 — Set FM Module Frequency

Use the **FREQ+/FREQ−** buttons on the FM module to set your broadcast frequency. Tune a nearby FM radio to the same frequency to confirm audio.

**Button reference:**

| Button | Short press | Long press |
|---|---|---|
| VOL+/− | ±1 volume | Continuous |
| FREQ+/− | ±0.1 MHz | ±1.0 MHz |
| Mute | Toggle mute | — |

---

## Step 7 — Antenna

Connect a **75cm rod antenna** to the **ANT port** on the FM module. Keep the area around it clear of obstacles. Transmission range is approximately 100m in open space.

---

## Day-to-Day Use

1. Pi boots with wayvnc running automatically
2. Open TigerVNC Viewer and connect to `YOUR_PI.local:5900`
3. Open Chromium and navigate to any audio source (Spotify Web, BBC Sounds, YouTube, radio streams, etc.)
4. Audio plays through the FM module
5. Tune any nearby FM radio to your chosen frequency

---

## Power Notes

- Use the **official Raspberry Pi USB-C power supply** — the Pi 4 is sensitive to underpowered or PD-negotiating chargers
- Power the **FM module separately** from a standard USB wall charger for cleaner audio
- The FM module draws only **35mA** — any USB charger is sufficient
- Optionally add a **ferrite bead** to the USB audio cable to reduce switching noise

---

## FM Module Quick Reference

| Spec | Value |
|---|---|
| Frequency range | 87.0–108.0 MHz |
| Output power | 100mW |
| Audio response | 50Hz–18kHz |
| Power input | 5V via Micro-USB, 35mA |
| Antenna | 75cm rod |
| Audio inputs | USB (CD002), LINE (3.5mm), MIC (built-in) |
| Input switching | Automatic |
