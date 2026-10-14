<img src="packaging/krfb-virtualmonitor-gui.svg" width="72" align="right" alt="">

# Krfb Virtual Screen Manager

**A desktop GUI for `krfb-virtualmonitor` — create, manage, and monitor KDE's
virtual displays without touching the command line.**

[![License: GPL-3.0-or-later](https://img.shields.io/badge/License-GPL--3.0--or--later-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.html)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/UI-PySide6%20%28Qt6%29-41cd52.svg)](https://doc.qt.io/qtforpython/)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%C2%B7%20Wayland%20%C2%B7%20KWin-informational.svg)](#requirements)

[中文文档](README_CN.md)

---

## Overview

`krfb-virtualmonitor` is the command-line tool shipped with [krfb](https://invent.kde.org/network/krfb),
KDE's VNC server. It creates **virtual displays** on top of KWin — extra monitors
that exist only in software, perfect for headless remote access, software KVM setups,
or driving a tablet as a second screen.

It is powerful but bare: every adjustment means re-typing a long command with a
plaintext password, and there is no way to see which screens are running. This
project wraps the whole thing in a native Qt6 desktop application with two
non-negotiable guarantees:

> **1. Closing the GUI never affects running virtual screens.**
> **2. Reopening the GUI always re-adopts them.**

## Features

- **Full lifecycle management** — create, edit, start, stop, and delete virtual
  screens from a list/detail interface, individually or all at once.
- **Truthful state tracking** — a screen counts as "running" only when its process
  is genuinely alive *and* KWin has actually materialized the `Virtual-<name>`
  output. States are explicit: running, starting, stopped, crashed, failed, unmanaged.
- **Survives GUI restarts** — screens are detached into their own session, and the
  GUI re-identifies them by `(name, port)` with `pid + starttime` liveness checks
  (PID-reuse and zombie-proof).
- **Adopt external processes** — launched `krfb-virtualmonitor` by hand? The
  **Scan** action finds it in `/proc` and takes it over, password included.
- **Password vaulting** — passwords live in **KDE Wallet**, reached through
  kwalletd's native `org.kde.KWallet` D-Bus interface (not the generic
  `org.freedesktop.secrets` name, which any installed implementation can claim —
  on a machine with gnome-keyring around, that would silently put your passwords
  in the wrong store). Passwords never appear in config files. If the wallet is
  locked or disabled, the app offers to unlock it at startup and otherwise
  degrades to session-only memory, saying so explicitly — it never blocks or hangs.
- **Requested vs. actual values, side by side** — KWin is known to override the
  `--scale` request; the UI shows what was asked for *and* what KWin actually
  applied, and highlights any mismatch.
- **Live log viewer** — per-screen krfb output, streamed incrementally.
- **Environment self-check** — at startup the app verifies `krfb-virtualmonitor`,
  the Wayland socket, `kscreen-doctor` health, and systemd cgroup semantics, and
  reports anything that would break the two guarantees above.
- **Login autostart** — one application-level `.desktop` restores every screen
  marked *desired running*. No plaintext passwords ever touch disk.
- **Desktop-native UX** — system tray with single-instance handling, light/dark
  theming that follows the system palette, and a live command-line preview of
  exactly what the GUI is about to execute.
- **11 UI languages** — English, Simplified & Traditional Chinese, Japanese, Korean,
  German, French, Spanish, Italian, Brazilian Portuguese and Russian. The interface
  follows the system language by default and can be switched instantly from
  Settings → Language (no restart).
- **Your call on closing** — the title-bar X can minimize to the tray, quit the
  program, or ask every time (with a *remember my choice* checkbox). Also
  configurable in Settings → Closing the window.

## Requirements

| Component | Requirement |
|---|---|
| Session | **Wayland running KWin** (KDE Plasma). Virtual displays are a KWin-only feature — GNOME/X11 cannot work, and the app tells you why at startup. |
| krfb | The `krfb` package on Arch / Debian / Ubuntu / Fedora — it provides `/usr/bin/krfb-virtualmonitor`. |
| kscreen | `kscreen-doctor` — strongly recommended. Used to read back the *real* resolution/scale and to fix up overridden `--scale` values. |
| kwallet | `kwalletd6` (KDE Wallet) — required for password storage. If the wallet subsystem is switched off in System Settings, the app says so and keeps passwords in memory for the session only. |
| Python | 3.11+ (source run only; the packaged build needs nothing preinstalled). |
| Tooling | [uv](https://docs.astral.sh/uv/) for dependency management. |

## Quick Start

```bash
# 1. Install dependencies into .venv (uses uv.lock for reproducibility)
uv sync

# 2. Run
./run.sh              # normal launch
./run.sh --tray       # start minimized to the system tray
```

Or invoke the entry point directly:

```bash
.venv/bin/python main.py [--tray] [--version]
```

## Building a Standalone Executable

The build script produces a **onedir** bundle (executable + `_internal/`) that runs
on any Linux machine — no Python, no virtualenv, no dependencies required:

```bash
packaging/build.sh
./dist/krfb-virtualmonitor-gui/krfb-virtualmonitor-gui
```

`onedir` is a deliberate choice: PyInstaller's onefile mode would decompress
hundreds of megabytes into `/tmp` on every launch, which is a poor fit for an
always-available tray application.

To add the app to the KDE application menu and `~/.local/bin`:

```bash
packaging/install-desktop.sh              # install
packaging/install-desktop.sh --uninstall  # remove
```

The desktop launcher prefers the packaged build and falls back to running from
source via `.venv` if the bundle has not been built.

## Usage

1. **Create a screen** — click *New*, pick a name, resolution (presets or custom),
   scale, and port. The dialog shows the exact command line it will run, live.
2. **Start it** — the app launches `krfb-virtualmonitor`, then waits (up to 8 s)
   for KWin to report the `Virtual-<name>` output. Only then is it "running".
   If KWin overrode the requested scale, it is corrected via `kscreen-doctor` and
   the actual values are read back into the detail pane.
3. **Connect** — point any VNC client at `localhost:<port>`. The password is the
   one generated (or entered) in the dialog, retrievable from the detail pane.
4. **Walk away** — close the window (or the whole GUI): the screens keep running.
   Reopen later; everything is re-adopted and the logs are still there.
5. **Adopt strays** — if you started krfb from a terminal, *Scan* imports it,
   password included, and it becomes fully managed.

Login autostart is a toggle in *Settings*: when enabled, the GUI starts in the
tray at login and restores every screen marked as *desired running*. It
deliberately writes **one application-level entry** rather than one `.desktop`
per screen — a per-screen entry would have to embed `--password` in plaintext
inside a world-readable `0644` desktop file, defeating the entire point of
keyring storage. Starting the GUI instead keeps passwords off disk completely.
(The unit KDE's autostart generator derives from the entry is `ExitType=cgroup`,
which is the safe case — see the cgroup note below.)

## Architecture

```
main.py                     Entry point: single-instance guard, theme, wiring
krfb_gui/
  constants.py              XDG paths, krfb parameter constraints, env whitelist
  models.py                 Screen (config) / Runtime (observed) / ProcInfo
  store.py                  Atomic JSON persistence (tmp + fsync + rename)
  proctools.py              Pure /proc readers: starttime, zombies, ports, argv
  envtools.py               Sanitized child environment — the ONLY way to spawn
  kscreen.py                kscreen-doctor parsing; real output readback
  manager.py                Lifecycle: spawn/stop/state, adoption, self-check
  secrets.py                KDE Wallet client with hard timeouts; degrades to
                            session-only memory, never blocks
  autostart.py              Single application-level .desktop autostart
  ui/                       Main window, screen list, detail pane, dialogs,
                            log viewer, theming, embedded SVG icons, vector art
tests/
  test_persistence.py       Two-process GUI-restart re-adoption test
  test_child_env.py         Packaged-build child environment regression
  test_process_state.py     Zombie-process liveness regression
```

Two design rules shape everything:

**Config and runtime state are separate files.** `Screen` is user intent, written
only when settings change; `Runtime` is observed reality (pid, actual resolution),
rewritten on every process event. Mixing them would rewrite the config file on
every poll, and let two GUI instances clobber each other's updates.

**Data modules never import Qt.** `manager`, `store`, `proctools`, `kscreen`,
`envtools`, `secrets` and `autostart` are pure Python and independently testable;
`ui/` is the only layer that depends on PySide6.

## Storage Layout

| What | Where | Mode |
|---|---|---|
| Screen configuration (no passwords) | `~/.config/krfb-virtualmonitor-gui/screens.json` | `0600` |
| Runtime state (pids, observed values) | `~/.local/state/krfb-virtualmonitor-gui/runtime.json` | `0600` |
| Per-screen logs | `~/.local/state/krfb-virtualmonitor-gui/logs/<id>.log` | `0600` |
| Passwords | KDE Wallet (`kdewallet`, via `org.kde.KWallet`) | — |
| Autostart entry | `~/.config/autostart/krfb-virtualmonitor-gui.desktop` | `0644` |

Passwords are stored in the standard *Passwords* folder of the KDE wallet, keyed by
the screen's stable UUID — which is also why screen identity never depends on pid.
(Upgrading from an older build? On the first read the app moves any password still
sitting in the freedesktop Secret Service into the wallet — read-only, nothing is
deleted.)

## Testing

```bash
# Core requirement, phase A: start a screen, then exit
.venv/bin/python tests/test_persistence.py --phase a

# Phase B: a brand-new process rediscovers and re-adopts it
.venv/bin/python tests/test_persistence.py --phase b
```

The two phases run in **separate Python processes** — that is the whole point:
it is the only way to actually prove "the virtual screen outlives the GUI, and a
fresh GUI can take it over". Test state lives in
`/tmp/krfb-virtualmonitor-gui-test` (override with `KRBFTEST_DIR`) and never
touches your real configuration.

Two further regression suites run without a display, a build, or any GUI:

```bash
.venv/bin/python tests/test_child_env.py      # packaged-build child env hygiene
.venv/bin/python tests/test_process_state.py  # zombies must not count as "running"
```

`test_child_env.py` simulates PyInstaller's `LD_LIBRARY_PATH` injection, asserts
that `kscreen-doctor` / `krfb --version` still work under it, and scans the source
tree for any bare `subprocess` call that bypasses the sanitizer.
`test_process_state.py` spawns real zombie processes and asserts the liveness
rules against them.

## Engineering Notes

The interesting parts of this project are the failure modes it had to survive.
Each one below was observed on real hardware, and each has a fix plus (where
possible) a regression test.

### Zombie processes masquerade as "running"

krfb exits within ~1 s of `SIGTERM` and KWin drops the virtual output within ~3 s —
but the GUI showed "running" for over a minute. Reason: krfb is the GUI's child,
and the parent never `waitpid`s, so the process becomes a **zombie**.
`/proc/<pid>/stat` still exists and `starttime` is unchanged, so an
identity check passes. The zombie is only reaped opportunistically — `subprocess`
runs `_cleanup()` the next time a child is created. Fix: liveness additionally
rejects the `Z` state character, and "Stop" records the user's intent *before*
identity verification (a zombie's `/proc/<pid>/exe` is unreadable, so verification
necessarily fails — but "the user doesn't want this running" must still be honored,
or the UI raises a bogus crash banner).

### `--scale` is effectively ignored

Requesting `--scale 1.25` or `1.5` yielded **1.75** every time. KWin persists a
per-output configuration in `kwinoutputconfig.json`, and **every newly created
virtual display is assigned the same UUID** — so stale config for that UUID
always wins over the command-line request. Fix: after the output appears, set the
scale explicitly with `kscreen-doctor output.<connector>.scale.<value>`, then read
back the true values. The UI displays requested and actual values separately and
flags mismatches.

### Opening the wallet can hang the app forever

`kwalletd`'s `open()` pops the wallet password prompt, and **D-Bus calls have no
timeout of their own**. If the prompt can't be displayed (headless, started from a
systemd unit, prompter broken), that call never returns. Fix: probing only uses
calls that can't prompt (`isEnabled`, `isOpen`), every wallet call runs on a
daemon thread with a 2 s timeout, and anything that might prompt is additionally
confined to the explicit unlock path — never the polling/refresh path. When the
wallet stays shut, the app degrades to session-only memory with a clear UI label.
**The startup path never depends on the wallet succeeding.** (Daemon threads, not
a `ThreadPoolExecutor` — the executor joins its workers at interpreter exit, which
would reintroduce the hang.)

### VNC passwords are 8 characters, full stop

krfb links against libvncserver, which uses classic VNC DES authentication —
**only the first 8 characters of the password are ever used**. The generator
therefore produces exactly 8 characters, and the UI says so. Handing users a
32-character password that only contributes 8 characters of entropy is security
theater.

### Passwords are visible to other local users

Passwords are passed via `--password`, and `/proc/<pid>/cmdline` is mode `0444` —
world-readable. krfb offers no stdin/environment alternative and no
loopback-only binding, so this cannot be fixed at the wrapper level. The UI
discloses it plainly rather than pretending otherwise.

### "Started" ≠ "virtual display created"

krfb will report a portal error yet still listen on the port. The only reliable
proof of success is KWin actually listing the `Virtual-<name>` output. When
`kscreen-doctor` is unavailable or unhealthy, the check degrades to port-listening
— a weaker but honest signal, chosen so a real screen is never misreported as failed.

### Packaged builds poison child processes

PyInstaller's Linux bootloader injects `LD_LIBRARY_PATH=<bundle>/_internal:...`
into the GUI's own environment so it can load the bundled Qt6. Every child
process inherits it — and every helper this app runs (`krfb-virtualmonitor`,
`kscreen-doctor`, `systemctl`) is a *system* Qt program that will then load the
wrong libQt6 and abort (SIGABRT, empty stdout). The consequences are severe:
`list_outputs()` returns empty forever, so start verification always "times out"
after 8 s, wipes the runtime record, and orphans the process.

Fix: a strict environment whitelist (`ENV_PASSTHROUGH` in `constants.py`) strips
`LD_LIBRARY_PATH` / `PYTHONPATH` / `QT_*` and friends, and **every** external
command goes through `envtools.run_helper()`. A static rule in
`tests/test_child_env.py` fails the build if a bare `subprocess` call ever
reappears. Two related fallbacks: if `kscreen-doctor` is entirely unusable,
start verification degrades to port-checking (as promised by the environment
self-check), and identity is never cleared while the process is in fact alive.

### Systemd cgroups can kill your screens

`setsid()` defeats `SIGHUP`, not cgroup-level cleanup. If the GUI is started from
a unit with `KillMode=control-group` + `ExitType=main`, exiting the GUI SIGTERMs
the entire cgroup — taking every virtual screen with it. The app detects this at
startup and explains the fix (`ExitType=cgroup`, or launch from the desktop
launcher as usual).

## Known Limitations

- **Wayland + KWin only.** Virtual monitors require compositor support that, as of
  today, only KWin implements.
- **Passwords readable via `/proc/<pid>/cmdline`** by other local users (krfb
  limitation, disclosed in the UI).
- **VNC authentication uses 8 characters**, regardless of password length.
- **In the packaged build**, the log viewer's "Open containing folder" button goes
  through `QDesktopServices` → `xdg-open`, a Qt-internal fork that cannot receive
  a sanitized environment — so it still carries the bundle's `LD_LIBRARY_PATH` and
  the file manager may fail to launch. Scope: that one button.
- **Autostart must be toggled off/on** when switching between running from source
  and running the packaged build, because the `.desktop` entry records the path of
  the launcher that wrote it.

## License

Copyright (C) 2026 SkyDreamLG.

This program is free software: you can redistribute it and/or modify it under the
terms of the **GNU General Public License** as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but **WITHOUT ANY
WARRANTY**; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the [GNU General Public License](LICENSE) for details.
