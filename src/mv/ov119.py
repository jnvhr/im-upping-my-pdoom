# v119 overhauls.
# GPU: every one of the ~116k GPUs is drawn as its own point of light (numpy splat), so the end shot is a campus
#      made of 100,000+ distinct glittering dots, not gold rectangles. Starts on one H100 die.
# FENCES: a containment compound seen from above: four concentric chain-link fence rings (RLHF, RED TEAM, EVALS,
#      KILL SWITCH) around the gold cube. On each hit the cube grows and a shockwave flattens the next ring; its panels
#      topple outward, posts fly, sparks spray. The camera cranes up and back with every break.
import math
import numpy as np
import aggdraw
from PIL import Image
from scipy.ndimage import gaussian_filter
from cam3d import *
from s3a import T0, T1, WT
from ov116 import beats, capcam, glow
from ov118 import GPU, NCH, CS


# ======================================================== SAFETY FENCES 117.14 - 119.05
HITS = [117.38, 117.75, 118.18, 118.62]
FLAB = ['RLHF', 'RED TEAM', 'EVALS', 'KILL SWITCH']
RS = [480.0, 880.0, 1320.0, 1820.0]
FH = 430.0
SIDES = [((1, 0, 0), (0, 0, -1)), ((0, 0, 1), (1, 0, 0)), ((-1, 0, 0), (0, 0, 1)), ((0, 0, -1), (-1, 0, 0))]  # (along, outward)


def _fcam(t):
    ks = [(T0(37) - 0.05, -0.35, 0.30, 2450, -260, 52),
          (117.62, 0.00, 0.40, 2850, -200, 54),
          (118.02, 0.35, 0.52, 3350, -140, 54),
          (118.45, 0.70, 0.66, 3950, -80, 54),
          (T0(38) + 0.05, 1.00, 0.95, 5200, 0, 54)]
    for a, b in zip(ks, ks[1:]):
        if t <= b[0]:
            u = smooth(prog(t, a[0], b[0]))
            return [lerp(x, y, u) for x, y in zip(a[1:], b[1:])]
    return list(ks[-1][1:])


def s_fences(g, t, lt):
    t0 = T0(37); tE = T0(38)
    nb = sum(1 for h in HITS if t > h)
    hit = sum(math.exp(-(t - h) * 10) for h in HITS if t > h)
    yaw, pitch, dist, ty, fov = _fcam(t)
    tg = (0.0, ty, 0.0)
    eye = orbit(tg, dist, yaw, pitch)
    cam = Cam3(shake_eye(eye, t, 5 + 45 * min(1.5, hit)), tg, fov, 0.03 * math.sin(t * 1.7))
    env(g, cam)
    floor(g, cam, 0.0, 200, 36, GRID2, 0.7, 0, 0, fog=9000)
    bt = beats(t0 - 0.5, t + 0.001)
    lb = bt[-1] if bt else t0
    pb = math.exp(-(t - lb) * 8)
    # shockwaves on the ground
    for k, h in enumerate(HITS):
        e = t - h
        if 0 < e < 0.6:
            R_ = RS[k] * (0.5 + 2.2 * eo(e / 0.6))
            poly3(g, cam, [(R_ * math.cos(q * math.pi / 32), -3, R_ * math.sin(q * math.pi / 32)) for q in range(65)], GOLDL, 6, 1 - e / 0.6, fog=9000)
    S = SFaces()
    links = []
    for k, Rk in enumerate(RS):
        e = t - HITS[k]
        broke = e > 0
        big = k == 3
        col = INK if big else (150, 150, 144)
        npan = 3 + k
        P = 2 * Rk / npan
        for si, (al_, out) in enumerate(SIDES):
            o = v_mul(out, Rk)
            for pi in range(npan):
                u0 = -Rk + pi * P
                key = k * 100 + si * 10 + pi
                dl = hsh(key, 3) * 0.10
                ee = max(0.0, e - dl) if broke else 0.0
                th = min(1.5, 2.6 * ee * ee * 6 + 1.2 * ee) if broke else 0.0
                slide = 900 * eo(clamp(ee / 0.5)) * (0.6 + 0.6 * hsh(key, 4)) if broke else 0.0
                lift = -500 * ee + 1400 * ee * ee if (broke and hsh(key, 5) < 0.25) else 0.0
                base = v_add(o, v_mul(out, slide))
                def W_(uu, hh, base=base, th=th, lift=lift):
                    p = v_add(base, v_mul(al_, uu))
                    return (p[0] + out[0] * hh * math.sin(th), -hh * math.cos(th) + (lift if lift < 0 else 0) * (hh / FH), p[2] + out[2] * hh * math.sin(th))
                fa = 1.0 - clamp((ee - 0.35) / 0.4) if broke else 1.0
                if fa <= 0.02:
                    continue
                # post at the panel start
                pa, pt = W_(u0 + 4, 0), W_(u0 + 4, FH + 40)
                S.tube([pa, pt], 14, (110, 110, 104), None, 5, amb=0.45)
                S.tube([W_(u0 + 4, FH * 0.55), W_(u0 + 4, FH * 0.7)], 16, GOLD, None, 5, amb=0.6)
                # rails
                links.append((W_(u0, FH), W_(u0 + P, FH), col, 3, fa))
                links.append((W_(u0, 8), W_(u0 + P, 8), col, 2, fa))
                # chain-link diagonals
                sp = 70.0
                n_ = int((P + FH) / sp)
                for q in range(1, n_):
                    d = q * sp
                    # line u - h = const and u + h = const, clipped to the panel rectangle
                    a0 = (min(d, P), max(0.0, d - P)); a1 = (max(0.0, d - FH), min(d, FH))
                    links.append((W_(u0 + a0[0], a0[1]), W_(u0 + a1[0], a1[1]), col, 1.3, 0.75 * fa))
                    links.append((W_(u0 + P - a0[0], a0[1]), W_(u0 + P - a1[0], a1[1]), col, 1.3, 0.75 * fa))
                # barbed coil along the top
                if not broke or ee < 0.3:
                    cp = [W_(u0 + P * s / 10, FH + 30 + 22 * math.sin(s * 2.1)) for s in range(11)]
                    for a, b in zip(cp, cp[1:]):
                        links.append((a, b, col, 1.6, fa))
        # label above the far side of the ring (readable, never in the lens)
        fx, fz = -math.sin(yaw), math.cos(yaw)
        lp = (fx * Rk, -FH - 180, fz * Rk)
        if not broke and k == nb:
            la = clamp((t - (HITS[k - 1] if k else T0(37))) / 0.12)
            text3(g, cam, 'FENCE %02d' % (k + 1), v_add(lp, (0, -150, 0)), 80, DIM, 'mono', la)
            text3(g, cam, FLAB[k], lp, 150 if big else 130, GOLD, 'monox', la)
        elif broke and e < 0.35:
            text3(g, cam, FLAB[k], v_add(lp, (fx * 700 * e, -600 * e + 1600 * e * e, fz * 700 * e)), 130, GOLDL, "monox", 1 - e / 0.35)
    S.draw(g, cam, fog=9000)
    for a, b, c, w, al in links:
        seg3(g, cam, a, b, c, w, al, fog=9000)
    # floodlights at the compound corners
    for k in (1, 3):
        for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            if t > HITS[k]:
                continue
            p = (sx * RS[k], -FH - 160, sz * RS[k])
            glow(g, cam, p, 90, GOLD, 0.55)
    # sparks off each break
    for k, h in enumerate(HITS):
        e = t - h
        if 0 < e < 0.7:
            for q in range(70):
                a = hsh(q, k) * 6.283
                sp = 900 + 1500 * hsh(q, k + 5)
                p = (math.cos(a) * (RS[k] + sp * e), -FH * hsh(q, 7) - 900 * e * hsh(q, 8) + 1800 * e * e, math.sin(a) * (RS[k] + sp * e))
                point3(g, cam, p, 5, GOLDL if q % 3 else INK, 1 - e / 0.7)
    # the gold cube at the centre: grows with every fence it breaks, punches on the beat
    sz = (230 + 95 * nb + 60 * min(1.0, hit)) * (1 + 0.04 * pb)
    cy = -sz * 0.7 - 40
    C = SFaces()
    C.sbox((0, 0, 0), (sz, sz, sz), GOLD, GOLDL, 2, xf=lambda v: v_add(rot3(v, t * 1.6, t * 1.1, 0.3), (0, cy, 0)), amb=0.45)
    C.draw(g, cam)
    glow(g, cam, (0, cy, 0), sz * 1.6 + 400 * min(1.0, hit), GOLD, 0.3 + 0.35 * min(1.0, hit))
    g.flash = max(g.flash, 0.16 * max([math.exp(-(t - h) * 16) * (1.5 if i == 3 else 1) for i, h in enumerate(HITS) if t > h] or [0]))
    g.flash_c = GOLDL
    camc, c, r, u = capcam()
    lyric3x(g, camc, t, 37, v_add(c, v_mul(camc.u, 345)), r, u, 1500, 110, INK, {'safety': GOLD, 'fence': GOLD}, depth=40)


# ======================================================== HUNDRED THOUSAND GPU 119.05 - 120.82
def _proj(cam, P):
    d = P - np.array(cam.eye)
    x = d @ np.array(cam.r); y = d @ np.array(cam.u); z = d @ np.array(cam.f)
    k = cam.F / np.maximum(z, 1.0)
    return cam.cx + x * k, cam.cy + y * k, z


CH3 = np.stack([GPU['chips'][:, 0], np.zeros(NCH), GPU['chips'][:, 1]], 1)
TW = np.array([hsh(i, 11) for i in range(NCH)])   # twinkle phase per GPU


def _D(t):
    t0 = T0(38); tE = T0(39)
    u = prog(t, t0 - 0.02, 120.25)
    w = 1 - (1 - u) ** 2.4
    return math.exp(lerp(math.log(170.0), math.log(30000.0), w)) * (1 + 0.10 * smooth(prog(t, 120.25, tE)))


def _splat(g, sx, sy, inten, col, sig_core=0.6, glow_k=0.0):
    """additive points onto the frame (bilinear splat + blur)"""
    g.d.flush()
    buf = np.zeros((H, W), np.float32)
    ok = (sx >= 0) & (sx < W - 1) & (sy >= 0) & (sy < H - 1)
    x = sx[ok]; y = sy[ok]; v = inten[ok]
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int)
    fx = x - x0; fy = y - y0
    np.add.at(buf, (y0, x0), v * (1 - fx) * (1 - fy))
    np.add.at(buf, (y0, x0 + 1), v * fx * (1 - fy))
    np.add.at(buf, (y0 + 1, x0), v * (1 - fx) * fy)
    np.add.at(buf, (y0 + 1, x0 + 1), v * fx * fy)
    core = gaussian_filter(buf, sig_core) * 3.0
    tot = core
    if glow_k > 0:
        tot = tot + gaussian_filter(buf, 6.0) * glow_k * 40
    img = np.asarray(g.img).astype(np.float32)
    img += np.minimum(tot, 1.6)[..., None] * np.array(col, np.float32)[None, None, :]
    g.img = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    g.d = aggdraw.Draw(g.img)


def s_gpu(g, t, lt):
    t0 = T0(38); tg = WT(38, 2); tE = T0(39)
    bt = beats(t0 - 0.5, t + 0.001)
    lb = bt[-1] if bt else t0
    pb = math.exp(-(t - lb) * 8)
    D = _D(t) * (1 - 0.03 * pb)
    u = prog(t, t0, tE)
    yaw = 0.25 + 0.85 * smooth(u)
    pitch = lerp(1.25, 0.36, smooth(prog(t, t0, 120.45)))
    c0 = GPU['c0']
    w = smooth(prog(t, t0, 120.2))
    tg3 = (float(c0[0]) * (1 - w), 0.0, float(c0[1]) * (1 - w))
    eye = orbit(tg3, D, yaw, pitch)
    cam = Cam3(eye, tg3, 55, 0.04 * math.sin(t * 1.7))
    env(g, cam)
    Rl = 1.1 * D + 60
    n = int(np.searchsorted(GPU['dsorted'], Rl))
    if t > 120.2:
        n = NCH
    rank = GPU['rank']
    sx, sy, sz = _proj(cam, CH3)
    px = CS * cam.F / np.maximum(sz, 1.0)
    vis = (sz > 40) & (sx > -200) & (sx < W + 200) & (sy > -200) & (sy < H + 200)
    lit = rank < n
    # big chips: real packages with die + HBM; small ones become points of light
    quad = vis & (px > 9)
    qa = np.clip((px - 9) / 8, 0, 1)
    idx = np.nonzero(quad)[0]
    if len(idx) > 2600:
        idx = idx[np.argsort(sz[idx])[:2600]]
    C = GPU['chips']
    for e in idx:
        cx, cz = C[e, 0], C[e, 1]
        al = float(qa[e])
        q = [(cx - 50, 0, cz - 50), (cx + 50, 0, cz - 50), (cx + 50, 0, cz + 50), (cx - 50, 0, cz + 50)]
        fill3(g, cam, q, (40, 40, 37), al)
        dq = [(cx - 32, 0, cz - 32), (cx + 32, 0, cz - 32), (cx + 32, 0, cz + 32), (cx - 32, 0, cz + 32)]
        fill3(g, cam, dq, GOLD if lit[e] else (72, 72, 66), al)
        if px[e] > 70:
            for s_ in (-1, 1):
                for r_ in (-1, 0, 1):
                    hb = (cx + s_ * 42, 0, cz + r_ * 26)
                    fill3(g, cam, [(hb[0] - 6, 0, hb[2] - 10), (hb[0] + 6, 0, hb[2] - 10), (hb[0] + 6, 0, hb[2] + 10), (hb[0] - 6, 0, hb[2] + 10)], (96, 96, 90), al)
            poly3(g, cam, q + [q[0]], GOLDD, 1.5, al)
        if lit[e] and px[e] > 40:
            glow(g, cam, (cx, -4, cz), 55, GOLD, 0.35 * al)
    # hall + pod outlines (faint) so the rows read as a datacenter
    for name, hx, hz, a0 in (('halls', 9 * 3300.0 / 2 + 300, 9 * 1700.0 / 2 + 300, 0.8), ('pods', 5 * 600.0 / 2 + 60, 4 * 340.0 / 2 + 60, 0.35)):
        Cc = GPU[name]
        hpx = 2 * hx * cam.F / max(D, 1.0)
        if hpx < 30:
            continue
        aa = a0 * clamp((hpx - 30) / 60)
        if name == 'pods':
            aa *= clamp((4000 - hpx) / 2000)
        if aa < 0.03:
            continue
        P3 = np.stack([Cc[:, 0], np.zeros(len(Cc)), Cc[:, 1]], 1)
        cx_, cy_, cz_ = _proj(cam, P3)
        ok = np.nonzero((cz_ > 100) & (cx_ > -W) & (cx_ < 2 * W) & (cy_ > -H) & (cy_ < 2 * H))[0][:900]
        for e in ok:
            x, z = Cc[e, 0], Cc[e, 1]
            q = [(x - hx, -2, z - hz), (x + hx, -2, z - hz), (x + hx, -2, z + hz), (x - hx, -2, z + hz)]
            poly3(g, cam, q + [q[0]], GOLDD if name == 'halls' else GRID2, 2 if name == 'halls' else 1.2, aa, closed=False)
    # every other GPU as its own point of light: lit ones twinkle gold, unlit ones are dim
    pts = vis & ~(quad & (qa > 0.95))
    pts[idx] = pts[idx] & (qa[idx] < 0.95)
    fade = np.where(quad, 1 - qa, 1.0)
    dist = np.hypot(C[:, 0] - tg3[0], C[:, 1] - tg3[2])
    wave = np.exp(-np.abs(dist - (t - lb) * 2.5 * D) / (0.08 * D)) * pb
    tw = 0.75 + 0.25 * np.sin(t * 9 + TW * 40)
    near = np.clip(px / 5, 0.45, 1.0)
    il = np.where(lit, (1.5 * tw + 0.9 * wave) * near, 0.22) * fade
    _splat(g, sx[pts], sy[pts], il[pts].astype(np.float32), (255, 196, 70), glow_k=0.12, sig_core=0.5)
    g.post = dict(glow=0.3)
    if t < t0 + 0.25:
        g.flash = max(g.flash, 0.2 * (1 - prog(t, t0, t0 + 0.25))); g.flash_c = GOLDL
    shown = min(100000, n)
    camc, c, r, uu = capcam()
    word3(g, camc, 'H100 \u00d7 %s' % format(shown, ','), v_add(c, v_mul(camc.u, -150)), r, uu, 820 + 120 * pb * (t > tg), 200, GOLD, 'monox', 1, x=True, depth=60, n=6)
    lyric3x(g, camc, t, 38, v_add(c, v_mul(camc.u, -345)), r, uu, 1500, 115, INK, {'gpu': GOLD, 'thousand': GOLD}, depth=40)
