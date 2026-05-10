# Blinkt! VU Meter for Raspberry Pi 4

A real-time audio VU meter that visualises desktop audio output on a [Pimoroni Blinkt!](https://shop.pimoroni.com/products/blinkt?variant=22408658695) LED strip connected to a Raspberry Pi 4.

Audio is captured from the PipeWire monitor source — whatever is playing through the 3.5mm phone jack is reflected live on the 8 LEDs, green through red.

---

## Requirements

- Raspberry Pi 4 running Raspberry Pi OS Bookworm (64-bit)
- [Pimoroni Blinkt!](https://shop.pimoroni.com/products/blinkt?variant=22408658695) connected to the GPIO header
- Python 3.13+

---

## Installation

### 1. System dependencies

```bash
sudo apt install portaudio19-dev pulseaudio-utils -y
```

`pulseaudio-utils` provides `parec`, which is used to tap into PipeWire's audio monitor. `portaudio19-dev` is needed to build PyAudio.

### 2. Python dependencies

```bash
pip install blinkt pyaudio audioop-lts --break-system-packages
```

> [!NOTE]
> `audioop` was removed in Python 3.13. `audioop-lts` is a drop-in replacement.

---

## Finding your monitor source

Run:

```bash
pactl list sources short
```

Look for a source with `.monitor` in the name, for example:

```
57  alsa_output.platform-XXXXXXXX.mailbox.stereo-fallback.monitor  PipeWire  s16le 2ch 48000Hz  RUNNING
```

Copy the full name — you'll need it in the script.

---

## Configuration

Open `run.py` and adjust these values at the top:

| Variable | Default | Description |
|---|---|---|
| `MONITOR` | _(your source name)_ | PipeWire monitor source name from `pactl` |
| `SENSITIVITY` | `1800` | Lower = more reactive. Set to roughly `peak_rms / 8` |
| `BRIGHTNESS` | `0.08` | LED brightness 0.0–1.0. Blinkt is very bright, keep low |
| `NOISE_FLOOR` | `300` | RMS below this is treated as silence |

### Calibrating sensitivity

To find the right `SENSITIVITY` for your setup, temporarily add a `print(rms)` line and play music at normal volume:

```python
rms = audioop.rms(data, 2)
print(rms)  # add this line temporarily
```

Note the peak values, then set `SENSITIVITY = peak / 8`. Remove the print line when done.

---

## The script

Save as `run.py`:

```python
try:
    import audioop
except ImportError:
    import audioop_lts as audioop

import subprocess
import signal
import sys
import os
import threading
import queue
from blinkt import set_pixel, show, clear

# --- Configuration ---
MONITOR     = "alsa_output.platform-XXXXXXXX.mailbox.stereo-fallback.monitor"
SENSITIVITY = 1800    # lower = more reactive; set to roughly peak_rms / 8
BRIGHTNESS  = 0.08    # 0.0-1.0; Blinkt is very bright, keep low
NOISE_FLOOR = 300     # RMS below this is treated as silence

COLORS = [
    (0, 255, 0),    # LED 0 - green
    (0, 255, 0),    # LED 1 - green
    (50, 220, 0),   # LED 2
    (120, 200, 0),  # LED 3
    (200, 200, 0),  # LED 4 - yellow
    (255, 140, 0),  # LED 5 - orange
    (255, 60, 0),   # LED 6
    (255, 0, 0),    # LED 7 - red
]
# --- End configuration ---

env = os.environ.copy()
env['PULSE_RUNTIME_PATH'] = f'/run/user/{os.getuid()}/pulse'

proc = subprocess.Popen(
    ['parec', '--device=' + MONITOR, '--format=s16le', '--rate=44100', '--channels=1', '--latency-msec=20'],
    stdout=subprocess.PIPE,
    env=env,
    bufsize=0
)

# Reader thread — drains the pipe continuously, keeps only the latest chunk
q = queue.Queue(maxsize=1)

def reader():
    while True:
        data = proc.stdout.read(512)
        try:
            q.get_nowait()  # discard any unread old chunk
        except queue.Empty:
            pass
        q.put(data)

t = threading.Thread(target=reader, daemon=True)
t.start()

def cleanup(signum, frame):
    clear()
    show()
    proc.terminate()
    sys.exit(0)

signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGHUP, cleanup)

current_level = 0

print("Running - Ctrl+C to stop")
try:
    while True:
        try:
            data = q.get(timeout=0.1)
        except queue.Empty:
            continue

        rms = audioop.rms(data, 2)

        if rms < NOISE_FLOOR:
            level = 0
        else:
            level = min(8, int((rms - NOISE_FLOOR) / SENSITIVITY))

        current_level = max(level, current_level - 2)

        clear()
        for i in range(current_level):
            set_pixel(i, *COLORS[i], brightness=BRIGHTNESS)
        show()

except KeyboardInterrupt:
    print("\nStopping...")
finally:
    clear()
    show()
    proc.terminate()
```

---

## Running

### From terminal

```bash
cd ~/blinkt
python3 run.py
```

Press `Ctrl+C` to stop. LEDs will clear on exit.

### From the desktop (double-click)

Create a `.desktop` launcher:

```bash
nano ~/Desktop/vu-meter.desktop
```

```ini
[Desktop Entry]
Name=VU Meter
Exec=python3 /home/YOUR_USERNAME/blinkt/run.py
Icon=audio-card
Terminal=true
Type=Application
```

```bash
chmod +x ~/Desktop/vu-meter.desktop
```

Double-click the icon on the desktop to launch. Closing the terminal window will cleanly stop the script and clear the LEDs.

---

## How it works

- `parec` taps the PipeWire monitor source — a virtual loopback of whatever audio is playing — with a 20ms latency buffer.
- A background thread drains the pipe continuously, keeping only the most recent 512-byte chunk to avoid buffer lag.
- The RMS value of each chunk is mapped to a number of LEDs (0–8), with a noise floor to suppress silence.
- LEDs decay by 2 steps per frame for a smooth but responsive fall-off.
- Signal handlers (`SIGTERM`, `SIGHUP`) ensure LEDs clear when the process is killed or the terminal is closed.
