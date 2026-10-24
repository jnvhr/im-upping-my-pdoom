# v120 overhauls (she rejected the v119 versions of both scenes).
# FENCES: chase-cam wrecking run. The gold cube smashes through four different physical barriers, each one breaking
#   its own way: 01 RLHF laser fence (beams snap and whip back), 02 RED TEAM chain-link (panels torn off and flung),
#   03 EVALS concrete block wall (blocks explode outward and tumble), 04 KILL SWITCH steel blast door (door blown off).
# GPU: a real datacenter. 8 halls x 10 rows x 20 racks = 1,600 racks x 64 GPUs = 102,400 GPUs, every GPU an LED on
#   a rack front. Starts flying down a cold aisle between towering racks, then cranes up and out to the whole campus.
import math
import numpy as np
from cam3d import *
from s3a import T0, T1, WT
from ov116 import beats, capcam, glow

# =============================================================== SAFETY FENCES 117.14 - 119.05
HITS = [117.519, 117.973, 118.428, 118.883]   # v129: one barrier per beat (132 bpm grid), was on word onsets
FLAB = ['RLHF', 'RED TEAM', 'EVALS', 'KILL SWITCH']
FX = [900.0, 2100.0, 3300.0, 4500.0]
FHT = [380.0, 430.0, 480.0, 560.0]
ZS = 650.0
CUBE = 180.0
CY = -160.0


def _xc(t):
    ks = [(T0(37) - 0.06, -350.0)] + [(h, FX[i] - CUBE * 0.45) for i, h in enumerate(HITS)] + [(T0(38) + 0.06, 4800.0)]
    for a, b in zip(ks, ks[1:]):
        if t <= b[0]:
            u = prog(t, a[0], b[0])
            return lerp(a[1], b[1], u ** 1.55)   # accelerate into each barrier
    return ks[-1][1]


def _gravity(p0, v, e, g_=2600.0, floor_y=0.0, r=0.0):
    x = p0[0] + v[0] * e; z = p0[2] + v[2] * e
    y = p0[1] + v[1] * e + 0.5 * g_ * e * e
    return (x, min(y, floor_y - r), z)


def s_fences(g, t, lt):
    t0 = T0(37); tE = T0(38)
    xc = _xc(t)
    nb = sum(1 for h in HITS if t > h)
    hit = sum(math.exp(-(t - h) * 9) * (1.6 if i == 3 else 1.0) for i, h in enumerate(HITS) if t > h)
    bt = beats(t0 - 0.5, t + 0.001)
    lb = bt[-1] if bt else t0
    pb = math.exp(-(t - lb) * 8)
    # chase camera, low and behind-left; lifts and pulls back after the last barrier
    out = smooth(prog(t, 118.86, tE + 0.05))
    eye = (xc - 820 - 140 * min(1, hit) - 900 * out, -560 - 900 * out, -520 - 600 * out)
    tg = (xc + 700 + 300 * out, -250 + 60 * out, 120)
    cam = Cam3(shake_eye(eye, t, 6 + 40 * min(1.6, hit)), tg, 50 + 5 * min(1, hit), 0.035 * math.sin(t * 1.9) + 0.04 * min(1, hit) * math.sin(t * 40))
    env(g, cam)
    floor(g, cam, 0.0, 200, 40, GRID2, 0.7, xc + 1500, 0, fog=7000)
    S = SFaces()
    L = []        # (a, b, colour, width, alpha) lines drawn after the solids
    labels = []
    sparks = []
    for k in range(4):
        X = FX[k]; Hh = FHT[k]; e = t - HITS[k]; broke = e > 0
        if X < xc - 2600:
            continue
        if k == 0:
            # ---- laser fence: emitters + beams that snap at the impact point and whip back
            for s_ in (-1, 1):
                S.sbox((X, -Hh / 2, s_ * ZS), (46, Hh, 46), (60, 60, 56), GOLDD, 1.5)
                S.sbox((X, -Hh - 14, s_ * ZS), (70, 28, 70), GOLD, None, 1, amb=0.6)
            for j in range(7):
                y = -40 - j * (Hh - 70) / 6
                if not broke:
                    fl = 0.8 + 0.2 * math.sin(t * 50 + j)
                    L.append(((X, y, -ZS), (X, y, ZS), GOLDL, 4, fl))
                    L.append(((X, y, -ZS), (X, y, ZS), GOLD, 14, 0.18 * fl))
                elif e < 0.4:
                    r = 1 - eo(e / 0.3)
                    for s_ in (-1, 1):
                        tip = s_ * ZS * (1 - r) + s_ * 30 * r
                        wob = 60 * math.sin(e * 60 + j) * (1 - e / 0.4)
                        L.append(((X, y, s_ * ZS), (X + wob, y + wob * 0.5, tip), GOLDL, 4, 1 - e / 0.4))
        elif k == 1:
            # ---- chain-link: posts + mesh panels; centre panels are torn off and flung
            npn = 5; P = 2 * ZS / npn
            for pi in range(npn + 1):
                z = -ZS + pi * P
                lean = 0.0
                if broke and 0 < pi < npn:
                    lean = min(0.5, 2.0 * e) * (1.0 if abs(z) < 300 else 0.35)
                S.tube([(X, 0, z), (X + Hh * math.sin(lean), -Hh * math.cos(lean) - 30, z)], 12, (110, 110, 104), None, 5, amb=0.45)
            for pi in range(npn):
                z0 = -ZS + pi * P; zm = z0 + P / 2
                key = 37 + pi
                if broke and abs(zm) < 420:
                    v = (1300 + 500 * hsh(key, 1), -700 - 500 * hsh(key, 2), zm * 2.2)
                    c0 = _gravity((X, -Hh / 2, zm), v, e, r=40)
                    ang = e * (5 + 4 * hsh(key, 3))
                    def W_(u, h, c0=c0, ang=ang, key=key):
                        lp = rot3((0.0, -(h - Hh / 2), u - P / 2), ang, ang * 0.6 * (hsh(key, 4) - 0.5), ang * 0.3)
                        return v_add(c0, lp)
                    fa = 1 - clamp((e - 0.45) / 0.3)
                else:
                    lean = min(0.5, 2.0 * e) * 0.35 if broke else 0.0
                    def W_(u, h, z0=z0, lean=lean):
                        return (X + h * math.sin(lean), -h * math.cos(lean), z0 + u)
                    fa = 1.0
                if fa < 0.03:
                    continue
                L.append((W_(0, Hh), W_(P, Hh), INK, 3, fa))
                L.append((W_(0, 6), W_(P, 6), INK, 2, fa))
                sp = 58.0
                for q in range(1, int((P + Hh) / sp)):
                    d = q * sp
                    a0 = (min(d, P), max(0.0, d - P)); a1 = (max(0.0, d - Hh), min(d, Hh))
                    L.append((W_(a0[0], a0[1]), W_(a1[0], a1[1]), (170, 170, 162), 1.3, 0.8 * fa))
                    L.append((W_(P - a0[0], a0[1]), W_(P - a1[0], a1[1]), (170, 170, 162), 1.3, 0.8 * fa))
                cp = [W_(P * s / 10, Hh + 26 + 18 * math.sin(s * 2.3)) for s in range(11)]
                for a, b in zip(cp, cp[1:]):
                    L.append((a, b, INK, 1.6, fa))
        elif k == 2:
            # ---- concrete block wall: blocks near the impact explode outward and tumble
            bh = Hh / 4; bw = 2 * ZS / 11
            for r_ in range(4):
                for c_ in range(11):
                    off = (bw / 2) * (r_ % 2)
                    z = -ZS + bw / 2 + c_ * bw + off
                    if z > ZS:
                        continue
                    y = -bh / 2 - r_ * bh
                    key = 100 + r_ * 11 + c_
                    dd = math.hypot(z, y - CY)
                    col = (122, 120, 112) if (r_ + c_) % 3 else (104, 102, 96)
                    if broke and dd < 430:
                        sp = (1 - dd / 430)
                        v = (900 + 1600 * sp * (0.6 + 0.6 * hsh(key, 1)), -500 - 900 * hsh(key, 2), z * 2.6 * (0.5 + hsh(key, 3)))
                        c = _gravity((X, y, z), v, e, r=bh / 2)
                        ang = e * (6 + 6 * hsh(key, 4))
                        S.sbox(c, (60, bh - 6, bw - 6), col, (60, 60, 56), 1, xf=lambda p, c=c, ang=ang, key=key: v_add(rot3(v_sub(p, c), ang, ang * hsh(key, 5), ang * 0.4), c), amb=0.35)
                    else:
                        S.sbox((X, y, z), (60, bh - 6, bw - 6), col, (60, 60, 56), 1, amb=0.35)
        else:
            # ---- blast door: heavy frame, hazard-striped steel door with the kill switch; blown off its hinges
            S.sbox((X, -Hh / 2, -ZS + 120), (90, Hh, 240), (70, 70, 66), (40, 40, 38), 1.5)
            S.sbox((X, -Hh / 2, ZS - 120), (90, Hh, 240), (70, 70, 66), (40, 40, 38), 1.5)
            S.sbox((X, -Hh + 40, 0), (100, 80, 2 * ZS), (70, 70, 66), (40, 40, 38), 1.5)
            dc = (X, -(Hh - 80) / 2, 0.0)
            ang = 0.0
            if broke:
                dc = _gravity(dc, (2600, -900, 300), e, r=60)
                ang = e * 7
            xf = lambda p, dc=dc, ang=ang: v_add(rot3(v_sub(p, (0, 0, 0)), ang * 0.3, ang, ang * 0.15), dc)
            if not broke or e < 0.43:
                fa = 1 - clamp((e - 0.3) / 0.13) if broke else 1.0
                S.sbox((0, 0, 0), (60, Hh - 80, 2 * ZS - 480), (150, 150, 144), (60, 60, 56), 1.5, xf=xf, al=fa, amb=0.4)
                for q in range(-4, 5):
                    z = q * 85
                    S.sq([xf((-32, -(Hh - 80) / 2 + 4, z - 20)), xf((-32, -(Hh - 80) / 2 + 4, z + 20)), xf((-32, -(Hh - 80) / 2 + 40, z + 60)), xf((-32, -(Hh - 80) / 2 + 40, z + 20))], GOLD, None, 1, fa, amb=0.7)
                S.sphere((0, 0, 0), 46, (255, 120, 60) if int(t * 8) % 2 else GOLD, None, 6, 10, al=fa, xf=lambda p: xf(v_add(p, (-40, -40, 0))), amb=0.7)
        if not broke and k == nb:
            na = clamp((t - (HITS[k - 1] if k else T0(37) - 0.1)) / 0.1)
            labels.append(('FENCE %02d' % (k + 1), (X, -Hh - 190, 0), 46, DIM, 'mono', na))
            labels.append((FLAB[k], (X, -Hh - 110, 0), 104, GOLD if k == nb else INK, 'monox', na))
        elif broke and e < 0.22:
            labels.append((FLAB[k], (X + 300 * e, -Hh - 110 - 900 * e, 0), 104 * (1 + e), GOLDL, 'monox', 1 - e / 0.22))
        if broke and e < 0.6:
            for q in range(60):
                a = hsh(q, k + 20) * 6.283
                v = (500 + 1700 * hsh(q, k + 30), -900 * hsh(q, k + 40) - 200, math.cos(a) * 1300)
                p = _gravity((X, CY + 120 * math.sin(a), 0), v, e)
                sparks.append((p, GOLDL if q % 3 else INK, 1 - e / 0.6))
    # the gold cube, tumbling harder after every barrier
    sz = (CUBE + 26 * nb) * (1 + 0.05 * pb + 0.12 * min(1, hit))
    rot = t * (2.0 + 0.6 * nb)
    S.sbox((0, 0, 0), (sz, sz, sz), GOLD, GOLDL, 2, xf=lambda p: v_add(rot3(p, rot, rot * 0.7, 0.3), (xc, CY - 0.1 * sz, 0)), amb=0.45)
    S.draw(g, cam, fog=7000)
    for a, b, c, w, al in L:
        seg3(g, cam, a, b, c, w, al, fog=7000)
    glow(g, cam, (xc, CY, 0), sz * 1.1 + 260 * min(1, hit), GOLD, 0.2 + 0.3 * min(1, hit))
    for p, c, al in sparks:
        point3(g, cam, p, 5, c, al)
    for s, p, size, c, f, al in labels:
        text3(g, cam, s, p, size, c, f, al)
    g.flash = max(g.flash, 0.22 * max([math.exp(-(t - h) * 14) * (1.6 if i == 3 else 1) for i, h in enumerate(HITS) if t > h] or [0]))
    g.flash_c = GOLDL
    camc, c, r, u = capcam()
    lyric3x(g, camc, t, 37, v_add(c, v_mul(camc.u, 345)), r, u, 1500, 110, INK, {'safety': GOLD, 'fence': GOLD}, depth=40)


# =============================================================== HUNDRED THOUSAND GPU 119.05 - 120.82
RW, RD, RH = 56.0, 110.0, 230.0
RPX, RPZ = 64.0, 280.0
NCOL, NROW = 20, 10
HALLX, HALLZ = NCOL * RPX, NROW * RPZ
HGX, HGZ = 700.0, 700.0


def _racks():
    R = []
    for hz in range(2):
        for hx in range(4):
            ox = hx * (HALLX + HGX); oz = hz * (HALLZ + HGZ)
            for i in range(NROW):
                for j in range(NCOL):
                    R.append((ox + j * RPX + RW / 2 + 4, oz + i * RPZ + RD / 2 + 30, 1 if i % 2 == 0 else -1, hx + 4 * hz))
    return np.array(R)


RACK = _racks()
NR = len(RACK)                       # 1600 racks
NGPU = NR * 64                       # 102,400
RTW = np.array([hsh(i, 9) for i in range(NR)])
CX = (4 * HALLX + 3 * HGX) / 2; CZ = (2 * HALLZ + HGZ) / 2
AZ = 2 * RPZ + RD + 30 + (RPZ - RD) / 2        # cold aisle between row 2 and row 3 of hall 1


def _gkeys():
    t0 = T0(38); tE = T0(39)
    return [(t0 - 0.05, (-260, -125, AZ), (500, -105, AZ), 62, 0.0),
            (119.55, (620, -135, AZ), (1450, -100, AZ), 62, 0.03),
            (119.95, (240, -1500, AZ - 1700), (1150, -40, AZ + 900), 58, 0.0),
            (120.35, (-300, -2300, -1500), (CX + 500, 0, CZ + 900), 58, 0.0),
            (tE + 0.05, (100, -2200, -1700), (CX + 800, 0, CZ + 1000), 58, 0.0)]


def _s5(u):
    u = clamp(u)
    return u * u * u * (u * (u * 6 - 15) + 10)


def _gcam(t):
    # v121: one continuous move, no overshoot or whip. Dolly down the cold aisle accelerating, exit the end of
    # hall 1 while craning up and drifting left, panning right onto the campus; it never fully stops.
    t0 = T0(38)
    a = prog(t, t0 - 0.05, 120.6)
    xe = -260 + 1900 * (0.3 * a + 0.7 * _s5(a))
    b = _s5(prog(t, 119.46, 120.6))
    d = max(0.0, t - 120.35)
    bh = _s5(prog(t, 119.40, 120.5))
    bz = _s5(prog(t, 119.58, 120.62))
    eye = (xe + 140 * d, -lerp(125, 2900, bh) - 80 * d, lerp(AZ, -1900, bz) - 150 * d)
    tb = _s5(prog(t, 119.40, 120.55))
    ta = (xe + 900, -100, AZ)
    tf = (4700 + 260 * d, 0, 3900)
    tgt = v_lerp(ta, tf, tb)
    fov = lerp(62, 56, b)
    roll = -0.07 * math.sin(math.pi * b)
    return eye, tgt, fov, roll


def s_gpu(g, t, lt):
    t0 = T0(38); tg = WT(38, 2); tE = T0(39)
    bt = beats(t0 - 0.5, t + 0.001)
    lb = bt[-1] if bt else t0
    pb = math.exp(-(t - lb) * 8)
    eye, tgt, fov, roll = _gcam(t)
    fov *= 1 - 0.025 * pb
    cam = Cam3(eye, tgt, fov, roll + 0.02 * math.sin(t * 2.1))
    env(g, cam)
    E = np.array(eye); Rr = np.array(cam.r); Ru = np.array(cam.u); Rf = np.array(cam.f); F = cam.F
    # hall floors
    for h in range(8):
        hx, hz = h % 4, h // 4
        ox = hx * (HALLX + HGX); oz = hz * (HALLZ + HGZ)
        q = [(ox - 40, 0, oz), (ox + HALLX + 40, 0, oz), (ox + HALLX + 40, 0, oz + HALLZ + 20), (ox - 40, 0, oz + HALLZ + 20)]
        fill3(g, cam, q, (26, 26, 24), 1.0)
        poly3(g, cam, q + [q[0]], GOLDD, 2.5, 0.9, fog=0)
    # racks: painter's order, far to near
    C = RACK
    dvec = np.stack([C[:, 0] - E[0], -RH / 2 - E[1] + np.zeros(NR), C[:, 1] - E[2]], 1)
    zc = dvec @ Rf
    order = np.argsort(-zc)
    dist = np.hypot(C[:, 0] - CX * 0 - eye[0], C[:, 1] - eye[2])
    wave_r = (t - lb) * 9000
    wave = np.exp(-np.abs(np.hypot(C[:, 0] - 600, C[:, 1] - AZ) - wave_r) / 500) * pb
    hit0 = math.exp(-max(0.0, t - T0(38)) * 6)
    lum = 0.7 + 0.3 * np.sin(t * 7 + RTW * 30) + 0.6 * wave + 0.8 * hit0

    def P(p):
        d = np.asarray(p, float) - E
        z = d @ Rf
        return np.stack([cam.cx + (d @ Rr) * F / np.maximum(z, 1e-3), cam.cy + (d @ Ru) * F / np.maximum(z, 1e-3), z], -1)

    top_vis = eye[1] < -RH
    for idx in order:
        if zc[idx] < 30:
            continue
        x, z, fd, hall = C[idx]
        x0, x1, z0, z1 = x - RW / 2, x + RW / 2, z - RD / 2, z + RD / 2
        # cull off-screen
        pc = P((x, -RH / 2, z))
        if pc[0] < -300 or pc[0] > W + 300 or pc[1] < -400 or pc[1] > H + 400:
            continue
        faces = []
        if eye[2] < z0:
            faces.append(('z', z0, -1))
        elif eye[2] > z1:
            faces.append(('z', z1, 1))
        if eye[0] < x0:
            faces.append(('x', x0, -1))
        elif eye[0] > x1:
            faces.append(('x', x1, 1))
        if top_vis:
            faces.append(('t', None, 0))
        lu = float(lum[idx])
        for kind, c, sgn in faces:
            if kind == 'z':
                V = [(x0, 0, c), (x1, 0, c), (x1, -RH, c), (x0, -RH, c)]
            elif kind == 'x':
                V = [(c, 0, z0), (c, 0, z1), (c, -RH, z1), (c, -RH, z0)]
            else:
                V = [(x0, -RH, z0), (x1, -RH, z0), (x1, -RH, z1), (x0, -RH, z1)]
            pp = P(V)
            if pp[:, 2].min() < 8:
                continue
            flat = pp[:, :2].ravel().tolist()
            if kind == 't':
                g.poly(flat, fill=(28, 28, 26), stroke=(62, 62, 57), w=1, a=1.0, fa=1.0)
                continue
            if kind == 'x':
                g.poly(flat, fill=(20, 20, 19), stroke=(50, 50, 46), w=1, a=1.0, fa=1.0)
                continue
            front = (sgn == fd)
            pxh = RH * F / max(pp[:, 2].mean(), 1)
            k_ = (1.2 if front else 0.6) * lu
            if pxh < 16:
                g.poly(flat, fill=mix((18, 18, 17), GOLD, clamp(0.8 * k_)), stroke=None, w=1, a=1.0, fa=1.0)
                continue
            g.poly(flat, fill=(16, 16, 15), stroke=(58, 58, 54), w=1, a=1.0, fa=1.0)
            if pxh < 110 or not front:
                ys = -24 - np.arange(8) * 25.0
                A = P([(x0 + 5, y, c) for y in ys]); B = P([(x1 - 5, y, c) for y in ys])
                wv = max(1.0, pxh / 75)
                for a, b in zip(A, B):
                    g.line([a[0], a[1], b[0], b[1]], GOLDL if front else GOLD, wv, clamp(k_))
            else:
                # every GPU its own LED: 8 servers x 8 GPUs
                ys = -24 - np.arange(8) * 25.0
                xs = x0 + 6 + np.arange(8) * ((RW - 12) / 7)
                G_ = np.array([(xx, yy, c) for yy in ys for xx in xs])
                pg = P(G_)
                rr = max(1.2, 3.2 * F / max(pp[:, 2].mean(), 1))
                for qi, q in enumerate(pg):
                    on = 0.6 + 0.4 * math.sin(t * 13 + qi * 1.7 + idx)
                    g.rect(q[0] - rr, q[1] - rr * 0.6, q[0] + rr, q[1] + rr * 0.6, fill=GOLDL if on > 0.5 else GOLD, a=clamp(k_ * on + 0.2), fa=clamp(k_ * on + 0.2))
    # hall labels once we are high enough to see the campus
    la = clamp((-eye[1] - 1400) / 600)
    if la > 0.02:
        for h in range(8):
            hx, hz = h % 4, h // 4
            ox = hx * (HALLX + HGX); oz = hz * (HALLZ + HGZ)
            text3(g, cam, 'HALL %d' % (h + 1), (ox + HALLX / 2, -40, oz - 200), 170, GOLD, 'monox', la * 0.9)
    # counter: every GPU on the campus
    uw = prog(t, T0(38) + 0.05, 120.25)
    w = 1 - (1 - uw) ** 1.7
    n = int(math.exp(lerp(math.log(64), math.log(NGPU), w)))
    n = min(100000, max(64, (n // 64) * 64))
    if t > 120.3:
        n = 100000
    g.flash = max(g.flash, 0.28 * hit0); g.flash_c = GOLDL
    camc, c, r, uu = capcam()
    word3(g, camc, 'H100 \u00d7 %s' % format(n, ','), v_add(c, v_mul(camc.u, -150)), r, uu, 820 + 120 * pb * (t > tg), 200, GOLD, 'monox', 1, x=True, depth=60, n=6)
    nr = max(1, n // 64)
    sub = '%s RACK%s \u00b7 64 GPUs EACH' % (format(nr, ','), '' if nr == 1 else 'S')
    word3(g, camc, sub, v_add(c, v_mul(camc.u, -40)), r, uu, 520, 60, INK, 'mono', 0.8)
    lyric3x(g, camc, t, 38, v_add(c, v_mul(camc.u, -345)), r, uu, 1500, 115, INK, {'gpu': GOLD, 'thousand': GOLD}, depth=40)
