# Checking a Copy Is Complete

Four checks, in order of speed vs. certainty. The first two catch what's most likely to actually go wrong (missing or truncated files); the last is the strongest guarantee but slowest.

## 1. Filename match

Confirms nothing is missing or extra:

```bash
diff <(cd /path/to/source && find . -type f | sort) <(cd /path/to/dest && find . -type f | sort)
```

Empty output = every file that exists on one side exists on the other.

## 2. Per-file byte size match

Confirms no truncated/partial files slipped through:

```bash
cd /path/to/source
find . -type f -exec stat -f "%N %z" {} \; | sort > /tmp/src-sizes.txt

cd /path/to/dest
find . -type f -exec stat -f "%N %z" {} \; | sort > /tmp/dst-sizes.txt

diff /tmp/src-sizes.txt /tmp/dst-sizes.txt
```

(Linux: swap `stat -f "%N %z"` for `stat -c "%n %s"`.)

Empty output = every file's actual content size matches exactly, byte for byte.

## 3. Apparent-size totals

Sanity-check at the aggregate level. Use the apparent-size flag, not plain `du -sh` — plain `du` reports disk-block usage, which can legitimately differ across filesystems (extended attributes, block size, metadata) even when file content is identical.

```bash
du -sh -A /path/to/source /path/to/dest              # macOS
du -sh --apparent-size /path/to/source /path/to/dest # Linux
```

## 4. Full checksum verification

The strongest guarantee — catches same-size-but-different-content corruption that steps 1–3 can't detect:

```bash
rsync -rlhtvc --dry-run /path/to/source/ /path/to/dest/
```

`c` forces rsync to compare checksums instead of size+mtime. `--dry-run` means nothing gets modified — it just reports any file that doesn't match. Empty output = byte-for-byte identical.

## Which to use when

Steps 1 and 2 catch the most common real-world failures: missing files, truncated files. Step 3 is a quick aggregate sanity check but can give false alarms across different filesystems. Step 4 is the one to reach for if you suspect silent corruption rather than incompleteness — same size, different bytes.
