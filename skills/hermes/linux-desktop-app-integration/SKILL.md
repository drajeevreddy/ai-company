---
name: linux-desktop-app-integration
description: "Install/launch GUI desktop apps on Fedora GNOME Wayland."
version: 1.0.0
---

# Linux Desktop App Integration (Fedora - GNOME - Wayland)

Getting a third-party desktop app installed, visible in the GNOME app grid, and launchable from Hermes background shells on this machine.

## Install-path decision order
1. For `.rpm`: try `sudo dnf install -y ./pkg.rpm` first. SUDO_PASSWORD lives in the Hermes env file, so plain `sudo` works without prompting; piping passwords to `sudo -S` is BLOCKED by the terminal security layer — don't retry that shape. If dnf reports a file conflict (e.g. two packages shipping the same `/usr/lib/.build-id/...` symlink — happened with Traycer vs opencode), do NOT force/override files owned by another installed package. Fall back to manual extraction or AppImage.
2. For `.deb` on Fedora/RHEL (no native package manager): use `dpkg-deb --extract` to unpack into a temp dir, then place files manually under `~/Applications/` with a wrapper in `~/.local/bin/` (see "Manual .deb extraction" below). Do not try `alien` — it frequently fails on complex Electron apps and produces no cleaner result than manual extraction.
3. For AppImage: park in `~/Applications/` (see "AppImage → app-grid integration" below).

## Manual .deb extraction (Fedora/RHEL)
Used when a vendor ships only a `.deb` (Claude Desktop did this). The goal: get the binary tree under `~/Applications/`, the executable on PATH via a wrapper, icons into hicolor, and the `.desktop` entry registered — without running `dpkg -i` (which would own files in `/usr/`).
1. `dpkg-deb --extract ~/Downloads/foo.deb /tmp/foo-extract/`
2. Copy the lib tree: `cp -r /tmp/foo-extract/usr/lib/foo/* ~/Applications/foo/`
3. Write a wrapper script `~/.local/bin/foo` that exec's the binary at its `~/Applications/` path with `"$@"`. `chmod +x` it.
4. Copy icons: `for size in 16x16 32x32 48x48 128x128 256x256; do cp /tmp/foo-extract/usr/share/icons/hicolor/$size/apps/foo.png ~/.local/share/icons/hicolor/$size/apps/; done`. Also copy the flat icon to `~/.local/share/icons/foo.png`.
5. Copy the `.desktop` file from `/tmp/foo-extract/usr/share/applications/` into `~/.local/share/applications/`. Edit each `Exec=` line to point to the absolute wrapper path in `~/.local/bin/foo` (the .deb's entries assume `/usr/bin/` which won't exist). `StartupWMClass` is already correct in the vendor's file — read it, don't invent it.
6. `update-desktop-database ~/.local/share/applications/ && gtk-update-icon-cache -f ~/.local/share/icons/ && desktop-file-validate <entry>`
7. Clean up the temp dir.

## AppImage -> app-grid integration
1. `curl -L -o ~/Applications/<name>.AppImage <url> && chmod +x <file>`. Move the file to `~/Applications/` first; the next step extracts relative to CWD, so if you're in `/tmp` the extract ends up in `/tmp/squashfs-root/` and the temp cleanup nukes your reference files.
2. Icon: `cd ~/Applications && ./<name>.AppImage --appimage-extract 'usr/share/icons/*'`, then copy the 256x256 (or 1024x1024) png to `~/.local/share/icons/<name>.png` AND `~/.local/share/icons/hicolor/<size>/apps/<name>.png`. PITFALL: extracting a top-level `*.png` glob can yield a broken symlink (icon is a symlink into usr/share/icons) — extract the `usr/share/icons/*` directory instead. Clean up the `squashfs-root` dir afterwards.
3. If the AppImage ships a `.desktop` file (check `squashfs-root/<name>.desktop`), use it as the source of truth for `Name`, `StartupWMClass`, `Categories`, `Comment`, and `Exec` — only the `Exec=` line needs rewriting to point to the absolute AppImage path. Don't invent `StartupWMClass`; a wrong value means the GNOME dock shows a generic/blank icon instead of the app's.
4. Write the `.desktop` entry into `~/.local/share/applications/`. Electron apps need `--no-sandbox` in Exec.
5. Finish with `update-desktop-database ~/.local/share/applications/ && gtk-update-icon-cache -f ~/.local/share/icons/ && desktop-file-validate <entry>` — validation must pass.

## Launching GUI apps from a Hermes background shell
The background shell has NO display environment. Export before exec:
```
export WAYLAND_DISPLAY=wayland-0 DISPLAY=:0 XDG_RUNTIME_DIR=/run/user/1000
```
If sockets differ later, read current values from the live session: `tr '\0' '\n' < /proc/$(pgrep -x gnome-shell)/environ | grep -E 'WAYLAND|DISPLAY|XAUTH'`. For Electron add `--ozone-platform-hint=auto`. After an unclean exit, clear stale `~/.config/<App>/Singleton*` locks or the app quits immediately with "single-instance lock unavailable".

## Verify it really opened
- `pgrep -f '.mount_<name>'` confirms the process is alive; tail the app's log for renderer activity.
- If cua-driver screen capture comes back empty (0x0), don't retry blindly — fall back to process/log checks and ask the user to confirm the window visually. Never claim the window opened without one of those confirmations.

## Uninstalling (the reverse playbook)
The install half above is the happy path. The user uninstalls third-party
apps as often as they install them, and skipping steps leaves systemd
services, port listeners, or config dirs to silently come back on next
login. When asked to uninstall, follow the 6-step sequence in
`references/uninstall-third-party-app.md` — inventory → secrets check →
stop service → delete in order → verify → report. Two real uninstalls
(Traycer, OmniRoute) verified the sequence in 2026-09.

## RAM-usage triage: dev-mode vs production mode
If the user reports a heavy "installed" app, the cause is often `npm run
dev` keeping source maps and the full module graph in process memory, not
the app being inherently large. Diagnostic path: identify the heavy PID →
read `/proc/<pid>/cwd` for the project → check `package.json` scripts →
look for `NODE_ENV=production` set but `next dev` launched anyway. The fix
is `npm run build && npm start` (production mode), which typically uses
200–400 MB instead of multi-GB for a Next.js app of any size. If the user
wants the app removed entirely, use the uninstall sequence above; if they
want it lighter, point them at production-mode startup.

## References
- `references/traycer-install-fedora44.md` — full Traycer session record: RPM conflict details, working launch command, benign log noise, and the 2026-08 multi-agent orchestrator landscape (pricing, sunset status).
- `references/uninstall-third-party-app.md` — the 6-step uninstall sequence (inventory → secrets → stop → delete → verify → report), with a side-by-side of the Traycer and OmniRoute teardowns and the "do not" list learned the hard way.
