"""v38: creative exits out of the four "I'm upping my P(doom)" chorus cards.
A = last frame of the gold P(DOOM) card, B = the incoming scene (already post-processed).
Each chorus gets its own move instead of the old zoom + crossfade."""
import math
import numpy as np
from PIL import Image
from kit import *

DUR = 0.46
GOLD_RGB = np.array(GOLD[:3] if isinstance(GOLD, tuple) else (245, 180, 32), np.float32)


def _ease(u):
    return eio(clamp(u))


def letter_segments(a):
    """column spans of the dark letters on the gold card"""
    lum = a[..., :3].mean(axis=2)
    band = lum[int(H * 0.30):int(H * 0.72)]
    ink = (band < 90).sum(axis=0) > 6
    segs, on, x0 = [], False, 0
    for x, v in enumerate(ink):
        if v and not on:
            on, x0 = True, x
        elif not v and on:
            on = False
            if x - x0 > 8:
                segs.append((x0, x))
    if on:
        segs.append((x0, W))
    rows = np.where((lum[:, :] < 90).sum(axis=1) > 20)[0]
    rows = rows[(rows > H * 0.2) & (rows < H * 0.8)]
    y0, y1 = (int(rows.min()), int(rows.max())) if len(rows) else (int(H * 0.35), int(H * 0.65))
    return segs, y0, y1


def zoom_about(img, z, cx, cy):
    """scale an RGB array by z about (cx, cy), keeping (cx, cy) fixed (memory-safe affine, no giant resize)"""
    im = Image.fromarray(img)
    a = 1.0 / z
    bg = BG[:3] if isinstance(BG, tuple) else (10, 10, 10)
    out = im.transform((W, H), Image.AFFINE, (a, 0, cx - a * cx, 0, a, cy - a * cy), Image.BILINEAR, fillcolor=bg)
    return np.asarray(out).copy()


# ---------------------------------------------------------------- 1b: v40 smooth portal
P_PRE = 0.34      # the dive starts on the card itself, before the cut
P_POST = 0.50     # and finishes inside the next scene
P_ZMAX = 16.0
_PG = {}


def portal_geom(a):
    if 'g' not in _PG:
        segs, y0, y1 = letter_segments(a)
        s = segs[4] if len(segs) >= 6 else (W // 2 - 60, W // 2 + 60)
        lum = a[..., :3].mean(axis=2)
        mx = (s[0] + s[1]) // 2
        col = lum[y0:y1, mx] > 120               # the gold counter inside the O, on the centre column
        c = (y1 - y0) // 2
        ys = []
        if col[c]:
            i0 = c
            while i0 > 0 and col[i0 - 1]:
                i0 -= 1
            i1 = c
            while i1 < len(col) - 1 and col[i1 + 1]:
                i1 += 1
            ys = [i0, i1]
        if len(ys):
            cy0, cy1 = y0 + ys[0], y0 + ys[1]
            my = (cy0 + cy1) // 2
            row = lum[my, :] > 120
            i0 = i1 = mx
            while row[i0 - 1]:
                i0 -= 1
            while row[i1 + 1]:
                i1 += 1
            cx0, cx1 = i0, i1
            _PG['g'] = ((cx0 + cx1) / 2, (cy0 + cy1) / 2, (cx1 - cx0) / 2 * 0.97, (cy1 - cy0) / 2 * 0.97)
        else:
            _PG['g'] = ((s[0] + s[1]) / 2, (y0 + y1) / 2, (s[1] - s[0]) * 0.21, (y1 - y0) * 0.30)
    return _PG['g']


def portal_s(t, st):
    return clamp((t - (st - P_PRE)) / (P_PRE + P_POST))


def portal_zoom(s):
    # log-zoom with zero start velocity that keeps accelerating smoothly (no late snap)
    return math.exp(math.log(P_ZMAX) * (s * s * (3 - 2 * s) * 0.55 + s * s * 0.45))


def portal_card(card_raw, geom, s):
    cx, cy, _, _ = geom
    z = portal_zoom(s)
    im = card_raw.convert('RGB')
    a = 1.0 / z
    return im.transform((W, H), Image.AFFINE, (a, 0, cx - a * cx, 0, a, cy - a * cy), Image.BICUBIC,
                        fillcolor=(10, 10, 10))


def portal_mix(card_post, b, geom, s):
    """card_post: zoomed + post-processed card (array); b: incoming scene (array)"""
    cx, cy, rx0, ry0 = geom
    s0 = P_PRE / (P_PRE + P_POST)
    p = clamp((s - s0) / (1 - s0))
    z = portal_zoom(s) * (1 + 0.9 * p ** 3)
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.hypot((xx - cx) / (rx0 * z), (yy - cy) / (ry0 * z))
    soft = max(2.0, rx0 * z * 0.05)
    inside = np.clip((1.0 - d) * rx0 * z / soft, 0, 1)
    # v48: the O's counter is a window pane that slides UP like a sash, revealing the scene from the bottom
    o = eio(clamp(p / 0.42))
    ry = ry0 * z
    yb = cy + ry - o * 2.0 * ry * 1.02                 # bottom edge of the rising pane
    bsoft = max(1.5, ry * 0.012)
    below = np.clip((yy - yb) / bsoft, 0, 1)
    m = (inside * below)[..., None]
    # the scene beyond the hole grows toward us and settles exactly as the hole fills the frame
    bs = lerp(0.72, 1.0, 1 - (1 - p) ** 2)
    bi = Image.fromarray(b)
    ai = 1.0 / bs
    bz = np.asarray(bi.transform((W, H), Image.AFFINE, (ai, 0, cx - ai * cx, 0, ai, cy - ai * cy), Image.BICUBIC,
                                 fillcolor=(10, 10, 10)), np.float32)
    bz = bz * (1 - 0.55 * np.clip(1 - (yy - yb) / max(4.0, ry * 0.08), 0, 1)[..., None] * (yy >= yb)[..., None])  # shadow under the pane
    out = card_post.astype(np.float32) * (1 - m) + bz * m
    if 0.0 < o < 1.0:                                   # bright sash edge on the pane's bottom
        ew = max(2.0, ry * 0.018)
        edge = (np.clip(1 - np.abs(yy - yb) / ew, 0, 1) * inside)[..., None] * (1 - o ** 4)
        out = out * (1 - edge) + np.array([255, 226, 150], np.float32) * edge
    return out.clip(0, 255).astype(np.uint8)


# ---------------------------------------------------------------- 1: through the O (v38, replaced by 1b)
def t_portal(a, b, u):
    segs, y0, y1 = letter_segments(a)
    if len(segs) >= 6:
        s = segs[4]                      # second O of DOOM
    else:
        s = (W // 2 - 60, W // 2 + 60)
    cx, cy = (s[0] + s[1]) / 2, (y0 + y1) / 2
    rx0 = (s[1] - s[0]) * 0.21           # the O's counter (an upright oval)
    ry0 = (y1 - y0) * 0.30
    e = _ease(u)
    z = math.exp(math.log(28.0) * e ** 1.6)
    az = zoom_about(a, z, cx, cy)
    bz = zoom_about(b, lerp(1.6, 1.0, e), W / 2, H / 2)
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.hypot((xx - cx) / (rx0 * z), (yy - cy) / (ry0 * z))
    m = np.clip((1.0 - d) * rx0 * z / 3.0, 0, 1)[..., None]
    return (az * (1 - m) + bz * m).astype(np.uint8)


# ---------------------------------------------------------------- 2: venetian slices
def t_slices(a, b, u, n=14):
    out = b.astype(np.float32).copy()
    hh = H / n
    for i in range(n):
        y0, y1 = int(i * hh), int((i + 1) * hh)
        uu = clamp((u - 0.22 * abs(i + 0.5 - n / 2) / (n / 2)) / 0.78)
        e = _ease(uu) ** 1.5
        dirn = 1 if i % 2 == 0 else -1
        dx = int(dirn * e * W * 1.15)
        strip = a[y0:y1].astype(np.float32)
        # trailing echoes: three ghost copies behind the moving strip
        for k, al in ((3, 0.18), (2, 0.32), (1, 0.55), (0, 1.0)):
            ox = int(dx - dirn * k * 60 * e)
            xs0, xs1 = max(0, ox), min(W, W + ox)
            if xs1 <= xs0:
                continue
            src = strip[:, xs0 - ox:xs1 - ox]
            out[y0:y1, xs0:xs1] = out[y0:y1, xs0:xs1] * (1 - al) + src * al
    return out.clip(0, 255).astype(np.uint8)


# ---------------------------------------------------------------- 3: letters drop out
def t_drop(a, b, u):
    segs, y0, y1 = letter_segments(a)
    e = _ease(clamp(u / 0.55))
    # the gold card tears open from the centre line first
    gap = int(e * H * 0.5)
    out = b.astype(np.float32).copy()
    card = a.astype(np.float32).copy()
    inkm = a[..., :3].mean(axis=2) < 90
    inkm[:int(H * 0.25)] = False; inkm[int(H * 0.8):] = False
    card[inkm] = np.median(card[int(H * 0.3):int(H * 0.7), :40].reshape(-1, 3), axis=0)  # letters lifted off the card
    if gap < H // 2:
        out[:H // 2 - gap] = card[gap:H // 2]
        out[H // 2 + gap:] = card[H // 2:H - gap]
    # letters fall one after another with echo trails
    lum = a[..., :3].mean(axis=2)
    for i, (x0, x1) in enumerate(segs):
        uu = clamp((u - 0.06 * i) / 0.6)
        if uu >= 1:
            continue
        fall = (uu ** 2) * H * 1.3
        col = a[y0 - 4:y1 + 5, x0:x1].astype(np.float32)
        m = (lum[y0 - 4:y1 + 5, x0:x1] < 90)[..., None].astype(np.float32)
        ink = np.full_like(col, 244.0)            # letters flip to paper white as they drop
        ink[..., 1] = 244; ink[..., 2] = 240
        for k, al in ((3, 0.15), (2, 0.28), (1, 0.5), (0, 1.0)):
            yy = int(y0 - 4 + fall - k * 34 * min(1, uu * 4))
            ya, yb = max(0, yy), min(H, yy + col.shape[0])
            if yb <= ya:
                continue
            mm = m[ya - yy:yb - yy] * al
            c = ink[ya - yy:yb - yy] if k == 0 else np.array(GOLD_RGB)[None, None, :]
            out[ya:yb, x0:x1] = out[ya:yb, x0:x1] * (1 - mm) + c * mm
    return out.clip(0, 255).astype(np.uint8)


# ---------------------------------------------------------------- 4: tile flip wave
def t_tiles(a, b, u, n=12):
    ts = W // n
    out = np.empty_like(a)
    for gy in range(0, H, ts):
        for gx in range(0, W, ts):
            k = (gx / W + gy / H) / 2.0             # diagonal wave from top-left
            uu = clamp((u - k * 0.5) / 0.45)
            ang = uu * math.pi
            sx = abs(math.cos(ang))
            src = a if ang < math.pi / 2 else b
            tile = src[gy:gy + ts, gx:gx + ts]
            th, tw = tile.shape[:2]
            cell = np.empty_like(tile)
            cell[:] = (10, 10, 10)
            w2 = max(1, int(tw * sx))
            if w2 > 1:
                sq = np.asarray(Image.fromarray(tile).resize((w2, th), Image.BILINEAR))
                o = (tw - w2) // 2
                cell[:, o:o + w2] = sq
                if 0.05 < uu < 0.95:                  # gold edge on the flipping tile
                    cell[:, o:o + 3] = GOLD_RGB
                    cell[:, o + w2 - 3:o + w2] = GOLD_RGB
            out[gy:gy + th, gx:gx + tw] = cell
    return out


# ---------------------------------------------------------------- 2 (v54): fang slash
def t_slash(a, b, u):
    """three diagonal claw/fang slashes rip across the gold card, then the four shards
    slide apart along the cuts (alternating up/down), tilting and dimming, revealing the basilisk"""
    from PIL import ImageDraw, ImageFilter
    cuts = [560, 960, 1360]                 # x of each cut at mid height
    sl = 0.42                               # slant: x shift per y
    def xcut(c, y):
        return c + sl * (y - H / 2)
    out = Image.fromarray(b).convert('RGB')
    A0 = Image.fromarray(a).convert('RGB')
    P = 1500                                 # pad so shards never show the card's frame edge
    edgec = tuple(int(v) for v in np.median(a[int(H * 0.05):int(H * 0.2), :60].reshape(-1, 3), axis=0))
    A = Image.new('RGB', (W + 2 * P, H + 2 * P), edgec)
    A.paste(A0, (P, P))
    # cut lines are drawn quickly one after another (0 .. 0.32), then the shards part (0.22 .. 1)
    sep = _ease(clamp((u - 0.22) / 0.78))
    edges = [-10 ** 4] + cuts + [10 ** 4]
    dl = math.hypot(sl, 1.0)
    dx_al, dy_al = sl / dl, 1 / dl          # direction along a cut (down-right)
    for i in range(4):
        c0, c1 = edges[i], edges[i + 1]
        poly = []
        for c, ys in ((c0, (-P, H + P)), (c1, (H + P, -P))):
            for y in ys:
                x = -P if c < -1000 else (W + P if c > 1000 else xcut(c, y))
                poly.append((x + P, y + P))
        m = Image.new('L', (W + 2 * P, H + 2 * P), 0)
        ImageDraw.Draw(m).polygon(poly, fill=255)
        dirn = -1 if i % 2 == 0 else 1
        mag = sep ** 1.3 * H * 0.55
        pm = (i - 1.5) * sep ** 1.5 * W * 0.85        # shards part sideways, outer ones leave frame
        ox = dirn * mag * dx_al + pm * dy_al
        oy = dirn * mag * dy_al - pm * dx_al
        z = 1.0
        cx, cy = W / 2, H / 2
        az = 1 / z
        co = (az, 0, cx - az * (cx + ox) + P, 0, az, cy - az * (cy + oy) + P)
        As = A.transform((W, H), Image.AFFINE, co, Image.BILINEAR)
        ms = m.transform((W, H), Image.AFFINE, co, Image.BILINEAR)
        if sep > 0:
            dim = 1 - 0.45 * sep
            As = Image.eval(As, lambda v, d=dim: int(v * d))
        out.paste(As, (0, 0), ms)
        # glowing torn edges on the moving shard
        if 0 < sep < 1:
            d = ImageDraw.Draw(out)
            for c in (c0, c1):
                if abs(c) > 1000:
                    continue
                p0 = ((xcut(c, -50) - cx) * z + cx + ox, (-50 - cy) * z + cy + oy)
                p1 = ((xcut(c, H + 50) - cx) * z + cx + ox, (H + 50 - cy) * z + cy + oy)
                d.line([p0, p1], fill=(245, 180, 32), width=4)
    # the slash strokes themselves: white-hot, drawn top to bottom, glow fading as shards part
    gl = Image.new('RGB', (W, H), (0, 0, 0))
    d = ImageDraw.Draw(gl)
    for k, c in enumerate(cuts):
        uu = clamp((u - 0.07 * k) / 0.16)
        if uu <= 0:
            continue
        fade = 1 - clamp((u - 0.3 - 0.05 * k) / 0.35)
        if fade <= 0:
            continue
        y1 = -50 + (H + 100) * _ease(uu)
        col = tuple(int(v * fade) for v in (255, 246, 214))
        d.line([(xcut(c, -50), -50), (xcut(c, y1), y1)], fill=col, width=10)
    if gl.getbbox():
        glow = gl.filter(ImageFilter.GaussianBlur(14))
        o = np.asarray(out).astype(np.float32)
        o = o + np.asarray(glow).astype(np.float32) * np.array([1.6, 1.3, 0.6]) + np.asarray(gl).astype(np.float32)
        out = Image.fromarray(o.clip(0, 255).astype(np.uint8))
    return np.asarray(out)


EXITS = {6: t_portal, 17: t_slash, 28: t_drop, 40: t_tiles}
DURS = {17: 0.62, 40: 0.2}   # v127: Loom must be on screen while "Just" is sung (was 0.46)
