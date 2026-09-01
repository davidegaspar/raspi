# tmux — Session Basics

Minimal tmux workflow for running a long job over SSH (e.g. an rsync transfer) that needs to survive a dropped connection.

## Why

A normal SSH shell dies (SIGHUP) if the connection drops, killing anything running in it. tmux runs a session on the remote machine independently of any one SSH connection — you can disconnect, reconnect, or even lose the connection unexpectedly, and the session keeps running.

## Install

```bash
sudo apt install tmux
```

## "No server running"

```
error connecting to /tmp/tmux-1000/default (No such file or directory)
```

`tmux ls` prints this when no session exists yet — it's the normal empty state, not a fault. The socket is created by the first session and removed when the last one exits.

## Start a session

```bash
tmux new -s <session-name>
```

Names the session — pick anything memorable. Run whatever long-lived command you need inside it as normal.

Confirmation you're inside tmux: a status bar appears at the bottom of the terminal listing the session name.

## Detach

`Ctrl-b` then `d` (release `Ctrl-b` first, then tap `d`).

Drops back to the normal shell; the session keeps running in the background.

**If the keybind doesn't visibly do anything:** it's not required for the session to be safe. Since the session is independent of the SSH connection, closing the terminal window entirely (or letting the SSH connection drop) has the same effect — the tmux session on the remote machine keeps running regardless.

## Reattach

```bash
tmux attach -t <session-name>
```

Works after a deliberate detach or after an unexpected disconnection — tmux doesn't distinguish between the two.

## List sessions

```bash
tmux ls
```

Shows all sessions and whether each is `(attached)` or not. Useful to confirm a session actually started (if `tmux new` failed silently, this will show nothing / "no server running").

## Switch between sessions

From inside a tmux session, without detaching first:

```bash
tmux switch -t <session-name>
```

Or visually: `Ctrl-b` then `s` opens a list to arrow through and hit Enter on.

## Create a second session

From inside an existing session, typed as a normal command (not a keybind):

```bash
tmux new -s <new-name>
```

tmux supports nesting this way — it drops you straight into the new session.

## Scroll back

`Ctrl-b [` enters copy mode, which is the only way to see anything above the visible screen.

- `PgUp` / `PgDn`, or arrow keys, to move
- `q` or `Esc` to leave copy mode and return to the live view
- `Ctrl-r` searches backwards (emacs keys, the default); `?` if `mode-keys` is set to vi

To scroll with the mouse wheel instead: `Ctrl-b :` then `set -g mouse on`.

Scrollback is capped at 2000 lines per pane by default, so the start of a long-running job may already be gone. Raise it with `set -g history-limit 50000` (applies to panes created afterwards), or write the job's output to a log file and stop relying on scrollback.

`Ctrl-b :` then `clear-history` drops a pane's scrollback without disturbing whatever is running in it.

## How long a session lasts

Sessions don't expire on a timer, and detaching doesn't start a clock — an idle session sits there indefinitely.

A session ends when:

- the last window's process exits (typing `exit` in the shell closes that window; closing the last one ends the session),
- the machine reboots — sessions do **not** survive a reboot,
- someone runs `tmux kill-session -t <name>` or `tmux kill-server`.

The server process itself exits once the final session is gone, which is what removes the socket and makes `tmux ls` report "no server running" again.

## Read a session's output without attaching

```bash
tmux capture-pane -t <session-name> -p
```

Prints the currently visible pane content. Add `-S -` for full scrollback:

```bash
tmux capture-pane -t <session-name> -p -S -
```

Pipe to a file to save or search it:

```bash
tmux capture-pane -t <session-name> -p -S - > session.log
```
