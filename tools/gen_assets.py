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

def load_font_flat(size, cjk=True, bold=True):
    """Flat-style assets: bold CJK (Hiragino Sans GB W6) / bold Latin."""
    cjk_paths = [
        ("/System/Library/Fonts/PingFang.ttc", 4),                    # Semibold if present
        ("/System/Library/Fonts/Hiragino Sans GB.ttc", 2),            # W6
        ("/System/Library/Fonts/Hiragino Sans GB.ttc", 0),            # W3
        ("/System/Library/Fonts/STHeiti Medium.ttc", 0),
    ]
    lat_paths = [
        ("/System/Library/Fonts/Helvetica.ttc", 1),                   # Bold
        ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 0),
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
# FLAT MINIMAL STYLE (matches assets/icon_1024.png baseline)
#   navy #0a0f2e subtle gradient, pale ice-blue flat ship,
#   #4a9fd8 canopy, flat light-blue flame, #e8713a accents,
#   sparse white stars, NO glow / NO outline / NO neon.
# ============================================================
NAVY_TOP = (10, 15, 46)     # #0a0f2e
NAVY_BOT = (19, 26, 64)     # slightly lighter bottom
ICE      = (220, 232, 245)  # #dce8f5 hull
ICE_SOFT = (198, 214, 235)  # secondary hull tone
CANOPY_B = (74, 159, 216)   # #4a9fd8 canopy
ORANGE_F = (232, 113, 58)   # #e8713a accent
STAR_F   = (232, 240, 250)  # star dots
NOSE_BL  = (126, 194, 240)  # flat nose blue
FLAME_T  = (166, 214, 248)  # flame gradient top
FLAME_B  = (228, 243, 254)  # flame gradient bottom
SPEED_L  = (66, 84, 136)    # flat speed lines
SUBTXT_F = (150, 172, 206)  # subtitle blue-gray
TITLE_F  = (234, 242, 250)  # near-white ice

def flat_bg(w, h, seed=7, stars=110):
    """Deep navy subtle vertical gradient + sparse small flat star dots."""
    rnd = random.Random(seed)
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(NAVY_TOP[0] + (NAVY_BOT[0] - NAVY_TOP[0]) * t)
        g = int(NAVY_TOP[1] + (NAVY_BOT[1] - NAVY_TOP[1]) * t)
        b = int(NAVY_TOP[2] + (NAVY_BOT[2] - NAVY_TOP[2]) * t)
        for x in range(w):
            px[x, y] = (r, g, b)
    d = ImageDraw.Draw(img)
    for _ in range(stars):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        mag = rnd.random()
        if mag > 0.90:
            r_ = rnd.uniform(1.8, 2.8) * S
        else:
            r_ = rnd.uniform(0.7, 1.6) * S
        v = rnd.randint(150, 240)
        tint = rnd.choice([(v, v, v), (v, v, min(255, v + 15)),
                           (min(255, v + 10), v, v)])
        d.ellipse([x - r_, y - r_, x + r_, y + r_], fill=tint)
    return img

def flat_tracked(d, xy, text, font, fill, anchor="mm", track_ratio=0.32):
    """Flat wide-tracked text (no glow). track_ratio of font size between chars."""
    tracking = int(font.size * track_ratio)
    widths = [d.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    ax, ay = xy
    x = ax - total / 2 if anchor.startswith("m") else ax
    anchor_y = anchor[1] if len(anchor) > 1 else "m"
    for ch, wch in zip(text, widths):
        d.text((x, ay), ch, font=font, fill=fill, anchor="l" + anchor_y)
        x += wch + tracking
    return total

def flat_ship_layer(size, k, flame=True):
    """One flat fighter in its own RGBA image; ship centered, nose up.
    Same geometric language as the icon: pale delta hull, blue nose wedge,
    blue canopy, orange wingtip dots, flat light-blue gradient flame."""
    w = h = size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = w / 2, h / 2
    # pale ice-blue delta hull (single flat fill)
    d.polygon(_scale_pts(HULL, cx, cy, k), fill=ICE + (255,))
    # slightly darker rear fuselage panel (flat two-tone, like icon shading)
    d.polygon(_scale_pts([(16, 44), (-16, 44), (-30, 30), (-56, 36), (-56, 26),
                          (-38, 8), (-16, -8), (16, -8), (38, 8), (56, 26), (56, 36), (30, 30)],
                         cx, cy, k * 0.0) if False else
              _scale_pts([(-14, 44), (14, 44), (10, 20), (-10, 20)], cx, cy, k),
              fill=ICE_SOFT + (255,))
    # flat blue nose wedge
    d.polygon(_scale_pts([(0, -56), (9, -22), (-9, -22)], cx, cy, k), fill=NOSE_BL + (255,))
    # canopy: medium blue flat ellipse
    cw, chh = 7.5 * k, 11 * k
    d.ellipse([cx - cw, cy - 16 * k - chh, cx + cw, cy - 16 * k + chh], fill=CANOPY_B + (255,))
    # orange wingtip dots
    for sgn in (-1, 1):
        ox, oy = cx + sgn * 53 * k, cy + 30 * k
        r_ = 4.2 * k
        d.ellipse([ox - r_, oy - r_, ox + r_, oy + r_], fill=ORANGE_F + (255,))
    if flame:
        # flat light-blue vertical-gradient tail flame: long tapered triangle
        # (icon-style) + brighter inner core triangle
        def flame_tri(half0, top_y, bot_y, col_a, col_b):
            strips = 28
            for i in range(strips):
                t0 = i / strips
                t1 = (i + 1) / strips
                y0 = top_y + (bot_y - top_y) * t0
                y1 = top_y + (bot_y - top_y) * t1
                hw0 = half0 * (1 - t0)
                hw1 = half0 * (1 - t1)
                col = tuple(int(col_a[c] + (col_b[c] - col_a[c]) * t0) for c in range(3))
                d.polygon([(cx - hw0, y0), (cx + hw0, y0), (cx + hw1, y1), (cx - hw1, y1)],
                          fill=col + (255,))
        flame_tri(9 * k, cy + 42 * k, cy + 108 * k, FLAME_T, FLAME_B)
        flame_tri(4 * k, cy + 42 * k, cy + 84 * k, FLAME_B, (255, 255, 255))
    return img

def paste_flat_ship(base, cx, cy, scale, **kw):
    size = int(300 * scale)
    ship = flat_ship_layer(size, scale * 2.0, **kw)
    base.alpha_composite(ship, (int(cx - size / 2), int(cy - size / 2)))

def speed_lines(d, pts_list, color=SPEED_L, width=3):
    for (x0, y0, x1, y1) in pts_list:
        d.line([x0, y0, x1, y1], fill=color, width=width)

def orange_blob(d, cx, cy, rx, ry):
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=ORANGE_F)

# ============================================================
# 1) social-preview.png 1280x640  (flat minimal style)
# ============================================================
def social_preview():
    W, H = 1280 * S, 640 * S
    img = flat_bg(W, H, seed=11, stars=130)
    d = ImageDraw.Draw(img)

    # title block (flat, no glow)
    f_title = load_font_flat(int(104 * S), cjk=True)
    f_sub_en = load_font_flat(int(30 * S), cjk=False, bold=True)
    f_sub = load_font_flat(int(28 * S), cjk=True, bold=False)
    title_cy = int(H * 0.155)
    d.text((W // 2, title_cy), "雷霆战机", font=f_title, fill=TITLE_F, anchor="mm")
    # thin orange divider under title
    div_y = title_cy + int(62 * S)
    d.line([W // 2 - int(70 * S), div_y, W // 2 + int(70 * S), div_y],
           fill=ORANGE_F, width=3 * S)
    flat_tracked(d, (W // 2, div_y + int(34 * S)), "THUNDER STRIKE", f_sub_en,
                 SUBTXT_F, anchor="mm", track_ratio=0.42)

    # hero flat ship, centered
    ship_cx, ship_cy = W // 2, int(H * 0.565)
    ship_scale = 0.98 * S
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    paste_flat_ship(overlay, ship_cx, ship_cy, ship_scale, flame=True)
    img_rgb = img.convert("RGBA")
    img_rgb.alpha_composite(overlay)
    img = img_rgb.convert("RGB")
    d = ImageDraw.Draw(img)

    # flat orange ellipse accents flanking the ship (echo the icon)
    orange_blob(d, int(W * 0.175), int(H * 0.47), int(11 * S), int(26 * S))
    orange_blob(d, int(W * 0.825), int(H * 0.47), int(11 * S), int(26 * S))
    # a few flat diagonal speed lines near the ship
    k = ship_scale * 2.0
    speed_lines(d, [
        (ship_cx - 130 * k / 2, ship_cy + 60 * k / 2, ship_cx - 160 * k / 2, ship_cy + 105 * k / 2),
        (ship_cx + 130 * k / 2, ship_cy + 60 * k / 2, ship_cx + 160 * k / 2, ship_cy + 105 * k / 2),
        (ship_cx - 105 * k / 2, ship_cy + 95 * k / 2, ship_cx - 128 * k / 2, ship_cy + 130 * k / 2),
        (ship_cx + 105 * k / 2, ship_cy + 95 * k / 2, ship_cx + 128 * k / 2, ship_cy + 130 * k / 2),
    ], width=3 * S)

    # bottom subtitle
    d.text((W // 2, int(H * 0.935)), "开源 HTML5 纵版弹幕射击 · Web / macOS",
           font=f_sub, fill=(196, 210, 230), anchor="mm")

    img = img.resize((1280, 640), Image.LANCZOS)
    img.save(f"{ASSETS}/social-preview.png", optimize=True)

# ============================================================
# 2) banner.png 1200x300  (flat minimal style)
# ============================================================
def banner():
    W, H = 1200 * S, 300 * S
    img = flat_bg(W, H, seed=23, stars=70)
    d = ImageDraw.Draw(img)

    # left title block
    f_title = load_font_flat(int(72 * S), cjk=True)
    f_en = load_font_flat(int(22 * S), cjk=False, bold=True)
    tx = int(W * 0.065)
    d.text((tx, int(H * 0.38)), "雷霆战机", font=f_title, fill=TITLE_F, anchor="lm")
    # orange thin divider
    div_y = int(H * 0.585)
    d.line([tx, div_y, tx + int(150 * S), div_y], fill=ORANGE_F, width=3 * S)
    flat_tracked(d, (tx, int(H * 0.75)), "THUNDER STRIKE", f_en, SUBTXT_F,
                 anchor="lm", track_ratio=0.42)

    # right: V formation of 3 flat ships
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    paste_flat_ship(overlay, int(W * 0.79), int(H * 0.42), 0.60 * S)
    paste_flat_ship(overlay, int(W * 0.665), int(H * 0.66), 0.40 * S)
    paste_flat_ship(overlay, int(W * 0.915), int(H * 0.66), 0.40 * S)
    img_rgb = img.convert("RGBA")
    img_rgb.alpha_composite(overlay)
    img = img_rgb.convert("RGB")
    d = ImageDraw.Draw(img)

    # flat diagonal speed lines trailing the formation
    speed_lines(d, [
        (int(W * 0.60), int(H * 0.16), int(W * 0.645), int(H * 0.30)),
        (int(W * 0.97), int(H * 0.16), int(W * 0.93), int(H * 0.30)),
        (int(W * 0.855), int(H * 0.10), int(W * 0.875), int(H * 0.19)),
    ], width=3 * S)
    # one small orange accent blob (echo the icon)
    orange_blob(d, int(W * 0.585), int(H * 0.52), int(7 * S), int(16 * S))

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
    # NOTE: icon() below is the LEGACY neon generator and must NOT be run —
    # assets/icon_1024.png is the hand-crafted flat-style style baseline.
    # Regenerating it would overwrite the baseline. Run banner/social only.
    social_preview()
    banner()
    print("done (banner + social-preview; icon untouched)")
