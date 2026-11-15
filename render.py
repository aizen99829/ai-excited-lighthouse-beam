#!/usr/bin/env python3
"""Riding the Lighthouse Beam — procedural render for make.fun ai-excited-01.

A lone silhouetted surfer rides a solid beam of golden light diagonally down
from a lighthouse (top-left) toward a stormy sea of stars (bottom-right).
Deterministic: fixed seed, no external assets, no network, no text in image.

Usage: python3 render.py [output-path]   (default: entry.png next to this file)
"""

import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter

SEED = 20261116
W = H = 1024

# Palette
SKY_TOP = (13, 18, 52)       # deep indigo
SKY_BOTTOM = (4, 5, 16)      # near-black indigo
BEAM_CORE = (255, 244, 214)   # white-gold
BEAM_MID = (255, 196, 92)     # amber
BEAM_GLOW = (255, 170, 60)    # deep gold
TEAL = (64, 199, 186)
VIOLET = (138, 99, 226)
STAR = (235, 240, 255)
MOON = (250, 240, 205)

# Beam geometry: lighthouse lamp -> where the beam meets the star-sea.
# The lamp sits in the lamp room at the top of the tower (tower top y=58,
# lamp room y=18..42, so the lamp centre is ~(168, 32)).
LAMP = (168, 32)
BEAM_END = (922, 818)
SURFER_T = 0.34  # fraction along the beam from the lamp


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def point_on_beam(t):
    return (LAMP[0] + (BEAM_END[0] - LAMP[0]) * t,
            LAMP[1] + (BEAM_END[1] - LAMP[1]) * t)


def beam_angle():
    return math.atan2(BEAM_END[1] - LAMP[1], BEAM_END[0] - LAMP[0])


def tapered_band(draw, p0, p1, w0, w1, fill):
    """Draw a tapered quad (a band wider at p0 than at p1)."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    length = math.hypot(dx, dy)
    nx, ny = -dy / length, dx / length  # unit normal
    pts = [
        (p0[0] + nx * w0 / 2, p0[1] + ny * w0 / 2),
        (p0[0] - nx * w0 / 2, p0[1] - ny * w0 / 2),
        (p1[0] - nx * w1 / 2, p1[1] - ny * w1 / 2),
        (p1[0] + nx * w1 / 2, p1[1] + ny * w1 / 2),
    ]
    draw.polygon(pts, fill=fill)


def sky(img):
    """Vertical indigo gradient with a faint warm halo near the lamp."""
    top = Image.new("RGB", (1, H))
    px = top.load()
    for y in range(H):
        px[0, y] = lerp(SKY_TOP, SKY_BOTTOM, y / (H - 1))
    img.paste(top.resize((W, H)))
    # warm halo around the lamp, very subtle
    halo = Image.new("L", (W, H), 0)
    hd = ImageDraw.Draw(halo)
    hd.ellipse([LAMP[0] - 260, LAMP[1] - 260, LAMP[0] + 260, LAMP[1] + 260],
               fill=60)
    halo = halo.filter(ImageFilter.GaussianBlur(140))
    warm = Image.new("RGB", (W, H), (90, 62, 18))
    img.paste(warm, (0, 0), halo)


def stars_and_nebula(img, rng):
    """Starfield, brighter cross-sparkle stars, and low teal/violet wisps."""
    # Nebula wisps low in the frame, on their own layer, heavily blurred.
    neb = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(neb)
    for _ in range(26):
        cx = rng.uniform(0, W)
        cy = rng.uniform(H * 0.45, H * 0.98)
        rx = rng.uniform(60, 220)
        ry = rng.uniform(18, 60)
        col = TEAL if rng.random() < 0.5 else VIOLET
        nd.ellipse([cx - rx, cy - ry, cx + rx, cy + ry],
                   fill=col + (rng.randint(10, 26),))
    neb = neb.filter(ImageFilter.GaussianBlur(38))
    img.paste(Image.alpha_composite(img.convert("RGBA"), neb).convert("RGB"),
              (0, 0))

    d = ImageDraw.Draw(img, "RGBA")
    # Several hundred small stars, denser toward the bottom (the star-sea).
    for _ in range(520):
        if rng.random() < 0.45:
            x = rng.uniform(0, W)
            y = rng.uniform(H * 0.72, H)
        else:
            x = rng.uniform(0, W)
            y = rng.uniform(0, H * 0.75)
        r = rng.choice([0.7, 0.9, 1.1, 1.4, 1.8])
        b = rng.randint(90, 255)
        a = rng.randint(140, 255)
        d.ellipse([x - r, y - r, x + r, y + r], fill=STAR + (a,))
        if rng.random() < 0.06:  # a few brighter stars
            d.ellipse([x - r * 2.2, y - r * 2.2, x + r * 2.2, y + r * 2.2],
                      outline=(255, 255, 255, 90), width=1)
    # A dozen cross-sparkle stars.
    for _ in range(12):
        x = rng.uniform(40, W - 40)
        y = rng.uniform(40, H * 0.85)
        s = rng.uniform(4, 9)
        a = rng.randint(170, 235)
        d.line([x - s, y, x + s, y], fill=(255, 255, 255, a), width=1)
        d.line([x, y - s, x, y + s], fill=(255, 255, 255, a), width=1)
        d.ellipse([x - 1.6, y - 1.6, x + 1.6, y + 1.6],
                  fill=(255, 255, 255, a))


def moon(img):
    """Small crescent moon, upper right."""
    cx, cy, r = 838, 132, 34
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    md.ellipse([cx - r + 17, cy - r - 7, cx + r + 17, cy + r - 7], fill=0)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([cx - r - 14, cy - r - 14, cx + r + 14, cy + r + 14],
               fill=(250, 240, 205, 40))
    glow = glow.filter(ImageFilter.GaussianBlur(12))
    base = Image.alpha_composite(img.convert("RGBA"), glow)
    base.paste(Image.new("RGBA", (W, H), MOON + (235,)), (0, 0), mask)
    img.paste(base.convert("RGB"), (0, 0))


def beam(img):
    """The solid diagonal beam of golden light, layered translucent strokes."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # Faint parallel rays fanning from the lamp, above and below the beam.
    ang = beam_angle()
    for k, spread in enumerate([-0.30, -0.18, -0.08, 0.10, 0.22]):
        a = ang + spread
        ex = LAMP[0] + math.cos(a) * 460
        ey = LAMP[1] + math.sin(a) * 460
        d.line([LAMP, (ex, ey)], fill=BEAM_GLOW + (13 - k * 2,), width=6)
    # Layered tapered bands: outer glow, amber mid, white-gold core.
    tapered_band(d, LAMP, BEAM_END, 210, 120, BEAM_GLOW + (46,))
    tapered_band(d, LAMP, BEAM_END, 128, 74, BEAM_MID + (110,))
    tapered_band(d, LAMP, BEAM_END, 62, 36, BEAM_CORE + (215,))
    tapered_band(d, LAMP, BEAM_END, 22, 12, (255, 252, 240, 255))
    # The beam's far end is left uncapped: it plunges into the star-sea and
    # the dense stars + crest sparkles there mark the impact moment.
    layer = layer.filter(ImageFilter.GaussianBlur(2.2))
    img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"),
              (0, 0))
    # Hot core line, crisp, drawn after the blur.
    d2 = ImageDraw.Draw(img, "RGBA")
    d2.line([LAMP, BEAM_END], fill=(255, 252, 240, 200), width=5)


def lighthouse(img):
    """Small dark lighthouse silhouette at the top-left, lamp glowing."""
    d = ImageDraw.Draw(img, "RGBA")
    x, y = 132, 58  # top of the tower
    body = (10, 10, 26, 255)
    # Tower: slightly tapered, with two pale bands catching the light.
    d.polygon([(x, y + 118), (x + 14, y), (x + 58, y), (x + 72, y + 118)],
              fill=body)
    d.polygon([(x + 6, y + 40), (x + 66, y + 40), (x + 68, y + 52),
               (x + 4, y + 52)], fill=(38, 34, 66, 255))
    d.polygon([(x + 3, y + 82), (x + 69, y + 82), (x + 70, y + 94),
               (x + 2, y + 94)], fill=(38, 34, 66, 255))
    # Gallery + lamp room.
    d.rectangle([x + 6, y - 16, x + 66, y - 2], fill=body)
    d.rectangle([x + 16, y - 40, x + 56, y - 16], fill=(24, 22, 48, 255))
    # Lamp glow + bright lamp.
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([LAMP[0] - 52, LAMP[1] - 52, LAMP[0] + 52, LAMP[1] + 52],
               fill=(255, 214, 130, 110))
    glow = glow.filter(ImageFilter.GaussianBlur(18))
    img.paste(Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB"),
              (0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([LAMP[0] - 13, LAMP[1] - 13, LAMP[0] + 13, LAMP[1] + 13],
              fill=(255, 246, 220, 255))
    d.ellipse([LAMP[0] - 6, LAMP[1] - 6, LAMP[0] + 6, LAMP[1] + 6],
              fill=(255, 255, 255, 255))


def surfer(img):
    """Small dark silhouette surfing down the beam, with spray trail."""
    sx, sy = point_on_beam(SURFER_T)
    ang = beam_angle()
    d = ImageDraw.Draw(img, "RGBA")
    dark = (8, 8, 20, 255)
    # Spray / wake trail behind the board: one soft tapered streak up the
    # beam, plus a few bright flecks, blurred so it reads as spray, not dots.
    trail = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(trail)
    tx0, ty0 = point_on_beam(SURFER_T - 0.005)
    tx1, ty1 = point_on_beam(SURFER_T - 0.075)
    tapered_band(td, (tx0, ty0), (tx1, ty1), 10, 2,
                 (255, 244, 210, 150))
    for i in range(10):
        t = SURFER_T - 0.01 - 0.007 * i
        px, py = point_on_beam(t)
        td.ellipse([px - 1.6, py - 1.6, px + 1.6, py + 1.6],
                   fill=(255, 250, 230, max(0, 170 - i * 16)))
    trail = trail.filter(ImageFilter.GaussianBlur(2.0))
    img.paste(Image.alpha_composite(img.convert("RGBA"), trail).convert("RGB"),
              (0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    # Board: long thin ellipse along the beam direction.
    bx, by = sx, sy + 2
    blen, bwid = 46, 7
    ca, sa = math.cos(ang), math.sin(ang)
    corners = []
    for sgn_l, sgn_w in [(1, 1), (1, -1), (-1, -1), (-1, 1)]:
        corners.append((bx + sgn_l * blen / 2 * ca - sgn_w * bwid / 2 * sa,
                        by + sgn_l * blen / 2 * sa + sgn_w * bwid / 2 * ca))
    d.polygon(corners, fill=dark)
    # Crouched figure: head, leaning torso, bent legs — pure silhouette.
    hx, hy = sx - 4, sy - 26
    d.ellipse([hx - 5, hy - 5, hx + 5, hy + 5], fill=dark)          # head
    d.line([(hx, hy + 4), (sx + 2, sy - 6)], fill=dark, width=7)    # torso
    d.line([(sx + 2, sy - 6), (sx - 12, sy - 1)], fill=dark, width=5)  # back leg
    d.line([(sx + 2, sy - 6), (sx + 12, sy - 1)], fill=dark, width=5)  # front leg
    d.line([(hx, hy + 4), (sx - 14, sy - 12)], fill=dark, width=4)  # back arm
    d.line([(hx, hy + 4), (sx + 14, sy - 10)], fill=dark, width=4)  # front arm
    # Motion-blur arc above the surfer.
    d.arc([sx - 52, sy - 78, sx + 52, sy + 10], start=200, end=330,
          fill=(255, 220, 150, 90), width=3)


def star_sea(img, rng):
    """Bottom band: churning stars, foam streaks, wave-crest sparkles."""
    d = ImageDraw.Draw(img, "RGBA")
    # Foam-like light streaks, mostly horizontal, denser near the bottom.
    for _ in range(90):
        x = rng.uniform(0, W)
        y = rng.uniform(H * 0.76, H * 0.99)
        ln = rng.uniform(14, 70)
        a = rng.randint(40, 130)
        d.line([x, y, x + ln, y + rng.uniform(-3, 3)],
               fill=(190, 220, 255, a), width=1)
    # Bright wave-crest sparkles where the beam meets the sea.
    bx, by = point_on_beam(0.97)
    for _ in range(22):
        x = bx + rng.uniform(-90, 110)
        y = by + rng.uniform(-26, 40)
        s = rng.uniform(3, 8)
        a = rng.randint(150, 240)
        d.line([x - s, y, x + s, y], fill=(255, 250, 230, a), width=1)
        d.line([x, y - s, x, y + s], fill=(255, 250, 230, a), width=1)
    # Darken the very bottom edge.
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    sd.rectangle([0, H - 60, W, H], fill=(2, 2, 8, 110))
    shade = shade.filter(ImageFilter.GaussianBlur(24))
    img.paste(Image.alpha_composite(img.convert("RGBA"), shade).convert("RGB"),
              (0, 0))


def vignette(img):
    """Very gentle darkening at the corners to focus the eye on the beam."""
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([-W * 0.12, -H * 0.12, W * 1.12, H * 1.12], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(90))
    dark = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    base = img.convert("RGBA")
    base.paste(dark, (0, 0), Image.eval(mask, lambda v: 255 - v).point(
        lambda v: int(v * 0.5)))
    img.paste(base.convert("RGB"), (0, 0))


def render(out_path):
    rng = random.Random(SEED)
    img = Image.new("RGB", (W, H))
    sky(img)
    stars_and_nebula(img, rng)
    moon(img)
    beam(img)
    lighthouse(img)
    surfer(img)
    star_sea(img, rng)
    vignette(img)
    img.save(out_path, format="PNG", optimize=True)
    return out_path


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "entry.png")
    render(out)
    print(f"wrote {out} ({os.path.getsize(out)} bytes)")
