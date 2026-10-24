"""3D scenes 0:00 - 0:38.4. Every scene owns a moving 3D camera (cam3d.Cam3)."""
import math, random
from cam3d import *

L = LINES
def T0(i): return LINES[i][0]
def T1(i): return LINES[i][1]
def WT(li, k): return LINE_WORDS[li][k][1]


from cam3d import env


def dust(g, cam, t, n=160, R=2500, seed=3, c=DIM, al=0.7):
    for i in range(n):
        p = ((hsh(i, seed) - 0.5) * R * 2, (hsh(i, seed + 1) - 0.5) * R, (hsh(i, seed + 2) - 0.5) * R * 2)
        p = (p[0] + math.sin(t * 0.3 + i) * 20, p[1] - (t * 15 + i * 7) % 300, p[2])
        point3(g, cam, p, 2.0, c, al)


# ======================================================== BOOT 0 - 1.8
# monitor body + base corners: the boot camera re-aims every frame so these stay centred on screen
_BOOT_PTS = [(x, y, z) for x in (-740, 740) for y in (-280, 180) for z in (40, 260)] + \
            [(x, 355, z) for x in (-360, 360) for z in (30, 370)]


def _center_on(cam, pts, it=4):
    eye = cam.eye
    tgt = v_add(eye, v_mul(cam.f, 1000.0))
    fov = math.degrees(2 * math.atan((H / 2) / cam.F))
    roll = math.atan2(-cam.r[1], cam.u[1]) if False else None
    for _ in range(it):
        xs, ys = [], []
        for p in pts:
            q = cam.p(p)
            if q:
                xs.append(q[0]); ys.append(q[1])
        if not xs:
            break
        dx = (min(xs) + max(xs)) / 2 - cam.cx
        dy = (min(ys) + max(ys)) / 2 - cam.cy
        if abs(dx) < 0.5 and abs(dy) < 0.5:
            break
        k = 1000.0 / cam.F
        tgt = v_add(tgt, v_add(v_mul(cam.r, dx * k), v_mul(cam.u, dy * k)))
        c2 = Cam3(eye, tgt, fov, 0.0)
        # keep the original roll: rebuild r/u by matching the old roll offset
        c2.r, c2.u = _reroll(c2, cam)
        cam = c2
    return cam


def _reroll(c2, ref):
    # roll angle of ref relative to an unrolled camera with the same forward
    base = Cam3(ref.eye, v_add(ref.eye, ref.f), 50, 0.0)
    a = math.atan2(v_dot(ref.r, base.u), v_dot(ref.r, base.r))
    c, s_ = math.cos(a), math.sin(a)
    r, u = c2.r, c2.u
    return v_add(v_mul(r, c), v_mul(u, s_)), v_add(v_mul(u, c), v_mul(r, -s_))


def s_boot(g, t, lt):
    cam = cam_at(t, [(0.0, (0, -120, -3200), (0, -20, 0), 50, 0.0),
                     (1.8, (520, -330, -1150), (0, 0, 0), 55, -0.04)])
    cam = _center_on(cam, _BOOT_PTS)
    env(g, cam, 320, al=prog(t, 0.05, 0.8))
    # 3D monitor: solid body, inset screen, neck and base
    F = SFaces()
    F.sbox((0, -50, 150), (1480, 460, 220), (38, 37, 34), GOLDD, 1.4, amb=0.35)
    F.sbox((0, 255, 200), (90, 150, 70), (44, 43, 40), None, amb=0.35)
    F.sbox((0, 342, 200), (720, 26, 340), (44, 43, 40), GOLDD, 1.0, amb=0.35)
    F.draw(g, cam)
    zs = 38.0
    fill3(g, cam, [(-700, -260, zs), (700, -260, zs), (700, 160, zs), (-700, 160, zs)], (13, 13, 12), 1.0, stroke=GOLD, w=2)
    lines = ['> INIT HUD.SYS', '> LOAD IRIS_SCAN_v0.1', '> P(DOOM) MONITOR ........ ONLINE', '> AWAITING SUBJECT_']
    for i, s in enumerate(lines):
        t0 = 0.12 + i * 0.26
        if t > t0:
            n = max(1, int(len(s) * prog(t, t0, t0 + 0.2)))
            Lr = text_layer(s[:n], 46, GOLD if i == 2 else INK, 'mono')
            wd = Lr.size[0] * 1.0
            map_layer(g, cam, Lr, (-640 + wd / 2, -170 + i * 72, zs - 2), (1, 0, 0), (0, -1, 0), wd)
    sy_ = -255 + 410 * ((t * 0.9) % 1.0)
    poly3(g, cam, [(-695, sy_, zs - 3), (695, sy_, zs - 3)], GOLD, 2, 0.35)
    point3(g, cam, (640, 125, zs - 3), 7, GOLD, 0.5 + 0.5 * (int(t * 4) % 2))
    g.hud = dict(a=prog(t, 0.6, 1.2))


# ======================================================== IRIS 1.8 - 9.4
def _iris():
    tr = []
    for i in range(56):
        a0 = 2 * math.pi * i / 56 + hsh(i, 1) * 0.05
        r1 = 150 + hsh(i, 2) * 130
        da = (hsh(i, 3) - 0.5) * 0.35
        r2 = r1 + 40 + hsh(i, 4) * 170
        zz = -(30 + hsh(i, 5) * 160)
        tr.append([(92, a0, 0), (r1, a0, zz * 0.4), (r1, a0 + da, zz), (r2, a0 + da, zz * 1.4)])
    return tr

IRIS = _iris()
EYEBALL = sphere_mesh(560, 10, 24)
BALL = sphere_mesh(40, 6, 10)


def s_eye(g, t, lt, keys_override=None):
    dive = prog(t, WT(2, 1), T1(2) + 0.05)
    nerv = t > WT(1, 4) - 0.05
    keys = [(1.8, orbit((0, 0, 0), 2900, -0.75, 0.32), (0, 0, 0), 50, 0.05),
            (4.2, orbit((0, 0, 0), 1900, -0.25, 0.18), (0, 40, 0), 52, 0.0),
            (6.6, orbit((0, 0, 0), 1500, 0.35, 0.10), (0, 60, 0), 54, -0.03),
            (8.4, orbit((0, 0, 0), 900, 0.12, 0.02), (0, 0, 0), 58, 0.0),
            (9.45, (0, 0, -60), (0, 0, 400), 75, 0.2)]
    if keys_override is not None:
        keys = keys_override
    cam = cam_at(t, keys, punch=1.5, shake=(24 * (0.4 + feat('flux', t)) if nerv else 0))
    env(g, cam, 650, fog=6000)
    from eye3 import draw_eye, blink
    op = eo(prog(t, 1.85, 2.5))
    bl = blink(t, (3.6, 6.25))
    lu = lerp(2, 34, op) * (1 - bl) + 1 * bl + 10 * dive
    ll = lerp(-2, -30, op) * (1 - bl) - 1 * bl - 8 * dive
    from eye3 import look_at_cam
    ly, lp = look_at_cam(cam, 0.75)
    yaw = (ly + 0.08 * math.sin(t * 0.7)) * (1 - dive)
    pitch = (lp + 0.05 * math.sin(t * 0.5 + 1)) * (1 - dive)
    dil = (1 + 0.6 * dive)
    draw_eye(g, cam, t, yaw, pitch, lu, ll, dil, glitch=0.0, wave=0.0, flux=feat('flux', t))
    # lyrics on a plane under the iris
    hl = {'agi': GOLD, 'nervous': GOLD, 'surprise': GOLD}
    for li in (0,):
        lyric3x(g, cam, t, li, (0, 470, -160), (1, 0, 0), (0, -1, 0), 1900, 112, INK, hl, depth=50)
    tag_scan = 'IRIS_SCAN  //  SUBJECT: HUMAN  //  ' + ('PUPIL DILATION ERR' if nerv else 'NOMINAL')
    text3(g, cam, tag_scan, (0, -470, 0), 26, GOLD if nerv else DIM, 'mono', 0.9)
    g.post = dict(ca=0.6 if nerv else 0.0)


_SE = None
def _sph_edges():
    global _SE
    if _SE is None:
        _SE = sphere_mesh(560, 10, 24)[1]
    return _SE


def _mesh(m):
    return m[0], m[1]


# ======================================================== LOSS LANDSCAPE 9.4 - 17.7
def _h(x, z, t, drop):
    h = 120 * math.sin(x * 0.004 + 0.6) * math.cos(z * 0.0035) + 70 * math.sin(x * 0.009 + z * 0.006 + t * 0.3)
    pit = math.exp(-((x - 150) ** 2 + (z - 100) ** 2) / (2 * 260 ** 2))
    return h - drop * 900 * pit


def s_loss(g, t, lt):
    tdrop = WT(3, 4)
    drop = eo(prog(t, tdrop - 0.05, tdrop + 0.6))
    keys = [(9.3, (-1900, -950, -1700), (0, 150, 0), 52, 0.06),
            (11.0, (-700, -650, -1600), (100, 300, 100), 55, 0.0),
            (12.6, (500, -500, -1150), (150, 500, 100), 60, -0.05),
            (14.6, (1300, -900, -400), (0, 100, 200), 55, -0.02),
            (17.7, (900, -1700, 900), (0, 0, 0), 50, 0.0)]
    cam = cam_at(t, keys, punch=1.0, shake=40 * math.exp(-max(0, t - tdrop) * 3) * (t > tdrop))
    env(g, cam, 900, fog=7000, al=0.6)
    N = 26; S = 2400
    rows = []
    for i in range(N + 1):
        row = []
        for j in range(N + 1):
            x = -S / 2 + S * i / N; z = -S / 2 + S * j / N
            row.append((x, 300 - _h(x, z, t, drop), z))
        rows.append(row)
    for i in range(N + 1):
        cc = (78, 78, 74) if i % 4 else (120, 116, 104)
        poly3(g, cam, rows[i], cc, 1.6, 1.0, fog=7000)
        poly3(g, cam, [rows[j][i] for j in range(N + 1)], cc, 1.6, 1.0, fog=7000)
    # gradient-descent ball trail
    steps = 40
    tr = []
    for k in range(steps):
        u = k / steps
        x = lerp(-900, 150, eo(u)); z = lerp(-700, 100, eo(u))
        tr.append((x, z))
    pk = prog(t, 9.6, tdrop)
    n = max(2, int(steps * pk))
    pts = [(x, 300 - _h(x, z, t, drop) - 18, z) for x, z in tr[:n]]
    poly3(g, cam, pts, GOLD, 3.0, 1.0)
    bx, bz = tr[n - 1]
    by = 300 - _h(bx, bz, t, drop) - 40
    mesh3(g, cam, *BALL, c=GOLD, w=2, xf=xform((bx, by, bz), ry=t * 2))
    lossv = 2.31 * (1 - pk) + 0.08 - 0.079 * drop
    text3(g, cam, 'LOSS %.4f' % lossv, (bx, by - 120, bz), 34, GOLD, 'mono')
    text3(g, cam, '\u2207L  STEP %05d' % int(pk * 48000), (bx, by - 80, bz), 22, DIM, 'mono')
    hl = {'drop': GOLD, 'loss,': GOLD, 'servant': GOLD, 'boss': GOLD}
    c3 = (0, 0, 250)
    r, u = face_at(keys, 11.6, c3)
    lyric3x(g, cam, t, 3, c3, r, u, 1900, 112, INK, hl, depth=60)
    c4 = (300, -100, 250)
    r, u = face_at(keys, 15.2, c4)
    lyric3x(g, cam, t, 4, c4, r, u, 1500, 112, INK, hl, depth=60)


# ======================================================== JAW 17.7 - 22.55
def _teeth(n=14, R=420):
    out = []
    for i in range(n):
        a = math.pi * (0.06 + 0.88 * i / (n - 1))
        out.append((R * math.cos(a), R * math.sin(a), 30 + 18 * abs(math.cos(a))))
    return out

TEETH = _teeth()


def s_jaw(g, t, lt):
    keys = [(17.7, (0, -420, -2600), (0, 0, 300), 50, 0.0),
            (19.5, (-500, -150, -1500), (0, 0, 300), 54, 0.08),
            (21.0, (350, -40, -700), (0, 0, 400), 60, -0.05),
            (22.55, (0, 0, 120), (0, 0, 900), 70, 0.0)]
    cam = cam_at(t, keys, punch=2.0)
    env(g, cam, 520, fog=6000)
    chomp = 1 - pulse(t, 1, 5)
    if t > WT(5, 3) - 0.05:
        chomp = 1 - pulse(t, 2, 6)
    open_a = 0.12 + 0.42 * chomp * prog(t, 17.8, 18.4)
    F = Faces()
    for half, sgn in (('up', -1), ('lo', 1)):
        ang = -open_a if sgn < 0 else open_a * 0.6
        def xf(v, ang=ang):
            x, y, z = v
            # hinge at back z=600
            z0 = z - 600
            c, s = math.cos(ang), math.sin(ang)
            return (x, y * c - z0 * s, y * s + z0 * c + 600)
        for (x, zf, h) in TEETH:
            # teeth arranged on U along x/z
            px, pz = x, 600 - zf * 1.2
            hh = h * 2.2
            V = box_verts((0, 0, 0), (54, hh, 54))
            V = [xf((v[0] + px, v[1] + sgn * (-hh / 2 - 6), v[2] + pz)) for v in V]
            for idx in BOX_F:
                F.quad([V[q] for q in idx], GOLD if hsh(int(x), 3) < 0.25 else INK, BG, 2)
        # gum line
        gum = [xf((R2 * math.cos(math.pi * u / 20), sgn * (-4), 600 - R2 * math.sin(math.pi * u / 20) * 1.2)) for u in range(21) for R2 in (440,)]
        poly3(g, cam, gum, GOLD, 3, 0.9)
    F.draw(g, cam, fog=6000)
    hl = {'chatgpt,': GOLD, 'eat': GOLD, 'alive': GOLD}
    lyric3x(g, cam, t, 5, (0, -40, 1100), (1, 0, 0), (0, -1, 0), 1800, 112, INK, hl, depth=60)
    text3(g, cam, 'MODEL.MOUTH  OPEN %.0f%%' % (open_a * 180), (-420, -260, 300), 22, GOLD, 'mono')


# ======================================================== CHORUS (shared, extruded block type)
EXPL = [(math.cos(2 * math.pi * hsh(i, 1)) * math.sqrt(1 - (2 * hsh(i, 2) - 1) ** 2),
         2 * hsh(i, 2) - 1,
         math.sin(2 * math.pi * hsh(i, 1)) * math.sqrt(1 - (2 * hsh(i, 2) - 1) ** 2), 0.4 + hsh(i, 3)) for i in range(700)]


def chorus(g, t, li, li2, t0, t1, hl2=None, yawdir=1.0, boom_t=None):
    u = prog(t, t0, t1)
    keys = [(t0, orbit((0, 0, 0), 1500, -0.85 * yawdir, 0.22), (0, 0, 0), 60, 0.1 * yawdir),
            (lerp(t0, t1, 0.45), orbit((0, 0, 0), 1250, -0.05 * yawdir, 0.05), (0, 0, 0), 55, 0.0),
            (t1, orbit((0, 0, 0), 1700, 0.8 * yawdir, 0.3), (0, 80, 0), 55, -0.08 * yawdir)]
    cam = cam_at(t, keys, punch=3.0, shake=10 * pulse(t, 1, 6))
    env(g, cam, 420, fog=6000)
    # rotating rings around the type
    for k in range(3):
        R = 900 + k * 180
        pts = [(R * math.cos(a), (k - 1) * 60 + 40 * math.sin(a * 3 + t), R * math.sin(a)) for a in [2 * math.pi * q / 80 + t * 0.2 * (k + 1) for q in range(81)]]
        poly3(g, cam, pts, GOLD if k == 1 else GRID2, 2, 0.7)
        for q in range(0, 80, 8):
            point3(g, cam, pts[q], 5, GOLD, 0.8)
    hl = {'p(doom)': GOLD, 'foom': GOLD}
    hl.update(hl2 or {})
    lyric3x(g, cam, t, li, (0, -90, 0), (1, 0, 0), (0, -1, 0), 1700, 140, INK, hl, depth=110, n=8)
    if li2 is not None:
        lyric3x(g, cam, t, li2, (0, 130, -40), (1, 0, 0), (0, -1, 0), 1600, 120, INK, hl, depth=90, n=7)
    if boom_t is not None and t > boom_t:
        e = t - boom_t
        for (dx, dy, dz, sp) in EXPL:
            d = 1800 * sp * eo(clamp(e / 1.4))
            point3(g, cam, (dx * d, dy * d, dz * d), 4, GOLD if sp > 1.0 else INK, 0.8 * clamp(1.2 - e * 0.6))
        g.post = dict(glow=0.45)
        g.flash = 0.35 * math.exp(-e * 9)
    return cam


def s_foom(g, t, lt):
    tf = WT(7, 4)
    chorus(g, t, 6, 7, 22.55, 26.4, boom_t=tf - 0.02)


# ======================================================== CHINESE ROOM 26.4 - 30.0  (camera inside)
HANZI = '\u4e2d\u6587\u623f\u95f4\u7b26\u53f7\u89c4\u5219\u7406\u89e3\u610f\u4e49\u8bed\u6cd5\u8f93\u5165\u8f93\u51fa\u673a\u5668\u601d\u60f3'
RX, RY, RZ = 900, 520, 900


def _mushroom(F, c, s):
    x, y, z = c
    F.box((x, y - 40 * s, z), (26 * s, 80 * s, 26 * s), INK, BG, 2)
    cap = [(x + 70 * s * math.cos(a), y - 80 * s, z + 70 * s * math.sin(a)) for a in [2 * math.pi * q / 16 for q in range(16)]]
    for q in range(16):
        F.quad([cap[q], cap[(q + 1) % 16], (x, y - 135 * s, z)], GOLD, BG, 2)


def s_room(g, t, lt):
    # yaw: left wall -> whip past the slot -> right wall
    tsw = T0(9)
    if t < tsw - 0.25:
        yaw = lerp(-1.32, -1.05, prog(t, 26.4, tsw - 0.25))
    else:
        yaw = lerp(-1.05, 1.2, eio(prog(t, tsw - 0.25, tsw + 0.35))) + 0.12 * prog(t, tsw + 0.35, 30.0)
    pitch = 0.05 * math.sin(t * 1.3)
    ex = lerp(0, 120, prog(t, 26.4, 30.0)); ez = lerp(-260, 60, prog(t, 26.4, 30.0))
    eye = (ex, -40, ez)
    tgt = (ex + math.sin(yaw) * 1000, -40 + math.sin(pitch) * 1000, ez + math.cos(yaw) * 1000)
    cam = Cam3(shake_eye(eye, t, 6), tgt, 74, 0.03 * math.sin(t * 2))
    # walls: floor, ceiling, 4 walls as grids
    st = 90
    grid3(g, cam, (0, RY, 0), (1, 0, 0), (0, 0, 1), RX // st, RZ // st, st, GRID2, 1.0, 1.4, fog=0)
    grid3(g, cam, (0, -RY, 0), (1, 0, 0), (0, 0, 1), RX // st, RZ // st, st, GRID, 1.0, 1.2, fog=0)
    for sx in (-1, 1):
        grid3(g, cam, (sx * RX, 0, 0), (0, 1, 0), (0, 0, 1), RY // st, RZ // st, st, GRID2, 1.0, 1.3, fog=0)
    for sz in (-1, 1):
        grid3(g, cam, (0, 0, sz * RZ), (1, 0, 0), (0, 1, 0), RX // st, RY // st, st, GRID2, 1.0, 1.3, fog=0)
    # room edges in gold
    C = [(sx * RX, sy * RY, sz * RZ) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
    for a in range(8):
        for b in range(a + 1, 8):
            if sum(1 for k in range(3) if C[a][k] != C[b][k]) == 1:
                seg3(g, cam, C[a], C[b], GOLD, 3, 0.9)
    # hanzi tiles on walls (flicker in on beats)
    for i, ch in enumerate(HANZI):
        side = i % 3
        row = (i // 3) % 3; col = (i // 9) % 3 + (i % 2) * 0.5
        on = hsh(i + int(beat(t)), 4) > 0.3
        cc = GOLD if hsh(i, 9) < 0.3 else INK
        if side == 0 and row == 1:
            continue
        if side == 0:
            word3(g, cam, ch, (-RX + 2, -280 + row * 230, -500 + col * 380), (0, 0, 1), (0, -1, 0), 170, 130, cc, 'cjk', 0.6 if on else 0.25)
        elif side == 1:
            word3(g, cam, ch, (RX - 2, -280 + row * 230, 500 - col * 380), (0, 0, -1), (0, -1, 0), 170, 130, cc, 'cjk', 0.6 if on else 0.25)
        else:
            word3(g, cam, ch, (-600 + col * 420, -330 + row * 150, RZ - 2), (1, 0, 0), (0, -1, 0), 120, 130, cc, 'cjk', 0.6 if on else 0.25)
    # input slot on back wall + card sliding through
    poly3(g, cam, [(-200, 40, RZ - 1), (200, 40, RZ - 1), (200, 80, RZ - 1), (-200, 80, RZ - 1)], GOLD, 3, 1, True)
    cu = (t * 0.9) % 1.0
    cz = RZ - cu * 600
    fill3(g, cam, [(-150, 50, cz), (150, 50, cz), (150, 52, cz - 220), (-150, 52, cz - 220)], INK, 0.85, stroke=GOLD)
    text3(g, cam, 'INPUT_SLOT \u2192', (0, 120, RZ - 5), 26, GOLD, 'mono')
    # desk with rulebook and shrooms
    F = Faces()
    F.box((420, 330, 420), (700, 30, 380), GOLD, BG, 2)
    for lx in (-1, 1):
        for lz in (-1, 1):
            F.box((420 + lx * 320, 440, 420 + lz * 160), (24, 190, 24), INK, BG, 2)
    F.box((260, 290, 420), (220, 50, 160), INK, BG, 2)
    _mushroom(F, (560, 315, 380), 1.0)
    _mushroom(F, (660, 315, 500), 0.7)
    _mushroom(F, (480, 315, 520), 0.55)
    F.draw(g, cam)
    text3(g, cam, 'RULEBOOK v\u221e', (260, 240, 420), 22, GOLD, 'mono')
    hl = {'chinese': GOLD, 'room,': GOLD, 'shrooms': GOLD}
    lyric3x(g, cam, t, 8, (-RX + 30, -60, 0), (0, 0, 1), (0, -1, 0), 1500, 120, INK, hl, depth=40, n=4)
    lyric3x(g, cam, t, 9, (RX - 30, -120, 150), (0, 0, -1), (0, -1, 0), 1400, 120, INK, hl, depth=40, n=4)
    g.post = dict(vig=1.2)


# ======================================================== SHOGGOTH 30.0 - 38.4
TENT = [(hsh(i, 1) * 2 * math.pi, (hsh(i, 2) - 0.5) * 2.2, 500 + hsh(i, 3) * 700) for i in range(26)]


def _tent(i, t, k):
    a, el, Ln = TENT[i]
    u = k / 24
    r = Ln * u
    wob = 160 * u * u
    x = math.cos(a) * math.cos(el) * r + math.sin(t * 1.3 + i + u * 5) * wob
    y = math.sin(el) * r * 0.7 + math.cos(t * 1.1 + i * 2 + u * 4) * wob
    z = math.sin(a) * math.cos(el) * r + math.sin(t * 0.9 + i * 3 + u * 6) * wob + 200
    return (x, y, z)


def s_shoggoth(g, t, lt):
    eyes_t = T0(11)
    keys = [(30.0, orbit((0, 0, 200), 2600, -0.4, 0.18), (0, 0, 200), 52, 0.04),
            (33.2, orbit((0, 0, 200), 1900, 0.35, 0.05), (0, 0, 100), 55, -0.03),
            (35.6, orbit((0, 0, 200), 1500, -0.1, -0.05), (0, -60, 0), 58, 0.0),
            (37.2, orbit((0, 0, 200), 2400, 1.4, 0.45), (0, 0, 200), 55, 0.12),
            (38.4, orbit((0, 0, 200), 3100, 2.2, 0.6), (0, 0, 200), 50, 0.0)]
    cam = cam_at(t, keys, punch=2.0, shake=12 * pulse(t, 1, 7) * (t > 35.6))
    env(g, cam, 700, fog=6500)
    dust(g, cam, t)
    for i in range(len(TENT)):
        pts = [_tent(i, t, k) for k in range(25)]
        poly3(g, cam, pts, GRID2, 3.0, 0.9)
        for k in range(0, 25, 2):
            point3(g, cam, pts[k], 9 * (1 - k / 26) + 2, GOLD if (k + i) % 7 == 0 else INK, 0.85)
    # core blob point cloud
    for i in range(380):
        th = hsh(i, 5) * 2 * math.pi; ph = math.acos(2 * hsh(i, 6) - 1)
        r = 330 * (0.85 + 0.25 * math.sin(t * 3 + i))
        point3(g, cam, (r * math.sin(ph) * math.cos(th), r * math.cos(ph), r * math.sin(ph) * math.sin(th) + 200), 3, INK, 0.6)
    # smiley mask (the lie) slipping
    slip = prog(t, WT(10, 4) - 0.05, WT(10, 4) + 0.7)
    mc = (-slip * 380, -40 - slip * 420, -160)
    mrot = slip * 0.9
    def mx(p):
        x, y, z = p
        c, s = math.cos(mrot), math.sin(mrot)
        return (mc[0] + x * c - y * s, mc[1] + x * s + y * c, mc[2] + z)
    fill3(g, cam, [mx(p) for p in disc_pts((0, 0, 0), 260, 40)], INK, 0.95, stroke=GOLD, w=3)
    fill3(g, cam, [mx(p) for p in disc_pts((-90, -60, -2), 28, 16)], BG, 1)
    fill3(g, cam, [mx(p) for p in disc_pts((90, -60, -2), 28, 16)], BG, 1)
    sm = [mx((150 * math.cos(a), 30 + 110 * math.sin(a), -2)) for a in [math.pi * (0.15 + 0.7 * q / 16) for q in range(17)]]
    poly3(g, cam, sm, BG, 12, 1)
    text3(g, cam, 'RLHF_MASK.PNG', mx((0, -300, 0)), 24, GOLD, 'mono')
    # shinigami eyes
    if t > eyes_t - 0.1:
        e = prog(t, eyes_t - 0.1, eyes_t + 0.4)
        for sx in (-1, 1):
            c = (sx * 140, -80, -40)
            fill3(g, cam, disc_pts(c, 60 * e, 24), GOLD, 1, stroke=GOLDL, w=3)
            fill3(g, cam, disc_pts((c[0], c[1], c[2] - 2), 18 * e, 12), BG, 1)
        word3(g, cam, '\u6b7b\u795e', (0, -80, 600), (1, 0, 0), (0, -1, 0), 1500, 300, GOLD, 'cjk', 0.35 * e)
    hl = {"shoggoth's": GOLD, 'lies,': GOLD, 'shinigami': GOLD, 'eyes': GOLD}
    lyric3x(g, cam, t, 10, (0, 420, -350), (1, 0, 0), (0, -1, 0), 1800, 120, INK, hl, depth=60)
    lyric3x(g, cam, t, 11, (0, 420, -350), (1, 0, 0), (0, -1, 0), 1800, 120, INK, hl, depth=60)
    if t > 35.7:
        u = prog(t, 35.7, 38.4)
        for k in range(int(6 + u * 30)):
            R = 1400 + k * 60
            yy = 700 - ((t * 400 + k * 90) % 1400)
            pts = [(R * math.cos(a), yy, R * math.sin(a) + 200) for a in [2 * math.pi * q / 60 for q in range(61)]]
            poly3(g, cam, pts, GOLD if k % 4 == 0 else GRID2, 1.6, 0.4 + 0.4 * u)
        g.flash = 0.25 * pulse(t, 2, 8) * u
    g.post = dict(ca=0.4 if t > eyes_t else 0)


TL = [
    (0.0, s_boot, BG),
    (1.8, s_eye, BG),
    (9.36, s_loss, BG),
    (17.7, s_jaw, BG),
    (22.55, s_foom, BG),
    (26.4, s_room, BG),
    (30.0, s_shoggoth, BG),
]
