"""Pillow poster helper kit — copy-and-adapt for direct-to-PNG social graphics.

Companion to the pillow-graphics skill. CRITICAL: draw everything on a transparent
overlay (new_canvas) and alpha_composite onto the background at save time
(composite). Do NOT draw alpha fills directly on an RGBA canvas and convert("RGB")
— Pillow drops the alpha, so ghosts/textures render opaque.

Usage sketch:
    ov, d = new_canvas(W, H, ghost="01")
    ...draw with d...
    composite(ov, W, H).save("post1.png", quality=95)
"""
from PIL import Image, ImageDraw, ImageFont

# ---------- palette (tweak per brand) ----------
INK_TOP = (10, 29, 37); INK_BOT = (6, 18, 24)   # vertical ink gradient
CARD    = (16, 42, 52); CARD2  = (11, 30, 38)
WHITE   = (236, 246, 246); MUTED = (146, 180, 187)
TEAL    = (45, 212, 191); AMBER = (245, 190, 110); RED = (248, 113, 113)

# ---------- fonts ----------
_MONTSERRAT = "/usr/share/fonts/julietaula-montserrat-fonts/Montserrat-"
def F(style, size):
    """style in {Black, ExtraBold, Bold, SemiBold, Medium, Regular, Light, Thin}."""
    return ImageFont.truetype(_MONTSERRAT + style + ".otf", size)

def A(c, a):
    return (c[0], c[1], c[2], a)  # color + alpha

# ---------- canvas / compositing ----------
def vgrad(w, h, top, bot):
    img = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(1, h - 1)
        img.putpixel((0, y), tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    return img.resize((w, h), Image.BILINEAR)

def new_canvas(w, h, ghost=None):
    """Transparent overlay + draw context. Ghost = big faint page number."""
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov, "RGBA")
    if ghost:
        d.text((w - 8, h * 0.17), ghost, font=F("Black", w // 3),
               fill=A(WHITE, 11), anchor="rm")
    return ov, d

def composite(ov, w, h, top=INK_TOP, bot=INK_BOT):
    return Image.alpha_composite(vgrad(w, h, top, bot).convert("RGBA"), ov).convert("RGB")

# ---------- text ----------
def wrap(draw, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if draw.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = wd
    if cur: lines.append(cur)
    return lines

def wrap_rich(draw, segs, font, maxw):
    """segs = [(text, color), ...]; returns lines of [(word, color), ...]."""
    words = [(wd, c) for text, c in segs for wd in text.split()]
    lines, cur = [], []
    for wd, c in words:
        test = cur + [(wd, c)]
        if draw.textlength(" ".join(x[0] for x in test), font=font) <= maxw:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = [(wd, c)]
    if cur: lines.append(cur)
    return lines

def draw_rich_lines(draw, x, y, lines, font, lh):
    for line in lines:
        xx = x
        for wd, c in line:
            draw.text((xx, y), wd, font=font, fill=c)
            xx += draw.textlength(wd + " ", font=font)
        y += lh
    return y

def tracked(draw, xy, text, font, fill, tracking=0, cy=None):
    """Letter-spaced text; cy = vertical center for anchor 'lm' style alignment."""
    x, y = xy
    for ch in text:
        draw.text((x, cy if cy is not None else y), ch, font=font, fill=fill,
                  anchor="lm" if cy is not None else None)
        x += draw.textlength(ch, font=font) + tracking
    return x

def chip(draw, x, y, text, font, fg, bg, padx=26, pady=15, tracking=4):
    """Pill label; returns (width, height)."""
    tw = sum(draw.textlength(ch, font=font) for ch in text) + tracking * (len(text) - 1)
    asc, desc = font.getmetrics()
    h = asc + desc
    draw.rounded_rectangle([x, y, x + tw + 2 * padx, y + h + 2 * pady],
                           radius=(h + 2 * pady) // 2, fill=bg)
    tracked(draw, (x + padx, y + pady), text, font, fg, tracking)
    return tw + 2 * padx, h + 2 * pady

# ---------- icons (primitives only, no assets) ----------
def plus_sign(d, cx, cy, r, color, width=None):
    w = width or max(4, r // 3)
    d.line([cx - r, cy, cx + r, cy], fill=color, width=w)
    d.line([cx, cy - r, cx, cy + r], fill=color, width=w)

def xmark(d, cx, cy, r, color):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=A(color, 26))
    w = max(3, r // 3)
    d.line([cx - r * 0.42, cy - r * 0.42, cx + r * 0.42, cy + r * 0.42], fill=color, width=w)
    d.line([cx - r * 0.42, cy + r * 0.42, cx + r * 0.42, cy - r * 0.42], fill=color, width=w)

def check(d, cx, cy, r, color):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=A(color, 26))
    w = max(3, r // 3)
    d.line([cx - r * 0.45, cy, cx - r * 0.1, cy + r * 0.38], fill=color, width=w)
    d.line([cx - r * 0.1, cy + r * 0.38, cx + r * 0.5, cy - r * 0.38], fill=color, width=w)

def arrow(d, x, y, length, color, w=6):
    d.line([x, y, x + length, y], fill=color, width=w)
    hd = length * 0.22
    d.line([x + length, y, x + length - hd, y - hd * 0.9], fill=color, width=w)
    d.line([x + length, y, x + length - hd, y + hd * 0.9], fill=color, width=w)

def cloud(d, cx, cy, s, bg=CARD, outline=None):
    outline = outline or A((236, 246, 246), 70)
    for x0, y0, x1, y1 in [(-1.55, -0.45, -0.35, 0.5), (-0.5, -0.8, 0.45, 0.35),
                           (0.15, -0.55, 1.15, 0.45)]:
        d.ellipse([cx + x0 * s, cy + y0 * s, cx + x1 * s, cy + y1 * s],
                  fill=bg, outline=outline, width=2)
    d.rectangle([cx - 1.55 * s, cy + 0.12 * s, cx + 1.15 * s, cy + 0.5 * s],
                fill=bg, outline=outline, width=2)

def server(d, x, y, w, h, accent=TEAL):
    d.rounded_rectangle([x, y, x + w, y + h], radius=22, fill=CARD,
                        outline=A(WHITE, 50), width=2)
    d.rounded_rectangle([x + 10, y + 10, x + w - 10, y + 58], radius=12, fill=A(accent, 26))
    sy, sh, gap = y + 74, 42, 14
    for i in range(4):
        ry = sy + i * (sh + gap)
        d.rounded_rectangle([x + 16, ry, x + w - 16, ry + sh], radius=8,
                            fill=CARD2, outline=A(WHITE, 25), width=1)
        d.ellipse([x + 34, ry + sh / 2 - 7, x + 48, ry + sh / 2 + 7], fill=accent)
        for v in range(3):
            vx = x + 66 + v * 42
            d.line([vx, ry + sh / 2 - 10, vx, ry + sh / 2 + 10], fill=A(WHITE, 40), width=3)

def lock_badge(d, cx, cy, r, accent=TEAL, ink=(6, 18, 24)):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=accent)
    d.rounded_rectangle([cx - 8, cy - 22, cx + 8, cy - 6], radius=6, fill=ink)
    d.ellipse([cx - 12, cy - 14, cx + 12, cy + 14], fill=ink)
    d.ellipse([cx - 4, cy - 2, cx + 4, cy + 6], fill=accent)
