#!/usr/bin/env bash
# appimage-to-desktop.sh — integrate an AppImage into the GNOME desktop
# Usage: appimage-to-desktop.sh <AppImage-path> <AppName> [WMClass]
set -euo pipefail

SRC="${1:?Usage: $0 <AppImage-path> <AppName> [WMClass]}"
NAME="${2:?Missing AppName}"
WMCLASS="${3:-$NAME}"

[ -f "$SRC" ] || { echo "ERROR: $SRC not found" >&2; exit 1; }

HOME_DIR="$HOME"
APPS_DIR="$HOME_DIR/Applications"
ICONS_DIR="$HOME_DIR/.local/share/icons"
DESKTOP_DIR="$HOME_DIR/.local/share/applications"
mkdir -p "$APPS_DIR" "$ICONS_DIR" "$DESKTOP_DIR"

TARGET="$APPS_DIR/${NAME}.AppImage"
mv "$SRC" "$TARGET"
chmod +x "$TARGET"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
( cd "$WORK" && "$TARGET" --appimage-extract 'usr/share/icons/*' >/dev/null 2>&1 ) || {
  echo "WARN: no icon tree extracted; continuing without icon" >&2
}

ICON_PNG=""
if [ -d "$WORK/squashfs-root/usr/share/icons" ]; then
  ICON_PNG=$(find "$WORK/squashfs-root/usr/share/icons" -name '*.png' \
    | sort -t/ -k99 2>/dev/null | head -1)
  # prefer largest dimension available
  for size in 512x512 256x256 128x128 64x64; do
    CAND=$(find "$WORK/squashfs-root/usr/share/icons" -path "*$size*" -name '*.png' | head -1)
    [ -n "$CAND" ] && ICON_PNG="$CAND" && break
  done
fi

ICON_KEY="terminal"
if [ -n "${ICON_PNG:-}" ] && cp "$ICON_PNG" "$ICONS_DIR/${NAME}.png" 2>/dev/null; then
  ICON_KEY="$NAME"
fi

cat > "$DESKTOP_DIR/${NAME}.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=$NAME
Exec=$TARGET --no-sandbox %U
Icon=$ICON_KEY
Terminal=false
Categories=Development;
StartupWMClass=$WMCLASS
EOF

update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
gtk-update-icon-cache -f "$ICONS_DIR" 2>/dev/null || true
desktop-file-validate "$DESKTOP_DIR/${NAME}.desktop"

echo "OK: '$NAME' installed."
echo "  Binary : $TARGET"
echo "  Icon   : $ICONS_DIR/${NAME}.png (${ICON_KEY})"
echo "  Entry  : $DESKTOP_DIR/${NAME}.desktop"
echo "Launch from GNOME: Super → type '$NAME'. If launched from a script, also:"
echo "  export WAYLAND_DISPLAY=wayland-0 DISPLAY=:0 XDG_RUNTIME_DIR=/run/user/1000"
