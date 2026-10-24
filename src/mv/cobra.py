"""v56: a sculpted 3D cobra (black king-cobra look with cream bands, glossy shading, gold rim light).
build_cobra(pose) -> (faces list, info).  The scene is in s4b.s_basilisk."""
import math
from cam3d import *

KEY = v_norm((-0.55, -0.75, -0.45))      # towards the key light (upper left, in front)
GROUND = 430.0
C0 = (0.0, GROUND, 650.0)                # coil centre


def _lit(cam, base, n, p, gloss=0.55, rim=0.85, amb=0.16):
    v = v_norm(v_sub(cam.eye, p))
    if v_dot(n, v) < 0:
        n = v_mul(n, -1)
    lam = max(0.0, v_dot(n, KEY))
    h = v_norm(v_add(KEY, v))
    sp = max(0.0, v_dot(n, h)) ** 36 * gloss
    fr = (1 - max(0.0, v_dot(n, v))) ** 3 * rim
    k = amb + 0.9 * lam
    return tuple(int(clamp(base[i] * k + 255 * sp * 0.92 + GOLDL[i] * fr * 0.55, 0, 255)) for i in range(3))


def _bez(p0, p1, p2, p3, u):
    a = (1 - u) ** 3; b = 3 * (1 - u) ** 2 * u; c = 3 * (1 - u) * u * u; d = u ** 3
    return tuple(a * p0[i] + b * p1[i] + c * p2[i] + d * p3[i] for i in range(3))


def _resample(P, n):
    L = [0.0]
    for i in range(1, len(P)):
        L.append(L[-1] + math.sqrt(v_dot(v_sub(P[i], P[i - 1]), v_sub(P[i], P[i - 1]))))
    out = []; j = 0
    for k in range(n):
        s = L[-1] * k / (n - 1)
        while j < len(L) - 2 and L[j + 1] < s:
            j += 1
        u = (s - L[j]) / max(1e-6, L[j + 1] - L[j])
        out.append(v_lerp(P[j], P[j + 1], clamp(u)))
    return out, L[-1]


def spine(pose):
    """pose: rise, sway(x), lean(z), strike(0..1), yaw.  returns resampled spine + head frame"""
    rise, sx, lean, st = pose['rise'], pose['sway'], pose['lean'], pose['strike']
    P = []
    ph = pose.get('slide', 0.0)
    # tail + loose stacked coil, ending at the front of the pile heading inward
    nC = 120
    for k in range(nC):
        q = k / (nC - 1)
        a = -math.pi / 2 - 2 * math.pi * 1.65 * (1 - q) + ph * (1 - q) ** 2
        R = 260 + 290 * (1 - q) ** 0.8
        y = GROUND - 70 - 95 * q * (1 - 0.5 * q) - 40 * math.sin(q * math.pi * 3.3) * (1 - q)
        P.append((C0[0] + R * math.cos(a), y, C0[2] + R * math.sin(a)))
    B = P[-1]
    T0 = v_norm(v_sub(P[-1], P[-3]))
    # neck: rises vertically, head top H
    Hy = lerp(GROUND - 260, -470, rise) + 280 * st
    H = (sx, Hy, C0[2] - 330 + lean - 520 * st)
    p1 = v_add(B, v_mul(T0, 260))
    p2 = (sx * 0.55, Hy + 360, H[2] + 60 + 120 * st)
    for k in range(1, 60):
        P.append(_bez(B, p1, p2, H, k / 59))
    # 90 degree bend from "up" into the forward-facing head
    yaw = pose.get('yaw', 0.0)
    fwd = v_norm((math.sin(yaw), 0.18 * st - pose.get('pitch', 0.0), -math.cos(yaw)))
    up = (0, -1, 0)
    rb = 70.0
    ctr = v_add(H, v_mul(fwd, rb))
    for k in range(1, 9):
        a = (math.pi / 2) * k / 8
        P.append(v_add(ctr, v_add(v_mul(fwd, -rb * math.cos(a)), v_mul(up, rb * math.sin(a)))))
    S, Ltot = _resample(P, 360)
    return S, Ltot, fwd


def frames(S):
    """parallel-transport frames; dorsal starts pointing up"""
    T = []
    m = len(S)
    for i in range(m):
        T.append(v_norm(v_sub(S[min(m - 1, i + 1)], S[max(0, i - 1)])))
    D = [None] * m
    d = (0.0, -1.0, 0.0)
    for i in range(m):
        d = v_sub(d, v_mul(T[i], v_dot(d, T[i])))
        d = v_norm(d)
        D[i] = d
    Lt = [v_norm(v_cross(T[i], D[i])) for i in range(m)]
    return T, D, Lt


def neck_frames(S, T, D, Lt, fwd, i0, i1):
    """from i1 on, the belly faces fwd (the camera side) so the hood spreads sideways; blend i0..i1"""
    m = len(S)
    for i in range(i0, m):
        Lg = v_cross(T[i], fwd)
        if v_dot(Lg, Lg) < 1e-6:
            continue
        Lg = v_norm(Lg)
        Dg = v_norm(v_cross(Lg, T[i]))
        if v_dot(Dg, fwd) > 0:
            Dg = v_mul(Dg, -1); Lg = v_mul(Lg, -1)
        w = clamp((i - i0) / max(1, i1 - i0)); w = w * w * (3 - 2 * w)
        d = v_norm(v_add(v_mul(D[i], 1 - w), v_mul(Dg, w)))
        if v_dot(d, d) < 1e-6:
            d = Dg
        d = v_norm(v_sub(d, v_mul(T[i], v_dot(d, T[i]))))
        D[i] = d; Lt[i] = v_norm(v_cross(T[i], d))
    return D, Lt


BLACK = (30, 29, 26)
BLACK2 = (36, 34, 30)
CREAM = (226, 200, 140)
CREAM2 = (212, 188, 130)
BANDC = (214, 184, 118)
GOLDDK = (150, 112, 30)


def _mouth(add, cam, GU, GL, NX, NA, jaw):
    """Inside of the open mouth: dark throat, shaded palate with folds and two rows of small teeth,
    gummy lip margins, a trough-shaped floor, the glottis and a rounded forked tongue, fang sheaths."""
    def _edges(G1, G2, x):
        i = min(int(x), NX - 1); fr = x - i
        a = v_lerp(G1[i][NA], G1[i + 1][NA], fr); b = v_lerp(G1[i][0], G1[i + 1][0], fr)
        a2 = v_lerp(G2[i][NA], G2[i + 1][NA], fr); b2 = v_lerp(G2[i][0], G2[i + 1][0], fr)
        return a, b, v_norm(v_sub(v_lerp(a2, b2, 0.5), v_lerp(a, b, 0.5)))

    def pal(x, w, lift=0.0):
        a, b, dn = _edges(GU, GL, x)
        return v_add(v_lerp(a, b, (w + 1) / 2), v_mul(dn, lift - 12 * (1 - w * w)))   # vaulted roof (pushed up)

    def flo(x, w, lift=0.0):
        a, b, up = _edges(GL, GU, x)
        return v_add(v_lerp(a, b, (w + 1) / 2), v_mul(up, lift - 14 * (1 - w * w)))   # trough

    def shade(q, c, gl=0.35):
        nv = v_cross(v_sub(q[1], q[0]), v_sub(q[3 if len(q) > 3 else 2], q[0]))
        if v_dot(nv, nv) < 1e-9:
            add(q, c); return
        nv = v_norm(nv)
        pc = q[0]
        if v_dot(nv, v_sub(cam.eye, pc)) < 0:
            nv = v_mul(nv, -1)
        add(q, _lit(cam, c, nv, pc, gloss=gl, amb=0.3))
    DEEP = (16, 6, 6)
    GUM = (150, 92, 84); ROOF = (98, 50, 48); FLOOR = (86, 38, 38)
    # throat opening at the back
    ring = [pal(0.6, -0.8 + 1.6 * k / 8) for k in range(9)] + [flo(0.6, 0.8 - 1.6 * k / 8) for k in range(9)]
    add(ring, DEEP)
    NW = 8
    for fn, base_c in ((pal, ROOF), (flo, FLOOR)):
        for x in range(NX):
            dep = clamp(1 - (x - 0.5) / (NX * 0.45)) ** 1.2      # darker toward the throat
            for j in range(NW):
                wa = -1 + 2 * j / NW; wb = wa + 2 / NW
                q = [fn(x, wa), fn(x, wb), fn(x + 1, wb), fn(x + 1, wa)]
                c = base_c
                if j in (0, NW - 1):
                    c = GUM                                   # pale gum along the lips
                elif fn is pal:
                    if x % 2 == 0:
                        c = mix(c, (84, 40, 38), 0.4)         # transverse palate folds
                    if j in (3, 4):
                        c = mix(c, (60, 26, 26), 0.4)         # central groove
                else:
                    if j in (3, 4):
                        c = mix(c, (60, 24, 24), 0.35)        # tongue groove
                shade(q, mix(c, DEEP, dep * 0.85))
    # two rows of small backward-curved teeth on each side of the roof
    for w in (-0.66, -0.36, 0.36, 0.66):
        x = 2.5
        while x < NX * 0.86:
            p0 = pal(x, w, 1); p1 = pal(x + 0.32, w, 1); tip = pal(x - 0.12, w, 12)
            add([p0, p1, tip], (234, 226, 204))
            x += 0.85
    # rounded forked tongue lying in the trough, emerging from its sheath behind the glottis
    TONG = (124, 18, 26); TH = (184, 56, 60); TIP = (14, 6, 6)
    xs = [NX * (0.1 + 0.06 * k) for k in range(11)]            # 0.1 .. 0.7
    prof = [(-1, 14), (-0.5, 22), (0, 25), (0.5, 22), (1, 14)]
    for a_, b_ in zip(xs, xs[1:]):
        wa = 0.3 * (1 - 0.5 * a_ / NX); wb = 0.3 * (1 - 0.5 * b_ / NX)
        dep = clamp(1 - a_ / (NX * 0.35))
        for (u0, l0), (u1, l1) in zip(prof, prof[1:]):
            q = [flo(a_, wa * u0, l0), flo(a_, wa * u1, l1), flo(b_, wb * u1, l1), flo(b_, wb * u0, l0)]
            c = TH if (u0 == -0.5 or u0 == 0) and abs(u0 + u1) < 1.1 else TONG
            if u0 in (-0.5, 0):
                c = mix(TONG, TH, 0.55 if u0 == 0 else 0.35)
            shade(q, mix(c, DEEP, dep * 0.7), gl=0.7)
        q = [flo(a_, -0.015, 26), flo(a_, 0.015, 26), flo(b_, 0.015, 26), flo(b_, -0.015, 26)]
        add(q, mix((60, 12, 16), DEEP, dep * 0.6))           # mid-line crease
    for sx in (-1, 1):                                         # the fork: two thin black-tipped prongs
        pts = [(0.7, 0.0), (0.77, 0.06), (0.84, 0.12), (0.9, 0.18), (0.95, 0.23)]
        for (xa, wa), (xb, wb) in zip(pts, pts[1:]):
            th = 0.06 * (1 - (xa - 0.7) / 0.4)
            q = [flo(NX * xa, sx * wa - th, 22), flo(NX * xa, sx * wa + th, 22), flo(NX * xb, sx * wb + th * 0.7, 20), flo(NX * xb, sx * wb - th * 0.7, 20)]
            add(q, mix(TONG, TIP, clamp((xb - 0.7) / 0.2)))
    # glottis: a small breathing tube on the floor in front of the tongue sheath
    gx = NX * 0.06 + 0.4
    rimp = [flo(gx + 0.5 * math.sin(2 * math.pi * k / 12), 0.09 * math.cos(2 * math.pi * k / 12), 22) for k in range(12)]
    shade(rimp, (170, 100, 92))
    hole = [flo(gx + 0.28 * math.sin(2 * math.pi * k / 10), 0.04 * math.cos(2 * math.pi * k / 10), 24) for k in range(10)]
    add(hole, (24, 8, 8))
    # fleshy sheaths around the fang roots
    for w in (-0.55, 0.55):
        ringf = [pal(NX * 0.8 + 0.45 * math.sin(2 * math.pi * k / 10), w + 0.08 * math.cos(2 * math.pi * k / 10), 3) for k in range(10)]
        shade(ringf, (190, 120, 110))


def build(cam, pose):
    S, Ltot, fwd = spine(pose)
    T, D, Lt = frames(S)
    m = len(S)
    D, Lt = neck_frames(S, T, D, Lt, fwd, int(0.6 * m), int(0.72 * m))
    flare = pose['hood']
    F = []

    def add(q, col):
        F.append((q, col, col, 1.0, 1.0))

    # radius profile
    def rad(i):
        s = i / (m - 1)
        if s < 0.22:
            r = 8 + 56 * math.sin(s / 0.22 * math.pi / 2)
        elif s < 0.62:
            r = 64
        else:
            r = 64 - 16 * (s - 0.62) / 0.38
        return r
    n = 32
    seg = Ltot / (m - 1)
    i_top = m - 1 - int(55 / seg)
    hood_len = 600.0
    i_bot = max(0, int(i_top - hood_len / seg))

    def hbump(i):
        if i < i_bot or i > i_top + 6:
            return 0.0
        v = (i_top - i) / max(1, i_top - i_bot)
        return clamp(min((v + 0.1) / 0.25, (1 - v) / 0.1))
    rings = []; norms = []
    for i in range(m):
        r = rad(i)
        ring = []; nr = []
        for k in range(n):
            th = 2 * math.pi * k / n
            # loaf section: flatter belly
            c, s_ = math.cos(th), math.sin(th)
            hb = flare * hbump(i)
            rr = r * (1 - 0.18 * max(0.0, -c) ** 2) * (1 - 0.8 * hb)
            nv = v_norm(v_add(v_mul(D[i], c), v_mul(Lt[i], s_)))
            ring.append(v_add(S[i], v_add(v_mul(D[i], rr * c), v_mul(Lt[i], r * (1.04 - 0.8 * hb) * s_))))
            nr.append(nv)
        rings.append(ring); norms.append(nr)
    def bcol(si, th):
        c = math.cos(th)
        if c < -0.45:
            return CREAM2 if (si % 2.0) < 0.4 else CREAM
        ph = (si - 8 * abs(math.sin(th))) % 17
        if ph < 2.2 and si > 0.08 * m:
            return BANDC
        return BLACK

    def avg(cs):
        return tuple(sum(c[j] for c in cs) / len(cs) for j in range(3))
    for i in range(m - 1):
        if flare * min(hbump(i), hbump(i + 1)) > 0.45:
            continue          # inside the hood: the hood sheet carries the neck's front
        for k in range(n):
            th0 = 2 * math.pi * k / n; dth = 2 * math.pi / n
            col = avg([bcol(i + di, th0 + dj * dth) for di in (0.25, 0.75) for dj in (0.25, 0.75)])
            ventral = math.cos(th0 + dth / 2) < -0.45
            # scale texture: staggered rows of overlapping scales, each lit at its front and shadowed at its trailing edge
            if ventral:
                kf = 0.8 if i % 3 == 0 else (1.03 if i % 3 == 1 else 0.98)
            else:
                row = i // 2
                cell = (k + row % 2) // 2
                kf = (1.07 if i % 2 == 0 else 0.84) * (0.96 if (k + row % 2) % 2 else 1.0)
                kf *= 0.95 + 0.1 * hsh(row * 53 + cell, 11)
                if hsh(row * 71 + cell, 13) < 0.025 and col[0] < 100:
                    col = mix(col, BANDC, 0.55)          # pale flecks
            col = tuple(clamp(x * kf, 0, 255) for x in col)
            q = [rings[i][k], rings[i][(k + 1) % n], rings[i + 1][(k + 1) % n], rings[i + 1][k]]
            nv = v_norm(v_add(norms[i][k], norms[i + 1][(k + 1) % n]))
            pc = v_mul(v_add(q[0], q[2]), 0.5)
            add(q, _lit(cam, col, nv, pc, gloss=0.6 if not ventral else 0.25))

    # ---------------- hood: a cupped sheet spreading sideways from the neck
    def IP(arr, fi):
        j = min(max(int(math.floor(fi)), 0), m - 2)
        return v_lerp(arr[j], arr[j + 1], fi - j)
    Wmax = 235.0
    thick = 14.0

    def hw_of(v):
        i = i_top - v * (i_top - i_bot)
        if v < 0.3:
            shape = 0.6 + 0.4 * math.sin(v / 0.3 * math.pi / 2)
        else:
            shape = 0.12 + 0.88 * math.cos((v - 0.3) / 0.7 * math.pi / 2) ** 1.25
        w = rad(i) + (Wmax * shape - rad(i)) * flare
        return i, max(w, rad(i) * 1.1)

    def hp(u, v, back=0.0, lift=0.0):
        i, w = hw_of(v)
        cup = 0.38 * w * u * u * flare
        xr = u * w / rad(i)
        bulge = rad(i) * 0.85 * math.exp(-xr * xr * 0.9)
        off = rad(i) * 0.3 * hbump(i) - cup - bulge + back - lift
        shoulder = 120 * clamp((0.3 - v) / 0.3) ** 1.5 * math.sqrt(max(0.0, 1 - u * u)) * flare   # hood rises beside the head
        return v_add(v_add(IP(S, i), v_mul(IP(T, i), shoulder)), v_add(v_mul(IP(Lt, i), u * w), v_mul(IP(D, i), off)))

    if flare > 0.02:
        NV = (i_top - i_bot) * 3; NU = 44
        G = [[hp(-1 + 2 * b_ / NU, a_ / NV) for b_ in range(NU + 1)] for a_ in range(NV + 1)]
        for a_ in range(NV):
            v = (a_ + 0.5) / NV
            i, w = hw_of(v)
            Di = IP(D, i)
            for b_ in range(NU):
                u = -1 + 2 * (b_ + 0.5) / NU
                q = [G[a_][b_], G[a_][b_ + 1], G[a_ + 1][b_ + 1], G[a_ + 1][b_]]
                nv = v_norm(v_cross(v_sub(q[1], q[0]), v_sub(q[3], q[0])))
                if v_dot(nv, Di) > 0:
                    nv = v_mul(nv, -1)
                pc = v_mul(v_add(q[0], q[2]), 0.5)
                xr = abs(u) * w / rad(i)
                if abs(u) > 0.9:
                    fc = BLACK
                elif xr < 1.35:
                    fc = (226, 206, 140)          # broad ventral plates down the middle
                else:
                    tt = clamp((abs(u) - 0.3) / 0.55) ** 1.1
                    fc = mix(CREAM, (46, 40, 30), tt)
                add(q, _lit(cam, fc, nv, pc, gloss=0.3, amb=0.34))
                bq = [v_add(x, v_mul(Di, thick)) for x in q]
                add(bq, _lit(cam, BLACK if (a_ // 3 + b_) % 2 else BLACK2, v_mul(nv, -1), pc, gloss=0.5))
        for a_ in range(NV):
            v = a_ / NV; i, _ = hw_of(v)
            for b_ in (0, NU):
                p0, p1 = G[a_][b_], G[a_ + 1][b_]
                Di = IP(D, i)
                add([p0, p1, v_add(p1, v_mul(Di, thick)), v_add(p0, v_mul(Di, thick))], (190, 150, 50))
        # throat bars (front) as thin strips just above the surface, smooth chevrons
        NB = 40
        for (v0, v1, uw) in ((0.265, 0.315, 0.74), (0.355, 0.38, 0.7)):
            for k in range(NB):
                ua = -uw + 2 * uw * k / NB; ub = ua + 2 * uw / NB
                va0 = v0 + 0.06 * ua * ua; vb0 = v0 + 0.06 * ub * ub
                va1 = v1 + 0.06 * ua * ua; vb1 = v1 + 0.06 * ub * ub
                q = [hp(ua, va0, lift=9), hp(ub, vb0, lift=9), hp(ub, vb1, lift=9), hp(ua, va1, lift=9)]
                nv = v_norm(v_cross(v_sub(q[1], q[0]), v_sub(q[3], q[0])))
                add(q, _lit(cam, (40, 36, 30), nv, q[0], gloss=0.3))
        # ventral scute lines down the middle of the hood
        for k in range(2, 22):
            v = k / 22.0
            i, w = hw_of(v)
            uw = min(0.8, 1.7 * rad(i) / w)
            for j in range(8):
                ua = -uw + 2 * uw * j / 8; ub = ua + 2 * uw / 8
                q = [hp(ua, v, lift=6), hp(ub, v, lift=6), hp(ub, v + 0.007, lift=6), hp(ua, v + 0.007, lift=6)]
                nv = v_norm(v_cross(v_sub(q[1], q[0]), v_sub(q[3], q[0])))
                add(q, _lit(cam, (140, 120, 76), nv, q[0], gloss=0.2, amb=0.34))
        # pale spots on the dark hood margins and dark flecks near the plates (smooth ovals)
        for k in range(80):
            uu_ = (0.52 + 0.36 * hsh(k, 21)) * (1 if k % 2 else -1)
            vv_ = 0.06 + 0.8 * hsh(k, 22)
            dark = False
            rs = 0.011 + 0.011 * hsh(k, 23)
            ring = [hp(uu_ + rs * math.cos(2 * math.pi * j / 8), vv_ + rs * 1.4 * math.sin(2 * math.pi * j / 8), lift=4) for j in range(8)]
            nv = v_norm(v_cross(v_sub(ring[2], ring[0]), v_sub(ring[6], ring[0])))
            add(ring, _lit(cam, (70, 60, 42) if dark else (206, 182, 118), nv, ring[0], gloss=0.3, amb=0.34))
        # spectacle mark on the back of the hood (two rings joined by a bridge)
        NS = 28
        for sx in (-1, 1):
            for k in range(NS):
                a0 = 2 * math.pi * k / NS; a1 = 2 * math.pi * (k + 1) / NS
                def P(a, rr):
                    return hp(sx * 0.42 + rr * 0.2 * math.cos(a), 0.36 + rr * 0.11 * math.sin(a), back=thick + 4)
                q = [P(a0, 0.62), P(a1, 0.62), P(a1, 1.0), P(a0, 1.0)]
                nv = v_norm(v_cross(v_sub(q[1], q[0]), v_sub(q[3], q[0])))
                add(q, _lit(cam, (200, 160, 60), nv, q[0], gloss=0.4))
        for k in range(10):
            ua = -0.24 + 0.48 * k / 10; ub = ua + 0.048
            q = [hp(ua, 0.245, back=thick + 4), hp(ub, 0.245, back=thick + 4), hp(ub, 0.275, back=thick + 4), hp(ua, 0.275, back=thick + 4)]
            nv = v_norm(v_cross(v_sub(q[1], q[0]), v_sub(q[3], q[0])))
            add(q, _lit(cam, (200, 160, 60), nv, q[0], gloss=0.4))

    # ---------------- head
    hood_p = hp
    hp = S[-1]
    f = fwd
    rr_ = v_norm(v_cross((0, -1, 0), f))
    if v_dot(rr_, rr_) < 1e-6:
        rr_ = (1, 0, 0)
    uh = v_norm(v_cross(f, rr_))   # head up (screen-up-ish)
    if uh[1] > 0:
        uh = v_mul(uh, -1); rr_ = v_mul(rr_, -1)
    jaw = pose['jaw']
    L = 285.0; Wh = 98.0; Ht = 82.0
    NX = 14; NA = 14

    def hw(x):
        if x < 0.32:
            return Wh * (0.86 + 0.14 * math.sin(x / 0.32 * math.pi / 2))
        return Wh * math.sqrt(max(0.0, 1 - ((x - 0.32) / 0.68) ** 2.0))

    def hh(x):
        return Ht * (1 - 0.42 * x) * math.sqrt(max(0.0, 1 - x ** 6))

    base = v_add(hp, v_add(v_mul(f, -40), v_mul(uh, -18)))

    def upper(x, a):            # a in [0, pi]: lip(right) -> top -> lip(left)
        c, s_ = math.cos(a), math.sin(a)
        sx_ = math.copysign(abs(c) ** 0.6, c)
        sy_ = abs(s_) ** 0.45
        return v_add(base, v_add(v_mul(f, x * L), v_add(v_mul(rr_, hw(x) * sx_), v_mul(uh, hh(x) * sy_ + 4))))

    def lower(x, a):
        c, s_ = math.cos(a), math.sin(a)
        sx_ = math.copysign(abs(c) ** 0.6, c)
        sy_ = abs(s_) ** 0.6
        ang = jaw * 0.5
        fx = math.cos(ang); fy = -math.sin(ang)
        jf = v_norm(v_add(v_mul(f, fx), v_mul(uh, fy)))
        ju = v_cross(jf, rr_)
        if v_dot(ju, uh) < 0:
            ju = v_mul(ju, -1)
        xx = x * 0.94
        return v_add(base, v_add(v_mul(jf, xx * L), v_add(v_mul(rr_, hw(xx) * 0.9 * sx_), v_mul(ju, -hh(xx) * 0.42 * sy_))))

    HEADC = (36, 34, 29)
    GG = {}
    for fn, col_main, gl in ((upper, HEADC, 0.75), (lower, (205, 180, 122), 0.35)):
        G = [[fn(x / NX, math.pi * a / NA) for a in range(NA + 1)] for x in range(NX + 1)]
        GG[fn] = G
        for x in range(NX):
            for a in range(NA):
                q = [G[x][a], G[x][a + 1], G[x + 1][a + 1], G[x + 1][a]]
                nv = v_cross(v_sub(q[1], q[0]), v_sub(q[3], q[0]))
                if v_dot(nv, nv) < 1e-9:
                    continue
                nv = v_norm(nv)
                pc = v_mul(v_add(q[0], q[2]), 0.5)
                # large head plates: alternate tone in a coarse grid
                LIP = (218, 194, 124); BAR = (30, 27, 22)
                rim = (a <= 1 or a >= NA - 2) and x < NX - 2
                if fn is upper:
                    col = tuple(int(c_ * (0.93 + 0.14 * hsh(x * 17 + a, 31))) for c_ in (66, 57, 40))   # head scales
                    if rim:
                        col = BAR if x % 3 == 1 and x > 2 else LIP       # barred lip scales
                    elif (a in (2, NA - 3)) and x > 4:
                        col = (150, 128, 80)                             # pale line above the lip
                else:
                    col = BAR if (rim and x % 3 == 1 and x > 2) else ((226, 206, 140) if x % 2 == 0 else (200, 180, 118))
                add(q, _lit(cam, col, nv, pc, gloss=gl if x < NX - 2 else 0.15))
        # palate / mouth floor (dark) closes the open side
        for x in range(NX):
            q = [G[x][0], G[x + 1][0], G[x + 1][NA], G[x][NA]]
            if jaw <= 0.1:
                add(q, (20, 17, 14))
    if jaw > 0.1:
        _mouth(add, cam, GG[upper], GG[lower], NX, NA, jaw)
    # neck-to-head bridge: a loft from the neck ring into the back of the skull, so the head grows out of the neck
    j0 = m - 1 - int(170 / seg)
    NB = 7; NL = 2 * NA
    R0 = rad(m - 1) * 1.05

    def ring_head(k):
        if k <= NA:
            return upper(0.0, math.pi * k / NA)
        return lower(0.0, math.pi * (NL - k) / NA)

    def ring_neck(t, k):
        ph = math.pi * k / NA
        c = IP(S, j0 + t * (m - 1 - j0))
        return v_add(c, v_add(v_mul(rr_, R0 * math.cos(ph)), v_mul(uh, R0 * math.sin(ph))))
    BR = []
    for b in range(NB + 1):
        t = b / NB
        w = t * t * (3 - 2 * t)
        BR.append([v_lerp(ring_neck(t, k), ring_head(k), w) for k in range(NL + 1)])
    for b in range(NB):
        for k in range(NL):
            q = [BR[b][k], BR[b][k + 1], BR[b + 1][k + 1], BR[b + 1][k]]
            nv = v_cross(v_sub(q[1], q[0]), v_sub(q[3], q[0]))
            if v_dot(nv, nv) < 1e-9:
                continue
            nv = v_norm(nv)
            if v_dot(nv, v_sub(v_mul(v_add(q[0], q[2]), 0.5), IP(S, j0 + (b + 0.5) / NB * (m - 1 - j0)))) < 0:
                nv = v_mul(nv, -1)
            belly = k > NA + 1 and k < NL - 1
            col = (214, 190, 124) if belly else tuple(int(c_ * (0.92 + 0.14 * hsh(b * 13 + k, 41))) for c_ in (62, 54, 38))
            if belly and b % 2 == 0:
                col = (176, 152, 98)
            add(q, _lit(cam, col, nv, v_mul(v_add(q[0], q[2]), 0.5), gloss=0.5 if not belly else 0.3))
    # throat: the chin's underside flows straight down into the hood's ventral plates (no seam under the jaw)
    if flare > 0.02 and jaw <= 0.1:
        it = i_top
        sgn = 1 if v_dot(IP(Lt, it), rr_) > 0 else -1
        NK = 10; NR = 6
        top = [lower(0.1 + 0.3 * (1 - abs(2 * k / NK - 1)) ** 2, math.pi * (0.16 + 0.68 * k / NK)) for k in range(NK + 1)]
        bot = [hood_p(sgn * 0.34 * (1 - 2 * k / NK), 0.015, lift=4) for k in range(NK + 1)]
        mid_c = v_lerp(v_lerp(top[NK // 2], bot[NK // 2], 0.5), IP(S, it), 0.0)
        out_dir = v_norm(v_sub(v_lerp(top[NK // 2], bot[NK // 2], 0.5), IP(S, it)))
        TR = []
        for r_ in range(NR + 1):
            t = r_ / NR
            TR.append([v_add(v_lerp(top[k], bot[k], t), v_mul(out_dir, 22 * math.sin(math.pi * t) * (1 - abs(2 * k / NK - 1) ** 2))) for k in range(NK + 1)])
        for r_ in range(NR):
            for k in range(NK):
                q = [TR[r_][k], TR[r_][k + 1], TR[r_ + 1][k + 1], TR[r_ + 1][k]]
                nv = v_cross(v_sub(q[1], q[0]), v_sub(q[3], q[0]))
                if v_dot(nv, nv) < 1e-9:
                    continue
                nv = v_norm(nv)
                if v_dot(nv, out_dir) < 0:
                    nv = v_mul(nv, -1)
                edge = k in (0, NK - 1)
                col = (226, 206, 140) if r_ % 2 == 0 else (204, 182, 120)
                if edge:
                    col = mix(col, (60, 52, 38), 0.6)
                add(q, _lit(cam, col, nv, v_mul(v_add(q[0], q[2]), 0.5), gloss=0.3, amb=0.3))
    # fangs: part of the mesh, rooted in the upper jaw just behind the snout
    jw = clamp((jaw - 0.12) / 0.5)
    if jw > 0:
        for sx in (-1, 1):
            xr_ = 0.8
            root = v_add(base, v_add(v_mul(f, xr_ * L), v_add(v_mul(rr_, sx * hw(xr_) * 0.55), v_mul(uh, 3))))
            tip = v_add(root, v_add(v_mul(uh, -46 * jw), v_mul(f, -12 * jw)))
            for side in (-1, 1):
                tri = [v_add(root, v_add(v_mul(f, -7), v_mul(rr_, side * 4))), v_add(root, v_mul(f, 7)), tip]
                add(tri, (238, 234, 222) if side == 1 else (196, 192, 180))
    info = {'base': base, 'f': f, 'r': rr_, 'u': uh, 'L': L, 'Wh': Wh, 'Ht': Ht, 'hw': hw, 'hh': hh,
            'S': S, 'D': D, 'Lt': Lt, 'i_top': i_top, 'i_bot': i_bot}
    return F, info


def draw_cobra(g, cam, pose, t):
    F, I = build(cam, pose)
    FF = Faces(); FF.f = F
    # soft contact shadow under the coil
    sh = [(C0[0] + 720 * math.cos(a), GROUND + 2, C0[2] + 640 * math.sin(a)) for a in [2 * math.pi * k / 48 for k in range(48)]]
    fill3(g, cam, sh, (4, 4, 4), 0.7)
    FF.draw(g, cam)
    base, f, r, u, L = I['base'], I['f'], I['r'], I['u'], I['L']
    hw, hh = I['hw'], I['hh']
    # eyes on the sides of the head, under a brow
    for sx in (-1, 1):
        x = 0.36
        ec = v_add(base, v_add(v_mul(f, x * L), v_add(v_mul(r, sx * hw(x) * 0.93), v_mul(u, hh(x) * 0.45))))
        n_out = v_norm(v_add(v_mul(r, sx), v_mul(f, 0.35)))
        if v_dot(n_out, v_sub(cam.eye, ec)) <= 0:
            continue
        glow = pose.get('eyeglow', 1.0)
        point3(g, cam, ec, 50 * glow, GOLD, 0.10 * glow)
        point3(g, cam, ec, 19, (12, 10, 8), 1)
        point3(g, cam, ec, 16.5, (170, 128, 34), 1)
        point3(g, cam, ec, 14, (10, 9, 8), 1)
        point3(g, cam, v_add(ec, v_add(v_mul(u, 7), v_mul(f, 3))), 3, (255, 248, 225), 0.8)
    # nostrils
    for sx in (-1, 1):
        x = 0.88
        point3(g, cam, v_add(base, v_add(v_mul(f, x * L), v_add(v_mul(r, sx * 26), v_mul(u, hh(x) * 0.75)))), 6, (8, 8, 8), 0.9)
    jaw = pose['jaw']
    fl = pose.get('tongue', 0.0)
    if fl > 0.05:
        t0 = v_add(base, v_add(v_mul(f, L * 0.98), v_mul(u, -8)))
        tm = v_add(t0, v_add(v_mul(f, 120 * fl), v_mul(u, -20 * fl)))
        seg3(g, cam, t0, tm, (20, 18, 16), 6, 1)
        for sx in (-1, 1):
            tt = v_add(tm, v_add(v_mul(f, 55 * fl), v_add(v_mul(r, sx * 26 * fl), v_mul(u, -10 * fl * sx))))
            seg3(g, cam, tm, tt, (20, 18, 16), 4, 1)
    return I
