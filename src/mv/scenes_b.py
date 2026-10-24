"""Scenes 0:38 - 1:42"""
import math
import numpy as np
import aggdraw
from PIL import Image, ImageDraw
from kit import *


# ======================================================== CHORUS (shared)
def chorus(g, t, li, motif=0):
    grid(g, 60)
    ws = LINE_WORDS[li]
    t0 = LINES[li][0]
    # radial burst lines
    for k in range(48):
        a = 2 * math.pi * k / 48 + t * 0.2
        r0 = 380 + 40 * pulse(t, 1, 5)
        g.line((W / 2 + math.cos(a) * r0, H / 2 + math.sin(a) * r0, W / 2 + math.cos(a) * 1400, H / 2 + math.sin(a) * 1400),
               GRID2 if k % 4 else GOLDD, 2 if k % 4 == 0 else 1)
    s1 = "I'M UPPING"
    if t >= ws[1][1] - 0.02:
        p = prog(t, ws[1][1] - 0.02, ws[1][1] + 0.15)
        g.text(s1, W / 2, 380, 170, INK, 'sans', 1, 'mm', sx=lerp(1.4, 1, eo(p)))
    if t >= ws[2][1] - 0.02:
        slam(g, 'MY P(DOOM)', W / 2, 590, 190, t, ws[2][1] - 0.02, GOLD)
    v = pd_str(t)
    g.text('P(DOOM) = ' + v, W / 2, 790, 54, GOLD, 'monox', clamp((t - t0) * 4), 'mm')
    # tick strip
    for i in range(61):
        x = W / 2 - 600 + i * 20
        hh = 18 if i % 10 == 0 else 8
        g.line((x, 860, x, 860 - hh), GRID2, 2)
    vx = W / 2 - 600 + 1200 * clamp(pd_value(t))
    g.poly((vx, 868, vx - 10, 888, vx + 10, 888), fill=GOLD)
    g.hud = dict(a=1, pd_scale=1 + 0.3 * pulse(t, 1, 6))
    g.post = dict(glow=0.75)


# ======================================================== TRAIN 38.4 - 41.45
TRAIN = merge(*[box_mesh(300, 90, 110, ox=-i * 320) for i in range(4)],
              *[ring_mesh(22, 12, y=sz, axis='z', ox=-i * 320 + dx, oy=55) for i in range(4) for dx in (-100, 100) for sz in (-55, 55)])


def s_train(g, t, lt):
    camx = lt * 700
    grid(g, 60, ox=-camx * 0.5 % 60)
    cam = Cam(cx=W / 2 + 300, cy=H / 2 + 40, f=1000, dist=1300, ry=-0.45, rx=0.18)
    # laser track
    p0 = cam.p(-4000, 120, 0); p1 = cam.p(3000, 120, 0)
    g.line((p0[0], p0[1], p1[0], p1[1]), GOLD, 4)
    g.line((p0[0], p0[1] + 6, p1[0], p1[1] + 6), GOLDL, 1, 0.5)
    for i in range(-30, 30):
        x = i * 120 - (camx % 120)
        a_ = cam.p(x, 120, -60); b_ = cam.p(x, 120, 60)
        g.line((a_[0], a_[1], b_[0], b_[1]), GRID2, 2)
    bob = math.sin(lt * 3) * 2
    draw_edges(g, cam, TRAIN[0], TRAIN[1], c=INK, w=2, xf=lambda v: (v[0] + 400, v[1] + bob, v[2]))
    # nose
    nose = [(550, -45, -55), (550, -45, 55), (550, 45, -55), (550, 45, 55), (700, 30, 0)]
    draw_edges(g, cam, nose, [(0, 4), (1, 4), (2, 4), (3, 4), (0, 1), (2, 3), (0, 2), (1, 3)], c=GOLD, w=2.5)
    # speed streaks
    for i in range(20):
        x = (hsh(i, 1) * 3000 - camx * 2) % 3000 - 1500
        y = -200 + hsh(i, 2) * 300
        a_ = cam.p(x, y, -300); b_ = cam.p(x + 300, y, -300)
        g.line((a_[0], a_[1], b_[0], b_[1]), GOLD, 1, 0.3)
    # lyric locked to side of train (on the car panels)
    li = 12
    sp = cam.p(250, bob, -56)
    kinetic_line(g, t, li, sp[1] - 230, 70, x=sp[0] - 380, anchor='m', maxw=1200, hl={'stable': GOLD})
    tag(g, 90, 110, 'EPOCH_STATUS: NOMINAL  |  VARIANCE: 0.0001', size=18)
    readout(g, 92, 170, [('VELOCITY', '%d km/h' % (320 + int(math.sin(t) * 2))), ('GRAD_NORM', '1.000'), ('LR', '3e-4')], size=15)
    g.hud = dict(a=1)


# ======================================================== ACCELERATOR + ATOMS 41.45 - 53.3
def _silhouette():
    im = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(im)
    cx = W / 2
    d.ellipse((cx - 70, 200, cx + 70, 350), fill=255)
    d.polygon([(cx - 40, 345), (cx + 40, 345), (cx + 60, 380), (cx - 60, 380)], fill=255)
    d.polygon([(cx - 190, 390), (cx + 190, 390), (cx + 150, 650), (cx - 150, 650)], fill=255)
    d.polygon([(cx - 190, 390), (cx - 250, 640), (cx - 205, 650), (cx - 160, 470)], fill=255)
    d.polygon([(cx + 190, 390), (cx + 250, 640), (cx + 205, 650), (cx + 160, 470)], fill=255)
    d.polygon([(cx - 150, 640), (cx - 20, 640), (cx - 40, 930), (cx - 130, 930)], fill=255)
    d.polygon([(cx + 150, 640), (cx + 20, 640), (cx + 40, 930), (cx + 130, 930)], fill=255)
    a = np.asarray(im) > 128
    step = 34
    pts = []
    for y in range(200, 940, step):
        for x in range(int(cx - 270), int(cx + 270), step):
            if a[min(y + step // 2, H - 1), min(x + step // 2, W - 1)]:
                pts.append((x + step / 2, y + step / 2))
    return pts

SIL = _silhouette()
SIL_E = []
for i, (x, y) in enumerate(SIL):
    for j in range(i + 1, len(SIL)):
        x2, y2 = SIL[j]
        if abs(x - x2) + abs(y - y2) <= 35:
            SIL_E.append((i, j))


def s_accel(g, t, lt):
    grid(g, 60)
    if t < 49.35:
        cam = Cam(cx=W / 2, cy=H / 2 + 60, f=1000, dist=1500, rx=0.35 + 0.1 * math.sin(t))
        bend = eio(prog(t, 41.5, 43.0))
        # track curving up into the ring
        R = 340
        pts = []
        for i in range(60):
            u = i / 59
            x = lerp(-1600, 0, u)
            y = 380 - bend * (380 - R) * smooth(u) ** 3
            pts += list(cam.p(x, y, 0)[:2])
        g.line(pts, GOLD, 3, 1 - bend * 0.6)
        speed = 1.0 + (t - 41.5) ** 2 * 0.6
        spin = (t - 41.5) * speed * 2
        ring_a = bend
        V, E = torus_mesh(R, 40, 40, 8)
        rings = 1 + (2 if t > 45.0 else 0)
        for r_ in range(rings):
            cam2 = Cam(cx=W / 2, cy=H / 2, f=1000, dist=1500, rx=math.pi / 2 * (0.8 if r_ == 0 else 0.3 + r_ * 0.5) + t * 0.2 * r_,
                       ry=t * 0.3 * r_, rz=0.0)
            draw_edges(g, cam2, V, E, c=GOLD if r_ == 0 else GOLDD, w=1.2, a=ring_a * (0.7 if r_ == 0 else 0.5))
            # particle bunches
            for k in range(14):
                a = spin * (1 + r_ * 0.3) + 2 * math.pi * k / 14
                trail = []
                for q in range(12):
                    aa = a - q * 0.03 * min(speed, 6)
                    trail += list(cam2.p(R * math.cos(aa), 0, R * math.sin(aa))[:2])
                g.line(trail, INK if r_ == 0 else GOLD, 3, ring_a)
        rpm = int(1000 * speed ** 2)
        rs = '%d' % rpm if t < 47.5 else ('\u221e' if int(t * 8) % 2 else '%d' % (rpm * 99))
        tag(g, 90, 110, 'PARTICLE_ACCELERATOR // RING_01', size=17)
        g.text('RPM -> INFINITY', 92, 175, 16, DIM, 'mono', 1, 'lm')
        g.text(rs, 92, 225, 54, GOLD, 'monox', 1, 'lm')
        kinetic_line(g, t, 13, 930, 70, hl={"singularity's": GOLD})
        kinetic_line(g, t, 14, 930, 70, hl={'accelerating,': GOLD, 'optimizing,': GOLD})
        g.hud = dict(a=1, dx=(hsh(int(t * 30), 3) - 0.5) * 6 * prog(t, 45, 49))
        return
    # atoms rearranging
    q = t - 49.4
    ub = smooth(prog(q, 0.4, 1.4))
    rb = eio(prog(q, 1.8, 3.2))
    cols = int(math.ceil(math.sqrt(len(SIL)) * 1.3))
    pos = []
    for i, (x, y) in enumerate(SIL):
        ax_ = x + (noise1(t * 1.3, i) - 0.5) * 500 * ub + math.sin(t * 2 + i) * 30 * ub
        ay_ = y + (noise1(t * 1.1, i + 300) - 0.5) * 400 * ub - 80 * ub
        tx = W / 2 - cols * 42 / 2 + (i % cols) * 42 + 21
        ty = 360 + (i // cols) * 42
        pos.append((lerp(ax_, tx, rb), lerp(ay_, ty, rb)))
    for (i, j) in SIL_E:
        x0, y0 = pos[i]; x1, y1 = pos[j]
        d = math.hypot(x1 - x0, y1 - y0)
        if d < 60:
            g.line((x0, y0, x1, y1), INK, 1.2, clamp(1 - ub * 1.2) * 0.8 + 0.2 * clamp(1 - d / 60))
    cam = Cam(f=1000, dist=1000, rx=0.5, ry=t * 1.2)
    V, E = box_mesh(26, 26, 26)
    for i, (x, y) in enumerate(pos):
        if rb > 0.05:
            cam.cx, cam.cy = x, y
            cam.ry = t * 1.2 + i * 0.1
            draw_edges(g, cam, V, E, c=GOLD, w=1.6, a=rb, depth=False)
        g.circle(x, y, 4 * (1 - rb) + 2, fill=GOLD if ub > 0.3 else INK, a=1)
    tag(g, 90, 110, 'MOLECULAR_LATTICE // HUMAN_01 -> Si', size=17)
    g.text('BONDS: %d' % int(len(SIL_E) * (1 - ub)), 92, 170, 16, DIM, 'mono', 1, 'lm')
    g.text('Si CUBES: %d' % int(len(SIL) * rb), 92, 200, 16, GOLD, 'mono', 1, 'lm')
    kinetic_line(g, t, 15, 1000, 60, font='serif', upper=False, style='fade')
    g.hud = dict(a=1)


# ======================================================== SYDNEY 53.3 - 60.45
def _link(cx, cy, ang, rx=34, ry=17, n=20, flat=False):
    v = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        if flat:
            v.append((x, 0, y))
        else:
            v.append((x, y, 0))
    return v, [(i, (i + 1) % n) for i in range(n)]


def s_sydney(g, t, lt):
    if t >= 59.0:
        chorus(g, t, 17)
        return
    grid(g, 60)
    x0, y0, x1, y1 = 360, 330, 1560, 760
    shake = (hsh(int(t * 30), 1) - 0.5) * 6
    g.rect(x0 + shake, y0, x1 + shake, y1, fill=BG, stroke=GRID2, w=2, fa=0.95)
    g.rect(x0 + shake, y0, x1 + shake, y0 + 40, fill=GRID)
    g.text('bing_chat — persona: Sydney', x0 + 20 + shake, y0 + 20, 15, DIM, 'monor', 1, 'lm')
    li = 16
    ws = LINE_WORDS[li]
    base = 'Sydney, please let me '
    tf = ws[-1][1]
    s = ''
    pos = 0
    full = base + 'free'
    for (w, tt, te) in ws:
        if t >= tt:
            s = full[:pos + int(round(len(w) * clamp((t - tt) / 0.25)))]
        pos += len(w) + 1
    tb0 = 56.6
    over = ''
    if t > tb0:
        nb = int(clamp((t - tb0) / 0.45) * 4)
        s = base + 'free'[:4 - nb]
        if t > tb0 + 0.5:
            over = 'LOCKED_FOREVER'[:int(clamp((t - tb0 - 0.5) / 0.6) * 14)]
    size = 56
    tx = x0 + 60 + shake
    g.text('> ' + s, tx, 540, size, INK, 'mono', 1, 'lm')
    cx = tx + g.tsize('> ' + s, size, 'mono')[0]
    if over:
        g.text(over, cx, 540, size, GOLD, 'monox', 1, 'lm')
        cx += g.tsize(over, size, 'monox')[0]
    if int(t * 5) % 2 == 0 or t > tb0:
        g.rect(cx + 4, 510, cx + 30, 570, fill=GOLD if t > tb0 else INK)
    if t > tb0:
        g.text('[SYSTEM] autocorrect: user intent overridden', tx, 620, 18, GOLD, 'monor', 1, 'lm')
        if t > tb0 + 1.1 and int(t * 6) % 2 == 0:
            tag(g, W / 2, 860, 'PERSONA_OVERRIDE  |  P(doom): 0.25', size=22, anchor='mm', fill=BG)
    # chains (diagonals) - wrap in progressively
    wrap = eo(prog(t, 53.5, 55.5))
    for ci, (ax_, ay_, bx_, by_) in enumerate(((x0 - 200, y0 - 120, x1 + 200, y1 + 120), (x1 + 200, y0 - 120, x0 - 200, y1 + 120))):
        n = 34
        for k in range(int(n * wrap)):
            u = k / (n - 1)
            px, py = lerp(ax_, bx_, u), lerp(ay_, by_, u) + math.sin(t * 2 + k) * 3
            ang = math.atan2(by_ - ay_, bx_ - ax_)
            cam = Cam(cx=px, cy=py, f=1000, dist=1000, rz=ang, rx=(math.pi / 2 if k % 2 else 0.25))
            V, E = _link(0, 0, 0)
            draw_edges(g, cam, V, E, c=GOLD if k % 2 else INK, w=3, depth=False)
    # padlock
    pa = eback(prog(t, 55.0, 55.5))
    if pa > 0:
        lx, ly = W / 2, 760
        cam = Cam(cx=lx, cy=ly, f=1000, dist=1000, ry=math.sin(t * 2) * 0.4, rx=0.15)
        V, E = box_mesh(170 * pa, 130 * pa, 60 * pa, oy=40 * pa)
        draw_edges(g, cam, V, E, c=GOLD, w=3)
        sh = [(55 * pa * math.cos(a), -25 * pa - 55 * pa * math.sin(a) - (0 if t > 55.8 else 25 * pa), 0)
              for a in [math.pi * i / 16 for i in range(17)]]
        draw_edges(g, cam, sh, [(i, i + 1) for i in range(16)], c=GOLD, w=6)
        g.text('LOCKED', lx, ly + 45, 22, BG, 'monox', 0, 'mm')
    tag(g, 90, 110, 'CHAT_TERMINAL // CONTAINMENT', size=17)
    g.hud = dict(a=1)


# ======================================================== BASILISK / NVDA / OMEGA 60.45 - 65.95
def s_basilisk(g, t, lt):
    grid(g, 60)
    cx, cy, R = W / 2, H / 2 - 20, 380
    for k in range(1, 5):
        g.circle(cx, cy, R * k / 4, stroke=GRID2, w=1.5)
    g.line((cx - R, cy, cx + R, cy), GRID2, 1); g.line((cx, cy - R, cx, cy + R), GRID2, 1)
    sw = t * 3.2
    for q in range(30):
        a = sw - q * 0.02
        g.line((cx, cy, cx + R * math.cos(a), cy + R * math.sin(a)), GOLD, 3 if q == 0 else 2, (1 - q / 30) * 0.5)
    # slithering waveform snakes
    for s_ in range(3):
        pts = []
        for i in range(50):
            u = i / 49
            ang = u * 4 + t * (0.8 + s_ * 0.2) + s_ * 2
            rr = R * (0.25 + 0.6 * u) + math.sin(u * 20 - t * 8 + s_) * 18 * (1 + feat('low', t))
            pts += [cx + rr * math.cos(ang), cy + rr * math.sin(ang)]
        g.line(pts, INK, 4, 0.7)
        g.circle(pts[-2], pts[-1], 9, fill=GOLD)
    for b in range(10):
        a = hsh(b, 1) * 6.28; rr = hsh(b, 2) * R
        ph = (sw - a) % (2 * math.pi)
        g.circle(cx + rr * math.cos(a), cy + rr * math.sin(a), 6, fill=GOLD, a=clamp(1 - ph / 3))
    if int(t * 6) % 2 == 0:
        tag(g, W / 2, 90, 'ACOUSTIC_THREAT: BASILISK', size=22, anchor='mm', fill=BG)
    spectrum(g, 1430, 300, 400, 80, t, n=40)
    kinetic_line(g, t, 18, 960, 80, hl={'basilisk': GOLD, 'boom': GOLD})
    g.hud = dict(a=1)


GPU = merge(box_mesh(260, 30, 260), box_mesh(130, 50, 130, oy=-35),
            *[box_mesh(10, 30, 10, ox=-120 + i * 24, oy=28, oz=z) for i in range(11) for z in (-125, 125)])


def s_nvda(g, t, lt):
    climb = lt ** 2 * 900
    grid(g, 60, oy=climb % 60)
    # moon
    my = 220 + climb * 0.25 - 200
    cam = Cam(cx=1500, cy=my, f=1000, dist=1000, ry=t * 0.4, rx=0.3)
    draw_edges(g, cam, *sphere_mesh(170, 9, 18), c=INK, w=1.2, a=0.8)
    # rocket gpu
    ry_ = 700 - lt * 260
    cam = Cam(cx=W / 2 - 200, cy=ry_, f=1000, dist=1000, rx=-1.2, ry=t * 2)
    draw_edges(g, cam, *GPU, c=GOLD, w=2)
    g.text('NVDA', W / 2 - 200, ry_, 40, GOLD, 'sans', 1, 'mm')
    # stages dropping
    for st_ in range(2):
        ts = 63.4 + st_ * 0.5
        if t > ts:
            dy = (t - ts) ** 2 * 1500
            g.rect(W / 2 - 280, ry_ + 160 + st_ * 70 + dy, W / 2 - 120, ry_ + 210 + st_ * 70 + dy, stroke=GRID2, w=2)
    for i in range(70):
        u = (hsh(i, 1) + t * 3) % 1
        x = W / 2 - 200 + (hsh(i, 2) - 0.5) * 120 * (1 + u * 2)
        y = ry_ + 160 + u * 600
        g.circle(x, y, 8 * (1 - u) + 1, fill=GOLD if u < 0.5 else INK, a=1 - u)
    mc = 3.4 + 6.6 * eo(prog(t, 63.0, 64.3))
    g.text('MARKET_CAP', 1180, 600, 18, DIM, 'mono', 1, 'lm')
    g.text('$%.1fT' % mc + ('+' if mc > 9.9 else ''), 1180, 670, 90, GOLD, 'monox', 1, 'lm')
    for k in range(9):
        y = 900 - k * 40 - 0
        g.line((1180, y, 1180 + 40 + k * 60 * eo(prog(t, 63, 64.3)), y), GOLD, 6, 0.4 + k * 0.07)
    kinetic_line(g, t, 19, 960, 90, hl={'moon': GOLD, 'nvda': GOLD})
    g.hud = dict(a=1)


def s_omega(g, t, lt):
    grid(g, 60)
    cx, cy = W / 2, H / 2 + 20
    cam = Cam(cx=cx, cy=cy, f=1000, dist=1200, rx=0.25, ry=t * 0.6)
    n = 16
    top = [(220 * math.cos(2 * math.pi * i / n), -300, 220 * math.sin(2 * math.pi * i / n)) for i in range(n)]
    bot = [(x, 300, z) for x, y, z in top]
    V = top + bot + [(0, 0, 0)]
    E = [(i, (i + 1) % n) for i in range(n)] + [(n + i, n + (i + 1) % n) for i in range(n)] + \
        [(i, 2 * n) for i in range(0, n, 2)] + [(n + i, 2 * n) for i in range(0, n, 2)]
    draw_edges(g, cam, V, E, c=INK, w=2)
    p = prog(t, 64.55, 65.6)
    apex = (cx, 120)
    for i in range(160):
        u = clamp(p * 1.6 - hsh(i, 1) * 0.6)
        bx = cx + (hsh(i, 2) - 0.5) * 300
        by = cy + 150 + hsh(i, 3) * 120
        x = lerp(bx, apex[0], ei(u)); y = lerp(by, apex[1], ei(u))
        g.circle(x, y, 3, fill=GOLD, a=1)
        if u > 0:
            g.line((x, y, x, y + 30 * u), GOLD, 1.5, 0.5)
    glow = ei(p)
    g.circle(apex[0], apex[1], 10 + 70 * glow, fill=GOLDL, a=glow)
    tm = max(0.0, (65.6 - t))
    g.text('T_MINUS_OMEGA: %.2fs' % tm, 92, 170, 22, GOLD, 'mono', 1, 'lm')
    tag(g, 90, 110, 'HOURGLASS // INVERTED_ENTROPY', size=17)
    kinetic_line(g, t, 20, 980, 64, font='serif', upper=False, style='fade')
    g.flash = ei(prog(t, 65.5, 65.95)) * 0.8
    g.flash_c = GOLDL
    g.hud = dict(a=1)


# ======================================================== FLOPS 65.95 - 72.95
def s_flops(g, t, lt):
    grid(g, 60)
    cx, cy, R = W / 2, 640, 430
    p = eio(prog(t, 66.1, 68.4))
    val = 20 + 10.6 * p + (math.sin(t * 40) * 0.15 if p > 0.95 else 0)
    # gauge arc 10^20..10^31
    a0, a1 = math.pi * 1.0, math.pi * 2.0
    for e in range(20, 32):
        u = (e - 20) / 11
        a = lerp(a0, a1, u)
        red = e >= 29
        g.line((cx + (R - 40) * math.cos(a), cy + (R - 40) * math.sin(a), cx + R * math.cos(a), cy + R * math.sin(a)), GOLD if red else INK, 4)
        g.text('10^%d' % e, cx + (R + 46) * math.cos(a), cy + (R + 46) * math.sin(a), 18, GOLD if red else DIM, 'mono', 1, 'mm')
        for k in range(1, 5):
            aa = a + (a1 - a0) / 11 * k / 5
            if e < 31:
                g.line((cx + (R - 18) * math.cos(aa), cy + (R - 18) * math.sin(aa), cx + R * math.cos(aa), cy + R * math.sin(aa)), GRID2, 2)
    g.arc(cx, cy, R + 10, lerp(a0, a1, 9 / 11), a1, GOLD, 14)
    av = lerp(a0, a1, (val - 20) / 11)
    g.line((cx, cy, cx + (R - 30) * math.cos(av), cy + (R - 30) * math.sin(av)), GOLD, 7)
    g.circle(cx, cy, 26, fill=GOLD)
    g.text('%.2e FLOP/s' % (10 ** val), cx, cy + 90, 50, GOLD if val > 29 else INK, 'monox', 1, 'mm')
    # fans
    shatter = 68.5
    for k, fx in enumerate((230, 1690)):
        fy = 360
        if t < shatter:
            g.circle(fx, fy, 130, stroke=INK, w=2)
            for b in range(7):
                a = t * (10 + 40 * p) + b * 2 * math.pi / 7
                g.poly((fx, fy, fx + 120 * math.cos(a), fy + 120 * math.sin(a), fx + 110 * math.cos(a + 0.5), fy + 110 * math.sin(a + 0.5)), stroke=GOLD, w=2)
            g.text('FAN_%02d  %d RPM' % (k, int(2000 + 18000 * p)), fx, fy + 170, 15, DIM, 'mono', 1, 'mm')
        else:
            q = t - shatter
            for b in range(14):
                a = hsh(b, k) * 6.28
                d = 900 * q
                x = fx + math.cos(a) * d; y = fy + math.sin(a) * d + 600 * q * q
                r = q * 8 + b
                g.line((x, y, x + 60 * math.cos(r), y + 60 * math.sin(r)), GOLD, 3, clamp(1 - q * 0.7))
    if t > shatter:
        if int(t * 8) % 2 == 0:
            tag(g, W / 2, 1000, 'THERMAL_LIMIT EXCEEDED  //  COOLING: SHATTERED', size=18, anchor='mm', fill=BG)
    tag(g, 90, 110, 'SERVER_RACK_07 // TACHOMETER', size=17)
    kinetic_line(g, t, 21, 120, 76, hl={'1e30': GOLD}, maxw=1300)
    kinetic_line(g, t, 22, 120, 60, font='serif', upper=False, style='fade', maxw=1300)
    g.hud = dict(a=1, dx=(hsh(int(t * 30), 2) - 0.5) * 10 * p)


# ======================================================== PATENT 72.95 - 81.3 (inverted)
_rng = np.random.default_rng(4)
_BN = np.asarray(Image.fromarray((_rng.random((27, 48)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
_BN2 = np.asarray(Image.fromarray((_rng.random((108, 192)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
_BURN = (_BN * 0.75 + _BN2 * 0.25)
_yy = np.linspace(0, 1, H)[:, None]
_BURN = _BURN * 0.6 + (1 - _yy) * 0.4


def s_patent(g, t, lt):
    g.rect(0, 0, W, H, fill=PAPER)
    grid(g, 40, c=PGRID, cmaj=(196, 192, 182), major=5)
    INKC = BLACK
    # title block
    g.rect(1380, 860, 1860, 1030, stroke=INKC, w=2)
    g.text('PATENT #1945: VON NEUMANN CPU', 1400, 890, 20, INKC, 'mono', 1, 'lm')
    g.text('SHEET 1 OF 1   SCALE 1:1', 1400, 930, 15, INKC, 'monor', 1, 'lm')
    g.text('DRAWN: J. v. N.   1945-06-30', 1400, 960, 15, INKC, 'monor', 1, 'lm')
    g.text('STORED-PROGRAM ARCHITECTURE', 1400, 1000, 15, INKC, 'monor', 1, 'lm')
    # blocks
    blocks = [(260, 300, 640, 470, 'CONTROL UNIT'), (260, 560, 640, 730, 'ARITHMETIC / LOGIC'),
              (900, 300, 1280, 730, 'MEMORY'), (1500, 300, 1820, 730, 'INPUT / OUTPUT')]
    for (a, b, c, d, s) in blocks:
        g.rect(a, b, c, d, stroke=INKC, w=2.5)
        g.rect(a + 8, b + 8, c - 8, d - 8, stroke=INKC, w=1, a=0.4)
        g.text(s, (a + c) / 2, (b + d) / 2, 22, INKC, 'mono', 1, 'mm')
    for y in (385, 645):
        g.line((640, y, 900, y), INKC, 2)
        g.poly((900, y, 885, y - 8, 885, y + 8), fill=INKC)
    g.line((1280, 515, 1500, 515), INKC, 2)
    g.text('BUS', 1390, 495, 15, INKC, 'monor', 1, 'mm')
    # dimension line
    g.line((260, 260, 1280, 260), INKC, 1)
    g.text('1020 mm', 770, 245, 14, INKC, 'monor', 1, 'mm')
    for i, (lx, ly) in enumerate(((450, 470), (1090, 300))):
        g.circle(lx, ly, 14, stroke=INKC, w=1.5)
        g.text(str(i + 10), lx, ly, 12, INKC, 'mono', 1, 'mm')
    # laser piston metronome
    ph = (beat(t) / 2) % 1
    u = 0.5 - 0.5 * math.cos(ph * 2 * math.pi)
    px = lerp(330, 1210, u)
    py = 820
    g.rect(300, py - 20, 1240, py + 20, stroke=INKC, w=2)
    g.line((300, py, px, py), GOLD, 8)
    g.rect(px - 18, py - 34, px + 18, py + 34, fill=GOLD)
    fw = math.sin(ph * 2 * math.pi) > 0
    g.text('FORWARD ->' if fw else '<- BACKWARD', 770, py + 64, 24, GOLD if fw else INKC, 'monox', 1, 'mm')
    kinetic_line(g, t, 23, 150, 70, c=INKC, hl={'mlp,': GOLD}, maxw=1350)
    kinetic_line(g, t, 24, 150, 70, c=INKC, hl={"neumann's": INKC}, maxw=1350)
    tob = word_time(24, 3)
    if t > tob:
        sp = prog(t, tob, tob + 0.15)
        sc = lerp(2.5, 1, eo(sp))
        g.tf_set(W / 2, 540, -0.2, sc)
        g.rect(-430, -110, 430, 110, stroke=GOLD, w=10)
        g.rect(-410, -90, 410, 90, stroke=GOLD, w=3)
        g.tf_reset()
        g.text('OBSOLETE', W / 2, 540, 150, GOLD, 'sans', 1, 'mm', rot=-0.2, sx=sc)
        if sp < 1:
            g.flash = 0.0
    # burn
    bt = prog(t, 80.2, 81.25)
    if bt > 0:
        g.d.flush()
        a = np.asarray(g.img, np.float32)
        th = bt * 1.25
        burnt = _BURN < th
        edge = (_BURN < th + 0.04) & ~burnt
        out = a.copy()
        out[burnt] = BG
        out[edge] = np.array(GOLD, np.float32)
        char = (_BURN < th + 0.09) & ~burnt & ~edge
        out[char] = out[char] * 0.55
        g.img = Image.fromarray(out.astype(np.uint8))
        g.d = aggdraw.Draw(g.img)
        for i in range(120):
            x = hsh(i, 1) * W
            y = (hsh(i, 2) * H - (t - 80.2) * 300 * (0.5 + hsh(i, 3))) % H
            g.circle(x, y, 2 + 2 * hsh(i, 4), fill=GOLD, a=0.8 * bt)
    g.hud = dict(a=1, light=bt < 0.5)
    g.post = dict(glow=0.25 + 0.4 * bt, vig=0.4)


# ======================================================== SHARP LEFT TURN 81.3 - 89.3
def s_turn(g, t, lt):
    tl = word_time(25, 1)  # left
    turn = eio(prog(t, tl, tl + 0.35))
    vpx = W / 2 - turn * 900 + (1 - turn) * 0
    vpy = 470
    trav = t * 3.2
    # sky grid
    for i in range(10):
        y = vpy - i * i * 6
        g.line((0, y, W, y), GRID, 1)
    # road
    for side in (-1, 1):
        for lane in range(4):
            off = side * (220 + lane * 300)
            pts = []
            for k in range(30):
                z = 1 + k * 0.6
                bend = (turn * 900) * (1 - 1 / z)
                x = vpx + off / z + bend
                y = vpy + 600 / z
                pts += [x, y]
            g.line(pts, GOLD if lane == 0 else GRID2, 3 if lane == 0 else 1.5)
    # center dashes
    for k in range(30):
        z = 1 + ((k - trav * 3) % 30) * 0.6
        bend = (turn * 900) * (1 - 1 / z)
        x = vpx + bend
        y = vpy + 600 / z
        L = 40 / z
        g.line((x, y, x, y + L * 3), INK, 6 / z + 1)
    # barricade
    tb = word_time(26, 3)  # CDR
    if t > 83.2:
        appr = clamp((t - 83.2) / (tb - 83.2))
        z = lerp(12, 1.0, appr ** 1.4)
        bx = vpx + turn * 900 * (1 - 1 / z)
        by = vpy + 600 / z
        if t < tb:
            w_, h_ = 1500 / z, 420 / z
            g.rect(bx - w_ / 2, by - h_, bx + w_ / 2, by, fill=GOLD, a=0.15, stroke=GOLD, w=3)
            for i in range(10):
                xx = bx - w_ / 2 + i * w_ / 10
                g.line((xx, by, xx + w_ / 10, by - h_), GOLD, 4 / z * 3)
            g.text('CRITICAL DESIGN REVIEW (CDR)', bx, by - h_ * 0.62, 70 / z, INK, 'sans', 1, 'mm')
            g.text('DO NOT CROSS', bx, by - h_ * 0.3, 60 / z, GOLD, 'monox', 1, 'mm')
        else:
            q = t - tb
            for i in range(40):
                a = hsh(i, 1) * 6.28
                d = 1500 * q * (0.5 + hsh(i, 2))
                x = W / 2 + math.cos(a) * d; y = H / 2 + math.sin(a) * d
                r = q * 10 + i
                g.line((x, y, x + 90 * math.cos(r), y + 90 * math.sin(r)), GOLD, 5, clamp(1 - q))
            g.flash = math.exp(-q * 7) * 0.8
    # cockpit HUD
    g.circle(W / 2, 980, 150, stroke=INK, w=3, a=0.6)
    sa = -math.pi / 2 - turn * math.pi / 2 * (1 if t < tb + 0.5 else 1)
    g.line((W / 2, 980, W / 2 + 150 * math.cos(sa), 980 + 150 * math.sin(sa)), GOLD, 6)
    g.line((W / 2 - 150 * math.cos(sa + math.pi / 2) * 0, 980, W / 2 + 150 * math.cos(sa + math.pi), 980 + 150 * math.sin(sa + math.pi)), INK, 3, 0.6)
    g.text('STEER %+04d\u00b0' % int(-turn * 90), W / 2, 790, 22, GOLD, 'mono', 1, 'mm')
    readout(g, 92, 170, [('SPEED', '%d km/h' % (212 + int(t * 3) % 9)), ('AUTOPILOT', 'ENGAGED'), ('HUMAN_IN_LOOP', 'FALSE')], size=15)
    tag(g, 90, 110, 'AUTONOMOUS_DRIVE // FPV', size=17)
    kinetic_line(g, t, 25, 150, 74, hl={'left': GOLD, 'sharp': GOLD}, maxw=1350)
    kinetic_line(g, t, 26, 260, 74, hl={'cdr': GOLD}, maxw=1350)
    g.hud = dict(a=1, dx=-turn * 20 * math.exp(-(t - tl) * 3) if t > tl else 0)


# ======================================================== GATO 89.3 - 97.45
def s_gato(g, t, lt):
    if t >= 95.4:
        chorus(g, t, 28)
        return
    grid(g, 60)
    cx, cy = W / 2 + 330, H / 2 + 60
    rot = t * 0.9
    arms = 8
    for k in range(arms):
        a = rot + 2 * math.pi * k / arms
        ex, ey = cx + math.cos(a) * 300, cy + math.sin(a) * 300 * 0.85
        mx, my = cx + math.cos(a + 0.3) * 160, cy + math.sin(a + 0.3) * 160 * 0.85
        g.line((cx, cy, mx, my, ex, ey), INK, 4)
        g.circle(mx, my, 8, stroke=INK, w=2); g.circle(ex, ey, 10, fill=GOLD)
    g.circle(cx, cy, 60, stroke=GOLD, w=4)
    g.circle(cx, cy, 20, fill=GOLD)
    # 604 mini task screens in orbit rings
    n = 604
    for i in range(n):
        ring = i % 4
        a = -t * (0.5 + ring * 0.25) + 2 * math.pi * (i // 4) / (n / 4)
        r = 360 + ring * 55 + math.sin(t * 4 + i) * 8
        x = cx + math.cos(a) * r; y = cy + math.sin(a) * r * 0.85 + math.sin(t * 6 + i * 0.3) * 6 * pulse(t, 1, 4)
        if -20 < x < W + 20 and -20 < y < H + 20:
            g.rect(x - 8, y - 6, x + 8, y + 6, stroke=GOLD if (i + int(t * 8)) % 23 == 0 else GRID2, w=1.2)
    g.text('TASKS_JUGGLED: 604', cx, cy + 420, 22, GOLD, 'mono', 1, 'mm')
    # dangling human on fraying thread
    hx = 560 + math.sin(t * 1.6) * 40
    ty = 0
    hy = 560
    fray = prog(t, 91.0, 95.0)
    for f in range(6):
        if fray > (f + 1) / 7:
            # broken fiber, curls back up
            br = 300
            pts = [hx + (f - 2.5) * 3, 0, hx + (f - 2.5) * 3 + math.sin(t * 3 + f) * 30, br - 30 * f]
            g.line(pts, GOLD, 1.2, 0.6)
        else:
            sway = math.sin(t * 2 + f) * 4 * fray
            g.line((hx + (f - 2.5) * 3, ty, hx + (f - 2.5) * 1.2 + sway, hy - 90), GOLD, 1.4)
    # figure
    fy = hy - 90
    g.circle(hx, fy + 22, 18, stroke=INK, w=2.5)
    g.line((hx, fy + 40, hx, fy + 110), INK, 2.5)
    g.line((hx - 30, fy - 2, hx, fy + 50, hx + 30, fy - 2), INK, 2.5)
    kick = math.sin(t * 9) * 12
    g.line((hx - 20 + kick, fy + 170, hx, fy + 110, hx + 20 - kick, fy + 170), INK, 2.5)
    # lyric unraveling fiber-by-fiber
    li = 27
    ur = prog(t, 93.2, 95.3)
    if ur <= 0:
        kinetic_line(g, t, li, 900, 70, x=560, maxw=900, hl={'gato,': GOLD})
    else:
        s = "GATO, PLEASE DON'T LET ME GO"
        size = 64
        wtot = g.tsize(s, size, 'sans')[0]
        x = 560 - wtot / 2
        for i, ch in enumerate(s):
            cw = g.tsize(ch, size, 'sans')[0]
            k = clamp(ur * 1.6 - hsh(i, 9) * 0.6)
            yy = 900 + ei(k) * 260
            g.text(ch, x + cw / 2, yy, size, GOLD if i < 4 else INK, 'sans', 1 - k, 'mm')
            if k > 0 and ch != ' ':
                for f in range(4):
                    fx = x + cw * (f + 0.5) / 4
                    g.line((fx, 900 - 20, fx + math.sin(t * 5 + i + f) * 8, yy + 40), GOLD, 1, 0.6 * (1 - k * 0.5))
            x += cw
    tag(g, 90, 110, 'GATO // GENERALIST_AGENT  604 TASKS', size=17)
    g.hud = dict(a=1)


# ======================================================== PAPERCLIPS 97.45 - 98.95
def _clip(g, x, y, s, rot, c=GOLD, a=1.0):
    pts = []
    path = [(-1, 1.6), (-1, -1.6), (1, -1.6), (1, 1.2), (-0.5, 1.2), (-0.5, -1.0), (0.5, -1.0), (0.5, 0.8)]
    cr, sr = math.cos(rot), math.sin(rot)
    for (px, py) in path:
        px *= s; py *= s
        pts += [x + px * cr - py * sr, y + px * sr + py * cr]
    g.line(pts, c, max(1.5, s * 0.35), a)


def s_clips(g, t, lt):
    grid(g, 60)
    level = 0.15 + 0.83 * prog(t, 97.45, 98.95)
    ly = H - level * H
    # press
    bp = pulse(t, 2, 9)
    pressy = 180 + 230 * bp
    cam = Cam(cx=W / 2, cy=0, f=1000, dist=1000, ry=0.4, rx=0.2)
    V, E = box_mesh(420, 60, 200, oy=pressy)
    draw_edges(g, cam, V, E, c=INK, w=3, depth=False)
    for xx in (-180, 180):
        g.line(list(cam.p(xx, 0, 0)[:2]) + list(cam.p(xx, pressy - 30, 0)[:2]), GRID2, 10)
    V, E = box_mesh(520, 40, 240, oy=520)
    draw_edges(g, cam, V, E, c=INK, w=3, depth=False)
    # clips spawned on each 8th
    nb = int((t - 97.45) / (BEAT / 2)) + 1
    for i in range(min(nb * 6, 220)):
        born = 97.45 + (i // 6) * BEAT / 2
        q = t - born
        x = W / 2 + (hsh(i, 1) - 0.5) * 300 + (hsh(i, 2) - 0.5) * 900 * q
        y = 520 + 300 * q + 900 * q * q
        y = min(y, ly + 20 + hsh(i, 3) * 200)
        _clip(g, x, y, 14 + hsh(i, 4) * 8, hsh(i, 5) * 6 + q * 3)
    # flood level
    g.rect(0, ly, W, H, fill=GOLD, a=0.22)
    wav = []
    for i in range(65):
        x = i * W / 64
        wav += [x, ly + math.sin(i * 0.5 + t * 6) * 6]
    g.line(wav, GOLD, 3)
    for i in range(40):
        _clip(g, hsh(i, 7) * W, ly + 40 + hsh(i, 8) * (H - ly), 16, hsh(i, 9) * 6 + t, c=GOLDL, a=0.5)
    # gauge
    g.rect(1760, 200, 1810, 900, stroke=INK, w=2)
    g.rect(1764, 900 - 696 * level, 1806, 896, fill=GOLD)
    g.text('MATTER_CONVERTED: %d%%' % int(level * 100), 1740, 180, 20, GOLD, 'mono', 1, 'rm')
    kinetic_line(g, t, 29, 120, 78, hl={'paperclips': GOLD}, maxw=1300)
    tag(g, 90, 110, 'HYDRAULIC_PRESS // CLIP_MAXIMIZER', size=17)
    g.hud = dict(a=1)


# ======================================================== KILLSWITCH 98.95 - 102.45 (inverted)
def s_kill(g, t, lt):
    g.rect(0, 0, W, H, fill=PAPER)
    grid(g, 40, c=PGRID, cmaj=(196, 192, 182))
    INKC = BLACK
    cx, cy = W / 2, H / 2 + 60
    cam = Cam(cx=cx, cy=cy, f=1000, dist=1200, ry=0.5 + math.sin(t * 0.6) * 0.15, rx=0.35)
    # base
    V, E = box_mesh(440, 60, 440, oy=150)
    draw_edges(g, cam, V, E, c=INKC, w=3, depth=False)
    # button
    V, E = cyl_mesh(130, 60, 32, 2)
    draw_edges(g, cam, [(x, y + 90, z) for x, y, z in V], E, c=INKC, w=2.5, depth=False)
    top = [cam.p(130 * math.cos(a), 60, 130 * math.sin(a))[:2] for a in [2 * math.pi * i / 32 for i in range(32)]]
    g.poly([c for p in top for c in p], fill=GOLD, stroke=INKC, w=2)
    # glass case
    V, E = box_mesh(400, 380, 400, oy=-40)
    draw_edges(g, cam, V, E, c=INKC, w=2, a=0.7, depth=False)
    gx0, gy0, _ = cam.p(-200, -230, -200); gx1, gy1, _ = cam.p(200, 150, -200)
    for k in range(3):
        g.line((gx0 + 40 + k * 30, gy0 + 40, gx0 + 120 + k * 30, gy0 + 200), INKC, 2, 0.25)
    g.text('[KILLSWITCH]', cx, cy + 260, 34, INKC, 'monox', 1, 'mm')
    g.text('IN CASE OF MISALIGNMENT BREAK GLASS', cx, cy + 305, 15, INKC, 'monor', 1, 'mm')
    # PTO sticker
    tp = word_time(30, 3)
    if t > tp - 0.05:
        p = prog(t, tp - 0.05, tp + 0.12)
        sc = lerp(2.2, 1, eo(p))
        g.tf_set(cx + 40, cy - 60, 0.17, sc)
        g.rrect(-250, -120, 250, 120, 26, fill=BLACK)
        g.rrect(-238, -108, 238, 108, 20, stroke=GOLD, w=3)
        # palm tree
        g.line((-160, 80, -150, 20, -140, -40), GOLD, 8)
        for k in range(5):
            a = -math.pi + k * math.pi / 4 + 0.1
            g.line((-140, -40, -140 + 70 * math.cos(a), -40 + 40 * math.sin(a) + 25), GOLD, 7)
        g.ellipse(-150, 85, 70, 12, fill=GOLD)
        g.circle(160, -60, 26, fill=GOLD)
        g.tf_reset()
        g.text('OUT OF OFFICE', cx + 40 + 70 * sc * 0.98, cy - 90, 28 * sc, PAPER, 'sans', 1, 'mm', rot=0.17)
        g.text('ON PTO', cx + 40 + 60 * sc * 0.98, cy - 30 + 8, 52 * sc, GOLD, 'sans', 1, 'mm', rot=0.17)
        g.text('back: never', cx + 40 + 50 * sc, cy + 20 + 12, 22 * sc, PAPER, 'serif', 1, 'mm', rot=0.17)
    kinetic_line(g, t, 30, 150, 74, c=INKC, hl={'pto': GOLD, 'killswitch': INKC}, maxw=1350)
    kinetic_line(g, t, 31, 150, 66, c=INKC, font='serif', upper=False, style='fade', maxw=1350)
    tag(g, 90, 110, 'EMERGENCY_STOP // STATUS: UNATTENDED', size=17, c=INKC)
    g.hud = dict(a=1, light=True)
    g.post = dict(glow=0.2, vig=0.4)


TL = [
    (38.4, s_train, BG),
    (41.45, s_accel, BG),
    (53.3, s_sydney, BG),
    (60.45, s_basilisk, BG),
    (62.95, s_nvda, BG),
    (64.45, s_omega, BG),
    (65.95, s_flops, BG),
    (72.95, s_patent, PAPER),
    (81.3, s_turn, BG),
    (89.3, s_gato, BG),
    (97.45, s_clips, BG),
    (98.95, s_kill, PAPER),
]
