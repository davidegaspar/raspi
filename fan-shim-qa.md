# Raspberry Pi — Fan SHIM: Q&A

## Software setup

```bash
sudo apt update
sudo apt install git -y

git clone https://github.com/pimoroni/fanshim-python
cd fanshim-python
sudo ./install.sh
```

Then install the automatic temperature-triggered service:

```bash
cd examples
sudo ./install-service.sh --on-threshold 65 --off-threshold 55 --delay 2
```

`--on-threshold`/`--off-threshold` are °C (Pimoroni's own tested defaults), `--delay` is seconds between temp checks.

Stop/disable later:

```bash
sudo systemctl stop pimoroni-fanshim.service
sudo systemctl disable pimoroni-fanshim.service
```

## What does the LED mean?

Fades green (cool) → red (hot) as CPU temperature changes — it's a temperature indicator only, not a mode indicator. Same behaviour in both automatic and manual mode.

## Does the button do anything?

- **Long press** — toggles automatic mode on/off
- **Short press** (only when in manual mode) — toggles the fan
- On hold, the LED flashes blue 3× as acknowledgment the press registered — same flash regardless of which direction the mode is switching.

## How do I tell what mode it's in?

No persistent state file and no distinct LED colour for manual vs automatic — confirmed by reading `examples/automatic.py`: mode is held in an in-memory `armed` boolean, only ever exposed via a `--verbose` flag that prints a line like:

```
Current: 42.10 Target: 55.00 Freq 1.50 Automatic: True On: False
```

Not enabled by default in the systemd service. `install-service.sh` doesn't accept a `--verbose` flag (it only knows `--preempt`/`--noled`/`--nobutton`/`--on-threshold`/`--off-threshold`/`--low-temp`/`--high-temp`/`--delay`/`--brightness`/`--venv`/`--extended-colours` — anything else gets rejected), so add it via a systemd drop-in instead.

`sudo systemctl edit pimoroni-fanshim.service` opens `$EDITOR` (often nano over SSH) on a temp file — easy to end up with an empty/broken override if the save sequence isn't followed exactly (`Ctrl+O`, `Enter`, `Ctrl+X` in nano) or if a long pasted line gets auto-wrapped by the terminal into extra broken lines. More reliable to write the drop-in directly, one short line at a time so nothing gets mangled on paste:

```bash
sudo -i
cd /etc/systemd/system/pimoroni-fanshim.service.d   # mkdir -p first if missing
rm -f override.conf
echo '[Service]' >> override.conf
echo 'ExecStart=' >> override.conf
echo 'ExecStart=/usr/bin/python3 -u \' >> override.conf
echo '/path/to/automatic.py \' >> override.conf
echo '--on-threshold 65 --off-threshold 55 \' >> override.conf
echo '--delay 2 --verbose' >> override.conf
cat -A override.conf   # every continuation line should end in \$ except the last
```

Notes:
- `ExecStart=` (blank line) before the new `ExecStart=` is required — it clears the original command. Skipping it causes `Refusing... more than one ExecStart=` on restart.
- `-u` forces unbuffered Python stdout — without it, `print()` output sits in a buffer and never reaches the journal.
- Trailing `\` on continuation lines is systemd's own line-continuation syntax; without it you get `Missing '=', ignoring line` errors.

Then:

```bash
systemctl daemon-reload
systemctl restart pimoroni-fanshim.service
systemctl cat pimoroni-fanshim.service   # confirm the merged unit looks right
exit
sudo journalctl -u pimoroni-fanshim.service -f
```

## How do I check the current temp?

```bash
vcgencmd measure_temp
# or
cat /sys/class/thermal/thermal_zone0/temp   # millidegrees — divide by 1000
```

## Why do the two temp commands differ by ~1°C?

Normal, not a bug. Same physical sensor, two independent readers: `vcgencmd` asks the closed-source VideoCore firmware directly; `/sys/class/thermal/thermal_zone0/temp` comes from the Linux kernel's own thermal driver. Slightly different conversion algorithms from raw ADC value → temperature account for the gap.

## Fan not starting after reboot — how to debug

Work through these in order:

1. **Is the service actually enabled and running?**
   ```bash
   sudo systemctl status pimoroni-fanshim.service
   sudo systemctl is-enabled pimoroni-fanshim.service
   sudo journalctl -u pimoroni-fanshim.service -b   # this boot's log only
   ```
   If `is-enabled` says `disabled`, that alone explains it — `sudo systemctl enable --now pimoroni-fanshim.service`.

2. **Turn on `--verbose`** (see "How do I tell what mode it's in?" above) and watch the live log while temp is above the on-threshold:
   ```bash
   sudo journalctl -u pimoroni-fanshim.service -f
   ```
   Look for a line like `Current: 68.10 Target: 65.00 Freq 1.50 Automatic: True On: True`.

3. **Split software vs. hardware based on what that line says:**
   - `On: False` even though current temp is above the threshold → logic/config problem — double check the `--on-threshold`/`--off-threshold` values actually in the running `ExecStart` (`systemctl cat pimoroni-fanshim.service`), not just what you think you set.
   - `On: True` but the fan doesn't physically spin → hardware problem, not software. Confirmed cause here: the fan ran fine once nudged by hand and stopped cleanly when the code turned it off — a worn/sealed hydraulic bearing that can't self-start from rest but works once moving. See "Fan spec (for replacement)" below.

## Fan spec (for replacement)

30mm 5V DC fan, sealed hydraulic bearing, 2-wire (no PWM/tach), JST PH2.0 connector — AVC DATA0307R5H-002 (or equivalent 3007 fan).

| Spec | Value |
|---|---|
| Dimensions | 30 × 30 × 7mm |
| Voltage | 5V DC |
| Current | 0.13A |
| Power | 0.65W |
| Speed | ~7,200 RPM |
| Bearing | Hydraulic (sealed — not lubricatable/serviceable) |
| Wires | 2 (power/ground, no tach/PWM) |

Symptom of a worn/failing bearing: fan runs fine once spinning and stops cleanly on command, but won't self-start from rest without a manual nudge. Not fixable (sealed bearing) — replace the fan.

## Battery drain — fan on vs off, hot vs cold

Fan (AVC DATA0307R5H-002, per manufacturer spec):

| State | Draw |
|---|---|
| Off | ~0mA (GPIO cuts power entirely) |
| On | ~130mA @ 5V (0.65W) |

Ambient temperature doesn't meaningfully affect this — draw is a function of voltage/RPM, not air temperature. What *does* change with heat is the Pi's own SoC draw (separately from the fan) — often 600mA–1.2A+ under full load vs idle.

## Does cooling the CPU during load conserve battery?

Generally no — slight net cost, not a saving, for sustained loads. Thermal throttling exists specifically to *cut* power draw when hot (lower clock, some voltage reduction), so an uncooled throttled Pi draws less than a cooled one running full speed plus the fan's own ~130mA overhead.

Exception: finite/bursty tasks can benefit from "race to idle" — finishing faster at full clock lets the CPU idle sooner, which can net out ahead if the time saved outweighs the fan's overhead. Pi throttling steps are fairly mild, so the effect is usually small.
