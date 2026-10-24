import sys, os, subprocess
from kit import *
import s3a
TL = list(s3a.TL)
for m in ('s3b', 's3c'):
    try:
        TL += __import__(m).TL
    except ImportError as e:
        print('missing', m, e)
TL.sort(key=lambda r: r[0])


def scene_at(t):
    cur = TL[0]
    for r in TL:
        if t >= r[0]:
            cur = r
    return cur


def frame(t):
    st, fn, bg = scene_at(t)
    g = G(bg)
    g.hud = dict(a=1); g.flash = 0.0; g.flash_c = GOLD; g.post = {}
    fn(g, t, t - st)
    h = dict(g.hud)
    hud(g, t, a=h.get('a', 1), dx=h.get('dx', 0), dy=h.get('dy', 0), light=h.get('light', bg != BG),
        pd_scale=h.get('pd_scale', 1.0), minimal=h.get('minimal', False))
    img = g.done()
    kw = dict(glow=0.6, ca=0.0, grain=0.03, vig=0.9)
    kw.update(g.post)
    kw['ca'] = 0.0  # chromatic aberration makes blue/red fringes: banned palette
    since = t - st
    fl = g.flash
    if since < 0.08 and st > 0.5:
        fl = max(fl, 0.25 * (1 - since / 0.08))
    return post(img, t, flash=clamp(fl), flash_c=g.flash_c, **kw)


def render_range(f0, f1, out):
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', str(FPS),
           '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(f0, f1):
        p.stdin.write(frame(f / FPS).tobytes())
        if f % 150 == 0:
            print(out, f, flush=True)
    p.stdin.close(); p.wait()


if __name__ == '__main__':
    if sys.argv[1] == 'still':
        os.makedirs('st3', exist_ok=True)
        for ts in sys.argv[2:]:
            frame(float(ts)).save('st3/%s.png' % ts)
    elif sys.argv[1] == 'range':
        render_range(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
