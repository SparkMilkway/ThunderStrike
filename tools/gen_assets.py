# -*- coding: utf-8 -*-
"""雷霆战机 开源仓库视觉资产生成器 — Pillow 纯绘制，零外部素材。"""
import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageFont

ASSETS = "/Users/onespark/Documents/kimi/workspace/thunder-strike-game/assets"
S = 2  # supersample

# ---------- palette ----------
CYAN    = (0, 229, 255)
CYAN_D  = (14, 165, 183)
MAGENTA = (255, 45, 149)
ORANGE  = (255, 158, 44)
WHITE   = (240, 250, 255)
BG_TOP  = (4, 6, 24)
BG_BOT  = (13, 16, 48)

# ---------- fonts ----------
def load_font(size, cjk=True):
    cjk_paths = [
        ("/System/Library/Fonts/PingFang.ttc", 0),
        ("/System/Library/Fonts/Hiragino Sans GB.ttc", 1),  # W6
        ("/System/Library/Fonts/Hiragino Sans GB.ttc", 0),  # W3
        ("/System/Library/Fonts/STHeiti Light.ttc", 0),
    ]
    lat_paths = [
        ("/System/Library/Fonts/Supplemental/Arial Black.ttf", 0),
        ("/System/Library/Fonts/Helvetica.ttc", 1),
        ("/System/Library/Fonts/Helvetica.ttc", 0),
    ]
    for path, idx in (cjk_paths if cjk else lat_paths):
        try:
            return ImageFont.truetype(path, size, index=idx)
        except Exception:
            continue
    return ImageFont.load_default()

# ---------- background ----------
def space_bg(w, h, seed=7, stars=220, glow_center=None, glow_color=(20, 40, 110)):
    rnd = random.Random(seed)
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * t)
        for x in range(w):
            px[x, y] = (r, g, b)
    # central nebula glow
    if glow_center:
        layer = Image.new("RGB", (w, h), (0, 0, 0))
        d = ImageDraw.Draw(layer)
        cx, cy, rad = glow_center
        d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=glow_color)
        layer = layer.filter(ImageFilter.GaussianBlur(rad * 0.55))
        img = ImageChops.add(img, layer)
    d = ImageDraw.Draw(img)
    for _ in range(stars):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        mag = rnd.random()
        if mag > 0.92:  # bright star with sparkle
            r = rnd.uniform(1.6, 2.6) * S
            c = rnd.choice([WHITE, CYAN, (255, 220, 235)])
            d.ellipse([x - r, y - r, x + r, y + r], fill=c)
            a = r * 3.2
            d.line([x - a, y, x + a, y], fill=c, width=S)
            d.line([x, y - a, x, y + a], fill=c, width=S)
        else:
            r = rnd.uniform(0.6, 1.6) * S
            v = rnd.randint(120, 235)
            tint = rnd.choice([(v, v, v), (v, v, min(255, v + 20)), (v, min(255, v + 10), v)])
            d.ellipse([x - r, y - r, x + r, y + r], fill=tint)
    return img

# ---------- glow helpers ----------
def additive_glow(base, draw_fn, blur, gain=2):
    """draw_fn(d) paints on black layer; blur & additively composite `gain` times."""
    layer = Image.new("RGB", base.size, (0, 0, 0))
    d = ImageDraw.Draw(layer)
    draw_fn(d)
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    out = base
    for _ in range(gain):
        out = ImageChops.add(out, layer)
    return out

def neon_text(base, xy, text, font, fill, glow, glow_blur=10, anchor="mm",
              glow_gain=2, tracking=0):
    """Text with neon halo. tracking = extra px between chars (already scaled)."""
    layer = Image.new("RGB", base.size, (0, 0, 0))
    d = ImageDraw.Draw(layer)
    if tracking:
        _draw_tracked(d, xy, text, font, glow, anchor)
    else:
        d.text(xy, text, font=font, fill=glow, anchor=anchor)
    layer = layer.filter(ImageFilter.GaussianBlur(glow_blur))
    out = base
    for _ in range(glow_gain):
        out = ImageChops.add(out, layer)
    d = ImageDraw.Draw(out)
    if tracking:
        _draw_tracked(d, xy, text, font, fill, anchor)
    else:
        d.text(xy, text, font=font, fill=fill, anchor=anchor)
    return out

def _draw_tracked(d, xy, text, font, fill, anchor):
    widths = [d.textlength(ch, font=font) for ch in text]
    tracking = int(font.size * 0.18)
    total = sum(widths) + tracking * (len(text) - 1)
    ax, ay = xy
    x = ax - total / 2 if anchor.startswith("m") else ax
    anchor_y = anchor[1] if len(anchor) > 1 else "m"
    for ch, wch in zip(text, widths):
        d.text((x, ay), ch, font=font, fill=fill, anchor="l" + anchor_y)
        x += wch + tracking

# ---------- ship ----------
HULL = [(0, -56), (9, -24), (16, -8), (38, 8), (56, 26), (56, 36), (30, 30),
        (16, 44), (-16, 44), (-30, 30), (-56, 36), (-56, 26), (-38, 8), (-16, -8), (-9, -24)]

def _scale_pts(pts, cx, cy, k, dy=0):
    return [(cx + p[0] * k, cy + p[1] * k + dy) for p in pts]

def ship_layer(size, k, body=CYAN, hull_pale=(214, 244, 255), flame=True):
    """Render one fighter into its own RGBA image; ship centered, nose up."""
    w = h = size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = w / 2, h / 2
    # outer pale hull
    d.polygon(_scale_pts(HULL, cx, cy, k), fill=hull_pale + (255,))
    # mid cyan hull
    d.polygon(_scale_pts(HULL, cx, cy, k * 0.78, dy=-2 * k), fill=body + (255,))
    # dark spine
    d.polygon(_scale_pts([(0, -56), (7, -18), (5, 18), (-5, 18), (-7, -18)], cx, cy, k * 0.9),
              fill=(8, 60, 80, 255))
    # nose highlight
    d.polygon(_scale_pts([(0, -56), (4, -30), (-4, -30)], cx, cy, k), fill=WHITE + (255,))
    # canopy
    cw, chh = 7.5 * k, 11 * k
    d.ellipse([cx - cw, cy - 26 * k, cx + cw, cy - 26 * k + 2 * chh], fill=(6, 34, 52, 255),
              outline=body + (255,), width=max(1, int(1.4 * k)))
    # wing accents (magenta)
    for sgn in (-1, 1):
        d.polygon(_scale_pts([(sgn * 34, 12), (sgn * 52, 27), (sgn * 52, 33), (sgn * 30, 27)],
                             cx, cy, k * 0.95), fill=MAGENTA + (255,))
    # tail stripe
    d.polygon(_scale_pts([(-14, 36), (14, 36), (12, 44), (-12, 44)], cx, cy, k), fill=CYAN_D + (255,))
    if flame:
        # engine flames (orange core, cyan sheath)
        for sgn in (-1, 1):
            nx = cx + sgn * 13 * k
            ny = cy + 44 * k
            fl = 34 * k
            d.polygon([(nx - 5 * k, ny), (nx + 5 * k, ny), (nx, ny + fl)], fill=ORANGE + (230,))
            d.polygon([(nx - 2.6 * k, ny), (nx + 2.6 * k, ny), (nx, ny + fl * 0.62)],
                      fill=(255, 240, 200, 240))
        # center main thruster
        ny = cy + 44 * k
        d.polygon([(cx - 7 * k, ny), (cx + 7 * k, ny), (cx, ny + 52 * k)], fill=(140, 240, 255, 220))
        d.polygon([(cx - 3.2 * k, ny), (cx + 3.2 * k, ny), (cx, ny + 34 * k)], fill=WHITE + (240,))
    return img

def paste_ship(base, cx, cy, scale, glow=True, **kw):
    size = int(260 * scale)
    ship = ship_layer(size, scale * 2.0, **kw)  # k=2 at scale 1 -> ship ~ 224px tall
    if glow:
        halo = ship.filter(ImageFilter.GaussianBlur(6 * scale * S / 2))
        tinted = Image.new("RGBA", ship.size, (0, 0, 0, 0))
        tinted.paste(CYAN + (140,), (0, 0), halo.split()[3])
        base.alpha_composite(tinted, (int(cx - size / 2), int(cy - size / 2)))
    base.alpha_composite(ship, (int(cx - size / 2), int(cy - size / 2)))

# ---------- enemies / bullets / whip ----------
def drone(d, cx, cy, r, color):
    pts = [(cx, cy - r), (cx + r * 0.9, cy), (cx, cy + r), (cx - r * 0.9, cy)]
    d.polygon(pts, fill=color)
    d.polygon([(cx, cy - r * 0.45), (cx + r * 0.45, cy), (cx, cy + r * 0.45), (cx - r * 0.45, cy)],
              fill=WHITE)

def draw_drone(base, cx, cy, r, color):
    base = additive_glow(base, lambda d: drone(d, cx, cy, r, color), blur=10 * S, gain=1)
    d = ImageDraw.Draw(base)
    drone(d, cx, cy, r, color)
    return base

def whip_pts(x0, y0, x1, y1, amp, waves, phase=0.0):
    pts = []
    n = 60
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    for i in range(n + 1):
        t = i / n
        env = math.sin(t * math.pi)          # taper at ends
        off = amp * env * math.sin(t * math.pi * waves + phase)
        pts.append((x0 + dx * t + px * off, y0 + dy * t + py * off))
    return pts

def draw_whip(base, pts, color, width):
    def paint(d):
        d.line(pts, fill=color, width=width, joint="curve")
    base = additive_glow(base, paint, blur=9 * S, gain=2)
    d = ImageDraw.Draw(base)
    d.line(pts, fill=WHITE, width=max(2, width // 3), joint="curve")
    d.line(pts, fill=color, width=width, joint="curve")
    return base

def draw_bolt(base, x, y, length, color, width):
    """Vertical bolt, head (muzzle end) at y, body extends downward `length`."""
    pts = [(x, y), (x, y + length)]
    base = additive_glow(base, lambda d: d.line(pts, fill=color, width=width), blur=6 * S, gain=2)
    d = ImageDraw.Draw(base)
    d.line(pts, fill=WHITE, width=max(2, width // 3))
    d.line(pts, fill=color, width=width)
    hr = width * 0.55
    d.ellipse([x - hr, y - hr, x + hr, y + hr], fill=WHITE)
    return base

def draw_sparks(base, cx, cy, rad, color, n=26, seed=3):
    rnd = random.Random(seed)
    def paint(d):
        for _ in range(n):
            a = rnd.uniform(0, math.tau)
            rr = rnd.uniform(rad * 0.35, rad)
            x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
            r = rnd.uniform(2, 5) * S
            d.ellipse([x - r, y - r, x + r, y + r], fill=color)
            if rnd.random() > 0.6:
                d.line([cx + math.cos(a) * rr * 0.5, cy + math.sin(a) * rr * 0.5, x, y],
                       fill=color, width=S)
    base = additive_glow(base, paint, blur=5 * S, gain=2)
    paint(ImageDraw.Draw(base))
    return base

def vignette(img, strength=90):
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    d.rectangle([0, 0, w, h], fill=strength)
    d.ellipse([-w * 0.25, -h * 0.35, w * 1.25, h * 1.35], fill=0)
    mask = mask.filter(ImageFilter.GaussianBlur(w * 0.08))
    black = Image.new("RGB", (w, h), (0, 0, 0))
    return Image.composite(black, img, mask)

# ============================================================
# 1) social-preview.png 1280x640
# ============================================================
def social_preview():
    W, H = 1280 * S, 640 * S
    img = space_bg(W, H, seed=11, stars=260, glow_center=(W // 2, int(H * 0.62), int(W * 0.42)),
                   glow_color=(16, 42, 108))
    # distant enemy drones (upper corners)
    img = draw_drone(img, int(W * 0.20), int(H * 0.30), 26 * S, MAGENTA)
    img = draw_drone(img, int(W * 0.80), int(H * 0.30), 26 * S, MAGENTA)
    img = draw_drone(img, int(W * 0.10), int(H * 0.14), 16 * S, ORANGE)
    img = draw_drone(img, int(W * 0.90), int(H * 0.14), 16 * S, ORANGE)

    # player ship (kept compact so the flame clears the bottom subtitle)
    ship_cx, ship_cy = W // 2, int(H * 0.615)
    ship_scale = 1.0 * S
    k = ship_scale * 2.0                      # ship local scale used by paste_ship
    nose_y = ship_cy - 56 * k                 # nose tip y
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    paste_ship(overlay, ship_cx, ship_cy, ship_scale, flame=True)
    img_rgb = img.convert("RGBA")
    img_rgb.alpha_composite(overlay)
    img = img_rgb.convert("RGB")
    # vulcan bolts upward (fan of 4 with a center gap), ending right at the nose
    for i, dx in enumerate((-3, -1.5, 1.5, 3)):
        bx = ship_cx + dx * 24 * S
        by = nose_y - 50 * S
        img = draw_bolt(img, bx, by, 46 * S, CYAN, 7 * S)

    # plasma whips from wingtips wrapping the two side drones
    for sgn, ex in ((-1, int(W * 0.20)), (1, int(W * 0.80))):
        pts = whip_pts(ship_cx + sgn * 112 * S, ship_cy + 52 * S, ex, int(H * 0.33),
                       amp=34 * S, waves=2.2, phase=sgn * 0.9)
        img = draw_whip(img, pts, MAGENTA, 6 * S)
        img = draw_sparks(img, ex, int(H * 0.31), 34 * S, MAGENTA, n=12, seed=ex)

    # vignette
    img = vignette(img)

    # title
    f_title = load_font(int(118 * S), cjk=True)
    f_sub_en = load_font(int(44 * S), cjk=False)
    f_sub = load_font(int(30 * S), cjk=True)
    img = neon_text(img, (W // 2, int(H * 0.145)), "雷霆战机", f_title, WHITE, CYAN,
                    glow_blur=14 * S, glow_gain=2, tracking=1)
    img = neon_text(img, (W // 2, int(H * 0.285)), "THUNDER STRIKE", f_sub_en,
                    (190, 245, 255), (0, 140, 180), glow_blur=9 * S, glow_gain=2, tracking=1)
    # subtitle at bottom
    img = neon_text(img, (W // 2, int(H * 0.945)), "开源 HTML5 纵版弹幕射击 · Web / macOS",
                    f_sub, (220, 235, 245), (90, 60, 140), glow_blur=7 * S, glow_gain=1)

    img = img.resize((1280, 640), Image.LANCZOS)
    img.save(f"{ASSETS}/social-preview.png", optimize=True)

# ============================================================
# 2) banner.png 1200x300
# ============================================================
def banner():
    W, H = 1200 * S, 300 * S
    img = space_bg(W, H, seed=23, stars=150, glow_center=(int(W * 0.78), H // 2, int(H * 1.4)),
                   glow_color=(18, 46, 112))
    # left title block
    f_title = load_font(int(76 * S), cjk=True)
    f_en = load_font(int(26 * S), cjk=False)
    img = neon_text(img, (int(W * 0.065), int(H * 0.40)), "雷霆战机", f_title, WHITE, CYAN,
                    glow_blur=11 * S, glow_gain=2, anchor="lm")
    img = neon_text(img, (int(W * 0.068), int(H * 0.70)), "THUNDER STRIKE", f_en,
                    (185, 240, 255), (0, 130, 170), glow_blur=7 * S, glow_gain=1, anchor="lm")
    d = ImageDraw.Draw(img)
    d.line([int(W * 0.065), int(H * 0.545), int(W * 0.30), int(H * 0.545)],
           fill=MAGENTA, width=3 * S)

    # right: danmaku arcs + 3-ship V formation
    # bullet streams: dense glowing beads along fan curves, plus faint trails
    for i in range(4):
        cx0, cy0 = W * 1.02, -H * 0.30 + i * H * 0.30
        pts = []
        for t in range(80):
            tt = t / 79
            x = cx0 - tt * W * 0.62
            y = cy0 + tt * H * (0.55 + i * 0.20) + math.sin(tt * math.pi * 2 + i) * 9 * S
            pts.append((x, y))
        col = (ORANGE, MAGENTA, CYAN, MAGENTA)[i]
        # faint trail
        img = additive_glow(img, lambda dd, pts=pts, col=col:
                            dd.line(pts, fill=col, width=2 * S, joint="curve"),
                            blur=5 * S, gain=1)
        # beads
        for j in range(4, 80, 5):
            x, y = pts[j]
            r = max(2.2 * S, (6 - j / 16) * S)
            img = additive_glow(img, lambda dd, x=x, y=y, r=r, col=col:
                                dd.ellipse([x - r, y - r, x + r, y + r], fill=col),
                                blur=4 * S, gain=1)
            dd = ImageDraw.Draw(img)
            dd.ellipse([x - r, y - r, x + r, y + r], fill=col)
            dd.ellipse([x - r * 0.45, y - r * 0.45, x + r * 0.45, y + r * 0.45], fill=WHITE)

    # formation: lead + 2 wingmen
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    paste_ship(overlay, int(W * 0.80), int(H * 0.52), 0.85 * S)
    paste_ship(overlay, int(W * 0.68), int(H * 0.76), 0.58 * S)
    paste_ship(overlay, int(W * 0.92), int(H * 0.76), 0.58 * S)
    img_rgb = img.convert("RGBA")
    img_rgb.alpha_composite(overlay)
    img = img_rgb.convert("RGB")
    # short bolts above formation (heads near each nose)
    for bx, by, bl in ((0.80, 0.12, 44), (0.68, 0.42, 30), (0.92, 0.42, 30)):
        img = draw_bolt(img, int(W * bx), int(H * by), bl * S, CYAN, 5 * S)
    img = vignette(img, strength=70)
    img = img.resize((1200, 300), Image.LANCZOS)
    img.save(f"{ASSETS}/banner.png", optimize=True)

# ============================================================
# 3) icon_1024.png 1024x1024
# ============================================================
def squircle_mask(size, radius_ratio=0.225):
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    r = int(size * radius_ratio)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=255)
    return m

def icon():
    W = H = 1024 * S
    img = space_bg(W, H, seed=42, stars=200, glow_center=(W // 2, int(H * 0.56), int(W * 0.55)),
                   glow_color=(22, 58, 140))
    # secondary magenta nebula
    layer = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([W * 0.55, H * 0.02, W * 1.15, H * 0.5], fill=(70, 16, 70))
    layer = layer.filter(ImageFilter.GaussianBlur(W * 0.14))
    img = ImageChops.add(img, layer)

    # explosion spark clusters
    img = draw_sparks(img, int(W * 0.22), int(H * 0.28), 90 * S, ORANGE, n=22, seed=9)
    img = draw_sparks(img, int(W * 0.79), int(H * 0.24), 58 * S, MAGENTA, n=15, seed=14)
    img = draw_sparks(img, int(W * 0.83), int(H * 0.58), 36 * S, CYAN, n=11, seed=19)

    # hero ship
    ship_scale = 2.35 * S
    k = ship_scale * 2.0
    ship_cy = int(H * 0.50)
    nose_y = ship_cy - 56 * k
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    paste_ship(overlay, W // 2, ship_cy, ship_scale, flame=True)
    img_rgb = img.convert("RGBA")
    img_rgb.alpha_composite(overlay)
    img = img_rgb.convert("RGB")
    # vulcan bolts, heads just above the nose tip
    for dx in (-2, 0, 2):
        img = draw_bolt(img, W // 2 + dx * 60 * S, nose_y - int(150 * S), 110 * S,
                        CYAN, 9 * S)

    # gradient rim: cyan->magenta glow ring inside squircle
    ring = Image.new("RGB", (W, H), (0, 0, 0))
    rd = ImageDraw.Draw(ring)
    r = int(W * 0.225)
    steps = 48
    inset = int(10 * S)
    for i in range(steps):
        t = i / (steps - 1)
        col = tuple(int(CYAN[c] + (MAGENTA[c] - CYAN[c]) * t) for c in range(3))
        rd.arc([inset + i, inset + i, W - inset - i, H - inset - i], 0, 360, fill=col)
    ring = ring.filter(ImageFilter.GaussianBlur(6 * S))
    img = ImageChops.add(img, ring)

    # inner crisp edge
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([inset, inset, W - inset - 1, H - inset - 1], radius=r - inset,
                        outline=(120, 235, 255), width=3 * S)

    # squircle crop
    mask = squircle_mask(W, 0.225).resize((W, H), Image.LANCZOS)
    out = Image.new("RGB", (W, H), (0, 0, 0))
    out.paste(img, (0, 0), mask)
    out = out.resize((1024, 1024), Image.LANCZOS)
    out.save(f"{ASSETS}/icon_1024.png", optimize=True)

if __name__ == "__main__":
    social_preview()
    banner()
    icon()
    print("done")
