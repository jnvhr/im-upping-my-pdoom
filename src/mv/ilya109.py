# v109: "What did Ilya see? We'll never know" overhauled.
# A lone figure stands in a long classified corridor in front of the vault door. On "see?" the door swings open and
# blinding gold light pours out around his silhouette, with the intelligence glimpsed inside. He walks in. On
# "We'll" the door slams behind him: [REDACTED]. Through "never know", redaction bars stamp across the door on
# each beat while the camera pulls back down a corridor of identical sealed doors. Their lights go dark one by one,
# until only a single "?" is left glowing before "Was it all for show?".
import math
from cam3d import *
from s3a import T0, T1, WT
from s4a import _panels

BPH = 0.2462121212121225; BP = 60.0 / 132.0
FLOOR = 400.0
CX = 1400.0                     # corridor half width
SIDE_Z = (-1300, -2500, -3700, -4900, -6100)


def _beat(t):
    b = (t - BPH) / BP
    return int(math.floor(b)), (b - math.floor(b)) * BP


def _walker(t, z, walk):
    """standing / walking joints, facing +z (into the door)"""
    ph = walk * math.pi * 2
    sw = math.sin(ph) * (1 if walk > 0 else 0)
    bob = abs(math.sin(ph)) * 10 if walk > 0 else 0
    j = {}
    j['head'] = (0, -330 - bob, z)
    j['neck'] = (0, -240 - bob, z)
    j['hip'] = (0, 50 - bob, z)
    j['le'] = (-95, -100 - bob, z - 40 * sw); j['re'] = (95, -100 - bob, z + 40 * sw)
    j['lh'] = (-105, 30 - bob, z - 90 * sw); j['rh'] = (105, 30 - bob, z + 90 * sw)
    j['lk'] = (-45, 230, z + 110 * sw); j['rk'] = (45, 230, z - 110 * sw)
    j['lf'] = (-48, FLOOR - 10, z + 150 * sw - 20); j['rf'] = (48, FLOOR - 10, z - 150 * sw - 20)
    return j


def _door_xf(ang):
    def dxf(v):
        x, y, z = v
        x2 = x + 500
        c, s = math.cos(ang), math.sin(ang)
        return (x2 * c - z * s - 500, y - 100, x2 * s + z * c)
    return dxf


def s_vault(g, t, lt):
    from person import person, fill_joints
    t0 = T0(44); tsee = WT(44, 3); tw = WT(44, 4); tn = WT(44, 5); tk = WT(44, 6); tE = T0(45)
    tslam = tw + 0.38
    # door: cracks on "Ilya", swings wide on "see?", slams on "We'll"(+0.38)
    op = 0.06 * eio(prog(t, t0 + 0.2, WT(44, 2))) + 0.94 * eio(prog(t, tsee - 0.08, tsee + 0.35))
    op *= 1 - eio(prog(t, tslam - 0.16, tslam))
    slam = t >= tslam
    e = max(0.0, t - tslam)
    bi, bt = _beat(t)
    kick = math.exp(-bt * 9.0)
    keys = [(t0, (-260, -40, -2900), (0, -80, 0), 48, 0.02),
            (tsee, (-330, -250, -1500), (0, -140, 0), 56, 0.0),
            (tw + 0.1, (-200, -220, -1250), (40, -140, 200), 60, 0.0),
            (tslam + 0.05, (-160, -200, -1150), (0, -140, 0), 60, 0.0),
            (tk + 0.3, (120, -420, -2500), (0, -180, 0), 54, -0.03),
            (tk + 1.8, (0, -1000, -5200), (0, -200, -1300), 52, 0.0),
            (tE, (0, -1500, -7200), (0, -150, -2600), 50, 0.02)]
    cam = cam_at(t, keys, shake=55 * math.exp(-e * 6) * slam + 10 * kick * slam)
    env(g, cam)
    gl = clamp(op / 0.7)
    # --- what is inside: the intelligence, glimpsed through the opening
    core = (0, -100, 1600)
    if gl > 0.02:
        point3(g, cam, core, 520, GOLDL, 0.25 * gl)
        for i in range(260):
            th = hsh(i, 1) * 2 * math.pi; ph = math.acos(2 * hsh(i, 2) - 1)
            rr = 420 * (0.8 + 0.3 * math.sin(t * 4 + i))
            point3(g, cam, (core[0] + rr * math.sin(ph) * math.cos(th + t), core[1] + rr * math.cos(ph),
                            core[2] + rr * math.sin(ph) * math.sin(th + t)), 5, GOLDL if i % 4 else INK, gl)
        for k in range(4):
            R_ = 560 + k * 150
            pts = [v_add(core, rot3((R_ * math.cos(a), R_ * math.sin(a), 0), t * (0.7 + k * 0.3), k * 1.1, 0))
                   for a in [2 * math.pi * q / 48 for q in range(49)]]
            poly3(g, cam, pts, GOLD, 3, gl)
        # an iris looking back out at him
        for k in range(3):
            pts = [v_add(core, (r_ * math.cos(a), r_ * math.sin(a) * 0.55, -300))
                   for r_ in [(160, 110, 60)[k]] for a in [2 * math.pi * q / 40 for q in range(41)]]
            poly3(g, cam, pts, INK if k == 2 else GOLDL, 5, gl)
    # --- corridor: floor, side walls with sealed doors, front wall with the vault opening
    F = SFaces()
    dimk = 1 - 0.65 * eio(prog(t, tk + 0.5, tE - 0.2))
    WC = tuple(int(v * dimk) for v in (44, 44, 41)); WS = tuple(int(v * dimk) for v in (58, 58, 54))
    _panels(F, (-CX, FLOOR, -7600), (1, 0, 0), (0, 0, 1), 4, 19, 2 * CX / 4, 400, tuple(int(v * dimk) for v in (30, 30, 28)), WS)
    for sx in (-1, 1):
        _panels(F, (sx * CX, -1100, -7600), (0, 0, 1), (0, 1, 0), 19, 2, 400, 750, WC, WS)
    for (x0, x1, y0, y1) in ((-CX, -500, -1100, FLOOR), (500, CX, -1100, FLOOR), (-500, 500, -1100, -600)):
        _panels(F, (x0, y0, 0), (1, 0, 0), (0, 1, 0), 2, 2, (x1 - x0) / 2, (y1 - y0) / 2, WC, WS)
    F.draw(g, cam)
    # side doors: framed, stamped, a light slit underneath that goes dark beat by beat at the end
    off_b = [tk + 0.55 + BP * q for q in range(10)]
    n = 0
    for zi, z in enumerate(SIDE_Z):
        for sx in (-1, 1):
            x = sx * (CX - 4)
            fr = [(x, -560, z - 300), (x, -560, z + 300), (x, FLOOR, z + 300), (x, FLOOR, z - 300)]
            poly3(g, cam, fr, GOLDD, 2.5, 0.9, True)
            text3(g, cam, 'CLASSIFIED', (x, -640, z), 26, GOLD, 'mono', 0.8)
            lit = t < off_b[min(n, 9)] if slam else True
            n += 1
            if lit:
                seg3(g, cam, (x - sx * 6, FLOOR - 6, z - 280), (x - sx * 6, FLOOR - 6, z + 280), GOLDL, 7, 1.0)
                point3(g, cam, (x - sx * 10, -720, z), 26, GOLDL, 0.9)
                point3(g, cam, (x - sx * 10, -720, z), 70, GOLD, 0.25)
            else:
                point3(g, cam, (x - sx * 10, -720, z), 14, (40, 38, 30), 0.9)
            if slam and t > tn + 0.1 + 0.05 * zi:
                word3(g, cam, '[REDACTED]', (x - sx * 8, -150, z), (0, 0, -sx), (0, -1, 0), 520, 90, GOLD, 'monox', 0.85)
    # overhead strip lights flicker on the slam
    fl = 1.0 if not slam else (0.25 + 0.75 * (hsh(int(t * 30), 9) > 0.4) if e < 0.5 else 0.55)
    for sx in (-1, 1):
        seg3(g, cam, (sx * 700, -1090, -7400), (sx * 700, -1090, -100), GOLDL, 3, 0.35 * fl)
    # light pouring out of the opening, around his silhouette
    if gl > 0.02:
        for i in range(48):
            yy = -580 + hsh(i, 2) * 960; xx = -480 + hsh(i, 5) * 960
            seg3(g, cam, (xx, yy, 0), (xx * 1.8 + (hsh(i, 4) - 0.5) * 600, yy * 1.3 + 200 * hsh(i, 6), -2600 * gl),
                 GOLDL, 3, 0.3 * gl)
        fill3(g, cam, [(-500, -600, 2), (500, -600, 2), (500, 400, 2), (-500, 400, 2)], GOLDL, 0.35 * gl)
        # light pool on the floor
        fill3(g, cam, [(-500, FLOOR - 2, 0), (500, FLOOR - 2, 0), (900, FLOOR - 2, -1800 * gl), (-900, FLOOR - 2, -1800 * gl)],
              GOLD, 0.22 * gl)
    # the figure: stands, then walks in through the door before it slams
    tw0, tw1 = tsee + 0.2, tslam - 0.05
    wz = lerp(-760, 420, eio(prog(t, tw0, tw1)) if t < tw1 else 1.0)
    walk = (t - tw0) / 0.42 if tw0 < t < tw1 else 0.0
    fig = None
    if not slam and wz < 300:
        sil = 1 - 0.75 * gl
        col = lambda c: tuple(int(v * sil) for v in c)
        PF = SFaces()
        person(PF, fill_joints(_walker(t, wz, walk)), 1, shirt=col((150, 148, 140)), skin=col((196, 186, 170)),
               pants=col((62, 62, 60)), hair=col((34, 32, 30)))
        fig = PF
        if wz > -150:
            PF.draw(g, cam)
    # the vault door
    dxf = _door_xf(op * 1.45)
    D = SFaces()
    D.sbox((0, 0, 0), (1000, 1000, 120), (86, 86, 80), GOLDD, 1.5, xf=dxf, amb=0.35)
    D.draw(g, cam)
    for k in range(3):
        rr = 120 + k * 100
        pts = [dxf((rr * math.cos(a), rr * math.sin(a), -64)) for a in
               [2 * math.pi * q / 40 + t * (0.5 + k * 0.4) * (1 if k % 2 else -1) for q in range(41)]]
        poly3(g, cam, pts, GOLD, 4, 1)
    for k in range(6):
        a = 2 * math.pi * k / 6 + t * 0.6
        seg3(g, cam, dxf((0, 0, -64)), dxf((360 * math.cos(a), 360 * math.sin(a), -64)), GOLD, 4, 1)
    if fig is not None and wz <= -150:
        fig.draw(g, cam)
    if slam:
        st = eback(clamp(e / 0.18))
        end_q = t > tE - 0.36
        g.flash = 0.35 * math.exp(-e * 9)
        # redaction bars stamped across the door on each beat
        labels = ['ACCESS DENIED', 'WITNESS: UNAVAILABLE', 'FILE NOT FOUND', 'REASON: \u2588\u2588\u2588\u2588\u2588\u2588']
        for q, lab in enumerate(labels):
            tq = tk + 0.17 + BP * q
            if t < tq:
                continue
            s2 = eback(clamp((t - tq) / 0.12))
            y = -380 + q * 190
            wv = 1200 * s2
            bar = [(-wv / 2, y - 60, -80), (wv / 2, y - 60, -80), (wv / 2, y + 60, -80), (-wv / 2, y + 60, -80)]
            ba = 1 - 0.8 * clamp((t - (tE - 0.36)) / 0.2)
            fill3(g, cam, bar, (8, 8, 8), 0.95 * ba, stroke=GOLD, w=2.5)
            text3(g, cam, lab, (0, y, -84), 44, GOLD, 'monox', clamp(s2 * 1.5) * ba)
        if not end_q:
            word3(g, cam, '[REDACTED]', (0, -100, -90), (1, 0, 0), (0, -1, 0), 900 * lerp(1.5, 1.0, st), 160, GOLD,
                  'monox', clamp(st * 2) * (1 - 0.6 * clamp((t - tk - 0.1) / 0.3)))
        else:
            qa = eback(clamp((t - (tE - 0.36)) / 0.2))
            word3(g, cam, '?', (0, -150, -90), (1, 0, 0), (0, -1, 0), 700 * qa, 400, GOLD, 'sans', 1, x=True, depth=60, n=5)
    c, r, u = ahead(cam, 1050)
    lyric3x(g, cam, t, 44, v_add(c, v_mul(cam.u, 340)), r, u, 1800, 120, INK,
            {'ilya': GOLD, 'see?': GOLD, 'never': GOLD, 'know': GOLD}, depth=60)
    g.post = dict(glow=0.6 + 0.5 * gl, vig=0.9 + 0.5 * (1 - dimk))
