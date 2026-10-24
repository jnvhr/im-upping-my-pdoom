"""Shared motion-graphics kit: blueprint grids, HUD, P(doom) counter, wireframe meshes,
kinetic type helpers. Palette is strictly obsidian / off-white / electric gold / grid grey."""
import math
from core import *
from lyrics import *

# ------------------------------------------------------------------ P(doom)
PD_KEYS = [(0, 0.01), (6.0, 0.01), (6.5, 0.02), (13.0, 0.02), (13.5, 0.04), (23.0, 0.04),
           (23.5, 0.07), (26.0, 0.08), (45.0, 0.11), (53.0, 0.13), (57.4, 0.14), (57.7, 0.25),
           (59.0, 0.25), (59.5, 0.33), (66.0, 0.36), (81.0, 0.44), (95.4, 0.49), (96.0, 0.58),
           (102.0, 0.66), (110.0, 0.72), (114.2, 0.78), (114.4, 0.89), (120.9, 0.90),
           (121.6, 0.93), (121.9, 0.999999), (141.4, 0.999999)]


def pd_value(t):
    if t <= PD_KEYS[0][0]:
        return PD_KEYS[0][1]
    for (t0, v0), (t1, v1) in zip(PD_KEYS, PD_KEYS[1:]):
        if t0 <= t < t1:
            return lerp(v0, v1, smooth((t - t0) / (t1 - t0)))
    return PD_KEYS[-1][1]


OUTRO = 140.24
PD_STAGES = [(OUTRO, '1.000000'), (143.2, '100%'), (145.2, '\u221e'),
             (147.2, 'ALEPH_NULL'), (149.2, 'STACK_OVERFLOW'), (151.0, 'NaN')]
GLYPHS = '0123456789#%&@$!?<>/\\=+*'


def pd_str(t):
    if t < OUTRO:
        v = pd_value(t)
        if v >= 0.99:
            return '%.6f' % v
        return '%.2f' % v
    s = PD_STAGES[0][1]
    for ts, ss in PD_STAGES:
        if t >= ts:
            s = ss; st = ts
    # glitch for 0.25s after each stage change
    if t - st < 0.25:
        k = int(t * 40)
        s = ''.join(GLYPHS[int(hsh(k, i) * len(GLYPHS))] if hsh(k, i + 50) < 0.6 else ch for i, ch in enumerate(s))
    return s


# ------------------------------------------------------------------ grids
def grid(g, step=60, c=GRID, major=5, a=1.0, ox=0.0, oy=0.0, cmaj=None, w=1.0, x0=0, y0=0, x1=W, y1=H):
    cmaj = cmaj or GRID2
    i0 = int(math.floor((x0 - ox) / step)) - 1
    i1 = int(math.ceil((x1 - ox) / step)) + 1
    for i in range(i0, i1):
        x = ox + i * step
        if x0 <= x <= x1:
            mj = i % major == 0
            g.line((x, y0, x, y1), cmaj if mj else c, w * (1.4 if mj else 1), a)
    j0 = int(math.floor((y0 - oy) / step)) - 1
    j1 = int(math.ceil((y1 - oy) / step)) + 1
    for j in range(j0, j1):
        y = oy + j * step
        if y0 <= y <= y1:
            mj = j % major == 0
            g.line((x0, y, x1, y), cmaj if mj else c, w * (1.4 if mj else 1), a)


def persp_grid(g, t, horizon=H * 0.45, c=GRID2, a=1.0, speed=0.0, n=22, spread=3.2, ripple=None, cx=W / 2):
    """floor plane receding to a horizon. ripple(x_norm, z) -> dy"""
    for k in range(n):
        z = (k + (speed * t) % 1.0)
        zz = 1 + z * 0.55
        y = horizon + (H - horizon) * 1.0 / zz * 1.0
        if ripple is None:
            g.line((0, y, W, y), c, 1.2, a * clamp(1.6 / zz))
        else:
            pts = []
            for i in range(41):
                xn = i / 40
                pts += [xn * W, y + ripple(xn, z) / zz]
            g.line(pts, c, 1.3, a * clamp(1.6 / zz))
    for i in range(-14, 15):
        x_far = cx + i * 18
        x_near = cx + i * 18 * spread * 6
        g.line((x_far, horizon + 2, x_near, H + 40), c, 1.0, a * 0.8)


def corners(g, x0, y0, x1, y1, L=26, c=GOLD, w=2.5, a=1.0):
    for (x, y, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        g.line((x + sx * L, y, x, y, x, y + sy * L), c, w, a)


def tag(g, x, y, s, c=GOLD, size=17, a=1.0, anchor='lm', box=True, fill=None, tc=None):
    w, h = g.tsize(s, size, 'mono')
    ax = {'l': 0, 'm': w / 2, 'r': w}[anchor[0]]
    ay = {'t': 0, 'm': h / 2, 'b': h}[anchor[1]]
    x0, y0 = x - ax - 8, y - ay - 5
    if box:
        if fill is not None:
            g.rect(x0, y0, x0 + w + 16, y0 + h + 10, fill=fill, a=a)
        g.rect(x0, y0, x0 + w + 16, y0 + h + 10, stroke=c, w=1.4, a=a * 0.9)
    g.text(s, x0 + 8, y0 + 5, size, tc or c, 'mono', a, 'lt')
    return w + 16


def readout(g, x, y, rows, size=15, c=INK, hc=GOLD, a=1.0, gap=1.45):
    for i, (k, v) in enumerate(rows):
        g.text(k, x, y + i * size * gap, size, DIM, 'monor', a, 'lm')
        g.text(str(v), x + size * 11, y + i * size * gap, size, hc if i == 0 else c, 'mono', a, 'lm')


def ticks(g, x, y, length, n=40, c=GRID2, a=1.0, vertical=False, major=5):
    for i in range(n + 1):
        L = 12 if i % major == 0 else 6
        p = length * i / n
        if vertical:
            g.line((x, y + p, x + L, y + p), c, 1.2, a)
        else:
            g.line((x + p, y, x + p, y - L), c, 1.2, a)


def ekg(g, x0, y0, w, h, t, c=GOLD, a=1.0, spike=1.0, speed=1.0, seed=0, lw=2.5):
    pts = []
    n = 160
    for i in range(n + 1):
        u = i / n
        ph = (u * 3.0 - t * speed * 1.3 + seed) % 1.0
        v = 0
        if 0.40 < ph < 0.44:
            v = -0.25
        elif 0.46 < ph < 0.49:
            v = 1.0 * spike
        elif 0.49 < ph < 0.52:
            v = -0.55 * spike
        elif 0.60 < ph < 0.68:
            v = -0.18
        v += (noise1(u * 40 + t * 9, seed) - 0.5) * 0.15 * spike
        pts += [x0 + u * w, y0 - v * h]
    g.line(pts, c, lw, a)


def spectrum(g, x0, y0, w, h, t, n=48, c=GOLD, a=1.0, seed=3, melan=False, gap=0.35):
    bw = w / n
    lv = feat('rms', t)
    for i in range(n):
        u = i / n
        base = math.exp(-((u - 0.25) ** 2) / 0.08) if melan else (1 - u * 0.6)
        v = base * (0.35 + 0.65 * noise1(t * 6 + i * 0.7, seed)) * (0.5 + lv * 0.8)
        hh = h * clamp(v, 0.02, 1.0)
        g.rect(x0 + i * bw, y0 - hh, x0 + (i + 1 - gap) * bw, y0, fill=c, a=a)


# ------------------------------------------------------------------ 3D wireframe
def rot3(p, rx=0.0, ry=0.0, rz=0.0):
    x, y, z = p
    if rz:
        c, s = math.cos(rz), math.sin(rz); x, y = x * c - y * s, x * s + y * c
    if ry:
        c, s = math.cos(ry), math.sin(ry); x, z = x * c + z * s, -x * s + z * c
    if rx:
        c, s = math.cos(rx), math.sin(rx); y, z = y * c - z * s, y * s + z * c
    return x, y, z


class Cam:
    def __init__(self, cx=W / 2, cy=H / 2, f=1000.0, dist=1200.0, rx=0.0, ry=0.0, rz=0.0):
        self.cx, self.cy, self.f, self.dist, self.rx, self.ry, self.rz = cx, cy, f, dist, rx, ry, rz

    def p(self, x, y, z):
        x, y, z = rot3((x, y, z), self.rx, self.ry, self.rz)
        zz = z + self.dist
        if zz < 20:
            zz = 20
        k = self.f / zz
        return self.cx + x * k, self.cy + y * k, k


def draw_edges(g, cam, verts, edges, c=GOLD, w=2.0, a=1.0, xf=None, depth=True):
    pv = []
    for v in verts:
        if xf is not None:
            v = xf(v)
        pv.append(cam.p(*v))
    for (i, j) in edges:
        x0, y0, k0 = pv[i]; x1, y1, k1 = pv[j]
        aa = a
        if depth:
            aa = a * clamp(0.35 + 0.65 * (k0 + k1) / 2 / (cam.f / cam.dist))
        g.line((x0, y0, x1, y1), c, w * clamp((k0 + k1) / 2 / (cam.f / cam.dist), 0.4, 2.2), aa)
    return pv


def box_mesh(sx, sy, sz, ox=0, oy=0, oz=0):
    v = [(ox + x * sx / 2, oy + y * sy / 2, oz + z * sz / 2) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    e = [(0, 1), (2, 3), (4, 5), (6, 7), (0, 2), (1, 3), (4, 6), (5, 7), (0, 4), (1, 5), (2, 6), (3, 7)]
    return v, e


def ring_mesh(r, n=48, y=0.0, axis='y', ox=0, oy=0, oz=0):
    v = []
    for i in range(n):
        a = 2 * math.pi * i / n
        if axis == 'y':
            v.append((ox + r * math.cos(a), oy + y, oz + r * math.sin(a)))
        elif axis == 'z':
            v.append((ox + r * math.cos(a), oy + r * math.sin(a), oz + y))
        else:
            v.append((ox + y, oy + r * math.cos(a), oz + r * math.sin(a)))
    e = [(i, (i + 1) % n) for i in range(n)]
    return v, e


def merge(*meshes):
    V, E = [], []
    for v, e in meshes:
        o = len(V); V += v; E += [(a + o, b + o) for a, b in e]
    return V, E


def cyl_mesh(r, h, n=24, rings=2, axis='y'):
    ms = [ring_mesh(r, n, y=-h / 2 + h * k / (rings - 1), axis=axis) for k in range(rings)]
    V, E = merge(*ms)
    for i in range(0, n, max(1, n // 12)):
        for k in range(rings - 1):
            E.append((k * n + i, (k + 1) * n + i))
    return V, E


def sphere_mesh(r, nlat=8, nlon=16):
    V, E = [], []
    for i in range(1, nlat):
        th = math.pi * i / nlat
        o = len(V)
        for j in range(nlon):
            ph = 2 * math.pi * j / nlon
            V.append((r * math.sin(th) * math.cos(ph), r * math.cos(th), r * math.sin(th) * math.sin(ph)))
            E.append((o + j, o + (j + 1) % nlon))
        if i > 1:
            for j in range(nlon):
                E.append((o + j, o - nlon + j))
    return V, E


def torus_mesh(R, r, nu=36, nv=10):
    V, E = [], []
    for i in range(nu):
        u = 2 * math.pi * i / nu
        for j in range(nv):
            v = 2 * math.pi * j / nv
            V.append(((R + r * math.cos(v)) * math.cos(u), r * math.sin(v), (R + r * math.cos(v)) * math.sin(u)))
    for i in range(nu):
        for j in range(nv):
            a = i * nv + j
            E.append((a, i * nv + (j + 1) % nv))
            E.append((a, ((i + 1) % nu) * nv + j))
    return V, E


# ------------------------------------------------------------------ type
def slam(g, s, x, y, size, t, t0, c=INK, font='sans', a=1.0, rot=0.0, overshoot=1.6, dur=0.18, anchor='mm'):
    """word slams in from large scale at t0"""
    if t < t0:
        return
    p = prog(t, t0, t0 + dur)
    sc = lerp(overshoot, 1.0, eo(p))
    g.text(s, x, y, size, c, font, a * min(1, p * 3 + 0.2), anchor, rot=rot, sx=sc)


def fit_size(g, s, maxw, size, font='sans'):
    w, _ = g.tsize(s, size, font)
    if w > maxw:
        size = size * maxw / w
    return size


def kinetic_line(g, t, li, y, size=120, c=INK, hl=None, font='sans', upper=True, maxw=1560, style='pop', hold=0.4, x=W / 2, anchor='m', dimc=None):
    return lyric(g, t, li, x, y, size, c, font, hl=hl, upper=upper, maxw=maxw, style=style, hold=hold, anchor=anchor, dimc=dimc)


def word_on(t, li, idx):
    return t >= word_time(li, idx)


def scramble(s, t, t0, dur=0.35, seed=0):
    p = prog(t, t0, t0 + dur)
    n = int(len(s) * p)
    out = s[:n]
    for i in range(n, len(s)):
        out += GLYPHS[int(hsh(int(t * 30), i + seed) * len(GLYPHS))] if s[i] != ' ' else ' '
    return out


# ------------------------------------------------------------------ HUD
def hud(g, t, a=1.0, dx=0.0, dy=0.0, light=False, pd_scale=1.0, minimal=False):
    """persistent frame HUD with the P(doom) counter"""
    if a <= 0.01:
        return
    ink = BLACK if light else INK
    dim = (120, 116, 108) if light else DIM
    m = 34
    corners(g, m + dx, m + dy, W - m + dx, H - m + dy, L=34, c=GOLD, w=2.2, a=a * 0.9)
    if not minimal:
        tc = '%02d:%02d:%02d' % (int(t // 60), int(t % 60), int(t * 30) % 30)
        g.text('TC ' + tc, m + 22 + dx, m + 26 + dy, 15, dim, 'monor', a, 'lm')
        g.text('BPM %d  //  BAR %03d  BEAT %d' % (int(round(__import__('warp105').bpm_at(t))), int(beat(t) // 4) + 1, int(beat(t)) % 4 + 1), m + 22 + dx, H - m - 24 + dy, 15, dim, 'monor', a, 'lm')
        g.text('UPPING_MY_P(DOOM).MP3', W - m - 22 + dx, H - m - 24 + dy, 15, dim, 'monor', a, 'rm')
        # v132: level-meter audio visualizer removed (she asked)
    # P(doom)
    s = pd_str(t)
    x = W - m - 26 + dx
    y = m + 30 + dy
    g.text('P(DOOM)', x, y, 15 * pd_scale, dim, 'mono', a, 'rm')
    sz = 44 * pd_scale
    fl = pulse(t, 1, 9) * 0.25 if t > 95 else 0
    g.text(s, x, y + 40 * pd_scale, sz, GOLD, 'monox', a, 'rm')
    v = pd_value(t) if t < OUTRO else 1.0
    bw = 210 * pd_scale
    g.rect(x - bw, y + 72 * pd_scale, x, y + 77 * pd_scale, fill=(PGRID if light else GRID), a=a)
    g.rect(x - bw, y + 72 * pd_scale, x - bw + bw * clamp(v), y + 77 * pd_scale, fill=GOLD, a=a)
    # v131: blinking live dot removed (she asked)
