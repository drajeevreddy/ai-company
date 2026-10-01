---
name: android-tablet-second-screen-usb
description: Use when an Android tablet becomes a USB second screen.
---

# Android tablet as a USB extended second screen (GNOME Wayland)

Goal: a genuine *extended* display (drag windows onto it), carried over USB so latency is a ~1ms link, not Wi-Fi.

Do NOT reach for Miracast/GNOME Network Displays (Android can't act as a Wi-Fi Display sink), Samsung Second Screen (Windows-only), or Wayland screen extenders (wlr-randr/wayvnc are wlroots-only, Mutter has none).

## 1. Host: GNOME Remote Desktop in `extend` mode

The mode is a hidden gsettings key; the GUI only exposes mirroring.

```
gsettings set org.gnome.desktop.remote-desktop.rdp screen-share-mode 'extend'   # enum: mirror-primary | extend
gsettings set org.gnome.desktop.remote-desktop.rdp auth-methods "['credentials']"
gsettings set org.gnome.desktop.remote-desktop.rdp port 3389
gsettings set org.gnome.desktop.remote-desktop.rdp negotiate-port false
gsettings set org.gnome.desktop.remote-desktop.rdp view-only false
grdctl rdp set-credentials <user> <pass>
grdctl rdp enable
systemctl --user enable --now gnome-remote-desktop.service
```

**Pitfall: with no TLS cert the daemon logs "RDP TLS certificate and key not yet configured properly" and never binds 3389.** Generate one yourself (the GUI panel does this normally; grdctl has no generate command):

```
openssl req -new -newkey rsa:2048 -days 3650 -nodes -x509 -subj "/CN=second-screen" \
  -keyout ~/.local/share/gnome-remote-desktop/rdp-tls.key \
  -out    ~/.local/share/gnome-remote-desktop/rdp-tls.crt
grdctl rdp set-tls-cert ~/.local/share/gnome-remote-desktop/rdp-tls.crt
grdctl rdp set-tls-key  ~/.local/share/gnome-remote-desktop/rdp-tls.key
systemctl --user restart gnome-remote-desktop.service
```

RSA 2048 (not ECDSA). Confirm with `ss -tln | grep 3389` and `grdctl status` ("Unit status: active").
`grdctl` prints harmless freerdp `x509_utils_from_pem: BIO_new failed` noise before the cert exists.

### Verifying extend mode without the tablet

Any RDP client on the host (install `freerdp`, run `xfreerdp /v:127.0.0.1 /u:.. /p:.. /cert:ignore /size:1600x900`) will spawn the virtual monitor. Observe it in Mutter, not in the client log:

```
gdbus call --session --dest org.gnome.Mutter.DisplayConfig \
  --object-path /org/gnome/Mutter/DisplayConfig \
  --method org.gnome.Mutter.DisplayConfig.GetCurrentState
```

The monitors array gains a connector entry `('Meta-0', 'MetaVendor', 'Virtual remote monitor', ...)` and an extra logical monitor placed beside the real one (e.g. at x=1920). It disappears on disconnect. This is the fastest way to prove the whole stack works before touching the tablet.

## 2. Transport: USB (two routes)

**A. adb reverse — preferred.** Requires Developer options + one authorized RSA prompt.
```
adb reverse tcp:3389 tcp:3389
```
The tunnel maps the *tablet's* 127.0.0.1:3389 to the *host's* 127.0.0.1:3389, so the client targets `127.0.0.1`. Tunnels vanish on unplug — automate with a user service:

```
# ~/.config/systemd/user/tablet-screen-tunnel.service
[Service]
ExecStart=/bin/bash -c 'adb start-server >/dev/null 2>&1; while :; do adb wait-for-device; adb reverse tcp:3389 tcp:3389 >/dev/null 2>&1; sleep 5; done'
Restart=always
[Install]
WantedBy=default.target
```
`adb devices` showing `unauthorized` means the RSA popup has not been accepted on the tablet yet.

**B. USB tethering — no developer mode.** Tablet: Mobile hotspot and tethering > USB tethering. NetworkManager auto-creates the profile; the host gets e.g. 192.168.42.x. Client targets that IP. Note this pulls Android's network stack in for nothing the adb route doesn't already give you.

### Verify the tablet can really reach the server (differential test)

Run the connect test *inside the tablet* and compare against a dead port — an exit 0 alone proves nothing:
```
adb shell 'toybox nc -w 3 127.0.0.1 3388 < /dev/null >/dev/null 2>&1; echo exit=$?'   # expect 1
adb shell 'toybox nc -w 3 127.0.0.1 3389 < /dev/null >/dev/null 2>&1; echo exit=$?'   # expect 0
```
A bare TCP connect produces no handshake, so nothing appears in the GRD journal — don't read log silence as failure.

**Gotcha: a probe like that leaves a phantom monitor.** An abruptly-closed connection arriving through an adb reverse forward can stay ESTAB on the host side (`ss -tn 'sport = :3389'` shows the daemon owning a socket with bytes still queued and no peer process). GRD treats it as a live client, so the virtual monitor never tears down and Displays keeps showing a second monitor nobody is watching. Clear it with `adb kill-server && adb start-server && adb reverse tcp:3389 tcp:3389`, then re-check Mutter for a single connector. A real RDP client closing normally does not do this.

### Changing the password later

`grdctl rdp set-credentials <user> <newpass>` then `systemctl --user restart gnome-remote-desktop.service`. Verify both directions — old password must now return `ERRCONNECT_LOGON_FAILURE`, new one must reach a session (check for the `Meta-0` connector, not just a clean client log).

## 3. Harden before you log off

GRD binds `*:3389`, and Fedora's default `FedoraWorkstation` firewalld zone leaves 1025-65535/tcp open, so the desktop is RDP-reachable from the whole LAN with those credentials. Since USB needs only loopback, drop the LAN:
```
sudo firewall-cmd --permanent --add-rich-rule="rule family=ipv4 source address=<wifi-subnet>/24 port port=3389 protocol=tcp drop"
sudo firewall-cmd --reload
```
Scope the drop to the Wi-Fi subnet (not a blanket rule) so a USB-tethering route from 192.168.42.x keeps working.

## 4. Tablet side

### "Touch works but there is no mouse pointer" — expect this, and fix it client-side

In RDP the pointer is not part of the video stream: it is a separate cursor object the server sends. **aRDP does not render server cursor shapes at all — it only ever draws its own local cursor** (maintainer-confirmed limitation, issue #426). So on the tablet the host pointer appears frozen/absent while touch keeps working, because touch is *absolute* (the tap position is the position — no cursor needed) whereas a pointer needs a rendered cursor.

Fix: aRDP connection → Advanced Settings → **Cursor Mode → "Local mouse pointer (select if pointer is invisible)"**. Its own help text: "If the pointer is invisible, select this to force it to be drawn by the app." If clicks land offset from the cursor, also enable "Disable pointer offset correction".

Input modes (aRDP's own text):
- *Direct, Hold/Swipe Pan* — "Control the mouse directly through touch." Tap anywhere = left-click at that point (absolute), two-finger tap = right-click, three-finger = middle, long-press = drag.
- *Simulated Touchpad* — swipe to move pointer, tap = left-click, two-finger tap = right-click, two-finger swipe = scroll, long tap = drag and drop. This sends **relative** motion; GRD 50 does support it (the installed daemon exports `NotifyPointerMotionRelative` / `handle-notify-pointer-motion-relative`), but per the upstream MR relative input is a *grab* mode: the client owns the cursor, so the client-side cursor is all you get. Verify support on any given GRD build with `strings /usr/libexec/gnome-remote-desktop-daemon | grep -i relative`.

Diagnose which input mode is live from the tablet without touching the app: `adb logcat -d | grep TouchInputHandler` — bVNC/aRDP logs the active handler (`TouchInputHandlerTouchpad`, `TouchInputHandlerDirectDragPan`, `TouchInputHandlerSingleHanded`).

- Client: **aRDP: Secure RDP Client** (Play Store) or **aFreeRDP** (F-Droid). Microsoft's Remote Desktop/Windows App was retired on Android.
- Host `127.0.0.1`, port 3389, GRD credentials (these are GRD's own, NOT the system account password). Accept the self-signed certificate warning.
- Set resolution to the tablet's *physical landscape* size — read it exactly with `adb shell wm size` (e.g. `1200x2000` portrait means `2000x1200` in the client). The virtual monitor is created at the client's requested resolution, so matching it gives 1:1 pixels and no scaling.
- Latency knobs: 32bpp colour, enable the H.264/GFX (RemoteFX) pipeline, disable client-side scaling.

## 5. Daily use

Connect the cable -> virtual monitor appears to the right of the laptop panel; rearrange under Settings > Displays like any monitor. Disconnect -> windows return to the primary and the virtual monitor is destroyed.
