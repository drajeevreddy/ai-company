# Traycer Desktop on Fedora 44 (session record, 2026-08)

## What was installed
- Traycer Desktop 1.1.10 via AppImage: `~/Applications/traycer-desktop.AppImage` (~176MB)
- Desktop entry: `~/.local/share/applications/traycer-desktop.desktop` (validated with desktop-file-validate)
- Icon: `~/.local/share/icons/traycer-desktop.png` (256x256, extracted from `usr/share/icons/hicolor/256x256/apps/` inside the AppImage)

## Why not the RPM
`sudo dnf install ./traycer-desktop-linux-x86_64.rpm` failed with:
```
file /usr/lib/.build-id/42/f633... from install of Traycer-1.1.10-1.x86_64
conflicts with file from package opencode-1.18.11-1.x86_64
```
Both packages ship the same build-id symlink. Do not `--force` or rpm-override — opencode is an actively used package. AppImage fallback avoids the package DB entirely.

## Working launch command
```bash
export WAYLAND_DISPLAY=wayland-0 DISPLAY=:0 XDG_RUNTIME_DIR=/run/user/1000
~/Applications/traycer-desktop.AppImage --no-sandbox --ozone-platform-hint=auto
```
User visually confirmed the window opened. Log noise that is BENIGN (do not chase):
- `HostRpcError ... agent.gui.listModels` — renderer queries failing until user signs in / configures agents; app still works.
- `gtk_widget_get_scale_factor: assertion failed` — cosmetic GTK warning on Wayland.

## Failure modes hit
1. First launch (no display env): process ran, renderer active, but no window anywhere — `/proc/<pid>/environ` had no DISPLAY/WAYLAND vars. Fix: export session env before exec.
2. Second launch after kill -9: "single-instance lock unavailable - quitting" — stale `~/.config/Traycer/Singleton{Lock,Socket,Cookie}`. Fix: delete the three Singleton files.
3. `--appimage-extract '*.png'` produced a broken symlink (top-level png is a symlink into usr/share/icons). Fix: extract the `usr/share/icons/*` subtree.

## Multi-agent orchestrator landscape (researched 2026-08)
| Tool | Cost | Notes |
|---|---|---|
| Traycer BYOA | $0 | Local-only, drives user's own CLI agents (claude-code, codex, opencode, cursor); no Traycer credits/markup on those paths. Paid: Sync $10/mo (cloud sync), Lite $20, Pro $40, Ultra $100 (inference credits, 20% markup on Traycer-provider models). |
| Vibe Kanban | Free OSS | `npx vibe-kanban`; kanban + worktrees; SUNSETTING (frozen development, still functional/self-hostable). |
| GitHub Agent HQ | $39/mo | Copilot Pro+ required; Claude/Codex/Copilot in GitHub/VS Code/Mobile; public preview. |
| Hermes native | free | `hermes chat -q`, tmux sessions, `-w` worktree mode, delegate_task. |

Downloads: `https://github.com/traycerai/traycer/releases/latest/download/traycer-desktop-linux-{x86_64.AppImage,amd64.deb,x86_64.rpm}`

## Setup steps for the user inside Traycer (post-install)
1. Sign in or use local/BYOA mode (free tier).
2. Settings -> Agents & Models: it auto-detects installed CLIs.
3. Create task/folder pointing at a repo — each agent gets its own git worktree.
