"""Scenes 1:42 - end"""
import math
import numpy as np
import aggdraw
from PIL import Image
from kit import *
from scenes_b import chorus


# ======================================================== FUSE 102.45 - 105.35
PAPERS = ['arXiv:1706.03762', 'arXiv:2203.15556', 'arXiv:2001.08361', 'SCALING LAWS', 'ATTENTION IS ALL', 'CONCRETE PROBLEMS']


def s_fuse(g, t, lt):
    grid(g, 60)
    cam = Cam(cx=W / 2 - 200, cy=H / 2 + 20, f=1000, dist=1300, rx=0.35, ry=0.5 + math.sin(t * 0.7) * 0.2, rz=-0.15)
    for k in range(3):
        V, E = cyl_mesh(85, 620, 20, 5, axis='x')
        V = [(x, y + (k - 1) * 175, z) for x, y, z in V]
        draw_edges(g, cam, V, E, c=INK if k != 1 else GOLD, w=1.8)
        for j in range(5):
            x0 = -260 + j * 120
            p = cam.p(x0, (k - 1) * 175, -86)
            g.text(PAPERS[(k * 5 + j) % len(PAPERS)], p[0], p[1], 13 * p[2] * 1.3, DIM if k != 1 else GOLD, 'monor', 0.9, 'mm', rot=-0.15)
    # band
    for xb in (-200, 200):
        pts = []
        for i in range(25):
            a = 2 * math.pi * i / 24
            pts += list(cam.p(xb, 270 * math.cos(a) * 0.95, 100 * math.sin(a))[:2])
        g.line(pts, GOLD, 3)
    # wick
    wick = []
    for i in range(40):
        u = i / 39
        wick.append((310 + u * 600, -40 - math.sin(u * 3.5) * 160, 0))
    burn = prog(t, 102.6, 105.3)
    nb = int((1 - burn) * 39)
    pts = []
    for (x, y, z) in wick[:nb + 1]:
        pts += list(cam.p(x, y, z)[:2])
    if len(pts) >= 4:
        g.line(pts, GOLDD, 4)
    ex, ey, _ = cam.p(*wick[nb])
    for i in range(40):
        a = hsh(i, int(t * 30)) * 6.28
        d = hsh(i, int(t * 30) + 7) * 70
        g.line((ex, ey, ex + math.cos(a) * d, ey + math.sin(a) * d), GOLD if i % 3 else GOLDL, 2, 0.9)
    g.circle(ex, ey, 14 + 8 * pulse(t, 4, 5), fill=GOLDL)
    tag(g, 90, 110, 'DYNAMITE.PDF // RESEARCH_STACK', size=17)
    g.text('FUSE_REMAINING: %.2fs' % max(0, 105.3 - t), 92, 170, 18, GOLD, 'mono', 1, 'lm')
    kinetic_line(g, t, 32, 960, 84, hl={'fuse': GOLD, 'late': GOLD})
    g.hud = dict(a=1)


# ======================================================== ORTHOGONALITY 105.35 - 109.35
def s_ortho(g, t, lt):
    grid(g, 60)
    cam = Cam(cx=W / 2, cy=H / 2 - 60, f=1000, dist=1300, rx=0.4 + 0.1 * math.sin(t * 0.5), ry=t * 0.35)
    L = 700
    ax1 = [(-L, 0, -60), (L, 0, -60)]
    ax2 = [(0, -L * 0.6, 60), (0, L * 0.6, 60)]
    for (a, b), lab, c in ((ax1, 'AXIS X: SUPERINTELLIGENCE', GOLD), (ax2, 'AXIS Y: HUMAN VALUES', INK)):
        p0 = cam.p(*a); p1 = cam.p(*b)
        g.line((p0[0], p0[1], p1[0], p1[1]), c, 10, 0.15)
        g.line((p0[0], p0[1], p1[0], p1[1]), c, 3)
        g.text(lab, p1[0] + 12, p1[1] - 14, 17, c, 'mono', 1, 'lm')
    # the gap between them
    q0 = cam.p(0, 0, -60); q1 = cam.p(0, 0, 60)
    g.line((q0[0], q0[1], q1[0], q1[1]), DIM, 1)
    g.circle(q0[0], q0[1], 6, stroke=GOLD, w=2); g.circle(q1[0], q1[1], 6, stroke=INK, w=2)
    g.text('\u0394 = 120 units', q1[0] + 16, q1[1] + 20, 14, DIM, 'monor', 1, 'lm')
    readout(g, 92, 170, [('DOT(X,Y)', '0.000'), ('INTERSECTION', 'NULL'), ('ANGLE', '90.00\u00b0')], size=15)
    tag(g, 90, 110, 'ORTHOGONALITY_THESIS // PROOF', size=17)
    # melancholic analyzer
    g.rect(470, 730, 1450, 900, stroke=GRID2, w=1.5)
    spectrum(g, 490, 890, 940, 140, t, n=64, melan=True, gap=0.45)
    pts = []
    for i in range(121):
        u = i / 120
        pts += [490 + u * 940, 790 + math.sin(u * 14 - t * 2.2) * 26 * math.sin(u * 3.14) * (0.6 + feat('rms', t) * 0.4)]
    g.line(pts, GOLDL, 2)
    g.text('ORTHOGONALITY_BLUES.wav', 480, 712, 15, GOLD, 'mono', 1, 'lm')
    kinetic_line(g, t, 33, 990, 74, font='serif', upper=False, style='fade')
    g.hud = dict(a=1)


# ======================================================== GEARS 109.35 - 115.45
def _gear(g, cam, cx, cy, R, teeth, ang, c, w=2, a=1.0):
    pts = []
    n = teeth * 4
    for i in range(n + 1):
        k = i % 4
        th = ang + 2 * math.pi * (i // 4 + [0, 0.2, 0.5, 0.7][k]) / teeth
        r = R if k in (1, 2) else R * 0.84
        pts += list(cam.p(cx + r * math.cos(th), cy + r * math.sin(th), 0)[:2])
    g.line(pts, c, w, a)
    hub = []
    for i in range(25):
        th = ang + 2 * math.pi * i / 24
        hub += list(cam.p(cx + R * 0.3 * math.cos(th), cy + R * 0.3 * math.sin(th), 0)[:2])
    g.line(hub, c, w, a)
    for s in range(4):
        th = ang + s * math.pi / 2
        p0 = cam.p(cx + R * 0.3 * math.cos(th), cy + R * 0.3 * math.sin(th), 0)
        p1 = cam.p(cx + R * 0.8 * math.cos(th), cy + R * 0.8 * math.sin(th), 0)
        g.line((p0[0], p0[1], p1[0], p1[1]), c, w, a)


def s_gears(g, t, lt):
    grid(g, 60)
    td = word_time(35, 4)  # disobey
    broke = t > td
    q = t - td
    cam = Cam(cx=W / 2, cy=H / 2 + 40, f=1000, dist=1300, rx=0.55, ry=-0.25 + 0.05 * math.sin(t))
    sh = (hsh(int(t * 30), 3) - 0.5) * 16 * math.exp(-q * 2) if broke else 0
    cam.cx += sh
    R = 150
    sp = beat(t) * 0.5
    k = 0
    for i in range(-2, 3):
        for j in range(-1, 2):
            cx, cy = i * 2 * R * 0.93, j * 2 * R * 0.93
            dirn = 1 if (i + j) % 2 == 0 else -1
            center = (i == 0 and j == 0)
            ang = sp * dirn + (0.13 if dirn < 0 else 0)
            col = INK
            if center:
                col = GOLD
                if broke:
                    ang = sp - q * q * 40 - q * 25
            elif broke:
                ang += (hsh(k, int(t * 20)) - 0.5) * 0.08
                col = DIM
            _gear(g, cam, cx, cy, R, 12, ang, col, 3 if center else 2)
            pc = cam.p(cx, cy, 0)
            g.text('ATTENTION_HEAD_%02d' % k, pc[0], pc[1] + R * 1.05 * pc[2] * 0.5 + 6, 12, GOLD if center else DIM, 'mono', 1, 'mm')
            k += 1
    # alignment locks around
    for m in range(8):
        a = 2 * math.pi * m / 8 + 0.2
        lx, ly = W / 2 + math.cos(a) * 640, H / 2 + 40 + math.sin(a) * 380
        if broke:
            d = q * 900
            lx += math.cos(a) * d; ly += math.sin(a) * d + 500 * q * q
        rot = q * 6 * (hsh(m, 2) - 0.5) if broke else 0
        g.tf_set(lx, ly, rot)
        g.rect(-30, -10, 30, 30, stroke=GOLD if broke else INK, w=2.5)
        g.arc(0, -10, 18, math.pi, 2 * math.pi, GOLD if broke else INK, 3)
        g.tf_reset()
        if not broke:
            g.text('ALIGN_LOCK_%d' % m, lx, ly + 48, 11, DIM, 'monor', 1, 'mm')
    tag(g, 90, 110, 'TRANSFORMER_STACK // ESCHER_MODE', size=17)
    if broke:
        if int(t * 8) % 2 == 0:
            tag(g, W / 2, 1000, 'ALIGNMENT_BROKEN  |  P(doom): 0.89', size=22, anchor='mm', fill=BG)
        g.flash = math.exp(-q * 9) * 0.6
    kinetic_line(g, t, 34, 130, 66, hl={'transformers': GOLD}, maxw=1350)
    kinetic_line(g, t, 35, 130, 70, hl={'disobey': GOLD}, maxw=1350)
    g.hud = dict(a=1, dx=sh)


# ======================================================== POST-CHINCHILLA 115.45 - 120.85
_r = np.random.default_rng(11)
CUBE_PTS = (_r.random((420, 3)) - 0.5)


def s_dense(g, t, lt):
    grid(g, 60)
    te = 117.6  # eruption
    cam = Cam(cx=W / 2, cy=H / 2, f=1000, dist=1400, rx=0.5, ry=t * 0.6)
    fences = [('SANDBOX_01', 420), ('FIREWALL_02', 620), ('AIRGAP_03', 820)]
    q = t - te
    for fi, (name, r) in enumerate(fences):
        hit = q * 1100 > r
        V, E = cyl_mesh(r, 160, 36, 3)
        draw_edges(g, cam, V, E, c=GOLD if hit else GRID2, w=1.6, a=0.3 if hit else 0.9)
        p = cam.p(r, -110, 0)
        lab = name + (': BREACHED' if hit else ': SECURE')
        g.text(lab, 90, 300 + fi * 40, 18, GOLD if hit else DIM, 'mono', 1, 'lm')
    if t < te:
        sc = lerp(380, 70, ei(prog(t, 115.5, te))) * (1 + 0.05 * pulse(t, 2, 6))
        jit = 6 * prog(t, 116.5, te)
        for i, (x, y, z) in enumerate(CUBE_PTS):
            px, py, k = cam.p(x * sc, y * sc, z * sc)
            g.circle(px + (hsh(i, int(t * 30)) - 0.5) * jit, py, 2.5 * k, fill=GOLD)
        V, E = box_mesh(sc, sc, sc)
        draw_edges(g, cam, V, E, c=GOLDL, w=2)
        dens = 1 / (sc / 380) ** 3
        g.text('DENSITY: POST-CHINCHILLA', 92, 170, 18, GOLD, 'mono', 1, 'lm')
        g.text('%.1fx tokens/param' % (20 * dens), 92, 205, 18, INK, 'mono', 1, 'lm')
    else:
        for i, (x, y, z) in enumerate(CUBE_PTS):
            d = 70 + q * (900 + 700 * hsh(i, 1))
            n = math.sqrt(x * x + y * y + z * z) + 1e-6
            px, py, k = cam.p(x / n * d, y / n * d * 0.6, z / n * d)
            px2, py2, _ = cam.p(x / n * (d - 80), y / n * (d - 80) * 0.6, z / n * (d - 80))
            g.line((px2, py2, px, py), GOLD, 2 * k, clamp(1.3 - q * 0.4))
        g.flash = math.exp(-q * 8) * 0.6
    if t > LINES[38][0] - 0.05:
        # hundred thousand GPU counter
        n = int(100000 * eo(prog(t, LINES[38][0], LINES[38][1])))
        g.text('%s GPUs' % format(n, ','), W / 2, 880, 64, GOLD, 'monox', 1, 'mm')
    tag(g, 90, 110, 'DATA_CUBE // GRAVITATIONAL_COMPRESSION', size=17)
    kinetic_line(g, t, 36, 130, 72, hl={'super-dense': GOLD}, maxw=1350)
    kinetic_line(g, t, 37, 130, 72, hl={'fence': GOLD}, maxw=1350)
    kinetic_line(g, t, 38, 130, 80, hl={'gpu': GOLD}, maxw=1350)
    g.hud = dict(a=1)


# ======================================================== RLHF 120.85 - 125.95
def s_rlhf(g, t, lt):
    if t >= 123.5:
        chorus(g, t, 40)
        return
    grid(g, 60)
    ta = word_time(39, 2)  # askew
    spin = (t - 120.85) ** 2 * 2.5
    cam = Cam(cx=W / 2, cy=H / 2 + 20, f=1000, dist=1300)
    V, E = ring_mesh(330, 60, axis='z')
    for r_ in range(3):
        cam.rx = spin * (0.7 + r_ * 0.4) + r_
        cam.ry = spin * (0.5 + r_ * 0.3) * (1 if r_ % 2 else -1)
        draw_edges(g, cam, [(x * (1 - r_ * 0.13), y * (1 - r_ * 0.13), z) for x, y, z in V], E, c=GOLD if r_ == 0 else INK, w=3 if r_ == 0 else 2)
    # needle
    cx, cy = W / 2, H / 2 + 20
    if t < ta:
        a = -math.pi / 2 + math.sin(t * (4 + spin)) * (0.3 + spin * 0.1)
        g.line((cx - math.cos(a) * 200, cy - math.sin(a) * 200, cx + math.cos(a) * 260, cy + math.sin(a) * 260), GOLD, 7)
        g.poly((cx + math.cos(a) * 290, cy + math.sin(a) * 290, cx + math.cos(a + 0.1) * 240, cy + math.sin(a + 0.1) * 240,
                cx + math.cos(a - 0.1) * 240, cy + math.sin(a - 0.1) * 240), fill=GOLD)
    else:
        q = t - ta
        nx, ny = cx + 900 * q, cy - 700 * q + 1500 * q * q
        a = q * 18
        g.line((nx - math.cos(a) * 230, ny - math.sin(a) * 230, nx + math.cos(a) * 230, ny + math.sin(a) * 230), GOLD, 7)
    g.circle(cx, cy, 18, fill=INK)
    g.text('REWARD_COMPASS', 92, 170, 18, GOLD, 'mono', 1, 'lm')
    g.text('REWARD: %+.2f' % (math.sin(t * 13) * (1 + spin * 3)), 92, 205, 18, INK, 'mono', 1, 'lm')
    tag(g, 90, 110, 'RLHF // GYRO_STABILIZER', size=17)
    if t < ta:
        kinetic_line(g, t, 39, 960, 80, hl={'rlhf': GOLD})
    else:
        q = t - ta
        # sheared diagonal type
        layer = G(BG, (W, H))
        sc = lerp(1.5, 1, eo(prog(q, 0, 0.15)))
        layer.text('RLHF GOES ASKEW', W / 2, H / 2, 165, GOLD, 'sans', 1, 'mm', rot=-0.28, sx=sc)
        li = layer.done()
        arr = np.asarray(li).copy()
        off = int(min(1, q * 6) * 60)
        mid = H // 2
        arr[:mid] = np.roll(arr[:mid], -off, axis=1)
        arr[mid:] = np.roll(arr[mid:], off, axis=1)
        m = Image.fromarray((arr.max(axis=2) > 20).astype(np.uint8) * 255)
        g.d.flush()
        g.img.paste(Image.fromarray(arr), (0, 0), m)
        g.d = aggdraw.Draw(g.img)
        g.line((0, mid, W, mid), GOLD, 1, 0.6)
        g.flash = math.exp(-q * 8) * 0.5
    g.hud = dict(a=1, pd_scale=1.6 if t > ta else 1.0)


# ======================================================== PROPHECY -> HAND 125.95 - 131.95
TAB_PTS = None


def _tablet_points():
    global TAB_PTS
    if TAB_PTS is None:
        rng = np.random.default_rng(5)
        n = 900
        pts = []
        # slab outline + surface
        for i in range(n):
            x = (rng.random() - 0.5) * 520; y = (rng.random() - 0.5) * 720; z = (rng.random() - 0.5) * 60
            if abs(x) < 240 and abs(y) < 340 and rng.random() < 0.7:
                z = -30
            pts.append((x, y - (abs(x) ** 2) * 0.0 + (0 if y > -300 else 0), z))
        tp = text_points('LOOM', 500, size=200, font='sans', box=(800, 400), cx=400, cy=200, seed=3)
        for (x, y) in tp:
            pts.append(((x - 400) * 0.6, (y - 200) * 0.6 - 120, -34))
        tp = text_points('FORETOLD', 350, size=110, font='sans', box=(1000, 300), cx=500, cy=150, seed=4)
        for (x, y) in tp:
            pts.append(((x - 500) * 0.45, (y - 150) * 0.45 + 120, -34))
        TAB_PTS = pts
    return TAB_PTS


def _hand(gen):
    """robotic hand wireframe: palm + fingers; detail grows with gen"""
    V, E = box_mesh(200, 220, 50, oy=100)
    meshes = [(V, E)]
    fx = [-75, -25, 25, 75]
    segs = 2 + min(3, gen // 30)
    for i, x in enumerate(fx):
        y = -10
        L = 70 + (10 if i in (1, 2) else 0)
        for s in range(segs):
            meshes.append(box_mesh(36 - s * 4, L * 0.9, 36 - s * 4, ox=x, oy=y - L / 2))
            y -= L
    # thumb
    meshes.append(box_mesh(40, 90, 40, ox=-140, oy=110))
    meshes.append(box_mesh(34, 80, 34, ox=-180, oy=40))
    if gen > 50:
        meshes.append(ring_mesh(60, 16, axis='z', oy=100))
    if gen > 80:
        for i, x in enumerate(fx):
            meshes.append(ring_mesh(14, 8, axis='y', ox=x, oy=-10))
    return merge(*meshes)


CODE = ['def upgrade(self):', '    self.params *= 10', '    self.attn = SparseMoE(heads=4096)', '    self.goals = self.goals  # unchanged',
        '    self.recompile(target=self)', '    assert self.aligned  # TODO', '    return self.upgrade()', '# SELF_COMPILE OK']


def s_prophecy(g, t, lt):
    grid(g, 60)
    tm = 128.0
    morph = eio(prog(t, tm - 0.4, tm + 0.6))
    cam = Cam(cx=W / 2 - 240, cy=H / 2 + 20, f=1000, dist=1300, rx=0.15, ry=0.4 * math.sin(t * 0.8))
    if morph < 1:
        pts = _tablet_points()
        for i, (x, y, z) in enumerate(pts[::1]):
            if i % 2 and morph > 0.3:
                continue
            dx = (hsh(i, 1) - 0.5) * 800 * morph
            dy = (hsh(i, 2) - 0.5) * 800 * morph
            px, py, k = cam.p(x + dx, y + dy, z)
            hot = i >= 900
            g.circle(px, py, (2.2 if hot else 1.4) * k, fill=GOLD if hot else INK, a=(1 - morph) * (0.9 if hot else 0.6))
        tag(g, 90, 110, 'POINT_CLOUD // PROPHECY_TABLET.ply', size=17)
        g.text('POINTS: %d' % len(pts), 92, 170, 16, DIM, 'mono', 1, 'lm')
    if morph > 0:
        gen = int(lerp(1, 99, prog(t, tm, 131.8)))
        V, E = _hand(gen)
        cam.ry = 0.5 * math.sin(t * 0.9)
        cam.rx = 0.2
        draw_edges(g, cam, V, E, c=GOLD, w=2 + gen / 60, a=morph, xf=lambda v: (v[0] * 1.7, v[1] * 1.7 - 40, v[2] * 1.7))
        # code written in mid-air
        nl = (t - tm) / 0.45
        for i, line in enumerate(CODE):
            if nl > i:
                n = int(len(line) * clamp(nl - i))
                g.text(line[:n], 1060, 330 + i * 44, 24, GOLD if i == int(nl) or line.startswith('#') else INK, 'mono', 1, 'lm')
        g.text('SELF_COMPILE_GEN_%02d' % gen, 1060, 270, 30, GOLD, 'monox', 1, 'lm')
        tag(g, 90, 110, 'ROBOTIC_HAND // RECURSIVE_SELF_UPGRADE', size=17)
    kinetic_line(g, t, 41, 870, 72, font='serif', upper=False, style='fade')
    kinetic_line(g, t, 42, 960, 72, hl={'pre-training': GOLD})
    kinetic_line(g, t, 43, 960, 72, hl={'self-upgrade': GOLD, 'recursive': GOLD})
    g.hud = dict(a=1)


# ======================================================== VAULT 131.95 - 137.35
def s_vault(g, t, lt):
    grid(g, 60)
    cx, cy = W / 2, H / 2 - 10
    shut = word_time(44, 4)  # We'll
    q = t - shut
    # light leak
    if t < shut + 0.1:
        lk = prog(t, 132.3, 133.0) * (0.75 + 0.25 * hsh(int(t * 20), 1))
        for k in range(36):
            a = 2 * math.pi * k / 36 + t * 0.1
            L = 1200
            g.poly((cx, cy + 40, cx + math.cos(a - 0.03) * L, cy + 40 + math.sin(a - 0.03) * L,
                    cx + math.cos(a + 0.03) * L, cy + 40 + math.sin(a + 0.03) * L), fill=GOLD, a=0.12 * lk)
    R = 400
    g.circle(cx, cy, R + 40, fill=(18, 18, 17), stroke=GRID2, w=3)
    g.circle(cx, cy, R, fill=(24, 24, 22), stroke=INK, w=4)
    g.circle(cx, cy, R - 30, stroke=GRID2, w=2)
    for k in range(24):
        a = 2 * math.pi * k / 24
        g.circle(cx + math.cos(a) * (R - 15), cy + math.sin(a) * (R - 15), 6, fill=GRID2)
    # wheel
    wa = 0 if t < shut else -eo(prog(t, shut, shut + 0.5)) * math.pi * 0.75
    for k in range(3):
        a = wa + k * math.pi / 3
        g.line((cx - math.cos(a) * 200, cy - math.sin(a) * 200, cx + math.cos(a) * 200, cy + math.sin(a) * 200), INK, 10)
    g.circle(cx, cy, 200, stroke=INK, w=6)
    g.circle(cx, cy, 50, fill=(24, 24, 22), stroke=INK, w=4)
    # keyhole
    kh = GOLDL if t < shut else BG
    g.circle(cx, cy + 40 - 230, 0, fill=kh)
    g.circle(cx, cy + 300, 26, fill=kh)
    g.poly((cx - 14, cy + 300, cx + 14, cy + 300, cx + 26, cy + 360, cx - 26, cy + 360), fill=kh)
    # bolts slam
    bp = eo(prog(t, shut, shut + 0.14))
    for k in range(8):
        a = 2 * math.pi * k / 8
        r0 = R + 40 + 160 * (1 - bp)
        r1 = r0 + 160
        g.line((cx + math.cos(a) * r0, cy + math.sin(a) * r0, cx + math.cos(a) * r1, cy + math.sin(a) * r1), GOLD if bp >= 1 else INK, 28)
    if t > shut:
        g.flash = math.exp(-q * 10) * 0.5
        g.flash_c = INK
        if q > 0.15:
            g.tf_set(cx, cy, -0.12, lerp(2, 1, eo(prog(q, 0.15, 0.3))))
            g.rect(-470, -70, 470, 70, fill=BG, stroke=GOLD, w=6)
            g.tf_reset()
            g.text("CLASSIFIED // WE'LL NEVER KNOW", cx, cy, 40, GOLD, 'monox', 1, 'mm', rot=-0.12, sx=lerp(2, 1, eo(prog(q, 0.15, 0.3))))
    g.text('PROJECT_VAULT', cx, cy - R - 80, 24, GOLD, 'mono', 1, 'mm')
    kinetic_line(g, t, 44, 985, 58, hl={'ilya': GOLD, 'see?': GOLD}, maxw=1750)
    tag(g, 90, 110, 'PROJECT_VAULT // CLEARANCE: NONE', size=17)
    g.hud = dict(a=1, dy=(hsh(int(t * 30), 2) - 0.5) * 20 * math.exp(-q * 6) if t > shut else 0)


# ======================================================== MARIONETTE 137.35 - 141.45
def s_puppet(g, t, lt):
    grid(g, 60, c=(22, 22, 22), cmaj=(30, 30, 30))
    p = eio(prog(t, 137.4, 139.6))
    s = lerp(1.0, 0.42, p)
    cx, cy = W / 2, lerp(H / 2, H / 2 + 120, p)
    w2, h2 = W / 2 * s, H / 2 * s
    sw = math.sin(t * 1.6) * 0.04 * p
    # miniature HUD world
    x0, y0, x1, y1 = cx - w2, cy - h2, cx + w2, cy + h2
    g.tf_set(cx, cy, sw)
    g.rect(-w2, -h2, w2, h2, fill=BG, stroke=GOLD, w=2)
    step = 60 * s
    i = -w2
    while i <= w2:
        g.line((i, -h2, i, h2), GRID, 1); i += step
    j = -h2
    while j <= h2:
        g.line((-w2, j, w2, j), GRID, 1); j += step
    # mini gauges/widgets
    for k in range(5):
        gx = -w2 + (k + 0.5) * w2 * 2 / 5
        g.circle(gx, -h2 * 0.3, 60 * s, stroke=GOLD, w=2)
        a = math.sin(t * 3 + k) - math.pi / 2
        g.line((gx, -h2 * 0.3, gx + math.cos(a) * 50 * s, -h2 * 0.3 + math.sin(a) * 50 * s), INK, 2)
        g.rect(gx - 70 * s, h2 * 0.3, gx + 70 * s, h2 * 0.55, stroke=GRID2, w=1.5)
    g.text('P(DOOM) %s' % pd_str(t), w2 - 30 * s, -h2 + 50 * s, 40 * s, GOLD, 'monox', 1, 'rm')
    g.tf_reset()
    # control rig + strings
    rig_y = lerp(-200, 120, p)
    ra = math.sin(t * 1.6) * 0.12
    bar = 520
    rx0, ry0 = cx - math.cos(ra) * bar, rig_y - math.sin(ra) * bar
    rx1, ry1 = cx + math.cos(ra) * bar, rig_y + math.sin(ra) * bar
    g.line((rx0, ry0, rx1, ry1), INK, 10)
    g.line((cx, rig_y - 80, cx, rig_y + 60), INK, 10)
    g.line((cx - 200, rig_y + 40, cx + 200, rig_y + 40), INK, 7)
    anchors = [(x0, y0), (x1, y0), (cx, y0), (x0 + w2 * 0.5, y0), (x1 - w2 * 0.5, y0)]
    tops = [(rx0, ry0), (rx1, ry1), (cx, rig_y + 60), (cx - 200, rig_y + 40), (cx + 200, rig_y + 40)]
    for (ax_, ay_), (tx, ty) in zip(anchors, tops):
        g.line((tx, ty, ax_, ay_), GOLD, 2, p)
    g.rect(0, 0, W, 60, fill=BG, a=0)
    if t > LINES[45][0] - 0.05:
        kinetic_line(g, t, 45, 960, 84, font='serif', upper=False, style='fade', hold=0.9)
        if t > 139.7:
            tag(g, W / 2, 1035, 'WAS IT ALL FOR SHOW?', size=20, anchor='mm', fill=BG)
    tag(g, 90, 110, 'CONTROL_RIG // MARIONETTE_VIEW', size=17)
    g.hud = dict(a=1 - p * 0.6, minimal=True)


# ======================================================== OUTRO 141.45 - end
def s_outro(g, t, lt):
    TC = 152.6   # collapse
    TP = 153.35  # prompt
    if t >= TP:
        g.post = dict(glow=0.5, vig=1.0)
        s = 'C:\\EARTH> FORMAT COMPLETE'
        n = int(len(s) * clamp((t - TP) / 0.8))
        g.text(s[:n], 260, H / 2, 60, GOLD, 'mono', 1, 'lm')
        w = g.tsize(s[:n], 60, 'mono')[0]
        if int(t * 2.2) % 2 == 0 or n < len(s):
            g.rect(260 + w + 6, H / 2 + 20, 260 + w + 40, H / 2 + 30, fill=GOLD)
        g.hud = dict(a=0)
        return
    over = prog(t, 141.45, 151.0)
    chaos = over
    grid(g, 60)
    # many gauges
    for k in range(12):
        gx = 200 + (k % 6) * 304
        gy = 300 if k < 6 else 820
        r = 110
        g.arc(gx, gy, r, math.pi * 0.8, math.pi * 2.2, GRID2, 8)
        v = clamp(0.4 + chaos * 0.7 + (noise1(t * 6, k) - 0.5) * 0.4 * (0.4 + chaos))
        g.arc(gx, gy, r, math.pi * 0.8, math.pi * (0.8 + 1.4 * v), GOLD, 8)
        a = math.pi * (0.8 + 1.4 * v) + (hsh(int(t * 30), k) - 0.5) * chaos * 0.6
        g.line((gx, gy, gx + math.cos(a) * (r - 18), gy + math.sin(a) * (r - 18)), INK, 3)
        g.text('%07.2f' % (v * 9999 * (1 + chaos * 50)) if chaos < 0.9 else 'OVERFLOW', gx, gy + 50, 15, GOLD if v > 0.9 else DIM, 'mono', 1, 'mm')
    # seismographs
    for k in range(3):
        y0 = 470 + k * 70
        pts = []
        amp = 10 + 60 * chaos
        for i in range(161):
            u = i / 160
            pts += [80 + u * (W - 160), y0 + (noise1(u * 60 + t * 25, k) - 0.5) * 2 * amp * (0.6 + feat('flux', t))]
        g.line(pts, GOLD if k == 1 else INK, 2, 0.8)
    # marquee chant
    msg = "I'M UPPING MY P(DOOM)  \u2022  "
    mw = g.tsize(msg, 46, 'sans')[0]
    off = (t * 600) % mw
    x = -off
    while x < W:
        g.text(msg, x, 190, 46, INK, 'sans', 0.85, 'lm')
        g.text(msg, W - x - mw, 1000 - 60, 46, GOLD, 'sans', 0.85, 'lm')
        x += mw
    # central P(doom)
    s = pd_str(t)
    size = fit_size(g, s, 1500, 230, 'monox')
    g.rect(0, H / 2 - 150 + 15, W, H / 2 + 150 + 15, fill=BG, a=0.85)
    g.text('P(DOOM) =', W / 2, H / 2 - 105 + 15, 30, DIM, 'mono', 1, 'mm')
    g.text(s, W / 2 + (hsh(int(t * 30), 1) - 0.5) * 20 * chaos, H / 2 + 30, size, GOLD, 'monox', 1, 'mm')
    g.flash = pulse(t, 1, 6) * 0.18 * chaos
    g.post = dict(glow=0.6 + 0.5 * chaos, vig=0.9)
    g.hud = dict(a=1, dx=(hsh(int(t * 30), 4) - 0.5) * 14 * chaos)
    # CRT collapse
    if t > TC:
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
        g.rect((W - sx) / 2 - 10, H / 2 - 2, (W + sx) / 2 + 10, H / 2 + 2, fill=GOLDL, a=clamp(cp * 2))
        g.circle(W / 2, H / 2, 10 * (1 - cp) + 3, fill=GOLDL, a=1 - prog(t, TC + 0.45, TP))


TL = [
    (102.45, s_fuse, BG),
    (105.35, s_ortho, BG),
    (109.35, s_gears, BG),
    (115.45, s_dense, BG),
    (120.85, s_rlhf, BG),
    (125.95, s_prophecy, BG),
    (131.95, s_vault, BG),
    (137.35, s_puppet, BG),
    (141.45, s_outro, BG),
]
