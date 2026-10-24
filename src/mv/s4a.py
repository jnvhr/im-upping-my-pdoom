import os
"""v3 scenes 0:00 - 0:38.6"""
import math
from cam3d import *
from s3a import T0, T1, WT, IRIS, dust, s_boot, s_eye, s_loss, s_shoggoth, TENT, _tent

DARKS = (34, 34, 32)


# ======================================================== shared 3D eye
def iris_lines(g, cam, t, xf, nerv=0.0, pr=90, glitch=0.0):
    bf = beat_frac(t)
    for k in range(11):
        r = 100 + k * 34
        wave = math.exp(-((bf * 11 - k) ** 2) * 0.5)
        if nerv > 0:
            wave = max(wave, hsh(int(t * 18), k) ** 2 * nerv)
        aa = 0.25 + 0.75 * wave
        segs = 6 + (k % 4) * 3
        jit = (hsh(int(t * 24), k + 40) - 0.5) * 0.5 * nerv
        for sgi in range(segs):
            a0 = 2 * math.pi * sgi / segs + t * 0.15 * (1 if k % 2 else -1) + k + jit
            a1 = a0 + 2 * math.pi / segs * (0.55 + 0.35 * hsh(k, sgi))
            pts = [xf((r * math.cos(a0 + (a1 - a0) * q / 10), r * math.sin(a0 + (a1 - a0) * q / 10), -k * 8)) for q in range(11)]
            poly3(g, cam, pts, GOLD if (k + sgi) % 3 == 0 else INK, 2.2, aa)
    for i, tr in enumerate(IRIS):
        pts = [xf((r * math.cos(a), r * math.sin(a), z * 0.5)) for (r, a, z) in tr]
        on = hsh(i, 7) < 0.3 + 0.4 * feat('flux', t) + 0.5 * glitch * hsh(i, int(t * 20))
        poly3(g, cam, pts, GOLD if on else GRID2, 2.0 if on else 1.4, 0.95)
        point3(g, cam, pts[-1], 5, GOLDL if (on and glitch > 0.3) else (GOLD if on else INK), 0.9)
    fill3(g, cam, [xf(p) for p in disc_pts((0, 0, 2), pr, 40)], BG, 1.0, stroke=GOLD, w=3)
    fill3(g, cam, [xf(p) for p in disc_pts((0, 0, 1), pr * 0.35, 20)], GOLD, 0.9)


def eye_model(g, cam, t, R=560, gaze=(0.0, 0.0), lid=1.0, pr=90, nerv=0.0, glitch=0.0):
    """eyeball centred at origin looking toward -z. lid: 1 open, 0 closed"""
    gx, gy = gaze
    S = SFaces()
    ring = [(R * 1.15 * math.cos(2 * math.pi * q / 40), R * 1.0 * math.sin(2 * math.pi * q / 40), -R * 0.15) for q in range(41)]
    S.tube(ring, R * 0.2, (30, 30, 28), None, 8, amb=0.35)
    S.draw(g, cam)
    F = SFaces()
    F.sphere((0, 0, 0), R, (52, 52, 49), None, 10, 22, amb=0.35)
    F.draw(g, cam)
    s = 0.62  # iris radius scale relative to R

    def xf(p):
        x, y, z = p
        q = (x * s * R / 560, y * s * R / 560, -R * 0.93 + z)
        return rot3(q, gy, gx, 0)
    iris_lines(g, cam, t, xf, nerv, pr, glitch)
    # lids (shell slightly larger than the eye)
    up = lerp(0.52, 0.29, lid)
    lo = lerp(0.52, 0.75, lid)
    L = SFaces()
    L.sphere((0, 0, 0), R * 1.07, DARKS, (60, 60, 56), 6, 26, lat0=0.0, lat1=up, amb=0.3, w=0.8)
    L.sphere((0, 0, 0), R * 1.07, DARKS, (60, 60, 56), 4, 26, lat0=lo, lat1=1.0, amb=0.3, w=0.8)
    L.draw(g, cam)
    for th, c in ((up, GOLD), (lo, GRID2)):
        a = math.pi * th
        pts = [(R * 1.08 * math.sin(a) * math.cos(ph), -R * 1.08 * math.cos(a), R * 1.08 * math.sin(a) * math.sin(ph)) for ph in [math.pi + math.pi * q / 30 for q in range(31)]]
        poly3(g, cam, pts, c, 4, 1)


def eye_keys():
    """one continuous camera move for 'Sparks of AGI' -> 'nervous' -> dive"""
    tn = WT(1, 4); ts = WT(2, 2); tend = T0(3)
    return [(1.8, orbit((0, 0, 0), 2900, -0.75, 0.32), (0, 0, 0), 50, 0.05),
            (4.2, orbit((0, 0, 0), 1900, -0.25, 0.18), (0, 40, 0), 52, 0.0),
            (T0(1), orbit((0, 0, 0), 1500, 0.35, 0.10), (0, 60, 0), 54, -0.03),
            (tn, orbit((0, 0, 0), 1250, 0.05, 0.05), (0, 20, 0), 56, 0.0),
            (ts, orbit((0, 0, 0), 1350, -0.15, 0.02), (0, 80, 0), 57, 0.02),
            (tend - 0.55, orbit((0, 0, 0), 1150, 0.0, 0.0), (0, 0, 0), 58, 0.0),
            (tend, (0, 0, -60), (0, 0, 400), 75, 0.2)]


def s_eye2(g, t, lt):
    s_eye(g, t, lt, keys_override=eye_keys())


# ======================================================== NERVOUS 5.9 - 9.5 (same eye model as the opening)
from s3a import EYEBALL


def _drop(g, cam, p, n, size, al, el=0.0):
    """a clear water bead: soft contact shadow, see-through body, dark refraction rim, caustic, sharp specular"""
    q = cam.p(p)
    if q is None or al <= 0.01:
        return
    if v_dot(n, v_sub(cam.eye, p)) <= 0:
        return
    r = max(1.5, size * q[2] / (cam.F / 1000.0))
    x, y = q[0], q[1]
    ry = r * (1 + 0.55 * el)
    yc = y - (ry - r) * 0.5                     # elongated upward, heavy bottom
    g.ellipse(x + r * 0.18, y + r * 0.22, r * 1.05, ry * 1.02, fill=(8, 8, 7), a=al * 0.28)
    g.ellipse(x, yc, r, ry, fill=(235, 236, 230), a=al * 0.16)
    g.ellipse(x, yc, r * 0.82, ry * 0.8, fill=(20, 20, 18), a=al * 0.10)
    g.ellipse(x, yc, r, ry, stroke=(28, 27, 25), w=max(1.0, r * 0.14), a=al * 0.45)
    g.ellipse(x + r * 0.05, y + r * 0.45, r * 0.55, r * 0.28, fill=(240, 238, 228), a=al * 0.32)
    g.circle(x - r * 0.38, yc - ry * 0.38, max(0.8, r * 0.2), fill=(255, 255, 252), a=al * 0.95)
    g.circle(x - r * 0.12, yc - ry * 0.55, max(0.5, r * 0.08), fill=(255, 255, 252), a=al * 0.7)


def _snrm(lat, lon):
    cl = math.cos(lat)
    return (cl * math.sin(lon), -math.sin(lat), -cl * math.cos(lon))


def sweat(g, cam, t, amt, Rs=590.0, n=16, C=(0.0, 0.0, 560.0), xf=None):
    """realistic sweat: a sheen of tiny beads on the brow, some swell, break loose and run down leaving wet streaks"""
    if amt <= 0.01:
        return
    X = xf or (lambda p: p)
    _sn = _snrm
    _snrm_ = lambda lat, lon: v_sub(X(v_add(C, _sn(lat, lon))), C)
    # tiny static beads, appearing as the nerves build
    for i in range(70):
        if hsh(i, 61) > amt:
            continue
        lon = (hsh(i, 62) - 0.5) * 2.4
        lat = 0.62 + hsh(i, 63) * 0.75
        if abs(lon) < 0.45 and lat < 0.8:
            continue
        nrm = _snrm_(lat, lon)
        sz = 4 + 8 * hsh(i, 64) ** 2
        _drop(g, cam, v_add(C, v_mul(nrm, Rs)), nrm, sz * (0.6 + 0.4 * clamp((amt - hsh(i, 61)) * 4)), clamp((amt - hsh(i, 61)) * 5))
    # running drops
    for i in range(n):
        per = 1.3 + hsh(i, 21) * 1.1
        life = ((t + hsh(i, 22) * per) % per) / per
        lon = (1 if i % 2 else -1) * (0.5 + 0.6 * hsh(i, 23))
        lat0 = 0.6 + hsh(i, 24) * 0.5
        grow = clamp(life / 0.35)
        u = clamp((life - 0.35) / 0.65)
        slide = u * u * (1.6 - 0.6 * u)
        lat = lat0 - slide * (lat0 + 1.25)
        wob = 0.04 * math.sin(lat * 9 + i)      # drops wander a little as they run
        sz = (13 + 11 * hsh(i, 25)) * (0.45 + 0.55 * grow) * (1 - 0.25 * u)
        al = amt * clamp(life / 0.08) * clamp((1 - life) / 0.1)
        if lat > -1.1:
            nrm = _snrm_(lat, lon + wob)
            p = v_add(C, v_mul(nrm, Rs))
            if u > 0.02 and v_dot(nrm, v_sub(cam.eye, p)) > 0:
                tr = [v_add(C, v_mul(_snrm_(lat + (lat0 - lat) * k / 9, lon + 0.04 * math.sin((lat + (lat0 - lat) * k / 9) * 9 + i)), Rs - 1)) for k in range(10)]
                poly3(g, cam, tr, (14, 14, 12), 2.6, al * 0.30)
                poly3(g, cam, [v_add(q_, (-2, 0, 0)) for q_ in tr], (230, 230, 224), 0.9, al * 0.35)
            _drop(g, cam, p, nrm, sz, al, el=min(1.0, u * 3))
        else:
            fall = -(lat + 1.1)
            nrm = _snrm_(-1.1, lon)
            p = v_add(v_add(C, v_mul(nrm, Rs)), (0, 900 * fall * fall + 200 * fall, 0))
            _drop(g, cam, p, (0, 0, -1), sz * 0.9, al, el=0.8)


def s_nervous(g, t, lt):
    t0 = T0(1); tc = WT(1, 1); tn = WT(1, 4); ts = WT(2, 2); tend = T0(3)
    # gaze: steady, then nervous darting
    gx = gy = 0.0
    if t > tn - 0.05:
        k = int((t - tn) / 0.15)
        tgx, tgy = (hsh(k, 3) - 0.5) * 260, (hsh(k, 4) - 0.5) * 140
        pk = (hsh(k - 1, 3) - 0.5) * 260, (hsh(k - 1, 4) - 0.5) * 140
        u = eo(clamp(((t - tn) % 0.15) / 0.05))
        gx, gy = lerp(pk[0], tgx, u), lerp(pk[1], tgy, u)
        if t > ts:
            f = 1 - eo(prog(t, ts, ts + 0.3))
            gx, gy = gx * f, gy * f
    # blinks (vertical squash of the whole iris) and a squint on "no surprise"
    sy = 1.0
    for tb in (tn + 0.05, tn + 0.36):
        sy = min(sy, 1 - math.exp(-((t - tb) / 0.06) ** 2))
    if t > ts - 0.1:
        sy = min(sy, lerp(1.0, 0.35, eo(prog(t, ts - 0.1, ts + 0.3))))
    sy = max(sy, 0.04)
    nerv = prog(t, tn - 0.1, tn + 0.2) * (1 - 0.6 * prog(t, ts, ts + 0.5))
    glitch = prog(t, tc - 0.05, tc + 0.3) * (1 - prog(t, tn + 0.6, ts))
    dive = eio(prog(t, tend - 0.55, tend))
    keys = eye_keys()
    cam = cam_at(t, keys, shake=26 * nerv)
    env(g, cam, int(lerp(650, 160, nerv)), fog=6000)
    from eye3 import draw_eye, blink
    bl = blink(t, (tn + 0.05, tn + 0.36))
    sq = eo(prog(t, ts - 0.1, ts + 0.3))
    lu = lerp(lerp(34, 40, nerv), 13, sq) * (1 - bl) + 1 * bl + 8 * dive
    ll = lerp(lerp(-30, -33, nerv), -12, sq) * (1 - bl) - 1 * bl - 8 * dive
    dil = (1 + 0.35 * nerv * math.sin(t * 40)) * (1 - 0.45 * prog(t, ts, ts + 0.4)) * (1 + 0.6 * dive)
    from eye3 import look_at_cam
    ly, lp = look_at_cam(cam, 0.85)
    yw = (ly + 0.08 * math.sin(t * 0.7) + gx / 900) * (1 - dive)
    pt = (lp + 0.05 * math.sin(t * 0.5 + 1) - gy / 900) * (1 - dive)
    draw_eye(g, cam, t, yw, pt, lu, ll, dil, glitch=max(glitch, nerv * 0.6), wave=0.0)
    X = lambda p: (p[0] + gx * 0.6, p[1] + gy * 0.6, p[2])
    # v24: sweat beads up on the eye's skin and runs down (replaces the spark particles)
    from eye3 import gaze_xf
    sweat(g, cam, t, prog(t, tn - 0.15, tn + 0.25), xf=None)
    hl = {'circuits': GOLD, 'nervous,': GOLD, 'surprise': GOLD}
    for li in (1, 2):
        if li == 1 and t > LINE_WORDS[2][0][1] - 0.04:
            continue
        lyric3x(g, cam, t, li, (0, 470, -160), (1, 0, 0), (0, -1, 0), 1900, 112, INK, hl, depth=50)
    tag = 'IRIS_SCAN  //  SUBJECT: HUMAN  //  NOMINAL' if t < tc - 0.05 else 'IRIS_SCAN  //  CIRCUIT LOAD %3d%%  //  %s' % (int(40 + 60 * max(glitch, nerv)), 'PUPIL DILATION ERR' if nerv > 0.3 else 'NOMINAL')
    text3(g, cam, tag, (0, -470, 0), 26, GOLD if nerv > 0.3 else DIM, 'mono', 0.9)


# ======================================================== JAW (solid mouth) 17.8 - 22.6
TEETH_N = 12
ROOF = (40, 40, 38)
FLESH = (58, 56, 52)


def _ucurve(u, R):
    a = math.pi * u
    return (R * math.cos(a), 600 - R * math.sin(a) * 1.15)


MW = 420.0            # mouth half-width
SKIN = (66, 60, 56)
LIP = (122, 104, 98)
GUM = (138, 88, 90)
TOOTH = (232, 230, 222)


def _mouth_open(t):
    """pac-man chomp: one clean open-shut per sung syllable; from the 'A' of 'alive' it opens wide and holds"""
    W5 = LINE_WORDS[5]
    sy = []
    t0, t1 = W5[0][1], W5[0][2]
    for k in range(4):                       # Chat-G-P-T
        sy.append(t0 + (t1 - t0) * k / 4)
    for w, a, e in W5[1:5]:
        sy.append(a)
    tA = W5[5][1]
    sy.append(tA)
    op = 0.04
    for i in range(len(sy) - 1):
        a, b = sy[i], sy[i + 1]
        d = min(b - a, 0.32)
        if a <= t < a + d:
            u = (t - a) / d
            op = 0.04 + 0.62 * (1 - abs(2 * u - 1))     # linear wedge open, snap shut
    wide = eio(prog(t, tA - 0.05, tA + 0.3))
    return lerp(op, 1.0, wide), wide


def _lipf(x):
    q = clamp(1 - (x / MW) ** 2, 0, 1)
    return q ** 0.7


def _mouth_edges(op, wide=1.0):
    H = 320 * op
    def f(x): return lerp(clamp(1 - abs(x) / MW), _lipf(x), wide)
    def yu(x): return -(10 + 0.96 * H * f(x))
    def yl(x): return 10 + 0.96 * H * f(x)
    def zz(x): return 110 * (x / MW) ** 2
    return yu, yl, zz


def s_jaw(g, t, lt):
    tA0 = T0(5); tE = T0(6)
    tA = LINE_WORDS[5][5][1]
    keys = [(tA0, (0, -80, -1550), (0, 30, 0), 46, 0.0),
            (18.6, (-560, -220, -1300), (0, 30, 0), 48, 0.04),
            (20.4, (440, -60, -1200), (0, 40, 0), 50, -0.03),
            (tA, (0, 20, -1000), (0, 60, 300), 52, 0.0),
            (tA + 0.55, (0, 60, -120), (0, 60, 700), 62, 0.0),
            (tE, (0, 60, 1450), (0, 60, 2400), 66, 0.0)]
    cam = cam_at(t, keys)
    camz = cam.eye[2] if hasattr(cam, 'eye') else path(t, keys)[0][2]
    inside = eio(prog(camz, -260, 40))
    env(g, cam) if inside < 0.99 else None
    op, wide = _mouth_open(t)
    yu, yl, zz = _mouth_edges(op, wide)
    N = 28
    xs = [-MW + 2 * MW * i / N for i in range(N + 1)]
    F = SFaces()
    # just gums and teeth: two horseshoe arches, deeper toward the back
    zA = lambda x: 300 * (x / MW) ** 2
    NT = 14
    for row, ed, sg in ((0, yu, 1), (1, yl, -1)):
        gp = [(x, ed(x) - sg * 34, zA(x)) for x in xs]
        F.tube(gp, 44, GUM, None, 10, rs=[44 * (0.75 + 0.25 * _lipf(x)) for x in xs], amb=0.45)
        F.tube([(x, ed(x) - sg * 70, zA(x) + 30) for x in xs], 30, mix(GUM, (20, 18, 18), 0.4), None, 8, amb=0.4)
        for i in range(NT):
            u = i / (NT - 1)
            x = -MW * 0.9 + 2 * MW * 0.9 * u
            fr = _lipf(x)
            gap = yl(x) - yu(x)
            h = min((88 if row == 0 else 74) * (0.7 + 0.3 * fr), 0.46 * gap + 30)
            w = 2 * MW * 0.9 / (NT - 1) * (0.46 + 0.1 * (1 - fr))
            c = (x, ed(x) + sg * (h * 0.5 - 8), zA(x) - 6)
            F.sphere(c, w, TOOTH, None, 8, 16, sy=(h * 0.55) / w, sz=0.5 + 0.35 * (1 - fr), amb=0.55)
    # tongue, deep and dim
    if op > 0.3:
        F.sphere((0, yl(0) * 0.6 + 10, 330), 230, (92, 60, 62), None, 6, 14, sy=0.3, sz=1.3, amb=0.3)
    if inside < 0.99:
        F.draw(g, cam, fog=0)
    # past the lips: pure dark cave
    if inside > 0:
        g.rect(0, 0, W, H, fill=(4, 4, 4), a=inside)
    # A-L-I-V-E: one letter after another deep inside the mouth, the camera flies through them
    for i, ch in enumerate('ALIVE'):
        ti = tA + 0.12 * i
        zi = 200 + 260 * i
        d = zi - camz
        if t < ti or d < 120 or d > 700:
            continue
        a = eo(prog(t, ti, ti + 0.12)) * clamp((d - 120) / 260) * clamp((700 - d) / 160) * (1 - prog(t, tE - 0.12, tE - 0.02))
        word3(g, cam, ch, (0, 60, zi), (1, 0, 0), (0, -1, 0), 170, 220, GOLD, al=a, x=True, depth=30, n=4)
    hl = {'chatgpt,': GOLD, 'eat': GOLD}
    if t < tA:
        lyric3x(g, cam, t, 5, (0, 560, 120), (1, 0, 0), (0, -1, 0), 1600, 112, INK, hl, depth=60, al=1 - prog(t, tA - 0.25, tA - 0.02))
    text3(g, cam, 'MODEL.MOUTH  OPEN %3.0f%%' % (op * 100), (-560, -480, 150), 22, GOLD, 'mono', 1 - inside - wide * 0.6)
    g.hud = dict(a=1 - inside)
    g.post = dict(vig=0.9 + 0.8 * inside, glow=0.6 * (1 - inside) + 0.2)


# ======================================================== 2D TYPOGRAPHY CHORUS
def type_scene(li, k_style=0):
    def fn(g, t, lt):
        words = LINE_WORDS[li]
        k = -1
        for i, (w, tt, te) in enumerate(words):
            if t >= tt - 0.03:
                k = i
        g.hud = dict(a=0.6, minimal=True)
        if k < 0:
            return
        w, tt, te = words[k]
        s = w.upper().strip(',')
        pd = 'P(DOOM)' in s
        if pd:
            g.rect(0, 0, W, H, fill=GOLD)
            g.hud = dict(a=0)
        e = clamp((t - tt + 0.03) / 0.14)
        size = fit_size(g, s, 1720, 700, 'sans')
        hgt = size * 0.75
        if hgt > 760:
            size = size * 760 / hgt
        sc = lerp(1.18, 1.0, eo(e))
        col = BG if pd else (GOLD if k == 1 and k_style else INK)
        g.text(s, W / 2, H / 2 + 20, size, col, 'sans', 1.0, 'mm', sx=sc)
        # flat accents
        ac = BG if pd else GOLD
        g.rect(W / 2 - 860, H - 150, W / 2 - 860 + 1720 * (k + 1) / len(words), H - 144, fill=ac)
        g.text('%02d / %02d' % (k + 1, len(words)), W / 2 - 860, H - 120, 22, BG if pd else DIM, 'mono', 1, 'lm')
        g.text('P(DOOM) ' + pd_str(t), W / 2 + 860, H - 120, 22, BG if pd else GOLD, 'mono', 1, 'rm')
        g.post = dict(glow=0.3 if pd else 0.5)
    fn.li = li
    return fn


# ======================================================== FOOM 24.4 - 26.5
def s_foom(g, t, lt):
    t0 = T0(7); tf = WT(7, 4); tE = T0(8)
    boom = t > tf - 0.02
    e = max(0.0, t - tf)

    def curve(u):
        x = -2000 + 4000 * u
        y = 300 - 40 * math.exp(u * 4.2)
        return (x, y, 0)
    gu = prog(t, t0, tf) * 0.86 + (0.14 * eo(clamp(e / 0.3)) if boom else 0)
    head = curve(gu)
    # one continuous shot: the camera keeps tracking the capability head and
    # only eases back a little on FOOM (no swing to a new angle)
    ee = eo(clamp(e / 0.6)) if boom else 0.0
    eye = (head[0] - 900 - 200 * ee, head[1] - 160 - 120 * ee, -900 - 700 * ee)
    look = (head[0] + 200 - 150 * ee, head[1] - 60 - 140 * ee, 0)
    cam = Cam3(shake_eye(eye, t, 18 * math.exp(-e * 5)) if boom else eye, look, 58 + 4 * ee, -0.05)
    env(g, cam)
    # timeline axis with year ticks
    seg3(g, cam, (-2600, 320, 0), (2600, 320, 0), GRID2, 3, 1)
    for k in range(14):
        x = -2400 + k * 380
        seg3(g, cam, (x, 300, 0), (x, 340, 0), GRID2, 2, 1)
        text3(g, cam, str(2020 + k), (x, 380, 0), 26, GOLD if k == 10 else DIM, 'mono')
    # exponential ribbon
    pts = [curve(gu * q / 80) for q in range(81)]
    for d in (0, 40, 80):
        poly3(g, cam, [(p[0], p[1], p[2] + d) for p in pts], GOLD if d == 0 else GOLDD, 5 if d == 0 else 2, 1)
    point3(g, cam, head, 16, GOLDL, 1)
    text3(g, cam, 'CAPABILITY', (head[0], head[1] - 90, 0), 30, GOLD, 'mono')
    if boom:
        for (dx, dy, dz, sp) in EXPL:
            d = 2200 * sp * eo(clamp(e / 1.0))
            point3(g, cam, (head[0] + dx * d, head[1] + dy * d, dz * d), 5, GOLD if sp > 1.0 else INK, clamp(1.3 - e * 1.4))
        for k in range(3):
            R_ = e * 3800 - k * 300
            if R_ > 0:
                poly3(g, cam, [(head[0] + R_ * math.cos(a), head[1], R_ * math.sin(a)) for a in [2 * math.pi * q / 64 for q in range(65)]], GOLD, 4, clamp(1 - e * 1.5))
        g.flash = 0.16 * math.exp(-e * 10); g.flash_c = GOLDL
        word3(g, cam, 'FOOM', (head[0], head[1] - 300, 0), (1, 0, 0), (0, -1, 0), 1400 * eback(clamp(e / 0.25)), 300, GOLD, 'sans', 1, x=True, depth=120, n=8)
    c, r, u = ahead(cam, 1000)
    # v38: FOOM is left out of the caption (the big 3D FOOM already says it)
    _full = LINE_WORDS[7]
    LINE_WORDS[7] = _full[:-1]
    try:
        lyric3x(g, cam, t, 7, v_add(c, v_mul(cam.u, 330)), r, u, 1700, 115, INK, {'future': GOLD}, depth=60)
    finally:
        LINE_WORDS[7] = _full


EXPL = [(math.cos(2 * math.pi * hsh(i, 1)) * math.sqrt(1 - (2 * hsh(i, 2) - 1) ** 2),
         2 * hsh(i, 2) - 1,
         math.sin(2 * math.pi * hsh(i, 1)) * math.sqrt(1 - (2 * hsh(i, 2) - 1) ** 2), 0.4 + hsh(i, 3)) for i in range(600)]


# ======================================================== CHINESE ROOM (solid, 3D)
HANZI = '\u4e2d\u6587\u623f\u95f4\u7b26\u53f7\u89c4\u5219\u7406\u89e3\u610f\u4e49\u8bed\u6cd5\u8f93\u5165\u8f93\u51fa\u673a\u5668\u601d\u60f3'
RX, RY, RZ = 1000, 520, 900
WALL = (40, 40, 37); FLOORC = (30, 29, 27); CEIL = (22, 22, 21); WOOD = (70, 64, 54)


def _panels(F, o, u, v, nu, nv, su, sv, base, stroke):
    for i in range(nu):
        for j in range(nv):
            a = v_add(o, v_add(v_mul(u, su * i), v_mul(v, sv * j)))
            F.sq([a, v_add(a, v_mul(u, su)), v_add(a, v_add(v_mul(u, su), v_mul(v, sv))), v_add(a, v_mul(v, sv))], base, stroke, 1.0, amb=0.55)


def room_shell(g, cam, trip=0.0, t=0.0):
    F = SFaces()
    _panels(F, (-RX, RY, -RZ), (1, 0, 0), (0, 0, 1), 16, 14, 2 * RX / 16, 2 * RZ / 14, FLOORC, None)
    _panels(F, (-RX, -RY, -RZ), (1, 0, 0), (0, 0, 1), 3, 3, 2 * RX / 3, 2 * RZ / 3, CEIL, None)
    _panels(F, (-RX, -RY, RZ), (1, 0, 0), (0, 1, 0), 5, 3, 2 * RX / 5, 2 * RY / 3, WALL, (54, 54, 50))
    _panels(F, (-RX, -RY, -RZ), (1, 0, 0), (0, 1, 0), 5, 3, 2 * RX / 5, 2 * RY / 3, WALL, (54, 54, 50))
    _panels(F, (-RX, -RY, -RZ), (0, 0, 1), (0, 1, 0), 4, 3, 2 * RZ / 4, 2 * RY / 3, WALL, (54, 54, 50))
    _panels(F, (RX, -RY, -RZ), (0, 0, 1), (0, 1, 0), 4, 3, 2 * RZ / 4, 2 * RY / 3, WALL, (54, 54, 50))
    F.draw(g, cam)
    # skirting + corner edges (gold trim)
    for sx in (-1, 1):
        seg3(g, cam, (sx * RX, RY - 2, -RZ), (sx * RX, RY - 2, RZ), GOLDD, 3, 1)
    seg3(g, cam, (-RX, RY - 2, RZ), (RX, RY - 2, RZ), GOLDD, 3, 1)
    # hanzi slips pinned on the walls
    for i, ch in enumerate(HANZI):
        side = i % 3
        row = (i // 3) % 2; col = (i // 6) % 4
        wob = trip * 40 * math.sin(t * 3 + i)
        if side == 0:
            c = (-RX + 3, -260 + row * 210 + wob, -620 + col * 330); r = (0, 0, 1)
        elif side == 1:
            c = (RX - 3, -260 + row * 210 + wob, 620 - col * 330); r = (0, 0, -1)
        else:
            if row == 0:
                continue
            c = (-780 + col * 520 + (i % 2) * 260, 60 + wob, RZ - 3); r = (1, 0, 0)
        up = (0, -1, 0)
        q = [v_add(c, v_add(v_mul(r, a * 70), v_mul(up, b * 80))) for a, b in ((-1, 1), (1, 1), (1, -1), (-1, -1))]
        fill3(g, cam, q, mix(BG, INK, 0.82 + 0.1 * hsh(i, 2)), 1)
        word3(g, cam, ch, c, r, up, 110, 120, INK, 'cjk', 1, light=True)
        if hsh(i, 9) < 0.3:
            point3(g, cam, v_add(c, v_mul(up, 70)), 6, GOLD, 1)
    # input slot (left wall) and output slot (right wall)
    for sx, nm in ((-1, 'INPUT \u2192'), (1, '\u2192 OUTPUT')):
        x = sx * (RX - 2)
        q = [(x, 200, -140), (x, 200, 140), (x, 235, 140), (x, 235, -140)]
        fill3(g, cam, q, BG, 1, stroke=GOLD, w=3)
        # v64: label painted flat onto the wall plane (was a floating billboard)
        rw = (0, 0, 1) if sx < 0 else (0, 0, -1)
        word3(g, cam, nm, (x - sx * 1, 170, 0), rw, (0, -1, 0), 200, 120, GOLD, 'mono', 1)


def _book(F, c, w, h, d, base):
    F.sbox(c, (w, h, d), base, (20, 20, 19), 0.8, amb=0.4)


BAG_C = (-430.0, -300.0)          # (x, z) of the spilled bag on the floor


def _shroom_spots():
    out = []
    for i in range(16):
        a = 6.283 * hsh(i, 41) ; r = 150 + 380 * hsh(i, 42)
        out.append((BAG_C[0] + r * math.cos(a), BAG_C[1] + r * 0.8 * math.sin(a), 0.6 + 0.6 * hsh(i, 43)))
    return out


SHROOMS = _shroom_spots()


def floor_shrooms(g, cam, F, t, trip):
    tb = T0(9) - 0.35
    fy = RY - 2
    gb = eo(prog(t, tb, tb + 0.9))
    if gb <= 0:
        return
    bx, bz = BAG_C
    # roots: creep out from the bag towards each shroom, then keep spreading
    for i, (sx, sz, sc) in enumerate(SHROOMS + [(bx + 700 * math.cos(k * 1.3), bz + 500 * math.sin(k * 1.3), 0) for k in range(6)]):
        st = tb + 0.3 + 0.1 * i
        L = eo(prog(t, st, st + 2.2))
        if L <= 0:
            continue
        n = 22; m = max(2, int(n * L) + 1)
        dx, dz = sx - bx, sz - bz; ln = math.hypot(dx, dz) + 1e-6; px, pz = -dz / ln, dx / ln
        pts = []
        for k in range(m):
            u = min(k / n, L)
            w = 40 * math.sin(u * 7 + i) * math.sin(u * 3.14)
            pts.append((bx + dx * u + px * w, fy, bz + dz * u + pz * w))
        poly3(g, cam, pts, GOLDD, 2.6, 0.9)
        if len(pts) > 6:     # side shoots
            for j in (len(pts) // 3, 2 * len(pts) // 3):
                p = pts[j]; a = hsh(i, j) * 6.283; sl = 90 * L
                q = [p, (p[0] + sl * 0.5 * math.cos(a), fy, p[2] + sl * 0.5 * math.sin(a)), (p[0] + sl * math.cos(a + 0.4), fy, p[2] + sl * math.sin(a + 0.4))]
                poly3(g, cam, q, GOLDD, 1.6, 0.7)
        point3(g, cam, pts[-1], 5, GOLD, 0.9 * (L < 1))
    # cardboard box rising out of the floor, its four flaps folding open
    BW, BD = 200.0, 160.0
    h = 140 * gb
    top = RY - h
    x0, x1, z0, z1 = bx - BW / 2, bx + BW / 2, bz - BD / 2, bz + BD / 2
    CB = (150, 140, 120); EDGE = (90, 84, 70); IN = (52, 47, 40)
    F.sq([(x0, top, z0), (x1, top, z0), (x1, RY, z0), (x0, RY, z0)], CB, EDGE, 1.0, amb=0.45)
    F.sq([(x1, top, z1), (x0, top, z1), (x0, RY, z1), (x1, RY, z1)], CB, EDGE, 1.0, amb=0.45)
    F.sq([(x0, top, z1), (x0, top, z0), (x0, RY, z0), (x0, RY, z1)], CB, EDGE, 1.0, amb=0.45)
    F.sq([(x1, top, z0), (x1, top, z1), (x1, RY, z1), (x1, RY, z0)], CB, EDGE, 1.0, amb=0.45)
    e = 5.0      # dark inside walls + floor, seen through the open top
    F.sq([(x0 + e, top, z0 + e), (x1 - e, top, z0 + e), (x1 - e, RY - 2, z0 + e), (x0 + e, RY - 2, z0 + e)], IN, None, amb=0.6)
    F.sq([(x0 + e, top, z1 - e), (x1 - e, top, z1 - e), (x1 - e, RY - 2, z1 - e), (x0 + e, RY - 2, z1 - e)], IN, None, amb=0.6)
    F.sq([(x0 + e, top, z0 + e), (x0 + e, top, z1 - e), (x0 + e, RY - 2, z1 - e), (x0 + e, RY - 2, z0 + e)], IN, None, amb=0.6)
    F.sq([(x1 - e, top, z0 + e), (x1 - e, top, z1 - e), (x1 - e, RY - 2, z1 - e), (x1 - e, RY - 2, z0 + e)], IN, None, amb=0.6)
    F.sq([(x0 + e, RY - 3, z0 + e), (x1 - e, RY - 3, z0 + e), (x1 - e, RY - 3, z1 - e), (x0 + e, RY - 3, z1 - e)], (30, 28, 24), None, amb=0.8)
    # flaps hinged on the four top edges: closed (lying flat over the top) -> folded out and tilted down
    fl = eo(prog(t, tb + 0.4, tb + 1.3))
    th = fl * 2.25 + 0.05 * math.sin(t * 3)
    up = (0.0, -1.0, 0.0)
    flaps = [((x0, top, z0), (x1, top, z0), (0, 0, 1), BD / 2 - 2),     # front edge, folds over +z when closed
             ((x1, top, z1), (x0, top, z1), (0, 0, -1), BD / 2 - 2),
             ((x0, top, z1), (x0, top, z0), (1, 0, 0), BD / 2 - 12),
             ((x1, top, z0), (x1, top, z1), (-1, 0, 0), BD / 2 - 12)]
    for k, (h0, h1, din, L) in enumerate(flaps):
        tk = th * (0.92 + 0.08 * k / 3)
        d = v_add(v_mul(din, math.cos(tk) * L), v_mul(up, math.sin(tk) * L))
        F.sq([h0, h1, v_add(h1, d), v_add(h0, d)], CB, EDGE, 1.0, amb=0.45)
    # shrooms packed inside the box, pushing up out of the open top
    for k in range(6):
        gk = eo(prog(t, tb + 0.8 + 0.12 * k, tb + 1.5 + 0.12 * k))
        if gk <= 0:
            continue
        ix = bx + (-60 + 60 * (k % 3)) + 14 * (hsh(k, 51) - 0.5)
        iz = bz + (-35 if k < 3 else 35) + 10 * (hsh(k, 52) - 0.5)
        sc = (0.75 + 0.35 * hsh(k, 53)) * gk
        stem = 40 + 60 * gk
        sh = stem - 40          # v41: stem only above the rim, so nothing inside the box shows through its walls
        if sh > 2:
            F.cyl((ix, top - sh / 2, iz), 13 * sc, sh, INK, None, 8)
        pul = 1 + trip * 0.15 * math.sin(t * 6 + k * 2)
        F.sphere((ix, top - stem + 40, iz), 50 * sc * pul, GOLD, None, 4, 10, lat0=0.0, lat1=0.5, sy=0.75, amb=0.35)
    # shrooms sprout one after another, scattered on the floor
    for i, (sx, sz, sc) in enumerate(SHROOMS):
        ti = T0(9) + 0.1 + 0.13 * i
        gr = eo(prog(t, ti, ti + 0.6))
        if gr <= 0:
            continue
        s = sc * gr
        pul = 1 + trip * 0.15 * math.sin(t * 6 + i)
        F.cyl((sx, RY - 30 * s, sz), 16 * s, 60 * s, INK, None, 8)
        F.sphere((sx, RY - 60 * s, sz), 58 * s * pul, GOLD, None, 4, 10, lat0=0.0, lat1=0.5, sy=0.75, amb=0.35)


def room_contents(g, cam, t, trip=0.0, show_bag=False):
    F = SFaces()
    if show_bag:
        floor_shrooms(g, cam, F, t, trip)
    # desk
    F.sbox_t((0, 300, 200), (900, 34, 420), WOOD, 60.0)
    for lx in (-1, 1):
        for lz in (-1, 1):
            F.sbox((lx * 410, 415, 200 + lz * 180), (28, 196, 28), WOOD, None)
    # v86: overhauled operator - a seated person (hair, face, ears, collared shirt, trousers, shoes) on an office
    # chair, leaning over the rulebook, left hand fetching cards, right hand writing with a gold pen
    SKIN = (196, 186, 170); SHIRT = (150, 148, 140); PANTS = (62, 62, 60); HAIR = (34, 32, 30); CH = (48, 48, 46)
    F.sbox((330, 365, 200), (200, 130, 380), WOOD, (50, 46, 40), 1.0, amb=0.4)          # drawer block
    for dy in (330, 395):
        F.sbox((330, dy, -2), (90, 10, 8), GOLDD, None, amb=0.8)
    # trays: incoming (left) and outgoing (right) card stacks
    for tx, n in ((-370, 5), (300, 3)):
        F.sbox((tx, 276, 60), (130, 12, 100), (44, 44, 42), GOLDD, 0.8, amb=0.4)
        for k in range(n):
            F.sbox((tx + 3 * math.sin(k * 2.1), 268 - k * 4, 60 + 2 * math.cos(k)), (110, 3, 80), INK if k % 2 else (210, 208, 200), None, amb=0.7)
    # chair: five-star base, gas column, seat, backrest, armrests
    for k in range(5):
        an = k * 1.2566 + 0.3
        F.tube([(0, 500, 590), (140 * math.cos(an), 505, 590 + 140 * math.sin(an))], 10, CH, None, 5)
        F.sphere((140 * math.cos(an), 510, 590 + 140 * math.sin(an)), 14, (30, 30, 29), None, 3, 6)
    F.cyl((0, 445, 590), 16, 110, (90, 90, 86), None, 8)
    F.sbox((0, 380, 590), (250, 32, 240), CH, (66, 66, 62), 1.0, amb=0.35)
    F.sbox((0, 215, 715), (240, 290, 34), CH, (66, 66, 62), 1.0, amb=0.35)
    F.tube([(0, 380, 700), (0, 350, 718), (0, 330, 715)], 12, (80, 80, 76), None, 5)
    for sx in (-1, 1):
        F.tube([(sx * 130, 370, 650), (sx * 130, 300, 650), (sx * 130, 300, 540)], 9, (80, 80, 76), None, 5)
    bob = math.sin(t * 2.0) * 6
    head_tilt = trip * 0.35 * math.sin(t * 2.5)
    # legs: thighs forward under the desk, shins down, shoes
    for sx in (-1, 1):
        hip = (sx * 62, 350, 600); kn = (sx * 72, 340, 410); ft = (sx * 80, 490, 380)
        F.tube([hip, v_lerp(hip, kn, 0.5), kn], 46, PANTS, None, 8, rs=[52, 46, 42], amb=0.3)
        F.tube([kn, v_lerp(kn, ft, 0.5), ft], 38, PANTS, None, 8, rs=[42, 36, 32], amb=0.3)
        F.sbox((sx * 80, 505, 350), (70, 32, 130), (26, 26, 25), None, amb=0.4)
    # torso: pelvis -> chest -> neck, leaning toward the desk
    pel = (0, 345, 600); che = (0, 170 + bob, 565); nek = (0, 60 + bob, 540)
    F.tube([pel, v_lerp(pel, che, 0.5), che, nek], 95, SHIRT, None, 10, rs=[92, 100, 108, 70], amb=0.3)
    F.tube([pel, (0, 355, 600)], 96, PANTS, None, 10, amb=0.3)                              # belt line
    F.sbox((0, 352, 512), (60, 16, 8), GOLDD, None, amb=0.8)                                 # buckle
    for sx in (-1, 1):                                                                         # collar points
        F.sq([(sx * 8, 62 + bob, 478), (sx * 52, 58 + bob, 492), (sx * 30, 96 + bob, 478)], (200, 198, 190), None, amb=0.5)
    F.cyl((0, 30 + bob, 535), 34, 60, SKIN, None, 8, amb=0.35)
    # head looking down at the rulebook
    hp = (40 * head_tilt, -40 + bob, 520)
    F.sphere(hp, 78, SKIN, None, 8, 14, sy=1.12, amb=0.35)
    F.sphere(v_add(hp, (0, -8, 8)), 84, HAIR, None, 6, 14, sy=1.08, lat0=0.0, lat1=0.45, amb=0.3)
    F.sphere(v_add(hp, (0, 10, 34)), 66, HAIR, None, 6, 12, sy=1.15, amb=0.3)
    for sx in (-1, 1):
        F.sphere(v_add(hp, (sx * 78, 6, 8)), 16, SKIN, None, 3, 6, sy=1.4, amb=0.35)          # ears
        F.sphere(v_add(hp, (sx * 28, 4, -70)), 8, (24, 24, 23), None, 3, 6, amb=0.6)          # eyes
        F.sbox(v_add(hp, (sx * 28, -14, -72)), (32, 6, 6), HAIR, None, amb=0.5)               # brows
    F.tube([v_add(hp, (0, 0, -76)), v_add(hp, (0, 22, -90))], 9, SKIN, None, 5, amb=0.4)    # nose
    F.sbox(v_add(hp, (0, 42, -70)), (30, 5, 6), (120, 90, 80), None, amb=0.5)                 # mouth
    # arms: left reaches for incoming cards / turns pages, right writes with a pen
    ph = (t * 0.75) % 1.0
    lh = (-150 - 120 * math.sin(ph * math.pi) if ph < 0.5 else -160, 262, 330 + 60 * math.sin(ph * 6))
    rh = (150 + 30 * math.sin(t * 7), 264, 300 + 20 * math.sin(t * 9))
    for sx, hd in ((-1, lh), (1, rh)):
        sh = (sx * 118, 90 + bob, 560)
        el = (sx * 175, 250, 470)
        F.sphere(sh, 46, SHIRT, None, 4, 8, amb=0.3)
        F.tube([sh, el], 38, SHIRT, None, 8, rs=[42, 34], amb=0.3)
        F.tube([el, v_lerp(el, hd, 0.75)], 32, SHIRT, None, 8, rs=[34, 28], amb=0.3)
        F.tube([v_lerp(el, hd, 0.75), hd], 22, SKIN, None, 6, rs=[24, 20], amb=0.35)
        F.sbox(v_add(hd, (0, 4, -18)), (50, 16, 46), SKIN, None, amb=0.35)                    # palm
        for k in range(4):
            fx = -18 + k * 12
            F.tube([v_add(hd, (fx, 6, -40)), v_add(hd, (fx, 14, -62))], 5, SKIN, None, 4)
        F.tube([v_add(hd, (sx * -24, 4, -14)), v_add(hd, (sx * -36, 10, -38))], 6, SKIN, None, 4)  # thumb
    F.tube([v_add(rh, (6, -6, -50)), v_add(rh, (34, 14, -96))], 5, GOLD, None, 5, amb=0.8)   # pen
    # rulebook on the desk, open, pages flipping
    F.sbox_t((-40, 278, 300), (420, 14, 280), (36, 36, 34), 50.0)
    for sx in (-1, 1):
        F.sq([(-40, 270, 170), (-40 + sx * 200, 266, 170), (-40 + sx * 200, 266, 430), (-40, 270, 430)], INK, None, amb=0.6)
    fa = math.pi * ((t * 1.6) % 1.0)
    fx = 200 * math.cos(fa); fy = -200 * math.sin(fa) * 0.6
    F.sq([(-40, 268, 175), (-40 + fx, 268 + fy, 175), (-40 + fx, 268 + fy, 425), (-40, 268, 425)], (220, 218, 210), None, amb=0.6)
    # bookshelves of rulebooks on the back wall; books slide in and out at random
    for row in range(3):
        y = -110 + row * 190
        F.sbox_t((0, y + 80, RZ - 80), (1700, 16, 150), WOOD, 70.0)
        for k in range(26):
            hgt = 120 + hsh(k, row) * 40
            fr = 5.0 + 7.0 * hsh(k, row + 11); ph = 6.283 * hsh(k, row + 13)
            mv = 0.5 + 0.5 * math.sin(t * fr + ph) * math.sin(t * fr * 0.37 + ph * 1.7)
            dz = -70 * mv * (0.4 + 0.6 * hsh(k, row + 15))
            F.sbox((-820 + k * 64 + hsh(k, row + 3) * 8, y + 72 - hgt / 2, RZ - 90 + dz), (52, hgt, 120),
                   GOLD if hsh(k, row + 7) < 0.12 else (60 + 30 * hsh(k, row + 9),) * 3, None, amb=0.4)
    # lamp
    F.sphere((0, -230, 250), 110, (70, 68, 62), None, 4, 14, lat0=0.0, lat1=0.5, sy=0.7)
    seg3(g, cam, (0, -RY, 250), (0, -300, 250), GRID2, 2, 1)
    F.draw(g, cam)
    # light cone
    for k in range(3):
        rr = 520 - k * 120
        poly = [cam.p((0, -235, 250))] + [cam.p((rr * math.cos(a), 285, 250 + rr * 0.6 * math.sin(a))) for a in [math.pi * q / 16 for q in range(17)]]
        if all(p is not None for p in poly):
            flat = []
            for p in poly:
                flat += [p[0], p[1]]
            g.poly(flat, fill=GOLDL, a=0.0, fa=0.035 + trip * 0.02)
    # the card: in through the input slot, across the desk, out through the output slot
    cu = (t * 0.7) % 1.0
    SY = 217.0
    if cu < 0.15:
        u = cu / 0.15; x = lerp(-RX - 200, -RX + 140, u); y = SY; z = 0.0
    elif cu < 0.4:
        u = eio((cu - 0.15) / 0.25); x = lerp(-RX + 140, -260, u); y = lerp(SY, 282, u); z = lerp(0, 185, u)
    elif cu < 0.65:
        x = lerp(-260, 200, (cu - 0.4) / 0.25); y = 282; z = 185.0
    elif cu < 0.85:
        u = eio((cu - 0.65) / 0.2); x = lerp(200, RX - 140, u); y = lerp(282, SY, u); z = lerp(185, 0, u)
    else:
        u = (cu - 0.85) / 0.15; x = lerp(RX - 140, RX + 200, u); y = SY; z = 0.0
    x0 = max(x - 90, -RX + 1); x1 = min(x + 90, RX - 1)
    if x1 > x0:
        q = [(x0, y, z - 65), (x1, y, z - 65), (x1, y, z + 65), (x0, y, z + 65)]
        fill3(g, cam, q, INK, 1, stroke=GOLD, w=2)
        if abs(x) < RX - 90:
            word3(g, cam, HANZI[int(t * 0.7) % len(HANZI)] + HANZI[(int(t * 0.7) + 5) % len(HANZI)], (x, y - 2, z), (1, 0, 0), (0, 0, 1), 140, 100, INK, 'cjk', 1, light=True)
    text3(g, cam, 'RULEBOOK v\u221e', (-40, 220, 300), 22, GOLD, 'mono')
    text3(g, cam, 'OPERATOR: UNDERSTANDS 0%', (0, -175, 540), 22, DIM, 'mono')


def _seg_hits_box(a, b, lo, hi):
    t0, t1 = 0.0, 1.0
    for k in range(3):
        d = b[k] - a[k]
        if abs(d) < 1e-9:
            if a[k] < lo[k] or a[k] > hi[k]:
                return False
            continue
        u0, u1 = (lo[k] - a[k]) / d, (hi[k] - a[k]) / d
        if u0 > u1:
            u0, u1 = u1, u0
        t0, t1 = max(t0, u0), min(t1, u1)
        if t0 > t1:
            return False
    return True


def s_room(g, t, lt):
    """'Trapped in the Chinese room' + 'with a bag of shrooms' as one continuous shot"""
    t8 = T0(8); t9 = T0(9); t10 = T0(10)
    trip = prog(t, WT(9, 2), WT(9, 4) + 0.3)
    keys = [(t8, (-900, -440, -860), (0, 150, 300), 84, 0.02),
            (t9, (-600, -400, -850), (-180, 260, 60), 80, -0.01),
            (t9 + 0.9, (-160, -260, -820), (-380, 440, -200), 74, 0.03),
            (t10 - 0.4, (-150, 0, -820), (-330, 520, -380), 70, -0.06),
            (t10 + 0.6, (-200, 380, -720), (-260, 520, -440), 62, 0.10)]
    cam = cam_at(t, keys, shake=4, roll_add=0.05 * trip * math.sin(t * 2.4))
    room_shell(g, cam, trip, t)
    room_contents(g, cam, t, trip, show_bag=True)
    gb = eo(prog(t, T0(9) - 0.35, T0(9) + 0.55))
    bmin = (BAG_C[0] - 100, RY - 140 * gb, BAG_C[1] - 80); bmax = (BAG_C[0] + 100, RY, BAG_C[1] + 80)
    for i in range(80):
        p = (BAG_C[0] + (hsh(i, 1) - 0.5) * 900, RY - ((t * 60 + i * 37) % 600), BAG_C[1] + (hsh(i, 3) - 0.5) * 700)
        if gb > 0 and _seg_hits_box(cam.eye, p, bmin, bmax):
            continue          # v41: spores hidden behind (or inside) the box
        point3(g, cam, p, 3, GOLD if i % 3 else INK, 0.7 * trip)
    c, r, u = ahead(cam, 900)
    # v42: line 8 rides with the camera like line 9 (it was on the back wall, so it slid as the camera moved)
    lyric3x(g, cam, t, 8, v_add(c, v_mul(cam.u, -300)), r, u, 1500, 120, INK, {'chinese': GOLD, 'room,': GOLD}, depth=40, n=4)
    lyric3x(g, cam, t, 9, v_add(c, v_mul(cam.u, -280)), r, u, 1500, 115, INK, {'bag': GOLD, 'shrooms': GOLD}, depth=40, n=4)
    g.late = lambda: mask_slide_in(g, t)
    g.post = dict(vig=1.15, glow=0.6 + 0.3 * trip)


# ======================================================== SHINIGAMI EYES 33.5 - 38.6
def _basis(f):
    f = v_norm(f)
    ref = (0, 1, 0) if abs(f[1]) < 0.9 else (1, 0, 0)
    r = v_norm(v_cross(ref, f)); u = v_cross(f, r)
    return f, r, u


def _sp(c, R, f, r, u, th, ph):
    return v_add(c, v_add(v_mul(f, R * math.cos(th)), v_mul(v_add(v_mul(r, math.cos(ph)), v_mul(u, math.sin(ph))), R * math.sin(th))))


def s_shinigami(g, t, lt):
    t0 = T0(11); te = WT(11, 3); tE = T0(12)
    keys = [(t0, (0, -100, -2600), (0, -80, 0), 52, 0.0),
            (te, (-260, -60, -1300), (0, -80, 0), 55, 0.04),
            (35.8, (0, -80, -900), (0, -80, 0), 60, 0.0),
            (37.4, orbit((0, -80, 0), 1800, 0.9, 0.3), (0, -80, 0), 55, -0.06),
            (tE, orbit((0, -80, 0), 2600, 1.5, 0.45), (0, -80, 0), 52, 0.0)]
    cam = cam_at(t, keys, shake=10 * prog(t, 35.6, 36.2))
    env(g, cam)
    # dark tentacle mass framing the eyes
    for i in range(0, len(TENT), 2):
        pts = [_tent(i, t, k) for k in range(25)]
        pts = [(p[0] * 1.3, p[1] * 1.1, p[2] + 600) for p in pts]
        poly3(g, cam, pts, GRID2, 3, 0.8)
    word3(g, cam, '\u6b7b\u795e', (0, -80, 900), (1, 0, 0), (0, -1, 0), 1900, 300, GOLD, 'cjk', 0.35, x=True, depth=120, n=5)
    op = eo(prog(t, t0, t0 + 0.5))
    for sx in (-1, 1):
        c = (sx * 330, -80, 0)
        gz = math.atan2(cam.eye[0] - c[0], -(cam.eye[2] - c[2])) * 0.8
        gy = -math.atan2(cam.eye[1] - c[1], -(cam.eye[2] - c[2])) * 0.8
        F = SFaces()
        F.sphere(c, 230, (46, 46, 43), None, 10, 20, amb=0.3)
        F.draw(g, cam)
        look = v_norm(v_sub(cam.eye, c))
        f, r_, u_ = _basis(v_add(look, (0.15 * math.sin(t * 1.3 + sx), 0.1 * math.cos(t * 1.7), 0)))
        I = SFaces()
        NI = 28
        for ring in range(6):
            th0 = 0.04 + ring * 0.085; th1 = th0 + 0.085
            for j in range(NI):
                p0 = 2 * math.pi * j / NI; p1 = 2 * math.pi * (j + 1) / NI
                q = [_sp(c, 232, f, r_, u_, th, ph) for th, ph in ((th0, p0), (th0, p1), (th1, p1), (th1, p0))]
                col = GOLDL if (j + int(t * 8)) % 9 == ring else GOLD
                I.sq(q, mix(GOLDD, col, 0.35 + 0.65 * (1 - ring / 6)), None, amb=0.6)
        I.draw(g, cam)
        sw = 0.06 + 0.05 * pulse(t, 1, 6)
        slit = [_sp(c, 234, f, r_, u_, abs(v) * 0.42 + 0.001, (math.pi / 2 if v > 0 else -math.pi / 2)) for v in [(q / 20 - 0.5) * 2 for q in range(21)]]
        slit = [v_add(p, v_mul(r_, 230 * sw * (1 - ((q / 20 - 0.5) * 2) ** 2))) for q, p in enumerate(slit)] + \
               [v_add(p, v_mul(r_, -230 * sw * (1 - ((q / 20 - 0.5) * 2) ** 2))) for q, p in reversed(list(enumerate(slit)))]
        fill3(g, cam, slit, BG, 1)
        rot = lambda p: v_add(c, v_mul(f, 240))
        # glow halo
        point3(g, cam, rot(0), 40 * op * (1 + 0.3 * pulse(t, 1, 5)), GOLDL, 0.25)
        # eyelid shells
        L = SFaces()
        lid = op if t < 35.65 else (1 - 0.5 * pulse(t, 2, 4))
        L.sphere(c, 245, (24, 24, 23), (60, 60, 56), 4, 18, lat0=0.0, lat1=lerp(0.5, 0.3, lid), w=0.8)
        L.sphere(c, 245, (24, 24, 23), (60, 60, 56), 3, 18, lat0=lerp(0.5, 0.72, lid), lat1=1.0, w=0.8)
        L.draw(g, cam)
    if t > 35.6:
        u = prog(t, 35.6, tE)
        for k in range(int(4 + u * 22)):
            R = 1200 + k * 70
            yy = 700 - ((t * 400 + k * 90) % 1400)
            pts = [(R * math.cos(a), yy, R * math.sin(a)) for a in [2 * math.pi * q / 60 for q in range(61)]]
            poly3(g, cam, pts, GOLD if k % 4 == 0 else GRID2, 1.6, 0.35 + 0.4 * u)
    lyric3x(g, cam, t, 11, (0, 360, -300), (1, 0, 0), (0, -1, 0), 1800, 120, INK, {'shinigami': GOLD, 'eyes': GOLD}, depth=60)
    g.post = dict(glow=0.75)



# ======================================================== SHOGGOTH + SHINIGAMI EYES 30.1 - 38.6 (one scene)
SH_C = (0.0, 0.0, 200.0)
EYE_POS = [(-175.0, -70.0, -95.0), (175.0, -70.0, -95.0)]


def _eye_basis(c, cam, k=0.75):
    tgt = v_lerp(v_add(c, (0, 0, -1000)), cam.eye, k)
    r, u = facing(c, tgt)
    f = v_norm(v_sub(tgt, c))
    return r, u, f


def _shini_eye(g, cam, t, c, R, e, wide, blinkv, j):
    r, u, f = _eye_basis(c, cam)
    P = lambda x, y, z=0.0: v_add(c, v_add(v_mul(r, x), v_add(v_mul(u, y), v_mul(f, z))))
    # glow + solid dark eyeball
    point3(g, cam, c, R * 2.2 * e, GOLD, 0.10 * e)
    B = SFaces()
    B.sphere(c, R * e, (34, 31, 24), None, 10, 18, amb=0.4)
    B.draw(g, cam)
    # dotted shell (same point language as the shoggoth body)
    for i in range(90):
        th = hsh(i + 50 * j, 5) * 2 * math.pi; ph = math.acos(2 * hsh(i + 50 * j, 6) - 1)
        p = v_add(c, (R * 1.04 * e * math.sin(ph) * math.cos(th), R * 1.04 * e * math.cos(ph), R * 1.04 * e * math.sin(ph) * math.sin(th)))
        if v_dot(v_sub(p, c), v_sub(cam.eye, p)) > 0:
            point3(g, cam, p, 2.4, INK, 0.55)
    op = e * (1 - blinkv)
    ri = R * 0.78 * e
    ring = lambda rad, z=-R * e * 0.98, n=48, sy=1.0: [P(rad * math.cos(2 * math.pi * q / n), rad * math.sin(2 * math.pi * q / n) * sy, -z) for q in range(n)]
    zf = R * e * 0.98
    sy = max(0.02, op)
    fill3(g, cam, [P(ri * math.cos(2 * math.pi * q / 48), ri * math.sin(2 * math.pi * q / 48) * sy, zf) for q in range(48)], (70, 50, 12), 1.0)
    fill3(g, cam, [P(ri * 0.82 * math.cos(2 * math.pi * q / 48), ri * 0.82 * math.sin(2 * math.pi * q / 48) * sy, zf + 1) for q in range(48)], GOLDD, 1.0)
    fill3(g, cam, [P(ri * 0.55 * math.cos(2 * math.pi * q / 40), ri * 0.55 * math.sin(2 * math.pi * q / 40) * sy, zf + 2) for q in range(40)], GOLD, 1.0)
    # radial fibres
    for i in range(64):
        a = 2 * math.pi * i / 64 + hsh(i, 9) * 0.05
        bend = (hsh(i, 8) - 0.5) * 0.4
        pts = [P(lerp(ri * 0.2, ri * 0.98, q / 5) * math.cos(a + bend * math.sin(q / 5 * math.pi)),
                 lerp(ri * 0.2, ri * 0.98, q / 5) * math.sin(a + bend * math.sin(q / 5 * math.pi)) * sy, zf + 3) for q in range(6)]
        poly3(g, cam, pts, GOLDL if hsh(i, 7) > 0.6 else GOLD, 1.6, 0.85)
    # rotating rune ring
    for k in range(12):
        a0 = 2 * math.pi * k / 12 + t * (0.6 if j else -0.6)
        pts = [P(ri * 0.7 * math.cos(a0 + 0.35 * q / 6), ri * 0.7 * math.sin(a0 + 0.35 * q / 6) * sy, zf + 4) for q in range(7)]
        poly3(g, cam, pts, BG, 3.0, 0.8)
    # vertical slit pupil (dilates on "eyes")
    pw = ri * (0.12 + 0.22 * wide); ph_ = ri * 0.78
    fill3(g, cam, [P(pw * math.cos(2 * math.pi * q / 32), ph_ * math.sin(2 * math.pi * q / 32) * sy, zf + 5) for q in range(32)], (6, 6, 6), 1.0, stroke=GOLDL, w=2)
    poly3(g, cam, [P(ri * math.cos(2 * math.pi * q / 64), ri * math.sin(2 * math.pi * q / 64) * sy, zf + 3) for q in range(65)], (16, 12, 6), 5, 1)
    # tentacle lids: bundles of dotted curves that part open and trail off into tentacles
    lids = []
    for side in (1, -1):
        for b in range(3):
            gap = (R * 0.86 * op + b * 16) * side
            pts = []
            for q in range(25):
                x = lerp(-R * 2.4, R * 2.4, q / 24)
                inside = max(0.0, 1 - (x / (R * 1.05)) ** 2)
                y = gap * math.sqrt(inside) + side * (b * 10) + math.sin(t * 2.4 + q * 0.5 + b + j * 3) * 12 * (1 - inside)
                zz = zf + 8 + 30 * inside - (abs(x) - R) * 0.35 * (abs(x) > R)
                pts.append(P(x * (1 + 0.04 * b), y, zz))
            lids.append(pts)
            poly3(g, cam, pts, GRID2 if b else INK, 3.0 - b * 0.6, 0.95)
            for q in range(0, 25, 2):
                point3(g, cam, pts[q], (7 - b * 1.5) * (0.6 + 0.4 * math.sin(math.pi * q / 24)), GOLD if (q + b) % 6 == 0 else INK, 0.85)
    return P, ri, zf


SHINI_LIDS = [True]


class _ClipG:
    """v47: proxy canvas that clips everything to a convex screen polygon (the almond opening)"""
    def __init__(self, g, P):
        self.g = g
        ar = sum(P[i][0] * P[(i + 1) % len(P)][1] - P[(i + 1) % len(P)][0] * P[i][1] for i in range(len(P)))
        self.P = P if ar > 0 else P[::-1]
        self.ok = abs(ar) > 20

    def _in(self, p, a, b):
        return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) >= 0

    def _x(self, p, q, a, b):
        dx, dy = q[0] - p[0], q[1] - p[1]
        ex, ey = b[0] - a[0], b[1] - a[1]
        den = ex * dy - ey * dx
        if abs(den) < 1e-9:
            return p
        u = -(ex * (p[1] - a[1]) - ey * (p[0] - a[0])) / den
        return (p[0] + dx * u, p[1] + dy * u)

    def clip_poly(self, pts):
        out = pts
        n = len(self.P)
        for i in range(n):
            a, b = self.P[i], self.P[(i + 1) % n]
            inp, out = out, []
            if not inp:
                break
            s_ = inp[-1]
            for e_ in inp:
                if self._in(e_, a, b):
                    if not self._in(s_, a, b):
                        out.append(self._x(s_, e_, a, b))
                    out.append(e_)
                elif self._in(s_, a, b):
                    out.append(self._x(s_, e_, a, b))
                s_ = e_
        return out

    def clip_seg(self, p, q):
        t0, t1 = 0.0, 1.0
        n = len(self.P)
        for i in range(n):
            a, b = self.P[i], self.P[(i + 1) % n]
            fp = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
            fq = (b[0] - a[0]) * (q[1] - a[1]) - (b[1] - a[1]) * (q[0] - a[0])
            if fp < 0 and fq < 0:
                return None
            if fp < 0:
                t0 = max(t0, fp / (fp - fq))
            elif fq < 0:
                t1 = min(t1, fp / (fp - fq))
        if t0 >= t1:
            return None
        L = lambda u: (p[0] + (q[0] - p[0]) * u, p[1] + (q[1] - p[1]) * u)
        return L(t0), L(t1)

    def poly(self, pts, fill=None, stroke=None, w=2, a=1.0, fa=None):
        if not self.ok:
            return
        P = [(pts[2 * k], pts[2 * k + 1]) for k in range(len(pts) // 2)]
        C = self.clip_poly(P)
        if len(C) >= 3:
            self.g.poly([v for p in C for v in p], fill=fill, stroke=None, w=w, a=a, fa=fa)
        if stroke is not None:
            for k in range(len(P)):
                self.line([*P[k], *P[(k + 1) % len(P)]], c=stroke, w=w, a=a)

    def line(self, pts, c=INK, w=2, a=1.0):
        if not self.ok:
            return
        P = [(pts[2 * k], pts[2 * k + 1]) for k in range(len(pts) // 2)]
        for k in range(len(P) - 1):
            r = self.clip_seg(P[k], P[k + 1])
            if r:
                self.g.line([*r[0], *r[1]], c=c, w=w, a=a)

    def circle(self, x, y, r, fill=None, stroke=None, w=2, a=1.0, fa=None):
        if self.ok and self.clip_seg((x, y), (x, y)):
            self.g.circle(x, y, r, fill=fill, stroke=stroke, w=w, a=a, fa=fa)

    def __getattr__(self, k):
        return getattr(self.g, k)


def _shini_eye2(g, cam, t, c, R, e, wide, blinkv, j):
    """v47 shinigami eye: ONLY the gold almond rim and the iris (clipped to the almond). No grey ball,
    no lid cover, no armour plates (user, v47). The iris turns to follow the camera; the rim is fixed."""
    sz = clamp(e * 1.8)
    if sz <= 0:
        return
    Rs = R * sz
    r0, u0, f0 = _eye_basis(c, cam, k=0.0)          # fixed socket frame, facing front
    S = lambda x, y, z=0.0: v_add(c, v_add(v_mul(r0, x), v_add(v_mul(u0, y), v_mul(f0, z))))
    gd = v_norm(v_sub(cam.eye, c))
    rI, uI = facing(c, v_add(c, v_mul(gd, 1000)))
    I = lambda x, y, z: v_add(c, v_add(v_mul(rI, x), v_add(v_mul(uI, y), v_mul(gd, z))))
    # the almond opening (fixed, slanted, outer corner up)
    op = clamp((e - 0.3) / 0.7) * (1 - blinkv)
    side = -1 if j == 0 else 1
    tilt = 0.20 * side
    Rw = Rs * 1.08; zl = Rs * 1.02
    hu = Rs * 0.62 * op + 1.0; hl = Rs * 0.42 * op + 1.0
    def rot(x, y):
        return (x * math.cos(tilt) - y * math.sin(tilt), x * math.sin(tilt) + y * math.cos(tilt))
    N = 28
    xs = [lerp(-Rw, Rw, q / N) for q in range(N + 1)]
    def prof(x):
        v = max(0.0, 1 - (x / Rw) ** 2)
        return v ** (0.75 if x * side > 0 else 0.95)
    up_edge = [rot(x, hu * prof(x)) for x in xs]
    lo_edge = [rot(x, -hl * prof(x)) for x in xs]
    scr = [cam.p(S(x, y, zl)) for x, y in up_edge + lo_edge[::-1][1:-1]]
    if any(q is None for q in scr):
        return
    G = _ClipG(g, [(q[0], q[1]) for q in scr])
    # iris, drawn through the clip
    zi = Rs * 0.93
    ri = Rs * 0.64
    circ = lambda rad, z, n=48: [I(rad * math.cos(2 * math.pi * q / n), rad * math.sin(2 * math.pi * q / n), z) for q in range(n)]
    fill3(G, cam, circ(ri * 1.06, zi - 2), (20, 15, 6), 1.0)
    fill3(G, cam, circ(ri, zi), (120, 78, 10), 1.0)
    fill3(G, cam, circ(ri * 0.8, zi + 1), GOLDD, 1.0)
    fill3(G, cam, circ(ri * 0.5, zi + 2), GOLD, 1.0)
    for i in range(72):                               # iris fibres
        a = 2 * math.pi * i / 72 + hsh(i + 9 * j, 9) * 0.04
        r1 = ri * (0.22 + 0.1 * hsh(i, 4)); r2 = ri * (0.96 - 0.12 * hsh(i, 5))
        poly3(G, cam, [I(r1 * math.cos(a), r1 * math.sin(a), zi + 3), I(r2 * math.cos(a + 0.03), r2 * math.sin(a + 0.03), zi + 3)],
              GOLDL if hsh(i, 7) > 0.55 else (150, 100, 14), 1.4, 0.8)
    for k in range(16):
        a0 = 2 * math.pi * k / 16 + t * (0.5 if j else -0.5)
        poly3(G, cam, [I(ri * 0.68 * math.cos(a0 + 0.24 * q / 4), ri * 0.68 * math.sin(a0 + 0.24 * q / 4), zi + 4) for q in range(5)], (20, 15, 6), 3.2, 0.9)
    poly3(G, cam, circ(ri * 0.86, zi + 4, 64) + [circ(ri * 0.86, zi + 4, 64)[0]], (20, 15, 6), 1.6, 0.7)
    pw = ri * (0.10 + 0.20 * wide); ph_ = ri * 0.82
    fill3(G, cam, [I(pw * math.cos(2 * math.pi * q / 40) * abs(math.cos(2 * math.pi * q / 40)) ** 0.2,
                     ph_ * math.sin(2 * math.pi * q / 40), zi + 5) for q in range(40)], (5, 5, 5), 1.0, stroke=GOLDL, w=1.5)
    point3(G, cam, I(-ri * 0.32, ri * 0.38, zi + 6), 9, INK, 0.75)          # catch light
    # the gold almond rim with its studs
    for edge in (up_edge, lo_edge):
        poly3(g, cam, [S(x, y, zl + 1) for x, y in edge], GOLD, 3.2, 1.0)
        for q in range(2, N - 1, 3):
            x, y = edge[q]
            point3(g, cam, S(x, y, zl + 2), 4.5, GOLDL if q % 2 else INK, 0.9 * clamp(op * 3))
    cx_, cy_ = rot(side * Rw * 0.86, -hl * 0.4)
    poly3(g, cam, [S(cx_ + side * 3 * q, cy_ - 13 * q * sz, zl + 3) for q in range(4)], GOLD, 2.2, 0.8 * clamp(op * 2))
    return S, ri, zl


# ---- v43: room -> shoggoth: the smiley mask slides in over the room, fills the frame, then shrinks into place
_mask_late = [None]
SH_START = 30.11          # TL start of s_shoggoth4
M_IN = 0.42               # slide-in over the end of the room
M_DOWN = 0.62             # shrink into its 3D spot at the start of the shoggoth scene
M_R = 1300.0              # screen radius when it covers the frame (half diagonal ~1101)


def _mask_local():
    disc = [(260 * math.cos(2 * math.pi * i / 64), 260 * math.sin(2 * math.pi * i / 64), 0) for i in range(64)]
    eyes = [[(x + 28 * math.cos(2 * math.pi * i / 20), -60 + 28 * math.sin(2 * math.pi * i / 20), -2) for i in range(20)] for x in (-90, 90)]
    smile = [(150 * math.cos(a), 30 + 110 * math.sin(a), -2) for a in [math.pi * (0.15 + 0.7 * q / 24) for q in range(25)]]
    return disc, eyes, smile


def draw_mask2d(g, m, sc, wk=12.0):
    """m: local (x, y, z) -> screen (x, y); sc: px per local unit (for the line weights)"""
    disc, eyes, smile = _mask_local()
    fl = lambda P: [v for p in P for v in m(p)]
    g.poly(fl(disc), fill=INK, stroke=GOLD, w=max(3.0, 7.0 * sc), a=0.95, fa=0.95)
    for E_ in eyes:
        g.poly(fl(E_), fill=BG, a=1, fa=1)
    g.line(fl(smile), c=BG, w=wk * sc, a=1)


def mask_slide_in(g, t):
    u = prog(t, SH_START - M_IN, SH_START)
    if u <= 0:
        return
    for echo in (2, 1, 0):          # two gold echo frames trailing the slide
        ue = clamp(u - 0.10 * echo)
        if ue <= 0:
            continue
        k = 1 - (1 - ue) ** 3
        cx = lerp(W + M_R * 1.05, W / 2, k); cy = lerp(H / 2 + 260, H / 2, k)
        rot = 0.55 * (1 - k)
        sc = M_R / 260.0
        c_, s_ = math.cos(rot), math.sin(rot)
        m = lambda p, cx=cx, cy=cy, c_=c_, s_=s_, sc=sc: (cx + sc * (p[0] * c_ - p[1] * s_), cy + sc * (p[0] * s_ + p[1] * c_))
        if echo:
            disc = _mask_local()[0]
            g.poly([v for p in disc for v in m(p)], fill=None, stroke=GOLD, w=10, a=0.35 / echo)
        else:
            draw_mask2d(g, m, sc)


def s_shoggoth4(g, t, lt):
    tE = T0(12); t_sh = WT(11, 2); t_eyes = WT(11, 3); t0e = T0(11)
    C0 = SH_C
    keys = [(30.0, orbit(C0, 2600, -0.4, 0.18), C0, 52, 0.04),
            (32.6, orbit(C0, 1900, 0.35, 0.05), (0, 0, 100), 55, -0.03),
            (t0e, orbit(C0, 1700, 0.10, 0.03), (0, -40, 60), 55, 0.0),
            (t_eyes, (-140, -70, -900), (0, -70, 0), 56, 0.02),
            (35.8, (60, -80, -700), (0, -70, -60), 58, 0.0),
            (37.2, orbit((0, -70, -95), 1050, 0.32, 0.10), (0, -70, -60), 56, 0.02),   # v44: stays in front, gentle pan
            (tE, orbit((0, -70, -95), 1500, -0.22, 0.05), (0, -60, -40), 54, -0.02)]
    cam = cam_at(t, keys, shake=12 * pulse(t, 1, 7) * (t > 35.6))
    env(g, cam, 700, fog=6500)
    dust(g, cam, t)
    e = eo(prog(t, t0e - 0.15, t_sh + 0.2))            # eyes emerge
    wide = eo(prog(t, t_eyes - 0.05, t_eyes + 0.3)) * (1 - 0.5 * prog(t, 36.5, tE))
    bl = math.exp(-((t - (t_sh - 0.12)) / 0.06) ** 2) if e > 0.5 else 0.0
    # where each eye's tentacle bases sit (on its rim, in the eye plane)
    bases = {}
    if e > 0:
        for j, c in enumerate(EYE_POS):
            r, u, f = _eye_basis(c, cam, k=0.0)
            for i in range(len(TENT)):
                if i % 3 == j:
                    a = TENT[i][0] * 1.0
                    bases[i] = v_add(c, v_add(v_mul(r, 150 * clamp(e * 1.8) * math.cos(a)), v_mul(u, 150 * clamp(e * 1.8) * math.sin(a))))
    # tentacles: those owned by an eye grow out of it and carry gold pulses into it
    for i in range(len(TENT)):
        pts = [_tent(i, t, k) for k in range(25)]
        own = i in bases
        if own:
            d = v_sub(bases[i], pts[0])
            pts = [v_add(p, v_mul(d, (1 - k / 24) ** 1.6 * e)) for k, p in enumerate(pts)]
        poly3(g, cam, pts, GOLDD if own and e > 0.3 else GRID2, 3.0, 0.9)
        for k in range(0, 25, 2):
            point3(g, cam, pts[k], 9 * (1 - k / 26) + 2, GOLD if (k + i) % 7 == 0 else INK, 0.85)
        if own and e > 0.2:
            for m in range(2):
                uu = 1 - ((t * 1.4 + hsh(i, 30) + m * 0.5) % 1.0)
                kk = uu * 24; k0 = int(kk); fr = kk - k0
                p = v_lerp(pts[k0], pts[min(24, k0 + 1)], fr)
                point3(g, cam, p, 10 * e, GOLDL, 0.9 * e)
    # core blob point cloud
    for i in range(380):
        th = hsh(i, 5) * 2 * math.pi; ph = math.acos(2 * hsh(i, 6) - 1)
        rr = 330 * (0.85 + 0.25 * math.sin(t * 3 + i))
        point3(g, cam, (rr * math.sin(ph) * math.cos(th), rr * math.cos(ph), rr * math.sin(ph) * math.sin(th) + 200), 3, INK, 0.6)
    # smiley mask (the lie) slipping off
    slip = prog(t, WT(10, 4) - 0.05, WT(10, 4) + 0.7)
    fly = eio(prog(t, t0e - 0.6, t0e + 0.3))
    mc = (-slip * 380 - fly * 900, -40 - slip * 420 - fly * 500, -160)
    mrot = slip * 0.9 + fly * 1.5
    ud = prog(t, SH_START, SH_START + M_DOWN)
    if fly < 1 and ud < 1:
        def mx(p):
            x, y, z = p
            c_, s_ = math.cos(mrot), math.sin(mrot)
            return (mc[0] + x * c_ - y * s_, mc[1] + x * s_ + y * c_, mc[2] + z)
        pc = cam.p(mx((0, 0, 0))); pr = cam.p(mx((260, 0, 0)))
        ps = math.hypot(pr[0] - pc[0], pr[1] - pc[1]) / 260.0
        k = eio(ud)
        sc = math.exp(lerp(math.log(M_R / 260.0), math.log(ps), k))
        cx = lerp(W / 2, pc[0], k); cy = lerp(H / 2, pc[1], k)
        def m2(p, cx=cx, cy=cy, sc=sc, k=k):
            q = cam.p(mx(p))
            lx = lerp(p[0], (q[0] - pc[0]) / ps, k); ly = lerp(p[1], (q[1] - pc[1]) / ps, k)
            return (cx + sc * lx, cy + sc * ly)
        zc = cam.cs(mx((0, 0, 0)))[2]
        print('PS', t, ps, zc) if os.environ.get('MDBG') else None
        _mask_late[0] = (m2, sc, 12.0 * clamp(1000.0 / zc, 0.35, 3.0) / ps)
    elif fly < 1:
        def mx(p):
            x, y, z = p
            c_, s_ = math.cos(mrot), math.sin(mrot)
            return (mc[0] + x * c_ - y * s_, mc[1] + x * s_ + y * c_, mc[2] + z)
        fill3(g, cam, [mx(p) for p in disc_pts((0, 0, 0), 260, 40)], INK, 0.95, stroke=GOLD, w=3)
        fill3(g, cam, [mx(p) for p in disc_pts((-90, -60, -2), 28, 16)], BG, 1)
        fill3(g, cam, [mx(p) for p in disc_pts((90, -60, -2), 28, 16)], BG, 1)
        sm = [mx((150 * math.cos(a), 30 + 110 * math.sin(a), -2)) for a in [math.pi * (0.15 + 0.7 * q / 16) for q in range(17)]]
        poly3(g, cam, sm, BG, 12, 1)
        text3(g, cam, 'RLHF_MASK.PNG', mx((0, -300, 0)), 24, GOLD, 'mono')
    if ud < 1:
        text3(g, cam, 'RLHF_MASK.PNG', (mc[0], mc[1] - 300, mc[2]), 24, GOLD, 'mono', ud)
    # the shinigami eyes, opening out of the shoggoth
    if e > 0:
        word3(g, cam, '\u6b7b\u795e', (0, -80, 700), (1, 0, 0), (0, -1, 0), 1500, 300, GOLD, 'cjk', 0.28 * wide)
        for j, c in enumerate(EYE_POS):
            _shini_eye2(g, cam, t, c, 122, e, wide, bl, j)
        # v63: eye-opening flash removed at user request
        text3(g, cam, 'SHINIGAMI.EXE  //  TRUE NAME VISIBLE', (0, -330, -100), 24, GOLD, 'mono', e)
    if _mask_late[0] is not None:
        _ml = _mask_late[0]; _mask_late[0] = None
        g.late = lambda: draw_mask2d(g, *_ml)
    hl = {"shoggoth's": GOLD, 'lies,': GOLD, 'shinigami': GOLD, 'eyes': GOLD}
    if t < LINE_WORDS[11][0][1] - 0.04:
        lyric3x(g, cam, t, 10, (0, 420, -350), (1, 0, 0), (0, -1, 0), 1800, 120, INK, hl, depth=60)
    elif t < 36.2:
        c_, r_, u_ = ahead(cam, 1000)
        lyric3x(g, cam, t, 11, v_add(c_, v_mul(cam.u, 330)), r_, u_, 1500, 110, INK, hl, depth=60)
    if t > 35.7:
        uq = prog(t, 35.7, tE)
        for k in range(int(6 + uq * 30)):
            Rr = 1400 + k * 60
            yy = 700 - ((t * 400 + k * 90) % 1400)
            pts = [(Rr * math.cos(a), yy, Rr * math.sin(a) + 200) for a in [2 * math.pi * q / 60 for q in range(61)]]
            poly3(g, cam, pts, GOLD if k % 4 == 0 else GRID2, 1.6, (0.4 + 0.4 * uq) * 0.45)   # v44: dimmer, the cam is closer now
        # v62: end-of-scene flashes removed at user request

s_shoggoth4.xfade = 0.0   # v43: replaced by the mask slide-in / shrink

from jaw3 import s_jaw_v3
from jaw2 import s_jaw_wire

TL = [
    (0.0, s_boot, BG),
    (1.8, s_eye2, BG),
    (T0(1) - 0.01, s_nervous, BG),
    (T0(3) - 0.01, s_loss, BG),
    (T0(5) - 0.01, s_jaw_wire, BG),  # v23: overhauled white/gold wireframe mouth (jaw2.py)
    (T0(6) - 0.01, type_scene(6), BG),
    (T0(7) - 0.01, s_foom, BG),
    (T0(8) - 0.01, s_room, BG),
    (T0(10) - 0.01, s_shoggoth4, BG),
]
