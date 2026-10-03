# SSD Transfer & rsync Notes

Notes from moving large files onto a USB-connected external disk using a Pi — either off the Pi's own SD card, or disk-to-disk with both drives attached to the Pi. Covers identifying the disk, wiping and formatting it as exFAT, mounting it, copying with rsync, and diagnosing what goes wrong.

**exFAT or ext4?** Use exFAT if the disk also has to mount on macOS or Windows — that's its only real advantage. Use ext4 for a Pi-only disk: it's faster, and it preserves Unix ownership and permissions, which exFAT cannot (see the rsync flag notes below).

## Identifying the disk

`lsblk` and `blkid` are Linux-only — on a Mac use `diskutil` instead. Device names differ too: the same disk is `/dev/sda` on the Pi and `/dev/diskN` on the Mac.

**On the Pi (Linux):**

```bash
lsblk -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINTS   # tree of disks and partitions
sudo blkid /dev/sda1                          # UUID, label, filesystem type
```

**On the Mac (macOS):**

```bash
diskutil list external        # external disks only, e.g. /dev/disk4 with partitions disk4s1, disk4s2
diskutil info /dev/disk4      # size, model, filesystem, UUID — confirm it's the right disk
```

`/dev/disk0` and the other internal disks are the Mac itself. macOS renumbers external disks as they're attached, so re-run `diskutil list` right before any destructive command.

On the Pi, `sda`/`sdb` are USB disks; `mmcblk0` is the onboard SD card. Confirm the size matches the disk you mean before running anything destructive — device letters are assigned in probe order and can move between boots.

A disk that was formatted on a Mac shows **two** partitions: a 200MB `vfat` one labelled `EFI`, plus the real data partition. macOS Disk Utility writes an EFI System Partition onto every GPT disk it initialises, even a data-only drive that will never boot. It's empty and harmless — but it means the data lives on partition **2**, so mount `sdb2`, not `sdb1`. A disk partitioned on Linux with `parted` (below) has just the one partition.

Throughout this file: `/dev/sda` is the **whole disk**, `/dev/sda1` is a **partition on it**. Wiping and partitioning target the disk; formatting and mounting target the partition. Mixing them up is the usual way to destroy the wrong thing.

## Two disks at once (disk-to-disk)

**Power is the first thing to get right.** All four USB ports on a Pi 4 share a budget of roughly 1.2A. Two bus-powered drives — spinning disks especially — can brown out mid-transfer, which surfaces as I/O errors or a disk silently dropping off the bus hours in. Use a powered hub or self-powered enclosures unless both are SSDs. `dmesg | tail -20` after attaching both shows resets and enumeration failures.

**Mount the source read-only.** There is no reason for the source to be writable during a copy, and `ro` removes any chance of damaging the disk you're migrating away from:

```bash
sudo mkdir -p /mnt/src
sudo mount -o ro /dev/sdb2 /mnt/src
```

The mount point must already exist — `mount` fails with `mount point does not exist` rather than creating it.

That works as-is for ext4 and exFAT. For an **NTFS** source, install `ntfs-3g` first. Prefer the in-kernel driver by mounting with `-t ntfs3` (check it exists: `grep ntfs3 /proc/filesystems`); confirm with `mount | grep sdb2` that you got `type ntfs3` and not `type fuseblk`, which is the much slower FUSE path — the same trap as exFAT. An NTFS disk last used on Windows with hibernation or Fast Startup is flagged dirty and won't mount read-write; `ro` sidesteps that entirely, which is another reason to use it.

## Wiping and formatting as exFAT

> **Destructive.** Every command in this section erases data, with no confirmation prompt and no undo. Re-check the device with `lsblk` (Pi) or `diskutil list` (Mac) immediately before each one.

Either machine can do it: steps 1–5 below run **on the Pi**; to do it **on the Mac** in one command, see "Formatting from macOS instead".

Install the tools (`exfatprogs` provides `mkfs.exfat` and `fsck.exfat`; the kernel handles mounting on its own):

```bash
sudo apt install exfatprogs
```

**1. Unmount anything on the disk** — formatting a mounted filesystem corrupts it:

```bash
sudo umount /dev/sda1        # repeat per mounted partition
lsblk /dev/sda               # MOUNTPOINTS column should now be empty
```

**2. Wipe the existing partition table and signatures:**

```bash
sudo wipefs -a /dev/sda      # whole disk — removes all filesystem/partition-table signatures
```

`wipefs` only clears the signatures that make a filesystem recognisable; the underlying data blocks remain until overwritten. That's fine for reuse, but it is *not* secure erase — for that, `sudo dd if=/dev/zero of=/dev/sda bs=4M status=progress` (hours on a large disk).

**3. Create a fresh partition table and one partition spanning the disk:**

```bash
sudo parted /dev/sda --script mklabel gpt mkpart primary 0% 100%
sudo partprobe /dev/sda      # re-read the table so /dev/sda1 appears
lsblk /dev/sda
```

Use `mklabel msdos` instead of `gpt` only if the disk has to work with something old that can't read GPT (cameras, older TVs); GPT is right for Mac/Windows/Linux.

**4. Format the partition as exFAT:**

```bash
sudo mkfs.exfat -L MyDisk /dev/sda1
```

- `-L` sets the volume label (what macOS/Windows show as the disk name).
- This is a *quick* format — it writes metadata only and takes seconds regardless of disk size. `-f` (`--full-format`) zeroes the entire disk instead and takes hours; only worth it if the old contents genuinely need to be gone.
- `-c` sets cluster size (e.g. `-c 1M`). The default is fine; a larger cluster helps only on disks holding a few very large files.

**5. Confirm the result:**

```bash
sudo blkid /dev/sda1         # should report TYPE="exfat" and the new UUID
```

### Checking and repairing an exFAT filesystem

The filesystem must be **unmounted** first:

```bash
sudo fsck.exfat -n /dev/sda1   # check only, change nothing
sudo fsck.exfat -p /dev/sda1   # repair automatically where it's safe to do so
sudo fsck.exfat -y /dev/sda1   # repair, answering yes to everything
```

Worth running after any unclean removal — exFAT has no journal, so a disk yanked mid-write can be left inconsistent with no automatic recovery.

### Formatting from macOS instead

**On the Mac (macOS)** — `diskutil eraseDisk` replaces all five Pi steps (unmount, wipe, partition, format) in one command:

```bash
diskutil list external                               # find the disk identifier
diskutil info /dev/disk4                             # confirm size/model
diskutil eraseDisk ExFAT MyDisk GPT /dev/disk4       # erases the WHOLE disk
diskutil eject /dev/disk4                            # flush and detach before unplugging
```

Use `/dev/diskN` (the whole disk), not `/dev/diskNsM` (a partition), and double-check the identifier — macOS renumbers disks as they're attached.

A GPT disk formatted this way gets the extra 200MB `EFI` partition described under "Identifying the disk", so on the Pi the data partition is `sdX2`, not `sdX1`.

## Mounting

```bash
sudo mkdir -p /mnt/ssd
sudo mount /dev/sda1 /mnt/ssd
```

- **ext4** — mounts as-is, supports Unix ownership/permissions natively.
- **exFAT** — the in-kernel driver (Linux 5.4+) handles mounting; `exfatprogs` is only needed for the mkfs/fsck tools. Avoid `exfat-fuse` if it's present (`sudo apt remove exfat-fuse`) — it's the old FUSE driver and is much slower.
- **NTFS** — needs `ntfs-3g`.

exFAT has no concept of Unix ownership or permission bits — the mount just fakes them from options given at mount time. This matters for the rsync flags below.

Mounted with no options, an exFAT volume ends up owned by `root` and effectively read-only for the `pi` user. To make it writable without `sudo`:

```bash
sudo mount -t exfat -o uid=$(id -u),gid=$(id -g),umask=022 /dev/sda1 /mnt/ssd
```

| Option | Effect |
|---|---|
| `uid=` / `gid=` | Owner and group every file/directory is *reported* as (nothing is stored on disk) |
| `umask=022` | Owner writable, others read-only; use `umask=000` for a disk shared by several users |
| `fmask=` / `dmask=` | Same, but set separately for files and directories |

### Mounting automatically at boot

A manual `mount` doesn't survive a reboot — only `/etc/fstab` entries do. Get the UUID first:

```bash
sudo blkid /dev/sda1         # exFAT UUIDs are short, e.g. UUID="A1B2-C3D4"
sudo cp /etc/fstab /etc/fstab.backup
sudo nano /etc/fstab
```

Add one line:

```
UUID=A1B2-C3D4  /mnt/ssd  exfat  defaults,uid=1000,gid=1000,umask=022,nofail,x-systemd.device-timeout=10  0  0
```

- **Mount by `UUID=`, not `/dev/sda1`** — device letters depend on probe order, so a second USB disk can silently take the name and mount the wrong volume.
- **`nofail` is not optional here.** Without it, the Pi refuses to finish booting when the disk isn't attached — and there's no SSH access to fix it. `x-systemd.device-timeout=10` caps the wait at 10s instead of 90s.
- The final `0 0` disables dump and boot-time fsck; exFAT isn't checked at boot.

Test before rebooting, while you still have a shell:

```bash
sudo systemctl daemon-reload
sudo umount /mnt/ssd 2>/dev/null
sudo mount -a               # must complete silently
findmnt /mnt/ssd            # confirm options took effect
```

### Unmounting safely

exFAT writes are buffered; pulling the cable before the cache flushes is what corrupts these disks.

**On the Pi (Linux):**

```bash
sync                        # flush pending writes
sudo umount /mnt/ssd
```

**On the Mac (macOS):**

```bash
diskutil unmount /Volumes/MyDisk     # one volume
diskutil unmountDisk /dev/disk4      # every volume on the disk, incl. the EFI partition
```

If it reports "target is busy" (Pi) or "Unmount failed / in use" (Mac), find what's holding it open — usually a shell sitting in the directory:

```bash
sudo lsof +f -- /mnt/ssd             # Pi
sudo lsof /Volumes/MyDisk            # Mac — given a mount point, lists every open file on that volume
```

On the Mac, Spotlight (`mds`) indexing a newly attached disk is a common culprit. `diskutil unmount force` exists but drops whatever the holder was writing — close the process instead.

Confirm nothing is still mounted before unplugging anything:

```bash
# Pi
lsblk -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINTS   # MOUNTPOINTS empty for every partition
findmnt /mnt/ssd                              # no output, exit 1 = not mounted

# Mac
mount | grep /Volumes/MyDisk                  # no output = not mounted
diskutil list external                        # disk still listed, but no volume mounted
```

A successful `umount` / `diskutil unmount` has already flushed the cache — both sync before releasing the filesystem, so there's no window where a disk is unmounted but still writing. The explicit `sync` above is belt-and-braces.

Optionally power the drive down before pulling the cable, which parks the heads on a spinning disk:

```bash
sudo udisksctl power-off -b /dev/sda          # Pi
diskutil eject /dev/disk4                     # Mac — unmounts everything first if needed, then detaches
```

The device disappears from `lsblk` (Pi) or `diskutil list` (Mac) afterwards — that absence is the confirmation.

### Before starting the copy

Confirm the destination is genuinely writable — an exFAT volume mounted without `uid`/`umask` is root-owned and will fail partway in:

```bash
findmnt /mnt/ssd                      # options should show your uid and type exfat
touch /mnt/ssd/.probe && rm /mnt/ssd/.probe && echo writable
```

Then size it up:

```bash
du -sh --apparent-size /mnt/src       # real content size
find /mnt/src -type f | wc -l         # file count — thousands of small files will be slow
df -h /mnt/ssd                        # destination free space
```

Use `--apparent-size`; plain `du` reports disk-block usage, which legitimately differs between filesystems and will mislead you comparing an NTFS or ext4 source against an exFAT destination.

## The rsync command

One canonical invocation — everything else in this file is a flag added to it, not a different command:

```bash
rsync -rlht --partial --modify-window=1 --timeout=60 \
      --info=progress2 --log-file=$HOME/rsync.log \
      /mnt/src/ /mnt/ssd/
```

| Flag | Meaning |
|---|---|
| `-r` | Recursive |
| `-l` | Preserve symlinks as symlinks |
| `-h` | Human-readable sizes |
| `-t` | Preserve modification timestamps — **required** for re-runs to skip completed files |
| `--partial` | Keep partially-copied files on interruption instead of deleting them |
| `--modify-window=1` | Tolerate a 1s mtime difference — see below, mandatory for exFAT/FAT destinations |
| `--timeout=60` | Abandon a stalled read/write after 60s instead of hanging (useful with a failing source disk) |
| `--info=progress2` | One aggregate progress line — total transferred, rate, percent, ETA |
| `--log-file=` | Clean per-file record, kept separate from the terminal display |

**`--modify-window=1` is not optional on exFAT.** FAT-family filesystems store timestamps at 2-second resolution, so a file written from a source with finer granularity comes back with an mtime that differs by up to a second. Without the window, rsync reads that as "changed" and recopies the entire dataset on every re-run — which silently destroys the idempotency the rest of this workflow depends on.

**Deliberately excluded:** `-o` (owner) and `-g` (group), which `-a` (archive mode) normally includes. exFAT can't hold Unix ownership, so rsync's `chown`/`chgrp` calls fail with `EPERM` — this shows up as errors on dotfiles first since they sort alphabetically, but affects every file. `-a` also implies `-t`, so when dropping `-a` you must add `-t` back explicitly.

### Flags to add for specific situations

| Situation | Add |
|---|---|
| Unsure what will land where | `--dry-run` (with `-v`, since progress2 shows nothing useful on a dry run) |
| Want per-file output instead of one aggregate line | `-v --progress`, drop `--info=progress2` |
| A specific file fails on a bad sector | `--exclude='badfile.zip'` |
| Destination must mirror source exactly, including deletions | `--delete` — destructive, always `--dry-run` it first |
| Source disk is failing and stalls | lower `--timeout`, then see bad sectors below |
| Resuming a run that was interrupted | nothing — re-run the identical command |
| Destination can't store the source's timestamps | `--size-only` — see "Files that never converge" |

### Trailing slash matters

- `rsync ... /mnt/src/ /mnt/ssd/` — copies the *contents* of `src` into `ssd`.
- `rsync ... /mnt/src /mnt/ssd/` — copies `src` itself, nested as `/mnt/ssd/src/`.

### Disk-to-disk on the Mac instead

**On the Mac (macOS)** — with both disks attached, they mount under `/Volumes` automatically (`ls /Volumes` for the real names), so there's nothing to mount:

```bash
caffeinate -i rsync -rlht --partial --modify-window=1 --progress \
  "/Volumes/OldDisk/MyFolder" "/Volumes/NewDisk/"
```

- Copy only: the source is just read, and with no `--delete` nothing on the destination is removed. A destination file at the same path that differs *is* overwritten.
- `caffeinate -i` keeps the Mac from sleeping mid-copy. Quote the paths — volume names often contain spaces.
- `--progress` instead of `--info=progress2`: `/usr/bin/rsync` on recent macOS is Apple's `openrsync` ("rsync version 2.6.9 compatible"), which accepts the flags above but not every modern one. If a flag is rejected, or a second run recopies everything instead of listing nothing, `brew install rsync` for the full version.
- Spotlight indexing a freshly formatted disk slows the copy; `sudo mdutil -i off /Volumes/NewDisk` stops it.

Verify afterwards with `verify_copy.py` (destination first): `caffeinate -i python3 verify_copy.py /Volumes/NewDisk/MyFolder /Volumes/OldDisk/MyFolder`.

## Resuming / idempotency

rsync is idempotent by design: a re-run compares size + mtime, skips files that already match, and resumes partial files rather than restarting them. Recovering from any interruption — dropped SSH, power loss, a disk that dropped off the bus — means re-running the exact same command with no changes.

This holds only if `-t` and `--modify-window=1` are both present. Lose either and every re-run recopies everything from scratch.

Wrap it in a retry loop for a flaky source, so transient errors don't need a human:

```bash
for i in $(seq 1 5); do
  rsync … /mnt/src/ /mnt/ssd/ && break        # the full command from above
  echo "attempt $i failed, retrying in 30s"; sleep 30
done
```

Run it inside `tmux` (see `../tmux-session-basics.md`) so it survives a dropped SSH connection — start the session *before* the transfer, since a process launched in a plain SSH shell can't be adopted into tmux afterwards.

### Monitoring a long run

`--info=progress2` gives a single live line:

```
3.47T  100%  3235028.75GB/s   0:00:00 (xfr#337582, to-chk=0/349478)
```

| Field | Reading it |
|---|---|
| Size | Bytes transferred so far. Monotonic — the only field that always moves forward, and the one to trust |
| Percent | Bytes done ÷ total *known so far*, not the true total |
| Time | ETA derived from that same partial total |
| `xfr#` | Files transferred so far |
| `to-chk=N/M` | `N` entries left to check, out of `M` discovered. `M` grows as scanning continues |

**The percentage and ETA going backwards is normal**, not a fault. rsync uses incremental recursion — it builds the file list *while* transferring rather than scanning everything up front. Each time it discovers more files the denominator jumps, so the percentage drops and the ETA swings. Both settle once `M` in `to-chk` stops growing and the list is complete.

The rate swings independently: large files push it up, directories of thousands of small files drag it down, because per-file overhead dominates there.

A `--dry-run` beforehand gives the true totals, which lets you compute real progress as transferred ÷ dry-run size, ignoring the reported percentage entirely. On a dry run the rate itself is meaningless — no bytes move, so rsync divides the full size by a near-zero elapsed time, producing the absurd figure above.

From a second tmux window (`Ctrl-b c` to create, `Ctrl-b n` to switch):

```bash
tail -f ~/rsync.log       # per-file detail as it lands
df -h /mnt/ssd            # destination filling up
```

Detach the whole session with `Ctrl-b d` and the transfer keeps running.

### Checking on it from elsewhere

Snapshot the pane without attaching, from any other window or a fresh SSH connection (see `../tmux-session-basics.md`):

```bash
tmux capture-pane -t copy -p
```

Because `--info=progress2` redraws one line using carriage returns, a capture returns that line as it stands at that instant, not a history. For a record over time, `~/rsync.log` from `--log-file` is the source to read.

Don't type into the pane running rsync — keystrokes go to its stdin, and `Ctrl-C` there kills the transfer. To clear a cluttered pane, `Ctrl-b :` then `clear-history` drops the scrollback without touching the running process; `Ctrl-l` does nothing, since rsync owns the foreground.

## Confirming the copy is complete

Re-run the same command with `--dry-run --stats` added. A complete copy reports **`Number of regular files transferred: 0`** — rsync finds nothing left to do. Anything above zero is a file that didn't land or doesn't match.

Keep `--modify-window=1` in the check. Without it every file on an exFAT destination looks changed and the result is meaningless.

To see *why* each straggler differs, add `-i` (`--itemize-changes`):

```bash
rsync -rlht --modify-window=1 --dry-run -i /mnt/src/ /mnt/ssd/ | head -50
```

| Code | Meaning | Action |
|---|---|---|
| `>f+++++++++` | Missing on the destination entirely | Re-run the real command; these copy normally |
| `>f.st......` | Size *and* time differ — truncated or partial | Re-run the real command |
| `>f..t......` | Content matches, only the mtime differs | Re-runs won't fix it — see below |

Also check what failed during the run itself:

```bash
grep -iE 'error|failed|cannot' ~/rsync.log | head -30
```

### Files that never converge

A `>f..t......` file that survives a second pass means the destination cannot store the timestamp rsync writes. It reads back different, so the file is "changed" on every run, forever. Re-running is pointless — diagnose it instead:

```bash
f=path/relative/to/the/mount/file.jpg
stat -c '%y %s' /mnt/src/"$f" /mnt/ssd/"$f"
```

Compare the two timestamps:

- **Source before 1980-01-01, destination exactly 1980-01-01** — the FAT epoch. exFAT cannot represent any date earlier than 1980, so the driver clamps it, leaving a permanent 1-day-or-more gap. No flag changes this. Count how many files are affected with `find /mnt/src -type f ! -newermt '1980-01-01' | wc -l`; if that matches the number rsync keeps reporting, every straggler is this case and the data is fine.
- **A gap of exactly one hour, or your UTC offset** — the exfat driver's timezone handling. exFAT stores local time plus an offset field, and a disk written by macOS or Windows can disagree with Linux about it. Fix at mount time with the `time_offset=<minutes>` option rather than widening the window.
- **1–2 seconds** — exFAT's 2-second granularity, one short of what `--modify-window=1` absorbs. Use `--modify-window=2`.

Equal sizes plus `cmp /mnt/src/"$f" /mnt/ssd/"$f"` returning silently proves the content copied correctly and only the recorded mtime differs — cosmetic, not data loss.

Two other things exFAT simply cannot store, which fail permanently the same way: **illegal characters** in names (`: * ? " < > | \`), common on ext4 and NTFS sources, and **symlinks**, which have no exFAT representation at all despite `-l`.

Once the remainder is understood and benign, close out on content instead of time:

```bash
rsync -rlh --size-only --dry-run --stats /mnt/src/ /mnt/ssd/     # expect 0 transferred
```

Keep `--size-only` in any future sync to this disk, or those files re-copy on every run — harmless, but they bury genuinely changed files in the output.

## Handling read errors (bad sectors)

```
rsync: [sender] read errors mapping "file.zip": Input/output error (5)
ERROR: file.zip failed verification -- update discarded.
```

This means the *source* media is failing to read specific blocks — not an rsync or filesystem issue. If it's the boot/root SD card, treat this as urgent: it's a sign of card failure, not just a one-off bad file.

Re-run rsync first — marginal sectors sometimes succeed on retry. If the same file fails consistently:

**Exclude it and let the rest finish** — add `--exclude='badfile.zip'` to the command and re-run.

**Attempt recovery with `ddrescue`** (works around bad sectors instead of failing on them):

```bash
sudo apt install gddrescue
sudo ddrescue -d /mnt/src/badfile.zip /mnt/ssd/badfile.zip $HOME/rescue.log
```

- `-d` — direct disk access, bypasses cache
- `rescue.log` — records which sectors succeeded/failed; re-run `ddrescue` later to retry only the failed regions

## Diffing source vs destination

After a run that didn't fully complete, find what's missing:

```bash
diff <(cd /mnt/src && find . -type f | sort) <(cd /mnt/ssd && find . -type f | sort)
```

Anything listed as source-only is what didn't make it across.

This is the weakest of the completeness checks — it catches missing files but not truncated or corrupted ones. For the full escalation (names → per-file sizes → totals → checksums) see `copy-verification-methods.md`, or run `verify_copy.py` alongside it to match by content rather than by path.

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
