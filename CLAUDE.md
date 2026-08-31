# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal notes-and-scripts repo for Raspberry Pi projects. There is **no build system, no test suite, no linter, and no dependency manifest** — don't look for `package.json`, `requirements.txt`, `Makefile`, or CI config; they don't exist. The repo is roughly 80% Markdown how-to documents and 20% small standalone Python scripts.

Almost everything here is designed to run **on a Pi**, not on the Mac where the repo lives. Scripts import hardware-only libraries (`gpiozero`, `picamera`, `RPi.GPIO`, `blinkt`, `sense_hat`) that will `ImportError` on the development machine — this is expected, not a bug to fix. Dependencies are installed ad hoc with `apt`/`pip --break-system-packages` per the relevant readme; there is no central install step.

The one exception is `transfer/verify_copy.py`, which is macOS/Linux host tooling and is the only script runnable locally.

## Structure

Each top-level directory is an independent project, self-documented by its own `readme.md` — there are no shared modules or imports across directories. Directories: `spy` (PIR motion sensor + circular-buffer camera), `cam` (motion daemon + Ansible control, plus GPIO button experiments), `sensehat` (cron-driven sensor logging to CSV), `fm` (Blinkt! VU meter reading a PipeWire monitor source), `scrollphat`, `webdav` (Dockerized nginx WebDAV server), `transfer` (external-disk copy guides + `verify_copy.py`), `setup` (per-topic Pi setup guides), `archive` (superseded notes — don't update these).

Loose Markdown files at the repo root are standalone reference documents on a single topic (fan control, tmux, Podman, WiFi fallback hotspot). New notes of this kind belong at the root unless they fit an existing project folder; `setup/` is the older organizing scheme.

## Guides index

Root-level references (current, topic-per-file):

| File | Covers |
| --- | --- |
| `accesspopup-setup.md` | Fallback WiFi hotspot on the Pi 4 using AccessPopup; why Comitup can't work on the brcmfmac chip |
| `fan-shim-qa.md` | Pimoroni Fan SHIM Q&A — LED/button meanings, modes, temp commands and why they disagree, boot debugging, battery drain |
| `rpi4-fan-control.md` | Built-in GPIO fan control via `raspi-config`, temperature thresholds and reference table, graphing temp over time |
| `podman-mac-to-pi.md` | Driving the Pi's containers from Podman on macOS, incl. Podman Desktop showing no containers |
| `tmux-session-basics.md` | Keeping a long SSH job (e.g. rsync) alive across dropped connections |

Per-project docs (live beside the code they describe):

| File | Covers |
| --- | --- |
| `transfer/readme.md` | Index of the three copy/verify docs and the `verify_copy.py` invocation |
| `transfer/ssd-transfer-rsync-notes.md` | End-to-end external USB disk workflow: identify (incl. the Mac EFI partition), disk-to-disk power budget and read-only source mounting, wipe/format as exFAT, mount + fstab with `uid`/`umask`/`nofail`, one canonical rsync command plus situational flags, idempotency via `-t` + `--modify-window=1`, monitoring, bad sectors, verification, slow-transfer diagnosis |
| `transfer/copy-verification-methods.md` | Four escalating checks that a copy is complete: filenames, per-file sizes, apparent-size totals, `rsync -c` |
| `webdav/README.md` | Overview + file map for the Dockerized WebDAV server |
| `webdav/docs/docker-install-raspi.md` | Installing Docker on Pi 4 (incl. cleaning broken apt sources) |
| `webdav/docs/webdav-docker.md` | Deploying, generating `.htpasswd`, building, verifying, Super Productivity sync settings |
| `webdav/docs/tailscale-setup.md` | Tailscale across Pi/Mac/iPhone, disabling key expiry |
| `webdav/docs/webdav-cleanup.md` | Tearing the whole WebDAV setup back down |
| `fm/fm-broadcast-setup.md` | FM browser broadcast station: OS flash, wayvnc + TigerVNC, FM module wiring/frequency, antenna, power |
| `fm/vu.md` | Blinkt! VU meter — PipeWire monitor source, deps, tuning, how the script works |
| `spy/readme.md` | PIR + camera deps and installing it as an init.d service |
| `sensehat/readme.md` | Cron entry for the CSV sensor logger |
| `scrollphat/readme.md` | Enabling I2C and running Scroll pHAT examples in Docker |
| `cam/readme.md`, `cam/ansible/readme.md` | The three motion-daemon playbooks |

`setup/` — the older Pi build-out guides (Dec 2022), one per topic: `raspi.md` (imager, SSH, first update), `usb.md` (format/mount/fstab), `nas.md` (Samba share), `transmission.md` (daemon + remote), `openvpn.md`, `nodejs.md`, `fan.md`, `hyperpixel.md`, `touch-display.md`, `other.md`. `setup/settings.json` is a Transmission config, not app config for this repo.

`archive/` — superseded notes kept for reference only (`os.md`, `network.md`, `usb.md`, `docker.md`, `setup.md`, `piespy/readme.md`). Read them if you need history; don't update or cite them as current.

## Commands

Managing the `cam` motion daemon over SSH (from `cam/ansible/`, targets the single Pi in `hosts`; `remote_user = pi`, host key checking disabled):

```bash
ansible-playbook start.yml   # service motion start
ansible-playbook stop.yml    # stop + halt
ansible-playbook move.yml    # stop, tar videos back to ~/tmp/raspi/, wipe remote, halt
```

Verifying a disk copy (runs locally on macOS, from `transfer/`; **argument order is destination-first**):

```bash
python3 verify_copy.py /Volumes/NewDisk /Volumes/OldDisk            # full blake2b hash
python3 verify_copy.py /Volumes/NewDisk /Volumes/OldDisk --quick    # sample first+last 1MB + size
caffeinate -i python3 verify_copy.py ...                            # prevent disk sleep on long runs
```

It is strictly read-only, matches by content rather than path (so reorganized folders still verify), groups disk A by file size before hashing to avoid hashing anything unnecessarily, and writes unmatched files to `missing_files.txt`. Preserve the read-only property in any change.

WebDAV server (on the Pi, from `webdav/`): `docker compose up -d --build`. `.htpasswd` and `data/` are deliberately untracked and must stay that way; the service is meant to be reachable over Tailscale only, never port-forwarded.

## Conventions

Markdown notes are written as terse, numbered, copy-pasteable procedures with fenced `bash` blocks, and they explain *why* a step exists when the reason is non-obvious (e.g. why `du --apparent-size` rather than `du`, why AccessPopup replaced Comitup). Match that voice: keep new notes runnable and short, and prefer amending an existing topic file over adding a near-duplicate one.

Python here is deliberately plain and script-shaped — top-level setup, a few functions, a `while True` or `with` block at the bottom. Don't restructure these into classes, packages, or add frameworks.

Config values that vary per machine (the Ansible IP in `cam/ansible/hosts`, `MONITOR` in `fm/run.py`, GPIO pin numbers) are hardcoded near the top of the file by design and documented in the neighbouring readme.
