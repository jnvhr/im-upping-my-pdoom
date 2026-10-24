# v111: 'What did Ilya see' reverted to the v108/v109 scene (the v110 corridor overhaul is kept in ilya109.py), with
# the plain slab door replaced by a real bank-vault door: a thick round door with a stepped face, 16 locking bolts
# that retract before it opens and shoot home on the slam, a spoked wheel handle that spins to unlock, heavy hinge
# arms, and a round steel bezel set into the wall (the square opening's corners are filled in).
import math
from cam3d import *
from s3a import T0, T1, WT
from s4a import _panels

VR = 500.0          # door radius
NB = 16             # locking bolts


def _ring(r, z, n=48, a0=0.0):
    return [(r * math.cos(a0 + 2 * math.pi * q / n), r * math.sin(a0 + 2 * math.pi * q / n), z) for q in range(n)]


def _disc(D, xf, r, z0, z1, base, stroke=None, n=48, amb=0.35):
    """closed cylinder along z (z0 front, toward camera), drawn through xf"""
    A = [xf(p) for p in _ring(r, z0, n)]; B = [xf(p) for p in _ring(r, z1, n)]
    D.sq(A, base, stroke, 1.5, amb=amb)
    D.sq(B[::-1], base, stroke, 1.5, amb=amb)
    for q in range(n):
        D.sq([A[q], A[(q + 1) % n], B[(q + 1) % n], B[q]], base, None, 1.0, amb=amb)


def s_vault(g, t, lt):
    t0 = T0(44); tsee = WT(44, 3); tw = WT(44, 4); tk = WT(44, 6); tE = T0(45)
    unl = eio(prog(t, t0 + 0.02, t0 + 0.42))                       # wheel spins + bolts retract
    op = eio(prog(t, t0 + 0.38, tsee)) * 0.7 * (1 - eio(prog(t, tw, tw + 0.38)))
    lock = eback(clamp((t - tw - 0.38) / 0.1)) if t > tw + 0.38 else 0.0   # bolts shoot home on the slam
    bolt_out = 1 - unl * (1 - lock)                                  # 1 = engaged
    slam = t > tw + 0.38
    e = max(0.0, t - tw - 0.38)
    keys = [(t0, (-1100, -180, -3000), (0, -100, 0), 50, 0.03),
            (tsee, (-520, -120, -900), (60, -100, 200), 58, 0.0),
            (tw + 0.38, (-470, -120, -820), (60, -100, 200), 60, 0.0),
            (tk + 0.4, (-300, -220, -1900), (0, -120, 0), 54, -0.02),
            (tE, (200, -300, -2600), (0, -100, 0), 52, 0.03)]
    cam = cam_at(t, keys, shake=45 * math.exp(-e * 6) * slam)
    env(g, cam)
    # what's inside: a glowing intelligence, glimpsed only through the gap
    core = (250, -100, 1500)
    gl = clamp(op / 0.42)
    if gl > 0.02:
        for i in range(240):
            th = hsh(i, 1) * 2 * math.pi; ph = math.acos(2 * hsh(i, 2) - 1)
            rr = 380 * (0.8 + 0.3 * math.sin(t * 4 + i))
            point3(g, cam, (core[0] + rr * math.sin(ph) * math.cos(th + t), core[1] + rr * math.cos(ph), core[2] + rr * math.sin(ph) * math.sin(th + t)), 5, GOLDL if i % 4 else INK, gl)
        for k in range(3):
            R_ = 520 + k * 140
            pts = [v_add(core, rot3((R_ * math.cos(a), R_ * math.sin(a), 0), t * (0.7 + k * 0.3), k * 1.1, 0)) for a in [2 * math.pi * q / 48 for q in range(49)]]
            poly3(g, cam, pts, GOLD, 3, gl)
        point3(g, cam, core, 240, GOLDL, 0.3 * gl)
    # wall with a doorway (solid panels around a 1000x1000 opening)
    F = SFaces()
    WC = (44, 44, 41)
    for (x0, x1, y0, y1) in ((-2600, -500, -1300, 1100), (500, 2600, -1300, 1100), (-500, 500, -1300, -600), (-500, 500, 400, 1100)):
        _panels(F, (x0, y0, 0), (1, 0, 0), (0, 1, 0), 2, 2, (x1 - x0) / 2, (y1 - y0) / 2, WC, (58, 58, 54))
    # round vault opening: fill the corners of the square hole, then a thick steel bezel around it
    for (cx_, cy_, a0) in ((500, 400, 0.0), (-500, 400, math.pi / 2), (-500, -600, math.pi), (500, -600, 1.5 * math.pi)):
        arc = [(VR * 1.04 * math.cos(a0 + math.pi / 2 * q / 8), -100 + VR * 1.04 * math.sin(a0 + math.pi / 2 * q / 8), 0) for q in range(9)]
        F.sq([(cx_, cy_, 0)] + arc, WC, None, 1.0, amb=0.55)
    BZ = (70, 70, 66)
    Ao = _ring(VR * 1.22, -60); Ai = _ring(VR * 1.04, -60); Bo = _ring(VR * 1.22, 0)
    for q in range(48):
        q2 = (q + 1) % 48
        F.sq([v_add(Ao[q], (0, -100, 0)), v_add(Ao[q2], (0, -100, 0)), v_add(Ai[q2], (0, -100, 0)), v_add(Ai[q], (0, -100, 0))], BZ, None, 1.0, amb=0.45)
        F.sq([v_add(Bo[q], (0, -100, 0)), v_add(Bo[q2], (0, -100, 0)), v_add(Ao[q2], (0, -100, 0)), v_add(Ao[q], (0, -100, 0))], BZ, None, 1.0, amb=0.45)
    F.draw(g, cam)
    # light spilling out of the gap
    if gl > 0.02:
        for i in range(36):
            yy = -560 + hsh(i, 2) * 920
            seg3(g, cam, (420 + 30 * hsh(i, 1), yy, -10), (420 - 900 * hsh(i, 3) * gl - 200, yy + (hsh(i, 4) - 0.5) * 400, -1600), GOLDL, 2.5, 0.35 * gl)
    # the door, hinged at x=-500
    ang = op * 1.3

    def dxf(v):
        x, y, z = v
        x2 = x + 500
        c, s = math.cos(ang), math.sin(ang)
        return (x2 * c - z * s - 500, y - 100, x2 * s + z * c)
    # the inside of the vault glowing through the round opening
    if gl > 0.02:
        fill3(g, cam, [(p[0], p[1] - 100, 160) for p in _ring(VR * 1.03, 0, 48)], GOLDL, 0.42 * gl)
        fill3(g, cam, [(p[0] + 120, p[1] - 100, 150) for p in _ring(VR * 0.55, 0, 40)], (255, 244, 200), 0.5 * gl)
    D = SFaces()
    STEEL = (92, 92, 86); STEEL2 = (110, 108, 100); DARKS = (60, 60, 56)
    _disc(D, dxf, VR, -110, 110, STEEL, GOLDD)                       # main door body, 220 thick
    _disc(D, dxf, VR * 0.84, -150, -110, STEEL2, GOLDD)              # stepped face
    _disc(D, dxf, VR * 0.30, -175, -150, DARKS, GOLD, n=32)          # lock housing
    # hinge arms on the hinge side (x=-500), bridging to the wall
    for hy in (-280, 280):
        D.sbox((0, 0, 0), (180, 110, 120), DARKS, GOLDD, 1.2, xf=lambda v, hy=hy: dxf((v[0] - 470, v[1] + hy, v[2] - 60)), amb=0.4)
    # locking bolts around the rim, sliding out into the frame
    for b in range(NB):
        a = 2 * math.pi * (b + 0.5) / NB
        ca, sa = math.cos(a), math.sin(a)
        if ca < -0.75:
            continue                                                  # none on the hinge side
        r0 = VR - 60; r1 = VR + 20 + 110 * bolt_out
        rm = (r0 + r1) / 2; L = r1 - r0
        D.sbox((0, 0, 0), (L, 54, 54), (150, 148, 138), None, 1.0,
               xf=lambda v, ca=ca, sa=sa, rm=rm: dxf((v[0] * ca - v[1] * sa + rm * ca, v[0] * sa + v[1] * ca + rm * sa, v[2])), amb=0.5)
    D.draw(g, cam)
    # engraved rings + bolt circle on the face
    for k in range(2):
        rr = (VR * 0.78, VR * 0.62)[k]
        poly3(g, cam, [dxf(p) for p in _ring(rr, -152, 60)] + [dxf((rr, 0, -152))], GOLD, 3, 0.9)
    for b in range(24):
        a = 2 * math.pi * b / 24
        point3(g, cam, dxf((VR * 0.7 * math.cos(a), VR * 0.7 * math.sin(a), -153)), 7, GOLDL, 0.9)
    # spoked wheel handle: spins open on the unlock, spins back on the slam
    wa = unl * 2.6 - lock * 2.6 * unl + 0.3
    hub = dxf((0, 0, -250))
    seg3(g, cam, dxf((0, 0, -175)), hub, STEEL2, 26, 1)
    rim = [dxf((300 * math.cos(wa + 2 * math.pi * q / 48), 300 * math.sin(wa + 2 * math.pi * q / 48), -250)) for q in range(49)]
    poly3(g, cam, rim, GOLD, 12, 1)
    for k in range(4):
        a = wa + 2 * math.pi * k / 4
        e0 = dxf((300 * math.cos(a), 300 * math.sin(a), -250))
        seg3(g, cam, hub, e0, GOLD, 10, 1)
        point3(g, cam, dxf((360 * math.cos(a), 360 * math.sin(a), -250)), 16, GOLDL, 1)
        seg3(g, cam, e0, dxf((360 * math.cos(a), 360 * math.sin(a), -250)), GOLD, 10, 1)
    point3(g, cam, hub, 30, GOLDL, 1)
    if slam:
        st = eback(clamp(e / 0.18))
        word3(g, cam, '[REDACTED]', dxf((0, 0, -270)), (1, 0, 0), (0, -1, 0), 900 * lerp(1.5, 1.0, st), 160, GOLD, 'monox', clamp(st * 2))
        g.flash = 0.3 * math.exp(-e * 9)
    else:
        text3(g, cam, 'CLASSIFIED  //  WHAT ILYA SAW', (0, -760, -10), 34, GOLD, 'mono')
    # question marks drifting toward the gap (curiosity)
    qn = prog(t, tsee - 0.3, tsee + 0.4)
    for i in range(9):
        a = hsh(i, 3) * 2 * math.pi
        p = (300 + 900 * math.cos(a + t * 0.3) - 250 * qn * (1 - slam * 1.0), -250 + 600 * math.sin(a * 1.7 + t * 0.4), -150 - 250 * hsh(i, 4))
        al = qn * (0.35 if slam and i else 1.0)
        if al > 0.02:
            word3(g, cam, '?', p, *facing(p, cam.eye), 90 + 70 * hsh(i, 5), 200, GOLD if i % 3 == 0 else INK, 'sans', al, x=True, depth=30, n=3)
    c, r, u = ahead(cam, 1050)
    lyric3x(g, cam, t, 44, v_add(c, v_mul(cam.u, 340)), r, u, 1800, 120, INK, {'ilya': GOLD, 'see?': GOLD, 'never': GOLD, 'know': GOLD}, depth=60)
    g.post = dict(glow=0.6 + 0.4 * gl)


