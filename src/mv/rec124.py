# v124 candidate: RECURSIVE SELF-UPGRADE overhaul (129.87 - 132.02)
# The gold cube builds a 2x bigger, more complex copy of itself around itself on each beat, faster every time:
# cube -> octahedron -> icosahedron -> lattice -> Menger sponge L1 -> Menger sponge L2. Earlier generations stay
# nested inside the newer ones. Version counter v1 -> v65,536 -> v-infinity, a CAPABILITY graph going vertical,
# then the fractal blazes and collapses to a point with a flash, handing off to the Ilya vault.
import math
from cam3d import *
from s3a import T0, T1, WT
from ov116 import beats, capcam, glow

BUILDS = [(130.02, 130.30), (130.33, 130.75), (130.79, 131.20), (131.24, 131.46), (131.48, 131.68)]
VERS = ['v1.0', 'v2.0', 'v4.0', 'v16', 'v256', 'v65,536']
BASE = 170.0


def _cube_edges(c, h):
    V = [(c[0] + sx * h, c[1] + sy * h, c[2] + sz * h) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
    E = [(a, b) for a in range(8) for b in range(a + 1, 8) if bin(a ^ b).count('1') == 1]
    return [(V[a], V[b]) for a, b in E]


def _menger(level, c=(0.0, 0.0, 0.0), h=1.0):
    if level == 0:
        return [(c, h)]
    out = []
    s = h / 3 * 2
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            for k in (-1, 0, 1):
                if abs(i) + abs(j) + abs(k) <= 1:
                    continue
                out += _menger(level - 1, (c[0] + i * s, c[1] + j * s, c[2] + k * s), h / 3)
    return out


def _shape(k):
    """unit-size edge list (radius ~1) for generation k"""
    if k == 0:
        return _cube_edges((0, 0, 0), 0.6)
    if k == 1:
        V = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
        return [(V[a], V[b]) for a in range(6) for b in range(a + 1, 6) if a // 2 != b // 2]
    if k == 2:
        p = (1 + 5 ** 0.5) / 2
        V = []
        for a in (-1, 1):
            for b in (-p, p):
                V += [(0, a, b), (a, b, 0), (b, 0, a)]
        n = math.sqrt(1 + p * p)
        V = [v_mul(v, 1 / n) for v in V]
        E = [(V[a], V[b]) for a in range(12) for b in range(a + 1, 12) if abs(math.dist(V[a], V[b]) - 2 / n) < 1e-3]
        return E
    if k == 3:
        E = []
        h = 0.62; n = 4
        xs = [-h + 2 * h * i / (n - 1) for i in range(n)]
        for a in xs:
            for b in xs:
                E += [((-h, a, b), (h, a, b)), ((a, -h, b), (a, h, b)), ((a, b, -h), (a, b, h))]
        return E
    lvl = 1 if k == 4 else 2
    E = []
    for c, h in _menger(lvl, (0, 0, 0), 0.62):
        E += _cube_edges(c, h)
    return E


SHAPES = [_shape(k) for k in range(6)]
SHAPES = [sorted(E, key=lambda e: -(e[0][1] + e[1][1])) for E in SHAPES]   # build bottom-up (y down = +)


def _zf(t):
    """continuous generation count"""
    z = 0.0
    for a, b in BUILDS:
        z += eio(prog(t, a, b))
    return z


def s_recursive(g, t, lt):
    t0 = T0(43); tE = T0(44)
    bt = beats(t0 - 0.5, t + 0.001)
    lb = bt[-1] if bt else t0
    pb = math.exp(-(t - lb) * 8)
    zf = _zf(t)
    blaze = prog(t, 131.68, 131.88)
    coll = eio(prog(t, 131.86, tE - 0.02))
    zc = sum(eio(prog(t, a - 0.06, a + (b - a) * 0.6)) for a, b in BUILDS)   # camera pulls back ahead of each build
    S = BASE * 2 ** min(zc + 0.6 * blaze, 5.6)
    yaw = -0.5 + 1.6 * prog(t, t0, tE) + 0.25 * zf
    pitch = 0.32 + 0.1 * math.sin(zf)
    D = 4.2 * S * (1 - 0.03 * pb)
    cam = Cam3(orbit((0, 0, 0), D, yaw, pitch), (0, -0.05 * S, 0), 54, 0.05 * math.sin(t * 1.4))
    env(g, cam)
    k_done = sum(1 for a, b in BUILDS if t >= b)
    shrink = 1 - coll
    rot = t * 0.35
    xf = lambda p, s: v_mul(rot3(p, rot * (0.6 if s % 2 else -0.4), 0, 0.15), shrink)
    # innermost: the original solid gold cube (v1.0)
    F = SFaces()
    F.sbox((0, 0, 0), (BASE * 1.2, BASE * 1.2, BASE * 1.2), GOLD, GOLDL, 2, xf=lambda p: xf(p, 0), amb=0.5)
    F.draw(g, cam)
    hot = min(1.0, blaze * 1.4)
    for k in range(1, 6):
        a, b = BUILDS[k - 1]
        bp = prog(t, a, b)
        if bp <= 0:
            break
        s = BASE * 2 ** k
        E = SHAPES[k]
        n = len(E) if bp >= 1 else int(len(E) * eo(bp))
        newest = (k == k_done + 1) or (k == k_done and t - b < 0.15)
        age = k_done - k
        col = GOLDL if (newest or hot > 0) else GOLD
        al = (1.0 if newest else clamp(0.85 - 0.12 * age)) * (1 - 0.6 * coll) + 0.0
        w = (3.2 if newest else 2.0) * (1 + 1.5 * hot) * (0.6 if k >= 5 else 1.0)
        for (p, q) in E[:n]:
            seg3(g, cam, xf(v_mul(p, s), k), xf(v_mul(q, s), k), col, w, al, wscale=False)
        if 0 < bp < 1:
            # scan plane + sparks at the build front
            yv = s * 0.7 * (1 - 2 * eo(bp))
            ring = [xf((s * 1.05 * math.cos(u), yv, s * 1.05 * math.sin(u)), k) for u in [2 * math.pi * i / 48 for i in range(49)]]
            poly3(g, cam, ring, GOLDL, 3, 0.9)
            for i in range(40):
                u = hsh(i, int(t * 30)) * 6.283
                r = s * (0.3 + 0.75 * hsh(i + 3, int(t * 30)))
                point3(g, cam, xf((r * math.cos(u), yv, r * math.sin(u)), k), 4, GOLDL, 0.9)
            # beams from the previous generation to the build front
            for i in range(4):
                u = hsh(i, int(t * 24)) * 6.283
                seg3(g, cam, xf((0, 0, 0), k), xf((s * math.cos(u), yv, s * math.sin(u)), k), GOLDL, 2, 0.5, wscale=False)
    glow(g, cam, (0, 0, 0), S * (0.8 + 2.5 * hot) * max(0.05, shrink), GOLD, 0.25 + 0.6 * hot)
    for b_ in beats(t0, tE):
        e = t - b_
        if 0 <= e < 0.3:
            g.flash = max(g.flash, 0.1 * (1 - e / 0.3)); g.flash_c = GOLDL
    for a, b in BUILDS:
        e = t - b
        if 0 <= e < 0.2:
            g.flash = max(g.flash, 0.14 * (1 - e / 0.2))
    if t > tE - 0.12:
        g.flash = max(g.flash, 0.9 * prog(t, tE - 0.12, tE - 0.02)); g.flash_c = GOLDL
    # HUD: version counter (bottom left) and capability curve (bottom right)
    ver = 'v\u221e' if blaze > 0.3 else VERS[min(5, k_done)]
    g.text('SELF_UPGRADE', 90, H - 190, 28, DIM, 'mono', 0.9, 'lm')
    g.text(ver, 90, H - 130, 78 if blaze > 0.3 else 64, GOLD, 'monox', 1.0, 'lm')
    bx, by, bw, bh = W - 470, H - 250, 380, 170
    g.line([bx, by, bx, by + bh, bx + bw, by + bh], DIM, 2, 0.8)
    g.text('CAPABILITY', bx, by - 22, 22, DIM, 'mono', 0.9, 'lm')
    up = prog(t, t0, 131.85)
    pts = []
    for i in range(61):
        x = i / 60
        if x > up:
            break
        y = (math.exp(6 * x ** 1.6) - 1) / (math.exp(6) - 1)
        pts += [bx + x * bw, by + bh - min(1.15, y) * bh]
    if len(pts) >= 4:
        g.line(pts, GOLD, 3, 1)
    camc, c, r, u = capcam()
    lyric3x(g, camc, t, 43, v_add(c, v_mul(camc.u, -350)), r, u, 1400, 105, INK, {'recursive': GOLD, 'self-upgrade': GOLD}, depth=40)
    g.post = dict(glow=0.6)
