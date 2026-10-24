"""Solid 3D eye (v6): glossy sclera, gold circuit-fibre iris, real eyelids.
Shared by the 'Sparks of AGI' and 'nervous' scenes. Front pole of the eye sits at the origin, looking -z."""
import math
from cam3d import *

R = 560.0
C = (0.0, 0.0, R)
TH_I = 0.55      # iris angular radius
TH_P = 0.17      # pupil angular radius (at dil = 1)
SCLERA = (226, 224, 216)
SKIN = (62, 59, 54)


def _basis(yaw, pitch):
    d = (math.sin(yaw) * math.cos(pitch), math.sin(pitch), -math.cos(yaw) * math.cos(pitch))
    ref = (0, 1, 0)
    e1 = v_norm(v_cross(ref, d))
    e2 = v_cross(d, e1)
    return d, e1, e2


def _sp(B, th, ph, rr=R):
    d, e1, e2 = B
    s = math.sin(th)
    v = v_add(v_mul(d, math.cos(th)), v_add(v_mul(e1, s * math.cos(ph)), v_mul(e2, s * math.sin(ph))))
    return v_add(C, v_mul(v, rr))


def gaze_xf(yaw, pitch):
    """rotation of the whole eye (lids included) about its centre so it turns to look"""
    d, e1, e2 = _basis(yaw, pitch)
    def X(p):
        v = v_sub(p, C)
        return v_add(C, v_add(v_add(v_mul(e1, -v[0]), v_mul(e2, v[1])), v_mul(d, -v[2])))
    return X


def _lid_pt(lat, lon, rr):
    la, lo = math.radians(lat), math.radians(lon)
    return (rr * math.cos(la) * math.sin(lo), -rr * math.sin(la), C[2] - rr * math.cos(la) * math.cos(lo))


def _edge(base, lon, meet=0.0):
    k = min(1.0, abs(lon) / 72.0)
    return lerp(base, meet, k ** 1.8)


def draw_eye(g, cam, t, yaw=0.0, pitch=0.0, lid_u=34.0, lid_l=-30.0, dil=1.0, glitch=0.0, wave=0.0, flux=0.3, lid_follow=0.0):
    """lid_u / lid_l: latitude (deg) of the upper / lower lid edge at the centre (0 = closed)."""
    B = _basis(yaw, pitch)
    # sclera
    S = SFaces()
    Xg = gaze_xf(yaw, pitch)
    S.sphere(C, R, SCLERA, None, 18, 36, amb=0.32, xf=lambda v: v_sub(Xg(v_add(C, v)), C))
    S.draw(g, cam)
    # faint gold capillary traces on the white
    for i in range(18):
        ph = 2 * math.pi * i / 18 + hsh(i, 21) * 0.3
        th = TH_I + 0.02
        pts = [_sp(B, th, ph, R + 2)]
        for s in range(4):
            th += 0.08 + 0.06 * hsh(i, s + 30)
            pts.append(_sp(B, th, ph, R + 2))
            ph += (hsh(i, s + 40) - 0.5) * 0.25
            pts.append(_sp(B, th, ph, R + 2))
        on = hsh(i, 22) < 0.25 + 0.6 * glitch * hsh(i, int(t * 20))
        poly3(g, cam, pts, GOLD if on else (176, 160, 120), 1.6, 0.55 + 0.4 * on)
        point3(g, cam, pts[-1], 4, GOLD if on else (176, 160, 120), 0.8)
    # iris base and limbus
    ring = lambda th, rr=R + 3, n=64: [_sp(B, th, 2 * math.pi * q / n, rr) for q in range(n)]
    fill3(g, cam, ring(TH_I), (30, 24, 12), 1.0)
    fill3(g, cam, ring(TH_I * 0.82), (60, 44, 14), 1.0)
    # radial fibres
    tp = TH_P * dil
    for i in range(170):
        ph0 = 2 * math.pi * i / 170 + hsh(i, 1) * 0.02
        bend = (hsh(i, 2) - 0.5) * 0.35
        th0 = tp * 1.08
        th1 = TH_I * (0.86 + 0.12 * hsh(i, 3))
        pts = [_sp(B, lerp(th0, th1, q / 6), ph0 + bend * math.sin(q / 6 * math.pi), R + 4) for q in range(7)]
        lv = hsh(i, 4)
        w8 = math.exp(-((wave * 8 - (i % 8)) ** 2) * 0.6)
        col = GOLDL if lv > 0.82 else (GOLD if lv > 0.4 else GOLDD)
        if glitch > 0 and hsh(i, int(t * 24)) < 0.15 * glitch:
            col = INK
        poly3(g, cam, pts, col, 1.8, 0.55 + 0.45 * max(w8, lv))
    # collarette circuit rings (dashed, counter-rotating)
    for k, (th, sp, c) in enumerate(((tp * 1.6 + 0.04, 0.4, GOLDL), (TH_I * 0.62, -0.25, GOLD), (TH_I * 0.93, 0.15, GOLDD))):
        segs = 9 + k * 4
        for sgi in range(segs):
            a0 = 2 * math.pi * sgi / segs + t * sp + k
            a1 = a0 + 2 * math.pi / segs * (0.5 + 0.3 * hsh(k, sgi))
            poly3(g, cam, [_sp(B, th, a0 + (a1 - a0) * q / 8, R + 5) for q in range(9)], c, 2.4, 0.9)
        for sgi in range(segs):
            if hsh(k + 9, sgi) < 0.5:
                point3(g, cam, _sp(B, th, 2 * math.pi * sgi / segs + t * sp + k, R + 6), 4, c, 0.9)
    poly3(g, cam, ring(TH_I, R + 5, 72), (14, 12, 8), 6, 1.0, True)
    # pupil
    fill3(g, cam, ring(tp, R + 6, 40), (6, 6, 6), 1.0, stroke=GOLD, w=2.5)
    # cornea gloss
    hl = v_add(C, v_mul(v_norm(v_add(B[0], (-0.28, -0.32, 0))), R + 30))
    point3(g, cam, hl, 46, (255, 255, 250), 0.22)
    point3(g, cam, hl, 14, (255, 255, 250), 0.85)
    point3(g, cam, v_add(C, v_mul(v_norm(v_add(B[0], (0.2, 0.22, 0))), R + 30)), 6, (255, 255, 250), 0.5)
    # lids stay fixed on the head; only the eyeball (white + iris + pupil) turns inside them
    # lid_follow=1 turns the whole eye (lids too) to look; 0 keeps the lids fixed and turns only the eyeball
    if lid_follow > 0.001:
        X = gaze_xf(yaw * lid_follow, pitch * lid_follow)
    else:
        X = lambda p: p
    LP = lambda la, lo, rr: X(_lid_pt(la, lo, rr))
    # eyelids: armoured shutter lids. Each lid is 4 overlapping curved plates of dark gunmetal,
    # the plate nearest the opening on top, gold-trimmed leading edges, staggered panel seams, rivets.
    eye_p = cam.eye
    front = lambda p: v_dot(v_sub(p, C), v_sub(eye_p, p)) > 0

    def vis(pts):
        c = v_mul(v_add(v_add(pts[0], pts[1]), v_add(pts[2], pts[-1])), 0.25)
        return front(c)

    NL = 64
    NP = 4
    lons = [-180 + 360 * j / NL for j in range(NL + 1)]
    PL = [(34, 32, 29), (26, 25, 23), (21, 20, 19), (17, 17, 16)]
    Lf = SFaces()
    trims = []
    for upper in (True, False):
        base = lid_u if upper else lid_l
        top = 89.0 if upper else -89.0
        sg = 1 if upper else -1
        for k in range(NP):
            rk = R * 1.05 + (NP - k) * 7.0
            f0, f1 = k / NP, min(1.0, (k + 1) / NP + 0.07)
            rows = []
            for i in range(4):
                f = lerp(f0, f1, i / 3)
                rows.append([LP(lerp(_edge(base, lo, 0.0), top, f ** 1.15), lo, rk) for lo in lons])
            for i in range(3):
                for j in range(NL):
                    q = [rows[i][j], rows[i][j + 1], rows[i + 1][j + 1], rows[i + 1][j]]
                    if vis(q):
                        col = shade_col(q, PL[k], 0.30)
                        Lf.sq(q, PL[k], col, 1.4, amb=0.30)
            # thick rolled leading edge on every plate (the first one is the lid margin)
            lead = [LP(lerp(_edge(base, lo, 0.0), top, f0 ** 1.15), lo, rk + 2) for lo in lons if abs(lo) <= 84]
            th = 13 if k == 0 else 7
            for m in range(len(lead) - 1):
                if front(lead[m]):
                    Lf.tube([lead[m], lead[m + 1]], th, (46, 43, 38) if k == 0 else PL[k], None, 6, amb=0.35)
            trims.append((k, upper, lead, rk, base, top, f0))
    Lf.draw(g, cam)
    for k, upper, lead, rk, base, top, f0 in trims:
        sg = 1 if upper else -1
        # contact shadow cast by this plate's edge onto the plate below, then the gold trim line
        if k > 0:
            sh = [LP(lerp(_edge(base, lo, 0.0), top, f0 ** 1.15) + sg * 1.6, lo, rk + 1) for lo in lons if abs(lo) <= 84]
            seg = [p for p in sh if front(p)]
            if len(seg) > 1:
                poly3(g, cam, seg, (4, 4, 4), 9.0, 0.8)
        tr = [p for p in lead if front(p)]
        if len(tr) > 1:
            poly3(g, cam, [v_add(p, (0, -sg * 0.0, 0)) for p in tr], GOLD if k == 0 else GOLDD, 3.0 if k == 0 else 2.0, 1.0 if k == 0 else 0.85)
        # specular band across the plate
        hb = [LP(lerp(_edge(base, lo, 0.0), top, (f0 + 0.11) ** 1.15), lo, rk + 3) for lo in lons if -60 <= lo <= 20]
        seg = [p for p in hb if front(p)]
        if len(seg) > 1 and upper:
            poly3(g, cam, seg, (225, 220, 208), 10.0, 0.06 + 0.03 * (3 - k))
            poly3(g, cam, seg, (240, 236, 226), 1.8, 0.3)
        # panel seams, staggered per plate, with a rivet at each end
        f1 = min(1.0, (k + 1) / 4.0)
        for s_ in range(-3, 4):
            lo = s_ * 22.0 + (11.0 if k % 2 else 0.0)
            if abs(lo) > 70:
                continue
            la0 = lerp(_edge(base, lo, 0.0), top, (f0 + 0.03) ** 1.15)
            la1 = lerp(_edge(base, lo, 0.0), top, (f1 - 0.01) ** 1.15)
            p0, p1 = LP(la0, lo, rk + 2), LP(la1, lo, rk + 2)
            if front(p0) and front(p1):
                poly3(g, cam, [p0, LP((la0 + la1) / 2, lo, rk + 2), p1], (14, 14, 13), 2.0, 0.8)
                poly3(g, cam, [v_add(p0, (2.5, 0, 0)), v_add(p1, (2.5, 0, 0))], (120, 114, 104), 1.0, 0.35)
                for pp in (LP(la0 + sg * 2.5, lo + 3, rk + 4), LP(la0 + sg * 2.5, lo - 3, rk + 4)):
                    point3(g, cam, pp, 3.2, (24, 23, 21), 1.0)
                    point3(g, cam, v_add(pp, (-0.8, -0.8, 0)), 1.6, GOLDL if k == 0 else (150, 140, 120), 0.9)
    # glowing seal where the lids meet the eyeball
    for upper in (True, False):
        e0 = [(lo, _edge(lid_u if upper else lid_l, lo, 0.0)) for lo in lons if abs(lo) <= 80]
        seg = [LP(la, lo, R * 1.05 + 30) for lo, la in e0]
        seg = [p for p in seg if front(p)]
        if len(seg) > 1:
            poly3(g, cam, seg, GOLD, 5.0, 0.18)
            poly3(g, cam, seg, GOLDL, 1.2, 0.8)


def blink(t, times, dur=0.07):
    """0 = open, 1 = shut"""
    v = 0.0
    for tb in times:
        v = max(v, math.exp(-((t - tb) / dur) ** 2))
    return v


def look_at_cam(cam, k=1.0, ymax=0.6, pmax=0.35):
    e = cam.eye
    dz = C[2] - e[2]
    yaw = math.atan2(e[0], max(1.0, dz))
    pitch = math.atan2(e[1], math.hypot(e[0], max(1.0, dz)))
    return clamp(yaw * k, -ymax, ymax), clamp(pitch * k, -pmax, pmax)
