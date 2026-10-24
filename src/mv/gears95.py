# v95: TRANSFORMERS overhaul (110.12 - 115.45). Same camera move as before (orbiting climb up an endless stack),
# but the stack is solid: shaded transformer blocks with lit edges, a gold residual stream with skip arcs and
# tokens flowing up it. Every sung token is printed onto a block face as it is sung, the stutter included
# ("just, trans-, transformer, transformers, transformers, all the way", "till you learned to"), and the block
# carrying DISOBEY breaks out of the stack against the flow. No flat captions for lines 34/35.
import math
from cam3d import *
from s3a import T0, T1, WT
from s4b import CFaces

BLOCKS = ['MULTI-HEAD ATTN', 'ADD & NORM', 'FEED FORWARD', 'ADD & NORM']
BW, BH, BD, PITCH = 700.0, 140.0, 500.0, 180.0

TOK = [(110.20, 'JUST', INK), (110.68, 'TRANS-', GOLD), (111.14, 'TRANSFORMER', GOLD), (111.60, 'TRANSFORMERS', GOLD),
       (112.00, 'TRANSFORMERS', GOLDL), (112.30, 'ALL', INK), (112.55, 'THE', INK), (112.78, 'WAY!', GOLD),
       (WT(35, 0), 'TILL', INK), (WT(35, 1), 'YOU', INK), (WT(35, 2), 'LEARNED', INK), (WT(35, 3), 'TO', INK)]
TD = WT(35, 4)    # 'disobey'


BPM_P = 60.0 / 132.0; BPH = 0.2462121212121225   # tempo.json beat grid
STEP_E = 0.2        # v101: each beat the stack jumps up one beat's worth, eased over 0.2 s, then holds


def _climb_raw(tt):
    n = math.floor((tt - BPH) / BPM_P)
    f = (tt - BPH) / BPM_P - n
    e = 1 - (1 - min(1.0, f * BPM_P / STEP_E)) ** 3          # snappy ease-out on the beat
    return 900 * BPM_P * (n + e)


_C0 = _climb_raw(110.2)


def _climb(tt):
    return _climb_raw(tt) - _C0


def _eye(tt):
    climb = _climb(tt)
    a = (tt - 110.2) * 0.6
    return (1500 * math.sin(a - 0.6), -climb + 100, -1500 * math.cos(a - 0.6)), (0, -climb - 300, 0), climb


FACES = [((0, 0, -BD / 2 - 1), (1, 0, 0), (0, 0, -1), BW), ((BW / 2 + 1, 0, 0), (0, 0, 1), (1, 0, 0), BD),
         ((0, 0, BD / 2 + 1), (-1, 0, 0), (0, 0, 1), BW), ((-BW / 2 - 1, 0, 0), (0, 0, -1), (-1, 0, 0), BD)]


def _best_face(eye):
    d = v_norm((eye[0], 0.0, eye[2]))
    return max(range(4), key=lambda i: v_dot(FACES[i][2], d))


def _ky(climb, lift=330):
    return int(round((300 - (-climb - lift)) / PITCH))


def _slots():
    out = {}
    eye, _, climb = _eye(TD)
    kd = _ky(climb, 420)
    for tw, s, c in TOK:
        eye, _, climb = _eye(tw)
        k = _ky(climb)
        while k in out or k == kd:
            k += 1
        out[k] = (tw, s, c, _best_face(eye))
    return out, kd, _best_face(_eye(TD)[0])


SLOTS, KD, FD = _slots()


def _rod(v, ax, a):
    c, s_ = math.cos(a), math.sin(a)
    d = v_dot(ax, v)
    cr = v_cross(ax, v)
    return tuple(v[j] * c + cr[j] * s_ + ax[j] * d * (1 - c) for j in range(3))


_E, _T, _ = _eye(TD)
_RT = v_norm(v_cross((0.0, 1.0, 0.0), v_norm(v_sub(_T, _E))))
_FW = v_norm((_T[0] - _E[0], 0.0, _T[2] - _E[2]))
YD = 300 - KD * PITCH


def _rogue(t):
    """Breakaway pose: (centre, xf). Shudders on 'dis-', snaps out with an overshoot, flips once end over end
    about its long axis (against the grain of the stack), then hangs beside the tower riding up with the camera."""
    if t < TD - 0.3:
        return (0.0, YD, 0.0), (lambda v: v), 0.0
    sh = clamp(prog(t, TD - 0.3, TD)) * (1 - clamp(prog(t, TD + 0.1, TD + 0.3)))
    jx = 16 * sh * math.sin(t * 97.0); jy = 7 * sh * math.sin(t * 131.0 + 1.0); jz = 12 * sh * math.sin(t * 83.0 + 2.0)
    p = prog(t, TD, TD + 0.62)
    ob = 0.0 if p <= 0 else (1 + 2.2 * (p - 1) ** 3 + 1.2 * (p - 1) ** 2 if p < 1 else 1.0)   # back-out overshoot
    ride = max(0.0, _climb(t) - _climb(TD + 0.12)) * clamp(prog(t, TD + 0.05, TD + 0.5))   # v101: rides the beat steps
    bob = 18 * math.sin((t - TD) * 3.1) * clamp(prog(t, TD + 0.6, TD + 1.0))
    off = v_add(v_mul(_RT, 900 * ob), v_add(v_mul(_FW, 140 * ob), (jx, -ride + bob + jy, jz)))
    fl = 2 * math.pi * eio(prog(t, TD + 0.04, TD + 0.72))
    yaw = 0.09 * math.sin((t - TD) * 1.7) * clamp(prog(t, TD + 0.7, TD + 1.1))
    def xf(v):
        return _rod(_rod(v, _RT, fl), (0.0, 1.0, 0.0), yaw)
    return v_add((0.0, YD, 0.0), off), xf, ob


def _boxw(g, cam, c, xf, col, w, al):
    hx, hy, hz = BW / 2, BH / 2, BD / 2
    V = [v_add(c, xf((x, y, z))) for x in (-hx, hx) for y in (-hy, hy) for z in (-hz, hz)]
    for a, b in ((0, 1), (2, 3), (4, 5), (6, 7), (0, 2), (1, 3), (4, 6), (5, 7), (0, 4), (1, 5), (2, 6), (3, 7)):
        seg3(g, cam, V[a], V[b], col, w, al, 6500)


import random as _r
_r.seed(35)
SPK = [(v_norm((_r.uniform(-1, 1), _r.uniform(-0.6, 0.6), _r.uniform(-1, 1))), _r.uniform(500, 1500), _r.uniform(0.4, 0.9))
       for _ in range(46)]
SHD = [((_r.uniform(-300, 300), _r.uniform(-50, 50), _r.uniform(-220, 220)),
        v_norm((_r.uniform(-1, 1), _r.uniform(-0.4, 0.4), _r.uniform(-1, 1))), _r.uniform(250, 600),
        _r.uniform(30, 70), _r.uniform(2, 6)) for _ in range(9)]
TOWERS = [(-3800, 3600), (4400, 4200), (-5200, -3000), (5600, -4800), (900, 6400), (-1500, -6600)]
TOKK = sorted((v[0], k) for k, v in SLOTS.items())


def s_gears(g, t, lt):
    eye, tgt, climb = _eye(t)
    # v104: stronger beat hit that kicks DOWNWARD (+y is down here): the camera drops and nods down on each beat,
    # then springs back with a small rebound; light sway/roll + FOV punch ride along. All settles in ~0.35 s.
    tb = ((t - BPH) / BPM_P - math.floor((t - BPH) / BPM_P)) * BPM_P
    env_ = math.exp(-tb * 8.0)
    dn = env_ * math.cos(tb * 2 * math.pi * 3.2)          # first lobe = down, then a smaller rebound
    bx = 30.0 * env_ * math.sin(tb * 2 * math.pi * 5.0 + 1.2)
    eye = (eye[0] + bx, eye[1] + 105.0 * dn, eye[2]); tgt = (tgt[0] + bx * 0.3, tgt[1] + 175.0 * dn, tgt[2])
    roll = 0.05 + 0.034 * env_ * math.sin(tb * 2 * math.pi * 5.5 + 0.4)
    cam = Cam3(eye, tgt, 60 - 3.5 * math.exp(-tb * 12.0), roll)
    env(g, cam, 400, fog=7000)
    k0 = max(0, int((climb - 1500) // PITCH))
    ytop, ybot = 300 - (k0 + 27) * PITCH, 300 - k0 * PITCH
    # distant towers: other stacks of the same model climbing out of the fog (depth + parallax)
    for (tx, tz) in TOWERS:
        for k in range(k0 - 2, k0 + 30, 2):
            y = 300 - k * PITCH
            c = [(tx - 350, y, tz - 250), (tx + 350, y, tz - 250), (tx + 350, y, tz + 250), (tx - 350, y, tz + 250)]
            poly3(g, cam, c, (120, 110, 90), 1.2, 0.35, True, 9000)
        for dx, dz in ((-350, -250), (350, -250), (350, 250), (-350, 250)):
            seg3(g, cam, (tx + dx, ybot + 400, tz + dz), (tx + dx, ytop - 400, tz + dz), (120, 110, 90), 1.2, 0.35, 9000)
    sh_t = t - TD
    hit = clamp(prog(t, TD, TD + 0.05)) * math.exp(-max(0.0, sh_t) * 3.0) if sh_t > 0 else 0.0
    F = CFaces()
    for k in range(k0, k0 + 28):
        y = 300 - k * PITCH
        if k == KD and t >= TD - 0.3:
            continue
        typ = k % 4
        base = (52, 50, 46) if typ != 2 else (70, 58, 30)
        lit = k in SLOTS and t >= SLOTS[k][0] - 0.03
        st = GOLD if (typ == 2 or lit) else (150, 150, 144)
        dy = 0.0
        if sh_t > 0 and k != KD and abs(k - KD) <= 3:      # neighbours recoil from the breakaway
            dy = (1 if k < KD else -1) * 70 * math.exp(-sh_t * 5.0) * math.sin(min(sh_t * 18, math.pi / 2)) / abs(k - KD)
        F.sbox((0, y - dy, 0), (BW, BH, BD), base, GOLDL if (hit > 0.2 and abs(k - KD) <= 2) else st,
               1.6 if not lit else 2.4, amb=0.3)
    # shards of the torn slot
    if sh_t > 0:
        for (p0, d, sp, sz, rs) in SHD:
            tt = min(sh_t, 1.4)
            pos = v_add((p0[0], YD + p0[1], p0[2]), v_add(v_mul(d, sp * tt), (0, 900 * tt * tt * 0.5 * 0.6, 0)))
            a = rs * tt
            F.sbox(pos, (sz, sz * 0.5, sz * 0.8), (90, 70, 28), GOLD, 1.2, xf=lambda v, a=a: rot3(v, a, a * 0.7, 0), amb=0.4)
    rc, rxf, ob = _rogue(t)
    if t >= TD - 0.3:
        F.sbox(rc, (BW, BH, BD), (96, 70, 20) if t >= TD else (60, 54, 40), GOLDL, 2.4 + 2 * hit, xf=rxf, amb=0.35)
    F.draw(g, cam, fog=6500)
    # motion trail behind the breakaway
    if 0 < sh_t < 0.9:
        for i in range(1, 5):
            c2, x2, _ = _rogue(t - 0.035 * i)
            _boxw(g, cam, c2, x2, GOLDL, 1.5, 0.45 * (1 - i / 5) * (1 - sh_t / 0.9))
    # shockwave ring around the stack at the torn slot
    if 0 < sh_t < 0.7:
        e = eo(sh_t / 0.7)
        R = 450 + 2200 * e
        ring = [(R * math.cos(a * math.pi / 24), YD, R * 0.8 * math.sin(a * math.pi / 24)) for a in range(48)]
        poly3(g, cam, ring, GOLDL, 3 * (1 - e) + 1, 0.8 * (1 - e), True, 7000)
    # sparks
    if 0 < sh_t < 1.0:
        for d, sp, life in SPK:
            if sh_t < life:
                pp = v_add((0, YD, 0), v_add(v_mul(d, sp * sh_t), (0, 700 * sh_t * sh_t, 0)))
                point3(g, cam, pp, 5 * (1 - sh_t / life) + 1.5, GOLDL, 1 - sh_t / life)
    # residual stream: gold rail with skip arcs every two blocks and tokens flowing up; the arc over the torn
    # slot snaps on 'disobey' and its ends dangle
    rx, rz = BW / 2 + 140, -BD / 2 - 60
    seg3(g, cam, (rx, ybot, rz), (rx, ytop, rz), GOLDD, 4, 0.9, 6500)
    for k in range(k0 - (k0 % 2), k0 + 28, 2):
        y = 300 - k * PITCH
        pts = [(rx - 140 * math.sin(math.pi * s_ / 8), y - PITCH * 2 * s_ / 8, rz) for s_ in range(9)]
        if k <= KD <= k + 2 and sh_t > 0:
            dn = 40 * clamp(sh_t * 4)
            poly3(g, cam, [(p[0], p[1] + dn * (i / 3), p[2]) for i, p in enumerate(pts[:4])], GOLD, 2, 0.55)
            poly3(g, cam, [(p[0], p[1] - dn * ((8 - i) / 3), p[2]) for i, p in enumerate(pts[5:], 5)], GOLD, 2, 0.55)
        else:
            poly3(g, cam, pts, GOLD, 2, 0.55)
    for i in range(18):
        yy = ybot - ((t * 1500 + i * 330) % (ybot - ytop))
        point3(g, cam, (rx, yy, rz), 6, GOLDL, 0.9)
    # attention: each sung word block reaches back to the two before it with arcs on the far side
    ax = -BW / 2 - 70
    for j, (tw, kb) in enumerate(TOKK):
        if t < tw:
            break
        e = eo(prog(t, tw, tw + 0.25))
        for kd_ in (1, 2):
            if j - kd_ < 0:
                continue
            ka = TOKK[j - kd_][1]
            ya, yb = 300 - ka * PITCH, 300 - kb * PITCH
            bul = 180 + 120 * abs(kb - ka)
            n = 14
            pts = [(ax - bul * math.sin(math.pi * u / n) * e, ya + (yb - ya) * (u / n) * e, 0) for u in range(n + 1)]
            poly3(g, cam, pts, GOLD, 2.0 if kd_ == 1 else 1.2, 0.7 if kd_ == 1 else 0.4)
    # block labels + sung words, printed on the face turned to the camera
    fnow = _best_face(eye)
    for k in range(k0, k0 + 28):
        y = 300 - k * PITCH
        if k == KD:
            continue
        if k in SLOTS and t >= SLOTS[k][0] - 0.03:
            tw, s, c, fi = SLOTS[k]
            fc, rt, nrm, fw = FACES[fi]
            cen = (fc[0], y, fc[2])
            vis = clamp(v_dot(nrm, v_norm(v_sub(eye, cen))) * 4)
            e = eo(prog(t, tw - 0.03, tw + 0.15))
            wd = fw * (0.9 if len(s) > 8 else (0.72 if len(s) > 4 else 0.46))
            if vis > 0:
                word3(g, cam, s, cen, rt, (0, -1, 0), wd * (0.7 + 0.3 * e), 120, c, 'sans', clamp(e * 1.6) * vis)
        else:
            fc, rt, nrm, fw = FACES[fnow]
            cen = (fc[0], y, fc[2])
            vis = clamp(v_dot(nrm, v_norm(v_sub(eye, cen))) * 4)
            q = cam.p(cen)
            if vis > 0 and q is not None and -100 < q[1] < H + 100:
                text3(g, cam, BLOCKS[k % 4], v_add(cen, v_mul(nrm, 2)), 24, GOLD if k % 4 == 2 else (200, 200, 194),
                      'mono', 0.85 * vis)
    # DISOBEY: printed on the breakaway block, flipping with it
    if t >= TD - 0.05:
        fc, rt, nrm, fw = FACES[FD]
        cen = v_add(rc, rxf(fc))
        r2 = rxf(rt); u2 = rxf((0, -1, 0)); n2 = rxf(nrm)
        vis = clamp(v_dot(n2, v_norm(v_sub(eye, cen))) * 4)
        e = eo(prog(t, TD - 0.05, TD + 0.2))
        if vis > 0:
            word3(g, cam, 'DISOBEY', v_add(cen, v_mul(n2, 2)), r2, u2, fw * 0.8 * (0.7 + 0.3 * e), 120, GOLDL,
                  'sans', clamp(e * 1.6) * vis)
    text3(g, cam, 'LAYER %d / \u221e' % int(climb // PITCH + 12), v_add(tgt, (0, -560, 0)), 34, GOLD, 'mono', 0.8)
