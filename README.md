<img src="packaging/krfb-virtualmonitor-gui.svg" width="72" align="right" alt="">

# Krfb Virtual Screen Manager

**A desktop GUI for `krfb-virtualmonitor` — create, manage, and monitor KDE virtual
displays without using the command line.**

[![License: GPL-3.0-or-later](https://img.shields.io/badge/License-GPL--3.0--or--later-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.html)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/UI-PySide6%20%28Qt6%29-41cd52.svg)](https://doc.qt.io/qtforpython/)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%C2%B7%20Wayland%20%C2%B7%20KWin-informational.svg)](#requirements)

[中文文档](README_CN.md)

---

## Overview

`krfb-virtualmonitor` ships with [krfb](https://invent.kde.org/network/krfb), KDE's
VNC server. It creates **virtual displays** on top of KWin: additional monitors that
exist only in software, used for headless remote access, software KVM setups, and
tablets configured as secondary screens.

The tool is capable but stateless. Every adjustment requires re-entering a full
command line including a plaintext password, and there is no way to see which
screens are currently running. This project provides a native Qt6 front end for it,
built around two invariants:

> **1. Closing the GUI never affects a running virtual screen.**
> **2. Reopening the GUI re-adopts every running virtual screen.**

## Features

- **Lifecycle management** — create, edit, start, stop and delete virtual screens
  from a list/detail interface, individually or in bulk.
- **Verified state tracking** — a screen is reported as running only when its process
  is alive *and* KWin has materialized the corresponding `Virtual-<name>` output.
  States are distinct: running, starting, stopped, crashed, failed, unmanaged.
- **Persistence across GUI restarts** — screens are detached into their own session.
  The GUI re-identifies them by `(name, port)` and verifies liveness with
  `pid + starttime`, which is immune to PID reuse and to zombie processes.
- **Adoption of external processes** — a `krfb-virtualmonitor` started by hand is
  located in `/proc` by the *Scan* action and taken under management, password
  included.
- **Three password stores** — **KDE Wallet** (via kwalletd's native
  `org.kde.KWallet` D-Bus interface, not the generic `org.freedesktop.secrets` name
  that any installed implementation may claim), the **system keyring** (Secret
  Service), and a **built-in encrypted vault** (SQLite; every value encrypted with a
  key derived from a user-set master password, `scrypt` → Fernet). The default is
  KDE Wallet. The store is selected in Settings, where only usable stores are
  listed; if the selected store is unavailable the application falls back to the
  system keyring and then to the built-in vault, and reports which store is in use.
  The preference is not modified by a fallback, so the selected store is used again
  as soon as it becomes available. Changing stores offers to migrate the passwords;
  if the target already holds passwords for this application, the choice is to keep
  the target's, overwrite them with the current ones, or merge — merging compares
  both sides first, reports the screens that conflict, and asks which version wins.
  Clearing the source store is a separate, separately confirmed step. Passwords are
  never written to configuration files. Locked stores are unlocked at startup on
  request; a store that becomes unavailable while holding passwords triggers a
  warning dialog rather than a silent "no saved password".
- **Requested and effective values, side by side** — KWin may override the `--scale`
  request. The UI shows both the requested and the effective values and flags any
  mismatch.
- **Live log viewer** — per-screen krfb output, streamed incrementally.
- **Environment self-check** — at startup the application verifies
  `krfb-virtualmonitor`, the Wayland socket, `kscreen-doctor` health and systemd
  cgroup semantics, and reports any condition that would violate the two invariants
  above.
- **Login autostart** — a single application-level `.desktop` entry restores every
  screen marked *desired running*.
- **Desktop integration** — system tray with single-instance handling, light/dark
  theming that follows the system palette, and a live preview of the exact command
  line the GUI is about to execute.
- **11 UI languages** — English, Simplified and Traditional Chinese, Japanese,
  Korean, German, French, Spanish, Italian, Brazilian Portuguese and Russian. The
  interface follows the system language by default and can be switched without
  restarting from Settings → Language.
- **Configurable close behaviour** — the title-bar close button can minimize to the
  tray, quit the application, or ask each time (with a *remember my choice*
  checkbox). Also configurable under Settings → Closing the window.

## Requirements

| Component | Requirement |
|---|---|
| Session | **Wayland running KWin** (KDE Plasma). Virtual displays are a KWin-only feature; the application reports the reason at startup on unsupported sessions. |
| krfb | The `krfb` package on Arch / Debian / Ubuntu / Fedora — it provides `/usr/bin/krfb-virtualmonitor`. |
| kscreen | `kscreen-doctor` — strongly recommended. Used to read back the effective resolution and scale, and to correct overridden `--scale` values. |
| kwallet | `kwalletd6` (KDE Wallet) — the default password store. If the wallet subsystem is disabled in System Settings, the application falls back to the system keyring or the built-in vault. |
| Python | 3.11+ (source run only; the packaged build requires nothing preinstalled). |
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

`packaging/build.sh` produces a **single file** that runs on any Linux machine
without Python, a virtualenv or any installed dependency:

```bash
packaging/build.sh            # → dist/krfb-virtualmonitor-gui   (66 MB)
./dist/krfb-virtualmonitor-gui
```

That file unpacks approximately 170 MB into `$TMPDIR` on every launch (0.79 s
measured on the reference machine, against 0.21 s for an already-unpacked build).
A directory build avoids the repeated extraction:

```bash
packaging/build.sh --onedir   # → dist/onedir/krfb-virtualmonitor-gui/
```

Use the single file when one artifact has to be copied between machines; use
`--onedir` when the application is installed long-term, particularly with login
autostart, where every session pays the extraction cost. Both layouts can coexist
in `dist/`.

An AppImage was evaluated and not adopted: it requires `appimagetool` and libfuse2,
which Ubuntu 24.04 and later no longer install by default, and without FUSE it
extracts the bundle at launch exactly as the single-file build does.

To add the application to the KDE application menu and `~/.local/bin`:

```bash
packaging/install-desktop.sh              # install
packaging/install-desktop.sh --uninstall  # remove
```

The desktop launcher prefers a packaged build and falls back to running from source
through `.venv` if no bundle has been built.

## Usage

1. **Create a screen** — click *New* and specify a name, resolution (preset or
   custom), scale and port. The dialog shows the exact command line it will run.
2. **Start it** — the application launches `krfb-virtualmonitor` and waits (up to
   8 s) for KWin to report the `Virtual-<name>` output; only then is the screen
   considered running. If KWin overrode the requested scale, it is corrected through
   `kscreen-doctor` and the effective values are read back into the detail pane.
3. **Connect** — point any VNC client at `localhost:<port>`, using the password
   generated (or entered) in the dialog, which the detail pane can display.
4. **Close the GUI** — the screens keep running. Reopening the application re-adopts
   them and retains their logs.
5. **Adopt unmanaged processes** — a krfb instance started from a terminal is
   imported by *Scan*, password included, and becomes fully managed.

Login autostart is a toggle in *Settings*: when enabled, the GUI starts in the tray
at login and restores every screen marked as *desired running*. It writes **one
application-level entry**, not one `.desktop` file per screen: a per-screen entry
would have to embed `--password` in plaintext inside a `0644` desktop file, which
would negate the purpose of keyring storage. Starting the GUI instead keeps
passwords off disk entirely.

## Architecture

```
main.py                     Entry point: single-instance guard, theme, wiring
krfb_gui/
  constants.py              XDG paths, krfb parameter constraints, env whitelist
  models.py                 Screen (config) / Runtime (observed) / ProcInfo
  store.py                  Atomic JSON persistence (tmp + fsync + rename)
  proctools.py              Pure /proc readers: starttime, zombies, ports, argv
  envtools.py               Sanitized child environment — the ONLY way to spawn
  kscreen.py                kscreen-doctor parsing; effective output readback
  manager.py                Lifecycle: spawn/stop/state, adoption, self-check
  secrets/                  Password stores: KDE Wallet / system keyring /
                            built-in encrypted vault, behind one facade with
                            hard timeouts and a non-blocking fallback
  prefs.py                  UI preferences (language, close behaviour, and the
                            selected password store)
  i18n/                     Translation catalogs for 11 languages
  autostart.py              Single application-level .desktop autostart
  ui/                       Main window, screen list, detail pane, dialogs,
                            log viewer, theming, embedded SVG icons, vector art
tests/
  test_persistence.py       Two-process GUI-restart re-adoption test
  test_i18n.py              Translation catalog completeness and consistency
  test_vault.py             Built-in vault KDF, storage and reset semantics
  test_backends.py          Store selection, migration and merge logic
  test_child_env.py         Packaged-build child environment regression
  test_process_state.py     Zombie-process liveness regression
```

Two design rules apply throughout:

**Configuration and runtime state are stored separately.** `Screen` represents user
intent and is written only when settings change; `Runtime` represents observed
reality (pid, effective resolution) and is rewritten on every process event.
Combining them would rewrite the configuration file on every poll and allow two GUI
instances to overwrite each other's updates.

**Data modules do not import Qt.** `manager`, `store`, `proctools`, `kscreen`,
`envtools`, `secrets` and `autostart` are pure Python and independently testable;
`ui/` is the only layer that depends on PySide6.

## Storage Layout

| What | Where | Mode |
|---|---|---|
| Screen configuration (no passwords) | `~/.config/krfb-virtualmonitor-gui/screens.json` | `0600` |
| Runtime state (pids, effective values) | `~/.local/state/krfb-virtualmonitor-gui/runtime.json` | `0600` |
| Per-screen logs | `~/.local/state/krfb-virtualmonitor-gui/logs/<id>.log` | `0600` |
| Passwords | KDE Wallet / system keyring / built-in vault (selected in Settings) | — |
| Built-in vault (only if selected) | `~/.local/share/krfb-virtualmonitor-gui/vault.db` | `0600` |
| Autostart entry | `~/.config/autostart/krfb-virtualmonitor-gui.desktop` | `0644` |

Passwords are keyed by the screen's stable UUID in every store, which is also why
screen identity never depends on a pid. In KDE Wallet they are stored in the
standard *Passwords* folder. In the built-in vault each value is encrypted
individually as `screen_id + separator + password`, so a ciphertext copied between
rows is rejected; the master password is never stored, only a verifier derived from
a separate half of the scrypt output. A forgotten master password cannot be
recovered: resetting the vault deletes its contents after a confirmation that
requires solving an arithmetic challenge. Installations upgraded from an earlier
build can migrate anything still held by the previously used store from
Settings → Password storage; nothing is deleted unless explicitly requested.

## Testing

```bash
# Core requirement, phase A: start a screen, then exit
.venv/bin/python tests/test_persistence.py --phase a

# Phase B: a brand-new process rediscovers and re-adopts it
.venv/bin/python tests/test_persistence.py --phase b
```

The two phases run in **separate Python processes**, which is the only way to verify
that a virtual screen outlives the GUI and that a fresh GUI can take it over. Test
state is written to `/tmp/krfb-virtualmonitor-gui-test` (override with
`KRBFTEST_DIR`) and never touches the real configuration.

The remaining suites require neither a build nor a display server:

```bash
.venv/bin/python tests/test_i18n.py          # catalog completeness and consistency
.venv/bin/python tests/test_vault.py         # vault KDF, storage and reset
.venv/bin/python tests/test_backends.py      # store selection, migration and merge
.venv/bin/python tests/test_child_env.py     # packaged-build child environment
.venv/bin/python tests/test_process_state.py # zombies must not count as running
```

`test_i18n.py` parses every `tr()` call in the source tree and verifies that each
literal is present in all catalogs with matching placeholders. `test_vault.py` pins
the KDF parameters and verifies persistence, tamper rejection and reset semantics
across processes. `test_backends.py` covers store selection, the fallback chain,
migration and merge planning against in-memory backends. `test_child_env.py`
simulates PyInstaller's `LD_LIBRARY_PATH` injection, asserts that `kscreen-doctor`
and `krfb --version` still work under it, and scans the source tree for any
`subprocess` call that bypasses the sanitizer. `test_process_state.py` spawns real
zombie processes and asserts the liveness rules against them.

## Technical Notes

The following constraints were established on real hardware and are handled
explicitly by the implementation; most of them have a regression test.

### Zombie processes are reported as running

krfb exits within about 1 s of `SIGTERM` and KWin drops the virtual output within
about 3 s, but a process that has exited without being reaped remains as a zombie:
`/proc/<pid>/stat` still exists and `starttime` is unchanged, so an identity check
passes. Because krfb is a child of the GUI, it is only reaped opportunistically,
when the next child process is created.

*Handling:* liveness checks additionally reject the `Z` state character, and the
*Stop* action records the user's intent before identity verification. A zombie's
`/proc/<pid>/exe` is unreadable, so verification necessarily fails — but the intent
must still be honored, or the UI would raise a spurious crash notification.

### `--scale` is overridden by persisted KWin output configuration

KWin persists per-output configuration in `kwinoutputconfig.json`, and every newly
created virtual display receives the same UUID. Stale configuration for that UUID
takes precedence over the command-line request, so a requested scale of 1.25 or 1.5
takes effect as 1.75.

*Handling:* once the output appears, the scale is set explicitly with
`kscreen-doctor output.<connector>.scale.<value>`, after which the effective values
are read back. The UI displays requested and effective values separately and flags
mismatches.

### `kwalletd` unlock calls can block indefinitely

`open()` causes kwalletd to display its own password prompt, and D-Bus calls have no
timeout of their own. If the prompt cannot be displayed — headless session, systemd
unit, or a broken prompter — the call never returns.

*Handling:* probing uses only calls that cannot prompt (`isEnabled`, `isOpen`); every
wallet call runs on a daemon thread with a 2 s timeout; and anything that may prompt
is confined to the explicit unlock path, never the polling path. While the wallet
remains closed, the application uses the fallback chain described under *Features*.
The startup path never depends on the wallet succeeding. Daemon threads are used
rather than a `ThreadPoolExecutor`, because the executor joins its workers at
interpreter exit and would reintroduce the hang.

### VNC authentication uses 8 characters

krfb links against libvncserver, which implements classic VNC DES authentication:
only the first 8 characters of a password are used.

*Handling:* the generator produces exactly 8 characters and the UI states the limit.
Longer passwords would contribute no additional entropy.

### Passwords are exposed through `/proc/<pid>/cmdline`

Passwords are passed via `--password`, and `/proc/<pid>/cmdline` is world-readable
(mode `0444`). krfb offers neither a stdin/environment alternative nor loopback-only
binding, so this cannot be addressed at the wrapper level.

*Handling:* the UI discloses the exposure rather than implying otherwise.

### Process start does not imply that the output exists

krfb can report a portal error and still listen on its port. The only reliable
confirmation of success is KWin listing the `Virtual-<name>` output.

*Handling:* when `kscreen-doctor` is unavailable or unhealthy, the check degrades to
port listening — a weaker but honest signal, selected so that a working screen is
never reported as failed.

### Packaged builds inherit the bundle's library path

PyInstaller's Linux bootloader injects `LD_LIBRARY_PATH=<bundle>/_internal:...` into
the application's environment so that the bundled Qt6 can be loaded. Every child
process inherits it, and every helper this application executes
(`krfb-virtualmonitor`, `kscreen-doctor`, `systemctl`) is a system Qt program that
would then load a mismatched libQt6 and abort with `SIGABRT`. The consequence is
severe: `list_outputs()` returns nothing, start verification times out after 8 s,
the runtime record is discarded, and the process is orphaned.

*Handling:* a strict environment whitelist (`ENV_PASSTHROUGH` in `constants.py`)
strips `LD_LIBRARY_PATH`, `PYTHONPATH`, `QT_*` and related variables, and every
external command goes through `envtools.run_helper()`. A static check in
`tests/test_child_env.py` fails if a bare `subprocess` call reappears. If
`kscreen-doctor` is unusable, start verification degrades to port checking, and
identity is never cleared while the process is in fact alive.

### systemd cgroup cleanup can terminate all screens

`setsid()` defeats `SIGHUP` but not cgroup-level cleanup. If the GUI is started from
a unit configured with `KillMode=control-group` and `ExitType=main`, exiting the GUI
sends `SIGTERM` to the entire cgroup, terminating every virtual screen with it.

*Handling:* the condition is detected at startup and the remedy is reported
(`ExitType=cgroup`, or launching from the desktop launcher).

## Known Limitations

- **Wayland with KWin only.** Virtual monitors require compositor support that only
  KWin implements.
- **Passwords are readable through `/proc/<pid>/cmdline`** by other local users
  (krfb limitation, disclosed in the UI).
- **VNC authentication uses 8 characters**, regardless of password length.
- **In the packaged build**, the log viewer's *Open containing folder* button uses
  `QDesktopServices` → `xdg-open`, a Qt-internal fork that cannot receive a sanitized
  environment. It therefore still carries the bundle's `LD_LIBRARY_PATH`, and the
  file manager may fail to launch. The scope is limited to that one button.
- **Autostart must be toggled off and on again** when switching between a source run
  and a packaged build, because the `.desktop` entry records the path of the launcher
  that wrote it.

## License

Copyright (C) 2026 SkyDreamLG.

This program is free software: you can redistribute it and/or modify it under the
terms of the **GNU General Public License** as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but **WITHOUT ANY
WARRANTY**; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the [GNU General Public License](LICENSE) for details.
