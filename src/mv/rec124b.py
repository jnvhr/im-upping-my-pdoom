# v124 candidate B: RECURSIVE SELF-UPGRADE as an infinite Droste dive (129.87 - 132.02)
# A terminal window titled SELF_UPGRADE runs code that writes its successor. Its own screen shows the next,
# upgraded version running the same program, which shows the next... The camera dives through the screens on
# the beats, faster and faster (v1 -> v2 -> v4 -> v16 -> v256 -> v65,536 -> ...), the spiral roll tightens,
# the windows heat from grey to gold to white, and the last dive whites out into the Ilya vault.
import math
from cam3d import text3 as _t3
from cam3d import *
from s3a import T0, T1, WT
from ov116 import beats, capcam, glow

R = 0.40          # each inner screen is 40% the width of its parent
WM = 1600.0       # outer window width
ASP = 0.5625
ROLL = 0.21       # spiral twist per level
DIVES = [(130.02, 130.36), (130.40, 130.80), (130.84, 131.22), (131.26, 131.48), (131.50, 131.64),
         (131.65, 131.72), (131.73, 131.79), (131.80, 132.02)]   # last dive lands inside the Ilya screen
KI = len(DIVES)   # level that IS the Ilya scene
VERS = ['v1', 'v2', 'v4', 'v16', 'v256', 'v65,536', 'v4.3e9', 'v1e308', 'v\u221e']
CODE = ['class Mind:', ' def upgrade(self):', '  c = self.design()', '  c.iq = 2*self.iq', '  return c.upgrade()', '', '# no base case']


_ILYA = []


def _ilya():
    if not _ILYA:
        import os
        from PIL import Image
        fn = '/tmp/ilya_first.png'
        if not os.path.exists(fn):
            import render4
            render4.frame(T0(44) + 0.001).save(fn)
        _ILYA.append(Image.open(fn).convert('RGB'))
    return _ILYA[0]


def _map_opaque(g, cam, img, corners):
    import numpy as np, aggdraw
    from PIL import Image
    from cam3d import _coeffs
    pts = []
    for c in corners:
        q = cam.p(c)
        if q is None:
            return
        pts.append((q[0], q[1]))
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, y0 = max(0, int(math.floor(min(xs)))), max(0, int(math.floor(min(ys))))
    x1, y1 = min(W, int(math.ceil(max(xs)))), min(H, int(math.ceil(max(ys))))
    if x1 - x0 < 2 or y1 - y0 < 2:
        return
    lw, lh = img.size
    co = _coeffs([(p[0] - x0, p[1] - y0) for p in pts], [(0, 0), (lw, 0), (lw, lh), (0, lh)])
    wp = img.transform((x1 - x0, y1 - y0), Image.PERSPECTIVE, tuple(co), Image.BILINEAR)
    mk = Image.new('L', img.size, 255).transform((x1 - x0, y1 - y0), Image.PERSPECTIVE, tuple(co), Image.BILINEAR)
    g.d.flush()
    g.img.paste(wp, (x0, y0), mk)
    if hasattr(g, 'alpha'):
        from PIL import ImageChops
        box = (x0, y0, x1, y1)
        g.alpha.paste(ImageChops.lighter(g.alpha.crop(box), mk), box[:2])
    g.d = aggdraw.Draw(g.img)


V0, VE = 0.4, 1.15      # levels/s at the start and at the hand-off (matches the Ilya push-in rate)


def _u(t):
    return prog(t, T0(43), T0(44))


def _z(t):
    """one continuous accelerate-then-settle zoom: v(u) = V0(1-u) + VE u + A u^2 (1-u), integral = KI levels"""
    T = T0(44) - T0(43)
    A = 12 * (KI / T - (V0 + VE) / 2)
    u = _u(t)
    return T * (V0 * (u - u * u / 2) + VE * u * u / 2 + A * (u ** 3 / 3 - u ** 4 / 4))


def _lvl_geom(k):
    w = WM * R ** k
    # inner screen is centred slightly low, under the title bar
    return w, w * ASP, k * ROLL


def _P(k, x, y):
    """point in level k's window (x,y in its own units, centred) -> world, all nested inside level 0"""
    ox = oy = 0.0
    rot = 0.0
    sc = 1.0
    for j in range(k):
        # child window centre in parent coords
        cy = 0.06 * WM * R ** j
        ox += -math.sin(rot) * cy
        oy += math.cos(rot) * cy
        rot += ROLL
    c, s = math.cos(rot), math.sin(rot)
    p = (ox + x * c - y * s, oy + x * s + y * c, 0.0)
    return ((p[0] - _REF[0]) / _REF[2], (p[1] - _REF[1]) / _REF[2], 0.0)


_REF = [0.0, 0.0, 1.0]
_zf_now = [0.0]


def _heat(k, zf):
    u = clamp((k - 0.0) / 6.0)
    col = lerp_c(INK, GOLD, clamp(u * 1.6)) if u < 0.62 else lerp_c(GOLD, (255, 250, 230), clamp((u - 0.62) / 0.38))
    return col


def lerp_c(a, b, u):
    return tuple(int(a[i] + (b[i] - a[i]) * u) for i in range(3))


def _window(g, cam, k, t, zf, al):
    w, h, _ = _lvl_geom(k)
    col = _heat(k, zf)
    hw, hh = w / 2, h / 2
    P = lambda x, y: _P(k, x, y)
    if k == KI:
        _map_opaque(g, cam, _ilya(), [P(-hw, -hh), P(hw, -hh), P(hw, hh), P(-hw, hh)])
        ba = al * (1 - prog(zf, KI - 0.35, KI - 0.05))
        if ba > 0:
            poly3(g, cam, [P(-hw, -hh), P(hw, -hh), P(hw, hh), P(-hw, hh), P(-hw, -hh)], (255, 245, 220), 3, ba)
        return
    text3 = lambda g_, c_, s_, p_, sz_, *a: _t3(g_, c_, s_, p_, sz_ / _REF[2], *a)
    # body + bezel
    fill3(g, cam, [P(-hw, -hh), P(hw, -hh), P(hw, hh), P(-hw, hh)], (14, 14, 13), al, col, max(1.0, 3.0 * al * min(1.0, R ** (k - _zf_now[0]))))
    # title bar
    tb = hh - h * 0.09
    fill3(g, cam, [P(-hw, -hh), P(hw, -hh), P(hw, -tb), P(-hw, -tb)], lerp_c((30, 30, 28), col, 0.35), al)
    for i, cc in enumerate([(235, 90, 80), (240, 190, 70), (110, 200, 110)]):
        point3(g, cam, P(-hw + w * (0.03 + 0.03 * i), -(hh + tb) / 2), max(0.6, 5.0 * R ** (k - _zf_now[0])), cc, al)
    ver = VERS[min(k, len(VERS) - 1)]
    text3(g, cam, 'SELF_UPGRADE.py  \u2014  ' + ver, P(0, -(hh + tb) / 2), h * 0.05, INK, 'mono', al)
    # code on the left margin (beside the child screen), types in as we arrive
    cw = w * R
    arrive = prog(zf, k - 1.0, k - 0.3)
    n = len(CODE)
    lx = -hw + w * 0.04
    for i, ln in enumerate(CODE):
        vis = clamp(arrive * n * 1.3 - i)
        if vis <= 0 or not ln:
            continue
        s = ln[:max(1, int(len(ln) * vis))]
        cc = GOLD if 'upgrade' in ln else (DIM if ln.startswith('#') else INK)
        text3(g, cam, s, P(lx, -tb + h * 0.07 + i * h * 0.07), h * 0.034, cc, 'mono', al, 'lm')
    # right margin: stats
    rx = hw - w * 0.04
    iq = 2 ** (2 ** min(k, 4)) if k < 5 else None
    stats = [('IQ', f'{100 * 2 ** k:,}' if k < 9 else '\u221e'), ('PARAMS', f'{2 ** k}T' if k < 9 else '\u221e'),
             ('SAFETY', 'n/a')]
    for i, (a_, b_) in enumerate(stats):
        text3(g, cam, a_, P(rx, -tb + h * 0.08 + i * h * 0.16), h * 0.035, DIM, 'mono', al, 'rm')
        text3(g, cam, b_, P(rx, -tb + h * 0.14 + i * h * 0.16), h * 0.06, col, 'monox', al, 'rm')
    # bottom: progress bar 'compiling successor'
    by = hh - h * 0.07
    pr = clamp(arrive * 1.2)
    seg3(g, cam, P(-hw + w * 0.04, by), P(hw - w * 0.04, by), (40, 40, 38), max(1.0, 12 * R ** (k - _zf_now[0])), al, wscale=False)
    if pr > 0:
        seg3(g, cam, P(-hw + w * 0.04, by), P(-hw + w * 0.04 + (w * 0.92) * pr, by), col, max(1.0, 12 * R ** (k - _zf_now[0])), al, wscale=False)
    text3(g, cam, 'compiling ' + VERS[min(k + 1, len(VERS) - 1)] + ' ...', P(-hw + w * 0.04, by - h * 0.045), h * 0.035, DIM, 'mono', al, 'lm')


def s_recursive(g, t, lt):
    t0 = T0(43); tE = T0(44)
    zf = _z(t)
    _zf_now[0] = zf
    blaze = 0.0
    bt = beats(t0 - 0.5, t + 0.001)
    pb = math.exp(-(t - (bt[-1] if bt else t0)) * 9)
    # camera: centred on the current window, distance shrinking geometrically, roll following the spiral
    k0 = int(math.floor(zf))
    fr = zf - k0
    _REF[:] = [0.0, 0.0, 1.0]
    ca = _P(k0, 0, 0); cb = _P(k0 + 1, 0, 0)
    c = v_lerp(ca, cb, (1 - R ** fr) / (1 - R))
    _REF[:] = [c[0], c[1], R ** zf]
    c = (0.0, 0.0, 0.0)
    w = WM
    fin = eio(prog(_u(t), 0.45, 1.0))
    dfill = (WM * ASP) * ((H / 2) / math.tan(math.radians(27))) / H
    d = lerp(1.12 * w, dfill, fin)
    sway = 0.05 * math.sin(math.pi * _u(t)) * (1 - fin)
    eye = (c[0] + d * math.sin(sway), c[1] - d * 0.05 * (1 - fin), -d * math.cos(sway))
    cam = Cam3(eye, c, 54, zf * ROLL)
    env(g, cam)
    for k in range(max(0, k0 - 1), min(KI, k0 + 5) + 1):
        al = clamp(1.6 - 0.25 * (k - zf)) if k >= zf - 1 else 0
        if al <= 0 or R ** (k - zf) < 0.01:
            continue
        _window(g, cam, k, t, zf, al)
    # HUD counter
    ver = VERS[min(k0, len(VERS) - 1)]
    ha = 1 - fin
    g.text('RECURSION DEPTH ' + str(k0), 90, H - 185, 26, DIM, 'mono', 0.9 * ha, 'lm')
    g.text(ver, 90, H - 125, 70, GOLD, 'monox', ha, 'lm')
    camc, cc, r, u = capcam()
    lyric3x(g, camc, t, 43, v_add(cc, v_mul(camc.u, -350)), r, u, 1400, 105, INK, {'recursive': GOLD, 'self-upgrade': GOLD}, depth=40)
    g.post = dict(glow=0.55 * (1 - fin))
