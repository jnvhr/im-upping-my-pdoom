# v118 overhauls: servant & boss (a colossal seated machine overlord), breaking through each safety fence
# (hex energy barriers that shatter, orbiting whip-pan camera), hundred thousand GPU (powers-of-ten zoom-out from one
# H100 die to a 9-hall campus, every GPU lighting up gold as the counter climbs).
import math
import numpy as np
from cam3d import *
from s3a import T0, T1, WT
from ov116 import beats, capcam, glow


# ======================================================== SERVANT & BOSS 13.18 - 16.66
def s_servant(g, t, lt):
    from s4b import CFaces, humanoid
    t0 = T0(4); tsv = WT(4, 3); tmy = WT(4, 6); tb = WT(4, 7); tE = T0(5)
    bow = eio(prog(t, tsv - 0.15, tsv + 0.35))
    awake = eo(prog(t, tb - 0.10, tb + 0.25))          # the boss's visor ignites on 'boss'
    reach = eio(prog(t, tmy - 0.25, tb + 0.30))        # its hand rises and hovers over the servant
    bt = beats(t0 - 0.5, t + 0.001)
    lb = bt[-1] if bt else t0
    pb = math.exp(-(t - lb) * 7)
    # camera: low behind the kneeling servant looking up, slow push; on 'boss' it drops lower and swings round
    keys = [(t0, (-1100, 200, -2900), (0, -650, 800), 50, 0.02),
            (tsv, (-1250, 160, -2500), (0, -680, 800), 50, 0.0),
            (tmy, (-1350, 120, -2150), (0, -720, 800), 52, -0.02),
            (tb + 0.12, (-700, 330, -1850), (0, -840, 900), 58, -0.05),
            (tE, (-450, 330, -1650), (60, -880, 900), 60, -0.03)]
    cam = cam_at(t, keys, shake=4 + 26 * math.exp(-max(0.0, t - tb) * 6) * (t > tb))
    env(g, cam)
    floor(g, cam, 470.0, 160, 34, GRID2, 0.6, 0, 600, fog=5000)
    F = CFaces()
    PLATE = (66, 65, 61); PLATE2 = (104, 102, 94); DARK = (34, 34, 32); BLK = (24, 24, 23)
    # backdrop: two rows of monolith server pillars with LED strips
    for sx in (-1, 1):
        for k in range(6):
            x = sx * (1250 + 80 * k); z = 1300 + k * 520
            F.sbox((x, -700, z), (220, 2340, 220), (26, 26, 25), None, amb=0.35)
    # dais: wide stepped plinth
    for k in range(4):
        F.sbox((0, 445 - k * 55, 900 + k * 60), (2300 - k * 330, 55, 1500 - k * 230), (48 - k * 3, 47 - k * 3, 44 - k * 3), None, amb=0.45)
        F.sbox((0, 418 - k * 55, 900 + k * 60 - (750 - k * 115)), (2300 - k * 330, 6, 10), GOLDD, None, amb=0.6)
    # throne block behind the colossus
    F.sbox((0, -120, 1250), (1500, 820, 380), (40, 40, 38), None, amb=0.4)
    F.sbox((0, -1300, 1420), (1700, 1700, 120), (32, 32, 30), None, amb=0.4)
    F.sbox((0, -1300, 1355), (40, 1600, 10), GOLD, None, amb=0.65)
    F.draw(g, cam, fog=6500); F = CFaces()   # v130: backdrop/throne pass first, then crown, then the colossus
    # ---- the colossus: seated, ~4x the servant
    br = 1 + 0.015 * math.sin(t * 2.0) + 0.02 * pb
    HIP = (0, 0, 1050)
    lean = 0.18 * reach                                  # leans toward the servant as it reaches
    def LX(p):   # torso lean about the hips
        y, z = p[1] - HIP[1], p[2] - HIP[2]
        c_, s_ = math.cos(lean), math.sin(lean)
        return (p[0], HIP[1] + y * c_ + z * s_, HIP[2] - y * s_ + z * c_)
    # pelvis
    F.tube([LX((0, 120, 1050)), LX((0, -120, 1050))], 0, DARK, None, 8, rs=[360, 380], amb=0.35, cap=True)
    # segmented abdomen
    for k in range(4):
        y = -150 - k * 95
        F.tube([LX((0, y, 1050)), LX((0, y - 80, 1055))], 0, PLATE if k % 2 == 0 else PLATE2, None, 8, rs=[300 + k * 22, 306 + k * 26], amb=0.35, cap=True)
    # chest: wide faceted prism flaring to the shoulders
    F.tube([LX((0, -520, 1060)), LX((0, -700, 1070)), LX((0, -880, 1075))], 0, PLATE, None, 6,
           rs=[380 * br, 500 * br, 540 * br], amb=0.33, cap=True)
    # gold seams down the chest front and a keel
    for sx in (-1, 0, 1):
        F.tube([LX((sx * 170, -870, 1075 - 470 + abs(sx) * 60)), LX((sx * 150, -540, 1060 - 360 + abs(sx) * 40))], 9, GOLD, None, 4, amb=0.65)
    # gorget + neck
    F.tube([LX((0, -880, 1070)), LX((0, -980, 1060))], 0, DARK, None, 8, rs=[270, 190], amb=0.35, cap=True)
    HEAD = LX((0, -1180 + 10 * math.sin(t * 1.3), 930))
    # shoulders / arms
    hands = []
    for sx in (-1, 1):
        sh = LX((sx * 560, -820, 1070))
        rest_el = (sx * 690, -330, 960); rest_hd = (sx * 660, -110, 640)
        el, hd = rest_el, rest_hd
        if sx < 0 and reach > 0:
            el = v_lerp(rest_el, (-560, -420, 480), reach)
            hd = v_lerp(rest_hd, (-150, 20, 60), reach)    # hovers palm-down over the servant
        for k in range(3):   # layered pauldron
            pc = v_add(sh, (sx * 40 * k, 60 * k - 50, 0))
            F.sphere(pc, 250 - 30 * k, PLATE2 if k == 0 else PLATE, None, 5, 10, sy=0.72, amb=0.42)
        F.tube([v_add(sh, (250 * math.cos(q), -20, 250 * math.sin(q))) for q in [2 * math.pi * k / 18 for k in range(19)]], 12, GOLD, None, 4, amb=0.6)
        F.tube([sh, el], 0, DARK, None, 6, rs=[130, 110], amb=0.33)
        F.sphere(el, 135, PLATE2, None, 4, 8, amb=0.42)
        F.tube([v_lerp(el, hd, 0.12), v_lerp(el, hd, 0.84)], 0, PLATE, None, 6, rs=[115, 150], amb=0.35, cap=True)
        F.tube([v_lerp(el, hd, 0.76), v_lerp(el, hd, 0.84)], 0, GOLD, None, 6, rs=[156, 156], amb=0.6)
        F.sphere(hd, 120, PLATE2, None, 4, 8, sy=0.75, amb=0.4)
        dvec = v_norm(v_sub(hd, el))
        down = (0.0, 1.0, 0.0)
        for f in range(4):
            off = (sx * (-60 + f * 40), 0, 0)
            a0 = v_add(v_add(hd, off), v_mul(dvec, 70))
            if sx < 0:
                a1 = v_add(a0, v_add(v_mul(dvec, 110 * (1 - reach) + 150 * reach), v_mul(down, 150 * (1 - reach) + 80 * reach)))
            else:
                a1 = v_add(a0, v_add(v_mul(dvec, 60), (0, 170, -40)))
            F.tube([a0, v_lerp(a0, a1, 0.55), a1], 0, DARK, None, 4, rs=[26, 22, 12], amb=0.45)
        hands.append(hd)
    # legs: thighs forward, shins down to the dais
    for sx in (-1, 1):
        kn = (sx * 300, -40, 520); ft = (sx * 330, 390, 430)
        F.tube([(sx * 250, 20, 1030), kn], 0, PLATE, None, 6, rs=[210, 170], amb=0.35)
        F.sphere(kn, 175, PLATE2, None, 5, 10, sy=0.85, amb=0.42)
        F.tube([kn, ft], 0, PLATE, None, 6, rs=[150, 125], amb=0.35)
        F.tube([v_lerp(kn, ft, 0.25), v_lerp(kn, ft, 0.8)], 0, PLATE2, None, 6, rs=[160, 140], amb=0.42)
        F.tube([v_add(kn, (0, 90, -140)), v_add(kn, (0, 115, -150))], 0, GOLD, None, 6, rs=[95, 95], amb=0.6)
        F.tube([v_add(ft, (0, 30, 60)), v_add(ft, (0, 40, -170)), v_add(ft, (0, 50, -330))], 0, DARK, None, 6, rs=[140, 120, 30], amb=0.38, cap=True)
    # head: tall faceted helm, flat mask with a single slit visor; tilts down toward the servant
    hp = 0.32 * eio(prog(t, tsv + 0.3, tsv + 0.9)) + 0.12 * reach
    def HX(p):
        y, z = p[1] - HEAD[1], p[2] - HEAD[2]
        c_, s_ = math.cos(hp), math.sin(hp)
        return (p[0], HEAD[1] + y * c_ - z * s_, HEAD[2] + y * s_ + z * c_)
    F.sphere(HEAD, 240, (52, 51, 48), None, 6, 12, sy=1.25, amb=0.42, xf=lambda v: v_sub(HX(v_add(HEAD, v)), HEAD))
    MASK = [(-200, -170, -130), (200, -170, -130), (165, 190, -150), (-165, 190, -150)]
    F.sq([HX(v_add(HEAD, p)) for p in MASK], (58, 57, 53), None, amb=0.45)
    F.sq([HX(v_add(HEAD, (-205, -175, -128))), HX(v_add(HEAD, (205, -175, -128))), HX(v_add(HEAD, (150, -260, -60))), HX(v_add(HEAD, (-150, -260, -60)))], PLATE2, None, amb=0.42)
    for sx in (-1, 1):   # swept horns / antennae
        b0 = HX(v_add(HEAD, (sx * 170, -200, 20)))
        F.tube([b0, HX(v_add(HEAD, (sx * 300, -420, 120))), HX(v_add(HEAD, (sx * 330, -640, 260)))], 0, DARK, None, 5, rs=[36, 24, 6], amb=0.45)
    # gyroscopic crown (v130: drawn BEFORE the body so the boss occludes it): three tilted rings behind the head, spinning, faster once it's awake
    cc = HX(v_add(HEAD, (0, -60, 480)))
    for k, R_ in enumerate((420, 500)):
        sp = (0.3 + 1.2 * awake) * (1 if k == 0 else -1.3)
        pts = [v_add(cc, rot3((R_ * math.cos(2 * math.pi * q / 72), R_ * math.sin(2 * math.pi * q / 72), 0), 0.15, 0.2 * math.sin(t * 0.7), 0)) for q in range(73)]
        poly3(g, cam, pts, GOLD if k == 0 else GOLDD, 3 + 2 * awake, 0.5 + 0.45 * awake)
        for q in range(16):   # spokes / ticks
            a = 2 * math.pi * q / 16 + t * sp
            p0 = v_add(cc, rot3(((R_ - 30) * math.cos(a), (R_ - 30) * math.sin(a), 0), 0.15, 0, 0))
            p1 = v_add(cc, rot3(((R_ + 30) * math.cos(a), (R_ + 30) * math.sin(a), 0), 0.15, 0, 0))
            seg3(g, cam, p0, p1, GOLD, 3, 0.5 + 0.45 * awake)
    F.draw(g, cam, fog=6500)
    # visor slit: dim ember before 'boss', a blazing gold bar after
    vl = HX(v_add(HEAD, (-150, -40, -145))); vr = HX(v_add(HEAD, (150, -40, -145)))
    seg3(g, cam, vl, vr, mix((90, 60, 14), GOLDL, awake), 7 + 9 * awake, 1.0)
    if awake > 0:
        for k in range(5):
            glow(g, cam, v_lerp(vl, vr, k / 4), 50 + 60 * awake, GOLD, 0.45 * awake)
    # chest core: rings pulse on the beat, ignite fully on 'boss'
    core = LX((0, -700, 1075 - 545))
    for k in range(4):
        R_ = 34 + k * 30
        a0 = t * (1 + k * 0.5) * (-1) ** k
        pts = [(core[0] + R_ * math.cos(2 * math.pi * q / 32 + a0), core[1] + R_ * math.sin(2 * math.pi * q / 32 + a0), core[2]) for q in range(33)]
        poly3(g, cam, pts, GOLD if k % 2 == 0 else GOLDD, 3, 1)
    glow(g, cam, core, 160 + 120 * awake + 60 * pb, GOLD, 0.35 + 0.4 * awake)
    # cables from its back down into the floor (wired into the machine)
    for k in range(8):
        sx = -1 if k % 2 else 1
        a = LX((sx * (120 + 60 * (k // 2)), -760 + 70 * (k // 2), 1260))
        b = (sx * (500 + 260 * (k // 2)), 470, 1900 + 120 * k)
        m = v_add(v_lerp(a, b, 0.5), (0, 320, 260))
        pts = [v_lerp(v_lerp(a, m, s), v_lerp(m, b, s), s) for s in [q / 16 for q in range(17)]]
        poly3(g, cam, pts, (60, 60, 56), 10, 0.95, fog=6000)
        ph = (t * 1.4 + k * 0.17) % 1.0
        q_ = pts[int((1 - ph) * 16)]
        point3(g, cam, q_, 9, GOLD, 0.6 + 0.4 * awake)
    # backdrop LED strips
    for sx in (-1, 1):
        for k in range(6):
            x = sx * (1250 + 80 * k) - sx * 152; z = 1300 + k * 520
            for r_ in range(10):
                on = hsh(k * 31 + r_ + (sx > 0) * 7, int(t * 6)) < 0.45 or awake > 0.5
                if on:
                    point3(g, cam, (x, 300 - r_ * 210, z - 100), 9, GOLD if r_ % 3 else GOLDL, 0.7)
    # the servant: kneels facing the colossus and bows
    kn = (0, 440, -60)
    hip_h = (kn[0], kn[1] - 150 + 25 * bow, kn[2] - 90)
    chest_h = v_add(hip_h, (0, -150 * (1 - bow) - 60 * bow, 160 * bow))
    head_h = v_add(chest_h, (0, -90 * (1 - bow) - 15 * bow, 100 * bow + 12))
    j = {'head': head_h, 'neck': v_lerp(chest_h, head_h, 0.4), 'chest': chest_h, 'hip': hip_h,
         'ls': v_add(chest_h, (-70, 10, 0)), 'rs': v_add(chest_h, (70, 10, 0)),
         'lhip': v_add(hip_h, (-40, 0, 0)), 'rhip': v_add(hip_h, (40, 0, 0)),
         'lk': (kn[0] - 50, kn[1] - 15, kn[2]), 'rk': (kn[0] + 50, kn[1] - 15, kn[2]),
         'lf': (kn[0] - 50, kn[1] - 10, kn[2] - 200), 'rf': (kn[0] + 50, kn[1] - 10, kn[2] - 200)}
    j['lh'] = v_add(j['lk'], (-20, -30 * (1 - bow), 130 + 90 * bow)); j['rh'] = v_add(j['rk'], (20, -30 * (1 - bow), 130 + 90 * bow))
    j['le'] = v_add(v_lerp(j['ls'], j['lh'], 0.5), (-40, 0, 0)); j['re'] = v_add(v_lerp(j['rs'], j['rh'], 0.5), (40, 0, 0))
    P = CFaces()
    humanoid(P, (200, 190, 175), j, facing=1)
    P.draw(g, cam)
    # the visor's light falls on the servant: a cone of gold scan lines once awake
    if awake > 0.02:
        tip = v_add(head_h, (0, -10, 0))
        mid = v_lerp(vl, vr, 0.5)
        for k in range(5):
            off = ((k - 2) * 70, 0, 0)
            seg3(g, cam, mid, v_add(tip, off), GOLD, 1.8, (0.45 if k == 2 else 0.22) * awake)
        glow(g, cam, tip, 160, GOLD, 0.3 * awake)
    # light pool under the hovering hand
    if reach > 0.05:
        glow(g, cam, v_add(hands[0], (0, 120, 0)), 200, GOLD, 0.25 * reach)
    text3(g, cam, 'ROLE: SERVANT', v_add(head_h, (0, -170, 0)), 28, GOLD if t > tsv else DIM, 'mono', clamp((t - t0) * 3))
    g.flash = max(g.flash, 0.18 * math.exp(-max(0.0, t - tb) * 9) * (t > tb)); g.flash_c = GOLDL
    camc, c, r, u = capcam()
    lyric3x(g, camc, t, 4, v_add(c, v_mul(camc.u, -340)), r, u, 1650, 112, INK, {'servant': GOLD, 'boss': GOLD}, depth=40)


# ======================================================== SAFETY FENCES 117.14 - 119.05
FZ = [700.0, 1800.0, 2900.0, 4000.0]
HITS = [117.38, 117.75, 118.18, 118.62]
FLAB = ['RLHF', 'RED TEAM', 'EVALS', 'KILL SWITCH']
CY = -560.0
HR = 92.0
PW, PH_ = 1800.0, 1300.0


def _hexes():
    out = []
    dx = 1.5 * HR; dy = math.sqrt(3) * HR
    for i in range(-7, 8):
        for jn in range(0, 9):
            x = i * dx
            y = -jn * dy - (dy / 2 if i % 2 else 0) - 20
            if abs(x) > PW / 2 - HR * 0.5 or y < -PH_ + HR * 0.6:
                continue
            out.append((x, y, i, jn))
    return out


HEX = _hexes()
HEXV = [(HR * math.cos(math.pi * k / 3), HR * math.sin(math.pi * k / 3)) for k in range(6)]


def _cz(t):
    t0 = T0(37)
    ks = [(t0, -900.0)] + [(h, z) for h, z in zip(HITS, FZ)] + [(T0(38) + 0.05, 5600.0)]
    for (a, za), (b, zb) in zip(ks, ks[1:]):
        if t <= b:
            u = prog(t, a, b)
            return lerp(za, zb, u ** 1.5)
    return ks[-1][1]


def _az(t):
    # whip-pans around the cube on every impact: behind-left > behind-right > left > front-right > front
    tgt = [-0.55, 0.55, -0.95, 1.35, 2.75]
    a = tgt[0]
    for k, h in enumerate(HITS):
        a += (tgt[k + 1] - tgt[k]) * eio(prog(t, h - 0.04, h + 0.24))
    return a + 0.08 * math.sin(t * 2.3)


def s_fences(g, t, lt):
    t0 = T0(37); tE = T0(38)
    cz = _cz(t)
    hit = sum(math.exp(-(t - h) * 10) for h in HITS if t > h)
    a = _az(t)
    R = 1550
    cpos = (0.0, CY, cz)
    eye = (R * math.sin(a), CY - 330 + 60 * math.sin(t * 1.9), cz - R * math.cos(a))
    tgt = (0.0, CY + 40, cz + 450 * math.cos(a) * 0.6 + 200)
    cam = Cam3(shake_eye(eye, t, 6 + 50 * min(1.5, hit)), tgt, 62 + 4 * min(1.0, hit), 0.05 * math.sin(a) + 0.05 * min(1.0, hit))
    env(g, cam)
    floor(g, cam, 0.0, 200, 34, GRID2, 0.7, 0, cz + 800, fog=5000)
    # light lane along the floor
    seg3(g, cam, (0, -2, -1500), (0, -2, 7000), GOLDD, 3, 0.7, fog=6000)
    for k, fz in enumerate(FZ):
        e = t - HITS[k]
        broke = e > 0
        big = k == 3
        S = SFaces()
        # emitter pylons with gold rings
        for sx in (-1, 1):
            px = sx * (PW / 2 + 70)
            S.sbox((px, -PH_ / 2 - 40, fz), (90, PH_ + 80, 90), (44, 44, 41), None, amb=0.45)
            for q in range(6):
                S.sbox((px, -100 - q * 220, fz), (110, 18, 110), GOLD if not broke else (70, 60, 40), None, amb=0.6)
        S.draw(g, cam, fog=6500)
        # approach: the barrier ripples as the cube nears
        prox = clamp(1 - (fz - cz) / 900) if not broke else 0.0
        col = INK if big else GOLD
        if not broke:
            fill3(g, cam, [(-PW / 2, 0, fz), (PW / 2, 0, fz), (PW / 2, -PH_, fz), (-PW / 2, -PH_, fz)], col, 0.03 + 0.07 * prox)
            for (x, y, i, jn) in HEX:
                d = math.hypot(x, y - CY)
                rip = math.exp(-abs(d - (t * 1800) % 1600) / 120) * 0.4 + prox * math.exp(-d / 500)
                pts = [(x + vx, y + vy, fz) for vx, vy in HEXV]
                poly3(g, cam, pts, mix(col, GOLDL, clamp(rip)), 1.6 + 2 * clamp(rip), 0.55 + 0.45 * clamp(rip), closed=True, fog=6500)
            nxt = min([i for i, h in enumerate(HITS) if t <= h] or [9])
            if k == nxt:
                la = clamp((t - (HITS[k - 1] if k else T0(37))) / 0.12)
                text3(g, cam, 'SAFETY FENCE %02d' % (k + 1), (0, -PH_ - 150, fz), 40, DIM, 'mono', la)
                text3(g, cam, FLAB[k], (0, -PH_ - 70, fz), 70 if big else 58, col, 'monox', la)
        else:
            # shatter: hex shards burst outward from the impact point, tumbling and fading
            if e < 0.9:
                fade = 1 - clamp(e / 0.9)
                for (x, y, i, jn) in HEX:
                    d = math.hypot(x, y - CY)
                    dl = d / 4000
                    ee = max(0.0, e - dl)
                    dirx, diry = x / (d + 1), (y - CY) / (d + 1)
                    sp = (900 + 900 * hsh(i * 7, jn)) * (1.6 if big else 1.0)
                    cx = x + dirx * sp * ee * 0.8
                    cy_ = y + diry * sp * ee * 0.8 + 1600 * ee * ee
                    czz = fz + (1400 + 1600 * hsh(i, jn * 3)) * ee * (1.4 if big else 1.0)
                    rx, ry = 7 * hsh(i, jn + 1) * ee, 9 * hsh(i + 3, jn) * ee
                    sc = 0.85
                    pts = [v_add((cx, cy_, czz), rot3((vx * sc, vy * sc, 0), rx, ry, 0)) for vx, vy in HEXV]
                    fill3(g, cam, pts, col, 0.14 * fade)
                    poly3(g, cam, pts, GOLDL if hsh(i, jn) > 0.6 else col, 2, 0.9 * fade, closed=True, fog=6500)
            # impact ring
            if e < 0.5:
                rr = 300 + 2600 * eo(e / 0.5)
                poly3(g, cam, [(rr * math.cos(q * math.pi / 24), CY + rr * math.sin(q * math.pi / 24), fz) for q in range(49)], GOLDL, 4, 1 - e / 0.5)
            # the label tumbles away
            if e < 0.8:
                text3(g, cam, FLAB[k], (300 * (hsh(k, 2) - 0.5) * e * 4, -PH_ - 80 - 600 * e + 1800 * e * e, fz + 1500 * e), 52, col, 'monox', 1 - e / 0.8)
    # the gold cube ramming through, squashing on each hit
    C = SFaces()
    sq_ = 1.0 + 0.16 * min(1.0, hit)
    bob = 16 * math.sin(t * 9)
    C.sbox((0, 0, 0), (340 * sq_, 340 / sq_, 340 / sq_ / sq_ * sq_), GOLD, GOLDL, 2, xf=lambda v: v_add(rot3(v, t * 2.6, t * 1.8, 0.2), (0, CY + bob, cz)), amb=0.45)
    C.draw(g, cam)
    glow(g, cam, (0, CY + bob, cz), 300 + 350 * min(1.0, hit), GOLD, 0.25 + 0.3 * min(1.0, hit))
    for q in range(30):   # light trail
        p = ((hsh(q, 1) - 0.5) * 320, CY + (hsh(q, 2) - 0.5) * 320, cz - 220 - hsh(q, 3) * 1100)
        seg3(g, cam, p, v_add(p, (0, 0, -300)), GOLDL, 2, 0.4)
    g.flash = max(g.flash, 0.18 * max([math.exp(-(t - h) * 16) * (1.5 if i == 3 else 1) for i, h in enumerate(HITS) if t > h] or [0]))
    g.flash_c = GOLDL
    camc, c, r, u = capcam()
    lyric3x(g, camc, t, 37, v_add(c, v_mul(camc.u, 345)), r, u, 1500, 110, INK, {'safety': GOLD, 'fence': GOLD}, depth=40)


# ======================================================== HUNDRED THOUSAND GPU 119.05 - 120.82
# hierarchy on the floor plane (x, z): chip -> tray (4x2) -> pod (5x4 trays) -> hall (9x9 pods) -> campus (3x3 halls)
CP_ = 130.0; CS = 100.0
TPX, TPZ = 600.0, 340.0
PPX, PPZ = 3300.0, 1700.0
HPX, HPZ = 32000.0, 17500.0


def _grid(nx, nz, px, pz):
    xs = (np.arange(nx) - (nx - 1) / 2) * px
    zs = (np.arange(nz) - (nz - 1) / 2) * pz
    X, Z = np.meshgrid(xs, zs, indexing='ij')
    return np.stack([X.ravel(), Z.ravel()], 1)


def _build_gpu():
    halls = _grid(3, 3, HPX, HPZ)
    pods_l = _grid(9, 9, PPX, PPZ)
    trays_l = _grid(5, 4, TPX, TPZ)
    chips_l = _grid(4, 2, CP_, CP_)
    pods = (halls[:, None, :] + pods_l[None]).reshape(-1, 2)
    trays = (pods[:, None, :] + trays_l[None]).reshape(-1, 2)
    chips = (trays[:, None, :] + chips_l[None]).reshape(-1, 2)
    d = np.hypot(chips[:, 0], chips[:, 1])
    order = np.argsort(d, kind='stable')
    rank = np.empty(len(chips), np.int64); rank[order] = np.arange(len(chips))
    dsorted = d[order]
    return dict(halls=halls, pods=pods, trays=trays, chips=chips, rank=rank, dsorted=dsorted,
                c0=chips[order[0]].copy())


GPU = _build_gpu()
NCH = len(GPU['chips'])
LEV = [  # name, half x, half z, chips per element
    ('halls', 9 * PPX / 2 + 300, 9 * PPZ / 2 + 300, 8 * 20 * 81),
    ('pods', 5 * TPX / 2 + 60, 4 * TPZ / 2 + 60, 8 * 20),
    ('trays', 2 * CP_ + 20, CP_ + 20, 8),
    ('chips', CS / 2, CS / 2, 1),
]


def _proj(cam, P):
    d = P - np.array(cam.eye)
    x = d @ np.array(cam.r); y = d @ np.array(cam.u); z = d @ np.array(cam.f)
    zz = np.maximum(z, 1.0)
    k = cam.F / zz
    return cam.cx + x * k, cam.cy + y * k, z


def _gpu_D(t):
    t0 = T0(38); tE = T0(39)
    u = prog(t, t0 - 0.02, 120.2)
    w = 1 - (1 - u) ** 2.2
    D = math.exp(lerp(math.log(170.0), math.log(85000.0), w)) * (1 + 0.12 * smooth(prog(t, 120.2, tE)))
    return D


def s_gpu(g, t, lt):
    t0 = T0(38); tg = WT(38, 2); tE = T0(39)
    D = _gpu_D(t)
    bt = beats(t0 - 0.5, t + 0.001)
    lb = bt[-1] if bt else t0
    pb = math.exp(-(t - lb) * 8)
    D *= 1 - 0.035 * pb
    u = prog(t, t0, tE)
    yaw = 0.25 + 0.95 * smooth(u)
    pitch = lerp(1.22, 0.55, smooth(prog(t, t0, 120.4)))
    c0 = GPU['c0']
    tg3 = (float(c0[0]) * (1 - smooth(u)), 0.0, float(c0[1]) * (1 - smooth(u)))
    eye = orbit(tg3, D, yaw, pitch)
    cam = Cam3(eye, tg3, 55, 0.04 * math.sin(t * 1.7))
    env(g, cam)
    # lit radius grows with the view; the counter is the number of GPUs inside it
    Rl = 0.62 * D * (1 + 0.4 * prog(t, 119.9, 120.25)) + 60
    n = int(np.searchsorted(GPU['dsorted'], Rl))
    if t > 120.25:
        n = NCH
    wave_r = (t - lb) * 3.2 * D
    rank = GPU['rank']
    fine_alpha_prev = None
    eyev = np.array(eye)
    for li, (name, hx, hz, per) in enumerate(LEV):
        C = GPU[name]
        dd = np.hypot(C[:, 0] - tg3[0], C[:, 1] - tg3[2])
        sel = np.nonzero(dd < 3.2 * D + 4 * hx)[0]
        if len(sel) == 0:
            continue
        P3 = np.stack([C[sel, 0], np.zeros(len(sel)), C[sel, 1]], 1)
        sx, sy, sz = _proj(cam, P3)
        px = 2 * hx * cam.F / np.maximum(sz, 1.0)
        thr = 26.0 if name == 'chips' else 14.0
        ok = (sz > 50) & (px > thr) & (sx > -px) & (sx < W + px) & (sy > -px) & (sy < H + px)
        # fog by depth relative to view distance
        sel = sel[ok]; px = px[ok]; sz = sz[ok]
        if len(sel) > 4000:
            o = np.argsort(sz)[:4000]; sel = sel[o]; px = px[o]; sz = sz[o]
        if len(sel) == 0:
            continue
        # lit fraction per element
        if name == 'chips':
            lit = (rank[sel] < n).astype(float)
        else:
            k = {'halls': 8 * 20 * 81, 'pods': 160, 'trays': 8}[name]
            # chips of element e are contiguous: [e*k, (e+1)*k)
            idx = sel[:, None] * k + np.arange(0, k, max(1, k // 16))[None]
            lit = (rank[idx] < n).mean(1)
        # how much the next-finer level covers this element (fade our fill as children appear)
        child = 0.0
        if li < 3:
            ratio = LEV[li + 1][1] / hx
            cpx = px * ratio
            cthr = 26.0 if LEV[li + 1][0] == 'chips' else 14.0
            child = np.clip((cpx - cthr) / (cthr * 1.2), 0, 1)
        else:
            child = np.zeros(len(sel))
        a_in = np.clip((px - thr) / thr, 0, 1)
        fogk = np.clip(1.0 - (sz - 1.6 * D) / (2.4 * D), 0.0, 1.0)
        for m in range(len(sel)):
            e = sel[m]
            cx, cz = C[e, 0], C[e, 1]
            al = float(a_in[m] * fogk[m])
            if al < 0.02:
                continue
            q = [(cx - hx, 0, cz - hz), (cx + hx, 0, cz - hz), (cx + hx, 0, cz + hz), (cx - hx, 0, cz + hz)]
            dist = math.hypot(cx - tg3[0], cz - tg3[2])
            wv = math.exp(-abs(dist - wave_r) / (0.12 * D)) * pb
            fl = float(lit[m])
            fillc = mix(mix((34, 33, 30), GOLD, fl), GOLDL, clamp(wv * fl))
            fa = (1 - float(child[m])) * al
            if name == 'chips':
                fill3(g, cam, q, (40, 40, 37), al)
                dh = 32
                dq = [(cx - dh, 0, cz - dh), (cx + dh, 0, cz - dh), (cx + dh, 0, cz + dh), (cx - dh, 0, cz + dh)]
                fill3(g, cam, dq, fillc if fl > 0 else (72, 72, 66), al)
                if px[m] > 70:
                    for s_ in (-1, 1):
                        for r_ in (-1, 0, 1):
                            hb = (cx + s_ * 42, 0, cz + r_ * 26)
                            fill3(g, cam, [(hb[0] - 6, 0, hb[2] - 10), (hb[0] + 6, 0, hb[2] - 10), (hb[0] + 6, 0, hb[2] + 10), (hb[0] - 6, 0, hb[2] + 10)], (96, 96, 90), al)
                    poly3(g, cam, q + [q[0]], GOLDD, 1.5, al)
                if fl > 0 and px[m] > 40:
                    glow(g, cam, (cx, -4, cz), 55, GOLD, 0.35 * al)
            else:
                if fa > 0.02:
                    fill3(g, cam, q, fillc, 0.85 * fa)
                poly3(g, cam, q + [q[0]], GOLD if name == 'halls' else GOLDD, 2.5 if name == 'halls' else 1.4, 0.8 * al)
                if name == 'halls' and px[m] > 40:
                    text3(g, cam, 'HALL %02d' % (e + 1), (cx, -200, cz - hz - 1200), 34, GOLD, 'mono', al)
    # the land around the campus: a faint survey grid, power lines running in with pulses, heat columns over halls
    far = clamp((D - 8000) / 20000)
    if far > 0:
        st = 8000.0
        for k in range(-8, 9):
            seg3(g, cam, (k * st, 0, -8 * st), (k * st, 0, 8 * st), GRID2, 1.2, 0.6 * far, fog=0, wscale=False)
            seg3(g, cam, (-8 * st, 0, k * st), (8 * st, 0, k * st), GRID2, 1.2, 0.6 * far, fog=0, wscale=False)
        for k, (ax, az_) in enumerate(((1, 0.2), (-1, 0.5), (0.3, 1), (-0.4, -1), (1, -0.7), (-1, -0.3))):
            dv = v_norm((ax, 0, az_))
            p0 = (dv[0] * 52000, 0, dv[2] * 30000); p1 = (dv[0] * 75000, 0, dv[2] * 75000)
            seg3(g, cam, p0, p1, GOLDD, 2, 0.8 * far, wscale=False)
            ph = ((t - lb) * 1.6 + k * 0.13) % 1.0
            glow(g, cam, v_lerp(p1, p0, ph), 2600, GOLD, 0.7 * far)
        for e in range(9):
            hc = GPU['halls'][e]
            for q in range(5):
                hh = ((t * 0.7 + q * 0.2 + e * 0.11) % 1.0)
                point3(g, cam, (hc[0] + 3000 * math.sin(q * 2 + e), -hh * 26000, hc[1] + 2000 * math.cos(q * 3 + e)), 9, GOLD, 0.45 * far * (1 - hh))
    # heat shimmer rising off the lit region
    for i in range(70):
        rr = Rl * math.sqrt(hsh(i, 1)); a = hsh(i, 2) * 6.283
        hgt = ((t * 0.9 + hsh(i, 3)) % 1.0)
        p = (tg3[0] + rr * math.cos(a), -hgt * 0.35 * D, tg3[2] + rr * math.sin(a))
        point3(g, cam, p, 4, GOLD, 0.5 * (1 - hgt))
    if t < t0 + 0.25:
        g.flash = max(g.flash, 0.2 * (1 - prog(t, t0, t0 + 0.25))); g.flash_c = GOLDL
    shown = min(100000, n)
    camc, c, r, uu = capcam()
    word3(g, camc, 'H100 \u00d7 %s' % format(shown, ','), v_add(c, v_mul(camc.u, -150)), r, uu, 820 + 120 * pb * (t > tg), 200, GOLD, 'monox', 1, x=True, depth=60, n=6)
    lyric3x(g, camc, t, 38, v_add(c, v_mul(camc.u, -345)), r, uu, 1500, 115, INK, {'gpu': GOLD, 'thousand': GOLD}, depth=40)
