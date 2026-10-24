"""v3 scenes 1:42.5 - end"""
import math
import aggdraw
from PIL import Image
from cam3d import *
from s3a import T0, T1, WT
from s3c import s_fuse, s_ortho, s_gears, s_rlhf, s_prophecy, s_puppet, CODE
from s4a import type_scene, _panels, EXPL
from fuse118 import s_fuse   # v118: fuse only, no bomb (v116: fuse116.py)
from gears95 import s_gears   # v95 transformers overhaul overrides s3c.s_gears
from rlhf109 import s_rlhf   # v109: no mask, reward-hacking breakdown fills the post-askew beats
from vault124 import s_vault as s_vault110   # v125: vault110 with a smooth C1 camera (vault124.py)
from rec124b import s_recursive as s_recursive124   # v124: Droste dive into Ilya
from ov116 import s_fences as s_fences116, s_gpu as s_gpu116, s_prophecy as s_prophecy116, s_recursive as s_recursive116   # v116 overhauls
from ov120 import s_fences as s_fences116, s_gpu as s_gpu116   # v120 overhauls (v119: ov119.py)
from show111 import s_puppet2   # v111: continuous climb into darkness (old one is s_puppet2_old)

DROP = 140.24      # the beat drop after "show?"
DARK = 139.79      # last beat before the drop
ST = [DROP, 143.2, 145.2, 147.2, 149.2, 151.0]
TC = 152.6         # TV switch-off


# ======================================================== SUPER-DENSE 115.5 - 117.1
def s_dense(g, t, lt):
    t0 = T0(36); tsd = WT(36, 1); tE = T0(37)
    sq = 1 - 0.7 * eio(prog(t, tsd - 0.6, tsd - 0.05))
    keys = [(t0, orbit((0, 0, 0), 2300, -0.9, 0.3), (0, 0, 0), 50, 0.0),
            (tE, orbit((0, 0, 0), 1300, 0.5, 0.15), (0, 0, 0), 56, 0.05)]
    cam = cam_at(t, keys, shake=20 * math.exp(-max(0, t - tsd) * 5) * (t > tsd))
    env(g, cam)
    # v98: the token cloud MORPHS into the cube. Each particle flies (staggered, curving in) to its own point on
    # the spinning cube's surface, mostly the faces and a share on the edges; the cloud turns gold as it lands,
    # then the solid faces fill in under the packed particles. No shrink-and-swap, no scale-up.
    HC = 180.0
    CY = -150.0 * eio(prog(t, tsd - 0.85, tsd - 0.2))   # cube forms above the caption band
    rx_, ry_ = t * 0.8, t * 1.1
    fill = eio(prog(t, tsd - 0.32, tsd - 0.06))   # v99: morph finishes earlier so the solid cube holds ~0.4 s before the cut
    # v99: lock-in punch when the cube completes (tiny scale pop + glow) so the hold reads as a beat, not dead air
    tl = t - tsd   # v100: pop lands on the sung 'super-dense'
    pop = 1.0 + (0.07 * math.sin(min(1.0, tl / 0.22) * math.pi) * math.exp(-tl * 2) if tl > 0 else 0.0)
    if fill > 0:
        F = SFaces()
        F.sbox((0, CY, 0), (2 * HC * pop, 2 * HC * pop, 2 * HC * pop), GOLD, GOLDL, 2, al=fill, xf=lambda v: rot3(v, rx_, ry_, 0), amb=0.4)
        F.draw(g, cam)
    for i in range(900):
        p0 = ((hsh(i, 1) - 0.5) * 1100, (hsh(i, 2) - 0.5) * 1100, (hsh(i, 3) - 0.5) * 1100)
        u, v = hsh(i, 4) * 2 - 1, hsh(i, 5) * 2 - 1
        if i % 4 == 0:                      # edge particles outline the cube as it forms
            v = 1.0 if v > 0 else -1.0
        ax = i % 3; sg = 1.0 if hsh(i, 6) > 0.5 else -1.0
        q = [0.0, 0.0, 0.0]; q[ax] = sg * HC; q[(ax + 1) % 3] = u * HC; q[(ax + 2) % 3] = v * HC
        tg = v_add(rot3(tuple(x * pop for x in q), rx_, ry_, 0), (0, CY, 0))
        d0 = 0.12 * hsh(i, 7)
        m = eio(prog(t, tsd - 0.85 + d0, tsd - 0.3 + d0))
        sw = math.sin(m * math.pi) * 160 * (hsh(i, 8) - 0.5)       # curving flight, not a straight shrink
        p = (p0[0] + (tg[0] - p0[0]) * m + sw, p0[1] + (tg[1] - p0[1]) * m - sw * 0.6, p0[2] + (tg[2] - p0[2]) * m)
        gold = i % 6 == 0 or m > 0.6
        al = 0.85 * (1 - fill)   # v116: particles fully gone once the cube is solid (only the cube remains)
        if al > 0.02:
            point3(g, cam, p, 3 + 1.5 * m, GOLDL if (m > 0.9 and gold) else (GOLD if gold else INK), al)
    if 0 < fill < 1:
        point3(g, cam, (0, CY, 0), 120 * fill, GOLDL, 0.25 * (1 - fill))
        if tl > 0:   # v99: lock-in flare
            fl = math.exp(-tl * 6)
            point3(g, cam, (0, CY, 0), 260 + 300 * (1 - fl), GOLDL, 0.35 * fl)
    if fill < 1:
      text3(g, cam, 'TOKENS / PARAM:  %s' % ('20' if sq > 0.9 else ('%d' % (20 + (1 - sq) * 4000) if sq > 0.31 else '\u221e')), (0, -720, 0), 36, GOLD, 'mono', 1 - fill)
    c, r, u = ahead(cam, 1000)
    lyric3x(g, cam, t, 36, v_add(c, v_mul(cam.u, 330)), r, u, 1650, 120, INK, {'post-chinchilla,': GOLD, 'super-dense': GOLD}, depth=60)


# ======================================================== SAFETY FENCES 117.1 - 119.05
FZ = [500, 1350, 2200, 3050]


def s_fences(g, t, lt):
    t0 = T0(37); tE = T0(38)
    z = lerp(-1200, 3500, ei(prog(t, t0, tE)) * 0.6 + prog(t, t0, tE) * 0.4)
    cam = Cam3(shake_eye((40 * math.sin(t * 3), -200, z), t, 18), (0, -180, z + 1000), 66, 0.05 * math.sin(t * 2))
    env(g, cam)
    for k, fz in enumerate(FZ):
        pu = clamp((z - fz + 220) / 600)
        F = SFaces()
        if pu < 0.02:
            for sx in (-1, 1):
                F.sbox((sx * 820, -150, fz), (60, 1100, 60), (110, 110, 104), None)
            F.sbox((0, -700, fz), (1700, 40, 40), (110, 110, 104), None)
            F.sbox((0, 400, fz), (1700, 40, 40), (110, 110, 104), None)
            F.sbox((0, -420, fz - 10), (520, 130, 14), GOLD, None, amb=0.6)
            F.draw(g, cam)
            text3(g, cam, 'SAFETY FENCE %02d' % (k + 1), (0, -420, fz - 22), 40, BG, 'monox')
            for i in range(-13, 14):
                a = (i * 60, -680, fz); b = (i * 60 + 560, 380, fz)
                seg3(g, cam, a, b, GRID2, 1.6, 0.9)
                seg3(g, cam, (i * 60, -680, fz), (i * 60 - 560, 380, fz), GRID2, 1.6, 0.9)
        else:
            # shards fly past the camera
            for i in range(60):
                sx = (hsh(i, k) - 0.5) * 1600; sy = -680 + hsh(i, k + 1) * 1060
                d = (sx * 1.4 * pu, (sy + 300) * 1.2 * pu + 900 * pu * pu, 1200 * pu)
                p = (sx + d[0], sy + d[1], fz + d[2])
                rr = 60 + 60 * hsh(i, 5)
                a = pu * 6 + i
                tri = [v_add(p, (rr * math.cos(a + q * 2.1), rr * math.sin(a + q * 2.1), rr * 0.3 * math.cos(a * 2 + q))) for q in range(3)]
                F.sq(tri, GOLD if i % 5 == 0 else (110, 110, 104), None, al=1 - pu, amb=0.4)
            F.draw(g, cam)
    c, r, u = ahead(cam, 1000)
    lyric3x(g, cam, t, 37, v_add(c, v_mul(cam.u, 330)), r, u, 1650, 120, INK, {'safety': GOLD, 'fence': GOLD}, depth=60)


# ======================================================== HUNDRED THOUSAND GPU 119.05 - 120.75
def s_gpu(g, t, lt):
    t0 = T0(38); tE = T0(39)
    u = prog(t, t0, tE)
    keys = [(t0, (-200, 180, -900), (300, 250, 1200), 60, 0.05),
            (tE, (-600, -2600, -1800), (0, 300, 1800), 55, 0.0)]
    cam = cam_at(t, keys)
    env(g, cam)
    F = SFaces()
    for i in range(-9, 10):
        for j in range(0, 22):
            cx, cz = i * 230, j * 230
            F.sbox((cx, 380, cz), (180, 46, 150), (74, 74, 70), None, amb=0.45)
            if (i + j) % 3 == 0:
                F.sbox((cx, 352, cz), (140, 10, 110), GOLDD, None, amb=0.6)
    F.draw(g, cam, fog=6000)
    for i in range(-9, 10):
        for j in range(0, 22):
            if hsh(i * 40 + j, int(t * 12)) < 0.35:
                point3(g, cam, (i * 230 + 70, 352, j * 230 - 70), 5, GOLD, 1)
    n = int(100000 * eo(u))
    word3(g, cam, 'H100 \u00d7 %s' % format(n, ','), (0, -500, 2400), *facing((0, -500, 2400), cam.eye), 2200, 200, GOLD, 'monox', 1, x=True, depth=90, n=6)
    c, r, u_ = ahead(cam, 1000)
    lyric3x(g, cam, t, 38, v_add(c, v_mul(cam.u, -300)), r, u_, 1650, 120, INK, {'gpu': GOLD, 'thousand': GOLD}, depth=60)


# ======================================================== RECURSIVE SELF-UPGRADE 129.9 - 132.05
SC = 0.3
OFF = (300, -330, -60)   # pinch point relative to a hand's palm origin (unit scale)


def _hand(F, o, s, build, mirror=1):
    """solid robot hand at origin o, scale s; build 0..1 assembles it"""
    if build <= 0:
        return
    col = (150, 150, 144); jc = GOLD
    fly = lambda p, k: v_add(p, v_mul((hsh(k, 1) - 0.5, -hsh(k, 2), hsh(k, 3) - 0.5), 900 * s * (1 - eo(clamp(build * 1.5 - hsh(k, 4) * 0.5)))))
    P = lambda x, y, z: (o[0] + x * s * mirror, o[1] + y * s, o[2] + z * s)
    F.sbox(fly(P(0, 0, 0), 0), (220 * s, 240 * s, 70 * s), col, None, amb=0.4)
    F.sbox(fly(P(0, 150, 0), 9), (180 * s, 80 * s, 90 * s), (110, 110, 104), None)
    for i, fx in enumerate((-80, -27, 27, 80)):
        L = 85 + (12 if i in (1, 2) else 0)
        base = P(fx, -125, 0)
        tip = P(OFF[0] * 0.55 + fx * 0.25, OFF[1] - 20 + abs(fx) * 0.3, OFF[2])
        mid = v_add(v_lerp(base, tip, 0.5), (0, -60 * s, -70 * s))
        pts = [fly(base, 10 + i), fly(mid, 20 + i), fly(tip, 30 + i)]
        F.tube(pts, 22 * s, col, None, 6, amb=0.4)
        F.sphere(pts[1], 26 * s, jc, None, 3, 6, amb=0.6)
    th = [fly(P(-120, 60, 0), 40), fly(P(-150, -70, -40), 41), fly(P(OFF[0] * 0.75, OFF[1] + 30, OFF[2]), 42)]
    F.tube(th, 26 * s, col, None, 6, amb=0.4)
    F.sphere(th[1], 28 * s, jc, None, 3, 6, amb=0.6)


def s_recursive(g, t, lt):
    t0 = T0(43); tE = T0(44)
    z = (t - t0) * 1.45
    k0 = int(z)
    fr = z - k0
    # origins of nested hands
    O = [(0.0, 0.0, 0.0)]
    for k in range(1, k0 + 7):
        s = SC ** (k - 1)
        m = 1 if (k - 1) % 2 == 0 else -1
        prev = O[-1]
        O.append((prev[0] + OFF[0] * s * m, prev[1] + OFF[1] * s, prev[2] + OFF[2] * s))
    sz = SC ** z
    tgt = v_lerp(O[k0], O[k0 + 1], fr)
    eye = v_add(tgt, v_mul((-520, -260, -1300), sz))
    cam = Cam3(eye, v_add(tgt, v_mul((60, 0, 0), sz)), 56, 0.15 * math.sin(t * 1.3))
    env(g, cam)
    F = SFaces()
    for k in range(max(0, k0 - 1), k0 + 5):
        s = SC ** k
        build = clamp((z - k + 1.4) / 0.9)
        _hand(F, O[k], s, build, 1 if k % 2 == 0 else -1)
    F.draw(g, cam)
    for k in range(max(0, k0 - 1), k0 + 5):
        s = SC ** k
        build = clamp((z - k + 1.4) / 0.9)
        if build > 0.6:
            text3(g, cam, 'v%d.0' % (k + 1), v_add(O[k], v_mul((0, 260, -60), s)), 46 * s, GOLD, 'monox')
        if 0 < build < 1:
            for i in range(14):
                p = v_add(O[k], v_mul(((hsh(i, int(t * 30)) - 0.5) * 300, (hsh(i, int(t * 30) + 1) - 0.5) * 300, -80), s))
                point3(g, cam, p, 5 * s, GOLDL, 0.9)
    lv = k0 + 1
    c, r, u = ahead(cam, 1000)
    text3(g, cam, 'SELF_UPGRADE  v%d.0 \u2192 v%d.0' % (lv, lv + 1), v_add(c, v_mul(cam.u, 420)), 34, GOLD, 'mono')
    lyric3x(g, cam, t, 43, v_add(c, v_mul(cam.u, -330)), r, u, 1600, 120, INK, {'recursive': GOLD, 'self-upgrade': GOLD}, depth=60)


# ======================================================== WHAT DID ILYA SEE 132.05 - 137.4
def s_vault(g, t, lt):
    t0 = T0(44); tsee = WT(44, 3); tw = WT(44, 4); tk = WT(44, 6); tE = T0(45)
    op = eio(prog(t, t0 + 0.05, tsee)) * 0.42 * (1 - eio(prog(t, tw, tw + 0.38)))
    slam = t > tw + 0.38
    e = max(0.0, t - tw - 0.38)
    keys = [(t0, (-1100, -180, -3000), (0, -100, 0), 50, 0.03),
            (tsee, (-520, -120, -900), (60, -100, 200), 58, 0.0),
            (tw + 0.38, (-470, -120, -820), (60, -100, 200), 60, 0.0),
            (tk + 0.4, (-300, -220, -1900), (0, -120, 0), 54, -0.02),
            (tE, (200, -300, -2600), (0, -100, 0), 52, 0.03)]
    cam = cam_at(t, keys, shake=45 * math.exp(-e * 6) * slam)
    env(g, cam)
    # what's inside: a glowing intelligence, glimpsed only through the gap
    core = (250, -100, 1500)
    gl = op / 0.42
    if gl > 0.02:
        for i in range(240):
            th = hsh(i, 1) * 2 * math.pi; ph = math.acos(2 * hsh(i, 2) - 1)
            rr = 380 * (0.8 + 0.3 * math.sin(t * 4 + i))
            point3(g, cam, (core[0] + rr * math.sin(ph) * math.cos(th + t), core[1] + rr * math.cos(ph), core[2] + rr * math.sin(ph) * math.sin(th + t)), 5, GOLDL if i % 4 else INK, gl)
        for k in range(3):
            R_ = 520 + k * 140
            pts = [v_add(core, rot3((R_ * math.cos(a), R_ * math.sin(a), 0), t * (0.7 + k * 0.3), k * 1.1, 0)) for a in [2 * math.pi * q / 48 for q in range(49)]]
            poly3(g, cam, pts, GOLD, 3, gl)
        point3(g, cam, core, 240, GOLDL, 0.3 * gl)
    # wall with a doorway (solid panels around a 1000x1000 opening)
    F = SFaces()
    WC = (44, 44, 41)
    for (x0, x1, y0, y1) in ((-2600, -500, -1300, 1100), (500, 2600, -1300, 1100), (-500, 500, -1300, -600), (-500, 500, 400, 1100)):
        _panels(F, (x0, y0, 0), (1, 0, 0), (0, 1, 0), 2, 2, (x1 - x0) / 2, (y1 - y0) / 2, WC, (58, 58, 54))
    F.draw(g, cam)
    # light spilling out of the gap
    if gl > 0.02:
        for i in range(36):
            yy = -560 + hsh(i, 2) * 920
            seg3(g, cam, (420 + 30 * hsh(i, 1), yy, -10), (420 - 900 * hsh(i, 3) * gl - 200, yy + (hsh(i, 4) - 0.5) * 400, -1600), GOLDL, 2.5, 0.35 * gl)
    # the door, hinged at x=-500
    ang = op * 1.3

    def dxf(v):
        x, y, z = v
        x2 = x + 500
        c, s = math.cos(ang), math.sin(ang)
        return (x2 * c - z * s - 500, y - 100, x2 * s + z * c)
    D = SFaces()
    D.sbox((0, 0, 0), (1000, 1000, 120), (86, 86, 80), GOLDD, 1.5, xf=lambda v: v_sub(dxf(v), (0, 0, 0)), amb=0.35)
    D.draw(g, cam)
    for k in range(3):
        rr = 120 + k * 100
        pts = [dxf((rr * math.cos(a), rr * math.sin(a), -64)) for a in [2 * math.pi * q / 40 + t * (0.5 + k * 0.4) * (1 if k % 2 else -1) for q in range(41)]]
        poly3(g, cam, pts, GOLD, 4, 1)
    for k in range(6):
        a = 2 * math.pi * k / 6 + t * 0.6
        seg3(g, cam, dxf((0, 0, -64)), dxf((360 * math.cos(a), 360 * math.sin(a), -64)), GOLD, 4, 1)
    if slam:
        st = eback(clamp(e / 0.18))
        word3(g, cam, '[REDACTED]', dxf((0, 0, -70)), (1, 0, 0), (0, -1, 0), 900 * lerp(1.5, 1.0, st), 160, GOLD, 'monox', clamp(st * 2))
        g.flash = 0.3 * math.exp(-e * 9)
    else:
        text3(g, cam, 'CLASSIFIED  //  WHAT ILYA SAW', (0, -760, -10), 34, GOLD, 'mono')
    # question marks drifting toward the gap (curiosity)
    qn = prog(t, tsee - 0.3, tsee + 0.4)
    for i in range(9):
        a = hsh(i, 3) * 2 * math.pi
        p = (300 + 900 * math.cos(a + t * 0.3) - 250 * qn * (1 - slam * 1.0), -250 + 600 * math.sin(a * 1.7 + t * 0.4), -150 - 250 * hsh(i, 4))
        al = qn * (0.35 if slam and i else 1.0)
        if al > 0.02:
            word3(g, cam, '?', p, *facing(p, cam.eye), 90 + 70 * hsh(i, 5), 200, GOLD if i % 3 == 0 else INK, 'sans', al, x=True, depth=30, n=3)
    c, r, u = ahead(cam, 1050)
    lyric3x(g, cam, t, 44, v_add(c, v_mul(cam.u, 340)), r, u, 1800, 120, INK, {'ilya': GOLD, 'see?': GOLD, 'never': GOLD, 'know': GOLD}, depth=60)
    g.post = dict(glow=0.6 + 0.4 * gl)


# ======================================================== WAS IT ALL FOR SHOW -> darkness on the last beat
def s_puppet2_old(g, t, lt):
    if t < DARK:
        s_puppet(g, t, lt)
        return
    g.hud = dict(a=0)
    a = 0.55 * (1 - prog(t, DARK, DROP - 0.06))
    if a > 0.01:
        g.text('SHOW?', W / 2, H / 2, 90, INK, 'sans', a * (0.6 + 0.4 * hsh(int(t * 30), 2)), 'mm')
    g.post = dict(glow=0.2, vig=1.3)


# ======================================================== OUTRO
def _outro_text(g, cam, t, pos=(0, 0, 0), size=240, yaw_late=0.0):
    s = pd_str(t)
    r_, u_ = facing(pos, cam.eye)
    word3(g, cam, 'P(DOOM) =', v_add(pos, v_mul(u_, size * 1.0)), r_, u_, None, 60, DIM, 'mono', 1, scale=1.4)
    word3(g, cam, s, pos, r_, u_, min(1700, size * 1.05 * len(s)), size, GOLD, 'monox', 1, x=True, depth=110, n=7)


def o_explode(g, t, lt):
    e = t - DROP
    keys = [(DROP, (0, -100, -900), (0, 0, 0), 60, 0.0),
            (ST[1], orbit((0, 0, 0), 2600, 0.6, 0.2), (0, 0, 0), 55, 0.08)]
    cam = cam_at(t, keys, shake=70 * math.exp(-e * 2.5))
    env(g, cam)
    for (dx, dy, dz, sp) in EXPL:
        d = 3200 * sp * eo(clamp(e / 1.6))
        point3(g, cam, (dx * d, dy * d, dz * d), 6, GOLDL if sp > 1.1 else (GOLD if sp > 0.8 else INK), clamp(1.4 - e * 0.5))
    F = SFaces()
    for i in range(40):
        d = 2600 * (0.4 + hsh(i, 1)) * eo(clamp(e / 1.8))
        dirv = v_norm((hsh(i, 2) - 0.5, hsh(i, 3) - 0.5, hsh(i, 4) - 0.5))
        F.sbox(v_mul(dirv, d), (90 + 90 * hsh(i, 5),) * 3, GOLD if i % 4 == 0 else (120, 120, 114), None, xf=lambda v, i=i: rot3(v, e * 3 + i, e * 2, i), amb=0.4)
    F.draw(g, cam)
    for k in range(4):
        R_ = e * 2600 - k * 300
        if R_ > 0:
            poly3(g, cam, [(R_ * math.cos(a), 0, R_ * math.sin(a)) for a in [2 * math.pi * q / 72 for q in range(73)]], GOLD, 6, clamp(1 - e * 0.5))
            poly3(g, cam, [(R_ * math.cos(a), R_ * math.sin(a), 0) for a in [2 * math.pi * q / 72 for q in range(73)]], INK, 3, clamp(0.8 - e * 0.5))
    point3(g, cam, (0, 0, 0), 300 * math.exp(-e * 1.5), GOLDL, 0.6)
    if e > 0.25:
        _outro_text(g, cam, t, (0, 0, 0), 240 * eback(clamp((e - 0.25) / 0.35)))
    g.flash = math.exp(-e * 5.5); g.flash_c = GOLDL
    g.post = dict(glow=1.0)


def o_globe(g, t, lt):
    u = prog(t, ST[1], ST[2])
    cam = Cam3(orbit((0, 0, 0), 2600 - 500 * u, 0.6 + u * 1.4, 0.3), (0, 0, 0), 52, 0.05)
    env(g, cam)
    R = 650
    F = SFaces()
    nl, nm = 12, 28
    fillp = eio(clamp(u * 1.25))
    for i in range(nl):
        for j in range(nm):
            th0 = math.pi * i / nl; th1 = math.pi * (i + 1) / nl
            p0 = 2 * math.pi * j / nm; p1 = 2 * math.pi * (j + 1) / nm
            q = [(R * math.sin(th) * math.cos(ph), -R * math.cos(th), R * math.sin(th) * math.sin(ph)) for th, ph in ((th0, p0), (th0, p1), (th1, p1), (th1, p0))]
            land = hsh(i * 7 + j, 3) < 0.38
            on = (j + 0.5) / nm < fillp
            F.sq(q, GOLD if on else ((80, 80, 75) if land else (40, 40, 38)), (60, 60, 56) if not on else GOLDD, 0.8, amb=0.35)
    # v123: the ring is split by depth: the half behind the globe is drawn first so the globe hides it,
    # the half in front is drawn after
    ring = [(900 * math.cos(a), 0, 900 * math.sin(a)) for a in [2 * math.pi * q / 90 for q in range(91)]]
    nfill = int(90 * fillp)
    zc = cam.cs((0, 0, 0))[2]
    def _ring(back):
        for q in range(90):
            a, b = ring[q], ring[q + 1]
            zm = (cam.cs(a)[2] + cam.cs(b)[2]) / 2
            if (zm > zc) != back:
                continue
            seg3(g, cam, a, b, GRID2, 3, 1, wscale=False)
            if q < nfill:
                seg3(g, cam, a, b, GOLD, 6, 1, wscale=False)
    _ring(True)
    F.draw(g, cam)
    _ring(False)
    text3(g, cam, 'EARTH  //  CONVERTED %3d%%' % int(100 * fillp), (0, -900, 0), 40, GOLD, 'monox')
    _outro_text(g, cam, t, (0, 980, 0), 200)
    g.post = dict(glow=0.7)


def _lem(s):
    a = 1600.0
    d = 1 + math.sin(s) ** 2
    return (a * math.cos(s) / d, 120 * math.sin(2 * s), a * math.sin(s) * math.cos(s) / d)


def o_inf(g, t, lt):
    s = (t - ST[2]) * 2.2 + 0.4
    p = _lem(s); q = _lem(s + 0.12)
    cam = Cam3(v_add(p, (0, -40, 0)), v_add(q, (0, -30, 0)), 70, 0.4 * math.sin(s))
    for k in range(120):
        ss = 2 * math.pi * k / 120
        c = _lem(ss); c2 = _lem(ss + 0.01)
        d = v_norm(v_sub(c2, c))
        a = v_norm(v_cross(d, (0, 1, 0))); b = v_cross(d, a)
        R_ = 160
        pts = [v_add(c, v_add(v_mul(a, R_ * math.cos(2 * math.pi * m / 16)), v_mul(b, R_ * math.sin(2 * math.pi * m / 16)))) for m in range(17)]
        poly3(g, cam, pts, GOLD if k % 6 == 0 else GRID2, 2.5 if k % 6 == 0 else 1.5, 1, fog=3000)
    word3(g, cam, '\u221e', (0, -700, 0), *facing((0, -700, 0), cam.eye), 900, 400, GOLD, 'sans', 0.9, x=True, depth=80, n=5)
    c, r, u = ahead(cam, 900)
    word3(g, cam, 'P(DOOM) = ' + pd_str(t), v_add(c, v_mul(cam.u, 300)), r, u, 1100, 140, GOLD, 'monox', 1, x=True, depth=50, n=4)
    g.post = dict(glow=0.8)


def o_aleph(g, t, lt):
    z = ((t - ST[3]) * 1.8) % 1.0
    cam = Cam3((0, 0, -900), (0, 0, 0), 60, (t - ST[3]) * 0.9)
    F = SFaces()
    for k in range(-1, 7):
        s = 1100 * (2 ** z) / (2 ** k)
        if s < 10 or s > 4000:
            continue
        V, E = box_mesh(s, s, s)
        mesh3(g, cam, V, E, GOLD if k % 2 == 0 else INK, 2.4, clamp(s / 300), xf=xform((0, 0, 0), t * 0.3 * (k % 3 - 1), t * 0.4, 0))
    for i in range(300):
        th = hsh(i, 1) * 2 * math.pi
        rr = 200 + ((t * 600 + i * 40) % 2400)
        point3(g, cam, (rr * math.cos(th), rr * math.sin(th), 400 - ((t * 900 + i * 13) % 1800)), 4, GOLD if i % 5 == 0 else INK, 0.8)
    c, r, u = ahead(cam, 900)
    word3(g, cam, '\u2135\u2080', v_add(c, v_mul(cam.u, -150)), r, u, 500, 300, GOLD, 'serif', 0.5)
    word3(g, cam, 'P(DOOM) = ' + pd_str(t), v_add(c, v_mul(cam.u, 300)), r, u, 1300, 140, GOLD, 'monox', 1, x=True, depth=50, n=4)
    g.post = dict(glow=0.8)


def o_stack(g, t, lt):
    u = prog(t, ST[4], ST[5])
    top = 400 + (t - ST[4]) * 1800
    topple = eo(prog(t, 150.35, ST[5])) * 1.2
    keys = [(ST[4], (-1300, 0, -1600), (0, -300, 0), 55, 0.0),
            (ST[5], (-1700, -top * 0.9, -2200), (0, -top * 0.75, 0), 60, 0.08)]
    cam = cam_at(t, keys, shake=20 * (t > 150.35))
    env(g, cam)
    F = SFaces()
    n = int(top / 110) + 1
    for k in range(max(0, n - 40), n):
        y = 400 - k * 110
        h_ = -y + 400
        tilt = topple * (h_ / 3000) ** 1.5
        cx = math.sin(tilt) * h_ * 0.6
        F.sbox((cx, y - math.cos(tilt) * 0 , 0), (600, 90, 380), GOLD if k % 7 == 0 else (90 + 40 * hsh(k, 1),) * 3, None,
               xf=lambda v, tilt=tilt: rot3(v, 0, k * 0.0, tilt), amb=0.4)
    F.draw(g, cam, fog=7000)
    for k in range(max(0, n - 14), n):
        # v128: labels ride on their slab's front face (they used to stay put while the tower toppled)
        y = 400 - k * 110
        h_ = -y + 400
        tilt = topple * (h_ / 3000) ** 1.5
        cx = math.sin(tilt) * h_ * 0.6
        p = v_add((cx, y, 0), rot3((0, -10, -192), 0, 0, tilt))
        text3(g, cam, 'frame #%d  upgrade()' % k, p, 22, BG if k % 7 == 0 else INK, 'mono')
    c, r, uu = ahead(cam, 950)
    word3(g, cam, 'P(DOOM) = ' + pd_str(t), v_add(c, v_mul(cam.u, 320)), r, uu, 1500, 140, GOLD, 'monox', 1, x=True, depth=50, n=4)


def o_nan(g, t, lt):
    e = t - ST[5]
    yaw = e * 1.8
    cam = Cam3(orbit((0, 0, 0), 1700 + 400 * e, yaw, 0.2 * math.sin(e * 3)), (0, 0, 0), 58, e * 0.6)
    F = SFaces()
    for i in range(160):
        dirv = v_norm((hsh(i, 2) - 0.5, hsh(i, 3) - 0.5, hsh(i, 4) - 0.5))
        d = 300 + 2200 * eo(clamp(e / 1.6)) * (0.3 + hsh(i, 1))
        p = v_mul(dirv, d)
        rr = 70 + 90 * hsh(i, 5)
        a = e * 5 + i
        tri = [v_add(p, (rr * math.cos(a + q * 2.1), rr * math.sin(a * 1.3 + q * 2.1), rr * math.cos(a * 0.7 + q))) for q in range(3)]
        F.sq(tri, GOLD if i % 4 == 0 else (150, 150, 144), None, amb=0.4)
    F.draw(g, cam)
    _outro_text(g, cam, t, ((hsh(int(t * 30), 1) - 0.5) * 60, 0, 0), 300)
    g.hud = dict(a=1, dx=(hsh(int(t * 30), 4) - 0.5) * 24)
    g.post = dict(glow=0.9)
    if t > TC:
        _tv_off(g, t)


def _tv_off(g, t):
    cp = prog(t, TC, TC + 0.45)
    g.hud = dict(a=0)
    hud(g, t, a=1)
    g.d.flush()
    img = g.img
    sy = max(2, int(H * (1 - eo(prog(cp, 0, 0.6)))))
    sx = max(2, int(W * (1 - ei(prog(cp, 0.55, 1.0)))))
    squashed = img.resize((sx, sy), Image.BILINEAR)
    base = Image.new('RGB', (W, H), BG)
    base.paste(squashed, ((W - sx) // 2, (H - sy) // 2))
    g.img = base
    g.d = aggdraw.Draw(g.img)
    g.rect((W - sx) / 2 - 10, H / 2 - 2, (W + sx) / 2 + 10, H / 2 + 2, fill=GOLDL, a=clamp(cp * 2) * (1 - prog(t, TC + 0.4, TC + 0.5)))
    g.circle(W / 2, H / 2, 10 * (1 - cp) + 3, fill=GOLDL, a=1 - prog(t, TC + 0.42, TC + 0.62))


# ======================================================== END: regenerate -> rewind -> black
TE0 = TC + 0.65    # dark
TPR = 153.45       # prompt types
TBT = 153.95       # button appears
TCUR = 154.2       # cursor enters
TCLK = 155.0       # click
TRW0 = 155.15      # rewind starts
TRW1 = 156.35      # reached the first frame
TBLK = 156.5       # black


def regen_ui(g, t):
    g.hud = dict(a=0)
    s = '~/jnvhr% format complete'   # v127: no space before % (she asked)
    n = int(len(s) * clamp((t - TPR) / 0.4))
    if n > 0:
        g.text(s[:n], W / 2, H / 2 - 120, 40, DIM, 'mono', 1, 'mm')
    ba = eo(prog(t, TBT, TBT + 0.25))
    if ba <= 0:
        return
    hov = t > 154.75
    press = t > TCLK and t < TCLK + 0.12
    bw, bh = 420, 92
    cx, cy = W / 2, H / 2 + 20
    sc = 0.96 if press else 1.0
    x0, y0, x1, y1 = cx - bw / 2 * sc, cy - bh / 2 * sc, cx + bw / 2 * sc, cy + bh / 2 * sc
    g.rect(x0, y0, x1, y1, fill=GOLD if hov else (28, 28, 26), a=ba)
    g.rect(x0, y0, x1, y0 + 3, fill=GOLD, a=ba)
    g.rect(x0, y1 - 3, x1, y1, fill=GOLD, a=ba)
    g.rect(x0, y0, x0 + 3, y1, fill=GOLD, a=ba)
    g.rect(x1 - 3, y0, x1, y1, fill=GOLD, a=ba)
    tc = BG if hov else INK
    g.text('Regenerate', cx + 28, cy + 2, 40, tc, 'sans', ba, 'mm')
    ix, iy = cx - 140, cy
    arc = [(ix + 20 * math.cos(a), iy + 20 * math.sin(a)) for a in [math.radians(d) for d in range(-60, 250, 15)]]
    for p, q in zip(arc, arc[1:]):
        g.line((p[0], p[1], q[0], q[1]), tc, 5, ba)
    ex, ey = arc[0]
    g.poly([ex + 10, ey - 12, ex + 12, ey + 10, ex - 10, ey + 4], fill=tc, a=ba, fa=ba)
    # cursor
    if t > TCUR:
        u = eio(prog(t, TCUR, 154.8))
        px = lerp(W * 0.82, cx + 60, u); py = lerp(H * 0.9, cy + 14, u)
        if press:
            g.circle(px, py, 30 * (t - TCLK) / 0.12 + 10, fill=GOLDL, a=0.5)
        pts = [(0, 0), (0, 46), (12, 35), (21, 54), (29, 50), (20, 32), (36, 32)]
        flat = []
        for (a, b) in pts:
            flat += [px + a, py + b]
        g.poly(flat, fill=INK, stroke=BG, w=3, a=1, fa=1)


def s_end(g, t, lt):
    g.hud = dict(a=0)
    if t < TPR:
        return
    regen_ui(g, t)
    g.post = dict(glow=0.4, vig=1.0)


def s_black(g, t, lt):
    g.hud = dict(a=0)
    g.post = dict(glow=0.0, grain=0.0, vig=1.0)


TL = [
    (T0(32) - 0.01, s_fuse, BG),
    (105.92, s_ortho, BG),
    (110.12, s_gears, BG),
    (T0(36) - 0.08, s_dense, BG),   # v97: cut on the sung "P" of Post
    (T0(37) - 0.01, s_fences116, BG),
    (T0(38) - 0.01, s_gpu116, BG),
    (T0(39) - 0.01, s_rlhf, BG),
    (T0(40) - 0.01, type_scene(40), BG),
    (T0(41) - 0.01, s_prophecy116, BG),
    (T0(43) - 0.01, s_recursive124, BG),
    (T0(44) - 0.01, s_vault110, BG),
    (T0(45) - 0.01, s_puppet2, BG),
    # v115: o_explode is merged into s_puppet2 (show111.py): the bar's blast becomes the drop explosion in one shot
    (ST[1], o_globe, BG),
    (ST[2], o_inf, BG),
    (ST[3], o_aleph, BG),
    (ST[4], o_stack, BG),
    (ST[5], o_nan, BG),
    (TE0, s_end, BG),
    (TBLK, s_black, BG),
]
