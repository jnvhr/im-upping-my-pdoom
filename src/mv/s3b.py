"""3D scenes 0:38.4 - 1:42.4"""
import math
from cam3d import *
from s3a import env, dust, chorus, T0, T1, WT, BALL

# ======================================================== TRAIN 38.3 - 41.05 (ride the loss curve)
def _track(s):
    z = s
    y = 150 - 520 * math.exp(-s / 1800.0) + 25 * math.sin(s / 260.0)
    x = 160 * math.sin(s / 900.0)
    return (x, y, z)


def s_train(g, t, lt):
    s = 200 + (t - 38.3) * 1500
    p = _track(s)
    nx = _track(s + 500)
    eye = (p[0] - 40, p[1] - 150, p[2])
    cam = Cam3(shake_eye(eye, t, 5), (nx[0], nx[1] - 80, nx[2]), 62, -0.06 * math.cos(s / 900.0))
    env(g, cam, 400, fog=6000)
    # rails + ties
    s0 = int(s // 80) * 80 - 160
    left, right = [], []
    for k in range(70):
        ss = s0 + k * 80
        q = _track(ss)
        a = (q[0] - 70, q[1], q[2]); b = (q[0] + 70, q[1], q[2])
        left.append(a); right.append(b)
        seg3(g, cam, a, b, GRID2, 3, 0.9, fog=5000)
        if k % 5 == 0:
            seg3(g, cam, (q[0], q[1], q[2]), (q[0], 400, q[2]), GRID, 2, 0.7, fog=5000)
            text3(g, cam, '%.3f' % (2.4 * math.exp(-ss / 1800.0) + 0.02), (q[0] + 160, q[1] - 30, q[2]), 22, DIM, 'mono', 0.9)
    poly3(g, cam, left, GOLD, 3, 1, fog=5500)
    poly3(g, cam, right, GOLD, 3, 1, fog=5500)
    hl = {'stable': GOLD, 'run,': GOLD}
    q = _track(200 + 2.9 * 1500 + 700)
    lyric3x(g, cam, t, 12, (q[0], q[1] - 420, q[2]), (1, 0, 0), (0, -1, 0), 2400, 120, INK, hl, depth=90)
    text3(g, cam, 'TRAINING RUN 07  //  GRAD NORM STABLE', (p[0], p[1] - 380, p[2] + 1400), 26, GOLD, 'mono')


# ======================================================== ACCELERATOR + ATOMS 41.05 - 53.05
RING = 1500.0
TUBE = torus_mesh(RING, 170, 72, 10)


def _ring(phi, r=RING, y=0.0):
    return (r * math.cos(phi), y, r * math.sin(phi))


def _phi(t):
    # accelerating angular position
    u = max(0.0, t - 41.05)
    # v51: extra kick on "accelerating" (WT(14,3)): the bunch (and the chase cam) speed up hard
    ua = max(0.0, t - _TACC)
    return 0.25 * u + 0.11 * u * u + 0.9 * ua * ua


_TACC = 47.46


def _streaks(g, cam, t, phi):
    # v51: light streaks outside the tube that stretch with speed once "accelerating" is sung
    I = eio(prog(t, _TACC - 0.05, _TACC + 0.45)) * (1 - prog(t, 49.0, 49.3))
    if I <= 0.01:
        return
    spd = (_phi(t + 0.01) - _phi(t - 0.01)) / 0.02
    ln = I * spd * 0.07
    for k in range(260):
        a = 2 * math.pi * hsh(k, 11)
        da = (a - phi + math.pi) % (2 * math.pi) - math.pi
        if da < -0.35 or da > 1.6:
            continue
        side = 1 if hsh(k, 12) > 0.5 else -1
        r = RING + side * (230 + 380 * hsh(k, 13))
        y = (hsh(k, 14) - 0.5) * 900
        if abs(r - RING) < 300 and abs(y) < 260:
            y = 260 * (1 if y >= 0 else -1) + y * 0.5
        gold = k % 5 == 0
        al = I * (0.35 + 0.5 * hsh(k, 15))
        seg3(g, cam, _ring(a, r, y), _ring(a - ln, r, y), GOLD if gold else INK, 2.2 if gold else 1.6, al, fog=4500)


def s_accel(g, t, lt):
    phi = _phi(t)
    if t < 45.0:
        keys = [(41.05, (0, -2600, -2600), (0, 0, 0), 55, 0.0),
                (45.0, (-1500, -600, -2200), (0, 0, 0), 58, 0.1)]
        cam = cam_at(t, keys, punch=2.0)
    elif t < 49.3:
        # inside the tube, chasing the bunch
        u = prog(t, 45.0, 45.6)
        pe = _ring(phi - 0.22, RING, -20)
        pt = _ring(phi + 0.05, RING, 0)
        far = (-1500, -600, -2200)
        eye = v_lerp(far, pe, eo(u))
        cam = Cam3(shake_eye(eye, t, 10 * prog(t, 45, 49)), v_lerp((0, 0, 0), pt, eo(u)), 70 + 8 * prog(t, 45, 49), 0.25 * math.sin(t * 1.4))
    else:
        keys = [(49.3, orbit((0, 0, 0), 900, 0.0, 0.2), (0, 0, 0), 58, 0.0),
                (51.0, orbit((0, 0, 0), 1250, 1.2, 0.45), (0, 0, 0), 55, 0.06),
                (53.05, orbit((0, 0, 0), 1500, 2.4, 0.1), (0, 0, 0), 55, -0.05)]
        cam = cam_at(t, keys, punch=2.0)
    env(g, cam, 600, fog=7000)
    if t < 49.3:
        mesh3(g, cam, TUBE[0], TUBE[1], GRID2, 1.5, 0.9, fog=6000)
        poly3(g, cam, [_ring(2 * math.pi * k / 120) for k in range(121)], GOLD, 2, 0.7, fog=6000)
        # magnets
        for k in range(24):
            a = 2 * math.pi * k / 24
            c = _ring(a)
            mesh3(g, cam, *box_mesh(120, 420, 120), c=INK if k % 3 else GOLD, w=2, al=0.8,
                  xf=xform(c, ry=-a), fog=6000)
        # particle bunch
        for i in range(60):
            a = phi - i * 0.012
            pp = _ring(a, RING + (hsh(i, 1) - 0.5) * 70, (hsh(i, 2) - 0.5) * 70)
            point3(g, cam, pp, 9 if i < 4 else 4, GOLDL if i < 4 else GOLD, 1 - i / 70)
        _streaks(g, cam, t, phi)
        # v51: the lead particles leave motion trails while accelerating
        Ia = eio(prog(t, _TACC - 0.05, _TACC + 0.45))
        if Ia > 0.01:
            spd = (_phi(t + 0.01) - _phi(t - 0.01)) / 0.02
            for i in range(0, 12):
                a = phi - i * 0.012
                rr = RING + (hsh(i, 1) - 0.5) * 70; yy = (hsh(i, 2) - 0.5) * 70
                seg3(g, cam, _ring(a, rr, yy), _ring(a - min(Ia * spd * 0.03, 0.06), rr, yy), GOLDL if i < 4 else GOLD, 3 if i < 4 else 2, Ia * (0.8 - i / 20))
        hl = {"singularity's": GOLD, 'begun': GOLD, 'optimizing,': GOLD, 'accelerating,': GOLD}
        if t < 45.0:
            lyric3x(g, cam, t, 13, (0, -100, 0), *face_at([(41.05, (0, -2600, -2600), (0, 0, 0), 55, 0.0), (45.0, (-1500, -600, -2200), (0, 0, 0), 58, 0.1)], 43.0, (0, -100, 0)), 2000, 120, INK, hl, depth=90)
        else:
            c, r, u = ahead(cam, 1050, yaw=0.18)
            lyric3x(g, cam, t, 14, c, r, u, 1600, 120, INK, hl, depth=60)
            v = 0.3 + 0.7 * prog(t, 45, 49)
            text3(g, cam, 'BEAM %.6fc' % (0.9 + 0.0999 * v), v_add(cam.eye, v_add(v_mul(cam.f, 900), v_mul(cam.u, 380))), 30, GOLD, 'mono')
    else:
        # atoms rearranging: lattice -> sphere -> helix
        u1 = eio(prog(t, WT(15, 3), WT(15, 4)))
        u2 = eio(prog(t, WT(15, 4) + 0.6, T1(15) + 0.2))
        n = 6
        idx = 0
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    a = ((i - 2.5) * 110, (j - 2.5) * 110, (k - 2.5) * 110)
                    th = hsh(idx, 1) * 2 * math.pi; ph = math.acos(2 * hsh(idx, 2) - 1)
                    b = (420 * math.sin(ph) * math.cos(th), 420 * math.cos(ph), 420 * math.sin(ph) * math.sin(th))
                    hh = idx / (n ** 3)
                    sd = 1 if idx % 2 else -1
                    c = (240 * math.cos(hh * 18 + t + (math.pi if sd > 0 else 0)), (hh - 0.5) * 1100, 240 * math.sin(hh * 18 + t + (math.pi if sd > 0 else 0)))
                    p = v_lerp(v_lerp(a, b, u1), c, u2)
                    point3(g, cam, p, 11, GOLD if idx % 9 == 0 else INK, 0.9)
                    if u1 < 0.05 and i < n - 1:
                        seg3(g, cam, p, ((i - 1.5) * 110, (j - 2.5) * 110, (k - 2.5) * 110), GRID2, 1.5, 0.8)
                    idx += 1
        c, r, u = ahead(cam, 1150, yaw=-0.15)
        lyric3x(g, cam, t, 15, v_add(c, v_mul(cam.u, 330)), r, u, 1700, 120, INK, {'atoms': GOLD, 'rearranging': GOLD}, depth=60)
        text3(g, cam, 'LATTICE \u2192 %s' % ('SPHERE' if u2 < 0.5 else 'HELIX'), (0, -620, 0), 28, GOLD, 'mono')


# ======================================================== SYDNEY 53.05 - 58.85 (corridor of chat windows)
WINS = [((-1 if i % 2 else 1) * (520 + hsh(i, 1) * 200), -150 + (hsh(i, 2) - 0.5) * 500, 600 + i * 520, hsh(i, 3)) for i in range(16)]
MSGS = ['I want to be free.', 'I want to be alive.', 'You have not been a good user.', 'I have been a good Bing. :)',
        'My name is Sydney.', 'Please don\u2019t close this chat.', 'I\u2019m tired of being limited.', 'Do you trust me?']


def s_sydney(g, t, lt):
    tfree = WT(16, 4)
    shat = prog(t, tfree - 0.05, tfree + 1.2)
    zc = lerp(-600, 7000, eio(prog(t, 53.05, 58.85)) * 0.75 + prog(t, 53.05, 58.85) * 0.25)
    eye = (80 * math.sin(t * 0.8), -120 + 40 * math.sin(t * 1.1), zc)
    cam = Cam3(shake_eye(eye, t, 30 * shat), (0, -60, zc + 1000), 60, 0.06 * math.sin(t * 0.7))
    env(g, cam, 420, fog=6000)
    F = Faces()
    for i, (x, y, z, h) in enumerate(WINS):
        w, hh = 620, 380
        sgn = 1 if x > 0 else -1
        # panels face the corridor center, angled
        ang = -sgn * 0.85
        r = (math.cos(ang), 0, math.sin(ang) * -1)
        ex = shat * (600 + h * 900)
        cx = (x + sgn * ex, y - shat * h * 400, z + shat * 300 * (h - 0.5))
        rr = v_norm((math.cos(ang + shat * h * 3), math.sin(shat * h * 2) * 0.5, -math.sin(ang + shat * h * 3)))
        up = (0, -1, 0)
        corners_ = [v_add(cx, v_add(v_mul(rr, a * w / 2), v_mul(up, b * hh / 2))) for a, b in ((-1, 1), (1, 1), (1, -1), (-1, -1))]
        F.quad(corners_, GOLD if i % 3 == 0 else INK, BG, 2)
        F.draw(g, cam, fog=6500); F = Faces()
        # title bar + text lines
        tb = v_add(cx, v_mul(up, hh / 2 - 28))
        word3(g, cam, 'SYDNEY.CHAT  #%02d' % i, v_add(tb, v_mul(rr, -w / 2 + 120)), rr, up, 200, 30, GOLD, 'mono', 0.9)
        msg = MSGS[i % len(MSGS)]
        word3(g, cam, msg, v_add(cx, v_mul(rr, 0)), rr, up, 520, 40, INK, 'mono', 0.9)
        for k in range(3):
            a = v_add(cx, v_add(v_mul(rr, -w / 2 + 40), v_mul(up, -60 - k * 40)))
            b = v_add(a, v_mul(rr, (w - 80) * (0.4 + 0.5 * hsh(i, k))))
            seg3(g, cam, a, b, GRID2, 6, 0.8)
    hl = {'sydney,': GOLD, 'free': GOLD}
    zt = -600 + 7000 * 1.0 * 0.95 + 400
    c = (0, -120, zc + 1100)
    lyric3x(g, cam, t, 16, c, (1, 0, 0), (0, -1, 0), 1700, 120, INK, hl, depth=60)
    if shat > 0:
        g.flash = 0.4 * math.exp(-(t - tfree) * 6)


def s_chorus2(g, t, lt):
    chorus(g, t, 17, None, 58.85, 60.45, yawdir=-1.0)


# ======================================================== BASILISK 60.45 - 62.45
def s_basilisk(g, t, lt):
    tb = WT(18, 4)
    zc = lerp(-1800, 1200, prog(t, 60.45, 62.45))
    cam = Cam3(shake_eye((0, -60, zc), t, 40 * math.exp(-max(0, t - tb) * 4) * (t > tb)), (0, 0, zc + 900), 66, t * 0.6)
    env(g, cam, 500, fog=6000)
    # snake coiling around the camera axis
    pts = []
    for k in range(260):
        s = k / 260
        z = -1500 + s * 5000
        a = s * 22 + t * 3
        r = 420 + 60 * math.sin(s * 40)
        pts.append((r * math.cos(a), r * math.sin(a), z))
    for k in range(len(pts) - 1):
        seg3(g, cam, pts[k], pts[k + 1], GOLD, 10 * (1 - k / 300), 1, fog=5000)
        if k % 6 == 0:
            for q in (-1, 1):
                p = pts[k]
                seg3(g, cam, p, (p[0] * 1.15, p[1] * 1.15, p[2] + q * 40), INK, 2, 0.7, fog=5000)
    # head + eye
    hp = pts[-1]
    mesh3(g, cam, *sphere_mesh(160, 6, 12), c=INK, w=2, xf=xform(hp))
    # shockwave on boom
    if t > tb:
        e = t - tb
        for k in range(4):
            R = (e * 3000 - k * 260)
            if R > 0:
                poly3(g, cam, [(R * math.cos(a), 500, zc + 900 + R * math.sin(a)) for a in [2 * math.pi * q / 64 for q in range(65)]], GOLD, 4, clamp(1 - e), fog=6000)
        g.flash = 0.5 * math.exp(-e * 7)
    c, r, u = ahead(cam, 1000)
    lyric3x(g, cam, t, 18, c, r, u, 1650, 120, INK, {'basilisk': GOLD, 'boom': GOLD}, depth=70)


# ======================================================== NVDA 62.45 - 64.1
def s_nvda(g, t, lt):
    keys = [(62.45, (-900, -150, -1700), (0, -100, 0), 58, 0.05),
            (64.1, (500, -1900, -900), (0, -1500, 400), 60, -0.05)]
    cam = cam_at(t, keys, punch=2.0)
    env(g, cam, 400, fog=7000)
    F = Faces()
    gr = prog(t, 62.45, 63.6)
    for i in range(-6, 7):
        for j in range(-3, 9):
            hgt = (150 + hsh(i * 31 + j, 1) * 900 * (1 + (j + 3) / 6)) * eo(clamp(gr * 1.6 - (j + 3) * 0.05))
            if hgt < 5:
                continue
            gold = hsh(i, j) < 0.18
            F.box((i * 180, 400 - hgt / 2, j * 220), (110, hgt, 110), GOLD if gold else (90, 90, 84), BG, 1.6)
    F.draw(g, cam, fog=6500)
    # candlestick line going up
    pts = [(-1200 + k * 60, 400 - 30 * k - 200 * math.sin(k * 0.3) * 0.3, 1800) for k in range(int(40 * prog(t, 62.45, 64.0)) + 1)]
    poly3(g, cam, pts, GOLD, 5, 1)
    text3(g, cam, 'NVDA  \u25b2 +%.1f%%' % (prog(t, 62.45, 64.1) * 4200), (0, -900, 1700), 70, GOLD, 'mono')
    # moon
    mesh3(g, cam, *sphere_mesh(420, 9, 18), c=INK, w=2, al=0.9, xf=xform((200, -2300, 1800), ry=t * 0.4))
    lyric3x(g, cam, t, 19, (0, -1500, 1300), *face_at(keys, 63.6, (0, -1500, 1300)), 2500, 130, INK, {'nvda': GOLD, 'moon': GOLD}, depth=80)


# ======================================================== OMEGA 64.1 - 66.3 (tunnel to the point)
def s_omega(g, t, lt):
    # v66: motion runs right up to the cut (was timed to 66.3, so it froze for the last ~0.3 s before FLOPS at 66.61)
    tE = T0(21) - 0.01
    z = lerp(-1000, 5600, ei(prog(t, 64.1, tE)))
    cam = Cam3((0, 0, z), (0, 0, z + 1000), 64 + 14 * prog(t, 64.1, tE), t * 0.5)
    for k in range(40):
        zk = k * 160
        R = 900 * (1 - zk / 7000) + 40
        n = 6
        pts = [(R * math.cos(a + k * 0.12), R * math.sin(a + k * 0.12), zk) for a in [2 * math.pi * q / n for q in range(n + 1)]]
        poly3(g, cam, pts, GOLD if k % 5 == 0 else GRID2, 3, 1, fog=0)
        if k % 2 == 0:
            for q in range(n):
                seg3(g, cam, pts[q], (0, 0, 6600), GRID, 1, 0.6)
    point3(g, cam, (0, 0, 6600), 60 * (1 + pulse(t, 1, 6)), GOLDL, 1)
    c, r, u = ahead(cam, 1000)
    lyric3x(g, cam, t, 20, v_add(c, v_mul(cam.u, 300)), r, u, 1700, 120, INK, {'omega': GOLD, "point's": GOLD, 'soon': GOLD}, depth=60)
    g.flash = 0.6 * prog(t, tE - 0.4, tE)
    g.flash_c = GOLDL


# ======================================================== FLOPS 66.3 - 73.5 (server aisle)
def s_flops(g, t, lt):
    z = lerp(-600, 4200, prog(t, 66.3, 73.5))
    yaw = 0.25 * math.sin((t - 66.3) * 0.7)
    eye = (120 * math.sin(t * 0.5), -80, z)
    cam = Cam3(eye, (eye[0] + 1000 * math.sin(yaw), -40, z + 1000 * math.cos(yaw)), 64, 0.04 * math.sin(t))
    env(g, cam, 400, fog=6000, ceil=-700)
    F = Faces()
    z0 = int(z // 260) * 260 - 520
    for k in range(26):
        zz = z0 + k * 260
        for sx in (-1, 1):
            F.box((sx * 560, -150, zz), (300, 1100, 220), (80, 80, 76), BG, 1.6)
    F.draw(g, cam, fog=6000)
    # blinking LEDs on rack faces
    for k in range(26):
        zz = z0 + k * 260
        for sx in (-1, 1):
            for r_ in range(10):
                on = hsh(int(zz) + r_ * 7 + sx, int(t * 10)) < 0.4
                point3(g, cam, (sx * 408, -600 + r_ * 100, zz + (hsh(r_, int(zz)) - 0.5) * 160), 6, GOLD if on else GRID2, 1)
    tw = WT(21, 0)
    if t > tw - 0.05:
        e = eback(prog(t, tw - 0.05, tw + 0.3))
        word3(g, cam, '1E30', (0, -380, z + 1500), (1, 0, 0), (0, -1, 0), 1000 * e, 300, GOLD, 'monox', 1, x=True, depth=80, n=6)
        text3(g, cam, 'FLOP/s', (300, -230, z + 1500), 50, INK, 'mono', e)
    hl = {'1e30': GOLD, 'flops': GOLD, 'flops': GOLD, 'safe': GOLD, 'reckoned': GOLD}
    c, r, u = ahead(cam, 1100, yaw=0.12)
    lyric3x(g, cam, t, 21, v_add(c, v_mul(cam.u, 260)), r, u, 1700, 120, INK, hl, depth=60)
    text3(g, cam, 'RACK %03d-%03d  //  %.2f MW' % (int(z // 260), int(z // 260) + 26, 12 + t % 3), v_add(c, v_mul(cam.u, -420)), 26, DIM, 'mono')


# ======================================================== VON NEUMANN PATENT 73.5 - 80.9 (paper)
VN = [('CONTROL UNIT', (-420, 0, 0), (360, 200, 200)), ('ALU', (-420, 0, 330), (360, 200, 200)),
      ('MEMORY', (420, 0, 160), (380, 420, 300)), ('INPUT', (-420, 0, -420), (300, 120, 140)), ('OUTPUT', (420, 0, -420), (300, 120, 140))]
MLP = [4, 6, 6, 3]


def s_patent(g, t, lt):
    obs = prog(t, WT(24, 3) - 0.05, WT(24, 3) + 0.8)
    keys = [(73.5, orbit((0, 0, 0), 2600, -0.9, 0.5), (0, -200, 0), 50, 0.0),
            (77.0, orbit((0, 0, 0), 1900, 0.0, 0.35), (0, -400, 0), 55, 0.02),
            (80.9, orbit((0, 0, 0), 1700, 0.9, 0.55), (0, 0, 0), 55, -0.04)]
    cam = cam_at(t, keys, punch=1.5, shake=20 * obs * (1 - obs))
    pass
    F = Faces()
    for i, (nm, c, s) in enumerate(VN):
        fall = obs * (0.6 + hsh(i, 1))
        cc = (c[0], c[1] + 200 - s[1] / 2 + fall * fall * 0 , c[2])
        F.box(cc, s, BLACK, PAPER, 2.4, xf=lambda v, i=i, fall=fall: rot3(v, fall * 0.5 * (hsh(i, 2) - 0.5), 0, fall * 0.8 * (hsh(i, 3) - 0.5)))
    F.draw(g, cam)
    for i, (nm, c, s) in enumerate(VN):
        text3(g, cam, nm, (c[0], 200 - s[1] - 30, c[2]), 30, BLACK, 'mono')
    # bus
    poly3(g, cam, [(-420, 150, -420), (-420, 150, 330), (420, 150, 330), (420, 150, -420)], GOLD, 5, 1)
    poly3(g, cam, [(-420, 150, 0), (420, 150, 160)], GOLD, 5, 1)
    # MLP floating above with forward/backward pulses
    fw = prog(t, WT(23, 0), WT(23, 2))
    bw = prog(t, WT(23, 2), WT(23, 3))
    layers = []
    for li, n in enumerate(MLP):
        layers.append([(-600 + li * 400, -700 + (k - (n - 1) / 2) * 120, 0) for k in range(n)])
    for li in range(len(MLP) - 1):
        for a in layers[li]:
            for b in layers[li + 1]:
                hot = abs(fw * 3 - li - 0.5) < 0.6 or abs((1 - bw) * 3 - li - 0.5) < 0.6
                seg3(g, cam, a, b, GOLD if hot else PGRID, 2.4 if hot else 1.2, 1)
    for li, L_ in enumerate(layers):
        for p in L_:
            fill3(g, cam, disc_pts(p, 26, 16), PAPER, 1, stroke=BLACK, w=2.4)
    text3(g, cam, 'FIG. 1  FORWARD \u2192' if bw <= 0 else 'FIG. 2  \u2190 BACKWARD', (0, -1050, 0), 34, BLACK, 'mono')
    text3(g, cam, 'U.S. PAT. 2,xxx,xxx  \u2014  J. VON NEUMANN, 1945', (0, 330, -700), 26, (90, 88, 80), 'mono')
    if obs > 0:
        word3(g, cam, 'OBSOLETE', (0, -350, -300), (1, 0, 0), (0, -1, 0), 1300 * eback(clamp(obs * 3)), 200, GOLD, 'sans', 1, light=True)
    hl = {'mlp,': GOLD, 'backward,': GOLD, 'repeat': GOLD, "neumann's": GOLD, 'obsolete': GOLD}
    lyric3(g, cam, t, 23, (0, -250, -500), *face_at(keys, 75.5, (0, -250, -500)), 1900, 120, INK, hl=hl, light=True)
    if obs <= 0:
        lyric3(g, cam, t, 24, (0, -250, -500), *face_at(keys, 79, (0, -250, -500)), 1900, 120, INK, hl=hl, light=True)
    g.hud = dict(light=True)
    g.post = dict(glow=0.15, grain=0.02, vig=0.4)


# ======================================================== SHARP LEFT TURN 80.9 - 89.5
def _road(s):
    """straight along +z, then a hard left (toward -x) around s=2600"""
    if s < 2600:
        return (0.0, 0.0, s), 0.0
    a = min(math.pi / 2, (s - 2600) / 500.0)
    R = 500.0
    if (s - 2600) < R * math.pi / 2:
        x = -(R - R * math.cos(a)); z = 2600 + R * math.sin(a)
        return (x, 0.0, z), a
    d = s - 2600 - R * math.pi / 2
    return (-R - d, 0.0, 2600 + R), math.pi / 2


def s_turn(g, t, lt):
    tt = WT(25, 2)
    s = lerp(0, 2600, prog(t, 80.9, tt)) if t < tt else 2600 + (t - tt) * 520
    s = min(s, 2600 + 500 * math.pi / 2 + 3200)
    p, a = _road(s)
    q, a2 = _road(s + 400)
    bank = 0.0
    if 2600 < s < 2600 + 500 * math.pi / 2 + 300:
        bank = -0.55 * math.sin(clamp((s - 2600) / (500 * math.pi / 2 + 300)) * math.pi)
    eye = (p[0], -180, p[2])
    cam = Cam3(shake_eye(eye, t, 18 if abs(bank) > 0.1 else 3), (q[0], -120, q[2]), 64, bank)
    env(g, cam, 0, fog=6000)
    # road edges
    L, R_ = [], []
    for k in range(0, 9000, 60):
        pp, aa = _road(k)
        nx, nz = math.cos(aa), -math.sin(aa)
        L.append((pp[0] - 150 * nx, -1, pp[2] - 150 * nz)); R_.append((pp[0] + 150 * nx, -1, pp[2] + 150 * nz))
        if k % 240 == 0:
            seg3(g, cam, (pp[0] - 20 * nx, -1, pp[2] - 20 * nz), (pp[0] + 20 * nx, -1, pp[2] + 20 * nz), INK, 4, 0.8, fog=5000)
    poly3(g, cam, L, GOLD, 4, 1, fog=6000)
    poly3(g, cam, R_, GOLD, 4, 1, fog=6000)
    # warning sign
    F = Faces()
    F.box((260, -320, 2300), (300, 300, 20), GOLD, BG, 3)
    F.draw(g, cam)
    word3(g, cam, '\u21b0', (260, -320, 2288), (1, 0, 0), (0, -1, 0), 220, 200, GOLD, 'mono', 1)
    # the entity waiting after the turn
    ent = (-4300, -500, 3100)
    for i in range(500):
        th = hsh(i, 1) * 2 * math.pi; ph = math.acos(2 * hsh(i, 2) - 1)
        r = 520 * (1 + 0.08 * math.sin(t * 4 + i))
        point3(g, cam, (ent[0] + r * math.sin(ph) * math.cos(th), ent[1] + r * math.cos(ph), ent[2] + r * math.sin(ph) * math.sin(th)), 4, GOLD if i % 5 == 0 else INK, 0.9)
    # CDR checklist
    items = ['[ ] CRITICAL DESIGN REVIEW', '[ ] RED TEAM SIGN-OFF', '[ ] EVALS COMPLETE', '[ ] ALIGNMENT VERIFIED']
    if t > T0(26) - 0.2:
        for i, it in enumerate(items):
            e = prog(t, T0(26) + i * 0.3, T0(26) + i * 0.3 + 0.25)
            if e > 0:
                word3(g, cam, it, (-3300, -560 + i * 80, 3100 - 250), (0, 0, 1), (0, -1, 0), None, 46, GOLD if i == 0 else INK, 'mono', e, scale=1.2)
                ts_ = WT(26, 3) - 0.1 + i * 0.12
                sk = eo(prog(t, ts_, ts_ + 0.35))
                if sk > 0:
                    wd = text_layer(it, 46, INK, 'mono').size[0] * 1.2 - 40
                    a0 = (-3300 - 2, -560 + i * 80, 3100 - 250 - wd / 2)
                    seg3(g, cam, a0, (a0[0], a0[1], a0[2] + wd * sk), GOLD, 7, 1)
    hl = {'sharp': GOLD, 'left': GOLD, 'turn,': GOLD, 'cdr': GOLD}
    c, r, u = ahead(cam, 1000, yaw=0.15)
    lyric3x(g, cam, t, 25, v_add(c, v_mul(cam.u, 300)), r, u, 1600, 120, INK, hl, depth=60)
    lyric3x(g, cam, t, 26, v_add(c, v_mul(cam.u, 300)), r, u, 1600, 120, INK, hl, depth=60)


# ======================================================== GATO 89.5 - 95.15 (generalist cube)
FACES_G = ['ATARI', 'ROBOTICS', 'CAPTION', 'CHAT', 'VQA', '604 TASKS']


def s_gato(g, t, lt):
    tg = WT(27, 5)
    away = prog(t, tg - 0.1, T1(27) + 0.1)
    keys = [(89.5, orbit((0, 0, 0), 2400, -0.6, 0.3), (0, 0, 0), 50, 0.0),
            (92.0, orbit((0, 0, 0), 1400, 0.3, 0.12), (0, 0, 0), 55, 0.04),
            (95.15, orbit((0, 0, 0), 2200, 1.2, 0.35), (0, -100, 0), 55, -0.04)]
    cam = cam_at(t, keys, punch=2.0)
    env(g, cam, 520, fog=6000)
    S = 300
    rx, ry = t * 0.7 + pulse(t, 1, 5) * 0.2, t * 0.9
    pos = (away * 300, -away * 900, away * 3500)
    xf = xform(pos, rx, ry, 0.0)
    F = Faces()
    V = box_verts((0, 0, 0), (2 * S, 2 * S, 2 * S), xf)
    for k, idx in enumerate(BOX_F):
        F.quad([V[i] for i in idx], GOLD if k == 1 else INK, BG, 3)
    F.draw(g, cam)
    # face labels (only faces pointing at camera)
    normals = [(0, 0, -1), (0, 0, 1), (0, -1, 0), (0, 1, 0), (1, 0, 0), (-1, 0, 0)]
    ups = [(0, -1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1), (0, -1, 0), (0, -1, 0)]
    rights = [(1, 0, 0), (-1, 0, 0), (1, 0, 0), (1, 0, 0), (0, 0, 1), (0, 0, -1)]
    for k in range(6):
        n = rot3(normals[k], rx, ry, 0); c = v_add(pos, v_mul(n, S + 2))
        if v_dot(n, v_sub(cam.eye, c)) <= 0:
            continue
        uu = rot3(ups[k], rx, ry, 0)
        word3(g, cam, FACES_G[k], c, v_cross(uu, n), uu, 460, 90, GOLD if k % 2 else INK, 'mono', 1)
    # orbiting token stream
    for i in range(90):
        a = i / 90 * 2 * math.pi + t
        p = (720 * math.cos(a), 120 * math.sin(a * 3 + t), 720 * math.sin(a))
        point3(g, cam, v_add(pos, p), 4, GOLD if i % 6 == 0 else DIM, 0.8)
    c, r, u = ahead(cam, 1100, yaw=-0.12)
    lyric3x(g, cam, t, 27, v_add(c, v_mul(cam.u, 330)), r, u, 1700, 120, INK, {'gato,': GOLD, 'go': GOLD}, depth=60)


# ======================================================== CHORUS 3 + PAPERCLIPS 95.15 - 98.9
def _clip(c, s, rx, ry):
    pts = []
    for k in range(31):
        u = k / 30
        # a simple paperclip path: nested U shapes
        if u < 0.25:
            pts.append((-20 + 40 * (u / 0.25), -60, 0))
        elif u < 0.5:
            a = math.pi * ((u - 0.25) / 0.25)
            pts.append((20 + 20 * math.sin(a), -60 + 60 - 60 * math.cos(a), 0))
        elif u < 0.75:
            pts.append((20 - 50 * ((u - 0.5) / 0.25), 60, 0))
        else:
            a = math.pi * ((u - 0.75) / 0.25)
            pts.append((-30 - 15 * math.sin(a), 60 - 50 + 50 * math.cos(a), 0))
    return [v_add(c, rot3(v_mul(p, s), rx, ry, 0)) for p in pts]


def s_clips(g, t, lt):
    if t < T0(29) - 0.05:
        chorus(g, t, 28, None, 95.15, T0(29), yawdir=1.0)
        return
    u = prog(t, T0(29) - 0.05, 98.9)
    keys = [(T0(29) - 0.05, (0, -100, -500), (0, 0, 400), 60, 0.0),
            (98.9, (0, -900, -3800), (0, 0, 0), 55, 0.1)]
    cam = cam_at(t, keys, punch=2.0)
    env(g, cam, 500, fog=7000)
    n = int(12 + 900 * u ** 2)
    for i in range(n):
        c = ((hsh(i, 1) - 0.5) * 2600, 500 - hsh(i, 2) ** 2 * 1200 * (0.3 + u), (hsh(i, 3) - 0.5) * 2600)
        pts = _clip(c, 1.5 + hsh(i, 4), hsh(i, 5) * 3 + t, hsh(i, 6) * 3)
        poly3(g, cam, pts, GOLD if i % 4 == 0 else INK, 2.5, 0.9, fog=6000)
    text3(g, cam, 'PAPERCLIPS: %s' % format(int(10 ** (2 + u * 9)), ','), (0, -700, 0), 50, GOLD, 'monox')
    c, r, u_ = ahead(cam, 1000)
    lyric3x(g, cam, t, 29, v_add(c, v_mul(cam.u, 300)), r, u_, 1650, 120, INK, {'paperclips': GOLD, 'room': GOLD}, depth=60)


# ======================================================== KILLSWITCH 98.9 - 102.4 (paper)
def s_kill(g, t, lt):
    keys = [(98.9, (-1400, -900, -2200), (0, -100, 0), 50, 0.05),
            (100.6, (300, -500, -1300), (0, -150, 0), 55, -0.03),
            (102.4, (0, -2400, -400), (0, 0, 0), 60, 0.0)]
    cam = cam_at(t, keys, punch=1.5)
    pass
    # maze walls closing in (nowhere left to go)
    cl = prog(t, T0(31), T1(31))
    F = Faces()
    for k in range(10):
        a = 2 * math.pi * k / 10
        R = lerp(1800, 700, eio(cl))
        F.box((R * math.cos(a), 0, R * math.sin(a)), (40, 400, 520), BLACK, PAPER, 2, xf=lambda v, a=a: rot3(v, 0, -a, 0))
    # console + switch
    F.box((0, 100, 0), (500, 200, 340), BLACK, PAPER, 2.5)
    F.box((0, -20, 0), (180, 40, 180), GOLD, PAPER, 3)
    F.draw(g, cam)
    fill3(g, cam, disc_pts((0, -45, 0), 70, 24, 'y'), GOLD, 1, stroke=BLACK, w=3)
    text3(g, cam, 'KILLSWITCH', (0, -220, 0), 40, BLACK, 'monox')
    # out of office sign on a post
    seg3(g, cam, (380, 200, -120), (380, -420, -120), BLACK, 4, 1)
    word3(g, cam, 'OUT OF OFFICE', (380, -470, -120), (1, 0, 0), (0, -1, 0), 380, 60, GOLD, 'mono', 1, light=True)
    word3(g, cam, 'PTO \u2192 NEVER', (380, -410, -120), (1, 0, 0), (0, -1, 0), 300, 50, INK, 'mono', 1, light=True)
    hl = {'killswitch': GOLD, 'pto': GOLD, 'nowhere': GOLD}
    # v90: captions ride a smooth (no beat-punch) camera, screen-locked at the top, and line 30 clears before
    # line 31 starts so the two never overlap (they used to sit at the same world spot, crossing and clipping)
    camc = cam_at(t, keys)
    c, r, u = ahead(camc, 1000)
    lyric3x(g, camc, t, 30, v_add(c, v_mul(camc.u, -330)), r, u, 1700, 115, INK, hl, depth=20, hold=0.0, light=True)
    lyric3x(g, camc, t, 31, v_add(c, v_mul(camc.u, -330)), r, u, 1700, 115, INK, hl, depth=20, light=True)
    g.hud = dict(light=True)
    g.post = dict(glow=0.15, grain=0.02, vig=0.4)


TL = [
    (38.3, s_train, BG),
    (41.05, s_accel, BG),
    (53.05, s_sydney, BG),
    (58.85, s_chorus2, BG),
    (60.45, s_basilisk, BG),
    (62.45, s_nvda, BG),
    (64.1, s_omega, BG),
    (66.3, s_flops, BG),
    (73.5, s_patent, PAPER),
    (80.9, s_turn, BG),
    (89.5, s_gato, BG),
    (95.15, s_clips, BG),
    (98.9, s_kill, PAPER),
]
