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
MONITOR = "alsa_output.platform-XXXXXXXX.mailbox.stereo-fallback.monitor"
SENSITIVITY = 1800  # lower = more reactive; set to roughly peak_rms / 8
BRIGHTNESS = 0.08  # 0.0-1.0; Blinkt is very bright, keep low
NOISE_FLOOR = 300  # RMS below this is treated as silence

COLORS = [
    (0, 255, 0),  # LED 0 - green
    (0, 255, 0),  # LED 1 - green
    (50, 220, 0),  # LED 2
    (120, 200, 0),  # LED 3
    (200, 200, 0),  # LED 4 - yellow
    (255, 140, 0),  # LED 5 - orange
    (255, 60, 0),  # LED 6
    (255, 0, 0),  # LED 7 - red
]
# --- End configuration ---

env = os.environ.copy()
env["PULSE_RUNTIME_PATH"] = f"/run/user/{os.getuid()}/pulse"

proc = subprocess.Popen(
    [
        "parec",
        "--device=" + MONITOR,
        "--format=s16le",
        "--rate=44100",
        "--channels=1",
        "--latency-msec=20",
    ],
    stdout=subprocess.PIPE,
    env=env,
    bufsize=0,
)

# Reader thread - drains the pipe continuously, keeps only the latest chunk
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
