#!/usr/bin/env python3
"""
verify_copy.py — Verify every file on disk B (old) exists, by content, on disk A (new),
even if folder structure differs. Strictly read-only: files are only opened for reading.

Order matters: disk A first (new/destination), disk B second (old/source).

Usage:
    # Full hash (guaranteed accuracy, slow for large files)
    python3 verify_copy.py /Volumes/NewDisk /Volumes/OldDisk

    # Fast mode — sample first+last 1MB instead of full hash (good for a quick sanity check)
    python3 verify_copy.py /Volumes/NewDisk /Volumes/OldDisk --quick

    # Prevent disk sleep on long runs (macOS)
    caffeinate -i python3 verify_copy.py /Volumes/NewDisk /Volumes/OldDisk

    # Custom report path
    python3 verify_copy.py /Volumes/NewDisk /Volumes/OldDisk --report /tmp/results.txt

    # Include OS junk files (.DS_Store, Thumbs.db, etc.)
    python3 verify_copy.py /Volumes/NewDisk /Volumes/OldDisk --include-junk
"""
import argparse
import errno
import hashlib
import os
import sys
import time
from collections import defaultdict

DEFAULT_IGNORE = {
    '.DS_Store', 'Thumbs.db', 'desktop.ini', '.Spotlight-V100',
    '.Trashes', '.fseventsd', 'System Volume Information', '$RECYCLE.BIN'
}

def format_bytes(n):
    n = float(n)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}PB"

def iter_files(root, ignore_names):
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in ignore_names]
        for fn in filenames:
            if fn in ignore_names:
                continue
            full = os.path.join(dirpath, fn)
            if os.path.islink(full):
                continue
            try:
                size = os.path.getsize(full)
            except OSError as e:
                print(f"  [warn] can't stat {full}: {e}", file=sys.stderr)
                continue
            yield full, size

def file_hash(path, size, use_fast_hash=False, chunk=1024 * 1024):
    h = hashlib.blake2b()
    with open(path, 'rb') as f:
        if use_fast_hash and size > 3 * chunk:
            h.update(f.read(chunk))
            f.seek(-chunk, os.SEEK_END)
            h.update(f.read(chunk))
            h.update(str(size).encode())
        else:
            for block in iter(lambda: f.read(chunk), b''):
                h.update(block)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser(description="Verify disk B files exist (by content) on disk A.")
    ap.add_argument('disk_a', help="New disk (destination) root path")
    ap.add_argument('disk_b', help="Old disk (source) root path")
    ap.add_argument('--quick', action='store_true',
                    help="Sample-hash large files (first+last 1MB + size) instead of full hash. "
                         "Faster on big media files; may produce false matches for files with "
                         "identical headers/footers but different content in the middle.")
    ap.add_argument('--report', default='missing_files.txt', help="Output file for missing/mismatched list")
    ap.add_argument('--include-junk', action='store_true', help="Don't skip OS junk files (.DS_Store etc.)")
    args = ap.parse_args()

    for label, path in [("disk A", args.disk_a), ("disk B", args.disk_b)]:
        if not os.path.isdir(path):
            sys.exit(f"Error: {label} path is not a directory: {path!r}")

    ignore = set() if args.include_junk else DEFAULT_IGNORE

    LARGE_THRESHOLD = 100 * 1024 * 1024  # 100MB

    print(f"Scanning disk A (new): {args.disk_a}")
    t0 = time.time()
    a_by_size = defaultdict(list)
    a_count = 0
    a_bytes = 0
    last_print = t0
    for path, size in iter_files(args.disk_a, ignore):
        a_by_size[size].append(path)
        a_count += 1
        a_bytes += size
        now = time.time()
        if now - last_print >= 1:
            print(f"  {a_count} files so far...", end='\r', flush=True)
            last_print = now
    print(f"  {a_count} files, {format_bytes(a_bytes)}, {time.time()-t0:.1f}s")

    print(f"Scanning disk B (old): {args.disk_b}")
    b_files = list(iter_files(args.disk_b, ignore))
    print(f"  {len(b_files)} files")

    hash_cache = {}
    hash_errors = {}
    def get_hash(path, size):
        if path not in hash_cache:
            try:
                hash_cache[path] = file_hash(path, size, use_fast_hash=args.quick)
            except OSError as e:
                print(f"  [warn] can't read {path}: {e}", file=sys.stderr)
                hash_cache[path] = None
                hash_errors[path] = (e.errno, str(e))
        return hash_cache[path]

    missing = []
    verified = 0
    zero_byte_count = 0
    consecutive_enoent = 0
    ENOENT_ABORT = 10

    print("Comparing (reads file contents only where sizes collide)...")
    t0 = time.time()
    last_print = t0
    progress_on_line = False  # tracks whether a \r line needs closing

    def print_progress(i):
        nonlocal last_print, progress_on_line
        pct = i / len(b_files) * 100
        print(f"  {i}/{len(b_files)} ({pct:.0f}%) — {verified} verified, {len(missing)} missing",
              end='\r', flush=True)
        progress_on_line = True
        last_print = time.time()

    def print_info(msg):
        nonlocal progress_on_line
        if progress_on_line:
            print()
            progress_on_line = False
        print(f"  {msg}", flush=True)

    for i, (b_path, size) in enumerate(b_files):
        if time.time() - last_print >= 1:
            print_progress(i)

        candidates = a_by_size.get(size, [])
        if not candidates:
            missing.append((b_path, size, "no file of this size on A"))
            continue
        # All zero-byte files are content-identical by definition.
        if size == 0:
            zero_byte_count += 1
            continue

        if size >= LARGE_THRESHOLD and b_path not in hash_cache:
            print_info(f"Hashing {os.path.basename(b_path)} ({format_bytes(size)})...")

        b_hash = get_hash(b_path, size)
        if b_hash is None:
            err_errno, err_str = hash_errors.get(b_path, (None, 'unknown error'))
            missing.append((b_path, size, f"could not read: {err_str}"))
            if err_errno == errno.ENOENT:
                consecutive_enoent += 1
                if consecutive_enoent >= ENOENT_ABORT:
                    print_info(f"Aborting: {ENOENT_ABORT} consecutive 'file not found' errors — disk B is likely disconnected or remounted.")
                    print_info("Tip: re-run with: caffeinate -i python3 verify_copy.py ...")
                    break
            else:
                consecutive_enoent = 0
            continue
        consecutive_enoent = 0

        matched = False
        for a_path in candidates:
            if size >= LARGE_THRESHOLD and a_path not in hash_cache:
                print_info(f"Hashing candidate {os.path.basename(a_path)} ({format_bytes(size)})...")
            a_hash = get_hash(a_path, size)
            if a_hash is None:
                missing.append((b_path, size, f"could not read candidate on A: {a_path} ({hash_errors.get(a_path, (None, 'unknown error'))[1]})"))
                matched = True  # avoid double-reporting as "content differs"
                break
            if a_hash == b_hash:
                verified += 1
                matched = True
                break
        if not matched:
            missing.append((b_path, size, f"{len(candidates)} file(s) on A share this size but content differs"))

    if progress_on_line:
        print()
    print(f"Done in {time.time()-t0:.1f}s\n")
    print(f"Verified on A:          {verified}")
    print(f"Zero-byte (content-equal by definition): {zero_byte_count}")
    print(f"Missing/mismatched:     {len(missing)}")

    try:
        with open(args.report, 'w') as f:
            for path, size, reason in missing:
                f.write(f"{path}\t{format_bytes(size)}\t{reason}\n")
        print(f"\nFull list written to {args.report}")
    except OSError as e:
        print(f"\nWarning: could not write report to {args.report!r}: {e}", file=sys.stderr)
        print("\nMissing/mismatched files:")
        for path, size, reason in missing:
            print(f"  {path}\t{format_bytes(size)}\t{reason}")

if __name__ == '__main__':
    main()
