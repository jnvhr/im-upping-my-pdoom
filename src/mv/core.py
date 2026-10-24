"""Core drawing kit for the P(doom) video. Written from scratch: PIL + aggdraw + numpy.
Every frame is a pure function of song time t (seconds)."""
import math, json, os
import numpy as np
import aggdraw
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1920, 1080
FPS = int(os.environ.get('PDOOM_FPS', '30'))   # v131: 60 for the production master
_T = json.load(open(os.path.join(HERE, 'tempo.json')))
BPM = _T['bpm']; PHASE = _T['phase']; BEAT = 60.0 / BPM
DUR = _T['dur']
FEAT = dict(np.load(os.path.join(HERE, 'feat.npz')))

# ---------------------------------------------------------------- palette
BG = (10, 10, 10)
INK = (244, 244, 240)
GOLD = (245, 180, 32)
GOLDD = (120, 88, 16)
GOLDL = (255, 226, 140)
GRID = (38, 38, 38)
GRID2 = (58, 58, 56)
DIM = (110, 110, 104)
PAPER = (245, 243, 239)
PGRID = (214, 210, 200)
BLACK = (10, 10, 10)

FONT = {
    'sans': os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fonts', 'ArchivoBlack-Regular.ttf'),
    'mono': os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fonts', 'JetBrainsMono-Bold.ttf'),
    'monox': os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fonts', 'JetBrainsMono-ExtraBold.ttf'),
    'monor': os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fonts', 'JetBrainsMono-Regular.ttf'),
    'serif': os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fonts', 'InstrumentSerif-Italic.ttf'),
    'cjk': os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fonts', 'NotoSansSC.ttf'),
}

# ---------------------------------------------------------------- math
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x

def lerp(a, b, x):
    return a + (b - a) * x

def prog(t, t0, t1):
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    return clamp((t - t0) / (t1 - t0))

def eo(x):  # ease out cubic
    x = clamp(x); return 1 - (1 - x) ** 3

def ei(x):
    x = clamp(x); return x ** 3

def eio(x):
    x = clamp(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2

def smooth(x):
    x = clamp(x); return x * x * (3 - 2 * x)

def eback(x, s=1.9):
    x = clamp(x); x -= 1; return x * x * ((s + 1) * x + s) + 1

def elastic(x):
    x = clamp(x)
    if x in (0, 1):
        return x
    return 2 ** (-10 * x) * math.sin((x * 10 - 0.75) * (2 * math.pi / 3)) + 1

def mix(c1, c2, x):
    x = clamp(x)
    return tuple(int(round(a + (b - a) * x)) for a, b in zip(c1, c2))

def hsv(h, s=1, v=1):
    h = (h % 1.0) * 6; i = int(h); f = h - i
    p, q, r = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    rgb = [(v, r, p), (q, v, p), (p, v, r), (p, q, v), (r, p, v), (v, p, q)][i % 6]
    return tuple(int(c * 255) for c in rgb)

def hsh(i, k=0):
    """deterministic hash -> [0,1)"""
    x = math.sin(i * 127.1 + k * 311.7 + 0.5) * 43758.5453
    return x - math.floor(x)

def noise1(x, seed=0):
    i = math.floor(x); f = x - i
    a, b = hsh(i, seed), hsh(i + 1, seed)
    return lerp(a, b, f * f * (3 - 2 * f))

# ---------------------------------------------------------------- music
def beat(t):
    return (t - PHASE) / BEAT

def beat_frac(t, div=1):
    b = beat(t) * div
    return b - math.floor(b)

def pulse(t, div=1, k=7.0):
    """decaying pulse on each beat subdivision"""
    return math.exp(-beat_frac(t, div) * k)

def feat(name, t):
    a = FEAT[name]; i = int(round(t * FPS))
    return float(a[min(max(i, 0), len(a) - 1)])

def snap_beat(t, div=4):
    q = BEAT / div
    return PHASE + round((t - PHASE) / q) * q

# ---------------------------------------------------------------- canvas
class G:
    def __init__(self, bg=BG, size=(W, H)):
        self.img = Image.new('RGB', size, bg)
        self.bg = bg
        self.d = aggdraw.Draw(self.img)
        self._pens = {}; self._brushes = {}; self._fonts = {}
        self.tf = None

    # transforms --------------------------------------------------------
    def tf_set(self, cx=0, cy=0, rot=0, sx=1, sy=None, ox=0, oy=0):
        """local (x,y) -> rotate/scale about (ox,oy) then translate to (cx,cy)"""
        if sy is None:
            sy = sx
        c, s = math.cos(rot), math.sin(rot)
        a, b, d_, e = c * sx, -s * sy, s * sx, c * sy
        self.d.settransform((a, b, cx - a * ox - b * oy, d_, e, cy - d_ * ox - e * oy))
        self.tf = True

    def tf_reset(self):
        self.d.settransform()
        self.tf = None

    # resources ---------------------------------------------------------
    def pen(self, c, w=2, a=1.0):
        k = (c, round(w, 1), int(a * 255))
        p = self._pens.get(k)
        if p is None:
            p = self._pens[k] = aggdraw.Pen(tuple(c), max(0.1, w), int(clamp(a) * 255))
        return p

    def brush(self, c, a=1.0):
        k = (c, int(a * 255))
        b = self._brushes.get(k)
        if b is None:
            b = self._brushes[k] = aggdraw.Brush(tuple(c), int(clamp(a) * 255))
        return b

    def font(self, name, size, c, a=1.0):
        size = max(4, int(round(size)))
        k = (name, size, c, int(clamp(a) * 255) // 4)
        f = _FONTCACHE.get(k)
        if f is None:
            if len(_FONTCACHE) > 3000:
                _FONTCACHE.clear()
            f = _FONTCACHE[k] = aggdraw.Font(tuple(c), FONT[name], size, int(clamp(a) * 255))
        return f

    # primitives --------------------------------------------------------
    def line(self, pts, c=INK, w=2, a=1.0):
        if a <= 0.004 or len(pts) < 4:
            return
        self.d.line(list(pts), self.pen(c, w, a))

    def poly(self, pts, fill=None, stroke=None, w=2, a=1.0, fa=None):
        if len(pts) < 6:
            return
        p = self.pen(stroke, w, a) if stroke is not None else None
        b = self.brush(fill, a if fa is None else fa) if fill is not None else None
        if p is None and b is None:
            return
        args = [x for x in (p, b) if x is not None]
        self.d.polygon(list(pts), *args)

    def circle(self, x, y, r, fill=None, stroke=None, w=2, a=1.0, fa=None):
        if r <= 0.05 or a <= 0.004:
            return
        p = self.pen(stroke, w, a) if stroke is not None else None
        b = self.brush(fill, a if fa is None else fa) if fill is not None else None
        args = [z for z in (p, b) if z is not None]
        if args:
            self.d.ellipse((x - r, y - r, x + r, y + r), *args)

    def ellipse(self, x, y, rx, ry, fill=None, stroke=None, w=2, a=1.0):
        p = self.pen(stroke, w, a) if stroke is not None else None
        b = self.brush(fill, a) if fill is not None else None
        args = [z for z in (p, b) if z is not None]
        if args:
            self.d.ellipse((x - rx, y - ry, x + rx, y + ry), *args)

    def rect(self, x0, y0, x1, y1, fill=None, stroke=None, w=2, a=1.0, fa=None):
        self.poly((x0, y0, x1, y0, x1, y1, x0, y1), fill, stroke, w, a, fa)

    def rrect(self, x0, y0, x1, y1, r, fill=None, stroke=None, w=2, a=1.0, fa=None):
        r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
        pts = []
        for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
            for k in range(7):
                ang = math.radians(a0 + k * 15)
                pts += [cx + r * math.cos(ang), cy + r * math.sin(ang)]
        self.poly(pts, fill, stroke, w, a, fa)

    def arc_pts(self, x, y, r, a0, a1, n=48, ry=None):
        ry = r if ry is None else ry
        out = []
        for i in range(n + 1):
            ang = a0 + (a1 - a0) * i / n
            out += [x + r * math.cos(ang), y + ry * math.sin(ang)]
        return out

    def arc(self, x, y, r, a0, a1, c=INK, w=2, a=1.0, n=48):
        self.line(self.arc_pts(x, y, r, a0, a1, n), c, w, a)

    def tsize(self, s, size, font='sans'):
        k = (s, int(round(size)), font)
        v = _SIZECACHE.get(k)
        if v is None:
            f = self.font(font, size, INK)
            v = _SIZECACHE[k] = self.d.textsize(s, f)
        return v

    def text(self, s, x, y, size, c=INK, font='sans', a=1.0, anchor='mm', rot=0.0, sx=1.0, sy=None):
        """anchor: two letters, horizontal l/m/r, vertical t/m/b (box based)"""
        if a <= 0.004 or not s:
            return (0, 0)
        if sy is None:
            sy = sx
        f = self.font(font, size, c, a)
        w, h = self.tsize(s, size, font)
        ax = {'l': 0, 'm': w / 2, 'r': w}[anchor[0]]
        ay = {'t': 0, 'm': h / 2, 'b': h}[anchor[1]]
        if rot == 0 and sx == 1 and sy == 1:
            self.d.text((x - ax, y - ay), s, f)
        else:
            self.tf_set(x, y, rot, sx, sy)
            self.d.text((-ax, -ay), s, f)
            self.tf_reset()
        return (w * sx, h * sy)

    def done(self):
        self.d.flush()
        return self.img


_FONTCACHE = {}
_SIZECACHE = {}

# ---------------------------------------------------------------- 3d
def proj(x, y, z, ry=0.0, rx=0.0, dist=900.0, cx=W / 2, cy=H / 2, f=900.0):
    c, s = math.cos(ry), math.sin(ry)
    x, z = x * c + z * s, -x * s + z * c
    c, s = math.cos(rx), math.sin(rx)
    y, z = y * c - z * s, y * s + z * c
    zz = z + dist
    if zz < 1:
        zz = 1
    k = f / zz
    return cx + x * k, cy + y * k, k

# ---------------------------------------------------------------- shape masks
def text_points(s, n, size=420, font='sans', seed=1, box=(W, H), cx=W / 2, cy=H / 2):
    im = Image.new('L', box, 0)
    dr = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT[font], size)
    dr.text((cx, cy), s, font=f, fill=255, anchor='mm')
    ys, xs = np.nonzero(np.asarray(im) > 128)
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(xs), n, replace=len(xs) < n)
    return np.stack([xs[idx], ys[idx]], 1).astype(np.float32)

def mask_points(draw_fn, n, seed=1):
    im = Image.new('L', (W, H), 0)
    dr = ImageDraw.Draw(im)
    draw_fn(dr)
    ys, xs = np.nonzero(np.asarray(im) > 128)
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(xs), n, replace=len(xs) < n)
    return np.stack([xs[idx], ys[idx]], 1).astype(np.float32)

# ---------------------------------------------------------------- post fx
_rng = np.random.default_rng(7)
_GRAIN = [(_rng.standard_normal((H // 2, W // 2)).astype(np.float32)) for _ in range(6)]
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
_VIG = (1.0 - 0.42 * (((_xx - W / 2) / (W * 0.62)) ** 2 + ((_yy - H / 2) / (H * 0.62)) ** 2)).clip(0.35, 1)
_SCAN = np.where((np.arange(H) % 3) == 0, 0.9, 1.0).astype(np.float32)[:, None]
del _yy, _xx


def post(img, t, glow=0.55, ca=0.0, grain=0.035, scan=0.0, vig=1.0, zoom=1.0, shake=(0, 0), flash=0.0, flash_c=(255, 255, 255)):
    if zoom != 1.0 or shake != (0, 0):
        z = zoom
        cx, cy = W / 2 + shake[0], H / 2 + shake[1]
        # inverse affine: output (x,y) samples input
        img = img.transform((W, H), Image.AFFINE, (1 / z, 0, cx - W / 2 / z - shake[0] * 0 , 0, 1 / z, cy - H / 2 / z), resample=Image.BILINEAR)
    a = np.asarray(img, dtype=np.float32)
    if glow > 0:
        small = img.resize((W // 6, H // 6), Image.BILINEAR).filter(ImageFilter.GaussianBlur(4))
        g = np.asarray(small.resize((W, H), Image.BILINEAR), dtype=np.float32)
        a = a + g * glow
    if ca > 0.3:
        s = int(round(ca))
        r = np.roll(a[:, :, 0], s, axis=1); b = np.roll(a[:, :, 2], -s, axis=1)
        a = np.stack([r, a[:, :, 1], b], 2)
    if vig:
        a *= (_VIG * vig + (1 - vig))[:, :, None]
    if scan > 0:
        a *= (1 - (1 - _SCAN) * scan / 0.1)[:, :, None]
    if grain > 0:
        n = _GRAIN[int(t * FPS) % len(_GRAIN)]
        n = np.repeat(np.repeat(n, 2, 0), 2, 1)
        a += (n * (grain * 255))[:, :, None]
    if flash > 0:
        a = a * (1 - flash) + np.array(flash_c, np.float32) * flash
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
