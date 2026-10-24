# v116 overhauls: Von Neumann, safety fences, hundred thousand GPU, Loom + masked pre-training (one continuous
# shot with real camera moves), recursive self-upgrade (re-framed, captions moved clear of the hands).
import math
from cam3d import *
from s3a import T0, T1, WT

PH = 0.2462121212121225
BT = 60.0 / 132


def beats(a, b):
    n = math.ceil((a - PH) / BT)
    out = []
    while PH + n * BT < b:
        out.append(PH + n * BT); n += 1
    return out


def capcam():
    camc = Cam3((0.0, 0.0, -1000.0), (0.0, 0.0, 0.0), 55)
    c, r, u = ahead(camc, 1000)
    return camc, c, r, u


def glow(g, cam, p, r, c, al):
    q = cam.p(p)
    if q is None:
        return
    rr = r * q[2] / (cam.F / 1000.0)
    for k, a in ((1.0, 0.10), (0.6, 0.18), (0.32, 0.4), (0.14, 1.0)):
        g.circle(q[0], q[1], max(0.8, rr * k), fill=c if k > 0.2 else GOLDL, a=al * a)


# ======================================================== VON NEUMANN 77.72 - 81.23 (paper)
VN_R = 1000.0
VN_C = (0.0, 0.0, 450.0)
VN_UNITS = [('INPUT', -1.15), ('CONTROL UNIT', -0.58), ('MEMORY', 0.0), ('ALU', 0.58), ('OUTPUT', 1.15)]
CAB = (420.0, 1050.0, 260.0)    # width, height, depth


def _cab_xf(k, theta):
    a = VN_UNITS[k][1]
    px, pz = VN_C[0] + VN_R * math.sin(a), VN_C[2] + VN_R * math.cos(a)
    ca, sa = math.cos(a), math.sin(a)
    ct, st = math.cos(theta), math.sin(theta)
    d2 = CAB[2] / 2

    def T(p):
        x, y, z = p
        z -= d2
        y, z = y * ct + z * st, -y * st + z * ct
        z += d2
        return (px + x * ca + z * sa, y, pz - x * sa + z * ca)
    return T


def s_vn(g, t, lt):
    t0 = T0(24); to = WT(24, 3); tE = T0(25)
    keys = [(t0, (-1700, -800, -1500), (0, -520, 450), 48, 0.04),
            (78.9, (-500, -520, -1300), (0, -540, 450), 50, 0.01),
            (to, (420, -640, -1250), (0, -560, 450), 53, -0.02),
            (80.55, (900, -1100, -1500), (0, -640, 450), 56, -0.04),
            (tE, (250, -2300, -1500), (0, -420, 600), 58, 0.0)]
    hit = math.exp(-max(0, t - to) * 6) * (t > to)
    cam = cam_at(t, keys, shake=34 * hit)
    # museum floor + plinth
    F = SFaces()
    F.sbox((0, 40, 450), (2900, 80, 2500), (236, 234, 228), (150, 148, 140), 1.2, amb=0.55)
    # velvet-rope stanchions in front
    for i in range(-3, 4):
        F.cyl((i * 420, -150, -820), 16, 380, (180, 150, 70), None, n=8, amb=0.5)
        F.cyl((i * 420, -10, -820), 70, 20, (90, 88, 82), None, n=10, amb=0.5)
    F.draw(g, cam)
    for i in range(-3, 3):
        a, b = (i * 420, -320, -820), ((i + 1) * 420, -320, -820)
        pts = [v_add(v_lerp(a, b, q / 8), (0, 60 * math.sin(math.pi * q / 8), 0)) for q in range(9)]
        poly3(g, cam, pts, (150, 40, 40), 5, 1)
    # cabinets: tubes glow on the beats, then pop out in a wave on 'obsolete' and the cabinets fall back
    G = SFaces()
    glows = []
    for k, (nm, a) in enumerate(VN_UNITS):
        tk = to + 0.42 + 0.09 * abs(k - 2)
        th = 0.0
        if t > tk:
            e = t - tk
            th = math.pi / 2 * min(1.0, (e / 0.42) ** 2)
            if e > 0.42:
                th = math.pi / 2 - 0.08 * math.exp(-(e - 0.42) * 7) * abs(math.sin((e - 0.42) * 22))
        T = _cab_xf(k, th)
        W_, H_, D_ = CAB
        G.sbox((0, 0, 0), CAB, (226, 224, 218), BLACK, 1.4, xf=lambda v, T=T: T(v_add(v, (0, -H_ / 2, 0))), amb=0.5)
        G.sbox((0, 0, 0), (W_ * 0.86, 60, 6), (60, 58, 54), None, xf=lambda v, T=T: T(v_add(v, (0, -H_ + 90, -D_ / 2 - 4))), amb=0.6)
        for r in range(6):
            for c in range(4):
                lp = (-W_ * 0.33 + c * W_ * 0.22, -170 - r * 120, -D_ / 2 - 12)
                idx = k * 100 + r * 10 + c
                G.sbox((0, 0, 0), (34, 70, 24), (150, 146, 136), None, xf=lambda v, T=T, lp=lp: T(v_add(v, lp)), amb=0.5)
                pop = to + 0.02 * (r + c) + 0.05 * abs(k - 2) + 0.06 * hsh(idx, 3)
                on = t < pop
                fl = 0.55 + 0.45 * math.exp(-((t - PH) / BT % 1) * 5) * (hsh(idx, int((t - PH) / BT)) > 0.3)
                glows.append((T(v_add(lp, (0, -44, -6))), on, pop, fl, idx))
    G.draw(g, cam)
    for p, on, pop, fl, idx in glows:
        if on:
            point3(g, cam, p, 12, GOLD, 0.95 * fl)
        else:
            e = t - pop
            if e < 0.25:
                point3(g, cam, p, 9 + 60 * e, GOLDL, 1 - e / 0.25)
                for s_ in range(3):
                    d = v_norm((hsh(idx, s_) - 0.5, -hsh(idx, s_ + 4), -0.6))
                    point3(g, cam, v_add(p, v_add(v_mul(d, 500 * e), (0, 900 * e * e, 0))), 4, (120, 118, 110), 1 - e / 0.25)
    # labels while standing
    for k, (nm, a) in enumerate(VN_UNITS):
        tk = to + 0.42 + 0.09 * abs(k - 2)
        if t < tk:
            T = _cab_xf(k, 0.0)
            text3(g, cam, nm, T((0, -CAB[1] + 90, -CAB[2] / 2 - 30)), 30, GOLD, 'monox')
    # the bus between control and memory: pulses on every beat (the bottleneck), snaps on 'obsolete'
    bus = [_cab_xf(k, 0.0)((0, -110, -CAB[2] / 2 - 30)) for k in range(5)]
    if t < to:
        poly3(g, cam, bus, GOLD, 5, 1)
        for b in beats(t0 - 0.5, to + 0.1):
            e = t - b
            if 0 <= e < 0.45:
                u = e / 0.45 * 4
                i = min(3, int(u))
                point3(g, cam, v_lerp(bus[i], bus[i + 1], u - i), 16, GOLDL, 1)
    else:
        e = t - to
        for i in range(4):
            a, b = bus[i], bus[i + 1]
            m = v_lerp(a, b, 0.5)
            for (p, q) in ((a, m), (m, b)):
                dv = v_mul((0, 1, -0.3), 700 * e * e + 120 * e)
                seg3(g, cam, v_add(p, dv), v_add(q, dv), GOLD, 5, max(0.0, 1 - e * 1.6))
    # the replacement: one tiny glowing chip rises in the middle of the plinth; gold traces race out from it
    ch = eo(prog(t, to - 0.1, to + 0.45))
    if ch > 0:
        cy = -10 - 260 * ch
        H2 = SFaces()
        H2.sbox((0, (cy + 0) / 2, 450), (130, max(4, -cy), 130), (200, 198, 190), BLACK, 1.2, amb=0.55)
        H2.sbox((0, 0, 0), (110, 16, 110), GOLD, GOLDD, 1.2, xf=lambda v: v_add(rot3(v, 0, t * 1.4, 0), (0, cy - 8, 450)), amb=0.6)
        H2.draw(g, cam)
        glow(g, cam, (0, cy - 20, 450), 260 * ch * (0.9 + 0.1 * math.sin(t * 30)), GOLD, 0.8)
        for i in range(16):
            ang = 2 * math.pi * i / 16 + 0.2
            L = 1300 * eo(prog(t, to, to + 0.8 + 0.2 * hsh(i, 2)))
            p0 = (0, -2, 450)
            p1 = (L * 0.55 * math.cos(ang), -2, 450 + L * 0.55 * math.sin(ang))
            p2 = (L * math.cos(ang + 0.25 * (hsh(i, 5) - 0.5)), -2, 450 + L * math.sin(ang + 0.25 * (hsh(i, 5) - 0.5)))
            poly3(g, cam, [p0, p1, p2], GOLD, 3, 0.9)
            point3(g, cam, p2, 7, GOLD, 1)
    text3(g, cam, 'EXHIBIT 1945  \u2014  VON NEUMANN ARCHITECTURE', (0, -6, -640), 28, (90, 88, 80), 'mono')
    camc, c, r, u = capcam()
    lyric3(g, camc, t, 24, v_add(c, v_mul(camc.u, -340)), r, u, 1700, 115, INK, hl={"neumann's": GOLD, 'obsolete': GOLD}, light=True)
    g.hud = dict(light=True)
    g.post = dict(glow=0.18, grain=0.02, vig=0.4)


# ======================================================== SAFETY FENCES 117.13 - 119.04
FZ6 = [700.0, 1800.0, 2900.0, 4000.0]
HITS = [117.38, 117.75, 118.18, 118.62]
FLAB = ['RLHF', 'RED TEAM', 'EVALS', 'KILL SWITCH']


def _cube_z(t):
    t0 = T0(37)
    ks = [(t0, -900.0)] + [(h, z - 230) for h, z in zip(HITS, FZ6)] + [(119.1, 5400.0)]
    for (a, za), (b, zb) in zip(ks, ks[1:]):
        if t <= b:
            u = prog(t, a, b)
            return lerp(za, zb, u ** 1.35)
    return ks[-1][1]


def s_fences(g, t, lt):
    t0 = T0(37); tE = T0(38)
    cz = _cube_z(t)
    CYc = -260.0
    hit = sum(math.exp(-(t - h) * 9) for h in HITS if t > h)
    bob = 18 * math.sin(t * 9)
    eye = (380 * math.sin(t * 1.6) - 260, -520 + 40 * math.sin(t * 2.3), cz - 1500 + 200 * prog(t, 118.62, tE))
    cam = Cam3(shake_eye(eye, t, 10 + 60 * hit), (0, CYc + 40, cz + 900), 60, 0.06 * math.sin(t * 2.1) + 0.04 * hit)
    env(g, cam)
    floor(g, cam, 0.0, 200, 30, GRID2, 0.7, 0, cz + 1500, fog=4500)
    for k, fz in enumerate(FZ6):
        e = t - HITS[k]
        broke = e > 0
        F = SFaces()
        tilt = 0.5 * eo(clamp(e / 0.3)) if broke else 0.0
        for sx in (-1, 1):
            base = (sx * 820, 0, fz)
            top = v_add(base, (sx * 120 * tilt, -1150 * math.cos(tilt * 0.6), 420 * tilt))
            F.tube([base, top], 26, (120, 120, 114), None, 6, amb=0.4)
            for s_ in range(5):
                q0 = v_lerp(base, top, 0.1 + s_ * 0.18); q1 = v_lerp(base, top, 0.19 + s_ * 0.18)
                F.tube([q0, q1], 29, GOLD if s_ % 2 == 0 else (30, 30, 28), None, 6, amb=0.5)
        if not broke:
            F.sbox((0, -1100, fz), (1640, 26, 26), (120, 120, 114), None)
            F.sbox((0, -40, fz), (1640, 26, 26), (120, 120, 114), None)
            F.sbox((0, -760, fz - 14), (780, 230, 12), GOLD, None, amb=0.6)
        F.draw(g, cam, fog=6000)
        # chain-link: diamond cells; the two halves swing open like torn gates, links scatter
        sp = 110.0
        for i in range(-7, 8):
            for j in range(0, 10):
                x0, y0 = i * sp, -80 - j * sp
                if abs(x0) > 780:
                    continue
                pa, pb = (x0, y0, fz), (x0 + sp, y0 - sp, fz)
                pc, pd = (x0 + sp, y0, fz), (x0, y0 - sp, fz)
                al = 0.85
                if broke:
                    side = -1 if x0 + sp / 2 < 0 else 1
                    ang = side * 1.9 * eo(clamp(e / 0.35)) * (0.7 + 0.3 * hsh(i, j))
                    pivx = side * 820
                    def R(p, ang=ang, pivx=pivx, i=i, j=j):
                        x, y, z = p[0] - pivx, p[1], p[2] - fz
                        x, z = x * math.cos(ang) - z * math.sin(ang), x * math.sin(ang) + z * math.cos(ang)
                        fly = 0.0 if hsh(i * 3, j) > 0.12 else 0.5
                        return (x + pivx + fly * (hsh(i, j + 7) - 0.5) * 1800 * e, y + fly * 900 * e * e, z + fz + fly * 1600 * e)
                    pa, pb, pc, pd = R(pa), R(pb), R(pc), R(pd)
                    al = 0.85 * (1 - clamp(e / 0.5))
                if al > 0.02:
                    seg3(g, cam, pa, pb, (150, 150, 144), 1.6, al, fog=6000)
                    seg3(g, cam, pc, pd, (150, 150, 144), 1.6, al, fog=6000)
        # barbed wire along the top
        if not broke:
            pts = [(-820 + q * 41, -1150 - 30 * (q % 2), fz) for q in range(41)]
            poly3(g, cam, pts, (150, 150, 144), 2, 0.9, fog=6000)
            text3(g, cam, 'SAFETY FENCE %02d' % (k + 1), (0, -800, fz - 26), 44, BG, 'monox')
            text3(g, cam, FLAB[k], (0, -718, fz - 26), 40, BG, 'monox')
        else:
            # the sign tumbles away, sparks spray from the impact point
            sg = (240 * (hsh(k, 1) - 0.5) * e * 4, -760 - 900 * e + 2200 * e * e, fz + 1900 * e)
            S = SFaces()
            S.sbox((0, 0, 0), (780, 230, 12), GOLD, None, xf=lambda v: v_add(rot3(v, e * 7, e * 3, e * 5), sg), amb=0.6)
            S.draw(g, cam, fog=6000)
            if e < 0.6:
                for q in range(50):
                    d = v_norm((hsh(q, k) - 0.5, -hsh(q, k + 1) * 0.8, hsh(q, k + 2) * 0.8 + 0.2))
                    p = v_add((0, CYc, fz), v_add(v_mul(d, 2400 * e * (0.4 + hsh(q, 9))), (0, 1400 * e * e, 0)))
                    point3(g, cam, p, 5, GOLDL if q % 3 else INK, 1 - e / 0.6)
    # the gold cube (from 'super-dense') ramming through
    C = SFaces()
    sq_ = 1.0 + 0.12 * hit
    C.sbox((0, 0, 0), (340 * sq_, 340 / sq_, 340 * sq_), GOLD, GOLDL, 2, xf=lambda v: v_add(rot3(v, t * 2.4, t * 1.7, 0.2), (0, CYc + bob, cz)), amb=0.45)
    C.draw(g, cam)
    glow(g, cam, (0, CYc + bob, cz), 420 + 500 * min(1.0, hit), GOLD, 0.35 + 0.4 * min(1.0, hit))
    for q in range(26):   # streaks behind the cube
        p = ((hsh(q, 1) - 0.5) * 300, CYc + (hsh(q, 2) - 0.5) * 300, cz - 200 - hsh(q, 3) * 900)
        seg3(g, cam, p, v_add(p, (0, 0, -260)), GOLDL, 2, 0.35)
    g.flash = max(g.flash, 0.35 * max([math.exp(-(t - h) * 14) for h in HITS if t > h] or [0]))
    g.flash_c = GOLDL
    camc, c, r, u = capcam()
    lyric3x(g, camc, t, 37, v_add(c, v_mul(camc.u, 345)), r, u, 1500, 110, INK, {'safety': GOLD, 'fence': GOLD}, depth=40)


# ======================================================== HUNDRED THOUSAND GPU 119.04 - 120.81
COLX = 760.0
RK = (360.0, 1000.0, 230.0)   # depth (x), height, width (z)


def s_gpu(g, t, lt):
    t0 = T0(38); tg = WT(38, 2); tE = T0(39)
    AX = COLX / 2
    keys = [(t0, (AX, -330, -900), (AX, -380, 2200), 64, 0.0),
            (tg, (AX - 40, -420, 900), (AX, -420, 3600), 62, 0.03),
            (120.25, (AX - 300, -2300, 1900), (AX, -200, 4700), 58, 0.05),
            (tE, (-1300, -5200, 1000), (0, 0, 5200), 56, 0.02)]
    cam = cam_at(t, keys, shake=8 + 30 * math.exp(-max(0, t - tg) * 6) * (t > tg))
    env(g, cam)
    ex, ey, ez = cam.eye
    floor(g, cam, 0.0, 300, 40, GRID2, 0.8, AX, ez + 3000, fog=7000)
    F = SFaces()
    near = []
    inside = ey > -1000
    for c in range(-8, 10):
        x = c * COLX
        for j in range(0, 48):
            z = j * (RK[2] + 8)
            d = math.hypot(x - ex, z - ez)
            if d > 9000 or (z < ez - 400 and abs(x - ex) < 2500):
                continue
            F.sbox((x, -RK[1] / 2, z), RK, (28, 28, 27), (78, 78, 72), 1.0, amb=0.45)
            if d < 3600:
                near.append((x, z, c, j))
    F.draw(g, cam, fog=8000)
    bl = beats(t0 - 0.5, t + 0.01)
    lb = bl[-1] if bl else t0
    for (x, z, c, j) in near:
        wave = math.exp(-abs((t - lb) * 7000 - (z - ez)) / 260)
        if inside and c in (0, 1):
            # blades + status LEDs on the two walls of our aisle; an LED wave runs down the hall on every beat
            fx = x + RK[0] / 2 + 2 if c == 0 else x - RK[0] / 2 - 2
            for r in range(9):
                y = -110 - r * 100
                seg3(g, cam, (fx, y, z - RK[2] / 2 + 12), (fx, y, z + RK[2] / 2 - 12), (110, 110, 104), 1.6, 0.9, fog=6000)
                on = hsh(c * 97 + j * 13 + r, int(t * 14)) < 0.5
                if on or wave > 0.2:
                    point3(g, cam, (fx, y - 40, z - 80 + 40 * (r % 3)), 7, GOLDL if wave > 0.4 else (GOLD if r % 3 else INK), 0.95)
        elif not inside:
            on = hsh(c * 97 + j * 13, int(t * 10)) < 0.4
            if on or wave > 0.2:
                point3(g, cam, (x, -RK[1] - 4, z), 8, GOLDL if wave > 0.4 else GOLD, 0.9)
    if not inside:
        # from above: a gold power rail along every row's roof, a pulse racing down each one on the beat
        for c in range(-8, 10):
            x = c * COLX
            seg3(g, cam, (x, -RK[1] - 3, 0), (x, -RK[1] - 3, 48 * (RK[2] + 8)), GOLDD, 4, 0.9, fog=9000)
            pz = (t - lb) * 7000 + ez
            if 0 < pz < 11000:
                glow(g, cam, (x, -RK[1] - 6, pz), 220, GOLD, 0.8)
    # overhead cable trays in gold over each aisle
    for c in range(-8, 10):
        xa = c * COLX + COLX / 2
        seg3(g, cam, (xa - 60, -1150, max(0, ez - 300)), (xa - 60, -1150, 11000), GOLDD, 3, 0.9, fog=8000)
        seg3(g, cam, (xa + 60, -1150, max(0, ez - 300)), (xa + 60, -1150, 11000), GOLDD, 3, 0.9, fog=8000)
    # heat haze dots rising off the roofs once we're above
    up = prog(t, tg, tE)
    if up > 0.2:
        for i in range(90):
            p = ((hsh(i, 1) - 0.4) * 9000, -1050 - ((t * 400 + hsh(i, 2) * 900) % 900), 1500 + hsh(i, 3) * 8000)
            point3(g, cam, p, 4, GOLD, 0.5 * up)
    n = int(100000 * eo(prog(t, t0, T1(38))))
    camc, c, r, u = capcam()
    word3(g, camc, 'H100 \u00d7 %s' % format(n, ','), v_add(c, v_mul(camc.u, -150)), r, u, 820 + 260 * eo(up), 200, GOLD, 'monox', 1, x=True, depth=60, n=6)
    lyric3x(g, camc, t, 38, v_add(c, v_mul(camc.u, -345)), r, u, 1500, 115, INK, {'gpu': GOLD, 'thousand': GOLD}, depth=40)


# ======================================================== LOOM + MASKED PRE-TRAINING 126.39 - 129.86
def _tree():
    nodes = [((0.0, 0.0, 0.0), -1, 0, True)]
    out = []
    def grow(i, d, ang, depth, gold):
        if depth >= 6:
            return
        p = nodes[i][0]
        nb = 3 if depth < 2 else 2
        for b in range(nb):
            yaw = ang + (b - (nb - 1) / 2) * (1.9 / (depth + 1)) + (hsh(i, b) - 0.5) * 0.5
            L = 640 * (0.78 ** depth)
            spread = 0.55 + 0.1 * depth
            dd = (math.cos(yaw) * spread, -1.0, math.sin(yaw) * spread)
            dd = v_norm(dd)
            q = v_add(p, v_mul(dd, L))
            g2 = gold and b == 0
            nodes.append((q, i, depth + 1, g2))
            grow(len(nodes) - 1, dd, yaw + 0.9 * (b - 1), depth + 1, g2)
    grow(0, (0, -1, 0), 0.3, 0, True)
    return nodes


TREE = _tree()
LTOK = ['the', 'it', 'and', 'we', 'was', 'a', 'doom', 'loom', 'end', 'of', 'all', 'show', 'see', 'so']
MASKW = ['the', 'cat', 'sat', 'on', 'the', 'mat', 'and', 'then', 'it', 'was', 'all', 'over', 'we', 'lit', 'a', 'fuse']


def s_prophecy(g, t, lt):
    t0 = T0(41) - 0.03; tm = T0(42); tr = T0(43) - 0.03
    tl = WT(41, 4)
    # one continuous move: orbit and crane up around the growing tree, then dive down the gold thread into the
    # token field it grows from, skim low over it, and swing up as the masks fill
    def oe(yaw, rad, y, ty):
        return (rad * math.sin(yaw), y, -rad * math.cos(yaw)), (0, ty, 0)
    k = []
    for tt, yaw, rad, y, ty, fov in ((t0, -1.0, 1850, -450, -800, 56), (126.95, -0.45, 1700, -900, -1050, 56),
                                    (127.5, 0.2, 1550, -1450, -1350, 58), (127.85, 0.55, 1450, -900, -700, 60)):
        e, tg = oe(yaw, rad, y, ty)
        k.append((tt, e, tg, fov, 0.04 * yaw))
    k += [(128.25, (500, -420, -650), (0, -60, 600), 60, -0.06),
          (128.9, (-250, -230, 400), (0, 40, 1800), 62, 0.05),
          (129.4, (-700, -520, 1200), (0, 0, 2400), 60, 0.0),
          (tr, (-300, -1300, 1300), (0, 0, 2700), 58, -0.03)]
    cam = cam_at(t, k, shake=6)
    env(g, cam)
    # ---- token field (pre-training data); the tree is rooted in it
    fill_t = [128.18, 128.54, 128.8, 129.18, 129.4, 129.6]
    F = SFaces()
    tiles = []
    for i in range(-9, 10):
        for j in range(-6, 22):
            x, z = i * 190, j * 190
            if math.hypot(x - cam.eye[0], z - cam.eye[2]) > 5200:
                continue
            m = hsh(i + 30, j + 30) < 0.22
            n = int(hsh(i + 50, j) * len(fill_t)) if m else -1
            ft = fill_t[n] + 0.05 * hsh(i, j) if m else 0.0
            filled = m and t > ft
            e = t - ft if m else 0.0
            lift = -80 * math.sin(min(1.0, e / 0.3) * math.pi) if filled and e < 0.3 else 0.0
            col = GOLD if filled else ((40, 38, 30) if m else (52, 52, 49))
            F.sbox((x, 20 + lift, z), (160, 24, 160), col, GOLD if m else None, 1.6, amb=0.45)
            tiles.append((x, z, m, filled, e, i, j, lift))
    F.draw(g, cam, fog=5200)
    for (x, z, m, filled, e, i, j, lift) in tiles:
        if math.hypot(x - cam.eye[0], z - cam.eye[2]) > 2600:
            continue
        w = MASKW[(i * 3 + j * 7) % len(MASKW)]
        if m and not filled:
            text3(g, cam, '[MASK]', (x, -4, z), 22, GOLD, 'mono')
        elif filled:
            text3(g, cam, w, (x, -4 + lift, z), 26, BG, 'monox')
            if e < 0.4:
                seg3(g, cam, (x, 0, z), (x, -900 * (1 - e / 0.4) - 100, z), GOLDL, 3, 1 - e / 0.4)
        else:
            text3(g, cam, w, (x, -4, z), 20, (150, 150, 144), 'mono')
    # ---- the Loom: a multiverse of continuations, the chosen thread in gold
    grow = prog(t, t0 - 0.1, tl + 0.1) * 6.4
    fade = 1 - 0.85 * prog(t, 128.2, 128.8)
    for idx, (p, par, d, gold) in enumerate(TREE):
        if par < 0:
            continue
        u = clamp(grow - (d - 1))
        if u <= 0:
            continue
        a = TREE[par][0]
        b = v_lerp(a, p, u)
        mid = v_add(v_lerp(a, b, 0.5), (40 * math.sin(idx), 0, 40 * math.cos(idx)))
        pts = [v_lerp(v_lerp(a, mid, s / 6), v_lerp(mid, b, s / 6), s / 6) for s in range(7)]
        lit = gold and t > tl - 0.35
        poly3(g, cam, pts, GOLD if lit else ((170, 170, 164) if gold else (120, 120, 114)), (6 if lit else 3.0) * (1.4 - d * 0.12), fade, fog=6000)
        if u >= 1:
            point3(g, cam, p, 9 if lit else 5, GOLDL if lit else (130, 130, 124), fade)
            if d <= 3:
                text3(g, cam, LTOK[idx % len(LTOK)], v_add(p, (0, -40, 0)), 26 if d < 3 else 20, GOLD if lit else (130, 130, 124), 'mono', fade)
    # loom frame: warp threads on a ring around the tree
    for i in range(36):
        a = 2 * math.pi * i / 36
        seg3(g, cam, (1500 * math.cos(a), 0, 1500 * math.sin(a)), (1500 * math.cos(a), -2300, 1500 * math.sin(a)), GRID2, 1.4, 0.6 * fade, fog=6000)
    poly3(g, cam, [(1500 * math.cos(2 * math.pi * q / 72), -2300, 1500 * math.sin(2 * math.pi * q / 72)) for q in range(73)], GRID2, 2, 0.6 * fade, fog=6000)
    # the thread pulse: a spark runs down the gold path into the field on 'Loom'
    gp = [n[0] for n in TREE if n[3]]
    gp.sort(key=lambda p: p[1])
    if tl < t < tm + 0.2:
        u = prog(t, tl, tm + 0.2)
        L = len(gp) - 1
        x = u * L; i = min(L - 1, int(x))
        sp = v_lerp(gp[i], gp[i + 1], x - i)
        glow(g, cam, sp, 160, GOLD, 1.0)
    camc, c, r, u = capcam()
    lyric3x(g, camc, t, 41, v_add(c, v_mul(camc.u, -345)), r, u, 1500, 115, INK, {'foretold': GOLD, 'loom': GOLD}, depth=40, hold=0.05)
    lyric3x(g, camc, t, 42, v_add(c, v_mul(camc.u, -345)), r, u, 1500, 115, INK, {'masked': GOLD, 'pre-training': GOLD}, depth=40)
    g.post = dict(glow=0.65)


# ======================================================== RECURSIVE SELF-UPGRADE 129.86 - 132.01
def s_recursive(g, t, lt):
    import s4c as S
    t0 = T0(43); tE = T0(44)
    z = (t - t0) * 1.45
    k0 = int(z)
    fr = z - k0
    O = [(0.0, 0.0, 0.0)]
    for k in range(1, k0 + 7):
        s = S.SC ** (k - 1)
        m = 1 if (k - 1) % 2 == 0 else -1
        prev = O[-1]
        O.append((prev[0] + S.OFF[0] * s * m, prev[1] + S.OFF[1] * s, prev[2] + S.OFF[2] * s))
    sz = S.SC ** z
    tgt = v_lerp(O[k0], O[k0 + 1], fr)
    # framed higher and further back so the hands sit in the middle of the frame, clear of the caption band
    eye = v_add(tgt, v_mul((-760, -140, -2000), sz))
    cam = Cam3(eye, v_add(tgt, v_mul((90, -400, 0), sz)), 54, 0.12 * math.sin(t * 1.3))
    env(g, cam)
    F = SFaces()
    for k in range(max(0, k0 - 1), k0 + 5):
        s = S.SC ** k
        build = clamp((z - k + 1.4) / 0.9)
        S._hand(F, O[k], s, build, 1 if k % 2 == 0 else -1)
    F.draw(g, cam)
    for k in range(max(0, k0 - 1), k0 + 5):
        s = S.SC ** k
        build = clamp((z - k + 1.4) / 0.9)
        if build > 0.6:
            text3(g, cam, 'v%d.0' % (k + 1), v_add(O[k], v_mul((-60, 300, -60), s)), 46 * s, GOLD, 'monox')
        if 0 < build < 1:
            # welding beams from the parent's fingertips to the new hand, sparks around it
            if k > 0:
                ps = S.SC ** (k - 1)
                tip = v_add(O[k - 1], v_mul((S.OFF[0] * (1 if (k - 1) % 2 == 0 else -1), S.OFF[1], S.OFF[2]), ps))
                for i in range(3):
                    q = v_add(O[k], v_mul(((hsh(i, int(t * 24)) - 0.5) * 260, (hsh(i + 5, int(t * 24)) - 0.5) * 260, -40), s))
                    seg3(g, cam, tip, q, GOLDL, 2.5, 0.8)
            for i in range(18):
                p = v_add(O[k], v_mul(((hsh(i, int(t * 30)) - 0.5) * 340, (hsh(i, int(t * 30) + 1) - 0.5) * 340, -80), s))
                point3(g, cam, p, 5 * s, GOLDL, 0.9)
            # scan ring sweeping over the part being assembled
            yv = (build * 2 - 1) * 260
            ring = [v_add(O[k], v_mul((300 * math.cos(a), yv, 300 * math.sin(a) * 0.4), s)) for a in [2 * math.pi * q / 40 for q in range(41)]]
            poly3(g, cam, ring, GOLD, 3, 0.8)
    for b in beats(t0, tE):
        e = t - b
        if 0 <= e < 0.3:
            g.flash = max(g.flash, 0.12 * (1 - e / 0.3)); g.flash_c = GOLDL
    lv = k0 + 1
    camc, c, r, u = capcam()
    # the newest hand is framed in the centre; the lyric sits in the top band and the version readout small at
    # the bottom, so neither covers the hands
    g.text('SELF_UPGRADE  v%d.0 \u2192 v%d.0' % (lv, lv + 1), 90, H - 150, 30, GOLD, "mono", 0.95, "lm")
    lyric3x(g, camc, t, 43, v_add(c, v_mul(camc.u, -350)), r, u, 1400, 105, INK, {'recursive': GOLD, 'self-upgrade': GOLD}, depth=40)
