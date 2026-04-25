# Raspberry Pi 4 — Fan Control Reference

## 1. Configure Fan Temperature

**Via raspi-config (recommended):**

1. Run `sudo raspi-config`
2. Go to **Performance Options → Fan**
3. Set GPIO pin to `14`
4. Set temperature threshold (recommended: `70`)
5. Reboot when prompted

**Via config.txt directly:**

1. Open the file:
   ```bash
   sudo nano /boot/firmware/config.txt
   # older OS versions:
   sudo nano /boot/config.txt
   ```
2. Add or edit this line:
   ```
   dtoverlay=gpio-fan,gpiopin=14,temp=70000
   ```
   > `temp` is in millidegrees — multiply °C by 1000
3. Save (`Ctrl+O`), exit (`Ctrl+X`), then reboot:
   ```bash
   sudo reboot
   ```

---

## 2. Check Temperature

**Single reading:**
```bash
vcgencmd measure_temp
```

**Live reading (updates every 2 seconds):**
```bash
watch -n 2 vcgencmd measure_temp
```

**Check for throttling:**
```bash
vcgencmd get_throttled
```
| Value | Meaning |
|-------|---------|
| `0x0` | All good |
| `0x50000` | Previously throttled (not currently) |
| `0x80008` | Currently throttling |

---

## 3. Temperature Reference

> **Recommended setting: `75000` (75°C)** — just below the default of 80°C. At this threshold the fan kicks in promptly, temperature drops rapidly, and the CPU never throttles.

| Range | Status |
|-------|--------|
| Under 60°C | Cool, fan not needed |
| 60–70°C | Normal under load |
| 70–80°C | Warm, fan should be running |
| Above 80°C | Throttling kicks in — too hot |

---

## 4. Graph Temperature Over Time

**Option A — stressberry (stress test + graph):**

1. Install:
   ```bash
   pip3 install stressberry matplotlib
   ```
2. Run stress test and record data:
   ```bash
   stressberry-run out.dat
   ```
3. Generate graph:
   ```bash
   stressberry-plot out.dat -o plot.png
   ```
4. Copy graph to your local machine:
   ```bash
   scp pi@<your-pi-ip>:~/plot.png .
   ```

**Option B — log to file and plot with gnuplot:**

1. Install gnuplot:
   ```bash
   sudo apt install gnuplot
   ```
2. Start logging (runs until `Ctrl+C`):
   ```bash
   while true; do echo "$(date +%s) $(vcgencmd measure_temp | grep -o '[0-9.]*')"; sleep 5; done >> temp_log.txt
   ```
3. Plot the log:
   ```bash
   gnuplot -p -e "plot 'temp_log.txt' using 1:2 with lines title 'CPU Temp'"
   ```
