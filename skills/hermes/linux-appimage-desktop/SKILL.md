---
name: linux-appimage-desktop
description: "Use when installing a downloaded .AppImage as a desktop app."
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [linux, desktop, fedora, gnome, appimage, installation]
---

# AppImage → Desktop Application Integration

Recurring pattern on this host (Fedora, GNOME/Wayland, x86_64): user downloads an
AppImage and wants it in the GNOME app grid like a native app. Two full installs
done this way (Traycer, Superset). Prefer this over distro packages unless the
RPM installs cleanly — see RPM caveat below.

## Standard procedure

0. **`chmod +x ~/Downloads/foo.AppImage` FIRST.** Browsers save AppImages
   non-executable; every `--appimage-extract` then fails with exit 126 (
   "command not found"/permission). Do this before anything else.
1. **Park the binary**: `mv ~/Downloads/foo-1.0-x86_64.AppImage ~/Applications/foo.AppImage`
   (`~/Applications` is this host's convention) and `chmod +x`.
2. **Extract the icon**:
   ```bash
   cd ~/Applications && ./foo.AppImage --appimage-extract 'usr/share/icons/*'
   # pick the largest: squashfs-root/usr/share/icons/hicolor/{512x512,256x256}/apps/*.png
   cp .../apps/icon.png ~/.local/share/icons/foo.png && rm -rf squashfs-root
   ```
   PITFALL: `--appimage-extract '*.png'` (top-level glob) often yields only a
   BROKEN SYMLINK into usr/share/icons — the target isn't extracted. Always pull
   the whole `usr/share/icons/*` tree.

   PITFALL: `--appimage-extract` with a glob that exists NOWHERE in the image
   exits 1 and extracts nothing, silently. `ls squashfs-root/` after every
   pattern extract instead of trusting the exit code.

   Reading the app's own desktop file needs only
   `--appimage-extract '*.desktop'` — the entry sits at the image root, so it
   comes out in one second. Reserve the full bare `--appimage-extract`
   (~2.5x the AppImage size) for browsing image contents nothing else reaches.

   PITFALL: `--appimage-extract` writes into the shell's CWD, and `rm -rf`-ing
   a directory the session is standing in BREAKS the terminal session: every
   later command dies with exit 126 / `getcwd: cannot access parent
   directories`, and file-editing tools refuse with a stale-cwd error. `cd ~`
   before deleting the scratch tree, or extract under an absolute path while
   the session stays elsewhere.
3. **Write the .desktop entry** to `~/.local/share/applications/foo.desktop`.

   Get the authoritative values from the app's OWN desktop file, which sits at
   the extract root, `squashfs-root/<name>.desktop` — it gives the real `Name`,
   `StartupWMClass`, `Categories`, `MimeType` and `Comment`. Do not invent
   `StartupWMClass`: a wrong value means the GNOME dock shows a generic/blank
   icon instead of the app's.

   ```ini
   [Desktop Entry]
   Type=Application
   Name=Foo Bar
   Exec=/home/<user>/Applications/foo.AppImage --no-sandbox %U
   Icon=foo
   Terminal=false
   Categories=Development;
   StartupWMClass=Foo Bar
   MimeType=x-scheme-handler/foo;          # only if the bundled entry has one
   ```

   - **Display name with a space** (e.g. `Munder Difflin`): the script below
     defaults WMClass to the filename-safe name and breaks the WMClass match.
     Install by hand — hyphenated filenames (`Munder-Difflin.AppImage`,
     `munder-difflin.desktop`, `munder-difflin.png`) with `Name=` and
     `StartupWMClass=` keeping the space.
   - Electron apps need `--no-sandbox` on this box or they fail to start.
   - `Categories=` accepts REGISTERED values only (`Development`, `Science`,
     `Utility`, ...). `DataScience` failed validation; run `desktop-file-validate`
     before telling the user it's done.
   - `desktop-file-validate` can exit 0 while still printing a `hint:` line, so
     a clean exit code is not a clean bill of health. Copy the bundled entry's
     `Categories` verbatim (one main category) rather than widening it — adding
     a second one (`AudioVideo;Utility;`) earns "contains more than one main
     category; application might appear more than once in the application
     menu".
4. **Register**: `update-desktop-database ~/.local/share/applications/ &&
   gtk-update-icon-cache -f ~/.local/share/icons/ && desktop-file-validate <entry>`.
   GNOME picks up changes live; Super-key search finds it immediately.

   Icon lookup: besides `~/.local/share/icons/<name>.png`, ALSO copy to
   `~/.local/share/icons/hicolor/512x512/apps/<name>.png`. GTK resolves named
   icons from the hicolor tree; the flat path alone is unreliable.
   `gtk-update-icon-cache` printing "No theme index file" is harmless — there is
   no `index.theme` in the user icon dir and lookup still succeeds by path.

## Launching from the agent's background shell (Wayland)

GUI apps launched from Hermes terminal/background sessions have NO DISPLAY and
run headless-invisible. Export the user session's environment, then `exec` the
AppImage as a tracked background process — `terminal(background=true,
command="export WAYLAND_DISPLAY=...; exec <path> --no-sandbox")`. Do NOT wrap
the launch in `setsid`/`nohup`/`&`: the terminal tool rejects shell-level
background wrappers and the call never runs. Confirm the socket name first
with `ls /run/user/$(id -u) | grep wayland`.

```bash
export WAYLAND_DISPLAY=wayland-0 DISPLAY=:0 XDG_SESSION_TYPE=wayland \
       XDG_RUNTIME_DIR=/run/user/1000
```

Electron: add `--ozone-platform-hint=auto`. Clear stale singleton locks before
a test launch (see Unclean-shutdown locks).

Readiness check for an Electron AppImage: the launch is REAL when `pgrep -af`
shows the binary running from `$TMPDIR/.mount_<Name>XXXX/` with
`--type=gpu-process` / `--type=renderer` and the network + audio utility
children. Only the parent runtime process present — or an empty log and no
children after ~10s — means it died. Match on `mount_<Name>`; do NOT hardcode
`/tmp/.mount_`, the mount point is wherever `$TMPDIR` points (on this host that
is the Hermes scratch dir, not `/tmp`).
Note `pgrep -f '<something>'` also matches your own wrapper shell; ignore the
`bash -c ... eval ...` line in the output.

### Proving a window is actually on screen

Use positive OS-level evidence rather than asking the user to look:

- **Wayland surface**: `ls -l /proc/<main-pid>/fd | grep -E
  'wayland-cursor|wayland-keymap'`. The main process holding
  `memfd:wayland-cursor` and `mutter-anonymous-file-wayland-keymap` means it
  created a surface and pulled the compositor's keymap — a window is mapped.
  Stronger than pgrep alone.
- **End-to-end entry test**: `gtk-launch <desktop-name>` (the exact path GNOME
  uses) with the session env exported. Exit 0 plus the app's own startup log
  proves `Exec=`/`Icon=` actually resolve. Safe while the app is already up:
  single-instance Electron apps just forward to the running instance.
- Say in the reply which signal you checked, and ask the user to confirm
  visually — never imply a pixel check you did not take.

## Unclean-shutdown locks

Killed Electron AppImages leave singleton locks that make the next launch quit
instantly ("single-instance lock unavailable"): delete
`~/.config/<AppName>/Singleton{Lock,Socket,Cookie}` then relaunch.

## Process cleanup footgun

`pkill -9 -f traycer` matches YOUR OWN wrapper shell command line (the eval'd
command contains the pattern) and kills the shell mid-call (-9/-15 exit, empty
output). Match on something not present in your own cmdline, e.g.
`pkill -f 'mount_<name>|Applications/<name>.AppImage'`, or pgrep first and kill
by PID list.

## RPM caveat

Distro RPM/DEB builds of the same app can hard-fail on build-id file conflicts
with unrelated installed packages (Traycer RPM collided with `opencode`). Check
`rpm -qpi` conflicts before choosing RPM; the AppImage route sidesteps packaging
entirely and is the default recommendation here.

## Script

`scripts/appimage-to-desktop.sh <AppImage-path> <AppName> [WMClass]` automates
steps 1–4 including icon-size selection and validation.
