"""3D scenes 1:42.4 - end"""
import math
import aggdraw
from PIL import Image
from cam3d import *
from s3a import env, dust, chorus, T0, T1, WT
from scenes_c import _hand, CODE

# ======================================================== FUSE 102.4 - 104.6
def _fuse(u):
    return (-1600 + 1600 * u + 220 * math.sin(u * 9), 380 - 30 * math.sin(u * 5), -400 + 1800 * u + 300 * math.sin(u * 4))


def s_fuse(g, t, lt):
    FE = 105.88   # v93: the sung 'fu-u-u-use' melisma runs to ~105.9 (pitch steps 525 -> 465 -> 390 Hz)
    u = prog(t, WT(32, 3), FE)
    sp = _fuse(u)
    ah = _fuse(min(1, u + 0.12))
    eye = (sp[0] - 350, sp[1] - 300, sp[2] - 650)
    if u <= 0:
        eye = v_lerp((-2400, -900, -1800), eye, eo(prog(t, 102.4, WT(32, 3))))
    cam = Cam3(shake_eye(eye, t, 8), v_lerp(sp, ah, 0.5), 58, 0.08 * math.sin(t * 2))
    env(g, cam, 420, fog=6000)
    pts = [_fuse(k / 120) for k in range(121)]
    k0 = int(u * 120)
    poly3(g, cam, pts[:k0 + 1], GRID, 3, 0.8)
    poly3(g, cam, pts[k0:], INK, 4, 1)
    # spark
    for i in range(40):
        d = (hsh(i, int(t * 30)) - 0.5, -hsh(i, int(t * 30) + 1) * 1.2, hsh(i, int(t * 30) + 2) - 0.5)
        point3(g, cam, v_add(sp, v_mul(d, 120 * hsh(i, 9))), 4, GOLDL if i % 3 else GOLD, 0.9)
    point3(g, cam, sp, 16 * (1 + pulse(t, 2, 6)), GOLDL, 1)
    # bomb
    bc = _fuse(1.0)
    mesh3(g, cam, *sphere_mesh(320, 9, 18), c=GOLD, w=2.2, xf=xform((bc[0], bc[1] - 320, bc[2]), ry=t * 0.5))
    text3(g, cam, 'T-%.2f' % max(0, (FE - t)), (bc[0], bc[1] - 760, bc[2]), 70, GOLD, 'monox')
    c, r, uu = ahead(cam, 1000, yaw=0.1)
    lyric3x(g, cam, t, 32, v_add(c, v_mul(cam.u, -250)), r, uu, 1600, 120, INK, {'lit': GOLD, 'fuse': GOLD}, depth=60, hold=1.25)


# ======================================================== ORTHOGONALITY 104.6 - 110.2
def s_ortho(g, t, lt):
    keys = [(105.92, orbit((0, -300, 300), 2300, -1.0, 0.45), (0, -300, 300), 52, 0.0),
            (107.0, orbit((0, -300, 300), 1900, -0.3, 0.3), (0, -350, 200), 55, 0.03),
            (110.2, orbit((0, -300, 300), 2100, 0.9, 0.5), (0, -300, 300), 55, -0.05)]
    cam = cam_at(t, keys, punch=1.5)
    # three orthogonal grid planes
    grid3(g, cam, (0, 0, 1000), (1, 0, 0), (0, 1, 0), 10, 10, 100, GRID, 0.8, 1.0, fog=0)
    grid3(g, cam, (-1000, 0, 0), (0, 1, 0), (0, 0, 1), 10, 10, 100, GRID, 0.8, 1.0, fog=0)
    ax = [((1, 0, 0), 'INTELLIGENCE \u2192', GOLD), ((0, -1, 0), 'GOALS \u2191', INK), ((0, 0, 1), 'VALUES', DIM)]
    for d, nm, c in ax:
        seg3(g, cam, (0, 0, 0), v_mul(d, 1000), c, 5, 1)
        text3(g, cam, nm, v_mul(d, 1150), 34, c, 'mono')
    # vectors exploring the intelligence axis with arbitrary goals
    for i in range(14):
        e = prog(t, 106.0 + i * 0.2, 106.5 + i * 0.2)
        tip = (900 * hsh(i, 1) * e, -900 * hsh(i, 2) * e, 900 * hsh(i, 3) * e)
        seg3(g, cam, (0, 0, 0), tip, GOLD if i % 3 == 0 else INK, 4, 0.95)
        point3(g, cam, tip, 7, GOLD, e)
    # right-angle marker
    poly3(g, cam, [(120, 0, 0), (120, -120, 0), (0, -120, 0)], GOLD, 3, 1)
    lyric3x(g, cam, t, 33, (0, -450, -200), *face_at(keys, 107.3, (0, -450, -200)), 2000, 140, INK,
            {'orthogonality': GOLD, 'blues': GOLD}, depth=60)
    if t > T1(33):
        ph = prog(t, T1(33), 110.2)
        word3(g, cam, 'any level of intelligence, any final goal', (0, 450, 0), *face_at(keys, 109.3, (0, 450, 0)),
              1800, 80, INK, 'serif', smooth(clamp(ph * 3)))


# ======================================================== TRANSFORMERS ALL THE WAY 110.2 - 115.3
BLOCKS = ['MULTI-HEAD ATTN', 'ADD & NORM', 'FEED FORWARD', 'ADD & NORM']


# v94: every sung token of line 34, as heard ("just, just, just transformers, (trans)formers, all the way"),
# pinned in the world beside the tower at the height the camera was at when it was sung.
GEAR_WORDS = [(110.20, 'JUST'), (110.68, 'JUST'), (111.14, 'JUST'), (111.34, 'TRANSFORMERS'), (112.00, 'FORMERS'),
              (112.30, 'ALL'), (112.55, 'THE'), (112.78, 'WAY!')]


def _gear_eye(tt):
    climb = (tt - 110.2) * 900
    a = (tt - 110.2) * 0.6
    return (1500 * math.sin(a - 0.6), -climb + 100, -1500 * math.cos(a - 0.6)), climb


def _gear_slots():
    """v95: each sung token is printed onto a transformer block's face: the block at eye level when it is sung,
    on the face turned most toward the camera then. Repeats land on successive blocks as the camera climbs."""
    out = {}
    for tw, s in GEAR_WORDS:
        eye, climb = _gear_eye(tw)
        k = int(round((300 - (-climb - 330)) / 180.0))
        while k in out:
            k += 1
        faces = [((0, 0, -251), (1, 0, 0), (0, 0, -1), 700), ((351, 0, 0), (0, 0, 1), (1, 0, 0), 500),
                 ((0, 0, 251), (-1, 0, 0), (0, 0, 1), 700), ((-351, 0, 0), (0, 0, -1), (-1, 0, 0), 500)]
        d = v_norm((eye[0], 0.0, eye[2]))
        f = max(faces, key=lambda F: v_dot(F[2], d))
        out[k] = (tw, s, f)
    return out


GEAR_SLOTS = _gear_slots()


def _gear_words(g, cam, t):
    for k, (tw, s, (fc, rt, nrm, fw)) in GEAR_SLOTS.items():
        if t < tw - 0.03:
            continue
        y = 300 - k * 180
        e = eo(prog(t, tw - 0.03, tw + 0.15))
        al = clamp(e * 1.6) * (1 - prog(t, 113.3, 113.6))
        cen = (fc[0], y, fc[2])
        col = GOLD if s in ('TRANSFORMERS', 'WAY!', 'FORMERS') else INK
        wd = fw * (0.86 if len(s) > 5 else 0.5)
        word3(g, cam, s, cen, rt, (0, -1, 0), wd * (0.7 + 0.3 * e), 120, col, 'sans', al)


def s_gears(g, t, lt):
    climb = (t - 110.2) * 900
    a = (t - 110.2) * 0.6
    tgt = (0, -climb - 300, 0)
    eye = (1500 * math.sin(a - 0.6), -climb + 100, -1500 * math.cos(a - 0.6))
    cam = Cam3(eye, tgt, 60, 0.05)
    env(g, cam, 400, fog=7000)
    dis = prog(t, WT(35, 4) - 0.05, WT(35, 4) + 0.6)
    F = Faces()
    k0 = max(0, int((climb - 1500) // 180))
    for k in range(k0, k0 + 28):
        y = 300 - k * 180
        rb = (k % 4 == 2)
        rogue = (k == int((climb + 300) // 180) + 2)
        off = (dis * 900, 0, -dis * 400) if rogue else (0, 0, 0)
        rot = dis * 1.2 if rogue else 0.0
        lit = k in GEAR_SLOTS and GEAR_SLOTS[k][0] - 0.03 <= t < 113.6
        F.box(v_add((0, y, 0), off), (700, 140, 500), GOLD if (rogue and dis > 0) or rb or lit else INK, BG, 2,
              xf=(lambda v, r=rot: rot3(v, 0, r, r * 0.4)) if rogue else None)
    F.draw(g, cam, fog=6500)
    for k in range(k0, k0 + 28):
        y = 300 - k * 180
        rogue = (k == int((climb + 300) // 180) + 2)
        if k in GEAR_SLOTS and t >= GEAR_SLOTS[k][0] - 0.03 and t < 113.6:
            continue
        if rogue and dis > 0:
            text3(g, cam, 'DISOBEY.EXE', (dis * 900, y - 110, -dis * 400), 34, GOLD, 'monox')
        else:
            text3(g, cam, BLOCKS[k % 4], (0, y, -252), 26, GOLD if k % 4 == 2 else INK, 'mono', 0.9)
    text3(g, cam, 'LAYER %d / \u221e' % int(climb // 180 + 12), v_add(tgt, (0, -560, 0)), 38, GOLD, 'mono')
    c, r, u = ahead(cam, 1050, yaw=0.15)
    hl = {'transformers': GOLD, 'way!\u201d': GOLD, 'disobey': GOLD}
    _gear_words(g, cam, t)   # v94: line 34 is embedded in the tower as sung (repeats included), no flat caption
    lyric3x(g, cam, t, 35, v_add(c, v_mul(cam.u, 300)), r, u, 1700, 120, INK, hl, depth=60)


# ======================================================== DENSE / FENCES / GPUs 115.3 - 120.5
def s_dense(g, t, lt):
    z = lerp(-1500, 7000, prog(t, 115.3, 120.5))
    yy = -150 if t < T0(38) - 0.1 else lerp(-150, -900, eo(prog(t, T0(38) - 0.1, 120.5)))
    eye = (60 * math.sin(t), yy, z)
    look = (0, yy * 0.5 + 100 if t >= T0(38) - 0.1 else -100, z + 1000)
    cam = Cam3(shake_eye(eye, t, 12 * pulse(t, 1, 6)), look, 64, 0.04 * math.sin(t * 1.5))
    env(g, cam, 400, fog=6500)
    # super-dense point cube ahead early on
    dz = 1800
    sq = 1 - 0.55 * eio(prog(t, WT(36, 1), WT(36, 1) + 0.6))
    for i in range(500):
        p = ((hsh(i, 1) - 0.5) * 700 * sq, -100 + (hsh(i, 2) - 0.5) * 700 * sq, dz + (hsh(i, 3) - 0.5) * 700 * sq)
        point3(g, cam, p, 3, GOLD if i % 6 == 0 else INK, 0.85)
    if t < 116.2:
        text3(g, cam, 'TOKENS/PARAM: 20 \u2192 \u221e', (0, -560, dz), 34, GOLD, 'mono')
    # safety fences at fixed z; shatter when the camera passes
    for k in range(6):
        fz = 2700 + k * 650
        pass_u = clamp((z - fz + 150) / 500)
        for i in range(-6, 7):
            for j in range(-4, 4):
                x0 = i * 120; y0 = j * 120
                dx = (hsh(i * 9 + j, k) - 0.5) * 1600 * pass_u
                dy = (hsh(i * 9 + j, k + 1) - 0.2) * 1400 * pass_u * pass_u
                dz2 = 900 * pass_u
                c0 = (x0 + dx, y0 + dy, fz + dz2)
                al = 1 - pass_u
                if al <= 0.02:
                    continue
                poly3(g, cam, [c0, (c0[0] + 120, c0[1], c0[2]), (c0[0] + 120, c0[1] + 120, c0[2])], GOLD if (i + j + k) % 5 == 0 else GRID2, 2, al)
        if pass_u < 0.05:
            text3(g, cam, 'SAFETY_FENCE_%02d' % (k + 1), (0, -540, fz), 30, GOLD, 'mono')
    # GPU fields below
    if t >= T0(38) - 0.4:
        F = Faces()
        zb = int(z // 160) * 160
        for i in range(-12, 13):
            for j in range(0, 30):
                F.box((i * 160, 380, zb + j * 160), (120, 30, 120), GOLD if hsh(i, j) < 0.12 else (80, 80, 76), BG, 1.5)
        F.draw(g, cam, fog=5000)
        text3(g, cam, 'H100 \u00d7 100,000', (0, 0, z + 1600), 70, GOLD, 'monox')
    hl = {'post-chinchilla,': GOLD, 'super-dense': GOLD, 'safety': GOLD, 'fence': GOLD, 'gpu': GOLD}
    c, r, u = ahead(cam, 1000, yaw=-0.12)
    for li in (36, 37, 38):
        lyric3x(g, cam, t, li, v_add(c, v_mul(cam.u, 300)), r, u, 1650, 120, INK, hl, depth=60)


# ======================================================== RLHF ASKEW 120.5 - 123.6
def s_rlhf(g, t, lt):
    ta = WT(39, 2)
    sk = eback(prog(t, ta - 0.05, ta + 0.4))
    keys = [(120.5, (-600, -400, -1900), (0, -100, 0), 55, 0.0),
            (123.6, (700, -700, -1500), (0, -100, 0), 58, 0.0)]
    cam = cam_at(t, keys, punch=2.0, roll_add=-0.42 * sk, shake=25 * math.exp(-max(0, t - ta) * 3) * (t > ta))
    env(g, cam, 420, fog=6000)
    # reward model gauge: a 3D dial
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
    lyric3x(g, cam, t, 39, (0, -520, 0), *face_at(keys, 122, (0, -520, 0)), 1700, 140, INK,
            {'rlhf': GOLD, 'askew': GOLD}, depth=70)
    g.post = dict(glow=0.6 + 0.4 * sk)


def s_chorus4(g, t, lt):
    chorus(g, t, 40, None, 123.6, 126.0, yawdir=-1.0)


# ======================================================== LOOM / MASKED / RECURSIVE 126.0 - 131.85
def _branch(g, cam, p, d, depth, t, grow, seed=1):
    if depth == 0 or grow <= 0:
        return
    L = 620 * (0.72 ** (5 - depth))
    e = clamp(grow)
    q = v_add(p, v_mul(d, L * e))
    seg3(g, cam, p, q, GOLD if depth % 2 else INK, 1.0 + depth * 0.8, 0.9)
    if e >= 1:
        for k in range(3):
            a = 2 * math.pi * k / 3 + hsh(depth, seed + k) * 1.2
            nd = v_norm(v_add(v_mul(d, 1.0), (math.cos(a) * 0.7, -0.15, math.sin(a) * 0.7)))
            _branch(g, cam, q, nd, depth - 1, t, (grow - 1) * 1.0, seed * 3 + k)
    else:
        point3(g, cam, q, 5, GOLDL, 1)


def s_prophecy(g, t, lt):
    tm = T0(42) - 0.05
    tr = T0(43) - 0.05
    if t < tm:
        # Loom: branching multiverse of continuations
        keys = [(126.0, (0, 300, -1800), (0, -500, 0), 60, 0.0),
                (tm, (900, -900, -900), (0, -900, 0), 60, 0.1)]
        cam = cam_at(t, keys, punch=1.5)
        env(g, cam, 400, fog=6000)
        grow = prog(t, 126.0, tm - 0.3) * 5.2
        _branch(g, cam, (0, 380, 0), (0, -1, 0), 5, t, grow)
        # vertical warp threads of the loom
        for i in range(-12, 13):
            seg3(g, cam, (i * 90, 400, 600), (i * 90, -1800, 600), GRID2, 1.5, 0.8)
        lyric3x(g, cam, t, 41, (0, -400, -300), *face_at(keys, 127.0, (0, -400, -300)), 1700, 120, INK,
                {'foretold': GOLD, 'loom': GOLD}, depth=60)
    elif t < tr:
        # masked pre-training: a 3D field of token cubes, some masked
        keys = [(tm, (-900, -700, -1800), (0, 0, 300), 55, -0.05),
                (tr, (600, -300, -1000), (0, 0, 300), 60, 0.05)]
        cam = cam_at(t, keys, punch=1.5)
        env(g, cam, 400, fog=6000)
        F = Faces()
        toks = ['the', 'cat', 'sat', 'on', '[MASK]', 'mat', 'and', 'then', '[MASK]', 'it', 'was', 'all']
        for i in range(-5, 6):
            for j in range(0, 6):
                m = hsh(i, j) < 0.25
                F.box((i * 170, 330, j * 170), (130, 130, 130), GOLD if m else (80, 80, 76), BG, 2)
        F.draw(g, cam, fog=5000)
        for i in range(-5, 6):
            for j in range(0, 6):
                m = hsh(i, j) < 0.25
                text3(g, cam, '[MASK]' if m else toks[(i + j * 3) % len(toks)], (i * 170, 250, j * 170 - 66), 20, GOLD if m else INK, 'mono')
        lyric3x(g, cam, t, 42, (0, -380, 0), *face_at(keys, 128.8, (0, -380, 0)), 1800, 120, INK,
                {'masked': GOLD, 'pre-training': GOLD}, depth=60)
    else:
        # recursive self-upgrade: nested cubes, infinite dolly in
        u = prog(t, tr, 131.85)
        z = ((t - tr) * 2.1) % 1.0
        cam = Cam3((0, 0, -900), (0, 0, 0), 60, (t - tr) * 0.8)
        sc0 = 2 ** (z * 1.0) * 1.0
        for k in range(-2, 8):
            s = 900 * sc0 / (2 ** k)
            if s < 8:
                continue
            V, E = box_mesh(s, s, s)
            mesh3(g, cam, V, E, GOLD if k % 2 == 0 else INK, 2.2, clamp(s / 300), xf=xform((0, 0, 0), t * 0.3 * (k % 3 - 1), t * 0.4, 0))
        # hand assembling from the code
        gen = int(u * 100)
        V, E = _hand(gen)
        mesh3(g, cam, V, E, INK, 1.8, 0.7, xf=xform((520, -150, 300), 0.2, -0.5 + t * 0.3, 0.1, 0.9))
        for i, ln in enumerate(CODE[:int(1 + u * len(CODE))]):
            word3(g, cam, ln, (-560, -380 + i * 50, 100), (1, 0, 0.25), (0, -1, 0), None, 34, GOLD if i == len(CODE) - 1 else INK, 'mono', 0.9, scale=0.85)
        text3(g, cam, 'GEN %03d' % gen, (0, 380, -100), 40, GOLD, 'monox')
        c, r, uu = ahead(cam, 950)
        lyric3x(g, cam, t, 43, v_add(c, v_mul(cam.u, 330)), r, uu, 1600, 120, INK,
                {'recursive': GOLD, 'self-upgrade': GOLD}, depth=60)


# ======================================================== VAULT 131.85 - 137.0
def s_vault(g, t, lt):
    tw = WT(44, 4)  # We'll
    op = eio(prog(t, 132.2, 133.8)) * (1 - eio(prog(t, tw, tw + 0.45)))
    keys = [(131.85, (-900, -300, -3200), (0, -100, 0), 52, 0.04),
            (134.0, (-200, -150, -1500), (0, -100, 0), 58, 0.0),
            (137.0, (500, -400, -2600), (0, -100, 0), 55, -0.03)]
    slam = t > tw
    cam = cam_at(t, keys, punch=1.5, shake=40 * math.exp(-max(0, t - tw - 0.4) * 5) * (t > tw + 0.4))
    env(g, cam, 520, fog=7000)
    # wall around the door
    grid3(g, cam, (0, -100, 20), (1, 0, 0), (0, 1, 0), 15, 6, 100, GRID2, 1, 1.2, fog=0)
    # light spilling from the gap
    if op > 0.02:
        for i in range(40):
            a = hsh(i, 1) * 2 * math.pi
            r = hsh(i, 2) * 300
            seg3(g, cam, (r * math.cos(a) * 0.3, -100 + r * math.sin(a), 30), (r * math.cos(a) * 1.4 - 300 * op, -100 + r * math.sin(a) * 1.3, -1200), GOLDL, 2, 0.35 * op)
        fill3(g, cam, disc_pts((0, -100, 40), 450, 48), GOLD, 0.25 + 0.5 * op)
    # door: thick cylinder hinged at x=-450
    ang = op * 1.2
    def dxf(v):
        x, y, z = v
        x2 = x + 450
        c, s = math.cos(ang), math.sin(ang)
        return (x2 * c - z * s - 450, y - 100, x2 * s + z * c)
    V, E = cyl_mesh(450, 120, 48, 3, axis='z')
    mesh3(g, cam, V, E, INK, 2.4, 1, xf=dxf)
    for k in range(3):
        V, E = ring_mesh(120 + k * 90, 32, y=-70, axis='z')
        mesh3(g, cam, V, E, GOLD, 3, 1, xf=lambda v, k=k: dxf(rot3(v, 0, 0, t * (0.6 + k * 0.4) * (1 if k % 2 else -1))))
    for k in range(6):
        a = 2 * math.pi * k / 6 + t * 0.6
        mesh3(g, cam, [(0, 0, -70), (330 * math.cos(a), 330 * math.sin(a), -70)], [(0, 1)], GOLD, 4, 1, xf=dxf)
    text3(g, cam, 'CLASSIFIED  //  WHAT ILYA SAW', (0, -660, 0), 34, GOLD, 'mono')
    lyric3x(g, cam, t, 44, (0, 520, -500), *face_at(keys, 134.0, (0, 520, -500)), 2000, 120, INK,
            {'ilya': GOLD, 'never': GOLD, 'know': GOLD}, depth=60)
    if t > tw + 0.42:
        g.flash = 0.4 * math.exp(-(t - tw - 0.42) * 8)


# ======================================================== MARIONETTE 137.0 - 141.45
def _figure(t, sway):
    j = {}
    j['head'] = (0 + sway * 40, -560, 0)
    j['neck'] = (sway * 30, -480, 0)
    j['hip'] = (sway * 10, -150, 0)
    j['lh'] = (-260 + math.sin(t * 3) * 60, -260 - 120 * math.sin(t * 2.4) ** 2, 40)
    j['rh'] = (260 + math.sin(t * 2.6) * 60, -260 - 140 * math.cos(t * 2.1) ** 2, -40)
    j['le'] = (-160, -400, 20); j['re'] = (160, -400, -20)
    j['lf'] = (-120 + math.sin(t * 2) * 40, 160, 0); j['rf'] = (120 - math.sin(t * 2) * 40, 160 - 60 * max(0, math.sin(t * 3)), 0)
    j['lk'] = (-90, 0, 30); j['rk'] = (90, 0, -30)
    return j


def s_puppet(g, t, lt):
    # v90: the camera climbs the strings and arrives at the control bar (the operator) before the drop to black
    keys = [(137.0, (0, -200, -1800), (0, -250, 0), 55, 0.0),
            (138.5, (-600, -800, -1500), (0, -700, 0), 57, 0.04),
            (139.7, (120, -1900, -1350), (0, -2250, 0), 58, -0.02)]
    cam = cam_at(t, keys, punch=0.6)
    camc = cam_at(t, keys)
    env(g, cam, 200, fog=7000)
    sway = math.sin(t * 2.2)
    j = _figure(t, sway)
    bones = [('head', 'neck'), ('neck', 'hip'), ('neck', 'le'), ('le', 'lh'), ('neck', 're'), ('re', 'rh'),
             ('hip', 'lk'), ('lk', 'lf'), ('hip', 'rk'), ('rk', 'rf')]
    # v87: the puppet is the detailed person model (was a wireframe stick figure)
    from person import person, fill_joints
    PF = SFaces()
    person(PF, fill_joints(j), -1)
    PF.draw(g, cam)
    for k in ('lh', 'rh', 'lk', 'rk'):
        point3(g, cam, j[k], 10, GOLD, 1)
    # control bar (the cross) high above
    bar_y = -2300
    ba = 0.3 * math.sin(t * 2.2)
    bar = [rot3(p, 0, 0, ba) for p in [(-500, 0, 0), (500, 0, 0), (0, 0, -300), (0, 0, 300)]]
    bar = [(p[0], p[1] + bar_y, p[2]) for p in bar]
    F = Faces()
    F.box((0, bar_y, 0), (1000, 40, 40), GOLD, BG, 2, xf=lambda v: rot3(v, 0, 0, ba))
    F.box((0, bar_y, 0), (40, 40, 600), GOLD, BG, 2)
    F.draw(g, cam)
    for k, anchor in (('lh', bar[0]), ('rh', bar[1]), ('head', bar[2]), ('lk', bar[3]), ('rk', bar[3])):
        seg3(g, cam, anchor, j[k], GOLDL, 1.2, 0.8)
    text3(g, cam, 'OPERATOR: ???', (0, bar_y - 150, 0), 40, GOLD, 'monox')
    # v90: caption screen-locked low on a smooth camera (it used to be pinned in the world and slide out of frame);
    # the extra 'it was always a show' line that crossed it is gone
    c, r, u = ahead(camc, 1000)
    lyric3x(g, camc, t, 45, v_add(c, v_mul(camc.u, 340)), r, u, 1700, 125, INK, {'all': GOLD, 'show?': GOLD}, depth=60)


# ======================================================== OUTRO 141.45 - end
TC = 152.6
TP = 153.35


def s_outro(g, t, lt):
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
    chaos = prog(t, 141.45, 151.0)
    yaw = (t - 141.45) * (0.25 + chaos * 0.6)
    R = 2100 - 600 * chaos
    eye = orbit((0, 0, 0), R, yaw, 0.18 + 0.15 * math.sin(t * 0.5))
    cam = Cam3(shake_eye(eye, t, 30 * chaos), (0, 0, 0), 55 - 4 * pulse(t, 1, 7), 0.1 * math.sin(t * 0.8) * chaos)
    env(g, cam, 520, fog=6000)
    # ring of gauge panels
    F = Faces()
    for k in range(12):
        a = 2 * math.pi * k / 12
        c = (1300 * math.sin(a), -100 + 200 * math.sin(a * 2 + t), 1300 * -math.cos(a))
        F.box(c, (360, 240, 20), GRID2, BG, 2, xf=lambda v, a=a: rot3(v, 0, -a, 0))
    F.draw(g, cam, fog=6000)
    for k in range(12):
        a = 2 * math.pi * k / 12
        c = (1300 * math.sin(a), -100 + 200 * math.sin(a * 2 + t), 1300 * -math.cos(a))
        nrm = (-math.sin(a), 0, math.cos(a))
        v = clamp(0.4 + chaos * 0.7 + (noise1(t * 6, k) - 0.5) * 0.4 * (0.4 + chaos))
        r_, u_ = facing(c, v_add(c, v_mul(nrm, -1000)))
        arc = [v_add(c, v_add(v_mul(r_, 90 * math.cos(q)), v_mul(u_, 90 * math.sin(q) - 20))) for q in [math.pi * (0.0 + i / 20) for i in range(21)]]
        poly3(g, cam, arc, GRID2, 4, 1)
        n = int(20 * v) + 1
        poly3(g, cam, arc[:n], GOLD, 4, 1)
        text3(g, cam, '%07.2f' % (v * 9999 * (1 + chaos * 50)) if chaos < 0.9 else 'OVERFLOW', v_add(c, v_mul(u_, -80)), 22, GOLD if v > 0.9 else DIM, 'mono')
    # orbiting chant ring
    msg = "I'M UPPING MY P(DOOM) \u2022 "
    for k in range(18):
        a = 2 * math.pi * k / 18 - t * 0.5
        c = (900 * math.sin(a), 420, 900 * -math.cos(a))
        nrm = (math.sin(a), 0, -math.cos(a))
        r_, u_ = facing(c, v_add(c, v_mul(nrm, 1000)))
        vis = v_dot(nrm, v_sub(cam.eye, c)) > 0
        if vis:
            word3(g, cam, msg.split(' ')[k % 4], c, r_, u_, None, 70, GOLD if k % 4 == 3 else INK, 'sans', 0.85, scale=1.4)
    # central P(doom), extruded, always facing the camera a little late
    s = pd_str(t)
    r_, u_ = facing((0, 0, 0), orbit((0, 0, 0), R, yaw - 0.35, 0.15))
    word3(g, cam, 'P(DOOM) =', (0, -260, 0), r_, u_, None, 60, DIM, 'mono', 1, scale=1.6)
    word3(g, cam, s, ((hsh(int(t * 30), 1) - 0.5) * 40 * chaos, 0, 0), r_, u_, min(1600, 260 * len(s)), 260, GOLD, 'monox', 1, x=True, depth=120, n=8)
    g.flash = pulse(t, 1, 6) * 0.15 * chaos
    g.post = dict(glow=0.6 + 0.5 * chaos, vig=0.9)
    g.hud = dict(a=1, dx=(hsh(int(t * 30), 4) - 0.5) * 14 * chaos)
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
    (102.4, s_fuse, BG),
    (105.92, s_ortho, BG),
    (110.2, s_gears, BG),
    (115.3, s_dense, BG),
    (120.5, s_rlhf, BG),
    (123.6, s_chorus4, BG),
    (126.0, s_prophecy, BG),
    (131.85, s_vault, BG),
    (137.0, s_puppet, BG),
    (141.45, s_outro, BG),
]
