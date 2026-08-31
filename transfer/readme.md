# transfer

Moving data onto external USB disks, and proving it arrived intact.

| File | Purpose |
| --- | --- |
| `ssd-transfer-rsync-notes.md` | The main guide: identify a disk, wipe and format it as exFAT, mount it (incl. fstab), copy with rsync, diagnose slow or failing transfers |
| `copy-verification-methods.md` | Four escalating shell checks that a copy is complete — filenames, per-file sizes, apparent-size totals, `rsync -c` checksums |
| `verify_copy.py` | Stronger verification than the shell checks: matches by content, so it still verifies when the destination folder structure differs |

`verify_copy.py` runs on the host (macOS/Linux), not the Pi, and is strictly read-only — it only ever opens files for reading:

```bash
python3 verify_copy.py /Volumes/NewDisk /Volumes/OldDisk          # destination first, then source
python3 verify_copy.py /Volumes/NewDisk /Volumes/OldDisk --quick  # sample first+last 1MB + size
caffeinate -i python3 verify_copy.py ...                          # keep the disks awake on long runs
```

Unmatched files are written to `missing_files.txt`.

Long transfers should run inside `tmux` (see `../tmux-session-basics.md`) so they survive a dropped SSH connection.
