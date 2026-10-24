"""v87: shared detailed person model (from the v86 Chinese-room operator): hair, face, ears, collared shirt,
belt, trousers, shoes, hands with fingers. Driven by a joint dict like s4b.humanoid; facing=+1 faces along
cross(up, right) (= +z for an upright figure with rs at +x), -1 the opposite way."""
import math
from cam3d import *


def v_len(a):
    return math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])

SKIN_P = (196, 186, 170); SHIRT_P = (150, 148, 140); PANTS_P = (62, 62, 60); HAIR_P = (34, 32, 30); SHOE_P = (26, 26, 25)


def fill_joints(j):
    """derive chest/shoulders/hips for a stick figure that only has head, neck, hip, elbows, hands, knees, feet"""
    j = dict(j)
    up = v_norm(v_sub(j['neck'], j['hip']))
    rt = v_sub(j['re'], j['le'])
    rt = v_norm(v_sub(rt, v_mul(up, v_dot(rt, up))))
    L = v_len(v_sub(j['neck'], j['hip']))
    s = L / 230.0
    j.setdefault('chest', v_lerp(j['neck'], j['hip'], 0.32))
    j.setdefault('ls', v_add(v_lerp(j['neck'], j['hip'], 0.1), v_mul(rt, -72 * s)))
    j.setdefault('rs', v_add(v_lerp(j['neck'], j['hip'], 0.1), v_mul(rt, 72 * s)))
    j.setdefault('lhip', v_add(j['hip'], v_mul(rt, -42 * s)))
    j.setdefault('rhip', v_add(j['hip'], v_mul(rt, 42 * s)))
    return j


def person(F, j, facing=1, shirt=SHIRT_P, skin=SKIN_P, pants=PANTS_P, hair=HAIR_P, accent=GOLDD):
    up = v_norm(v_sub(j['neck'], j['hip']))
    rt = v_sub(j['rs'], j['ls'])
    s = v_len(rt) / 140.0
    rt = v_norm(v_sub(rt, v_mul(up, v_dot(rt, up))))
    fw = v_mul(v_norm(v_cross(up, rt)), facing)
    P = lambda o, a=0, b=0, c=0: v_add(o, v_add(v_mul(rt, a * s), v_add(v_mul(up, b * s), v_mul(fw, c * s))))
    # legs: tapered trousers, shoes pointing forward
    for hp, kn, ft in (('lhip', 'lk', 'lf'), ('rhip', 'rk', 'rf')):
        a, b, c = j[hp], j[kn], j[ft]
        F.tube([a, v_lerp(a, b, 0.5), b], 30 * s, pants, None, 8, rs=[34 * s, 30 * s, 27 * s], amb=0.3)
        F.tube([b, v_lerp(b, c, 0.5), c], 25 * s, pants, None, 8, rs=[27 * s, 23 * s, 21 * s], amb=0.3)
        F.tube([P(c, 0, 4, -14), P(c, 0, -2, 22), P(c, 0, -6, 52)], 0, SHOE_P, None, 6, rs=[22 * s, 24 * s, 16 * s], amb=0.4, cap=True)
    # torso: pelvis -> chest -> neck base, belt + buckle, collar
    hip, che, nek = j['hip'], j['chest'], j['neck']
    pel = P(hip, 0, -12)
    F.tube([pel, v_lerp(pel, che, 0.5), che, P(nek, 0, -14)], 60 * s, shirt, None, 10, rs=[56 * s, 60 * s, 66 * s, 44 * s], amb=0.3)
    F.tube([P(hip, 0, -22), P(hip, 0, 6)], 0, pants, None, 10, rs=[58 * s, 58 * s], amb=0.3)
    F.tube([P(hip, 0, -12), P(hip, 0, -2)], 0, (40, 40, 38), None, 10, rs=[60 * s, 60 * s], amb=0.35)
    F.sbox(P(hip, 0, -7, 60), (24 * s, 12 * s, 6 * s), accent, None, amb=0.8)
    for sx in (-1, 1):
        F.sq([P(nek, sx * 5, -12, 30), P(nek, sx * 32, -10, 24), P(nek, sx * 18, -34, 34)], (200, 198, 190), None, amb=0.5)
    # neck + head
    hd = j['head']
    hu = v_norm(v_sub(hd, nek))
    F.tube([P(nek, 0, -16), v_lerp(nek, hd, 0.55)], 0, skin, None, 8, rs=[20 * s, 19 * s], amb=0.35)
    hr = 50 * s
    F.sphere(hd, hr, skin, None, 8, 14, sy=1.12, amb=0.35)
    F.sphere(P(hd, 0, 5, -4), hr * 1.07, hair, None, 6, 14, sy=1.08, lat0=0.0, lat1=0.45, amb=0.3)
    F.sphere(P(hd, 0, -4, -22), hr * 0.85, hair, None, 6, 12, sy=1.15, amb=0.3)
    for sx in (-1, 1):
        F.sphere(P(hd, sx * 50, -3, -2), 10 * s, skin, None, 3, 6, sy=1.4, amb=0.35)    # ears
        F.sphere(P(hd, sx * 18, 2, 45), 5 * s, (24, 24, 23), None, 3, 6, amb=0.6)       # eyes
        F.sbox(P(hd, sx * 18, 11, 46), (20 * s, 4 * s, 4 * s), hair, None, amb=0.5)      # brows
    F.tube([P(hd, 0, 2, 48), P(hd, 0, -12, 57)], 6 * s, skin, None, 5, amb=0.4)         # nose
    F.sbox(P(hd, 0, -26, 45), (18 * s, 3 * s, 4 * s), (120, 90, 80), None, amb=0.5)    # mouth
    # arms: shoulder ball, sleeve to the forearm, bare wrist, palm + four fingers + thumb
    for sh, el, ha, sx in (('ls', 'le', 'lh', -1), ('rs', 're', 'rh', 1)):
        a, b, c = j[sh], j[el], j[ha]
        F.sphere(a, 30 * s, shirt, None, 4, 8, amb=0.3)
        F.tube([a, b], 26 * s, shirt, None, 8, rs=[28 * s, 22 * s], amb=0.3)
        w = v_lerp(b, c, 0.72)
        F.tube([b, w], 21 * s, shirt, None, 8, rs=[22 * s, 18 * s], amb=0.3)
        F.tube([w, c], 14 * s, skin, None, 6, rs=[15 * s, 13 * s], amb=0.35)
        d = v_norm(v_sub(c, b))
        side = v_norm(v_cross(d, fw)) if abs(v_dot(d, fw)) < 0.95 else rt
        F.sphere(v_add(c, v_mul(d, 12 * s)), 17 * s, skin, None, 4, 8, sy=0.8, amb=0.35)
        for k in range(4):
            o = v_add(v_add(c, v_mul(d, 22 * s)), v_mul(side, (-12 + 8 * k) * s))
            F.tube([o, v_add(o, v_mul(d, 26 * s))], 3.6 * s, skin, None, 4)
        o = v_add(v_add(c, v_mul(d, 8 * s)), v_mul(side, 16 * s * -sx))
        F.tube([o, v_add(o, v_add(v_mul(d, 16 * s), v_mul(side, 8 * s * -sx)))], 4.2 * s, skin, None, 4)
