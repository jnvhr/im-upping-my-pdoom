# v116: FUSE overhaul 2: the fuse now runs across a circuit board. Traces branch off it and light up gold as the
# spark passes, chips at their ends wake up, and the bomb gets rivets and a strapped countdown timer wired to its neck.
# (v94 version: fuse94.py)
# v94: FUSE overhaul (102.48 - 105.92). Solid scene: a match drops onto a braided fuse lying on a dark floor
# ("we lit"), the spark races along it leaving a charred trail, embers + smoke; through the sung
# "fu-u-u-use" melisma the camera rises off the spark to reveal the iron bomb it is heading for, and the spark
# reaches the bomb's neck exactly as the note ends (FE). No flash: the bomb band warms with a soft glow.
import math
from cam3d import *
from s3a import T0, T1, WT
from s4b import CFaces

FE = 105.88
BOMB = (950.0, -400.0, 1500.0)
BR = 400.0
NECK = (BOMB[0], BOMB[1] - BR - 70, BOMB[2])
_CP = [(-2700, -16, -1900), (-2100, -16, -1500), (-1500, -16, -1700), (-900, -16, -1100), (-1100, -16, -400),
       (-500, -16, 100), (200, -16, -100), (600, -16, 500), (300, -16, 1000), (600, -16, 1400),
       (BOMB[0] - BR - 160, -16, BOMB[2]), (BOMB[0] - BR + 40, -220, BOMB[2]), (BOMB[0] - 200, NECK[1] - 120, BOMB[2]),
       (NECK[0], NECK[1] - 40, NECK[2])]


def _cr(p0, p1, p2, p3, s):
    return tuple(0.5 * (2 * b + (-a + c) * s + (2 * a - 5 * b + 4 * c - d) * s * s + (-a + 3 * b - 3 * c + d) * s ** 3)
                 for a, b, c, d in zip(p0, p1, p2, p3))


def _build():
    P = [_CP[0]] + _CP + [_CP[-1]]
    raw = []
    for i in range(1, len(P) - 2):
        for k in range(24):
            raw.append(_cr(P[i - 1], P[i], P[i + 1], P[i + 2], k / 24))
    raw.append(_CP[-1])
    L = [0.0]
    for a, b in zip(raw, raw[1:]):
        L.append(L[-1] + math.dist(a, b))
    tot = L[-1]
    out = []; j = 0
    for k in range(241):
        s = tot * k / 240
        while j < len(L) - 2 and L[j + 1] < s:
            j += 1
        f = (s - L[j]) / max(1e-6, L[j + 1] - L[j])
        out.append(v_lerp(raw[j], raw[j + 1], f))
    return out


FP = _build()


def fpos(u):
    x = clamp(u) * 240
    i = min(239, int(x))
    return v_lerp(FP[i], FP[i + 1], x - i)


def ftan(u, w=0.05):
    a, b = fpos(u - w), fpos(u + w)
    return v_norm(v_sub(b, a))


def _t_of_i():
    tl = WT(32, 4)
    ts = [tl + (FE - tl) * k / 600 for k in range(601)]
    us = [_u(x) for x in ts]
    out = []
    j = 0
    for i in range(241):
        target = i / 240
        while j < 600 and us[j] < target:
            j += 1
        out.append(ts[j])
    return out


def _traces():
    tr = []
    for n, i in enumerate(range(8, 226, 9)):
        p = FP[i]
        d = v_norm(v_sub(FP[min(240, i + 2)], FP[max(0, i - 2)]))
        d = v_norm((d[0], 0.0, d[2]))
        sd = 1 if n % 2 == 0 else -1
        nv = (-d[2] * sd, 0.0, d[0] * sd)
        L1 = 260 + 420 * hsh(n, 1); L2 = (200 + 500 * hsh(n, 2)) * (1 if hsh(n, 3) > 0.5 else -1)
        a = v_add(p, v_mul(nv, 50)); a = (a[0], -2, a[2])
        b = v_add(p, v_mul(nv, L1)); b = (b[0], -2, b[2])
        c = v_add(b, v_mul(d, L2))
        pts = [a, b, c]
        if hsh(n, 4) > 0.5:
            pts.append(v_add(c, v_mul(nv, 160 + 200 * hsh(n, 5))))
        tr.append((i, pts, n % 2 == 0))
    return tr


TR = _traces()
TI = None


def _u(t):
    tl = WT(32, 4)
    x = prog(t, tl, FE)
    # quick catch then a steady run; slight surge at the end so it lands on the note end
    return clamp(0.06 * smooth(clamp(x * 6)) + 0.94 * (x ** 1.15))


def _cam(t):
    tl = WT(32, 4)
    u = _u(t)
    sp = fpos(u)
    d = ftan(max(u, 0.04), 0.06)
    d = v_norm((d[0], 0.0, d[2]))
    side = v_norm(v_cross((0.0, 1.0, 0.0), d))
    trk_e = v_add(v_add(sp, v_mul(d, -620)), v_add(v_mul(side, 380), (0, -230, 0)))
    trk_t = v_add(sp, v_add(v_mul(d, 420), (0, -170, 0)))
    s0 = fpos(0.0)
    pre_e = v_add(s0, (-380, -300, -460)); pre_t = v_add(s0, (90, 60, 120))
    ka = smooth(prog(t, tl - 0.25, tl + 0.45))
    e = v_lerp(pre_e, trk_e, ka); tg = v_lerp(pre_t, trk_t, ka)
    # melisma: rise off the spark to frame spark + bomb
    w = smooth(prog(t, 104.25, 105.45))
    mid = v_lerp(sp, BOMB, 0.55)
    wide_e = v_add(mid, (-1500, -1250, -1350))
    wide_t = v_add(mid, (0, -420, 0))
    e = v_lerp(e, wide_e, w); tg = v_lerp(tg, wide_t, w)
    # slow drift at the end so nothing freezes
    e = v_add(e, (60 * math.sin(t * 0.9), 0, 40 * (t - 102.4)))
    return Cam3(shake_eye(e, t, 3), tg, 56 - 4 * w, 0.07 * math.sin(t * 1.3) * (1 - w) + 0.03 * w)


def glow(g, cam, p, r, c, al):
    _glow(g, cam, p, r, c, al)


def _glow(g, cam, p, r, c, al):
    q = cam.p(p)
    if q is None:
        return
    rr = r * q[2] / (cam.F / 1000.0)
    for k, a in ((1.0, 0.10), (0.6, 0.18), (0.32, 0.4), (0.14, 1.0)):
        g.circle(q[0], q[1], max(0.8, rr * k), fill=c if k > 0.2 else GOLDL, a=al * a)


s_TPOS = [None]


def s_fuse(g, t, lt):
    tl = WT(32, 4)
    cam = _cam(t)
    env(g, cam)
    lit = t >= tl
    u = _u(t) if lit else 0.0
    # floor
    global TI
    if TI is None:
        TI = _t_of_i()
    grid3(g, cam, (0, 0, 0), (1, 0, 0), (0, 0, 1), 52, 52, 100, (26, 26, 25), 0.9, 1.0, major=4, cmaj=(40, 40, 37), fog=5200)
    F = CFaces()
    # circuit board: traces branch off the fuse and light up gold as the spark passes, chips at the ends wake up
    lights = []
    for (i, pts, chip) in TR:
        e = t - TI[i] if lit else -1
        segs = list(zip(pts, pts[1:]))
        run = max(0.0, e) * 2600
        acc = 0.0
        for a, b in segs:
            L = math.dist(a, b)
            seg3(g, cam, a, b, (70, 70, 64), 4, 0.9, fog=7000)
            if run > acc:
                f = clamp((run - acc) / L)
                q = v_lerp(a, b, f)
                seg3(g, cam, a, q, GOLD, 9, 1.0, fog=7000)
                if f < 1:
                    lights.append(q)
            acc += L
        end = pts[-1]
        on = clamp((run - acc) / 300) if e > 0 else 0.0
        if chip:
            F.sbox((end[0], -22, end[2]), (230, 40, 230), mix((44, 44, 41), GOLD, on), None, amb=0.5)
            for q in range(4):
                for sgn in (-1, 1):
                    seg3(g, cam, (end[0] - 90 + q * 60, -2, end[2] + sgn * 115), (end[0] - 90 + q * 60, -2, end[2] + sgn * 165), mix((64, 64, 58), GOLD, on), 2, 0.9, fog=5200)
        else:
            point3(g, cam, end, 9, mix((64, 64, 58), GOLD, on), 1)
    # fuse: unburnt braided cord, charred behind the spark, glowing just behind it
    N = 240
    k0 = int(u * N)
    seg = 3
    for i in range(0, N, seg):
        pts = FP[i:i + seg + 1]
        if len(pts) < 2:
            continue
        um = (i + seg / 2) / N
        if um < u:
            dd = (u - um) * 14
            col = mix((235, 120, 30), (34, 30, 27), clamp(dd)) if dd < 1 else (34, 30, 27)
            r = 11
        else:
            col = mix((196, 178, 140), (150, 132, 100), 0.5 + 0.5 * math.sin(i * 1.7))
            r = 15
        F.tube(pts, r, col, None, n=6, amb=0.35)
    # bomb: iron sphere, gold band, neck
    F.sphere(BOMB, BR, (58, 56, 54), None, nlat=12, nlon=22, amb=0.28)
    warm = smooth(prog(t, FE - 0.35, FE + 0.04))
    F.cyl(v_add(BOMB, (0, -BR * 0.18, 0)), BR * 1.004, 70, mix(GOLDD, GOLDL, warm), None, n=22, caps=False, amb=0.4)
    F.cyl((NECK[0], NECK[1] + 30, NECK[2]), 120, 110, (90, 86, 80), None, n=14, amb=0.3)
    F.cyl((NECK[0], NECK[1] - 30, NECK[2]), 70, 30, GOLDD, None, n=12, amb=0.4)
    for q in range(18):
        a = 2 * math.pi * q / 18
        F.sphere(v_add(BOMB, (BR * 1.02 * math.cos(a), -BR * 0.18, BR * 1.02 * math.sin(a))), 16, (150, 120, 50), None, nlat=3, nlon=6, amb=0.5)
    # strapped countdown timer facing the camera side, wired to the neck
    tdir = v_norm((-1.0, 0.0, -0.9))
    TPOS = v_add(BOMB, v_add(v_mul(tdir, BR + 40), (0, -60, 0)))
    yaw = math.atan2(tdir[0], tdir[2])
    F.sbox((0, 0, 0), (300, 150, 70), (36, 36, 34), None, xf=lambda v: v_add(rot3(v, 0, yaw, 0), TPOS), amb=0.4)
    F.sbox((0, 0, 0), (240, 90, 8), (18, 14, 10), None, xf=lambda v: v_add(rot3(v_add(v, (0, 0, 36)), 0, yaw, 0), TPOS), amb=0.6)
    for k_, col in ((0, (170, 40, 30)), (1, GOLDD)):
        w0 = v_add(TPOS, (0, -70, 0))
        F.tube([w0, v_add(v_lerp(w0, NECK, 0.5), (60 * (k_ - 0.5), -160, 0)), v_add(NECK, (30 * (k_ - 0.5), 30, 0))], 8, col, None, n=5, amb=0.5)
    s_TPOS[0] = (TPOS, tdir)
    # match: drops in, strikes the fuse end at 'lit', then lies spent on the floor
    s0 = fpos(0.0)
    md = prog(t, 102.6, tl)
    mp = v_add(s0, (-30 - 260 * (1 - eo(md)), -60 - 420 * (1 - eo(md)), -200 * (1 - eo(md))))
    if t > tl:
        fall = eo(prog(t, tl, tl + 0.5))
        mp = v_add(mp, (-160 * fall, 40 * fall, -120 * fall))
    tip = v_add(mp, (40, -10, 30))
    tail = v_add(mp, (-170, -110, -130))
    F.tube([tail, tip], 7, (210, 170, 110), None, n=5, amb=0.4)
    F.sphere(tip, 13, (150, 40, 30), None, nlat=4, nlon=8)
    F.draw(g, cam, fog=6000)
    # match flame (dies 0.6s after lighting)
    mf = smooth(prog(t, 102.75, 102.95)) * (1 - prog(t, tl + 0.2, tl + 0.8))
    if mf > 0:
        fl = 0.85 + 0.15 * math.sin(t * 47)
        _glow(g, cam, v_add(tip, (8, -26, 6)), 70 * fl, GOLD, mf)
    # floor light pool + spark + embers + smoke
    if lit and t < FE + 0.05:
        sp = v_add(fpos(u), (0, -18, 0))
        fr = int(t * 30)
        q = cam.p(v_add(sp, (0, 16, 0)))
        _glow(g, cam, v_add(sp, (0, 14, 0)), 520, (90, 60, 14), 0.5)
        for i in range(46):
            a = hsh(i, fr) * 6.283; life = hsh(i, fr + 3)
            v = (math.cos(a) * 240 * life, -(80 + 340 * hsh(i, fr + 1)) * life + 300 * life * life, math.sin(a) * 240 * life)
            point3(g, cam, v_add(sp, v), 3.5 * (1 - life) + 1.2, GOLDL if i % 3 else GOLD, 0.95 * (1 - life * 0.6))
        for i in range(14):
            ag = (i * 0.071 + t * 0.6) % 1.0
            uu = clamp(u - ag * 0.05)
            pp = v_add(fpos(uu), (40 * math.sin(i * 3 + t), -40 - ag * 520, 40 * math.cos(i * 2.3 + t)))
            point3(g, cam, pp, 10 + ag * 26, (90, 88, 84), 0.22 * (1 - ag))
        fl = 0.8 + 0.2 * math.sin(t * 61) * math.sin(t * 23)
        _glow(g, cam, sp, 120 * fl, GOLD, 1.0)
    # T-minus on the floor beside the bomb (small, mono)
    TPOS, tdir = s_TPOS[0]
    rem = max(0.0, FE - t)
    blink = 1.0 if rem > 0 else (0.35 + 0.65 * (int(t * 8) % 2))
    text3(g, cam, '%05.2f' % rem, v_add(TPOS, v_mul(tdir, 50)), 58, GOLD if rem > 0.6 else GOLDL, 'monox', blink)
    text3(g, cam, 'P(DOOM)', v_add(TPOS, (0, 110, 0)), 22, DIM, 'mono', 0.9)
    for q in lights:
        glow(g, cam, q, 110, GOLD, 1.0)
    # end: the band and neck warm with a soft glow, no flash
    if warm > 0:
        _glow(g, cam, NECK, 260 * warm, GOLD, 0.8 * warm)
    # caption screen-locked in the top band (fixed caption camera), the spark/bomb framed below it
    camc = Cam3((0.0, 0.0, -1000.0), (0.0, 0.0, 0.0), 55)
    c, r, uu = ahead(camc, 1000)
    lyric3x(g, camc, t, 32, v_add(c, v_mul(camc.u, -330)), r, uu, 1500, 115, INK, {'lit': GOLD, 'fuse': GOLD},
            depth=20, hold=1.25)
