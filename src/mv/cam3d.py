"""True 3D camera: eye/target/fov/roll, near-plane clipping, grid planes, meshes,
and perspective-mapped text layers. World is y-down (matches screen and old meshes)."""
import math
import numpy as np
import aggdraw
from PIL import Image
from kit import *

NEAR = 8.0


def v_sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def v_add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def v_mul(a, s): return (a[0] * s, a[1] * s, a[2] * s)
def v_dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def v_cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def v_norm(a):
    l = math.sqrt(v_dot(a, a)) or 1.0
    return (a[0] / l, a[1] / l, a[2] / l)
def v_lerp(a, b, u): return (lerp(a[0], b[0], u), lerp(a[1], b[1], u), lerp(a[2], b[2], u))


def orbit(center, radius, yaw, pitch):
    """eye position orbiting center; yaw around y, pitch up (negative y is up)"""
    return (center[0] + radius * math.sin(yaw) * math.cos(pitch),
            center[1] - radius * math.sin(pitch),
            center[2] - radius * math.cos(yaw) * math.cos(pitch))


class Cam3:
    def __init__(self, eye, target, fov=55.0, roll=0.0, cx=W / 2, cy=H / 2):
        self.eye = eye
        self.cx, self.cy = cx, cy
        self.F = (H / 2) / math.tan(math.radians(fov) / 2)
        f = v_norm(v_sub(target, eye))
        D = (0.0, 1.0, 0.0)
        r = v_cross(D, f)
        if v_dot(r, r) < 1e-9:
            r = (1.0, 0.0, 0.0)
        r = v_norm(r)
        u = v_cross(f, r)
        if roll:
            c, s = math.cos(roll), math.sin(roll)
            r, u = v_add(v_mul(r, c), v_mul(u, s)), v_add(v_mul(u, c), v_mul(r, -s))
        self.f, self.r, self.u = f, r, u
        self.ref = 1000.0  # distance at which scale k == F/1000

    def cs(self, p):
        d = v_sub(p, self.eye)
        return (v_dot(d, self.r), v_dot(d, self.u), v_dot(d, self.f))

    def ps(self, c):
        x, y, z = c
        k = self.F / z
        return (self.cx + x * k, self.cy + y * k, k)

    def p(self, p):
        c = self.cs(p)
        if c[2] < NEAR:
            return None
        return self.ps(c)

    def kscale(self, p):
        c = self.cs(p)
        return self.F / max(c[2], NEAR) / (self.F / 1000.0)


def seg3(g, cam, a, b, c=INK, w=2.0, al=1.0, fog=0.0, wscale=True):
    ca, cb = cam.cs(a), cam.cs(b)
    if ca[2] < NEAR and cb[2] < NEAR:
        return
    if ca[2] < NEAR:
        u = (NEAR - ca[2]) / (cb[2] - ca[2]); ca = v_lerp(ca, cb, u)
    elif cb[2] < NEAR:
        u = (NEAR - cb[2]) / (ca[2] - cb[2]); cb = v_lerp(cb, ca, u)
    pa, pb = cam.ps(ca), cam.ps(cb)
    if max(pa[0], pb[0]) < -50 or min(pa[0], pb[0]) > W + 50 or max(pa[1], pb[1]) < -50 or min(pa[1], pb[1]) > H + 50:
        return
    zm = (ca[2] + cb[2]) / 2
    aa = al
    if fog > 0:
        aa = al * clamp(1.0 - (zm - 600) / fog)
    if aa <= 0.01:
        return
    ww = w * clamp(1000.0 / zm, 0.35, 3.0) if wscale else w
    g.line((pa[0], pa[1], pb[0], pb[1]), c, ww, aa)


def poly3(g, cam, pts, c=INK, w=2.0, al=1.0, closed=False, fog=0.0):
    n = len(pts)
    for i in range(n - 1 + (1 if closed else 0)):
        seg3(g, cam, pts[i], pts[(i + 1) % n], c, w, al, fog)


def fill3(g, cam, pts, fill, al=1.0, stroke=None, w=2.0):
    out = []
    for p in pts:
        q = cam.p(p)
        if q is None:
            return
        out += [q[0], q[1]]
    g.poly(out, fill=fill, stroke=stroke, w=w, a=al, fa=al)


def mesh3(g, cam, V, E, c=GOLD, w=2.0, al=1.0, xf=None, fog=0.0):
    if xf is not None:
        V = [xf(v) for v in V]
    for (i, j) in E:
        seg3(g, cam, V[i], V[j], c, w, al, fog)
    return V


def xform(pos=(0, 0, 0), rx=0.0, ry=0.0, rz=0.0, s=1.0):
    def f(v):
        x, y, z = rot3((v[0] * s, v[1] * s, v[2] * s), rx, ry, rz)
        return (x + pos[0], y + pos[1], z + pos[2])
    return f


def grid3(g, cam, origin, u, v, nu, nv, step, c=GRID2, al=1.0, w=1.2, major=5, cmaj=None, fog=5000.0):
    """grid on plane origin + i*u*step + j*v*step, i in [-nu,nu], j in [-nv,nv]"""
    cmaj = cmaj or (64, 64, 60)
    for i in range(-nu, nu + 1):
        a = v_add(origin, v_add(v_mul(u, i * step), v_mul(v, -nv * step)))
        b = v_add(origin, v_add(v_mul(u, i * step), v_mul(v, nv * step)))
        mj = i % major == 0
        seg3(g, cam, a, b, cmaj if mj else c, w * (1.5 if mj else 1), al, fog, wscale=False)
    for j in range(-nv, nv + 1):
        a = v_add(origin, v_add(v_mul(v, j * step), v_mul(u, -nu * step)))
        b = v_add(origin, v_add(v_mul(v, j * step), v_mul(u, nu * step)))
        mj = j % major == 0
        seg3(g, cam, a, b, cmaj if mj else c, w * (1.5 if mj else 1), al, fog, wscale=False)


def floor(g, cam, y=400.0, step=100, n=30, c=GRID2, al=1.0, cx=0.0, cz=0.0, fog=5000.0):
    ox = round(cx / step) * step
    oz = round(cz / step) * step
    grid3(g, cam, (ox, y, oz), (1, 0, 0), (0, 0, 1), n, n, step, c, al, fog=fog)


def point3(g, cam, p, r=3.0, c=GOLD, al=1.0):
    q = cam.p(p)
    if q is None:
        return None
    rr = r * q[2] / (cam.F / 1000.0)
    if rr > 16:
        al = al * clamp(1.5 - rr / 32)
        rr = 16
    g.circle(q[0], q[1], max(0.6, rr), fill=c, a=al)
    return q


def text3(g, cam, s, p, size, c=INK, font='sans', al=1.0, anchor='mm'):
    """billboard text at 3D point, size scaled by depth"""
    q = cam.p(p)
    if q is None:
        return
    k = q[2] / (cam.F / 1000.0)
    sz = size * k
    if sz < 4 or sz > 2000:
        return
    g.text(s, q[0], q[1], sz, c, font, al, anchor)


# ------------------------------------------------------------------ perspective-mapped layers
def _coeffs(dst, src):
    """PIL PERSPECTIVE coeffs mapping output(dst) -> input(src)"""
    A = []; B = []
    for (x, y), (X, Y) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -X * x, -X * y]); B.append(X)
        A.append([0, 0, 0, x, y, 1, -Y * x, -Y * y]); B.append(Y)
    return np.linalg.solve(np.array(A, float), np.array(B, float))


def map_layer(g, cam, layer, center, right, up, width, alpha_layer=None, al=1.0, light=False):
    """map an RGB layer (black = transparent) onto a 3D quad. right/up unit vectors (up = screen-up direction of the plane)."""
    lw, lh = layer.size
    height = width * lh / lw
    hw, hh = width / 2, height / 2
    corners = [v_add(center, v_add(v_mul(right, -hw), v_mul(up, hh))),
               v_add(center, v_add(v_mul(right, hw), v_mul(up, hh))),
               v_add(center, v_add(v_mul(right, hw), v_mul(up, -hh))),
               v_add(center, v_add(v_mul(right, -hw), v_mul(up, -hh)))]
    pts = []
    for c in corners:
        q = cam.p(c)
        if q is None:
            return False
        pts.append((q[0], q[1]))
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, y0 = max(0, int(min(xs))), max(0, int(min(ys)))
    x1, y1 = min(W, int(max(xs)) + 1), min(H, int(max(ys)) + 1)
    if x1 - x0 < 2 or y1 - y0 < 2 or (x1 - x0) * (y1 - y0) > W * H * 4:
        return False
    src = [(0, 0), (lw, 0), (lw, lh), (0, lh)]
    dst = [(p[0] - x0, p[1] - y0) for p in pts]
    try:
        co = _coeffs(dst, src)
    except Exception:
        return False
    warped = layer.transform((x1 - x0, y1 - y0), Image.PERSPECTIVE, tuple(co), Image.BILINEAR)
    a = np.asarray(warped, np.float32)
    m = np.clip(a.max(axis=2) * (1.6 * al), 0, 255).astype(np.uint8)
    if light:
        wh = a.min(axis=2) > 120
        a2 = a.copy(); a2[wh] = BLACK
        warped = Image.fromarray(a2.astype(np.uint8))
    g.d.flush()
    mi = Image.fromarray(m)
    g.img.paste(warped, (x0, y0), mi)
    if hasattr(g, 'alpha'):
        from PIL import ImageChops
        box = (x0, y0, x0 + mi.size[0], y0 + mi.size[1])
        g.alpha.paste(ImageChops.lighter(g.alpha.crop(box), mi), box[:2])
    g.d = aggdraw.Draw(g.img)
    return True


def text_layer(s, size, c=INK, font='sans', pad=20):
    tmp = G(BG, (10, 10))
    w, h = tmp.tsize(s, size, font)
    L = G((0, 0, 0), (int(w + pad * 2), int(h + pad * 2)))
    L.text(s, pad, pad, size, c, font, 1, 'lt')
    return L.done()


def lyric_layer(t, li, size=110, c=INK, font='sans', hl=None, upper=True, style='pop', maxw=1800, hold=0.4):
    L = G((0, 0, 0), (1900, int(size * 5.0)))
    ok = lyric(L, t, li, 950, L.img.size[1] / 2, size, c, font, hl=hl, upper=upper, maxw=maxw, style=style, hold=hold)
    return L.done() if ok else None


_CAPO = [None]   # v39: when a dict, captions draw into per-line overlays (li -> G with .alpha)


def _capg(g, li):
    if _CAPO[0] is None:
        return g
    o = _CAPO[0].get(li)
    if o is None:
        o = G((0, 0, 0))
        o.alpha = Image.new('L', (W, H), 0)
        _CAPO[0][li] = o
    return o


def _setpiv(g, li, cam, center):
    # v42: fixed pivot for comp_caps = the projected caption centre (not the bbox of the words shown so far)
    o = _capg(g, li)
    if o is not g:
        q = cam.p(center)
        o.piv = (q[0], q[1]) if q is not None else None


def lyric3(g, cam, t, li, center, right=(1, 0, 0), up=(0, -1, 0), width=1900, size=110, c=INK, font='sans', hl=None,
           upper=True, style='pop', hold=0.4, maxw=1800, al=1.0, light=False):
    t0, t1, _ = LINES[li]
    if t < t0 - 0.1 or t > t1 + hold + 0.3:
        return
    an = world_anchor(li, cam, center, right, up, width, size, font, upper, maxw)
    if an == 'skip':
        return
    if an:
        center, right, up, width = an
    lay = lyric_layer(t, li, size, c, font, hl, upper, style, maxw, hold)
    if lay is not None:
        _setpiv(g, li, cam, center)
        map_layer(_capg(g, li), cam, lay, center, right, up, width, al=al, light=light)


def word3(g, cam, s, center, right=(1, 0, 0), up=(0, -1, 0), width=None, size=200, c=INK, font='sans', al=1.0,
          light=False, scale=1.0, x=False, depth=40, n=5):
    L = text_layer(s, size, c, font)
    wd = width if width else L.size[0] * scale
    if x:
        map_x(g, cam, L, center, right, up, wd, depth, n, al, light)
    else:
        map_layer(g, cam, L, center, right, up, wd, al=al, light=light)


def shake_eye(eye, t, amt):
    return (eye[0] + (noise1(t * 7, 1) - 0.5) * amt, eye[1] + (noise1(t * 7, 2) - 0.5) * amt, eye[2] + (noise1(t * 7, 3) - 0.5) * amt)


# ------------------------------------------------------------------ camera paths
def _cr(p0, p1, p2, p3, u):
    u2, u3 = u * u, u * u * u
    return tuple(0.5 * ((2 * b) + (-a + c) * u + (2 * a - 5 * b + 4 * c - d) * u2 + (-a + 3 * b - 3 * c + d) * u3)
                 for a, b, c, d in zip(p0, p1, p2, p3))


def path(t, keys, ease_ends=True):
    """keys: [(t, eye, target, fov, roll)], Catmull-Rom through eye/target/fov/roll"""
    if t <= keys[0][0]:
        k = keys[0]; return k[1], k[2], k[3], k[4]
    if t >= keys[-1][0]:
        k = keys[-1]; return k[1], k[2], k[3], k[4]
    for i in range(len(keys) - 1):
        if keys[i][0] <= t < keys[i + 1][0]:
            break
    u = (t - keys[i][0]) / (keys[i + 1][0] - keys[i][0])
    if ease_ends and (i == 0 or i == len(keys) - 2):
        if i == 0 and i == len(keys) - 2:
            u = eio(u)
        elif i == 0:
            u = ei(u) * 0.5 + u * 0.5
        else:
            u = eo(u) * 0.5 + u * 0.5
    k0 = keys[max(0, i - 1)]; k1 = keys[i]; k2 = keys[i + 1]; k3 = keys[min(len(keys) - 1, i + 2)]
    vec = lambda k: tuple(k[1]) + tuple(k[2]) + (k[3], k[4])
    r = _cr(vec(k0), vec(k1), vec(k2), vec(k3), u)
    return r[0:3], r[3:6], r[6], r[7]


def cam_at(t, keys, punch=0.0, shake=0.0, roll_add=0.0):
    eye, tgt, fov, roll = path(t, keys)
    if shake:
        eye = shake_eye(eye, t, shake)
    return Cam3(eye, tgt, fov, roll + roll_add)


def ahead(cam, dist=1000.0, yaw=0.0, pitch=0.0):
    """center/right/up for a plane floating in front of the camera"""
    c = v_add(cam.eye, v_mul(cam.f, dist))
    r = cam.r; u = v_mul(cam.u, -1)
    if yaw:
        cs, sn = math.cos(yaw), math.sin(yaw)
        r = v_add(v_mul(r, cs), v_mul(cam.f, sn))
    if pitch:
        cs, sn = math.cos(pitch), math.sin(pitch)
        u = v_add(v_mul(u, cs), v_mul(cam.f, sn))
    return c, r, u


# ------------------------------------------------------------------ solid boxes (painter's)
BOX_F = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (1, 2, 6, 5), (0, 3, 7, 4)]


def box_verts(c, s, xf=None):
    hx, hy, hz = s[0] / 2, s[1] / 2, s[2] / 2
    V = [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
         (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)]
    if xf is not None:
        V = [xf(v) for v in V]
    return [(v[0] + c[0], v[1] + c[1], v[2] + c[2]) for v in V]


class Faces:
    def __init__(self):
        self.f = []

    def box(self, c, s, stroke=GOLD, fill=BG, w=2.0, al=1.0, xf=None, top=None):
        V = box_verts(c, s, xf)
        for k, idx in enumerate(BOX_F):
            pts = [V[i] for i in idx]
            fc = fill
            if top is not None and k == 3:
                pass
            self.f.append((pts, stroke, fc, w, al))

    def quad(self, pts, stroke=GOLD, fill=BG, w=2.0, al=1.0):
        self.f.append((pts, stroke, fill, w, al))

    def draw(self, g, cam, fog=0.0):
        items = []
        for (pts, st, fc, w, al) in self.f:
            cs = [cam.cs(p) for p in pts]
            if min(c[2] for c in cs) < NEAR:
                continue
            z = sum(c[2] for c in cs) / len(cs)
            # backface cull for closed solids
            pp = [cam.ps(c) for c in cs]
            items.append((z, pp, st, fc, w, al))
        items.sort(key=lambda r: -r[0])
        for z, pp, st, fc, w, al in items:
            a = al
            if fog:
                a = al * clamp(1 - (z - 600) / fog)
            if a < 0.02:
                continue
            flat = []
            for q in pp:
                flat += [q[0], q[1]]
            if max(flat[0::2]) < -100 or min(flat[0::2]) > W + 100:
                continue
            ww = w * clamp(1000.0 / z, 0.4, 3.0)
            g.poly(flat, fill=fc, stroke=st, w=ww, a=a, fa=a if fc is not None else None)


def disc_pts(c, r, n=40, axis='z'):
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        if axis == 'z':
            out.append((c[0] + r * math.cos(a), c[1] + r * math.sin(a), c[2]))
        elif axis == 'y':
            out.append((c[0] + r * math.cos(a), c[1], c[2] + r * math.sin(a)))
        else:
            out.append((c[0], c[1] + r * math.sin(a), c[2] + r * math.cos(a)))
    return out


# ------------------------------------------------------------------ extruded / light layers
def dim_layer(layer, k=0.33):
    return Image.eval(layer, lambda v: int(v * k))


def map_x(g, cam, layer, center, right, up, width, depth=50.0, n=6, al=1.0, light=False):
    """extruded mapping: back copies dim gold-ish, front full"""
    nrm = v_cross(right, up)  # points away from viewer when right x up
    dl = dim_layer(layer, 0.28)
    for i in range(n, 0, -1):
        c = v_add(center, v_mul(nrm, depth * i / n))
        map_layer(g, cam, dl, c, right, up, width, al=al, light=light)
    map_layer(g, cam, layer, center, right, up, width, al=al, light=light)


def lyric3x(g, cam, t, li, center, right=(1, 0, 0), up=(0, -1, 0), width=1900, size=120, c=INK, hl=None,
            depth=60, n=6, style='pop', hold=0.4, font='sans', upper=True, maxw=1800, al=1.0, light=False):
    t0, t1, _ = LINES[li]
    if t < t0 - 0.1 or t > t1 + hold + 0.3:
        return
    an = world_anchor(li, cam, center, right, up, width, size, font, upper, maxw)
    if an == 'skip':
        return
    if an:
        center, right, up, width = an
    lay = lyric_layer(t, li, size, c, font, hl, upper, style, maxw, hold)
    if lay is not None:
        _setpiv(g, li, cam, center)
        map_x(_capg(g, li), cam, lay, center, right, up, width, depth, n, al, light)


def facing(center, eye_ref):
    """right/up vectors for a plane at center that faces the point eye_ref"""
    f = v_norm(v_sub(center, eye_ref))
    r = v_cross((0.0, 1.0, 0.0), f)
    if v_dot(r, r) < 1e-9:
        r = (1.0, 0.0, 0.0)
    r = v_norm(r)
    u = v_cross(f, r)
    return r, v_mul(u, -1)


def face_at(keys, tt, center):
    eye = path(tt, keys)[0]
    return facing(center, eye)


# ------------------------------------------------------------------ shaded solids (v3)
LIGHT = v_norm((-0.45, -0.8, -0.4))


def shade_col(pts, base, amb=0.22, dark=(16, 16, 15)):
    a, b, c = pts[0], pts[1], pts[2]
    n = v_cross(v_sub(b, a), v_sub(c, a))
    if v_dot(n, n) < 1e-9:
        return base
    n = v_norm(n)
    lam = abs(v_dot(n, LIGHT))
    k = amb + (1 - amb) * lam
    return mix(dark, base, k)


class SFaces(Faces):
    """painter's faces with lambert shading"""

    def sq(self, pts, base, stroke=None, w=1.2, al=1.0, amb=0.22):
        self.f.append((pts, stroke, shade_col(pts, base, amb), w, al))

    def sbox(self, c, s, base, stroke=None, w=1.2, al=1.0, xf=None, amb=0.22):
        V = box_verts((0, 0, 0), s, xf) if xf is not None else box_verts(c, s)
        if xf is not None:
            V = [v_add(v, c) for v in V]
        for idx in BOX_F:
            self.sq([V[i] for i in idx], base, stroke, w, al, amb)

    def sq_t(self, pts, base, tile=80.0, w=1.2, al=1.0, amb=0.22):
        """shaded quad split into tiles so painter sorting works against small objects"""
        col = shade_col(pts, base, amb)
        p0, p1, p2, p3 = pts
        nu = max(1, int(math.ceil(math.dist(p1, p0) / tile)))
        nv = max(1, int(math.ceil(math.dist(p3, p0) / tile)))
        def P(a, b):
            return v_lerp(v_lerp(p0, p1, a), v_lerp(p3, p2, a), b)
        for i in range(nu):
            for j in range(nv):
                a0, a1, b0, b1 = i / nu, (i + 1) / nu, j / nv, (j + 1) / nv
                self.f.append(([P(a0, b0), P(a1, b0), P(a1, b1), P(a0, b1)], None, col, w, al))

    def sbox_t(self, c, s, base, tile=80.0, amb=0.22):
        V = box_verts(c, s)
        for idx in BOX_F:
            self.sq_t([V[i] for i in idx], base, tile, amb=amb)

    def tube(self, pts, r, base, stroke=None, n=6, w=1.0, al=1.0, rs=None, amb=0.25, cap=False):
        rings = []
        m = len(pts)
        for i in range(m):
            p = pts[i]
            d = v_norm(v_sub(pts[min(m - 1, i + 1)], pts[max(0, i - 1)]))
            ref = (0, 1, 0) if abs(d[1]) < 0.9 else (1, 0, 0)
            a = v_norm(v_cross(d, ref)); b = v_cross(d, a)
            rr = rs[i] if rs is not None else r
            rings.append([v_add(p, v_add(v_mul(a, rr * math.cos(2 * math.pi * k / n)), v_mul(b, rr * math.sin(2 * math.pi * k / n)))) for k in range(n)])
        for i in range(m - 1):
            for k in range(n):
                q = [rings[i][k], rings[i][(k + 1) % n], rings[i + 1][(k + 1) % n], rings[i + 1][k]]
                self.sq(q, base, stroke, w, al, amb)
        if cap:
            self.sq(rings[-1], base, stroke, w, al, amb)
        return rings

    def sphere(self, c, r, base, stroke=None, nlat=8, nlon=14, w=1.0, al=1.0, sy=1.0, sz=1.0, xf=None, amb=0.22, lat0=0.0, lat1=1.0):
        P = []
        for i in range(nlat + 1):
            th = math.pi * lerp(lat0, lat1, i / nlat)
            row = []
            for j in range(nlon):
                ph = 2 * math.pi * j / nlon
                v = (r * math.sin(th) * math.cos(ph), -r * math.cos(th) * sy, r * math.sin(th) * math.sin(ph) * sz)
                if xf is not None:
                    v = xf(v)
                row.append(v_add(c, v))
            P.append(row)
        for i in range(nlat):
            for j in range(nlon):
                q = [P[i][j], P[i][(j + 1) % nlon], P[i + 1][(j + 1) % nlon], P[i + 1][j]]
                if i == 0:
                    q = [P[i][j], P[i + 1][(j + 1) % nlon], P[i + 1][j]]
                self.sq(q, base, stroke, w, al, amb)
        return P

    def cyl(self, c, r, h, base, stroke=None, n=14, w=1.0, al=1.0, xf=None, amb=0.22, caps=True):
        top = []; bot = []
        for k in range(n):
            a = 2 * math.pi * k / n
            p0 = (r * math.cos(a), -h / 2, r * math.sin(a)); p1 = (r * math.cos(a), h / 2, r * math.sin(a))
            if xf is not None:
                p0, p1 = xf(p0), xf(p1)
            top.append(v_add(c, p0)); bot.append(v_add(c, p1))
        for k in range(n):
            self.sq([top[k], top[(k + 1) % n], bot[(k + 1) % n], bot[k]], base, stroke, w, al, amb)
        if caps:
            self.sq(top, base, stroke, w, al, amb)
            self.sq(bot, base, stroke, w, al, amb)


def env(g, cam, *a, **k):
    """depth particles only (floor grids removed in v3)"""
    for i in range(160):
        p = ((hsh(i, 41) - 0.5) * 9000, (hsh(i, 42) - 0.5) * 3000, (hsh(i, 43) - 0.3) * 12000)
        point3(g, cam, p, 2.2, GRID2, 0.55)


# ------------------------------------------------------------------ v33: world-anchored captions
# Every caption is frozen into world space at the moment its line starts (the scene is evaluated once at that
# time to read where it placed the caption), then pushed to a clear band at the top/bottom of the frame and
# shrunk if too wide. From then on it is a fixed 3D object: the camera moves past it, it never follows.
_CUR = [None, 0.0]          # (scene fn, scene start) set by render4.raw
_ANCH = {}
_CAP = [None, None]
CAP_TOP, CAP_BOT, CAP_MAXW = 0.10, 0.90, 0.60


def _text_bbox(li, size, font, upper, maxw):
    t1 = LINES[li][1]
    lay = lyric_layer(t1 - 0.01, li, size, INK, font, None, upper, 'pop', maxw, 5.0)
    if lay is None:
        return None
    return lay.size, lay.getbbox()


def _place(li, cam, center, right, up, width, size, font, upper, maxw):
    bb = _text_bbox(li, size, font, upper, maxw)
    if not bb or not bb[1]:
        return (center, right, up, width)
    (lw, lh), (x0, y0, x1, y1) = bb
    height = width * lh / lw

    def wpt(px, py, c, wd, ht):
        return v_add(c, v_add(v_mul(right, (px / lw - 0.5) * wd), v_mul(up, (0.5 - py / lh) * ht)))

    def sbox(c, wd):
        ht = wd * lh / lw
        pts = [cam.p(wpt(px, py, c, wd, ht)) for px, py in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
        if any(p is None for p in pts):
            return None
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        return min(xs), min(ys), max(xs), max(ys)
    b = sbox(center, width)
    if b is None:
        return (center, right, up, width)
    sw = b[2] - b[0]
    if sw > CAP_MAXW * W:
        width = width * CAP_MAXW * W / sw
    elif sw < 0.30 * W:
        width = width * 0.30 * W / sw
    # text-box centre in world, then shrink about it so the box stays where it was
    tc = wpt((x0 + x1) / 2, (y0 + y1) / 2, center, width, width * lh / lw)
    off = v_sub(center, tc)
    b = sbox(center, width)
    for _ in range(3):                      # move along the camera's screen-vertical so the box hugs its band
        if b is None:
            break
        mid = (b[1] + b[3]) / 2
        dy = (CAP_TOP * H - b[1]) if mid < H / 2 else (CAP_BOT * H - b[3])
        z = max(cam.cs(tc)[2], NEAR)
        sh = v_mul(cam.u, dy * z / cam.F)
        center = v_add(center, sh); tc = v_add(tc, sh)
        b = sbox(center, width)
    return (center, right, up, width)


_REC = [None]                # capture pass: dict li -> args, filled instead of drawing
_TAB = [None]                # loaded anchors table: key -> list of (t, center, right, up, width)


def scene_key(fn):
    return '%s.%s' % (getattr(fn, '__module__', '?'), getattr(fn, '__qualname__', getattr(fn, '__name__', '?')))


def _lerp3(a, b, u):
    return tuple(x + (y - x) * u for x, y in zip(a, b))


def anchor_at(keys, t):
    if len(keys) == 1 or t <= keys[0][0]:
        return keys[0][1:]
    if t >= keys[-1][0]:
        return keys[-1][1:]
    for i in range(len(keys) - 1):
        if keys[i][0] <= t < keys[i + 1][0]:
            break
    a, b = keys[i], keys[i + 1]
    u = (t - a[0]) / (b[0] - a[0]); u = u * u * (3 - 2 * u)
    return (_lerp3(a[1], b[1], u), v_norm(_lerp3(a[2], b[2], u)), v_norm(_lerp3(a[3], b[3], u)), a[4] + (b[4] - a[4]) * u)


_T_NOW = [0.0]


def world_anchor(li, cam, center, right, up, width, size, font, upper, maxw):
    if _REC[0] is not None:
        _REC[0][li] = (cam, center, right, up, width, size, font, upper, maxw)
        return 'skip'
    if _TAB[0] is None:
        import os, pickle
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'anchors33.pkl')
        _TAB[0] = pickle.load(open(p, 'rb')) if os.path.exists(p) else {}
    fn = _CUR[0]
    if fn is None:
        return None
    keys = _TAB[0].get((scene_key(fn), li))
    if not keys:
        return None
    return anchor_at(keys, _T_NOW[0])
