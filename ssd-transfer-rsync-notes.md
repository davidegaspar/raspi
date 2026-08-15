# SSD Transfer & rsync Notes

Notes from moving large files from a Pi's SD card to a USB-connected SSD.

## Mounting the SSD

Find the device and partition:

```bash
lsblk
sudo blkid /dev/sda2
```

Mount it:

```bash
sudo mkdir -p /mnt/ssd
sudo mount /dev/sda2 /mnt/ssd
```

- **ext4** — mounts as-is, supports Unix ownership/permissions natively.
- **exFAT** — needs `exfatprogs` (`sudo apt install exfatprogs`) for the mkfs/fsck tools. The in-kernel driver (Linux 5.4+) handles mounting; avoid `exfat-fuse` if it's present (`sudo apt remove exfat-fuse`) — it's the old FUSE driver and is much slower.
- **NTFS** — needs `ntfs-3g`.

exFAT has no concept of Unix ownership or permission bits — the mount just fakes read/write access via `fmask`/`dmask`. This matters for the rsync flags below.

A manual `mount` doesn't survive a reboot — only `/etc/fstab` entries do. Re-mount manually after every reboot unless an fstab entry is added.

## The rsync command

```bash
rsync -rlhtv --partial --progress --timeout=60 /path/to/sourcedir/ /mnt/ssd/destdir/
```

| Flag | Meaning |
|---|---|
| `-r` | Recursive |
| `-l` | Preserve symlinks as symlinks |
| `-h` | Human-readable sizes in output |
| `-t` | Preserve modification timestamps |
| `-v` | Verbose — list each file as it transfers |
| `--partial` | Keep partially-copied files on interruption instead of deleting them |
| `--progress` | Live per-file progress |
| `--timeout=60` | Abandon a stalled read/write after 60s instead of hanging indefinitely (useful with a failing source disk) |

**Deliberately excluded:** `-o` (owner) and `-g` (group), which `-a` (archive mode) normally includes. exFAT can't hold Unix ownership, so rsync's `chown`/`chgrp` calls fail with `EPERM` — this shows up as errors on dotfiles first since they sort alphabetically, but affects every file.

### Trailing slash matters

- `rsync ... /source/dir/ /dest/` — copies the *contents* of `dir` into `dest`.
- `rsync ... /source/dir /dest/` — copies `dir` itself, nested inside `dest`.

Use `--dry-run` first if unsure.

## Resuming / idempotency

rsync is idempotent: re-running the same command skips files that already match (by size + mtime) and resumes partial files rather than re-copying from scratch.

Retry loop for a flaky source disk:

```bash
for i in 1 2 3; do
  rsync -rlhtv --partial --progress --timeout=60 /path/to/sourcedir/ /mnt/ssd/destdir/ && break
done
```

Run this inside `tmux` (see `tmux-session-basics.md`) so it survives a dropped SSH connection.

## Handling read errors (bad sectors)

```
rsync: [sender] read errors mapping "file.zip": Input/output error (5)
ERROR: file.zip failed verification -- update discarded.
```

This means the *source* media is failing to read specific blocks — not an rsync or filesystem issue. If it's the boot/root SD card, treat this as urgent: it's a sign of card failure, not just a one-off bad file.

Re-run rsync first — marginal sectors sometimes succeed on retry. If the same file fails consistently:

**Exclude it and let the rest finish:**

```bash
rsync -rlhtv --partial --progress --timeout=60 --exclude='badfile.zip' /path/to/sourcedir/ /mnt/ssd/destdir/
```

**Attempt recovery with `ddrescue`** (works around bad sectors instead of failing on them):

```bash
sudo apt install gddrescue
sudo ddrescue -d /path/to/badfile.zip /mnt/ssd/destdir/badfile.zip /mnt/ssd/rescue.log
```

- `-d` — direct disk access, bypasses cache
- `rescue.log` — records which sectors succeeded/failed; re-run `ddrescue` later to retry only the failed regions

## Diffing source vs destination

After a run that didn't fully complete, find what's missing:

```bash
diff <(cd /path/to/sourcedir && find . -type f | sort) <(cd /mnt/ssd/destdir && find . -type f | sort)
```

Anything listed as source-only is what didn't make it across.

## Checking sizes

```bash
df -h /mnt/ssd                              # mount total/used/available
du -h --max-depth=1 /mnt/ssd | sort -h       # per-folder size, smallest to largest
```

## Diagnosing slow transfers

Rule out causes in this order:

1. **exFAT driver** — confirm `mount | grep <device>` shows `type exfat`, not `type fuseblk` (the slow FUSE driver).
2. **USB mode/negotiation** — `lsusb -t` should show `5000M` (USB 3.0), not `480M` (fell back to 2.0). `dmesg | grep -i uas` confirms whether UAS bound to the device.
3. **Known bad UAS chipsets** — some USB-SATA/NVMe bridges (e.g. VIA Labs VL715/716, seen in some Sabrent enclosures) have broken UAS on the Pi's xHCI controller. Fix by forcing BOT mode via a kernel quirk (see cmdline.txt warning below) — `usb-storage.quirks=VID:PID:u`. Confirm the actual VID:PID from `dmesg` before adding it.
4. **File count** — thousands of small files can tank throughput regardless of hardware, due to per-file open/stat/close overhead. `find dir -type f | wc -l`.
5. **Raw disk speed** — isolate rsync from hardware with `dd`:
   ```bash
   # Write test (destination)
   dd if=/dev/zero of=/mnt/ssd/testfile bs=1M count=1024 oflag=direct

   # Read test (source)
   dd if=/path/to/largefile of=/dev/null bs=1M iflag=direct
   ```
   `oflag=direct`/`iflag=direct` bypass the page cache for a real throughput number, not a burst into RAM.
6. **Pi 4 SD card ceiling** — even a healthy card in the onboard slot is capped around 20–45 MB/s (DDR50, ~50MB/s theoretical) due to the controller, not the card. A USB 3.0 card reader can hit 100MB/s+ with the same card. Anything well below ~20 MB/s on read points to card failure, not the controller ceiling.

## `cmdline.txt` warning

If editing `/boot/cmdline.txt` (or `/boot/firmware/cmdline.txt` on Bookworm) to add a `usb-storage.quirks` entry:

- The file must be a **single line**, space-separated, no line breaks.
- Always check the *current* content first (`cat /proc/cmdline` once booted, or the file directly) and only **append** — don't retype the line from memory.
- Verify the result before rebooting.
- A malformed line (e.g. a missing space, or a broken `root=`/`rootwait`) can prevent boot entirely, with no remote access to fix it — recovery requires pulling the SD card and editing it from another machine.

If it won't boot after an edit: pull the card, mount it on another machine, fix `cmdline.txt` there, re-insert, retry.
