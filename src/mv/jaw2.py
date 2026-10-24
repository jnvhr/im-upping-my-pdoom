"""v23 overhaul of the white/gold wireframe block mouth (based on s3a.s_jaw, v2)."""
import math
from cam3d import *
from lyrics import LINE_WORDS
from s3a import T0, WT

RX, RZ = 430.0, 360.0          # arch half-width / depth (front of arch at z=0)
HINGE = (0.0, RZ + 140.0)     # lower jaw hinge (y, z)
NT = 16                        # teeth per arch


def _arch(n=NT):
    out = []
    for i in range(n):
        a = math.pi * (0.04 + 0.92 * i / (n - 1))
        x = RX * math.cos(a); z = RZ * (1 - math.sin(a))
        # tangent direction in xz
        tx, tz = -math.sin(a), -math.cos(a)
        yaw = math.atan2(tz, tx)
        k = abs(i - (n - 1) / 2)       # 0 centre .. 7.5 back
        if k < 1.6:   kind = 'inc'
        elif k < 2.6: kind = 'can'
        elif k < 4.6: kind = 'pre'
        else:         kind = 'mol'
        out.append((x, z, yaw, kind, i))
    return out


ARCH = _arch()
SPEC = {'inc': (58, 120, 40, 0.75, 0.9), 'can': (52, 150, 52, 0.22, 0.3),
        'pre': (62, 100, 64, 0.7, 0.7), 'mol': (78, 82, 80, 0.85, 0.85)}


def _tooth(x, z, yaw, kind, sgn, root_y):
    """tapered block: root face at root_y, tip toward the bite plane"""
    w, h, d, tw, td = SPEC[kind]
    c, s = math.cos(yaw), math.sin(yaw)
    V = []
    for yy, sw, sd in ((0, 1, 1), (h, tw, td)):
        for (lx, lz) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            px = lx * w / 2 * sw; pz = lz * d / 2 * sd
            V.append((x + px * c - pz * s, root_y + sgn * yy, z + px * s + pz * c))
    return V, h


def _syllables():
    W5 = LINE_WORDS[5]
    t0, t1 = W5[0][1], W5[0][2]
    sy = [t0 + (t1 - t0) * k / 4 for k in range(4)]   # Chat-G-P-T
    sy += [a for w, a, e in W5[1:5]]
    return sy, W5[5][1]


def mouth_open(t):
    """smooth rounded open/close per syllable (no wedge); from 'alive' opens wide and holds"""
    sy, tA = _syllables()
    op = 0.06
    for i, a in enumerate(sy):
        b = sy[i + 1] if i + 1 < len(sy) else tA
        d = min(b - a, 0.34)
        if a <= t < a + d:
            u = (t - a) / d
            op = 0.06 + 0.5 * math.sin(math.pi * u) ** 0.8
    wide = eio(prog(t, tA - 1.0, tA - 0.45))
    return lerp(op, 1.0, wide), wide, sy


def _rot_lower(p, ang):
    x, y, z = p
    hy, hz = HINGE
    y0, z0 = y - hy, z - hz
    c, s = math.cos(ang), math.sin(ang)
    return (x, hy + y0 * c - z0 * s, hz + y0 * s + z0 * c)


def s_jaw_wire(g, t, lt):
    tS = T0(5); tE = T0(6)
    op, wide, sy = mouth_open(t)
    tA = _syllables()[1]
    keys = [(tS, (-120, -420, -1750), (0, 40, 200), 46, 0.0),
            (19.2, (-560, -240, -1250), (0, 50, 220), 50, 0.05),
            (tA - 0.1, (420, -120, -1050), (0, 60, 250), 54, -0.04),
            (tA + 0.3, (0, 40, -560), (0, 120, 400), 58, 0.0),
            (tE - 0.2, (0, 60, 60), (0, 330, 900), 64, 0.0),
            (tE, (0, 200, 420), (0, 700, 1100), 72, 0.0)]
    cam = cam_at(t, keys)
    ang = 0.62 * op                       # lower jaw drop
    lift = -40 * op                       # upper jaw tilts back a touch
    gap = 14
    # one smooth move: the keyed camera glides onto the throat axis over 0.6 s while it is already travelling inward
    k = eio(prog(t, 19.3, 20.4))
    if k > 0:
        sc = _sc(t, tA)
        eye = campos(sc, 0.62, gap)        # v49: camera path uses the wide-open jaw, so syllable chomps don't shake it
        tgt = campos(sc + 450, 0.62, gap, look=True)
        ke, kt, kf, kr = path(t, keys)
        E = tuple(lerp(a, b, k) for a, b in zip(ke, eye)); T = tuple(lerp(a, b, k) for a, b in zip(kt, tgt))
        c0 = Cam3(E, T, lerp(kf, 70, k), 0.0)
        # roll so each letter reads upright as the camera reaches it (a barrel roll down the throat)
        rolls = []; prev = 0.0
        for i in range(5):
            _, rt, _ = letter_frame(i, ang, gap)
            th = math.atan2(v_dot(rt, c0.u), v_dot(rt, c0.r))
            while th - prev > math.pi: th -= 2 * math.pi
            while th - prev < -math.pi: th += 2 * math.pi
            rolls.append(th); prev = th
        roll = 0.0
        for i in range(5):
            st = AL_S[i] - 520                          # turn while it approaches, upright ~200 before it
            w = eio(clamp((sc - st) / 320))
            roll = lerp(roll, rolls[i], w)
        cam = Cam3(E, T, lerp(kf, 70, k), kr * (1 - k))   # no roll: ALIVE is back in the caption
    env(g, cam, 420, fog=5000)
    # which teeth glow: a gold sweep crosses the arch on each syllable
    hot = set()
    for i, a in enumerate(sy):
        u = (t - a) / 0.3
        if 0 <= u < 1:
            c0 = int(u * NT)
            for k in (c0 - 1, c0, c0 + 1):
                hot.add((i % 2, k))
    F = Faces()
    for arch, sgn in ((0, -1), (1, 1)):
        root = sgn * (gap + 118)          # roots sit inside the gum rail
        for (x, z, yaw, kind, i) in ARCH:
            V, h = _tooth(x, z, yaw, kind, -sgn, root)
            if arch == 0:
                V = [(v[0], v[1] + lift * (1 - v[2] / RZ) * 0.3, v[2]) for v in V]
            else:
                V = [_rot_lower(v, ang) for v in V]
            gold = (arch, i) in hot or (kind == 'can')
            st = GOLD if gold else INK
            for idx in BOX_F:
                F.quad([V[q] for q in idx], st, BG, 2.2 if gold else 1.8)
        # gum rails (outer + inner) with ticks between teeth
        for rr, al in ((1.18, 0.95), (0.80, 0.55)):
            pts = []
            for u in range(41):
                a = math.pi * u / 40
                p = (RX * rr * math.cos(a), root, RZ - RZ * rr * math.sin(a) + (rr - 1) * 40)
                pts.append(_rot_lower(p, ang) if arch else p)
            poly3(g, cam, pts, GOLD, 3 if rr > 1 else 2, al)
        for (x, z, yaw, kind, i) in ARCH:
            p1 = (x * 1.18, root, RZ - (RZ - z) * 1.18 + 7)
            p2 = (x * 0.80, root, RZ - (RZ - z) * 0.80 - 8)
            if arch:
                p1, p2 = _rot_lower(p1, ang), _rot_lower(p2, ang)
            seg3(g, cam, p1, p2, GOLDD, 1.4, 0.8)
    # tongue: wire mesh inside the lower arch
    rows, cols = 7, 11
    tg = []
    for r in range(rows):
        row = []
        for cix in range(cols):
            u = cix / (cols - 1) * 2 - 1; v = r / (rows - 1)
            x = u * RX * 0.62 * (1 - 0.35 * (1 - v))
            z = 70 + v * (RZ + 40)
            y = gap + 150 - 55 * (1 - u * u) * math.sin(math.pi * (0.2 + 0.8 * v)) - 8 * math.sin(t * 5 + v * 4)
            row.append(_rot_lower((x, y, z), ang))
        tg.append(row)
    ta = 0.8
    if ta > 0.01:
        for row in tg:
            poly3(g, cam, row, INK, 1.2, ta * 0.7)
        for cix in range(cols):
            poly3(g, cam, [tg[r][cix] for r in range(rows)], INK, 1.2, ta * 0.7)
    F.draw(g, cam, fog=5000)
    throat(g, cam, t, tA, tE, ang, gap, k, tg[-1])
    # HUD callouts
    a_hud = 1 - prog(t, tA, tA + 0.4)
    if a_hud > 0.02:
        p = (-RX - 60, -170, 80)
        seg3(g, cam, p, (-RX + 30, -gap - 120, 120), GOLD, 1.2, a_hud)
        text3(g, cam, 'MODEL.MOUTH  OPEN %02d%%' % int(op * 100), (p[0] - 40, p[1] - 30, p[2]), 22, GOLD, 'mono', a_hud, 'rm')
        q = (RX + 80, 230, 120)
        seg3(g, cam, q, (RX - 40, gap + 120, 160), GOLD, 1.2, a_hud)
        text3(g, cam, 'TEETH 32/32  //  BITE %s N' % format(int(1200 + 5400 * op), ','), (q[0] + 30, q[1] + 30, q[2]), 22, INK, 'mono', a_hud, 'lm')
    # lyric above the mouth, facing camera
    hl = {'chatgpt,': GOLD, 'eat': GOLD, 'alive': GOLD}
    # world-anchored caption: a fixed 3D plane above the front of the mouth; the camera flies past it, it never follows
    # 'alive' is left out of the caption (so ME sits centred)
    if t < tE - 0.1:
        _full = LINE_WORDS[5]
        LINE_WORDS[5] = _full[:-1]
        try:
            lyric3x(g, cam, t, 5, (0.0, -330.0, -120.0), (1, 0, 0), (0, -1, 0), 1150, 100, INK, hl, depth=50)
        finally:
            LINE_WORDS[5] = _full
    # deep in the throat: ease to full black well before the chorus ("I'M")
    g.post = dict(glow=0.25, grain=0.03, vig=0.5)
    blk = eio(prog(t, tE - 0.7, tE - 0.18))
    if blk > 0:
        g.rect(0, 0, W, H, fill=BG, a=blk, fa=blk)




# ---------------- throat: starts at the back of the tongue and curves down into the dark
def _sc(t, tA):
    """camera distance along the mouth/throat axis: one constant glide, lips crossed right on the 'A'"""
    # v49: ONE monotone push-in (no back-and-forth): eases from rest at 19.3 s, matching the keyed camera's depth,
    # and reaches the 1450/s glide exactly at tA-0.2, so the lips are crossed right on ALIVE
    t1 = tA - 0.20
    s1 = 1450 * (t1 - tA - 0.47)
    if t >= t1:
        return 1450 * (t - tA - 0.47)
    t0 = 19.3; s0 = -1790.0
    h = t1 - t0; D = s1 - s0
    n = 1450 * h / D
    u = clamp((t - t0) / h)
    return s0 + D * u ** n


_LS = 1200.0


def _throat_eye(s, ang, gap, look=False):
    c, tg, n = tframe(s, ang, gap)
    r = _sect(max(0, s))[1]
    return v_add(c, v_mul(n, -r + 70 - (0 if look else 45))), tg


def campos(s, ang, gap, look=False):
    """camera line: straight in from the front at mouth height, through the open lips, over the tongue, then down the throat"""
    if s >= 0:
        return _throat_eye(s, ang, gap, look)[0]
    E0, tg0 = _throat_eye(0, ang, gap, look)
    P0 = (0.0, 110.0, E0[2] - _LS)
    if s <= -_LS:
        return (0.0, 110.0, P0[2] + (s + _LS))
    u = 1 + s / _LS
    P1 = (0.0, 110.0, P0[2] + _LS * 0.4)
    P2 = v_sub(E0, v_mul(tg0, _LS * 0.35))
    a, b, c, d = (1 - u) ** 3, 3 * u * (1 - u) ** 2, 3 * u * u * (1 - u), u ** 3
    return tuple(a * p0 + b * p1 + c * p2 + d * p3 for p0, p1, p2, p3 in zip(P0, P1, P2, E0))


AL_S = [380 + 260 * i for i in range(5)]
AL_A = [math.pi / 2 + i * 2 * math.pi / 5 for i in range(5)]   # A on the floor, then round the tube


def letter_frame(i, ang, gap):
    """ALIVE letter i stands on the throat wall at its own angle round the tube, top pointing to the centre"""
    s = AL_S[i]; a = AL_A[i]
    c, tg, n = tframe(s, ang, gap)
    rx, ry = _sect(s)
    cen = v_add(c, v_mul(n, -ry + 70))
    p = v_add(v_add(cen, (0.55 * rx * math.cos(a), 0, 0)), v_mul(n, 0.55 * ry * math.sin(a)))
    right = v_norm(v_add((math.sin(a), 0, 0), v_mul(n, -math.cos(a))))
    up = v_norm(v_add((-math.cos(a), 0, 0), v_mul(n, -math.sin(a))))
    return p, right, up


def _anchor(ang, gap):
    return _rot_lower((0.0, gap + 150.0, 70 + RZ + 40.0), ang)


def tframe(s, ang, gap, ds=20.0):
    """centre-line point, tangent and floor-normal of the throat at length s (s<0 = back toward the lips)"""
    p = list(_anchor(ang, gap))
    th0 = ang
    def th(u):
        return th0 + (1.25 - th0) * eio(clamp(u / 1100.0))
    if s <= 0:
        tg = (0.0, math.sin(th0), math.cos(th0))
        p = [p[0], p[1] + tg[1] * s, p[2] + tg[2] * s]
        a = th0
    else:
        u = 0.0
        while u < s:
            st = min(ds, s - u)
            a = th(u + st / 2)
            p[1] += math.sin(a) * st; p[2] += math.cos(a) * st
            u += st
        a = th(s)
    tg = (0.0, math.sin(a), math.cos(a))
    n = (0.0, math.cos(a), -math.sin(a))     # points to the throat floor (screen-down)
    return tuple(p), tg, n


def _sect(s):
    w = clamp(s / 900.0)
    return lerp(260, 165, w), lerp(120, 130, w)   # rx, ry


def throat(g, cam, t, tA, tE, ang, gap, inside=1.0, tback=None):
    """the throat is the tongue's own continuation: same white wire floor, flowing on down into the dark"""
    vis = 1.0      # the throat is there from the first frame of the scene
    NS = 20
    NC = 11
    rings = []
    for j in range(25):
        s = j * 70.0
        c, tg, n = tframe(s, ang, gap)
        rx, ry = _sect(s)
        sw = 1 + 0.04 * math.sin(t * 9 - j * 0.6) * clamp(s / 300)
        cen = v_add(c, v_mul(n, -ry * sw + 70))   # floor sits just under the tongue surface
        ring = []
        for i in range(NS + 1):
            a = 2 * math.pi * i / NS
            ring.append(v_add(v_add(cen, (rx * sw * math.cos(a), 0, 0)), v_mul(n, ry * sw * math.sin(a))))
        # floor lines: the tongue's 11 columns carried on round the bottom of the tube
        fl = []
        for ci in range(NC):
            u = ci / (NC - 1) * 2 - 1
            a = math.pi / 2 - u * 1.25
            fl.append(v_add(v_add(cen, (rx * sw * math.cos(a), 0, 0)), v_mul(n, ry * sw * math.sin(a))))
        rings.append((s, ring, cen, n, fl))
    for s, ring, cen, n, fl in rings:
        fade = vis * (1 - min(1, s / 1750))
        if int(s / 70) % 4 == 0:
            poly3(g, cam, ring, GOLD, 1.6, fade * 0.85)
        else:
            poly3(g, cam, ring, DIM, 1.1, fade * 0.6)
        poly3(g, cam, fl, INK, 1.2, fade * 0.56)       # cross lines of the floor, like the tongue rows
    for ci in range(NC):
        line = [r[4][ci] for r in rings]
        if tback is not None:
            line = [tback[ci]] + line                    # joined to the back row of the tongue
        poly3(g, cam, line, INK, 1.2, vis * 0.56)
    for i in range(0, NS, 2):
        if 0.3 * math.pi < 2 * math.pi * i / NS < 0.7 * math.pi:
            continue
        poly3(g, cam, [r[1][i] for r in rings], DIM, 1.0, vis * 0.45)
    # (v33) no ALIVE anywhere: removed from the throat and from the caption
