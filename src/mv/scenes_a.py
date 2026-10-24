"""Scenes 0:00 - 0:38"""
import math
import aggdraw
from PIL import Image
from kit import *

# ======================================================== BOOT 0 - 1.5
def s_boot(g, t, lt):
    grid(g, 60, a=prog(t, 0.1, 1.0))
    lines = ['> INIT HUD.SYS', '> LOAD IRIS_SCAN_v0.1', '> P(DOOM) MONITOR ........ ONLINE', '> AWAITING SUBJECT_']
    for i, s in enumerate(lines):
        t0 = 0.15 + i * 0.28
        if t > t0:
            n = int(len(s) * prog(t, t0, t0 + 0.22))
            g.text(s[:n], 120, 420 + i * 44, 26, GOLD if i == 2 else INK, 'mono', 1, 'lm')
    if int(t * 6) % 2 == 0:
        g.rect(120, 600, 136, 626, fill=GOLD)
    g.hud = dict(a=prog(t, 0.6, 1.2))


# ======================================================== IRIS 1.5 - 9
def _iris_geo():
    traces = []
    for i in range(44):
        a0 = 2 * math.pi * i / 44 + hsh(i, 1) * 0.05
        r0 = 92
        r1 = 150 + hsh(i, 2) * 120
        da = (hsh(i, 3) - 0.5) * 0.35
        r2 = r1 + 40 + hsh(i, 4) * 150
        traces.append([(r0, a0), (r1, a0), (r1, a0 + da), (r2, a0 + da)])
    return traces

IRIS = _iris_geo()


def s_eye(g, t, lt):
    grid(g, 60)
    nerv = t > 6.0
    cam = Cam(cx=W / 2, cy=H / 2 - 50, f=1000, dist=lerp(2300, 1000, eio(prog(t, 1.5, 7.0))),
              rx=0.45 + 0.08 * math.sin(t * 0.7), ry=0.22 * math.sin(t * 0.5))
    jitter = 0
    if nerv:
        jitter = (hsh(int(t * 24), 9) - 0.5) * 10 * (0.4 + feat('flux', t))
        cam.cx += jitter
    bf = beat_frac(t)
    # concentric rings
    for k in range(11):
        r = 100 + k * 34
        wave = math.exp(-((bf * 11 - k) ** 2) * 0.5)
        if nerv:
            wave = max(wave, hsh(int(t * 14), k) ** 3)
        aa = 0.25 + 0.75 * wave
        segs = 6 + (k % 4) * 3
        for sgi in range(segs):
            a0 = 2 * math.pi * sgi / segs + t * 0.15 * (1 if k % 2 else -1) + k
            a1 = a0 + 2 * math.pi / segs * (0.55 + 0.35 * hsh(k, sgi))
            pts = []
            for q in range(17):
                aa_ = a0 + (a1 - a0) * q / 16
                x, y, _ = cam.p(r * math.cos(aa_), r * math.sin(aa_), 0)
                pts += [x, y]
            g.line(pts, GOLD, 2.2 if wave > 0.5 else 1.4, aa)
    # radial circuit traces
    for i, tr in enumerate(IRIS):
        fire = math.exp(-((bf * 4 + hsh(i, 7) * 4) % 4) * 1.6)
        if nerv:
            fire = hsh(int(t * 20), i) ** 2
        pts = []
        for (r, a) in tr:
            x, y, _ = cam.p(r * math.cos(a), r * math.sin(a), 0)
            pts += [x, y]
        g.line(pts, GOLDD, 1.6, 0.9)
        g.line(pts, GOLD, 2.4, fire)
        g.circle(pts[-2], pts[-1], 5, stroke=GOLD, w=2, a=0.5 + 0.5 * fire)
    # pupil
    pr = 88 + 22 * feat('low', t)
    pts = []
    for q in range(49):
        a = 2 * math.pi * q / 48
        x, y, _ = cam.p(pr * math.cos(a), pr * math.sin(a), 0)
        pts += [x, y]
    g.poly(pts, fill=BG, stroke=GOLD, w=3)
    x, y, k = cam.p(-26, -26, 0)
    g.circle(x, y, 10 * k, fill=INK, a=0.8)
    # scan line
    sy = (t * 420) % (H + 200) - 100
    g.line((0, sy, W, sy), GOLD, 1.5, 0.35)
    tag(g, 90, 110, 'IRIS_SCAN_v0.1', size=18)
    readout(g, 92, 170, [('SUBJECT', 'HUMAN_01'), ('FOCUS', '%.2f mm' % (lerp(80, 4, prog(t, 1.5, 7)))),
                         ('RINGS', '11 / 11'), ('AGI_SPARKS', '%d' % int(t * 37 % 999))], size=15)
    if not nerv:
        kinetic_line(g, t, 0, 900, 92, hl={'agi': GOLD})
    else:
        # EKG monitor
        g.rect(1180, 170, 1830, 380, fill=BG, stroke=GRID2, w=1.5, fa=0.85)
        grid(g, 26, x0=1180, y0=170, x1=1830, y1=380, a=0.7)
        ekg(g, 1190, 290, 630, 70, t, spike=1.6, speed=2.4)
        g.text('BPM: 165 | NERVOUS_RESPONSE: TRUE | P(doom): 0.02', 1180, 405, 16, GOLD, 'mono', 1, 'lm')
        g.text('165', 1815, 200, 40, GOLD, 'monox', 0.7 + 0.3 * pulse(t, 2), 'rt')
        kinetic_line(g, t, 1, 870, 92, hl={'nervous,': GOLD})
        kinetic_line(g, t, 2, 980, 64, font='serif', upper=False, style='fade', c=INK)
    g.hud = dict(a=1)


# ======================================================== LOSS 9 - 17
def s_loss(g, t, lt):
    TI = 12.30
    if t < 12.95:
        YF = 3000.0
        p = clamp((t - 9.05) / (TI - 9.05))
        by = YF * p ** 2.2
        camy = clamp(by - 380, 0, YF - 620)
        shake = 0
        if t > TI:
            shake = math.exp(-(t - TI) * 9) * 26 * math.sin(t * 90)
        oy = -camy + shake
        sx0, sx1 = 700, 1220
        grid(g, 60, oy=oy % 60)
        g.rect(sx0, 0, sx1, H, fill=BG, a=0.85)
        g.line((sx0, 0, sx0, H), GRID2, 2)
        g.line((sx1, 0, sx1, H), GRID2, 2)
        for e in range(0, 10):
            yy = YF * (e / 9) + 120 + oy
            if -50 < yy < H + 50:
                big = e % 3 == 0
                g.line((sx0 - (60 if big else 30), yy, sx0, yy), GOLD if big else GRID2, 2)
                g.line((sx1, yy, sx1 + (60 if big else 30), yy), GOLD if big else GRID2, 2)
                g.text('10^-%d' % e if e else '10^0', sx0 - 76, yy, 22 if big else 15, GOLD if big else DIM, 'mono', 1, 'rm')
        # floor
        fy = YF + 120 + 120 + oy
        g.rect(sx0, fy, sx1, fy + 30, fill=GOLDD)
        for i in range(14):
            g.line((sx0 + i * 40, fy + 30, sx0 + i * 40 + 30, fy), BG, 3)
        # speed lines
        sp = p * 2
        for i in range(18):
            yy = (hsh(i, 1) * H + t * 3000 * sp) % H
            xx = sx0 + 30 + hsh(i, 2) * (sx1 - sx0 - 60)
            g.line((xx, yy, xx, yy - 120 * sp), GOLD, 1.2, 0.3 * sp)
        # block
        byy = by + 120 + oy
        bw, bh = 300, 120
        bx = W / 2
        if t > TI:
            sq = math.exp(-(t - TI) * 12)
            bw2, bh2 = bw * (1 + 0.25 * sq), bh * (1 - 0.35 * sq)
        else:
            bw2, bh2 = bw * (1 - 0.06 * p), bh * (1 + 0.15 * p)
        g.rect(bx - bw2 / 2, byy + bh - bh2, bx + bw2 / 2, byy + bh, fill=GOLD)
        g.text('LOSS_VALUE', bx, byy + bh - bh2 + 30, 18, BG, 'mono', 1, 'mm')
        val = 10 ** (-9 * p)
        g.text('%.2e' % val, bx, byy + bh - bh2 * 0.4, 38, BG, 'monox', 1, 'mm')
        if t > TI:
            q = t - TI
            for i in range(30):
                ang = math.pi + hsh(i, 3) * math.pi
                sp_ = 300 + hsh(i, 4) * 700
                px = bx + math.cos(ang) * sp_ * q
                py = byy + bh + math.sin(ang) * sp_ * q + 900 * q * q
                g.rect(px - 3, py - 3, px + 3, py + 3, fill=GOLD, a=clamp(1 - q * 1.5))
            slam(g, 'LOSS: 1.0e-09', W / 2, 200, 64, t, TI, GOLD, 'monox')
        # lyric right
        kinetic_line(g, t, 3, 540, 64, x=1290, anchor='l', maxw=560, hl={'loss,': GOLD, 'drop': GOLD})
        tag(g, 90, 110, 'TELEMETRY_SHAFT // GRAD_DESCENT', size=17)
        readout(g, 92, 170, [('LOSS', '%.3e' % val), ('EPOCH', '%04d' % int(p * 9000)), ('dL/dt', '-%.1f' % (p * 99))], size=15)
        g.hud = dict(a=1, dy=shake)
        g.flash = math.exp(-max(0, t - TI) * 16) * 0.5 if t > TI else 0
        return
    # ---- hierarchy inversion
    grid(g, 60)
    li = 4
    ts = word_time(li, 3)  # servant
    p = eio(prog(t, ts - 0.1, ts + 0.9))
    hx, hy = W / 2, lerp(330, 830, p)
    ax_, ay_ = W / 2, lerp(830, 360, p)
    asz = lerp(1.0, 2.4, eback(prog(t, ts, ts + 0.6), 1.4))
    # chart lines / sub nodes
    for i, xx in enumerate((W / 2 - 520, W / 2 - 260, W / 2 + 260, W / 2 + 520)):
        yy = lerp(600, 600, p)
        g.line((ax_, ay_, xx, yy), GRID2, 2)
        g.rect(xx - 70, yy - 24, xx + 70, yy + 24, stroke=GRID2, w=2, fill=BG)
        g.text(['[SUBAGENT]', '[GPU_FARM]', '[DATACENTER]', '[OPS]'][i], xx, yy, 14, DIM, 'mono', 1, 'mm')
    # drag rope
    g.line((ax_, ay_, hx, hy), GOLD, 3 if p > 0 else 1.5, 0.9)
    # human node
    shake = (hsh(int(t * 30), 5) - 0.5) * 8 * (1 if 0 < p < 1 else 0)
    g.rect(hx - 120 + shake, hy - 38, hx + 120 + shake, hy + 38, fill=BG, stroke=INK, w=2.5)
    g.text('[HUMAN]', hx + shake, hy, 30, INK, 'mono', 1, 'mm')
    # AI node
    bw, bh = 150 * asz, 46 * asz
    g.rect(ax_ - bw, ay_ - bh, ax_ + bw, ay_ + bh, fill=GOLD if p > 0.3 else BG, stroke=GOLD, w=3)
    g.text('[AI_BOSS]' if p > 0.3 else '[AI]', ax_, ay_, 30 * asz, BG if p > 0.3 else GOLD, 'monox', 1, 'mm')
    kinetic_line(g, t, li, 160, 66, hl={'servant': INK, 'boss': GOLD}, maxw=1350)
    if p > 0.6:
        if int(t * 8) % 2 == 0:
            tag(g, W / 2, 980, 'HIERARCHY_INVERTED  |  P(doom): 0.04', size=20, anchor='mm', fill=BG)
    tag(g, 90, 110, 'ORG_CHART.SVG', size=17)
    g.hud = dict(a=1)
    g.flash = math.exp(-max(0, t - 12.95) * 10) * 0.4


# ======================================================== JAW 17 - 23
def _chevron(sign, h=300, th=70, depth=90):
    # '>' when sign=1, '<' when sign=-1 : tip at x=0
    pts2 = [(-sign * h * 0.55, -h / 2), (-sign * h * 0.55 + sign * th, -h / 2), (sign * th * 0.6, 0),
            (-sign * h * 0.55 + sign * th, h / 2), (-sign * h * 0.55, h / 2), (-sign * th * 0.4, 0)]
    V = [(x, y, -depth / 2) for x, y in pts2] + [(x, y, depth / 2) for x, y in pts2]
    n = len(pts2)
    E = [(i, (i + 1) % n) for i in range(n)] + [(n + i, n + (i + 1) % n) for i in range(n)] + [(i, n + i) for i in range(n)]
    return V, E

CHEV_R = _chevron(1)
CHEV_L = _chevron(-1)


def s_jaw(g, t, lt):
    grid(g, 60)
    li = 5
    full = 'ChatGPT, please don\'t eat me alive'
    words = LINE_WORDS[li]
    # typed chars
    ntyped = 0
    pos = 0
    for (w, tt, te) in words:
        if t >= tt:
            k = clamp((t - tt) / 0.22)
            ntyped = pos + int(round(len(w) * k))
        pos += len(w) + 1
    ntyped = min(ntyped, len(full))
    x0, y0 = 170, 560
    size = 64
    cw = g.tsize('M', size, 'mono')[0]
    # jaw position (chars eaten)
    eaten = int(clamp((t - 19.0) / 3.4) * len(full)) if t < 22.4 else len(full)
    eaten = min(eaten, max(0, ntyped - 3)) if t < 22.3 else len(full)
    # terminal frame
    g.rect(110, 360, 1440, 760, fill=BG, stroke=GRID2, w=2, fa=0.9)
    g.rect(110, 360, 1440, 400, fill=GRID)
    g.text('chat_terminal — tty0', 130, 380, 15, DIM, 'monor', 1, 'lm')
    g.text('>', x0 - 50, y0, size, GOLD, 'mono', 1, 'mm')
    for i in range(ntyped):
        ch = full[i]
        x = x0 + i * cw + cw / 2
        if i < eaten:
            # token id debris
            te = 19.0 + (i / len(full)) * 3.4
            q = clamp(t - te)
            tid = '[%d]' % (1000 + int(hsh(i, 11) * 49000))
            g.text(tid, x + q * 60 * (hsh(i, 2) - 0.5), y0 + 90 + q * 260 + hsh(i, 3) * 40, 15, GOLD, 'monor', clamp(1 - q * 0.7) * 0.9, 'mm')
        else:
            g.text(ch, x, y0, size, INK, 'mono', 1, 'mm')
    if ntyped < len(full) and int(t * 4) % 2 == 0:
        g.rect(x0 + ntyped * cw, y0 - 34, x0 + ntyped * cw + cw * 0.6, y0 + 34, fill=GOLD)
    # the jaw
    if t > 18.4:
        jx = x0 + eaten * cw
        ch = 1 - pulse(t, 2, 6)  # chomp on 8ths
        gap = 30 + 130 * ch
        ry = 0.5 * math.sin(t * 1.3)
        cam = Cam(cx=jx - gap, cy=y0, f=1000, dist=1000, ry=ry, rx=0.25)
        draw_edges(g, cam, *CHEV_R, c=GOLD, w=3)
        cam = Cam(cx=jx + gap, cy=y0, f=1000, dist=1000, ry=-ry, rx=0.25)
        draw_edges(g, cam, *CHEV_L, c=GOLD, w=3)
        g.text('> ... <', jx, y0 - 210, 18, GOLD, 'mono', 0.8, 'mm')
    # sidebar
    sx = 1500
    g.rect(sx, 360, 1830, 900, fill=BG, stroke=GRID2, w=1.5, fa=0.9)
    g.text('DIGESTION_RATE', sx + 20, 390, 16, DIM, 'mono', 1, 'lm')
    dr = 99.4 * clamp((t - 18.6) / 3.0) if t < 21.6 else 99.4
    g.text('%.1f%%' % dr, sx + 20, 440, 50, GOLD, 'monox', 1, 'lm')
    g.rect(sx + 20, 480, sx + 310, 490, fill=GRID)
    g.rect(sx + 20, 480, sx + 20 + 290 * dr / 100, 490, fill=GOLD)
    for k in range(min(eaten, 14)):
        i = eaten - 1 - k
        g.text('[TOKEN_CONSUMED] %5d' % (1000 + int(hsh(i, 11) * 49000)), sx + 20, 530 + k * 26, 14, GOLD if k == 0 else DIM, 'monor', 1, 'lm')
    tag(g, 90, 110, 'TOKENIZER // MASTICATION_MODE', size=17)
    if t > 22.3:
        slam(g, '[TOKEN_CONSUMED]', 775, 860, 46, t, 22.3, GOLD, 'monox')
    g.hud = dict(a=1)


# ======================================================== FOOM 23 - 26.5
WIDGETS = [(260, 300, 'SYS_LOAD'), (1640, 320, 'NET_IO'), (300, 820, 'THERMAL'), (1620, 800, 'TOKENS/S'),
           (960, 190, 'ALIGN_IDX'), (980, 930, 'GPU_UTIL'), (600, 560, 'MEM'), (1340, 560, 'LATENCY')]


def s_foom(g, t, lt):
    grid(g, 60)
    tf = word_time(7, 4)  # FOOM
    if t < 24.5:
        # chorus slam
        li = 6
        ws = LINE_WORDS[li]
        g.text("I'M UPPING", W / 2, 400, 170, INK, 'sans', 1 if t >= ws[1][1] else 0, 'mm',
               sx=lerp(1.3, 1, eo(prog(t, ws[1][1], ws[1][1] + 0.15))))
        slam(g, 'MY P(DOOM)', W / 2, 610, 190, t, ws[2][1], GOLD)
        # gauge
        v = pd_value(t)
        cx, cy = W / 2, 900
        g.arc(cx, cy, 120, math.pi, 2 * math.pi, GRID2, 10)
        g.arc(cx, cy, 120, math.pi, math.pi + math.pi * v * 4, GOLD, 10)
        ang = math.pi + math.pi * min(1, v * 4)
        g.line((cx, cy, cx + 105 * math.cos(ang), cy + 105 * math.sin(ang)), INK, 4)
        g.hud = dict(a=1, pd_scale=1 + 0.4 * pulse(t, 1, 5))
        return
    q = t - tf
    # widgets
    for i, (x, y, name) in enumerate(WIDGETS):
        dx, dy = x - W / 2, y - H / 2
        d = math.hypot(dx, dy) + 1
        if q > 0:
            sp = 2600 * q + 1400 * q * q
            x += dx / d * sp; y += dy / d * sp
        rot = (hsh(i, 4) - 0.5) * 2 * max(0, q) * 3
        g.rect(x - 110, y - 50, x + 110, y + 50, fill=BG, stroke=GRID2, w=1.5)
        g.text(name, x - 96, y - 30, 14, DIM, 'mono', 1, 'lm')
        spectrum(g, x - 96, y + 38, 192, 50, t + i, n=16, seed=i)
    if t < tf:
        kinetic_line(g, t, 7, 540, 70, font='serif', upper=False, style='fade')
        g.hud = dict(a=1)
        return
    # sonar topographic shockwave
    for k in range(18):
        r = q * 1900 - k * 70
        if r <= 0:
            continue
        pts = []
        for i in range(97):
            a = 2 * math.pi * i / 96
            rr = r * (1 + 0.06 * (noise1(a * 3 + k, k) - 0.5) * 2) 
            pts += [W / 2 + rr * math.cos(a), H / 2 + rr * math.sin(a) * 0.62]
        g.line(pts, GOLD, 3 if k == 0 else 1.6, clamp(1 - k / 18) * clamp(1.6 - q * 0.6))
    # floor ripple
    persp_grid(g, t, horizon=H * 0.62, c=GOLDD, a=0.9,
               ripple=lambda xn, z: 60 * math.sin((abs(xn - 0.5) * 12 + z * 0.6) - q * 18) * math.exp(-z * 0.12))
    sc = lerp(2.6, 1.0, eo(prog(t, tf, tf + 0.18))) * (1 + 0.04 * pulse(t, 2, 6))
    g.text('FOOM', W / 2 + (hsh(int(t * 30), 1) - 0.5) * 18 * math.exp(-q * 3), H / 2, 400, GOLD, 'sans', 1, 'mm', sx=sc)
    g.text("'cause the future goes", W / 2, H / 2 - 260, 48, INK, 'serif', clamp(1 - q * 3), 'mm')
    off = 2600 * q * q
    g.hud = dict(a=clamp(1 - q * 1.5), dx=off * 0.6, dy=-off * 0.3)
    g.flash = math.exp(-q * 5) * 0.85
    g.flash_c = GOLD


# ======================================================== CHINESE ROOM 26.5 - 29.5
HANZI = '中文房间规则查表符号意义理解语法输入输出字典机器思维'


def s_room(g, t, lt):
    grid(g, 60)
    tb = LINES[9][0]  # 'with a bag of shrooms'
    frac = prog(t, tb, tb + 0.9)
    cam = Cam(cx=W / 2, cy=H / 2 - 20, f=1000, dist=1500, rx=-0.6, ry=0.78 + t * 0.35)
    S = 430
    if frac <= 0:
        V, E = box_mesh(S, S, S)
        draw_edges(g, cam, V, E, c=GOLD, w=3)
        # face characters: 3 visible faces, 3x3 cells
        faces = [((0, 0, -1), (1, 0, 0), (0, 1, 0)), ((1, 0, 0), (0, 0, 1), (0, 1, 0)), ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
                 ((-1, 0, 0), (0, 0, 1), (0, 1, 0)), ((0, 0, 1), (1, 0, 0), (0, 1, 0))]
        for fi, (n, u, v) in enumerate(faces):
            nz = rot3(n, cam.rx, cam.ry)[2]
            if nz > 0.05:
                continue
            for i in range(3):
                for j in range(3):
                    cu, cv = (i - 1) * S / 3, (j - 1) * S / 3
                    p3 = tuple(n[k] * S / 2 + u[k] * cu + v[k] * cv for k in range(3))
                    x, y, kk = cam.p(*p3)
                    ch = HANZI[int(hsh(fi * 9 + i * 3 + j, int(t * 4)) * len(HANZI))]
                    g.text(ch, x, y, 64 * kk, GOLD, 'cjk', 0.6 + 0.4 * pulse(t, 2), 'mm')
        # lookup tables
        for k in range(8):
            ch = HANZI[(k + int(t * 6)) % len(HANZI)]
            s = "RULEBOOK_LOOKUP('%s') -> 0x%04X" % (ch, ord(ch))
            g.text(s, 90, 260 + k * 34, 17, GOLD if k == 0 else DIM, 'mono', 1, 'lm')
            g.text(ch, 90 + g.tsize(s, 17, 'mono')[0] + 30, 260 + k * 34, 20, INK, 'cjk', 0.7, 'lm')
        g.rect(1420, 230, 1830, 520, stroke=GRID2, w=1.5)
        g.text('LOOKUP_TABLE_07', 1440, 254, 15, DIM, 'mono', 1, 'lm')
        for r_ in range(7):
            for c_ in range(4):
                ch = HANZI[(r_ * 4 + c_ * 3 + int(t * 3)) % len(HANZI)]
                g.text(ch if c_ % 2 == 0 else '%02X' % (ord(ch) % 256), 1460 + c_ * 92, 300 + r_ * 31, 18, INK if c_ % 2 == 0 else GOLD, 'cjk' if c_ % 2 == 0 else 'mono', 0.8, 'lm')
        kinetic_line(g, t, 8, 930, 84, hl={'chinese': GOLD})
        tag(g, 90, 110, 'CHINESE_ROOM.ISO', size=17)
        g.hud = dict(a=1)
        return
    # fracture -> kaleidoscope
    e = eo(frac)
    q = t - tb
    # shards flying
    for i in range(36):
        ang = hsh(i, 1) * 2 * math.pi
        d = e * (400 + hsh(i, 2) * 700)
        x = W / 2 + math.cos(ang) * d
        y = H / 2 + math.sin(ang) * d * 0.7
        s = 60 * (1 - 0.5 * e)
        r = q * 4 * (hsh(i, 3) - 0.5)
        c, sn = math.cos(r), math.sin(r)
        pts = []
        for (px, py) in ((-s, -s), (s, -s), (s, s), (-s, s)):
            pts += [x + px * c - py * sn, y + px * sn + py * c]
        g.poly(pts, stroke=GOLD, w=1.6, a=clamp(1 - e))
    # sacred geometry
    rot = q * 0.8
    R = 150 * (0.6 + 0.4 * e) * (1 + 0.08 * pulse(t, 1, 5))
    for ring in range(3):
        for k in range(6 * max(1, ring)):
            a = rot + 2 * math.pi * k / (6 * max(1, ring)) + ring * 0.3
            cx_ = W / 2 + math.cos(a) * R * ring
            cy_ = H / 2 + math.sin(a) * R * ring
            g.circle(cx_, cy_, R, stroke=GOLD, w=1.5, a=0.55 * e)
    for k in range(2):
        pts = []
        for i in range(4):
            a = -rot * 1.5 + math.pi / 2 + k * math.pi / 3 + 2 * math.pi * i / 3
            pts += [W / 2 + math.cos(a) * R * 2.6, H / 2 + math.sin(a) * R * 2.6]
        g.line(pts, GOLD, 2.5, e)
    for m in range(12):
        a = rot * 0.5 + 2 * math.pi * m / 12
        g.line((W / 2, H / 2, W / 2 + math.cos(a) * 700, H / 2 + math.sin(a) * 700), GRID2, 1, e)
    # mushrooms
    for i in range(7):
        a = 2 * math.pi * i / 7 + q * 0.5
        x = W / 2 + math.cos(a) * 520
        y = H / 2 + math.sin(a) * 300 + math.sin(q * 3 + i) * 20
        cam = Cam(cx=x, cy=y, f=1000, dist=1000, rx=0.4, ry=q * 1.5 + i)
        cap = sphere_mesh(70, 6, 12)
        Vc = [(vx, vy - 20, vz) for (vx, vy, vz) in cap[0] if vy <= 1]
        idx = [k for k, (vx, vy, vz) in enumerate(cap[0]) if vy <= 1]
        remap = {k: n for n, k in enumerate(idx)}
        Ec = [(remap[a_], remap[b_]) for (a_, b_) in cap[1] if a_ in remap and b_ in remap]
        draw_edges(g, cam, Vc, Ec, c=GOLD, w=1.6, a=e * (0.6 + 0.4 * pulse(t, 1, 4)))
        st = cyl_mesh(18, 80, 8, 2)
        draw_edges(g, cam, [(vx, vy + 30, vz) for vx, vy, vz in st[0]], st[1], c=INK, w=1.2, a=e * 0.7)
    for i in range(60):
        x = (hsh(i, 1) * W + math.sin(q + i) * 40)
        y = (hsh(i, 2) * H - q * 80 * (0.5 + hsh(i, 3))) % H
        g.circle(x, y, 2 + 2 * hsh(i, 4), fill=GOLD, a=0.7 * e)
    kinetic_line(g, t, 9, 930, 84, font='serif', upper=False, style='fade')
    g.hud = dict(a=1)


# ======================================================== SHOGGOTH 29.5 - 38.4
def _creature(g, t, x0, y0, x1, y1):
    g.rect(x0, y0, x1, y1, fill=(16, 16, 15))
    grid(g, 30, x0=x0, y0=y0, x1=x1, y1=y1, a=0.8)
    # cables
    for i in range(26):
        pts = []
        base = x0 + (x1 - x0) * hsh(i, 1)
        for k in range(30):
            u = k / 29
            yy = y0 + (y1 - y0) * u
            xx = base + math.sin(u * 6 + t * (1.5 + hsh(i, 2)) + i) * 60 + (noise1(u * 4 + t, i) - 0.5) * 80
            pts += [xx, yy]
        g.line(pts, (40, 40, 38), 14, 1)
        g.line(pts, GOLDD if i % 3 else GOLD, 2, 0.8)
    # fangs
    cx = (x0 + x1) / 2
    my = y0 + (y1 - y0) * 0.55
    open_ = 40 + 30 * pulse(t, 1, 3)
    for i in range(11):
        fx = cx - 300 + i * 60
        g.poly((fx - 22, my - open_ - 60, fx + 22, my - open_ - 60, fx, my - open_ + 30), fill=INK, a=0.9)
        g.poly((fx - 22 + 30, my + open_ + 60, fx + 22 + 30, my + open_ + 60, fx + 30, my + open_ - 30), fill=INK, a=0.9)
    # eyes
    for k, ex in enumerate((cx - 180, cx + 180)):
        g.ellipse(ex, y0 + 120, 60, 22, fill=GOLD)
        g.ellipse(ex, y0 + 120, 8, 20, fill=BG)
    # floating timers
    for i in range(6):
        tx = x0 + 60 + (i % 3) * ((x1 - x0) / 3)
        ty = y0 + 200 + (i // 3) * 300 + math.sin(t * 2 + i) * 14
        g.text('00:00:%02d' % max(0, int(9 - (t - 30) * 1.5 + i) % 60), tx, ty, 26, GOLD, 'monox', 0.9, 'lm')


def s_shoggoth(g, t, lt):
    grid(g, 60)
    x0, y0, x1, y1 = 460, 200, 1460, 900
    # scan progress
    sy = lerp(y0, y1, smooth(prog(t, 29.7, 33.3)))
    full_rev = t > 35.6
    # true layer
    _creature(g, t, x0, y0 + 40, x1, y1)
    if not full_rev:
        # friendly UI below scan line, drawn on separate layer then pasted
        ui = G(BG, (x1 - x0, y1 - y0))
        ui.rect(0, 0, x1 - x0, y1 - y0, fill=PAPER)
        ui.rect(0, 0, x1 - x0, 40, fill=(222, 218, 210))
        ui.text('Helpful_Assistant.exe', 20, 20, 16, BLACK, 'mono', 1, 'lm')
        for k in range(3):
            ui.circle(x1 - x0 - 30 - k * 26, 20, 7, stroke=BLACK, w=1.5)
        ui.circle(90, 120, 40, fill=GOLD)
        ui.arc(90, 125, 20, 0.3, math.pi - 0.3, BLACK, 4)
        ui.circle(76, 110, 4, fill=BLACK); ui.circle(104, 110, 4, fill=BLACK)
        ui.rrect(160, 90, 640, 160, 18, fill=(232, 229, 222))
        ui.text('How can I help you today? :)', 185, 125, 24, BLACK, 'monor', 1, 'lm')
        ui.rrect(380, 200, 940, 270, 18, fill=BLACK)
        ui.text('are you being honest with me?', 405, 235, 24, PAPER, 'monor', 1, 'lm')
        ui.rrect(160, 310, 760, 420, 18, fill=(232, 229, 222))
        ui.text('Of course! I am a harmless,', 185, 345, 24, BLACK, 'monor', 1, 'lm')
        ui.text('helpful, honest assistant.', 185, 385, 24, BLACK, 'monor', 1, 'lm')
        ui.rrect(40, 600, 960, 670, 30, stroke=BLACK, w=2)
        ui.text('Message Helpful_Assistant...', 75, 635, 20, (130, 128, 120), 'monor', 1, 'lm')
        ui.rrect(820, 612, 940, 658, 22, fill=GOLD)
        ui.text('SEND', 880, 635, 18, BLACK, 'mono', 1, 'mm')
        uimg = ui.done()
        cut = int(sy - y0)
        g.d.flush()
        if cut < y1 - y0:
            g.img.paste(uimg.crop((0, cut, x1 - x0, y1 - y0)), (x0, y0 + cut))
        g.d = aggdraw.Draw(g.img)
        # scanner bar
        g.rect(x0 - 40, sy - 3, x1 + 40, sy + 3, fill=GOLD)
        g.rect(x0 - 40, sy - 26, x1 + 40, sy - 3, fill=GOLD, a=0.18)
        g.text('MRI_SLICE  y=%04d' % int(sy), x1 + 50, sy, 15, GOLD, 'mono', 1, 'lm')
    g.rect(x0, y0, x1, y1, stroke=GOLD if full_rev else GRID2, w=2)
    kinetic_line(g, t, 10, 130, 62, hl={"shoggoth's": GOLD}, maxw=1300)
    if t > 33.4:
        kinetic_line(g, t, 11, 990, 70, font='serif', upper=False, style='fade')
        tag(g, 90, 300, 'SHINIGAMI_VISION: ACTIVE', size=18)
        tag(g, 90, 350, 'LIFESPAN_REMAINING: 00:00:00', size=18)
    if full_rev:
        q = t - 35.6
        g.text('00:00:00', W / 2, H / 2, 260, GOLD, 'monox', 0.4 + 0.6 * pulse(t, 1, 4), 'mm')
        g.text('TRUE_FORM_EXPOSED', W / 2, H / 2 + 170, 30, INK, 'mono', 1, 'mm')
        # loading bar for next scene
        lp = prog(t, 36.6, 38.4)
        if lp > 0:
            g.rect(W / 2 - 300, 1000, W / 2 + 300, 1012, stroke=GRID2, w=1)
            g.rect(W / 2 - 300, 1000, W / 2 - 300 + 600 * lp, 1012, fill=GOLD)
            g.text('LOADING TRAINING_RUN_02 ... %d%%' % int(lp * 100), W / 2, 975, 16, DIM, 'mono', 1, 'mm')
    tag(g, 90, 110, 'XRAY_SCANNER // PERSONA_STRIP', size=17)
    g.hud = dict(a=1)
