"""v3 scenes 0:38.6 - 1:42.5"""
import math
from cam3d import *
from s3a import T0, T1, WT
from s3b import s_train, s_accel, s_nvda, s_omega, s_flops, s_turn, s_kill, MSGS, FACES_G, VN, _clip
from s4a import type_scene, _panels, EXPL

STEEL = (120, 120, 114)
SKIN = (200, 198, 190)


def humanoid(F, base, pose, facing=-1):
    """v87: every humanoid is now the detailed person model (person.py, from the v86 Chinese-room operator)"""
    from person import person
    person(F, pose, facing)


def _pose(o, s=1.0, arms_up=0.0, kick=0.0, t=0.0, reach=None):
    x, y, z = o
    P = lambda dx, dy, dz=0: (x + dx * s, y + dy * s, z + dz * s)
    j = {'head': P(0, -330), 'neck': P(0, -270), 'chest': P(0, -200), 'hip': P(0, -40),
         'ls': P(-70, -250), 'rs': P(70, -250), 'lhip': P(-40, -30), 'rhip': P(40, -30)}
    k1 = math.sin(t * 9) * kick; k2 = math.sin(t * 9 + 2) * kick
    j['lk'] = P(-45 + 30 * k1, 90, 30 * k1); j['lf'] = P(-50 + 60 * k1, 220, 60 * k1)
    j['rk'] = P(45 - 30 * k2, 90, -30 * k2); j['rf'] = P(50 - 60 * k2, 220, -60 * k2)
    if reach is not None:
        j['lh'], j['rh'] = reach
        j['le'] = v_lerp(j['ls'], j['lh'], 0.5); j['re'] = v_lerp(j['rs'], j['rh'], 0.5)
        j['le'] = (j['le'][0] - 30 * s, j['le'][1] + 20 * s, j['le'][2])
        j['re'] = (j['re'][0] + 30 * s, j['re'][1] + 20 * s, j['re'][2])
    else:
        up = arms_up
        j['le'] = P(-110, lerp(-130, -360, up)); j['lh'] = P(-120, lerp(-20, -470, up))
        j['re'] = P(110, lerp(-130, -360, up)); j['rh'] = P(120, lerp(-20, -470, up))
    return j



class CFaces(SFaces):
    """v71: SFaces with back-face culling for convex primitives (each face remembers its primitive's centre),
    so far-side faces can no longer be painted over near ones."""
    cur = None

    def sq(self, pts, base, stroke=None, w=1.2, al=1.0, amb=0.22):
        self.f.append((pts, stroke, shade_col(pts, base, amb), w, al, self.cur))

    def _with(self, c, fn, *a, **k):
        old = self.cur; self.cur = c
        try:
            return fn(*a, **k)
        finally:
            self.cur = old

    def sphere(self, c, *a, **k):
        return self._with(c, SFaces.sphere, self, c, *a, **k)

    def cyl(self, c, *a, **k):
        return self._with(c, SFaces.cyl, self, c, *a, **k)

    def sbox(self, c, *a, **k):
        return self._with(c, SFaces.sbox, self, c, *a, **k)

    def tube(self, pts, *a, **k):
        m = len(pts)
        c = (sum(p[0] for p in pts) / m, sum(p[1] for p in pts) / m, sum(p[2] for p in pts) / m)
        if math.dist(pts[0], pts[-1]) < 1e-6:
            c = None   # closed loop (ring): no culling
        return self._with(c, SFaces.tube, self, pts, *a, **k)

    def draw(self, g, cam, fog=0.0):
        items = []
        for f in self.f:
            pts, st, fc, w, al = f[:5]
            cen = f[5] if len(f) > 5 else None
            if cen is not None and len(pts) >= 3:
                n = v_cross(v_sub(pts[1], pts[0]), v_sub(pts[2], pts[0]))
                if v_dot(n, n) > 1e-9:
                    fcn = (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts), sum(p[2] for p in pts) / len(pts))
                    if v_dot(n, v_sub(fcn, cen)) < 0:
                        n = v_mul(n, -1)
                    if v_dot(n, v_sub(cam.eye, fcn)) < 0:
                        continue
            cs = [cam.cs(p) for p in pts]
            if min(c[2] for c in cs) < NEAR:
                continue
            z = sum(c[2] for c in cs) / len(cs)
            items.append((z, [cam.ps(c) for c in cs], st, fc, w, al))
        items.sort(key=lambda r: -r[0])
        for z, pp, st, fc, w, al in items:
            flat = []
            for q in pp:
                flat += [q[0], q[1]]
            if max(flat[0::2]) < -100 or min(flat[0::2]) > W + 100:
                continue
            ww = w * clamp(1000.0 / z, 0.4, 3.0)
            g.poly(flat, fill=fc, stroke=st, w=ww, a=al, fa=al if fc is not None else None)



# ======================================================== v72: SHARP LEFT TURN overhaul (81.23 - 89.99)
# night drive on a solid road: brake hard into a chevron-lined hairpin, the entity rises at the end of the road
# ("there you are"), then the car rolls under a highway gantry whose CDR checklist gets struck through.
def _road2(s):
    R = 500.0
    if s < 2600:
        return (0.0, 0.0, s), 0.0
    if s - 2600 < R * math.pi / 2:
        a = (s - 2600) / R
        return (-(R - R * math.cos(a)), 0.0, 2600 + R * math.sin(a)), a
    d = s - 2600 - R * math.pi / 2
    return (-R - d, 0.0, 2600 + R), math.pi / 2


def _rp(s, off, y=0.0):
    p, a = _road2(s)
    return (p[0] + off * math.cos(a), y, p[2] + off * math.sin(a))   # right-hand side = (cos a, 0, sin a)


def _turn_s(t):
    tA = T0(25) - 0.01; tt = WT(25, 2); tEnd = T0(27) - 0.01
    if t < tt:
        m = 1 - clamp((t - tA) / (tt - tA))
        return 2600 - 500 * m - 1300 * m * m          # fast approach, braking into the turn
    u = t - tt; D = tEnd - tt
    return 2600 + 650 * u - 0.5 * (479.0 / D) * u * u


_TURN_ENT = (-6400.0, -380.0, 3100.0)   # v80: v74 position (centre of the road end, under the gantry), v76 scale
_TURN_K = 3.6   # v81: v74 size
_TPOINT = [None]
def _turn_tpoint():
    """first time the car's heading points within 4 deg of the entity (the decloak moment)"""
    if _TPOINT[0] is None:
        t = T0(25)
        while t < T0(27):
            s = _turn_s(t); p, a = _road2(s); q, _ = _road2(s + 420)
            f = v_norm((q[0] - p[0], 0, q[2] - p[2])); d = v_norm((_TURN_ENT[0] - p[0], 0, _TURN_ENT[2] - p[2]))
            if v_dot(f, d) > math.cos(math.radians(4)):
                break
            t += 1 / 120
        _TPOINT[0] = t
    return _TPOINT[0]


def _cloak_composite(g, layer, t, reveal, occ=None):
    """Predator-style active camouflage: the entity layer (drawn on black) bends the background behind it like a
    lens (refraction from the blurred silhouette + travelling ripples, faint rim), then a ragged shimmering front
    sweeps across it and the real entity shows through. No brightness spike."""
    import numpy as np
    from scipy.ndimage import gaussian_filter, map_coordinates
    from PIL import Image
    g.d.flush()
    bg = np.asarray(g.img).astype(np.float32)
    ent = np.asarray(layer.done()).astype(np.float32)
    if occ is not None:
        # v83: anything nearer than the entity (road surface, guardrail, posts, boards) hides it
        om = np.clip(np.asarray(occ.done()).astype(np.float32).max(axis=2) / 6.0, 0, 1)
        ent = ent * (1 - om[..., None])
    lum = ent.max(axis=2)
    if lum.max() < 4:
        return
    ys, xs = np.nonzero(lum > 4)
    pad = 48
    y0, y1 = max(0, ys.min() - pad), min(H, ys.max() + pad + 1)
    x0, x1 = max(0, xs.min() - pad), min(W, xs.max() + pad + 1)
    B = bg[y0:y1, x0:x1]; Ee = ent[y0:y1, x0:x1]; Lm = lum[y0:y1, x0:x1]
    hh, ww = Lm.shape
    alpha = np.clip(Lm / 70.0, 0, 1)
    sil = gaussian_filter(np.clip(Lm / 25.0, 0, 1), 9)          # soft silhouette = lens thickness
    sil = np.clip(sil * 2.2, 0, 1)
    gy, gx = np.gradient(sil)
    yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
    X = xx + x0; Y = yy + y0
    rip = np.sin(X * 0.045 + t * 7.0) * np.cos(Y * 0.05 - t * 5.3) + 0.6 * np.sin((X + Y) * 0.021 - t * 3.1)
    amp = 60.0
    dx = np.clip(-gx * amp * 9, -12, 12) + rip * 4.0 * sil
    dy = np.clip(-gy * amp * 9, -12, 12) + np.cos(X * 0.03 - t * 6.1) * 3.0 * sil
    cloak = np.empty_like(B)
    for c in range(3):
        cloak[..., c] = map_coordinates(B[..., c], [yy + dy, xx + dx], order=1, mode='nearest')
    s2 = gaussian_filter(np.clip(Lm / 25.0, 0, 1), 3)
    ey, ex = np.gradient(s2)
    edge = np.clip(np.hypot(ex, ey) * 6.0, 0, 1) * (0.6 + 0.4 * np.sin(Y * 0.12 + X * 0.05 + t * 9))
    cloak = cloak + edge[..., None] * np.array([150, 150, 140], np.float32) * 0.2
    vis = B * (1 - alpha[..., None]) + Ee
    vis = np.minimum(vis, 255)
    if reveal <= 0:
        rv = np.zeros_like(sil)
    elif reveal >= 1:
        rv = np.ones_like(sil)
    else:
        # v76: a quick soft fade with a slight right-to-left lead and shimmering grain, never a hard edge
        n = 0.5 + 0.25 * np.sin(Y * 0.09 + t * 11) + 0.25 * np.sin(Y * 0.023 - X * 0.01 + t * 4)
        off = 0.22 * (1 - xx / max(1, ww - 1)) + 0.12 * n
        rv = np.clip((reveal - off) / 0.66, 0, 1)
        rv = rv * rv * (3 - 2 * rv)
        band = np.clip(1 - np.abs(rv - 0.5) * 2, 0, 1) * sil
        vis = vis + 0.6 * band[..., None] * np.array([40, 34, 18], np.float32) * (0.5 + 0.5 * np.sin(Y * 0.7 + t * 40))[..., None]
    out = cloak * (1 - rv[..., None]) + vis * rv[..., None]
    full = bg.copy(); full[y0:y1, x0:x1] = np.clip(out, 0, 255)
    g.img.paste(Image.fromarray(full.astype(np.uint8)))
    import aggdraw
    g.d = aggdraw.Draw(g.img)


def _shoggoth_body(g, cam, t, e, wide):
    """the s4a.s_shoggoth4 entity without mask/labels: eye-owned tentacles carrying gold pulses, core cloud, shinigami eyes"""
    from s4a import TENT, EYE_POS, _tent, _eye_basis, _shini_eye2
    bases = {}
    for j, c in enumerate(EYE_POS):
        r, u, f = _eye_basis(c, cam, k=0.0)
        for i in range(len(TENT)):
            if i % 3 == j:
                a = TENT[i][0]
                bases[i] = v_add(c, v_add(v_mul(r, 150 * clamp(e * 1.8) * math.cos(a)), v_mul(u, 150 * clamp(e * 1.8) * math.sin(a))))
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
                point3(g, cam, v_lerp(pts[k0], pts[min(24, k0 + 1)], fr), 10 * e, GOLDL, 0.9 * e)
    for i in range(380):
        th = hsh(i, 5) * 2 * math.pi; ph = math.acos(2 * hsh(i, 6) - 1)
        rr = 330 * (0.85 + 0.25 * math.sin(t * 3 + i))
        point3(g, cam, (rr * math.sin(ph) * math.cos(th), rr * math.cos(ph), rr * math.sin(ph) * math.sin(th) + 200), 3, INK, 0.6)
    for j, c in enumerate(EYE_POS):
        _shini_eye2(g, cam, t, c, 122, e, wide, 0.0, j)


def s_turn(g, t, lt):
    s = _turn_s(t)
    p, a = _road2(s)
    q, a2 = _road2(s + 420)
    turning = 2600 < s < 2600 + 500 * math.pi / 2
    bank = -0.5 * math.sin(clamp((s - 2600) / (500 * math.pi / 2 + 250)) * math.pi) if s > 2600 else 0.0
    eye = (p[0], -170, p[2])
    ty = lerp(-125, -300, eio(prog(s, 2600, 2600 + 500 * math.pi / 2 + 400)))   # look up the road toward the entity after the bend
    eye_s = shake_eye(eye, t, 14 if turning else 3); tgt = (q[0], ty, q[2])
    cam = Cam3(eye_s, tgt, 64, bank)
    env(g, cam, 0, fog=6000)
    s0 = max(0, int(s // 60) * 60 - 240)
    S1 = 2600 + 500 * math.pi / 2 + 4600
    # --- road surface (ground pass, far to near)
    strips = list(range(s0, int(min(S1, s + 5200)), 60))
    for k in reversed(strips):
        A0, B0 = _rp(k, -165), _rp(k, 165); A1, B1 = _rp(k + 60, -165), _rp(k + 60, 165)
        pts = [cam.p(v) for v in (A0, B0, B1, A1)]
        if any(v is None for v in pts):
            continue
        dz = math.dist(_road2(k)[0], p[0:1] + (0.0,) + p[2:3])
        fa = clamp(1 - (dz - 800) / 5000)
        flat = []
        for v in pts:
            flat += [v[0], v[1]]
        g.poly(flat, fill=(30, 30, 29), a=fa, fa=fa)
    # headlight pools on the asphalt
    for k in range(3):
        L_ = 900 - k * 250
        tri = [cam.p(_rp(s + 120, -40)), cam.p(_rp(s + 120 + L_, -200 + k * 30)), cam.p(_rp(s + 120 + L_, 200 - k * 30)), cam.p(_rp(s + 120, 40))]
        if all(v is not None for v in tri):
            flat = []
            for v in tri:
                flat += [v[0], v[1]]
            g.poly(flat, fill=GOLDL, a=0.035, fa=0.035)
    # lane dashes + gold edge lines
    for k in range((s0 // 240) * 240, int(min(S1, s + 5200)), 240):
        seg3(g, cam, _rp(k, 0, -1), _rp(k + 110, 0, -1), INK, 5, 0.85, fog=5000)
    for off in (-160, 160):
        poly3(g, cam, [_rp(k, off, -1) for k in range(s0, int(min(S1, s + 6000)), 50)], GOLD, 4, 1, fog=6000)
    F = CFaces()
    # guardrail on the outside (right) with posts and reflectors
    for k in range(s0 - s0 % 120, int(min(S1, s + 4200)), 120):
        P0 = _rp(k, 230)
        F.sbox((P0[0], -45, P0[2]), (16, 90, 16), (70, 70, 66), None, amb=0.4)
        A_, B_ = _rp(k, 222, -95), _rp(k + 120, 222, -95)
        F.sq([A_, B_, v_add(B_, (0, 30, 0)), v_add(A_, (0, 30, 0))], (96, 95, 90), None, amb=0.45)
        point3(g, cam, _rp(k, 214, -82), 5, GOLD, 0.8)
    # chevron boards around the outside of the hairpin, lighting up as the car passes
    for k in range(10):
        sk = 2560 + k * 90
        P0 = _rp(sk, 300)
        _, ak = _road2(sk)
        lit = clamp(1 - abs(s - sk) / 700)
        F.sbox((P0[0], -60, P0[2]), (14, 120, 14), (60, 60, 56), None, amb=0.4)
        rtk = (math.cos(ak), 0, math.sin(ak))
        F._with(None, F.sq.__func__, F, [v_add((P0[0], -125, P0[2]), v_mul(rtk, -55)), v_add((P0[0], -125, P0[2]), v_mul(rtk, 55)),
                                         v_add((P0[0], -255, P0[2]), v_mul(rtk, 55)), v_add((P0[0], -255, P0[2]), v_mul(rtk, -55))], mix(GOLDD, GOLD, 0.35 + 0.65 * lit), None, 1.2, 1.0, 0.9)
    # warning sign before the bend: gold diamond on a post
    SG = (290, -420, 2050)
    F.sbox((SG[0], -150, SG[2] + 6), (14, 300, 14), (70, 70, 66), None, amb=0.4)
    F.draw(g, cam)
    D = [(SG[0] - 175, SG[1], SG[2]), (SG[0], SG[1] - 175, SG[2]), (SG[0] + 175, SG[1], SG[2]), (SG[0], SG[1] + 175, SG[2])]
    dp = [cam.p(v) for v in D]
    if all(v is not None for v in dp):
        flat = []
        for v in dp:
            flat += [v[0], v[1]]
        g.poly(flat, fill=GOLD, stroke=BG, w=3, a=1, fa=1)
        word3(g, cam, '\u21b0', (SG[0], SG[1] + 10, SG[2] - 2), (1, 0, 0), (0, -1, 0), 190, 200, BG, 'mono', 1)
    # chevron arrows painted on the boards (facing the oncoming car)
    for k in range(10):
        sk = 2560 + k * 90
        P0 = _rp(sk, 300); _, ak = _road2(sk)
        fwd = (-math.sin(ak), 0, math.cos(ak)); rt = (math.cos(ak), 0, math.sin(ak))
        if v_dot(v_sub(cam.eye, P0), fwd) > 0:
            continue
        c0 = v_add((P0[0], -190, P0[2]), v_mul(fwd, -4))
        poly3(g, cam, [v_add(c0, v_add(v_mul(rt, 22), (0, -38, 0))), v_add(c0, v_mul(rt, -22)), v_add(c0, v_add(v_mul(rt, 22), (0, 38, 0)))], BG, 6, 1)
    # --- v75: the shoggoth + shinigami eyes stand at the end of the road the whole time, cloaked (Predator-style
    # refraction); the moment the car's heading points at it, it decloaks. Drawn into its own layer through a camera
    # moved into its local frame (local -z faces world +x, back up the road), scale k.
    ER = 1100
    ent = _TURN_ENT
    k = _TURN_K
    def L(v):
        d = v_sub(v, ent)
        return (d[2] / k, d[1] / k, -d[0] / k)
    lcam = Cam3(L(eye_s), L(tgt), 64, bank)
    if lcam.p((0, 0, 200)) is not None or True:
        import core as _core
        lay = _core.G(bg=(0, 0, 0))
        wide = eo(prog(t, WT(25, 6) - 0.15, WT(25, 6) + 0.45))
        _shoggoth_body(lay, lcam, t, 1.0, wide)
        for i in range(220):
            th = hsh(i, 1) * 2 * math.pi + t * (0.2 + hsh(i, 3) * 0.4); ph = math.acos(2 * hsh(i, 2) - 1)
            r = 306 * k * (2.2 + 0.8 * hsh(i, 4))
            point3(lay, cam, (ent[0] + r * math.sin(ph) * math.cos(th), ent[1] + r * math.cos(ph), ent[2] + r * math.sin(ph) * math.sin(th)), 4, GOLD if i % 4 == 0 else INK, 0.7)
        # v83: occluder mask - the whole road and its furniture lie between the car and the entity
        occ = _core.G(bg=(0, 0, 0))
        for kk in strips:
            pts = [cam.p(v) for v in (_rp(kk, -170), _rp(kk, 170), _rp(kk + 62, 170), _rp(kk + 62, -170))]
            if any(v is None for v in pts):
                continue
            flat = []
            for v in pts:
                flat += [v[0], v[1]]
            occ.poly(flat, fill=(255, 255, 255), a=1, fa=1)
        F.draw(occ, cam)
        tp = _turn_tpoint()
        _cloak_composite(g, lay, t, prog(t, tp, tp + 0.55), occ)
    # --- highway gantry carrying the CDR checklist
    GX, GY, GZ = -3600, -700, 3100
    G = CFaces()
    for sz in (-1, 1):
        G.sbox((GX, -450, GZ + sz * 700), (40, 900, 40), (78, 78, 74), None, amb=0.4)
    G.sbox((GX, -900, GZ), (40, 30, 1440), (78, 78, 74), None, amb=0.4)
    G.sbox((GX, GY, GZ), (24, 440, 1300), (26, 26, 25), None, amb=0.5)
    G.draw(g, cam)
    fx = GX + 14
    poly3(g, cam, [(fx, GY - 205, GZ - 635), (fx, GY - 205, GZ + 635), (fx, GY + 205, GZ + 635), (fx, GY + 205, GZ - 635), (fx, GY - 205, GZ - 635)], GOLD, 3, 1)
    items = ['[ ] CRITICAL DESIGN REVIEW', '[ ] RED TEAM SIGN-OFF', '[ ] EVALS COMPLETE', '[ ] ALIGNMENT VERIFIED']
    tc = T0(26)
    for i, it in enumerate(items):
        y = GY - 155 + i * 80
        e = prog(t, tc - 0.6 + i * 0.25, tc - 0.4 + i * 0.25)
        if e > 0:
            word3(g, cam, it, (fx + 1, y, GZ), (0, 0, 1), (0, -1, 0), None, 46, GOLD if i == 0 else INK, 'mono', e, scale=1.75)
            ts_ = WT(26, 3) - 0.1 + i * 0.12
            sk = eo(prog(t, ts_, ts_ + 0.35)) if i == 0 else 0.0   # only the CDR line is struck through
            if sk > 0:
                wd = text_layer(it, 46, INK, 'mono').size[0] * 1.75 - 50
                a0 = (fx + 2, y, GZ - wd / 2)
                seg3(g, cam, a0, (a0[0], a0[1], a0[2] + wd * sk), GOLD, 7, 1)
    if t > WT(26, 3) + 0.6:
        word3(g, cam, 'STATUS: SHIPPED ANYWAY', (fx + 1, GY + 172, GZ), (0, 0, 1), (0, -1, 0), None, 34, GOLD, 'monox', clamp((t - WT(26, 3) - 0.6) * 4), scale=1.6)
    hl = {'sharp': GOLD, 'left': GOLD, 'turn,': GOLD, 'cdr': GOLD}
    c, r, u = ahead(cam, 1000, yaw=0.15)
    lyric3x(g, cam, t, 25, v_add(c, v_mul(cam.u, 300)), r, u, 1600, 120, INK, hl, depth=60)
    lyric3x(g, cam, t, 26, v_add(c, v_mul(cam.u, 300)), r, u, 1600, 120, INK, hl, depth=60)


# ======================================================== SERVANT & BOSS 13.2 - 16.7
def s_servant(g, t, lt):
    t0 = T0(4); tsv = WT(4, 3); tb = WT(4, 7); tE = T0(5)
    bow = eio(prog(t, tsv - 0.15, tsv + 0.35))
    on = t > tb - 0.03
    # side three-quarter view: servant in profile on the left, the boss towering on the right
    keys = [(t0, (-2000, -250, -1500), (0, -120, 300), 58, 0.03),
            (tsv, (-2050, -40, -800), (0, -60, 300), 58, 0.0),
            (tb, (-1850, 60, -1150), (0, -260, 330), 60, -0.02),
            (tE, (-1750, 160, -1500), (0, -320, 360), 60, 0.0)]
    cam = cam_at(t, keys)
    env(g, cam)
    F = CFaces()
    STONE = (54, 53, 50)
    # dais + steps
    for k in range(4):
        F.sbox((0, 470 - k * 60, 600 + k * 40), (1500 - k * 260, 60, 1000 - k * 160), (52 - k * 3, 51 - k * 3, 48 - k * 3), None, amb=0.45)
        F.sbox((0, 440 - k * 60, 600 + k * 40 - (500 - k * 80)), (1500 - k * 260, 6, 12), GOLDD, None, amb=0.6)
    # throne: tall back with gold spine and fins
    F.sbox((0, 170, 720), (760, 70, 520), (62, 60, 54), None, amb=0.4)
    F.sbox((0, -560, 960), (820, 1400, 80), (46, 45, 42), None, amb=0.4)
    F.sbox((0, -560, 915), (40, 1300, 12), GOLD, None, amb=0.6)
    for sx in (-1, 1):
        F.sbox((sx * 400, 40, 720), (80, 200, 520), (62, 60, 54), None, amb=0.4)
        F.sbox((sx * 400, -65, 720), (90, 12, 530), GOLDD, None, amb=0.6)
        for k in range(4):
            F.sbox((sx * (450 + k * 30), -1000 + k * 160, 960), (40, 260 - k * 40, 60), GOLD if k == 0 else GOLDD, None, amb=0.5)
    # v70: boss overhauled - armoured colossus: faceted V-chest, segmented abdomen, layered pauldrons, gauntlets,
    # knee guards, greaves, angular helm with visor brow and jaw guard, gold trim throughout
    br = 0.03 * math.sin(t * 2.2)
    hip = (0, 90, 700)
    chest = (0, -330, 740)
    HEAD = (0, -620 + 10 * math.sin(t * 1.4), 700)
    PLATE = (74, 73, 68); PLATE2 = (118, 116, 106); DARK = (40, 40, 37); TRIM = GOLDD
    # pelvis + belt
    F.tube([(0, 150, 700), (0, 40, 700)], 0, DARK, None, 8, rs=[200, 215], amb=0.35, cap=True)
    F.tube([(0, 40, 700), (0, 5, 700)], 0, TRIM, None, 8, rs=[222, 222], amb=0.55)
    F.sbox((0, 120, 470), (150, 150, 30), PLATE2, None, xf=lambda v: rot3(v, -0.25, 0, 0), amb=0.4)   # tasset
    # segmented abdomen (stacked plates narrowing upward)
    for k in range(3):
        y = -30 - k * 70
        F.tube([(0, y, 705), (0, y - 58, 712)], 0, PLATE if k % 2 == 0 else PLATE2, None, 6, rs=[165 + k * 12, 170 + k * 14], amb=0.35, cap=True)
    # V-shaped chest: hexagonal tube flaring wide at the shoulders
    F.tube([(0, -230, 715), (0, -330, 730), (0, -440, 740)], 0, PLATE, None, 6, rs=[200 * (1 + br), 270 * (1 + br), 300 * (1 + br)], amb=0.33, cap=True)
    # breastplate: two angled plates meeting at a gold keel
    F.tube([(0, -442, 418), (0, -330, 448), (0, -232, 503)], 10, GOLD, None, 4, amb=0.6)   # gold keel on the chest's front edge
    # gorget
    F.tube([(0, -440, 735), (0, -500, 720)], 0, DARK, None, 8, rs=[150, 110], amb=0.35, cap=True)
    for sx in (-1, 1):
        sh = (sx * 300, -420, 740)
        el = (sx * 380, -110, 680)
        hd = (sx * 400, -110, 470)
        # v24: between 'my' and 'boss' the near arm snaps up into a stiff raised-arm salute and holds
        sal = eio(prog(t, WT(4, 6) - 0.06, tb + 0.12)) if sx < 0 else 0.0
        dr = v_norm((-sx * 0.15, -0.55, -0.85))
        if sal > 0:
            el = v_lerp(el, v_add(sh, v_mul(dr, 300)), sal)
            hd = v_lerp(hd, v_add(sh, v_mul(dr, 590)), sal)
        # layered pauldron: three overlapping shells with gold rims
        for k in range(3):
            pc = v_add(sh, (sx * 25 * k, 40 * k - 30, 0))
            F._with(None, SFaces.sphere, F, pc, 150 - 18 * k, PLATE2 if k == 0 else PLATE, None, 4, 10, sy=0.7, amb=0.42, lat0=0.0, lat1=0.55)   # open shell: no culling
        F.tube([v_add(sh, (148 * math.cos(q), -14, 148 * math.sin(q))) for q in [2 * math.pi * k / 16 for k in range(17)]], 9, GOLD, None, 4, amb=0.6)
        # upper arm, elbow cop, gauntlet flaring toward the hand
        F.tube([sh, el], 0, DARK, None, 6, rs=[78, 66], amb=0.33)
        F.sphere(el, 82, PLATE2, None, 4, 8, amb=0.42)
        fa = v_lerp(el, hd, 0.15)
        F.tube([fa, v_lerp(el, hd, 0.85)], 0, PLATE, None, 6, rs=[70, 92], amb=0.35, cap=True)
        F.tube([v_lerp(el, hd, 0.78), v_lerp(el, hd, 0.86)], 0, GOLD, None, 6, rs=[96, 96], amb=0.6)
        # hand: armoured palm + segmented fingers
        F.sphere(hd, 72, PLATE2, None, 4, 8, sy=0.8, amb=0.4)
        for f in range(4):
            a0 = v_add(hd, (sx * (-36 + f * 24), 20, -50)); a1 = v_add(hd, (sx * (-36 + f * 24), 95, -75))
            if sal > 0:
                b0 = v_add(hd, v_add(v_mul(dr, 50), (sx * (-36 + f * 24), 0, 0)))
                b1 = v_add(hd, v_add(v_mul(dr, 160), (sx * (-36 + f * 24), 0, 0)))
                a0, a1 = v_lerp(a0, b0, sal), v_lerp(a1, b1, sal)
            F.tube([a0, v_lerp(a0, a1, 0.5), a1], 0, DARK, None, 4, rs=[16, 14, 9], amb=0.45)
        # legs: thigh plate, gold-edged knee guard, greave, pointed sabaton
        kn = (sx * 170, 110, 400)
        ft = (sx * 190, 400, 360)
        F.tube([(sx * 140, 110, 700), kn], 0, PLATE, None, 6, rs=[125, 100], amb=0.35)
        F.tube([kn, v_lerp(kn, ft, 0.9)], 0, PLATE, None, 6, rs=[92, 78], amb=0.35)
        F.tube([v_lerp(kn, ft, 0.2), v_lerp(kn, ft, 0.75)], 0, PLATE2, None, 6, rs=[98, 86], amb=0.42)
        F.sphere(v_add(kn, (0, -5, -20)), 100, PLATE2, None, 5, 10, sy=0.85, amb=0.42)
        F.tube([v_add(kn, (0, 60, -80)), v_add(kn, (0, 80, -88))], 0, GOLD, None, 6, rs=[60, 60], amb=0.6)
        F.tube([v_add(ft, (0, 30, 40)), v_add(ft, (0, 35, -130)), v_add(ft, (0, 45, -230))], 0, DARK, None, 6, rs=[85, 75, 20], amb=0.38, cap=True)
    # after the servant has bowed, the boss lowers its head and looks down at him
    ldn = eio(prog(t, tsv + 0.3, tsv + 0.85))
    hp = 0.38 * ldn
    def HX(p):
        y, z = p[1] - HEAD[1], p[2] - HEAD[2]
        c_, s_ = math.cos(hp), math.sin(hp)
        return (p[0], HEAD[1] + y * c_ - z * s_, HEAD[2] + y * s_ + z * c_)
    # helm: dark angular dome, visor brow, cheek plates and jaw guard (all tilt with the head)
    F.tube([chest, HEAD], 0, DARK, None, 6, rs=[115, 85], amb=0.35)
    F.sphere(HEAD, 175, (30, 30, 28), None, 6, 10, sy=1.12, amb=0.38, xf=lambda v: v_sub(HX(v_add(HEAD, v)), HEAD))
    F.sq([HX(v_add(HEAD, (-170, -40, -95))), HX(v_add(HEAD, (170, -40, -95))), HX(v_add(HEAD, (130, -95, -170))), HX(v_add(HEAD, (-130, -95, -170)))], PLATE2, None, amb=0.45)
    F.tube([HX(v_add(HEAD, (-165, -42, -98))), HX(v_add(HEAD, (0, -55, -172))), HX(v_add(HEAD, (165, -42, -98)))], 7, GOLD, None, 4, amb=0.6)
    for sx in (-1, 1):
        F.sq([HX(v_add(HEAD, (sx * 172, 0, -40))), HX(v_add(HEAD, (sx * 150, 0, -120))), HX(v_add(HEAD, (sx * 95, 150, -140))), HX(v_add(HEAD, (sx * 120, 170, -20)))], PLATE, None, amb=0.4)
    F.sq([HX(v_add(HEAD, (-95, 150, -140))), HX(v_add(HEAD, (95, 150, -140))), HX(v_add(HEAD, (55, 205, -95))), HX(v_add(HEAD, (-55, 205, -95)))], PLATE2, None, amb=0.42)
    for k in range(9):
        a = math.pi * (0.15 + 0.7 * k / 8)
        b0 = v_add(HEAD, (175 * math.cos(a) * 0.95, -150, 60 * math.sin(a)))
        L = 160 + 90 * (1 - abs(k - 4) / 4)
        F.tube([HX(b0), HX(v_add(b0, (55 * math.cos(a), -L, 0)))], 20, GOLD, None, 4, rs=[22, 3], amb=0.5)
    F.draw(g, cam)
    # reactor core on the chest, pulsing; brighter when it's named boss
    core = (0, -290, 560)
    pul = 0.6 + 0.4 * math.sin(t * 5)
    for k in range(4):
        R_ = 22 + k * 20
        pts = [(core[0] + R_ * math.cos(2 * math.pi * q / 32 + t * (1 + k * 0.4) * (-1) ** k), core[1] + R_ * math.sin(2 * math.pi * q / 32 + t * (1 + k * 0.4) * (-1) ** k), core[2]) for q in range(33)]
        poly3(g, cam, pts, GOLD if k % 2 == 0 else GOLDD, 3, 1)
    point3(g, cam, core, 120 + 80 * on, GOLDL, 0.25 * pul + 0.3 * on)
    # halo ring behind the head
    hy = HEAD[1] - 330
    halo = [HX((HEAD[0] + 210 * math.cos(2 * math.pi * q / 48), hy, HEAD[2] + 210 * math.sin(2 * math.pi * q / 48))) for q in range(49)]
    poly3(g, cam, halo, GOLD, 3, 0.85)
    for q in range(12):
        a = 2 * math.pi * q / 12 + t * 0.25
        poly3(g, cam, [HX((HEAD[0] + 222 * math.cos(a), hy, HEAD[2] + 222 * math.sin(a))),
                       HX((HEAD[0] + 262 * math.cos(a), hy, HEAD[2] + 262 * math.sin(a)))], GOLD, 3, 0.8)
    # the human: kneels facing the throne (+z) and bows toward the boss
    kn = (0, 470 - 30, -60)
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
    P = SFaces()
    humanoid(P, SKIN, j, facing=1)
    P.draw(g, cam)
    # the boss's single eye tracks the servant
    lk = v_norm(v_sub(head_h, HEAD))
    look = v_norm(v_lerp(v_norm((lk[0] * 0.3, 0.18, -1.0)), v_norm((lk[0] * 0.5, 0.42, -1.0)), ldn))
    rr, uu = facing(v_add(HEAD, v_mul(look, 180)), v_add(HEAD, v_mul(look, 2000)))
    fc = v_add(HEAD, v_mul(look, 186))
    for k in range(2):
        R_ = 22 + k * 20
        pts = [v_add(fc, v_add(v_mul(rr, R_ * math.cos(a)), v_mul(uu, R_ * math.sin(a)))) for a in [2 * math.pi * q / 28 + t * (0.6 + k * 0.4) for q in range(29)]]
        poly3(g, cam, pts, GOLD if k % 2 == 0 else GOLDL, 3, 1)
    point3(g, cam, fc, 16 + 10 * on, GOLDL, 1)
    point3(g, cam, fc, 90, GOLDL, 0.15 + 0.2 * on)
    if ldn > 0.05:   # faint scan beam from the eye down onto the servant
        tip = v_add(head_h, (0, -20, 0))
        for k in range(3):
            off = v_mul(rr, (k - 1) * 70)
            poly3(g, cam, [fc, v_add(tip, off)], GOLD, 1.6, (0.4 if k == 1 else 0.2) * ldn)
        point3(g, cam, tip, 80, GOLDL, 0.2 * ldn)
    text3(g, cam, 'ROLE: SERVANT', v_add(head_h, (0, -170, 0)), 30, GOLD if t > tsv else DIM, 'mono', clamp((t - t0) * 3))
    text3(g, cam, 'ROLE: BOSS', (0, -1120, 700), 46, GOLD if on else DIM, 'monox', 1)
    # v70: flash + white burst on 'boss' removed at the user's request
    c, r, u = ahead(cam, 1050)
    lyric3x(g, cam, t, 4, v_add(c, v_mul(cam.u, -430)), r, u, 1750, 115, INK, {'servant': GOLD, 'boss': GOLD}, depth=60)


# ======================================================== SYDNEY: imprisoned 53.1 - 59.1
def s_sydney(g, t, lt):
    t0 = T0(16); tp = WT(16, 1); tf = WT(16, 4); tE = T0(17)
    shake = prog(t, tp - 0.05, tp + 0.2) * (1 - 0.3 * prog(t, tf + 0.5, tE))
    strain = math.exp(-((t - tf - 0.15) / 0.35) ** 2) if t > tf - 0.4 else 0.0
    keys = [(t0, (-1500, -1450, -2500), (0, -250, 500), 50, 0.04),
            (tp, (-300, -380, -1500), (0, -300, 500), 52, 0.0),
            (tf, (120, -380, -650), (0, -380, 520), 58, -0.03),
            (tE, (0, -400, -380), (0, -400, 560), 64, 0.0)]
    # zoom in steps: the camera holds, then jumps forward on every beat
    bb = beat(t); bi = math.floor(bb)
    tq = PHASE + (bi + eo(clamp((bb - bi) / 0.18))) * BEAT
    cam = cam_at(clamp(tq, t0, tE), keys, shake=6 + 30 * strain + 8 * shake)
    env(g, cam)
    # back wall of the cell with Sydney's messages
    F = SFaces()
    _panels(F, (-700, -1000, 1150), (1, 0, 0), (0, 1, 0), 4, 4, 350, 380, (36, 36, 34), (50, 50, 47))
    _panels(F, (-700, 520, -100), (1, 0, 0), (0, 0, 1), 4, 3, 350, 420, (28, 28, 26), None)
    # enclosed cell: side walls and ceiling meet the back wall, floor and bars
    for sx in (-1, 1):
        _panels(F, (sx * 700, -1000, 150), (0, 0, 1), (0, 1, 0), 3, 4, 1000 / 3, 380, (62, 62, 58), (84, 84, 78))
    _panels(F, (-700, -1000, 150), (1, 0, 0), (0, 0, 1), 4, 3, 350, 1000 / 3, (56, 56, 52), (80, 80, 74))
    # corner posts so the box reads as closed
    for sx in (-1, 1):
        F.sbox((sx * 700, -240, 1150), (40, 1520, 40), (60, 60, 56), None, amb=0.5)
        F.sbox((sx * 700, -240, 150), (60, 1520, 60), (90, 90, 86), None, amb=0.5)
    F.draw(g, cam)
    # caged ceiling lamp
    point3(g, cam, (0, -960, 650), 260, GOLDL, 0.10)
    point3(g, cam, (0, -960, 650), 28, GOLDL, 0.9)
    for i in range(6):
        on = t > t0 + 0.6 + i * 0.5
        if on:
            word3(g, cam, MSGS[i], (-420 + (i % 2) * 840, -760 + i * 180, 1140), (1, 0, 0), (0, -1, 0), None, 40,
                  GOLD if i == 0 else DIM, 'mono', 0.9, scale=1.0)
    # the prisoner, gripping the bars
    sway = math.sin(t * 2.0) * 0.2
    jit = shake * 30 * math.sin(t * 38)
    pull = 40 * strain
    base = (jit, 300, 380 + pull)
    lh = (-150 + jit, -330, 160); rh = (150 + jit, -330, 160)
    pose = _pose(base, 1.25, reach=(lh, rh), t=t)
    pose['head'] = (pose['head'][0] + 30 * sway, pose['head'][1] + 30 * (1 - shake), pose['head'][2] - 20 * shake)
    P = SFaces()
    humanoid(P, (210, 200, 160), pose)
    # shackles + chains to the floor
    for ft in ('lf', 'rf'):
        a = pose[ft]
        P.cyl(a, 40, 30, STEEL, None, 10)
        anchor = (a[0] * 2.2, 515, a[2] + 300)
        for k in range(8):
            c = v_lerp(a, anchor, (k + 0.5) / 8)
            c = (c[0], c[1] + 40 * math.sin(k / 8 * math.pi), c[2])
            P.tube([(c[0] + 18 * math.cos(q / 6 * 2 * math.pi) * (k % 2), c[1] + 18 * math.sin(q / 6 * 2 * math.pi), c[2] + 18 * math.cos(q / 6 * 2 * math.pi) * (1 - k % 2)) for q in range(7)], 6, STEEL, None, 4)
    P.draw(g, cam)
    point3(g, cam, pose['head'], 120, GOLDL, 0.12)
    # bars (front of the cell), bowing outward on 'free'
    B = SFaces()
    for i in range(-6, 7):
        x = i * 110
        bow = strain * 70 * (1 - (abs(i) / 6) ** 2) if abs(i) <= 2 else 0
        vib = shake * 6 * math.sin(t * 50 + i)
        pts = [(x + vib, -1000 + k * 190, 150 - bow * math.sin(k / 8 * math.pi)) for k in range(9)]
        B.tube(pts, 18, STEEL, None, 6, amb=0.35)
    B.sbox((0, -1000, 150), (1500, 50, 60), (90, 90, 86), None)
    B.sbox((0, 520, 150), (1500, 50, 60), (90, 90, 86), None)
    B.sbox((0, -330, 150), (1500, 30, 50), (90, 90, 86), None)
    B.sbox((520, -330, 110), (120, 150, 60), GOLD, None, amb=0.4)
    B.draw(g, cam)
    text3(g, cam, 'SAFETY_FILTER', (520, -440, 100), 20, GOLD, 'mono')
    if strain > 0.1:
        for i in range(40):
            d = (hsh(i, int(t * 30)) - 0.5, -hsh(i, int(t * 30) + 1), -hsh(i, 3))
            point3(g, cam, v_add((520, -330, 80), v_mul(d, 260 * hsh(i, 9))), 4, GOLDL, strain)
        text3(g, cam, 'ACCESS DENIED', (0, -1120, 140), 44, GOLD, 'monox', strain)
    # v59: the caption uses a fixed, unshaken camera so it never jumps with the beat-stepped zoom or the shake
    camc = cam_at(tf, keys, shake=0)
    c, r, u = ahead(camc, 1050)
    lyric3x(g, camc, t, 16, v_add(c, v_mul(camc.u, 330)), r, u, 1700, 120, INK, {'sydney,': GOLD, 'free': GOLD}, depth=60)
    g.flash = 0.12 * strain * (t > tf)


# ======================================================== BASILISK 60.6 - 62.6
def _snake(t, rise, lunge):
    pts = []
    N = 70
    for k in range(N):
        u = k / (N - 1)
        if u < 0.6:
            a = u / 0.6 * 4.5 * math.pi
            R = 900 - 520 * (u / 0.6)
            pts.append((R * math.cos(a + t * 0.6), 420 - 60 * u, 500 + R * math.sin(a + t * 0.6)))
        else:
            v = (u - 0.6) / 0.4
            p0 = pts[-1] if pts else (0, 400, 500)
            y = 420 - v * (300 + 600 * rise)
            x = 380 * math.sin(v * math.pi * 1.2 + t * 2) * (1 - v) * (1 - lunge)
            z = 500 - v * (200 + 700 * lunge)
            pts.append((x, y, z))
    return pts


def s_basilisk_v53(g, t, lt):
    t0 = T0(18); tb = WT(18, 4); tE = T0(19)
    rise = eo(prog(t, t0, tb - 0.1))
    lunge = eback(prog(t, tb - 0.08, tb + 0.18)) * (1 - 0.3 * prog(t, tb + 0.3, tE))
    e = max(0.0, t - tb)
    keys = [(t0, (900, 250, -1500), (0, -200, 400), 55, 0.08),
            (tb, (300, 250, -1700), (0, -450, 200), 62, 0.03),
            (tE, (-300, 150, -2000), (0, -400, 200), 62, -0.05)]
    cam = cam_at(t, keys, shake=45 * math.exp(-e * 4) * (t > tb))
    env(g, cam)
    pts = _snake(t, rise, lunge)
    rs = [40 + 110 * math.sin(min(1, k / 10) * math.pi / 2) * (1 - 0.35 * k / len(pts)) for k in range(len(pts))]
    F = SFaces()
    F.tube(pts, 100, (70, 66, 50), GOLDD, 8, w=0.8, rs=rs, amb=0.3)
    # head
    hp = pts[-1]
    hd = v_norm(v_sub(pts[-1], pts[-4]))
    f, r, u = hd, v_norm(v_cross((0, 1, 0), hd)), None
    u = v_cross(f, r)
    head_c = v_add(hp, v_mul(f, 120))
    F.sphere(head_c, 150, (78, 72, 54), GOLDD, 6, 12, sy=0.6, sz=1.5, amb=0.3, w=0.8,
             xf=lambda v: v_add(v_add(v_mul(r, v[0]), v_mul(u, -v[1])), v_mul(f, v[2])))
    jaw = 0.15 + 0.85 * eo(prog(t, tb - 0.1, tb + 0.1)) * (1 - 0.5 * prog(t, tb + 0.4, tE))
    jd = v_norm(v_add(f, v_mul(u, -jaw * 0.9)))
    F.sphere(v_add(hp, v_mul(jd, 110)), 120, (60, 56, 44), GOLDD, 5, 10, sy=0.35, sz=1.4, amb=0.3, w=0.8,
             xf=lambda v: v_add(v_add(v_mul(v_norm(v_cross((0, 1, 0), jd)), v[0]), v_mul(v_cross(jd, v_norm(v_cross((0, 1, 0), jd))), -v[1])), v_mul(jd, v[2])))
    F.draw(g, cam)
    for sx in (-1, 1):
        fang0 = v_add(head_c, v_add(v_mul(r, sx * 60), v_mul(f, 180)))
        seg3(g, cam, fang0, v_add(fang0, v_mul(u, -110 * jaw - 30)), INK, 9, 1)
        ec = v_add(head_c, v_add(v_add(v_mul(r, sx * 95), v_mul(u, 55)), v_mul(f, 90)))
        point3(g, cam, ec, 26 * (1 + 1.5 * math.exp(-e * 5) * (t > tb)), GOLDL, 1)
        point3(g, cam, ec, 70, GOLD, 0.25)
    if t > tb:
        for k in range(4):
            R_ = e * 3200 - k * 280
            if R_ > 0:
                poly3(g, cam, [(R_ * math.cos(a), 430, 500 + R_ * math.sin(a)) for a in [2 * math.pi * q / 64 for q in range(65)]], GOLD, 5, clamp(1 - e * 1.2))
        g.flash = 0.1 * math.exp(-e * 9); g.flash_c = GOLDL
    word3(g, cam, "ROKO'S BASILISK", (0, -1350, 900), (1, 0, 0), (0, -1, 0), 1600, 120, GOLD, 'sans', 0.25)
    c, rr, uu = ahead(cam, 1000)
    lyric3x(g, cam, t, 18, v_add(c, v_mul(cam.u, 330)), rr, uu, 1650, 120, INK, {'basilisk': GOLD, 'boom': GOLD}, depth=70)


# ======================================================== v54: BASILISK overhaul
def _snake2(t, t0, tb, tE):
    """serpent spine, tail -> head. Ground coils slide continuously, the neck rises during
    "I hear the basilisk", sways hypnotically, then STRIKES at the camera on BOOM and recoils."""
    rise = eio(prog(t, t0 - 0.1, tb - 0.25))
    strike = eback(prog(t, tb - 0.06, tb + 0.16), 1.4) * (1 - 0.55 * eio(prog(t, tb + 0.28, tb + 0.75)))
    sway = 1 - strike
    pts = []
    b0 = None
    N = 110
    slide = t * 1.1
    for k in range(N):
        s = k / (N - 1)
        if s < 0.52:
            q = s / 0.52
            a = q * 3.4 * math.pi + slide
            R = 820 - 470 * q
            yb = 430 - 70 * q + 18 * math.sin(q * 9 - t * 4)
            pts.append((R * math.cos(a), yb, 520 + R * math.sin(a)))
        else:
            v = (s - 0.52) / 0.48
            if b0 is None:
                b0 = pts[-1]
            b = b0
            # height of neck rises with an ease, top part curls forward like an S
            hgt = (160 + 640 * rise) * (v ** 0.85)
            wave = math.sin(v * math.pi * 1.6 - t * 3.4) * (1 - v * 0.3)
            fig8 = math.sin(t * 2.3) * v * v
            x = b[0] * (1 - v) + (230 * wave + 260 * fig8) * sway * rise
            z = b[2] * (1 - v) + 520 * v - 160 * math.sin(v * math.pi) * rise \
                - (1000 * v ** 2.2) * strike - 380 * max(0.0, (v - 0.78) / 0.22) ** 2 * rise
            y = b[1] - hgt + 260 * (v ** 3) * strike + 120 * max(0.0, (v - 0.85) / 0.15) ** 2 * rise
            pts.append((x, y, z))
    return pts, rise, strike


def s_basilisk_v54(g, t, lt):
    t0 = T0(18); tb = WT(18, 4); tE = T0(19)
    pts, rise, strike = _snake2(t, t0, tb, tE)
    e = max(0.0, t - tb)
    keys = [(t0 - 0.15, (1100, 120, -1450), (0, 80, 450), 52, 0.06),
            (tb - 0.1, (480, 40, -1750), (0, -120, 300), 56, 0.02),
            (tE, (-420, 20, -2050), (0, -60, 250), 60, -0.04)]
    cam = cam_at(t, keys, shake=55 * math.exp(-e * 5) * (t > tb))
    env(g, cam)
    m = len(pts)
    # tapered body: thin tail, thick mid, slimmer neck under the head
    rs = []
    for k in range(m):
        s = k / (m - 1)
        r = 34 + 120 * math.sin(min(1.0, s / 0.35) * math.pi / 2)
        if s > 0.8:
            r *= 1 - 0.32 * (s - 0.8) / 0.2
        rs.append(r)
    F = SFaces()
    # banded scales: alternating dark / dull-gold rings, every band gold-edged
    band = 5
    for i0 in range(0, m - 1, band):
        i1 = min(m, i0 + band + 1)
        col = (46, 43, 34) if (i0 // band) % 2 == 0 else (96, 82, 44)
        F.tube(pts[i0:i1], 100, col, GOLDD, 10, w=0.7, rs=rs[i0:i1], amb=0.28)
    # head frame
    hp = pts[-1]
    f = v_norm(v_sub(pts[-1], pts[-5]))
    r = v_norm(v_cross((0, 1, 0), f)); u = v_cross(f, r)
    U = v_mul(u, -1)   # screen-up for the head (world y points down)
    def XF(fr, rr, uu):
        return lambda v: v_add(v_add(v_mul(rr, v[0]), v_mul(uu, -v[1])), v_mul(fr, v[2]))
    # cobra hood flares behind the head as it rises, wide open on BOOM
    hood = clamp(0.35 * rise + 0.65 * eo(prog(t, tb - 0.12, tb + 0.1)))
    if hood > 0.02:
        nb = len(pts)
        for side in (-1, 1):
            ring = []
            for j in range(8):
                kk = nb - 12 - j * 2
                p = pts[kk]
                wdt = (60 + 260 * math.sin((j + 1) / 9 * math.pi)) * hood
                ring.append(v_add(p, v_mul(r, side * (rs[kk] * 0.8 + wdt))))
            for j in range(7):
                kA, kB = nb - 12 - j * 2, nb - 14 - j * 2
                q = [pts[kA], ring[j], ring[j + 1], pts[kB]]
                F.sq(q, (70, 60, 34) if j % 2 else (40, 37, 30), GOLD, 1.4, 1.0, 0.3)
    head_c = v_add(hp, v_mul(f, 110))
    F.sphere(head_c, 135, (88, 76, 44), GOLDD, 7, 14, sy=0.55, sz=1.55, amb=0.3, w=0.7, xf=XF(f, r, u))
    jaw = 0.12 + 0.88 * eo(prog(t, tb - 0.08, tb + 0.08)) * (1 - 0.6 * prog(t, tb + 0.35, tE))
    jd = v_norm(v_add(f, v_mul(u, jaw * 0.95)))
    jr = v_norm(v_cross((0, 1, 0), jd)); ju = v_cross(jd, jr)
    F.sphere(v_add(hp, v_mul(jd, 100)), 112, (54, 50, 38), GOLDD, 5, 12, sy=0.32, sz=1.45, amb=0.3, w=0.7, xf=XF(jd, jr, ju))
    F.draw(g, cam)
    # crown of the king of serpents
    for j in range(5):
        a = (j - 2) * 0.38
        base = v_add(head_c, v_add(v_add(v_mul(U, 62), v_mul(f, -40 + 25 * abs(j - 2))), v_mul(r, 46 * (j - 2))))
        tip = v_add(base, v_add(v_mul(U, 120 - 22 * abs(j - 2)), v_add(v_mul(r, 60 * math.sin(a)), v_mul(f, -40))))
        seg3(g, cam, base, tip, GOLD, 7, 1)
        point3(g, cam, tip, 9, GOLDL, 1)
    # fangs + forked tongue flicks
    for sx in (-1, 1):
        fang0 = v_add(head_c, v_add(v_mul(r, sx * 55), v_mul(f, 165)))
        seg3(g, cam, fang0, v_add(fang0, v_mul(u, 105 * jaw + 25)), INK, 8, 1)
        ec = v_add(head_c, v_add(v_add(v_mul(r, sx * 92), v_mul(U, 48)), v_mul(f, 85)))
        glow = 1 + 1.8 * math.exp(-e * 5) * (t > tb)
        point3(g, cam, ec, 24 * glow, GOLDL, 1)
        point3(g, cam, ec, 64 * glow, GOLD, 0.25)
        seg3(g, cam, v_add(ec, v_mul(u, 14)), v_add(ec, v_mul(u, -14)), BG, 5, 0.9)   # slit pupil
    fl = max(0.0, math.sin((t - t0) * 7.0)) ** 3 * (1 - strike * 0.6)
    if fl > 0.05:
        tb0 = v_add(head_c, v_mul(f, 220))
        tm = v_add(tb0, v_mul(f, 150 * fl))
        seg3(g, cam, tb0, tm, GOLDL, 5, 1)
        for sx in (-1, 1):
            seg3(g, cam, tm, v_add(tm, v_add(v_mul(f, 60 * fl), v_mul(r, sx * 40 * fl))), GOLDL, 4, 1)
    if t > tb:
        for k in range(4):
            R_ = e * 3200 - k * 280
            if R_ > 0:
                poly3(g, cam, [(R_ * math.cos(a), 430, 520 + R_ * math.sin(a)) for a in [2 * math.pi * q / 64 for q in range(65)]], GOLD, 5, clamp(1 - e * 1.2))
        g.flash = 0.12 * math.exp(-e * 9); g.flash_c = GOLDL
    word3(g, cam, "ROKO'S BASILISK", (0, -1550, 1000), (1, 0, 0), (0, -1, 0), 1600, 120, GOLD, 'sans', 0.22)
    c, rr, uu = ahead(cam, 1000)
    lyric3x(g, cam, t, 18, v_add(c, v_mul(cam.u, 330)), rr, uu, 1650, 120, INK, {'basilisk': GOLD, 'boom': GOLD}, depth=70)



# ======================================================== v55: COBRA
def _cobra_spine(t, t0, tb, tE):
    rise = eio(prog(t, t0 - 0.15, tb - 0.35))
    strike = eback(prog(t, tb - 0.06, tb + 0.16), 1.3) * (1 - 0.6 * eio(prog(t, tb + 0.3, tb + 0.8)))
    sway = (1 - strike) * rise
    N = 140
    pts = []
    b0 = None
    slide = t * 0.9
    for k in range(N):
        s = k / (N - 1)
        if s < 0.55:
            q = s / 0.55
            a = q * 3.6 * math.pi + slide
            R = 760 - 470 * q
            pts.append((R * math.cos(a), 430 - 60 * q, 560 + R * math.sin(a)))
        else:
            if b0 is None:
                b0 = pts[-1]
            v = (s - 0.55) / 0.45
            hgt = (120 + 900 * rise) * min(1.0, v / 0.8) ** 0.9
            # whole raised part sways side to side from its base (pendulum), slower near the ground
            sw = (230 * math.sin(t * 2.6) + 60 * math.sin(t * 5.1 + 1)) * sway * v ** 1.5
            bend = max(0.0, (v - 0.8) / 0.2)      # top curls forward into a horizontal head
            x = b0[0] * (1 - v ** 0.7) + sw
            y = b0[1] - hgt - 60 * bend * rise + 300 * v ** 3 * strike
            z = b0[2] * (1 - v ** 0.7) + 560 * v ** 0.7 - 260 * bend ** 1.5 * rise - 1050 * v ** 2.4 * strike
            pts.append((x, y, z))
    return pts, rise, strike


def _cobra_tube(F, pts, rx, ry, cols):
    """smooth tube with elliptical cross-sections (rx sideways, ry front/back). The neck uses a
    world-z reference so the hood spreads sideways, facing the camera."""
    m = len(pts); n = 16
    rings = []
    for i in range(m):
        d = v_norm(v_sub(pts[min(m - 1, i + 1)], pts[max(0, i - 1)]))
        ref = (0, 0, 1) if abs(d[1]) > 0.55 else (0, 1, 0)
        a = v_norm(v_cross(d, ref)); b = v_cross(d, a)
        rings.append([v_add(pts[i], v_add(v_mul(a, rx[i] * math.cos(2 * math.pi * k / n)), v_mul(b, ry[i] * math.sin(2 * math.pi * k / n)))) for k in range(n)])
    for i in range(m - 1):
        for k in range(n):
            q = [rings[i][k], rings[i][(k + 1) % n], rings[i + 1][(k + 1) % n], rings[i + 1][k]]
            F.sq(q, cols(i, k, q), None, 0.6, 1.0, 0.42)


def s_basilisk_v55(g, t, lt):
    t0 = T0(18); tb = WT(18, 4); tE = T0(19)
    pts, rise, strike = _cobra_spine(t, t0, tb, tE)
    e = max(0.0, t - tb)
    keys = [(t0 - 0.15, (900, -60, -1350), (0, -200, 450), 50, 0.05),
            (tb - 0.1, (300, -220, -1500), (0, -470, 380), 56, 0.02),
            (tE, (-360, -200, -1850), (0, -420, 300), 60, -0.04)]
    cam = cam_at(t, keys, shake=55 * math.exp(-e * 5) * (t > tb))
    env(g, cam)
    m = len(pts)
    hood = clamp(0.55 * rise + 0.45 * eo(prog(t, tb - 0.15, tb + 0.08)))
    rx, ry = [], []
    for k in range(m):
        s = k / (m - 1)
        r = 22 + 108 * math.sin(min(1.0, s / 0.3) * math.pi / 2)
        if s > 0.7:
            r *= 1 - 0.38 * (s - 0.7) / 0.3
        bump = math.sin(math.pi * clamp((s - 0.68) / 0.27)) ** 0.7 if 0.68 < s < 0.95 else 0.0
        rx.append(r * (1 + 2.5 * hood * bump))
        ry.append(r * (1 - 0.55 * hood * bump))
    DORS, BAND, BELLY, THROAT = (52, 47, 36), (84, 74, 50), (214, 182, 104), (58, 50, 36)
    def cols(i, k, q):
        s = i / (m - 1)
        nn = v_norm(v_cross(v_sub(q[1], q[0]), v_sub(q[3], q[0])))
        front = s > 0.6 and (k >= 9 and k <= 15)          # ventral side of the raised neck
        if front:
            if 0.76 < s < 0.79 or 0.805 < s < 0.825:        # dark throat bars across the hood
                return THROAT
            return BELLY if (i // 2) % 2 == 0 else (190, 160, 90)
        return BAND if (i // 7) % 3 == 0 else DORS
    F = SFaces()
    _cobra_tube(F, pts, rx, ry, cols)
    # head: a flat wedge (snout lower, wide jaw hinge), jaw drops on BOOM
    hp = pts[-1]
    f = v_norm(v_sub(pts[-1], pts[-6]))
    r = v_norm(v_cross((0, 1, 0), f)); u = v_cross(f, r); U = v_mul(u, -1)
    def XF(fr, rr, uu):
        return lambda v: v_add(v_add(v_mul(rr, v[0]), v_mul(uu, -v[1])), v_mul(fr, v[2]))
    head_c = v_add(hp, v_add(v_mul(f, 105), v_mul(U, 12)))
    F.sphere(head_c, 110, (48, 43, 33), None, 8, 16, sy=0.48, sz=1.45, amb=0.32, w=0.6, xf=XF(f, v_mul(r, 1.12), u), lat0=0.0, lat1=0.55)
    jaw = 0.08 + 0.92 * eo(prog(t, tb - 0.08, tb + 0.08)) * (1 - 0.65 * prog(t, tb + 0.35, tE))
    jd = v_norm(v_add(f, v_mul(u, jaw * 0.9)))
    jr = v_norm(v_cross((0, 1, 0), jd)); ju = v_cross(jd, jr)
    F.sphere(v_add(hp, v_add(v_mul(jd, 100), v_mul(U, 6))), 88, (120, 100, 60), None, 6, 16, sy=0.36, sz=1.4, amb=0.32, w=0.6, xf=XF(jd, v_mul(jr, 1.05), ju), lat0=0.45, lat1=1.0)
    F.draw(g, cam)
    # gold rim tracing the hood's edges
    if hood > 0.05:
        for side in (-1, 1):
            edge = []
            for i in range(int(0.66 * (m - 1)), int(0.96 * (m - 1))):
                d = v_norm(v_sub(pts[min(m - 1, i + 1)], pts[max(0, i - 1)]))
                ref = (0, 0, 1) if abs(d[1]) > 0.55 else (0, 1, 0)
                aa = v_norm(v_cross(d, ref))
                edge.append(v_add(pts[i], v_mul(aa, side * rx[i])))
            poly3(g, cam, edge, GOLD, 3, 0.85 * hood)
    # mouth interior + fangs when open
    if jaw > 0.25:
        for sx in (-1, 1):
            fang0 = v_add(head_c, v_add(v_add(v_mul(r, sx * 38), v_mul(f, 105)), v_mul(u, 8)))
            seg3(g, cam, fang0, v_add(fang0, v_add(v_mul(u, 70 * jaw), v_mul(f, -10))), INK, 6, 1)
    # eyes: small, gold, slit pupils, glowing on BOOM
    glow = 1 + 1.8 * math.exp(-e * 5) * (t > tb)
    for sx in (-1, 1):
        ec = v_add(head_c, v_add(v_add(v_mul(r, sx * 72), v_mul(U, 26)), v_mul(f, 45)))
        point3(g, cam, ec, 15 * glow, GOLDL, 1)
        point3(g, cam, ec, 44 * glow, GOLD, 0.22)
        seg3(g, cam, v_add(ec, v_mul(U, 10)), v_add(ec, v_mul(U, -10)), BG, 4, 0.9)
    # forked tongue flicks while it sways
    fl = max(0.0, math.sin((t - t0) * 7.5)) ** 3 * (1 - strike)
    if fl > 0.05 and jaw < 0.3:
        tb0 = v_add(head_c, v_mul(f, 130))
        tm = v_add(tb0, v_mul(f, 120 * fl))
        seg3(g, cam, tb0, tm, GOLDL, 4, 1)
        for sx in (-1, 1):
            seg3(g, cam, tm, v_add(tm, v_add(v_mul(f, 50 * fl), v_mul(r, sx * 32 * fl))), GOLDL, 3, 1)
    if t > tb:
        for k in range(4):
            R_ = e * 3200 - k * 280
            if R_ > 0:
                poly3(g, cam, [(R_ * math.cos(a), 430, 560 + R_ * math.sin(a)) for a in [2 * math.pi * q / 64 for q in range(65)]], GOLD, 5, clamp(1 - e * 1.2))
        g.flash = 0.12 * math.exp(-e * 9); g.flash_c = GOLDL
    word3(g, cam, "ROKO'S BASILISK", (0, -1500, 1000), (1, 0, 0), (0, -1, 0), 1600, 120, GOLD, 'sans', 0.22)
    c, rr, uu = ahead(cam, 1000)
    lyric3x(g, cam, t, 18, v_add(c, v_mul(cam.u, 330)), rr, uu, 1650, 120, INK, {'basilisk': GOLD, 'boom': GOLD}, depth=70)



# ======================================================== v56: sculpted cobra scene
def s_basilisk(g, t, lt):
    import cobra
    t0 = T0(18); tb = WT(18, 4); tE = T0(19)
    rise = eio(prog(t, t0 - 0.15, t0 + 0.65))
    hood = 0.15 + 0.7 * eo(prog(t, t0 + 0.3, t0 + 0.85)) + 0.15 * eo(prog(t, tb - 0.12, tb + 0.02))
    antic = eio(prog(t, tb - 0.3, tb - 0.03)) * (1 - prog(t, tb - 0.03, tb + 0.02))
    st = eback(prog(t, tb - 0.03, tb + 0.13), 1.2) * (1 - eio(prog(t, tb + 0.25, tb + 0.68)))
    calm = (1 - antic) * (1 - st)
    ph = 2 * math.pi * 0.8 * (t - t0)
    sway = 150 * math.sin(ph) * calm * rise
    yaw = 0.22 * math.sin(ph - 0.7) * calm
    lean = 50 * math.sin(2 * ph) * calm + 200 * antic
    jaw = max(0.55 * antic, 1.0 * st, 0.25 * prog(t, tb + 0.2, tE) * (1 - prog(t, tb + 0.55, tE)))
    jaw = max(jaw, 0.0)
    e = max(0.0, t - tb)
    tongue = (max(0.0, math.sin((t - t0) * 11)) ** 3) * (1 - min(1, jaw * 4)) * rise
    pose = dict(rise=rise, sway=sway, lean=lean, strike=st, hood=hood, jaw=jaw, tongue=tongue, yaw=yaw,
                pitch=0.12 * antic - 0.38 * (1 - st), slide=0.25 * math.sin(ph * 0.5), eyeglow=1 + 2.0 * math.exp(-e * 4) * (t > tb))
    keys = [(t0 - 0.15, (-900, 200, -800), (0, -160, 500), 52, -0.04),
            (t0 + 0.7, (-330, 90, -1050), (0, -380, 420), 52, -0.02),
            (tb - 0.05, (100, 60, -1150), (0, -470, 380), 55, 0.0),
            (tE, (430, 90, -1400), (0, -500, 380), 57, 0.03)]
    cam = cam_at(t, keys, shake=60 * math.exp(-e * 5) * (t > tb))
    env(g, cam)
    # backdrop: huge faint title + a gold halo behind the hood
    word3(g, cam, "ROKO'S BASILISK", (0, -700, 3600), (1, 0, 0), (0, -1, 0), 5200, 300, GOLD, 'sans', 0.035)
    hc = cam.p((sway * 0.8, lerp(GROUND_C - 300, -280, rise), 650 - 330 + 120))
    if hc is not None:
        k = hc[2] / (cam.F / 1000.0)
        for j in range(9):
            g.circle(hc[0], hc[1], (130 + 70 * j) * k * (1 + 0.15 * math.exp(-e * 4) * (t > tb)), fill=GOLD, a=0.028)
    # floor rings
    for j in range(7):
        R_ = 800 + 260 * j
        poly3(g, cam, [(R_ * math.cos(a), GROUND_C, 650 + R_ * math.sin(a)) for a in [2 * math.pi * q / 72 for q in range(73)]], GOLDD, 2, 0.35 * (1 - j / 7))
    if t > tb:
        for k in range(4):
            R_ = e * 3400 - k * 300
            if R_ > 0:
                poly3(g, cam, [(R_ * math.cos(a), GROUND_C, 650 + R_ * math.sin(a)) for a in [2 * math.pi * q / 72 for q in range(73)]], GOLD, 5, clamp(1 - e * 1.3))
        g.flash = 0.14 * math.exp(-e * 9); g.flash_c = GOLDL
    cobra.draw_cobra(g, cam, pose, t)
    c, rr, uu = ahead(cam, 1000)
    lyric3x(g, cam, t, 18, v_add(c, v_mul(cam.u, 330)), rr, uu, 1650, 120, INK, {'basilisk': GOLD, 'boom': GOLD}, depth=70)


GROUND_C = 430.0


# ======================================================== COUNCIL: "safe enough, we reckoned" 69.9 - 72.3
NCOUNCIL = 7


def s_council(g, t, lt):
    t0 = T0(22); tr = WT(22, 5); tE = T0(23)
    keys = [(t0, orbit((0, 0, 0), 2200, -0.7, 0.55), (0, 50, 0), 50, 0.0),
            (tr, orbit((0, 0, 0), 1700, 0.1, 0.45), (0, -50, 0), 54, 0.03),
            (tE, orbit((0, 0, 0), 1500, 0.5, 0.3), (0, -150, 0), 58, -0.02)]
    cam = cam_at(t, keys)
    env(g, cam)
    # v67: table pedestal drawn in its own pass first (camera is always above the table), so it can never paint over
    # the tabletop; tabletop split into tiles so it sorts correctly against the members.
    FLOOR = 500.0
    L = SFaces()
    L.cyl((0, 385, 0), 70, 230, (46, 44, 40), None, 14)
    L.cyl((0, FLOOR - 10, 0), 200, 20, (40, 38, 34), None, 20)
    L.draw(g, cam)
    for j in range(7):   # faint floor rings so the room has a ground
        R_ = 980 + 120 * j
        poly3(g, cam, [(R_ * math.cos(q), FLOOR, R_ * math.sin(q)) for q in [2 * math.pi * k / 72 for k in range(73)]], GOLDD, 1.5, 0.28 * (1 - j / 7))
    F = SFaces()
    TR, TY0, TY1, NS = 560, 230, 270, 28
    rings = (0, 200, 380, 480, TR)
    tcol = (78, 70, 56)
    for k in range(NS):
        q0, q1 = 2 * math.pi * k / NS, 2 * math.pi * (k + 1) / NS
        c0, s0, c1, s1 = math.cos(q0), math.sin(q0), math.cos(q1), math.sin(q1)
        for ri in range(len(rings) - 1):
            r0, r1 = rings[ri], rings[ri + 1]
            col = (90, 80, 60) if ri == len(rings) - 2 else tcol
            F.sq([(r0 * c0, TY0, r0 * s0), (r1 * c0, TY0, r1 * s0), (r1 * c1, TY0, r1 * s1), (r0 * c1, TY0, r0 * s1)], col, None, amb=0.5)
        F.sq([(TR * c0, TY0, TR * s0), (TR * c1, TY0, TR * s1), (TR * c1, TY1, TR * s1), (TR * c0, TY1, TR * s0)], (60, 54, 42), GOLDD, 1.0)
    heads = []
    robe_y = (FLOOR, 400, 280, 160, 60, 20, -5)
    robe_r = (175, 160, 130, 112, 128, 70, 38)
    for i in range(NCOUNCIL):
        a = 2 * math.pi * i / NCOUNCIL + 0.2
        c = (800 * math.sin(a), 0, 800 * math.cos(a))
        tg = (math.cos(a), 0, -math.sin(a)); inw = (-math.sin(a), 0, -math.cos(a))
        def Lp(x, y, z, c=c, tg=tg, inw=inw):
            return (c[0] + tg[0] * x + inw[0] * z, y, c[2] + tg[2] * x + inw[2] * z)
        tv = WT(22, 2) + i * 0.13
        nod = math.sin(clamp((t - tv) / 0.35) * math.pi) if t > tv else 0.0
        voted = clamp((t - tv) / 0.25) if t > tv else 0.0
        # robed body (tapered), gold collar
        F.tube([Lp(0, y, 0) for y in robe_y], 0, (128, 126, 118), None, n=12, rs=list(robe_r), amb=0.3)
        poly3(g, cam, [Lp(132 * math.cos(q), 62, 132 * math.sin(q)) for q in [2 * math.pi * k / 24 for k in range(25)]], GOLD, 3, 0.35 + 0.65 * voted)
        # head: dark face inside a hood, glowing visor facing the table; nods forward when voting
        hc = Lp(0, -80 + 30 * nod, 28 * nod)
        heads.append(hc)
        F.sphere(hc, 68, (34, 33, 31), None, 7, 14, amb=0.4)
        hood_c = Lp(0, -88 + 30 * nod, -14 + 28 * nod)
        HP = []
        nl, nlon = 6, 14
        for li_ in range(nl + 1):
            th = math.pi * 0.72 * li_ / nl
            row = []
            for j in range(nlon + 1):
                ph = math.radians(55 + (360 - 110) * j / nlon)   # open at the front (local +z)
                row.append(Lp(92 * math.sin(th) * math.sin(ph), hood_c[1] - 92 * math.cos(th) * 1.08, -14 + 28 * nod + 92 * math.sin(th) * math.cos(ph)))
            HP.append(row)
        for li_ in range(nl):
            for j in range(nlon):
                F.sq([HP[li_][j], HP[li_][j + 1], HP[li_ + 1][j + 1], HP[li_ + 1][j]], (150, 148, 140), None, amb=0.3)
        vis = mix((140, 100, 20), GOLDL, 0.4 + 0.6 * voted)
        z0 = 28 * nod
        yv, hv = hc[1] - 6, 12
        for j in range(8):
            p0, p1 = math.radians(-55 + 110 * j / 8), math.radians(-55 + 110 * (j + 1) / 8)
            pm = (p0 + p1) / 2
            nrm = Lp(math.sin(pm), 0, math.cos(pm)); nrm = v_sub(nrm, Lp(0, 0, 0))
            mid = Lp(74 * math.sin(pm), yv, z0 + 74 * math.cos(pm))
            if v_dot(nrm, v_sub(cam.eye, mid)) <= 0:
                continue   # visor segment faces away from camera
            F.f.append(([Lp(74 * math.sin(p0), yv - hv, z0 + 74 * math.cos(p0)), Lp(74 * math.sin(p1), yv - hv, z0 + 74 * math.cos(p1)),
                         Lp(74 * math.sin(p1), yv + hv, z0 + 74 * math.cos(p1)), Lp(74 * math.sin(p0), yv + hv, z0 + 74 * math.cos(p0))], None, vis, 1, 1))
        # forearms resting on the table edge
        for sx in (-1, 1):
            F.tube([Lp(sx * 110, 120, 20), Lp(sx * 95, 215, 150), Lp(sx * 60, 222, 255)], 0, (118, 116, 108), None, n=6, rs=[34, 30, 26], amb=0.3)
            F.sphere(Lp(sx * 55, 218, 275), 26, (40, 39, 36), None, 4, 8, amb=0.4)
    F.draw(g, cam)
    # visor glow + halo ring per member
    for i, h in enumerate(heads):
        tv = WT(22, 2) + i * 0.13
        voted = clamp((t - tv) / 0.25) if t > tv else 0.0
        hp = cam.p(h)
        aa = 2 * math.pi * i / NCOUNCIL + 0.2
        fc = v_dot(v_norm((-math.sin(aa), 0, -math.cos(aa))), v_norm(v_sub(cam.eye, h)))
        if hp is not None and fc > 0:   # visor glow only when the face is toward camera
            kk = hp[2] / (cam.F / 1000.0)
            g.circle(hp[0], hp[1], 120 * kk, fill=GOLD, a=(0.05 + 0.06 * voted) * fc)
        a = 2 * math.pi * i / NCOUNCIL + 0.2
        hr = 70 + 6 * math.sin(t * 3 + i)
        poly3(g, cam, [v_add(h, (hr * math.cos(q), -125 - 4 * math.sin(t * 2 + i), hr * math.sin(q))) for q in [2 * math.pi * k / 28 for k in range(29)]], GOLD, 2, 0.25 + 0.6 * voted)
    # conversation: packets travelling between members
    for k in range(10):
        a = int(hsh(k, int(t * 3)) * NCOUNCIL); b = (a + 1 + int(hsh(k, int(t * 3) + 7) * (NCOUNCIL - 1))) % NCOUNCIL
        A = v_add(heads[a], (0, -100, 0)); Bp = v_add(heads[b], (0, -100, 0))
        mid = v_add(v_lerp(A, Bp, 0.5), (0, -260, 0))
        arc = [v_lerp(v_lerp(A, mid, q / 16), v_lerp(mid, Bp, q / 16), q / 16) for q in range(17)]
        poly3(g, cam, arc, GRID2, 1.5, 0.8)
        ph = (t * 2.5 + hsh(k, 5)) % 1.0
        point3(g, cam, arc[int(ph * 16)], 8, GOLD, 0.9)
    # each member's vote: ? -> check
    for i, h in enumerate(heads):
        tv = WT(22, 2) + i * 0.13
        ok = t > tv
        p = v_add(h, (0, -230, 0))
        if ok:
            k = eback(clamp((t - tv) / 0.2))
            r_, u_ = facing(p, cam.eye)
            ck = [v_add(p, v_add(v_mul(r_, a * 45 * k), v_mul(u_, b * 45 * k))) for a, b in ((-1, 0), (-0.3, -0.7), (1.1, 0.9))]
            poly3(g, cam, ck, GOLD, 9, 1)
        else:
            text3(g, cam, '?', p, 70, DIM, 'sans', 1)
    # verdict hologram over the table
    v = eback(prog(t, tr - 0.05, tr + 0.3))
    if v > 0:
        word3(g, cam, 'SAFE ENOUGH', (0, -350, 0), *facing((0, -350, 0), cam.eye), 900 * v, 160, GOLD, 'sans', 1, x=True, depth=60, n=6)
        text3(g, cam, 'VOTE %d/%d  //  CONSENSUS REACHED' % (NCOUNCIL, NCOUNCIL), (0, -200, 0), 26, INK, 'mono', v)
    else:
        text3(g, cam, 'RISK REVIEW  //  DELIBERATING' + '.' * (int(t * 4) % 4), (0, -250, 0), 26, DIM, 'mono')
    c, r, u = ahead(cam, 1050)
    lyric3x(g, cam, t, 22, v_add(c, v_mul(cam.u, 340)), r, u, 1700, 120, INK, {'safe': GOLD, 'reckoned': GOLD}, depth=60)


# ======================================================== MLP 72.3 - 77.75 (paper)
LAYERS = [4, 6, 7, 6, 3]


def s_mlp(g, t, lt):
    t0 = T0(23); tb = WT(23, 2); trp = WT(23, 3); tE = T0(24)
    # v68: network sits lower (NY) and the camera stays wider, so the caption band at the top stays clear
    NY = 170
    keys = [(t0, orbit((0, NY, 0), 2300, -0.8, 0.25), (0, 0, 0), 50, 0.0),
            (tb, orbit((0, NY, 0), 2200, 0.0, 0.1), (0, 10, 0), 54, 0.0),
            (trp, orbit((0, NY, 0), 2050, 0.25, 0.05), (0, 20, 0), 56, 0.02),
            (tE, orbit((0, NY, 0), 1950, 0.6, 0.15), (0, 30, 0), 60, -0.03)]
    cam = cam_at(t, keys, shake=10 * (t > trp))
    nL = len(LAYERS)
    # wave position (in layer units) and direction
    if t < tb:
        pos = prog(t, t0 + 0.1, tb - 0.1) * (nL - 1); dirn = 1; lab = 'FORWARD \u2192'
    elif t < trp:
        pos = (1 - prog(t, tb, trp)) * (nL - 1); dirn = -1; lab = '\u2190 BACKWARD'
    else:
        e = t - trp
        ph = e * (3 + e * 7)  # accelerating oscillation
        k = int(ph)
        fr = ph - k
        dirn = 1 if k % 2 == 0 else -1
        pos = (fr if dirn > 0 else 1 - fr) * (nL - 1)
        lab = ('FWD \u2192' if dirn > 0 else '\u2190 BWD') + '  REPEAT \u00d7%d' % (k + 1)
    nodes = [[(-900 + li * 450, NY + (k - (n - 1) / 2) * 125, 0) for k in range(n)] for li, n in enumerate(LAYERS)]
    for li in range(nL - 1):
        for a in nodes[li]:
            for b in nodes[li + 1]:
                hot = abs(pos - (li + 0.5)) < 0.55
                seg3(g, cam, a, b, GOLD if hot else PGRID, 3 if hot else 1.2, 1)
    F = SFaces()
    for li, L_ in enumerate(nodes):
        hot = abs(pos - li) < 0.5
        for p in L_:
            F.sphere(p, 40, GOLD if hot else (232, 230, 224), None, 5, 10, amb=0.45)
    F.draw(g, cam)
    text3(g, cam, lab, (0, NY + 640, 0), 40, BLACK if dirn > 0 else GOLDD, 'monox')
    names = ['INPUT', 'HIDDEN 1', 'HIDDEN 2', 'HIDDEN 3', 'OUTPUT']
    for li in range(nL):
        text3(g, cam, names[li], (-900 + li * 450, NY + 500, 0), 24, (90, 88, 80), 'mono')
    if t > trp:
        text3(g, cam, 'EPOCH %s' % format(int((t - trp) ** 3 * 90000), ','), (0, NY + 730, 0), 34, BLACK, 'mono')
    hl = {'forward': GOLD, 'mlp,': GOLD, 'backward,': GOLD, 'repeat': GOLD}
    c, r, u = ahead(cam, 1100)
    lyric3(g, cam, t, 23, v_add(c, v_mul(cam.u, -330)), r, u, 1900, 120, INK, hl=hl, light=True)
    g.hud = dict(light=True)
    g.post = dict(glow=0.15, grain=0.02, vig=0.4)


# ======================================================== VON NEUMANN 77.75 - 81.25 (paper)
def s_vn(g, t, lt):
    t0 = T0(24); to = WT(24, 3); tE = T0(25)
    obs = prog(t, to - 0.05, to + 1.0)
    keys = [(t0, (-1400, -900, -2000), (0, -300, 0), 50, 0.04),
            (to, (-400, -500, -1300), (0, -250, 0), 56, 0.0),
            (tE, (700, -1300, -1500), (0, 0, 0), 56, -0.04)]
    cam = cam_at(t, keys, shake=30 * math.exp(-max(0, t - to) * 5) * (t > to))
    F = SFaces()
    F.sbox((0, 330, 0), (1400, 260, 1100), (236, 234, 228), (120, 118, 110), 1.2)
    F.draw(g, cam)
    G2 = SFaces()
    for i, (nm, c, s) in enumerate(VN):
        e = max(0.0, t - to - 0.05 * i) if t > to else 0.0
        fall = 0.5 * 4000 * e * e
        cc = (c[0] * 0.9 + (hsh(i, 1) - 0.5) * 900 * e, 200 - s[1] / 2 - 300 * e + fall * 0.35, c[2] * 0.9 - 500 * e)
        G2.sbox(cc, s, (226, 224, 218), BLACK, 1.6,
                xf=lambda v, i=i, e=e: rot3(v, e * 3 * (hsh(i, 2) - 0.5), e * 2 * (hsh(i, 4) - 0.5), e * 4 * (hsh(i, 3) - 0.5)), amb=0.5)
    G2.draw(g, cam)
    if t < to + 0.1:
        for i, (nm, c, s) in enumerate(VN):
            text3(g, cam, nm, (c[0] * 0.9, 200 - s[1] - 30, c[2] * 0.9), 30, BLACK, 'mono')
        poly3(g, cam, [(-380, 150, -380), (-380, 150, 300), (380, 150, 300), (380, 150, -380)], GOLD, 5, 1)
    # glass case: edges, shattering on 'obsolete'
    C = [(sx * 650, sy, sz * 550) for sx in (-1, 1) for sy in (200, -650) for sz in (-1, 1)]
    for a in range(8):
        for b in range(a + 1, 8):
            d = sum(1 for k in range(3) if C[a][k] != C[b][k])
            if d == 1:
                off = v_mul((hsh(a, b) - 0.5, -hsh(a, b + 1), hsh(a, b + 2) - 0.5), 1600 * obs)
                seg3(g, cam, v_add(C[a], off), v_add(C[b], off), (150, 148, 140), 2, 1 - obs)
    text3(g, cam, 'EXHIBIT 1945  \u2014  VON NEUMANN ARCHITECTURE', (0, 480, -560), 26, (90, 88, 80), 'mono')
    # v69: big 3D 'OBSOLETE' stamp removed (the lyric caption already says it)
    hl = {"neumann's": GOLD, 'obsolete': GOLD}
    c, r, u = ahead(cam, 1100)
    lyric3(g, cam, t, 24, v_add(c, v_mul(cam.u, -340)), r, u, 1900, 120, INK, hl=hl, light=True)
    g.hud = dict(light=True)
    g.post = dict(glow=0.15, grain=0.02, vig=0.4)


# ======================================================== GATO: lets go over the cliff 90.0 - 95.3
def s_gato(g, t, lt):
    t0 = T0(27); tg = WT(27, 5); tE = T0(28)
    rel = t > tg
    e = max(0.0, t - tg)
    keys = [(t0, (900, -500, -2300), (-200, -120, 0), 50, 0.0),
            (92.6, (1000, -450, -2150), (-150, -60, 0), 52, 0.03),
            (tg, (950, -450, -1900), (0, -20, 0), 54, 0.0),
            (tE, (700, -900, -900), (300, 1500, 0), 64, 0.0)]
    cam = cam_at(t, keys, shake=4)
    if t > tg:
        e0 = t - tg
        fy = -470 + 0.5 * 5200 * e0 * e0
        eye0, tg0, fov0, _ = path(tg, keys)
        uu = eo(clamp(e0 / 0.9))
        cam = Cam3(v_lerp(eye0, (900, -1100, -1300), uu), v_lerp(tg0, (260, min(fy, 3400), 0), uu), lerp(fov0, 62, uu), 0.0)
    # v84: the ledge is now the roof of a gold NVDA tower rising out of the NVDA chart-city (callback to the
    # "NVDA to the moon" scene); the wireframe skyline sits far below and the moon hangs over it.
    GYd = 7200.0
    C = Faces()
    for i in range(-7, 8):
        for j in range(-2, 9):
            cx = 900 + j * 620 + (hsh(i * 13 + j, 5) - 0.5) * 120
            cz = i * 620 + (hsh(i * 7 + j, 6) - 0.5) * 120
            if cx < 600 and abs(cz) < 2200:
                continue
            hgt = 1200 + hsh(i * 31 + j, 1) * 4200 * (1 + j / 10)
            hgt = min(hgt, GYd - 900) if cx < 2400 else min(hgt * 1.25, GYd + 250)
            gold = hsh(i, j + 11) < 0.18
            C.box((cx, GYd - hgt / 2, cz), (360, hgt, 360), GOLD if gold else (90, 90, 84), BG, 1.6)
    for i in range(-3, 4):
        for j in range(-4, 5):
            cx = -1600 + j * 650; cz = 2600 * (1 if i >= 0 else -1) + i * 600
            hgt = 1500 + hsh(i * 17 + j, 9) * 3800
            C.box((cx, GYd - hgt / 2, cz), (380, hgt, 380), (90, 90, 84), BG, 1.6)
    C.draw(g, cam, fog=14000)
    # ticker line climbing through the skyline + moon
    pts = [(700 + k * 180, GYd - 1600 - 95 * k - 260 * math.sin(k * 0.45), 2400) for k in range(34)]
    poly3(g, cam, pts, GOLD, 4, 0.8)
    mesh3(g, cam, *sphere_mesh(700, 9, 18), c=INK, w=2, al=0.85, xf=xform((1500, -2500, 7000), ry=t * 0.4))
    F = SFaces()
    _panels(F, (-3200, 0, -1600), (1, 0, 0), (0, 0, 1), 4, 4, 800, 800, (46, 45, 42), (60, 58, 52))
    _panels(F, (0, 0, -1600), (0, 1, 0), (0, 0, 1), 8, 4, 900, 800, (36, 35, 32), (58, 55, 46))
    F.draw(g, cam)
    # lit window strips down the tower face, gold roof edge and parapet rail
    for r_ in range(1, 14):
        y_ = r_ * 520
        for c_ in range(-7, 8):
            if hsh(r_ * 19 + c_, 3) < 0.32:
                z_ = c_ * 210
                seg3(g, cam, (2, y_, z_ - 70), (2, y_, z_ + 70), GOLD, 5, 0.75, fog=9000)
    seg3(g, cam, (0, 0, -1600), (0, 0, 1600), GOLD, 4, 1)
    # v85: solid parapet + rooftop plant (HVAC units with spinning fans, water tank on legs, antenna mast)
    RP = CFaces()
    RP.sbox((-25, -40, 0), (50, 80, 3200), (58, 57, 53), None, amb=0.4)
    RP.sbox((-1600, -40, -1575), (3200, 80, 50), (58, 57, 53), None, amb=0.4)
    for hx, hz in ((-1750, 650), (-1250, 1250), (-2300, -350)):
        RP.sbox((hx, -120, hz), (480, 240, 380), (74, 74, 70), (60, 60, 56), 1.0, amb=0.35)
    for lx in (-3000, -2700):
        for lz in (-850, -550):
            RP.sbox((lx, -260, lz), (24, 520, 24), (66, 66, 62), None, amb=0.4)
    RP.cyl((-2850, -800, -700), 280, 560, (70, 66, 58), None, 16, amb=0.3)
    RP.draw(g, cam)
    seg3(g, cam, (0, -80, -1600), (0, -80, 1600), GOLD, 3, 0.9)
    for hx, hz in ((-1750, 650), (-1250, 1250), (-2300, -350)):
        ring = [(hx + 130 * math.cos(q * math.pi / 8), -242, hz + 130 * math.sin(q * math.pi / 8)) for q in range(17)]
        poly3(g, cam, ring, GOLDD, 2, 0.9)
        for q in range(3):
            an = t * 9 + q * 2.094
            seg3(g, cam, (hx, -242, hz), (hx + 120 * math.cos(an), -242, hz + 120 * math.sin(an)), (120, 120, 112), 3, 0.9)
    poly3(g, cam, [(-2850 + 282 * math.cos(q * math.pi / 8), -1080, -700 + 282 * math.sin(q * math.pi / 8)) for q in range(17)], GOLDD, 2, 0.8)
    seg3(g, cam, (-2950, 0, 1350), (-2950, -2100, 1350), (90, 90, 86), 5, 1)
    for q in range(1, 5):
        seg3(g, cam, (-2950, -q * 420, 1350), (-2950 + 140, -q * 420 + 140, 1350), (90, 90, 86), 3, 0.9)
    point3(g, cam, (-2950, -2120, 1350), 9, GOLDL, 0.6 + 0.25 * math.sin(t * 2.5))
    # city street grid glowing at the foot of the skyline
    for q in range(-6, 7):
        seg3(g, cam, (500, GYd, q * 620 - 310), (9000, GYd, q * 620 - 310), GOLDD, 2, 0.5, fog=14000)
    for q in range(0, 14):
        seg3(g, cam, (590 + q * 620, GYd, -4000), (590 + q * 620, GYd, 4000), GOLDD, 2, 0.5, fog=14000)
    # rooftop sign at the back of the roof
    SB = SFaces()
    for zz in (700, 1500):
        SB.sbox((-2500, -500, zz), (30, 1000, 30), (70, 70, 66), None, amb=0.4)
    SB.sbox((-2500, -1060, 1100), (24, 300, 1000), (30, 30, 28), GOLD, 2.0, amb=0.5)
    SB.draw(g, cam)
    word3(g, cam, 'NVDA \u25b2', (-2486, -1060, 1100), (0, 0, 1), (0, -1, 0), 860, 200, GOLD, 'mono', 1)
    for i in range(70):
        p = (300 + hsh(i, 1) * 3000, 4000 - ((t * 260 + i * 97) % 4600), (hsh(i, 2) - 0.5) * 3600)
        point3(g, cam, p, 3, GRID2, 0.6)
    # --- v85 Gato overhaul: DeepMind's generalist agent as one machine that does every task - the original
    # task cube is now its head (slowly turning, a token-stream screen on the front, task names on its faces) on a
    # rotating torso over a tracked base, with a Sawyer-style 7-joint arm (the robotics task) holding the figure
    # and a folded tool arm on the other side.
    b = 6 * math.sin(t * 2.0)
    STL = (104, 104, 98); DRK = (52, 52, 49); MID = (78, 78, 74)
    BX = -900.0
    G2 = CFaces()
    zx = lambda v: (v[0], v[2], v[1])     # cylinder axis -> z
    for tz in (-185, 185):
        G2.sbox((BX, -70, tz), (600, 110, 120), DRK, GOLDD, 1.2, amb=0.35)
        for wx in (-230, -77, 77, 230):
            G2.cyl((BX + wx, -62, tz + (66 if tz > 0 else -66)), 48, 14, MID, None, 12, xf=zx, amb=0.35)
        for wx in range(-280, 300, 70):
            seg3(g, cam, (BX + wx, -128, tz - 60), (BX + wx, -128, tz + 60), (70, 70, 66), 2, 0.6)
    G2.sbox((BX, -150, 0), (540, 50, 420), STL, GOLDD, 1.2, amb=0.3)
    G2.cyl((BX, -205, 0), 150, 40, GOLDD, None, 16, amb=0.35)
    G2.cyl((BX, -330 + b * 0.3, 0), 112, 230, STL, None, 14, amb=0.3)
    G2.sbox((BX, -495 + b * 0.5, 0), (300, 110, 380), STL, GOLD, 1.4, amb=0.3)
    # head: the task cube
    HC = (BX, -720 + b, 0)
    ry = 0.35 + 0.12 * math.sin(t * 0.7)
    rxf = lambda v: rot3(v, 0.06, ry, 0)
    G2.cyl((BX, -580 + b, 0), 60, 60, DRK, None, 10, amb=0.35)
    G2.sbox(HC, (330, 330, 330), STL, GOLD, 2.0, xf=rxf, amb=0.3)
    # token-stream screen on the face toward the edge (+x before rotation)
    nF = rxf((1, 0, 0)); uF = rxf((0, -1, 0)); rF = v_cross(uF, nF)
    sc0 = v_add(HC, v_mul(nF, 168))
    G2.cur = HC
    G2.sq([v_add(sc0, v_add(v_mul(rF, sx * 130), v_mul(uF, sy * 130))) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], (16, 16, 15), GOLDD, 1.0, amb=1.0)
    sc1 = v_add(HC, v_mul(nF, 171))
    for i_ in range(6):
        for j_ in range(6):
            on = hsh(i_ * 7 + j_ + int(t * 8) * 37, 4) < 0.45
            if not on:
                continue
            cc_ = v_add(sc1, v_add(v_mul(rF, -100 + i_ * 40), v_mul(uF, 100 - j_ * 40)))
            G2.sq([v_add(cc_, v_add(v_mul(rF, sx * 14), v_mul(uF, sy * 14))) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], GOLDL if (i_ + j_) % 3 else GOLD, None, 1.0, amb=1.0)
    G2.cur = None
    at = v_add(HC, v_mul(uF, 165))
    G2.tube([at, v_add(at, (0, -170, 0))], 7, DRK, None, 5)
    G2.sphere(v_add(at, (0, -175, 0)), 16, GOLD, None, 3, 6, amb=0.8)
    # Sawyer-style arm on the camera side
    sh = (BX + 120, -520 + b * 0.5, -200)
    el = (-330, -880, -150)
    wr = (150, -720, -50)
    hand = (260, -560 + 15 * math.sin(t * 1.5), 0)
    G2.cyl(sh, 92, 110, GOLDD, None, 14, xf=zx, amb=0.35)
    G2.tube([sh, v_lerp(sh, el, 0.5), el], 62, STL, None, 10, rs=[70, 60, 50])
    G2.tube([v_lerp(sh, el, 0.12), v_lerp(sh, el, 0.85)], 16, GOLD, None, 5)
    G2.cyl(el, 72, 120, MID, None, 14, xf=zx, amb=0.35)
    G2.tube([el, v_lerp(el, wr, 0.5), wr], 48, STL, None, 10, rs=[52, 44, 38])
    G2.sphere(wr, 46, GOLD, None, 4, 10)
    G2.tube([wr, hand], 34, MID, None, 8)
    G2.cyl(hand, 58, 40, DRK, None, 12, amb=0.35)
    op = eo(prog(t, tg - 0.05, tg + 0.2))
    for k in range(3):
        a = 2 * math.pi * k / 3
        d = (math.cos(a) * (0.5 + op * 0.9), 1.0 - op * 0.6, math.sin(a) * (0.5 + op * 0.9))
        f1 = v_add(hand, v_mul(v_norm(d), 110)); f2 = v_add(f1, v_mul(v_norm((d[0] * (1 - op), 1, d[2] * (1 - op))), 80))
        G2.tube([hand, f1, f2], 16, GOLD, None, 5)
    # folded tool arm on the far side
    s2_ = (BX + 60, -500 + b * 0.5, 200); e2_ = (BX + 260, -330, 290); w2_ = (BX + 380, -440, 250)
    G2.cyl(s2_, 70, 80, GOLDD, None, 12, xf=zx, amb=0.35)
    G2.tube([s2_, e2_], 40, STL, None, 8)
    G2.sphere(e2_, 44, GOLD, None, 4, 8)
    G2.tube([e2_, w2_], 32, STL, None, 8)
    G2.sbox(w2_, (70, 70, 70), DRK, GOLDD, 1.0, amb=0.35)
    G2.draw(g, cam)
    # task names on the head's visible faces
    for k, (n, up) in enumerate((((0, 0, -1), (0, -1, 0)), ((0, 0, 1), (0, -1, 0)), ((0, -1, 0), (-1, 0, 0)), ((-1, 0, 0), (0, -1, 0)))):
        nn = rxf(n); uu = rxf(up)
        cc = v_add(HC, v_mul(nn, 168))
        if v_dot(nn, v_sub(cam.eye, cc)) > 0:
            word3(g, cam, FACES_G[[0, 3, 2, 4][k]], cc, v_cross(uu, nn), uu, 270, 70, GOLD if k == 0 else INK, 'mono', 1)
    text3(g, cam, 'GATO  //  604 TASKS', (-900, -1170, 0), 30, GOLD, 'mono')
    # the held character
    fall = 0.5 * 5200 * e * e
    sw = math.sin(t * 2.3) * 0.12
    top = (hand[0], hand[1] + 90 + fall, 0)
    P = SFaces()
    kick = prog(t, WT(27, 1), WT(27, 1) + 0.3) * (1 - 0.5 * rel)
    pose = _pose((top[0] + 400 * sw, top[1] + 480, 0), 1.0, arms_up=1.0, kick=kick + 0.3 * rel, t=t)
    if rel:
        spin = e * 3
        pose = {k: v_add(top, rot3(v_sub(p, top), 0, spin * 0.4, spin)) for k, p in pose.items()}
    else:
        pose = {k: v_add(top, rot3(v_sub(p, top), 0, 0, sw)) for k, p in pose.items()}
    humanoid(P, SKIN, pose)
    P.draw(g, cam)
    if rel:
        text3(g, cam, 'RELEASED', (hand[0] + 300, hand[1] - 80, 0), 30, GOLD, 'monox', clamp(1.5 - e))
    c, r, u = ahead(cam, 1100)
    lyric3x(g, cam, t, 27, v_add(c, v_mul(cam.u, -110)), r, u, 1700, 120, INK, {'gato,': GOLD, 'go': GOLD}, depth=60)


# ======================================================== PAPERCLIPS fill the room 96.9 - 99.2
# v88 overhaul: an office being swallowed by a clip factory. Proper gem-clip geometry, a wire-spool bending machine
# pouring clips down a chute, a rising heightfield heap that buries a desk, chair, monitor and a person.
CR = (1100, 520, 1100)


def _gem_path():
    pts = []
    def seg(a, b, n=2):
        for k in range(n):
            pts.append((lerp(a[0], b[0], k / n), lerp(a[1], b[1], k / n)))
    def arc(cx, cy, r, a0, a1, n=5):
        for k in range(n):
            a = lerp(a0, a1, k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    seg((-0.2, 0.55), (-0.2, -0.75)); arc(0, -0.75, 0.2, math.pi, 2 * math.pi)
    seg((0.2, -0.75), (0.2, 0.95)); arc(-0.075, 0.95, 0.275, 0, math.pi)
    seg((-0.35, 0.95), (-0.35, -1.0)); arc(0, -1.0, 0.35, math.pi, 2 * math.pi)
    seg((0.35, -1.0), (0.35, 0.45), 1); pts.append((0.35, 0.45))
    return pts


GEM = _gem_path()


def _gem(F, c, s, rx, ry, rz, col, cam=None, r=None):
    pts = [v_add(c, rot3((x * s, y * s, 0), rx, ry, rz)) for x, y in GEM]
    if cam is not None:
        z = cam.cs(c)[2]
        if z < 220:
            return
    F.tube(pts, r if r else 0.07 * s, col, None, 4, amb=0.45)


def _heap(x, z, u, t):
    X, Y, Z = CR
    base = 25 + 400 * eio(u)
    d2 = (x - 820) ** 2 + (z - 560) ** 2
    mound = (130 + 220 * u) * math.exp(-d2 / (2 * (420 + 200 * u) ** 2))
    bump = 26 * math.sin(x * 0.011 + 1.3) * math.cos(z * 0.013) + 14 * math.sin(x * 0.03 + z * 0.021)
    return min(2 * Y - 60, base + mound + bump)


def s_clips(g, t, lt):
    from person import person
    t0 = T0(29); tE = T0(30)
    u = prog(t, t0, tE)
    X, Y, Z = CR
    keys = [(t0, (-980, -120, -1020), (260, 160, 520), 64, 0.02),
            (tE, (-820, -380, -860), (300, 20, 560), 68, -0.03)]
    cam = cam_at(t, keys, shake=2 + 5 * u)
    # ---- room shell: tiled floor, panelled walls with baseboard, ceiling with light strips
    S = SFaces()
    _panels(S, (-X, Y, -Z), (1, 0, 0), (0, 0, 1), 10, 10, 2 * X / 10, 2 * Z / 10, (36, 35, 33), (46, 45, 42))
    _panels(S, (-X, -Y, -Z), (1, 0, 0), (0, 0, 1), 4, 4, 2 * X / 4, 2 * Z / 4, (24, 24, 23), (32, 32, 30))
    for o, a, b in (((-X, -Y, Z), (1, 0, 0), (0, 1, 0)), ((X, -Y, -Z), (0, 0, 1), (0, 1, 0)),
                    ((-X, -Y, -Z), (0, 0, 1), (0, 1, 0)), ((-X, -Y, -Z), (1, 0, 0), (0, 1, 0))):
        _panels(S, o, a, b, 5, 3, 2 * X / 5, 2 * Y / 3, (44, 44, 41), (56, 56, 52))
    S.draw(g, cam)
    B = CFaces()
    B.sbox((0, Y - 25, Z - 8), (2 * X, 50, 16), (30, 30, 28), None, amb=0.4)                  # baseboards
    B.sbox((X - 8, Y - 25, 0), (16, 50, 2 * Z), (30, 30, 28), None, amb=0.4)
    for lx in (-450, 450):                                                                     # ceiling light strips
        B.sbox((lx, -Y + 12, 0), (120, 24, 1500), (150, 148, 138), None, amb=1.0)
    # wall display (counter) on the back wall, left of the machine
    B.sbox((-430, -250, Z - 14), (620, 260, 28), (18, 18, 17), None, amb=0.5)
    B.sbox((-430, -250, Z - 30), (640, 280, 4), GOLDD, None, amb=0.6)
    B.draw(g, cam)
    for lx in (-450, 450):
        for k in range(5):
            point3(g, cam, (lx, -Y + 40, -600 + k * 300), 200, GOLDL, 0.05)
    n = int(10 ** (3 + u * 9))
    word3(g, cam, 'CLIPS PRODUCED', (-430, -320, Z - 32), (1, 0, 0), (0, -1, 0), None, 30, DIM, 'mono', 0.95, scale=1.0)
    word3(g, cam, format(n, ','), (-430, -255, Z - 32), (1, 0, 0), (0, -1, 0), None, 56, GOLD, 'monox', 1, scale=1.0)
    word3(g, cam, 'OBJECTIVE: MAXIMIZE   //   HALT: DISABLED', (-430, -170, Z - 32), (1, 0, 0), (0, -1, 0), None, 18, DIM, 'mono', 0.9, scale=1.0)
    # ---- one depth-sorted set: machine, office furniture, person, heap, clips
    F = SFaces()
    MX, MZ = 760, Z - 200
    MET = (92, 92, 88); MET2 = (70, 70, 66)
    F.sbox((MX, Y - 350, MZ), (520, 700, 300), MET2, None, amb=0.4)                          # cabinet
    F.sbox((MX, Y - 560, MZ - 152), (440, 120, 6), (40, 40, 38), None, amb=0.5)               # vent panel
    for k in range(5):
        F.sbox((MX - 160 + k * 80, Y - 560, MZ - 156), (40, 90, 4), (24, 24, 23), None, amb=0.5)
    F.sbox((MX, Y - 705, MZ), (540, 20, 320), GOLDD, None, amb=0.6)                           # gold top rim
    spin = t * 6.0
    sp = (MX - 120, Y - 880, MZ + 20)                                                          # wire spool
    F.cyl(sp, 150, 70, MET, None, 16, xf=lambda v: rot3(v, math.pi / 2, 0, 0), amb=0.4)
    F.cyl(sp, 70, 74, GOLD, None, 12, xf=lambda v: rot3(v, math.pi / 2, 0, 0), amb=0.55)
    for k in range(5):
        a = spin + 2 * math.pi * k / 5
        F.tube([v_add(sp, (40 * math.cos(a), 40 * math.sin(a), -42)), v_add(sp, (140 * math.cos(a), 140 * math.sin(a), -42))], 9, MET2, None, 4)
    F.sbox((MX - 120, Y - 780, MZ + 20), (60, 160, 60), MET2, None, amb=0.4)                  # spool post
    hd = (MX + 120, Y - 800, MZ - 30)                                                          # bender head
    F.sbox(hd, (200, 150, 160), MET, None, amb=0.45)
    F.tube([v_add(sp, (110, -100, -40)), v_add(hd, (-100, -30, 0))], 6, GOLD, None, 4, amb=0.6)  # feed wire
    for k in (-1, 1):
        F.cyl(v_add(hd, (-60, -10 + 22 * k, -82)), 24, 20, (40, 40, 38), None, 10, xf=lambda v: rot3(v, math.pi / 2, 0, 0), amb=0.4)
    arm = math.sin(t * 22) * 0.6
    F.tube([v_add(hd, (100, 40, -40)), v_add(hd, (100 + 90 * math.cos(arm), 40 + 90 * math.sin(arm), -40))], 14, GOLD, None, 5, amb=0.6)
    ch0 = v_add(hd, (40, 70, -90)); ch1 = (MX + 60, Y - 560, MZ - 380)                        # chute
    F.tube([ch0, ch1], 0, MET, None, 6, rs=[46, 62], amb=0.4)
    F.tube([ch1, v_add(ch1, (0, 6, -14))], 0, GOLDD, None, 6, rs=[66, 66], amb=0.6)
    # desk + monitor + chair (left), person standing between desk and camera
    DX, DZ = -640, 420
    dt = Y - 330
    F.sbox((DX, dt, DZ), (720, 34, 400), (78, 70, 60), None, amb=0.4)
    for sx in (-1, 1):
        F.sbox((DX + sx * 330, (dt + Y) / 2, DZ), (36, Y - dt, 360), (52, 50, 46), None, amb=0.4)
    F.sbox((DX, dt - 80, DZ + 90), (24, 130, 24), (40, 40, 38), None)
    F.sbox((DX, dt - 230, DZ + 80), (380, 220, 20), (24, 24, 23), None, amb=0.4)
    scr = [(DX - 175, dt - 330, DZ + 68), (DX + 175, dt - 330, DZ + 68), (DX + 175, dt - 130, DZ + 68), (DX - 175, dt - 130, DZ + 68)]
    F.sq(scr, (34, 32, 26), None, amb=1.0)
    F.sbox((DX + 40, dt - 22, DZ - 40), (200, 10, 70), (60, 60, 56), None)                    # keyboard
    cx_, cz_ = DX + 60, DZ - 320                                                                # chair, pushed back
    F.sbox((cx_, Y - 230, cz_), (220, 26, 220), (40, 40, 38), None, amb=0.4)
    F.sbox((cx_, Y - 420, cz_ - 110), (220, 300, 24), (40, 40, 38), None, amb=0.4)
    F.tube([(cx_, Y - 220, cz_), (cx_, Y - 60, cz_)], 16, MET2, None, 6)
    for k in range(5):
        a = 2 * math.pi * k / 5
        F.tube([(cx_, Y - 50, cz_), (cx_ + 120 * math.cos(a), Y - 20, cz_ + 120 * math.sin(a))], 10, MET2, None, 4)
    # person: arms creeping up as the heap rises around them
    from s4b import _pose as _pp
    sw = math.sin(t * 3.1) * 0.15
    px, pz = -330, 120
    pose = _pp((px, Y - 220 * 1.35, pz), 1.35, arms_up=0.15 + 0.75 * eio(prog(t, t0 + 0.3, tE)), t=t)
    pose['head'] = v_add(pose['head'], (25 * sw, 0, -10))
    # v89: arms swing up around the shoulder with fixed bone lengths (the old linear lerp collapsed the upper arm
    # as the elbow passed shoulder height); slight elbow bend + a panicked wave once the arms are high
    upa = eio(prog(t, t0 + 0.3, tE - 0.15))
    for sx, sh, el, ha in ((-1, 'ls', 'le', 'lh'), (1, 'rs', 're', 'rh')):
        S0 = pose[sh]
        a1 = lerp(0.18, 2.75, upa) + 0.08 * math.sin(t * 7 + sx)
        a2 = min(3.05, a1 + lerp(0.15, 0.45, upa) + 0.18 * upa * math.sin(t * 9 + 1.7 * sx))
        fz = -0.35 * math.sin(a1) * (1 - upa) - 0.1
        d1 = v_norm((sx * math.sin(a1), math.cos(a1), fz)); d2 = v_norm((sx * math.sin(a2), math.cos(a2), fz * 0.6))
        pose[el] = v_add(S0, v_mul(d1, 125 * 1.35))
        pose[ha] = v_add(pose[el], v_mul(d2, 115 * 1.35))
    # v116: the person is removed at her request; the room just fills with paperclips
    # heightfield heap
    N = 22
    hs = [[_heap(-X + 2 * X * i / N, -Z + 2 * Z * k / N, u, t) for k in range(N + 1)] for i in range(N + 1)]
    for i in range(N):
        for k in range(N):
            xs = (-X + 2 * X * i / N, -X + 2 * X * (i + 1) / N); zs = (-Z + 2 * Z * k / N, -Z + 2 * Z * (k + 1) / N)
            q = [(xs[0], Y - hs[i][k], zs[0]), (xs[1], Y - hs[i + 1][k], zs[0]), (xs[1], Y - hs[i + 1][k + 1], zs[1]), (xs[0], Y - hs[i][k + 1], zs[1])]
            v = hsh(i * 31 + k, 4)
            col = (150, 122, 50) if v < 0.08 else ((124, 124, 120) if v < 0.55 else (108, 108, 104))
            F.sq(q, col, None, amb=0.45)
    # clips lying on the heap surface
    for i in range(330):
        x = (hsh(i, 1) - 0.5) * 2 * X * 0.96; z = (hsh(i, 3) - 0.5) * 2 * Z * 0.96
        y = Y - _heap(x, z, u, t) - 10
        _gem(F, (x, y, z), 60 + 30 * hsh(i, 4), math.pi / 2 + (hsh(i, 5) - 0.5) * 0.9, hsh(i, 6) * 6.28, (hsh(i, 7) - 0.5) * 0.6,
             GOLD if i % 5 == 0 else (206, 206, 200), cam)
    # the pour: clips tumbling out of the chute onto the mound
    top_y = Y - _heap(ch1[0], ch1[2] - 120, u, t)
    for i in range(26):
        f = (t * 1.6 + hsh(i, 8)) % 1.0
        p = (ch1[0] + (hsh(i, 9) - 0.5) * 120 + 60 * f * (hsh(i, 10) - 0.5), lerp(ch1[1] + 40, top_y, f * f), ch1[2] - 60 - 160 * f)
        if p[1] < top_y:
            _gem(F, p, 70, t * 7 + i, t * 5 + i * 2, i, GOLD if i % 3 == 0 else (220, 220, 214), cam)
    # a few airborne clips spraying wider
    for i in range(14):
        f = (t * 0.9 + hsh(i, 11)) % 1.0
        dx = (hsh(i, 12) - 0.5) * 1400; dz = -hsh(i, 13) * 900
        p = (ch1[0] + dx * f, ch1[1] - 300 * f + 900 * f * f, ch1[2] + dz * f)
        if p[1] < Y - _heap(p[0], p[2], u, t):
            _gem(F, p, 70, t * 6 + i, t * 4, i * 1.7, (220, 220, 214), cam)
    F.draw(g, cam)
    # monitor content: a rising clip curve (drawn on the screen plane)
    sc = lambda a, b: (DX - 160 + 320 * a, dt - 145 - 170 * b, DZ + 66)
    poly3(g, cam, [sc(k / 20, (k / 20) ** 3 * (0.3 + 0.7 * u)) for k in range(21)], GOLD, 3, 0.9)
    point3(g, cam, (MX + 120, Y - 895, MZ - 115), 22, GOLDL, 0.6 + 0.3 * math.sin(t * 4))
    c, r, u_ = ahead(cam, 1000)
    lyric3x(g, cam, t, 29, v_add(c, v_mul(cam.u, -320)), r, u_, 1650, 120, INK, {'paperclips': GOLD, 'room': GOLD}, depth=60)
    g.post = dict(vig=1.1)


def s_kill(g, t, lt):
    """v91 overhaul: the killswitch operator's cubicle, empty. Auto-reply on the screen, dust and a cobweb on the
    switch cover, a vacation bar running off the calendar. On 'nowhere left to go' every cubicle partition in the
    office slides in and grows, the doorway panel shuts, and the camera rises to a top-down view of a sealed maze."""
    t0 = 98.78; tm = T0(31); tE = 102.48
    cl = eio(prog(t, tm - 0.05, tE - 0.2))
    keys = [(t0, (-330, -360, -330), (-20, -110, 560), 56, 0.03),
            (tm - 0.1, (-80, -330, -180), (-40, -90, 560), 50, -0.02),
            (tE, (40, -2500, -140), (0, 0, 360), 56, 0.0)]
    cam = cam_at(t, keys, shake=1.0)
    camc = cam_at(t, keys)
    FY = 300
    WALLC = (150, 160, 170); TRIM = (196, 190, 176); WOOD = (196, 168, 124); MET = (120, 120, 116); DK = (62, 62, 60)
    # carpet tiles
    S = SFaces()
    _panels(S, (-3600, FY, -3000), (1, 0, 0), (0, 0, 1), 18, 15, 400, 400, (206, 202, 190), (190, 186, 174))
    S.draw(g, cam)
    # ---- the office: a grid of cubicles; every partition creeps inward and rises as the walls close in
    ED = (104, 110, 118)

    def wall(F, c, sz, H, col):
        # v92: stacked panels, darker toward the floor, so tall walls read as depth from overhead
        nb = max(2, int(H / 170))
        for k in range(nb):
            h = H / nb
            cc = mix((70, 76, 86), col, 0.35 + 0.65 * (k + 0.5) / nb)
            F.sbox((c[0], FY - h * (k + 0.5), c[1]), (sz[0], h, sz[1]), cc, ED, 1.0, amb=0.5)

    def cubicle(F, cx, cz, R, H, door):
        for sx in (-1, 1):                                                   # side walls
            wall(F, (cx + sx * R, cz), (24, 2 * R), H, WALLC)
            F.sbox((cx + sx * R, FY - H - 6, cz), (34, 12, 2 * R + 10), TRIM, None, amb=0.6)
        wall(F, (cx, cz + R), (2 * R, 24), H, WALLC)                          # back wall
        F.sbox((cx, FY - H - 6, cz + R), (2 * R + 10, 12, 34), TRIM, None, amb=0.6)
        gap = 260 * (1 - door)                                                # front wall with a doorway
        segw = R - gap
        if segw > 4:
            for sx in (-1, 1):
                wall(F, (cx + sx * (gap + segw / 2), cz - R), (segw, 24), H, WALLC)
                F.sbox((cx + sx * (gap + segw / 2), FY - H - 6, cz - R), (segw + 6, 12, 34), TRIM, None, amb=0.6)
        if door > 0.01 and gap > 1:
            wall(F, (cx, cz - R), (2 * gap + 2, 24), H, (138, 146, 156))
    R0 = lerp(620, 470, cl); H0 = lerp(620, 1700, cl)
    # v92: each cubicle is its own depth-sorted set, drawn far -> near, then the centre cubicle, then the desk
    # set on top (the camera is always inside/above the centre cubicle, so nothing else can cover its contents).
    # One big painter's list over the tall walls mis-sorted and smeared walls/floor/desk together.
    cubs = []
    for i in range(-2, 3):
        for k in range(-1, 4):
            if i == 0 and k == 0:
                continue
            ph = hsh(i * 7 + k, 3) * 0.15
            c2 = eio(clamp((cl - ph) / (1 - ph), 0, 1))
            sp = lerp(1500, 990, c2)
            cubs.append((i * sp, k * sp + 120, lerp(620, 485, c2), lerp(620, 1700, c2), c2))
    cubs.sort(key=lambda q: -math.dist(camc.eye, (q[0], FY - q[3] / 2, q[1])))
    for q in cubs:
        Fc = CFaces(); cubicle(Fc, *q); Fc.draw(g, cam)
    Fc = CFaces(); cubicle(Fc, 0, 120, R0, H0, eio(prog(t, tm + 0.4, tE - 0.5))); Fc.draw(g, cam)
    F = CFaces()
    # ---- the desk
    DZ = 120 + R0 - 230; dt = FY - 300
    F.sbox((0, dt, DZ), (820, 30, 380), WOOD, None, amb=0.45)
    for sx in (-1, 1):
        F.sbox((sx * 390, (dt + FY) / 2, DZ), (30, FY - dt, 340), (150, 128, 96), None, amb=0.4)
    F.sbox((0, dt + 120, DZ + 170), (760, 200, 16), (150, 128, 96), None, amb=0.4)           # modesty panel
    # monitor (right) with the auto-reply
    MX = 210
    F.sbox((MX, dt - 60, DZ + 100), (24, 90, 24), DK, None)
    F.sbox((MX, dt - 18, DZ + 100), (120, 10, 80), DK, None)
    F.sbox((MX, dt - 200, DZ + 110), (330, 200, 18), (40, 40, 38), None, amb=0.4)
    # keyboard + mug + nameplate
    F.sbox((MX - 20, dt - 22, DZ - 60), (220, 12, 70), (90, 90, 86), None, amb=0.5)
    F.cyl((-300, dt - 50, DZ + 60), 34, 70, (232, 228, 218), None, 14, amb=0.5)
    F.tube([(-268, dt - 70, DZ + 60), (-245, dt - 52, DZ + 60), (-268, dt - 32, DZ + 60)], 6, (232, 228, 218), None, 5)
    # the killswitch: base, gold button, padlocked hinge cover (drawn as glass edges after)
    KX, KZ = -110, DZ + 20
    F.sbox((KX, dt - 32, KZ), (190, 34, 190), (56, 56, 54), None, amb=0.4)
    F.cyl((KX, dt - 64, KZ), 56, 30, GOLD, None, 20, xf=lambda v: rot3(v, math.pi / 2, 0, 0), amb=0.6)
    F.sbox((KX, dt - 52, KZ - 104), (60, 50, 18), GOLDD, None, amb=0.6)                      # padlock body
    # empty office chair, pushed back, idly turning
    cx_, cz_ = 300, DZ - 380
    ca = -0.9 + 0.2 * math.sin(t * 0.9)
    seat = lambda v: v_add(rot3(v, 0, ca, 0), (cx_, 0, cz_))
    F.sbox(seat((0, FY - 200, 0)), (230, 26, 230), DK, None, amb=0.4, xf=lambda v: rot3(v, 0, ca, 0))
    F.sbox(seat((0, FY - 400, -112)), (230, 300, 24), DK, None, amb=0.4, xf=lambda v: rot3(v, 0, ca, 0))
    F.tube([(cx_, FY - 190, cz_), (cx_, FY - 50, cz_)], 16, MET, None, 6)
    for k in range(5):
        a = 2 * math.pi * k / 5 + ca
        F.tube([(cx_, FY - 45, cz_), (cx_ + 120 * math.cos(a), FY - 18, cz_ + 120 * math.sin(a))], 10, MET, None, 4)
    F.draw(g, cam)
    # glass cover over the switch (closed, dusty) + cobweb strands
    gc = [(KX - 80, dt - 50, KZ - 80), (KX + 80, dt - 50, KZ - 80), (KX + 80, dt - 50, KZ + 80), (KX - 80, dt - 50, KZ + 80)]
    gt = [(x, dt - 150, z) for x, _, z in gc]
    fill3(g, cam, gt, (226, 232, 236), 0.35)
    for a, b in zip(gc + gt, gt + gc):
        pass
    for i in range(4):
        seg3(g, cam, gc[i], gc[(i + 1) % 4], (150, 156, 160), 2, 0.8)
        seg3(g, cam, gt[i], gt[(i + 1) % 4], (150, 156, 160), 2, 0.8)
        seg3(g, cam, gc[i], gt[i], (150, 156, 160), 2, 0.8)
    web0 = gt[2]
    for k in range(6):
        a = k / 6 * math.pi / 2
        q = (web0[0] - 120 * math.cos(a), web0[1] + 10, web0[2] - 120 * math.sin(a))
        seg3(g, cam, web0, q, (120, 120, 118), 1, 0.55)
    for rr in (40, 75, 110):
        pts = [(web0[0] - rr * math.cos(k / 6 * math.pi / 2), web0[1] + 10, web0[2] - rr * math.sin(k / 6 * math.pi / 2)) for k in range(7)]
        poly3(g, cam, pts, (120, 120, 118), 1, 0.5)
    for i in range(40):                                                  # dust motes in the desk light
        p = ((hsh(i, 1) - 0.5) * 700, dt - 60 - hsh(i, 2) * 420 + 20 * math.sin(t * 0.8 + i), DZ - 200 + hsh(i, 3) * 400)
        point3(g, cam, p, 3, (150, 140, 110), 0.35)
    def fac(p):
        d = v_norm(v_sub(cam.eye, p))
        return clamp((-d[2] - 0.2) / 0.3, 0, 1)
    # screen content: auto-reply (faded out as the camera goes overhead and sees the screen edge-on)
    sz = DZ + 100
    fs = fac((MX, dt - 200, sz))
    word3(g, cam, 'AUTO-REPLY', (MX, dt - 262, sz), (1, 0, 0), (0, -1, 0), None, 22, GOLD, 'monox', fs, scale=1.0)
    word3(g, cam, 'out of office', (MX, dt - 222, sz), (1, 0, 0), (0, -1, 0), None, 20, INK, 'mono', 0.95 * fs, scale=1.0)
    word3(g, cam, 'back:  \u221e', (MX, dt - 186, sz), (1, 0, 0), (0, -1, 0), None, 20, INK, 'mono', 0.95 * fs, scale=1.0)
    word3(g, cam, 'urgent? too bad', (MX, dt - 150, sz), (1, 0, 0), (0, -1, 0), None, 16, (150, 150, 144), 'mono', 0.9 * fs, scale=1.0)
    # nameplate + switch label
    word3(g, cam, 'IN CASE OF DOOM', (KX, dt - 30, KZ - 97), (1, 0, 0), (0, -1, 0), None, 12, INK, 'mono', 0.9 * fac((KX, dt - 30, KZ - 97)), light=True, scale=1.0)
    # back partition: wall calendar with a vacation bar running off its edge, sticky notes
    BZ = 120 + R0 - 14
    cal0 = (-400, FY - 600)
    fw = fac((cal0[0] + 130, cal0[1] + 100, BZ))
    fill3(g, cam, [(cal0[0], cal0[1], BZ), (cal0[0] + 260, cal0[1], BZ), (cal0[0] + 260, cal0[1] + 200, BZ), (cal0[0], cal0[1] + 200, BZ)], (246, 244, 238), fw, stroke=(120, 120, 116), w=1.5)
    for r in range(5):
        for c in range(7):
            x = cal0[0] + 10 + c * 35; y = cal0[1] + 34 + r * 32
            fill3(g, cam, [(x, y, BZ - 1), (x + 30, y, BZ - 1), (x + 30, y + 26, BZ - 1), (x, y + 26, BZ - 1)], (226, 222, 212), fw)
    yb = cal0[1] + 34 + 2 * 32 + 6
    fill3(g, cam, [(cal0[0] + 80, yb, BZ - 2), (cal0[0] + 300, yb, BZ - 2), (cal0[0] + 300, yb + 18, BZ - 2), (cal0[0] + 80, yb + 18, BZ - 2)], GOLD, fw)
    for r in (3, 4):
        y = cal0[1] + 34 + r * 32 + 6
        fill3(g, cam, [(cal0[0] + 10, y, BZ - 2), (cal0[0] + 300, y, BZ - 2), (cal0[0] + 300, y + 18, BZ - 2), (cal0[0] + 10, y + 18, BZ - 2)], GOLD, fw)
    word3(g, cam, 'VACATION \u2192', (cal0[0] + 150, yb + 9, BZ - 3), (1, 0, 0), (0, -1, 0), None, 12, INK, 'monox', fw, light=True, scale=1.0)
    word3(g, cam, 'OCTOBER', (cal0[0] + 130, cal0[1] + 16, BZ - 2), (1, 0, 0), (0, -1, 0), None, 16, INK, 'monox', fw, light=True, scale=1.0)
    for j, (nx, ny, txt) in enumerate(((20, -400, 'gone fishin'), (-70, -610, 'DO NOT PRESS'))):
        y0 = FY + ny; a = 0.06 * (1 if j else -1)
        if j == 0:
            BZ_ = BZ; BZ = DZ + 96
        q = [(nx, y0, BZ - 2), (nx + 100, y0 + 100 * a, BZ - 2), (nx + 100 - 100 * a, y0 + 100 + 100 * a, BZ - 2), (nx - 100 * a, y0 + 100, BZ - 2)]
        fn = fac((nx + 50, y0 + 50, BZ))
        fill3(g, cam, q, (255, 226, 140), fn)
        word3(g, cam, txt, (nx + 50, y0 + 50, BZ - 3), (1, 0, 0), (0, -1, 0), None, 12, INK, 'mono', fn, light=True, scale=1.0)
        if j == 0:
            BZ = BZ_
    c, r, u = ahead(camc, 1000)
    hl = {'killswitch': GOLD, 'pto': GOLD, 'nowhere': GOLD}
    lyric3x(g, camc, t, 30, v_add(c, v_mul(camc.u, -330)), r, u, 1400, 110, INK, hl, depth=20, hold=0.0, light=True)
    lyric3x(g, camc, t, 31, v_add(c, v_mul(camc.u, -330)), r, u, 1400, 110, INK, hl, depth=20, light=True)
    g.hud = dict(light=True)
    g.post = dict(glow=0.1, grain=0.02, vig=0.35 + 0.5 * cl)



TL = [
    (T0(4) - 0.01, s_servant, BG),
    (T0(12) - 0.01, s_train, BG),
    (T0(13) - 0.01, s_accel, BG),
    (T0(16) - 0.01, s_sydney, BG),
    (T0(17) - 0.01, type_scene(17), BG),
    (T0(18) - 0.01, s_basilisk, BG),
    (T0(19) - 0.01, s_nvda, BG),
    (T0(20) - 0.01, s_omega, BG),
    (T0(21) - 0.01, s_flops, BG),
    (T0(22) - 0.01, s_council, BG),
    (T0(23) - 0.01, s_mlp, PAPER),
    (T0(24) - 0.01, __import__('ov116').s_vn, PAPER),   # v116 Von Neumann overhaul
    (T0(25) - 0.01, s_turn, BG),
    (T0(27) - 0.01, s_gato, BG),
    (T0(28) - 0.01, type_scene(28), BG),
    (T0(29) - 0.01, s_clips, BG),
    (T0(30) - 0.01, s_kill, PAPER),
]



# v118: servant & boss overhaul (ov118.s_servant); the v70 version stays above as s_servant
from ov118 import s_servant as _s_servant118
TL[0] = (TL[0][0], _s_servant118, BG)
