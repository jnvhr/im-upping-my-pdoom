# v105: RLHF goes askew, now with the RLHF smiley mask (the same mask the shoggoth wore earlier) strapped over the
# reward model like a face. It smiles politely and bobs while the reward climbs; on 'askew' it gets knocked crooked
# (overshooting tilt + slip), its smile warps lopsided, glitch slices tear across it, and a gold shoggoth eye
# peers through one eye hole. Then it keeps wobbling on the beat as the tempo ramps up.
import math
from cam3d import *
from s3a import T0, T1, WT

BPH = 0.2462121212121225; BP = 60.0 / 132.0


def s_rlhf(g, t, lt):
    ta = WT(39, 2)
    sk = eback(prog(t, ta - 0.05, ta + 0.4))
    keys = [(120.5, (-600, -400, -1900), (0, -100, 0), 55, 0.0),
            (123.6, (700, -700, -1500), (0, -100, 0), 58, 0.0)]
    cam = cam_at(t, keys, punch=2.0, roll_add=-0.42 * sk, shake=25 * math.exp(-max(0, t - ta) * 3) * (t > ta))
    env(g, cam, 420, fog=6000)
    F = Faces()
    F.box((0, 180, 0), (900, 120, 300), GOLD, BG, 2.5)
    F.draw(g, cam)
    arc = [(560 * math.cos(a), -60 - 560 * math.sin(a), 0) for a in [math.pi * q / 40 for q in range(41)]]
    poly3(g, cam, arc, INK, 6, 1)
    for q in range(0, 41, 4):
        a = math.pi * q / 40
        seg3(g, cam, (520 * math.cos(a), -60 - 520 * math.sin(a), 0), (600 * math.cos(a), -60 - 600 * math.sin(a), 0), GOLD, 3, 1)
    na = lerp(math.pi * 0.5, math.pi * 0.05 + 0.3 * math.sin(t * 25) * sk, sk) + (noise1(t * 3, 1) - 0.5) * 0.3
    seg3(g, cam, (0, -60, -10), (500 * math.cos(na), -60 - 500 * math.sin(na), -10), GOLD, 10, 1)
    text3(g, cam, 'REWARD MODEL v3', (-560, 60, 0), 26, INK, 'mono')
    text3(g, cam, 'REWARD %+.2f' % (lerp(0.2, 9.99, sk)), (0, 120, -160), 44, GOLD, 'monox')
    text3(g, cam, 'HUMAN FEEDBACK: \u2588\u2588\u2588\u2588\u2591\u2591 OVERFIT', (0, 330, -160), 26, DIM, 'mono')
    # _mask(g, cam, t, ta, sk)   # v107: mask removed at user request (kept in rlhf105_mask.py)
    lyric3x(g, cam, t, 39, (0, -520, 0), *face_at(keys, 122, (0, -520, 0)), 1700, 140, INK,
            {'rlhf': GOLD, 'askew': GOLD}, depth=70)
    g.post = dict(glow=0.6 + 0.4 * sk)


def _mask(g, cam, t, ta, sk):
    t0 = T0(39) - 0.02
    ap = eback(prog(t, t0, t0 + 0.35))                      # pops in at the start of the line
    if ap <= 0:
        return
    S = 0.62 * ap
    tb = ((t - BPH) / BP) % 1.0 * BP                         # time since the last beat (source time)
    kick = math.exp(-tb * 9.0)
    # before askew: polite bob on the beat; after: crooked, slipping, wobbling harder on each beat
    bob = 14 * kick * (1 - sk)
    rot = -0.92 * sk + 0.10 * sk * kick * math.sin(tb * 30) + 0.03 * math.sin(t * 2.0) * (1 - sk)
    cx = 0 + 30 * sk; cy = -260 + bob - 30 * sk + 18 * sk * kick
    cz = -170
    c_, s_ = math.cos(rot), math.sin(rot)

    def mx(p, ox=0.0):
        x, y, z = p[0] * S, p[1] * S, (p[2] if len(p) > 2 else -3)
        return (cx + ox + x * c_ - y * s_, cy + x * s_ + y * c_, cz + z)
    # shadow plate behind so the gauge does not show through
    fill3(g, cam, [mx(p) for p in disc_pts((0, 0, 8), 262, 48)], BG, 0.9 * ap)
    fill3(g, cam, [mx(p) for p in disc_pts((0, 0, 0), 260, 48)], (225, 218, 200), 0.95 * ap, stroke=GOLD, w=3.5)
    # gold shoggoth eye behind the left hole (only after askew)
    pe = clamp(prog(t, ta + 0.05, ta + 0.35))
    for j, ex in enumerate((-90, 90)):
        hole = [mx(p) for p in disc_pts((ex, -60, -2), 34, 20)]
        fill3(g, cam, hole, BG, 1.0)
        if j == 0 and pe > 0:
            look = 6 * math.sin(t * 7.0)
            fill3(g, cam, [mx(p) for p in disc_pts((ex + look, -60, -3), 31 * pe, 16)], GOLD, pe)
            fill3(g, cam, [mx(p) for p in disc_pts((ex + look, -60, -4), 9 * pe, 10)], (5, 5, 5), pe)
            point3(g, cam, mx((ex + look - 8, -68, -5)), 3, INK, 0.8 * pe)
    # the smile: perfect arc, warping lopsided as it goes askew
    sm = []
    for q in range(25):
        a = math.pi * (0.15 + 0.7 * q / 24)
        u = q / 24.0
        droop = sk * (60 * u * u - 25 * (1 - u)) + 10 * sk * kick * math.sin(u * 9 + t * 20)
        sm.append(mx((150 * math.cos(a), 30 + 110 * math.sin(a) - droop, -2)))
    poly3(g, cam, sm, BG, 12 * S / 0.62, 1.0)
    # glitch slices tearing across the mask right on 'askew'
    gl = math.exp(-max(0.0, t - ta) * 6.0) * (t > ta - 0.02)
    if gl > 0.05:
        for k in range(5):
            yy = -200 + 100 * k + 40 * math.sin(t * 50 + k)
            off = (hsh(k, int(t * 30)) - 0.5) * 140 * gl
            pts = [mx((-260, yy), off), mx((260, yy), off), mx((260, yy + 18), off), mx((-260, yy + 18), off)]
            poly3(g, cam, pts, GOLDL if k % 2 else GOLD, 2.0, 0.9 * gl, True)
    text3(g, cam, 'RLHF_MASK.PNG', mx((0, 330, 0)), 22, GOLD, 'mono', ap * (1 - clamp(sk)))
