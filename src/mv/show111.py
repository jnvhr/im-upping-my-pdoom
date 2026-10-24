# v111: "Was it all for show?" no longer hard-cuts to a black screen with a flickering SHOW? on the last beat.
# The camera keeps climbing in one continuous move: past the puppet, up the strings, past the control bar
# (OPERATOR: ???), just the one bar as in the original (v113: the second bar and its strings are gone). On the beat after
# "show?" the bar explodes: a flash, a fireball, shockwave rings, tumbling shards, and sparks, the strings go slack,
# and the camera is thrown back, straight into the drop.
import math
from cam3d import *
from s3a import T0, T1, WT
from s3c import _figure

DROP = 140.24
DARK = 139.79
BOOM = 140.25     # v114: the big hit after "show?" (spectral-flux peak 140.26); the bar holds and strains until here
HAND = 140.69     # o_explode takes over on the next hit (140.70)
CTR = (0, -2300, 0)   # v115: the bar's position is the centre of the drop explosion
ST1 = 143.2          # o_globe starts here (s4c ST[1])
SNAP = [140.06, 140.10, 140.14, 140.18, 140.22]   # strings snap one by one on the riser


def _bar(g, cam, y, size, ang, label, al=1.0):
    F = Faces()
    F.box((0, y, 0), (1000 * size, 40 * size, 40 * size), GOLD, BG, 2, al, xf=lambda v: rot3(v, 0, 0, ang))
    F.box((0, y, 0), (40 * size, 40 * size, 600 * size), GOLD, BG, 2, al)
    F.draw(g, cam)
    text3(g, cam, label, (0, y - 150 * size, 0), 40 * size, GOLD, 'monox', al)
    pts = [rot3(p, 0, 0, ang) for p in [(-500 * size, 0, 0), (500 * size, 0, 0), (0, 0, -300 * size), (0, 0, 300 * size)]]
    return [(p[0], p[1] + y, p[2]) for p in pts]


def s_puppet2(g, t, lt):
    keys = [(137.0, (0, -200, -1800), (0, -250, 0), 55, 0.0),
            (138.5, (-600, -800, -1500), (0, -700, 0), 57, 0.04),
            (139.7, (120, -1900, -1350), (0, -2250, 0), 58, -0.02),
            (DROP, (80, -2500, -2600), (0, -2400, 0), 64, 0.03),
            (140.48, (120, -2420, -3000), (0, -2300, 0), 66, 0.04),     # recoil from the blast
            (140.95, (0, -2420, -1150), (0, -2300, 0), 60, 0.01),       # push into the fireball as the number forms
            (142.2, v_add(CTR, orbit((0, 0, 0), 2000, 0.35, 0.15)), CTR, 57, 0.05),
            (ST1, v_add(CTR, orbit((0, 0, 0), 2600, 0.6, 0.2)), CTR, 55, 0.08)]
    kick = math.exp(-max(0.0, t - BOOM) * 8) * (t > BOOM)
    cam = cam_at(t, keys, punch=0.6, shake=70 * kick)
    camc = cam_at(t, keys)
    env(g, cam, 200, fog=7000)
    sway = math.sin(t * 2.2)
    j = _figure(t, sway)
    fall = max(0.0, t - SNAP[0])
    if fall > 0:
        j = {k: (v[0], v[1] + 1800 * fall * fall, v[2]) for k, v in j.items()}
    # v116: back to the original wireframe stick puppet (pre-v87), not the person model
    if fall < 1.3:
        for a_, b_ in (('head', 'neck'), ('neck', 'hip'), ('neck', 'le'), ('le', 'lh'), ('neck', 're'), ('re', 'rh'),
                       ('hip', 'lk'), ('lk', 'lf'), ('hip', 'rk'), ('rk', 'rf')):
            seg3(g, cam, j[a_], j[b_], INK, 8, 1)
        mesh3(g, cam, *sphere_mesh(70, 6, 12), c=INK, w=2, xf=xform(j['head']))
        for k in j:
            point3(g, cam, j[k], 10, GOLD, 1)
    # the control bar (the operator); on the beat after "show?" it blows apart
    ba = 0.3 * math.sin(t * 2.2)
    BY = -2300
    if t < BOOM:
        # after "show?" the bar strains: trembles harder, glows, and the strings snap one by one on the riser
        st = prog(t, DARK, BOOM)
        ba += 0.06 * st * math.sin(t * 90)
        bar = _bar(g, cam, BY + 18 * st * math.sin(t * 110), 1.0, ba, 'OPERATOR: ???')
        if st > 0:
            point3(g, cam, (0, BY, 0), 120 + 260 * st, GOLDL, 0.5 * st * st)
        for n_, (k, anchor) in enumerate((('lh', bar[0]), ('rh', bar[1]), ('head', bar[2]), ('lk', bar[3]), ('rk', bar[3]))):
            ts_ = SNAP[n_]
            if t < ts_:
                seg3(g, cam, anchor, j[k], GOLDL, 1.2 + 1.5 * st, 0.8 + 0.2 * st)
            else:
                e2 = t - ts_
                point3(g, cam, v_lerp(anchor, j[k], 0.5), 30 * math.exp(-e2 * 20), GOLDL, 1)
                seg3(g, cam, anchor, v_lerp(anchor, v_add(j[k], (0, 400 * e2, 0)), 0.45 * (1 - clamp(e2 * 3))), GOLDL, 1.2, 0.8)
                seg3(g, cam, j[k], v_lerp(j[k], anchor, 0.45 * (1 - clamp(e2 * 3))), GOLDL, 1.2, 0.8)
    else:
        e = t - BOOM
        ctr = (0, BY, 0)
        # flash + core fireball
        g.flash = max(g.flash, 0.85 * math.exp(-e * 7))
        g.flash_c = GOLDL
        point3(g, cam, ctr, 260 + 1600 * e, GOLDL, 0.55 * math.exp(-e * 4))
        point3(g, cam, ctr, 120 + 700 * e, (255, 246, 210), 0.9 * math.exp(-e * 6))
        # the bar shatters into tumbling pieces
        F = Faces()
        for q in range(14):
            d = v_norm(((hsh(q, 1) - 0.5), (hsh(q, 2) - 0.5) * 0.8, (hsh(q, 3) - 0.5)))
            sp = 1800 + 1600 * hsh(q, 4)
            p = v_add(ctr, v_add(v_mul(d, sp * e), (0, 900 * e * e, 0)))
            sz = 60 + 140 * hsh(q, 5)
            rx, rz = e * 9 * hsh(q, 6), e * 7 * hsh(q, 7)
            F.box(p, (sz * 2.2, sz * 0.4, sz * 0.4), GOLD, BG, 2, 1, xf=lambda v, rx=rx, rz=rz: rot3(v, rx, 0, rz))
        F.draw(g, cam)
        # sparks
        for q in range(120):
            d = v_norm(((hsh(q, 11) - 0.5), (hsh(q, 12) - 0.5), (hsh(q, 13) - 0.5)))
            p = v_add(ctr, v_add(v_mul(d, (2500 + 2500 * hsh(q, 14)) * e), (0, 600 * e * e, 0)))
            point3(g, cam, p, 6 + 6 * hsh(q, 15), GOLDL if q % 3 else INK, max(0.0, 1 - e * 1.5))
        # v115: the drop explosion (formerly o_explode, its own scene) now grows out of the same blast, in one shot
        import s4c as S4
        F2 = SFaces()
        for (dx, dy, dz, sp) in S4.EXPL:
            d = 3200 * sp * eo(clamp(e / 1.6))
            point3(g, cam, v_add(CTR, (dx * d, dy * d, dz * d)), 6, GOLDL if sp > 1.1 else (GOLD if sp > 0.8 else INK), clamp(1.4 - e * 0.5))
        for i in range(40):
            d = 2600 * (0.4 + hsh(i, 1)) * eo(clamp(e / 1.8))
            dirv = v_norm((hsh(i, 2) - 0.5, hsh(i, 3) - 0.5, hsh(i, 4) - 0.5))
            F2.sbox(v_add(CTR, v_mul(dirv, d)), (90 + 90 * hsh(i, 5),) * 3, GOLD if i % 4 == 0 else (120, 120, 114), None, xf=lambda v, i=i: rot3(v, e * 3 + i, e * 2, i), amb=0.4)
        F2.draw(g, cam)
        for k in range(4):
            R_ = e * 2600 - k * 300
            if R_ > 0:
                poly3(g, cam, [v_add(CTR, (R_ * math.cos(a), 0, R_ * math.sin(a))) for a in [2 * math.pi * q / 72 for q in range(73)]], GOLD, 6, clamp(1 - e * 0.5))
                poly3(g, cam, [v_add(CTR, (R_ * math.cos(a), R_ * math.sin(a), 0)) for a in [2 * math.pi * q / 72 for q in range(73)]], INK, 3, clamp(0.8 - e * 0.5))
        point3(g, cam, CTR, 300 * math.exp(-e * 1.5), GOLDL, 0.6)
        if e > 0.25:
            S4._outro_text(g, cam, t, CTR, 240 * eback(clamp((e - 0.25) / 0.35)))
        g.flash = max(g.flash, math.exp(-e * 5.5))
        # cut strings fall slack, the puppet drops
        for k in ('lh', 'rh', 'head', 'lk', 'rk'):
            a = j[k]
            top = v_add(a, (0, -900 + 1500 * e, 0))
            seg3(g, cam, a, v_lerp(a, top, 1 - clamp(e * 2)), GOLDL, 1.2, 0.8 * (1 - clamp(e * 2)))
    dk = 0.0
    c, r, u = ahead(camc, 1000)
    lyric3x(g, camc, t, 45, v_add(c, v_mul(camc.u, 340)), r, u, 1700, 125, INK, {'all': GOLD, 'show?': GOLD, 'show': GOLD}, depth=60,
            al=1 - prog(t, 140.62, 140.95))   # v115: the line fades as the camera pushes into the number
    g.post = dict(glow=0.55 + 0.3 * kick, vig=1.0 + 0.4 * dk) if t < BOOM else dict(glow=1.0)
