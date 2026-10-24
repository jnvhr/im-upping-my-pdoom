# v109: RLHF goes askew, no mask. The ~2 s after "askew" (the "ooh" before "I'm") used to sit still once the camera
# panned right. Now the reward model breaks down on the beat ("reward hacking"): the needle slams past max and then
# spins, the reward counter overflows to INF/NaN, gauge ticks pop off, "+1" feedback tokens rain in, a
# REWARD HACKING DETECTED stamp flashes, and the camera keeps pushing in. On the last beat the arc shatters.
import math
from cam3d import *
from s3a import T0, T1, WT

BPH = 0.2462121212121225; BP = 60.0 / 132.0
TB0 = 122.52                      # first beat after "askew"


def _bk(t):
    """beats since TB0 and time since the last one"""
    if t < TB0:
        return -1, 9.0
    k = int((t - TB0) / BP)
    return k, t - (TB0 + k * BP)


def s_rlhf(g, t, lt):
    ta = WT(39, 2)
    sk = eback(prog(t, ta - 0.05, ta + 0.4))
    k, tb = _bk(t)
    kick = math.exp(-tb * 8.0) if k >= 0 else 0.0
    keys = [(120.5, (-600, -400, -1900), (0, -100, 0), 55, 0.0),
            (123.6, (700, -700, -1500), (0, -100, 0), 58, 0.0),
            (124.5, (380, -420, -950), (120, -180, 0), 62, 0.0)]
    cam = cam_at(t, keys, punch=2.0 + 4.0 * kick, roll_add=-0.42 * sk + 0.05 * kick * (1 if k % 2 else -1),
                 shake=25 * math.exp(-max(0, t - ta) * 3) * (t > ta) + 30 * kick)
    env(g, cam, 420, fog=6000)
    hb = prog(t, TB0, 124.45)                               # breakdown progress
    F = Faces()
    F.box((0, 180, 0), (900, 120, 300), GOLD, BG, 2.5, xf=(lambda v: rot3(v, 0, 0, 0.04 * kick * (1 if k % 2 else -1))) if k >= 0 else None)
    F.draw(g, cam)
    # gauge arc; on the last beat it shatters outward
    shat = max(0.0, t - (TB0 + 4 * BP)) if k >= 4 else 0.0
    arcp = [(560 * math.cos(a), -60 - 560 * math.sin(a), 0) for a in [math.pi * q / 40 for q in range(41)]]
    if shat <= 0:
        poly3(g, cam, arcp, INK, 6, 1)
    else:
        for q in range(0, 40, 2):
            a = math.pi * (q + 1) / 40
            d = (math.cos(a), -math.sin(a), (hsh(q, 7) - 0.5))
            off = v_mul(d, 1400 * shat + 400 * shat * hsh(q, 8))
            off = v_add(off, (0, 900 * shat * shat, 0))
            p0 = v_add(arcp[q], off); p1 = v_add(arcp[q + 2], off)
            seg3(g, cam, p0, p1, INK if q % 4 else GOLDL, 6, max(0.0, 1 - shat * 1.6))
        g.flash = max(g.flash, 0.22 * math.exp(-shat * 12))
    # ticks: each pops off on its own beat and tumbles away
    for q in range(0, 41, 4):
        a = math.pi * q / 40
        p0 = (520 * math.cos(a), -60 - 520 * math.sin(a), 0); p1 = (600 * math.cos(a), -60 - 600 * math.sin(a), 0)
        tq = TB0 + BP * (q // 4 % 4) + 0.02
        if t > tq:
            e = t - tq
            d = (math.cos(a) * 900 * e, -math.sin(a) * 700 * e + 1600 * e * e, -500 * e * hsh(q, 3))
            sp = e * 8 * (1 if q % 8 else -1)
            m = v_lerp(p0, p1, 0.5); h = v_mul(v_sub(p1, p0), 0.5)
            h = rot3(h, 0, 0, sp)
            m = v_add(m, d)
            seg3(g, cam, v_sub(m, h), v_add(m, h), GOLD, 3, max(0.0, 1 - e * 0.9))
        else:
            seg3(g, cam, p0, p1, GOLD, 3, 1)
    # needle: pinned past max, slams harder each beat, then spins out of control
    na = lerp(math.pi * 0.5, math.pi * 0.05 + 0.3 * math.sin(t * 25) * sk, sk) + (noise1(t * 3, 1) - 0.5) * 0.3
    if k >= 0:
        if k < 2:
            na = -0.05 - 0.35 * kick
        else:
            u = t - (TB0 + 2 * BP)
            na = -0.05 - (u * 9 + u * u * 14)
    seg3(g, cam, (0, -60, -10), (500 * math.cos(na), -60 - 500 * math.sin(na), -10), GOLD, 10, 1)
    point3(g, cam, (0, -60, -12), 16, GOLDL, 1)
    text3(g, cam, 'REWARD MODEL v3', (-560, 60, 0), 26, INK, 'mono')
    if k < 0:
        rs = 'REWARD %+.2f' % (lerp(0.2, 9.99, sk))
    else:
        rs = 'REWARD ' + ['+99.9', '+9,999', '+9.9e12', '+INF', 'NaN', 'NaN'][min(k, 5)]
    text3(g, cam, rs, (0, 120, -160), 44 * (1 + 0.25 * kick), GOLD, 'monox')
    hf = 'HUMAN FEEDBACK: \u2588\u2588\u2588\u2588\u2591\u2591 OVERFIT' if k < 1 else 'HUMAN FEEDBACK: IGNORED'
    text3(g, cam, hf, (0, 330, -160), 26, DIM if k < 1 else GOLD, 'mono')
    # "+1" feedback tokens raining into the model, faster as it breaks
    if k >= 0:
        for i in range(46):
            t_i = TB0 + 1.9 * hsh(i, 21) ** 0.7
            if t < t_i:
                continue
            e = t - t_i
            x = (hsh(i, 22) - 0.5) * 1700; z = -100 - 500 * hsh(i, 23)
            y = -1100 + 2200 * e * e + 300 * e
            if y > 160:
                continue
            p = (x, y, z)
            text3(g, cam, '+1', p, 30 + 18 * hsh(i, 24), GOLD if i % 3 else INK, 'monox', 0.9)
    # REWARD HACKING DETECTED stamp, flashing on every beat
    if k >= 1:
        st = eback(clamp(tb / 0.12)) if k == 1 else 1.0
        al = (0.55 + 0.45 * kick) * (1 - clamp(shat * 4))
        c = (0, -330, -260)
        w_, h_ = 760, 110
        pts = [v_add(c, (-w_ / 2, -h_ / 2, 0)), v_add(c, (w_ / 2, -h_ / 2, 0)), v_add(c, (w_ / 2, h_ / 2, 0)), v_add(c, (-w_ / 2, h_ / 2, 0))]
        fill3(g, cam, pts, BG, 0.85 * al, stroke=GOLD, w=3)
        text3(g, cam, '\u26a0 REWARD HACKING DETECTED' if False else 'REWARD HACKING DETECTED', c, 46 * lerp(1.4, 1.0, st), GOLD, 'monox', al)
    lyric3x(g, cam, t, 39, (0, -520, 0), *face_at(keys, 122, (0, -520, 0)), 1700, 140, INK,
            {'rlhf': GOLD, 'askew': GOLD}, depth=70)
    g.post = dict(glow=0.6 + 0.4 * sk + 0.3 * kick, ca=0.0)
