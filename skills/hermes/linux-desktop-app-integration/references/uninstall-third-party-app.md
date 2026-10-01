# Uninstalling a third-party app on Fedora GNOME (session record, 2026-09)

The install half of this skill covers getting an app on the box. This file
records the *reversal* playbook for getting a third-party app fully OFF the
box — verified clean across two uninstalls in one session (Traycer 1.1.10
Electron app, then OmniRoute 3.8.50 Next.js dev server).

The order matters. Skipping steps is what leaves systemd services, port
listeners, and config dirs behind to silently come back.

## The 6-step sequence (worked both times)

1. **Inventory FIRST, before deleting anything.** Find every artifact location
   so nothing is missed. For an Electron or AppImage app, expected surfaces:
   ```bash
   pgrep -af <name>                            # running processes
   systemctl --user list-units --type=service  # systemd user services
   find /home/$USER -maxdepth 4 -iname '*<name>*' -not -path '*/node_modules/*'
   find ~/.local/share/applications -iname '*<name>*'
   find ~/.config -maxdepth 2 -iname '*<name>*'
   ls -la ~/Applications/ ~/Documents/ ~/Downloads/ 2>/dev/null | grep -i <name>
   ```
   For Traycer this surfaced 9 locations including a systemd user service, a
   desktop entry, an icon, an AppImage copy, a 3-GB Electron config tree, a
   host runtime, a session log cache, and a CLI cache. Missing any one means
   the next login resurrects something.

2. **Check for secrets BEFORE deleting.** Electron / Next.js / SaaS proxy apps
   almost always have an `.env`, a SQLite with encrypted keys at rest, or an
   `oauth/` directory. Grep first:
   ```bash
   grep -rE '(SECRET|KEY|TOKEN|PASSWORD)\s*=' <app>/.env 2>/dev/null
   ls -la <app>/.env <app>/storage.sqlite <app>/oauth/ 2>/dev/null
   ```
   For OmniRoute: `~/OmniRoute/.env` had `JWT_SECRET` + likely 290 provider
   API keys, and `~/.omniroute/server.env` had `STORAGE_ENCRYPTION_KEY`. If
   the user has no copy elsewhere, route to a backup folder; do not just wipe
   silent.

3. **Stop service, then processes.** In this order — stopping the service
   cleanly avoids the supervisor immediately respawning the process you
   just killed:
   ```bash
   systemctl --user stop <name>.service
   systemctl --user disable <name>.service  # removes the wants/ symlink too
   pkill -f <name>                          # catches anything else
   sleep 1
   pgrep -af <name>                         # MUST return empty
   ```

4. **Delete in this order: service file → caches → app dirs → downloads.**
   Top-down keeps the system from re-registering a service after you
   removed the dir it pointed at.
   ```bash
   rm -v ~/.config/systemd/user/<name>.service
   rm -rfv ~/.cache/<vendor>/-<path-to>-<name>/  # MCP/CLI logs if any
   rm -rfv ~/<app-dir>/ ~/.config/<Name>/ ~/.config/<name>/
   rm -v ~/Applications/<name>.AppImage ~/Documents/<name>*.{AppImage,rpm,deb} ~/Downloads/<name>*.{AppImage,rpm,deb}
   ```

5. **Verify clean across all the surfaces from step 1.** Any leftover
   means you missed a step:
   ```bash
   pgrep -af <name>                                   # no procs
   systemctl --user list-units --type=service | grep <name>   # no service
   find /home/$USER -iname '*<name>*' -not -path '*/.hermes/*'
   ss -ltn | grep <port>                              # ports free
   df -h /home | head -2                               # disk freed
   ```
   The `-not -path '*/.hermes/*'` filter is important — Hermes skill
   references often mention the app by name without being the app.

6. **Report disk freed and RAM delta.** These are the two user-visible wins
   and they confirm the work landed. Use `du -sh` of the dir you removed
   pre-delete (capture before step 4), then `df -h` post.

## Two uninstalls in this session, side by side

| Aspect            | Traycer (Electron)                          | OmniRoute (Next.js dev server)                |
|-------------------|---------------------------------------------|-----------------------------------------------|
| Total size        | ~3 GB (mostly Electron config + host runtime) | ~22 GB (18 + 4.5 repos, 25 MB config)        |
| Service file      | `~/.config/systemd/user/ai.traycer.host.service` | `~/.config/systemd/user/omniroute.service` |
| Desktop entry     | `~/.local/share/applications/traycer-desktop.desktop` | none                                  |
| Systemd linger    | Used `enable-linger` to survive logout — was already set | not set                          |
| Surprises         | 3 separate locations for "the same app" (Electron user data + AppImage + 184MB binary) | Two copies of the repo (main + under `~/doccare/`) |
| Secrets           | none in cleartext on disk (auth was OAuth + remote) | `.env` with JWT_SECRET, `server.env` with STORAGE_ENCRYPTION_KEY |
| Confirmation      | RAM 9.6G→2.7G, 12G available              | Disk 36% used, 187G free on /home            |

## What NOT to do (learned the hard way this session)

- Don't run `rm -rf` on the home dir tree without first running the inventory
  step — `~/.traycer/cli/bin/traycer` is a 122 MB binary that won't show up
  in any single obvious search. The full `find` before the delete caught it.
- Don't skip the `systemctl --user disable` before `rm` — the service file
  will be re-created by the next provider start if the symlink in
  `default.target.wants/` is still live.
- Don't trust "no process" alone. The Traycer AppImage was killed but its
  supervisor (`traycer host start`) was a separate process under a different
  name. `pkill -f '<name>'` with a grep is needed, not just `pkill <name>`.
- The `desktop-file-validate` step at install time has no uninstall twin, but
  `update-desktop-database ~/.local/share/applications/` should be run AFTER
  removing a `.desktop` entry so the app grid stops advertising it.
- Mass deletions in this sequence trip the terminal's "ransomware-like burst
  deletion" warning (15+ files in 20s). Expect to approve each step. Plan
  the commands so each `rm` is one logical batch (e.g. all caches, all
  config, all app dirs) and approve them as such.

## Disambiguating "the app" from "skill docs about the app"

The Hermes skill library has docs that *reference* apps without being them.
E.g. `~/.hermes/skills/devops/linux-desktop-app-integration/references/traycer-install-fedora44.md`
stays on disk after Traycer is uninstalled — it's a session record, not part
of Traycer. Same with `~/.hermes/skills/devops/ai-routing-gateway/` and
OmniRoute. These should NOT be deleted unless the user asks to drop the
skill entirely.
