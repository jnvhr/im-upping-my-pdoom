import sys, os, subprocess
import warp105
import numpy as np
from PIL import Image
from kit import *
import s4a
TL = list(s4a.TL)
for m in ('s4b', 's4c'):
    TL += __import__(m).TL
TL.sort(key=lambda r: r[0])
TYPE = set(id(r[1]) for r in TL if getattr(r[1], '__name__', '') == 'fn')


def scene_idx(t):
    k = 0
    for i, r in enumerate(TL):
        if t >= r[0]:
            k = i
    return k


def raw(t, k=None):
    if k is None:
        k = scene_idx(t)
    st, fn, bg = TL[k]
    g = G(bg)
    g.hud = dict(a=1); g.flash = 0.0; g.flash_c = GOLD; g.post = {}
    import cam3d
    cam3d._CUR[0], cam3d._CUR[1] = fn, st; cam3d._T_NOW[0] = t
    cam3d._CAPO[0] = {}
    try:
        fn(g, t, t - st)
    finally:
        ovs = cam3d._CAPO[0]; cam3d._CAPO[0] = None
    g.cap_ovs = ovs
    if not RAW_CAPS[0]:
        comp_caps(g, ovs)
    if getattr(g, 'late', None):
        g.late()      # v43: drawn over the captions (the mask transition)
    h = dict(g.hud)
    hud(g, t, a=h.get('a', 1), dx=h.get('dx', 0), dy=h.get('dy', 0), light=h.get('light', bg != BG),
        pd_scale=h.get('pd_scale', 1.0), minimal=h.get('minimal', False))
    return g, st


RAW_CAPS = [False]
_FIX = [None]


def capfix():
    if _FIX[0] is None:
        import json
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'capfix39.json')
        _FIX[0] = {int(k): v for k, v in json.load(open(p)).items()} if os.path.exists(p) else {}
    return _FIX[0]


def comp_caps(g, ovs):
    """v39: each line's caption is drawn on its own overlay (same 3D look as before), then moved
    by a fixed per-line screen offset/scale (capfix39.json) into the clear part of the frame"""
    if not ovs:
        return
    g.d.flush()
    for li, o in sorted(ovs.items()):
        o.d.flush()
        dx, dy, s = capfix().get(li, (0, 0, 1.0))
        img, al = o.img, o.alpha
        if dx == 'c' or dx or dy or s != 1.0:
            bb = al.getbbox()
            if bb is None:
                continue
            cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
            pv = getattr(o, 'piv', None)
            if pv is not None:
                cx, cy = pv     # v42: stable pivot, so words popping in don't slide the line
            if dx == 'c':
                dx = W / 2 - cx
            # x' = s*(x-cx)+cx+dx  ->  inverse affine for PIL
            a = 1.0 / s
            co = (a, 0, cx - a * (cx + dx), 0, a, cy - a * (cy + dy))
            img = img.transform((W, H), Image.AFFINE, co, Image.BILINEAR)
            al = al.transform((W, H), Image.AFFINE, co, Image.BILINEAR)
        g.img.paste(img, (0, 0), al)
    import aggdraw
    g.d = aggdraw.Draw(g.img)


def rewind_frame(t):
    import s4c
    u = prog(t, s4c.TRW0, s4c.TRW1)
    ts = 152.4 * (1 - u) ** 1.6
    img = frame(ts)
    a = np.asarray(img).astype(np.int16)
    # VHS rewind: tracking bands, horizontal skew, dimmed
    out = a.copy()
    rows = np.arange(H)
    off = (np.sin(rows / 37.0 + t * 40) * 18).astype(int)
    for band in range(3):
        y0 = int((hsh(band, int(t * 30)) * H))
        out[y0:y0 + 26] = np.clip(out[y0:y0 + 26] + 70, 0, 255)
    out = np.stack([np.roll(out[r], off[r], axis=0) if r % 4 == 0 else out[r] for r in range(H)])
    im = Image.fromarray(out.clip(0, 255).astype(np.uint8))
    g = G(BG); g.img = im
    import aggdraw
    g.d = aggdraw.Draw(g.img)
    g.text('\u25c0\u25c0  REWIND', 90, 90, 40, GOLD, 'monox', 1, 'lm')
    g.text('%06.2f' % ts, 90, 140, 28, INK, 'mono', 1, 'lm')
    return g.done()


def frame(t):
    import s4c
    if s4c.TRW0 <= t < s4c.TRW1:
        return rewind_frame(t)
    if s4c.TRW1 <= t < s4c.TBLK:
        return frame(0.0)
    k = scene_idx(t)
    g, st = raw(t, k)
    img = g.done()
    kw = dict(glow=0.6, ca=0.0, grain=0.03, vig=0.9)
    kw.update(g.post)
    kw['ca'] = 0.0
    since = t - st
    fl = g.flash
    out = post(img, t, flash=clamp(fl), flash_c=g.flash_c, **kw)
    out = _xfade(t, k, out, kw)
    if getattr(TL[k][1], '__name__', '') == 'fn' and getattr(TL[k][1], 'li', None) == 6 and k + 1 < len(TL):
        import trans4
        stn = TL[k + 1][0]
        if stn - trans4.P_PRE <= t < stn:
            geom = trans4.portal_geom(np.asarray(img.convert('RGB')))
            out = post(trans4.portal_card(img, geom, trans4.portal_s(t, stn)), t, flash=clamp(fl), flash_c=g.flash_c, **kw)
    # 2D typography -> 3D: the last word flies through the lens while the 3D world fades up
    if k > 0 and getattr(TL[k - 1][1], '__name__', '') == 'fn':
        import trans4
        li = getattr(TL[k - 1][1], 'li', None)
        ex = trans4.EXITS.get(li)
        if li == 6 and since < trans4.P_POST:
            # v40: smooth portal dive, continues from the pre-roll on the card
            g2, _ = raw(st - 0.02, k - 1)
            kw2 = dict(glow=0.6, ca=0.0, grain=0.03, vig=0.9); kw2.update(g2.post); kw2['ca'] = 0.0
            craw = g2.done()
            geom = trans4.portal_geom(np.asarray(craw.convert('RGB')))
            sp = trans4.portal_s(t, st)
            cp = np.asarray(post(trans4.portal_card(craw, geom, sp), t, flash=0, flash_c=GOLD, **kw2).convert('RGB'))
            out = Image.fromarray(trans4.portal_mix(cp, np.asarray(out.convert('RGB')), geom, sp))
        elif li == 6:
            pass
        elif ex is not None and since < trans4.DURS.get(li, trans4.DUR):
            # v38: a creative exit out of the chorus card instead of zoom + crossfade
            g2, _ = raw(st - 0.02, k - 1)
            kw2 = dict(glow=0.6, ca=0.0, grain=0.03, vig=0.9); kw2.update(g2.post); kw2['ca'] = 0.0
            a = np.asarray(post(g2.done(), st - 0.02, flash=0, flash_c=GOLD, **kw2).convert('RGB')).copy()
            bb = np.asarray(out.convert('RGB')).copy()
            out = Image.fromarray(ex(a, bb, since / trans4.DURS.get(li, trans4.DUR)))
        elif ex is None and since < 0.42:
            u = eio(since / 0.42)
            g2, _ = raw(st - 0.02, k - 1)
            b = g2.done()
            z = 1 + 2.6 * u
            bw, bh = int(W * z), int(H * z)
            bz = b.resize((bw, bh), Image.BILINEAR).crop(((bw - W) // 2, (bh - H) // 2, (bw - W) // 2 + W, (bh - H) // 2 + H))
            out = Image.blend(bz, out, u)
    return out


def _xfade(t, k, out, kw):
    """continuous handoff: the previous scene keeps running under a crossfade"""
    st = TL[k][0]
    if k > 0 and getattr(TL[k][1], 'xfade', 0) and t - st < TL[k][1].xfade:
        u = eio((t - st) / TL[k][1].xfade)
        g2, _ = raw(t, k - 1)
        kw2 = dict(glow=0.6, ca=0.0, grain=0.03, vig=0.9); kw2.update(g2.post); kw2['ca'] = 0.0
        b = post(g2.done(), t, flash=0, flash_c=GOLD, **kw2)
        out = Image.blend(b, out, u)
    return out


def render_range(f0, f1, out):
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', str(FPS),
           '-i', '-', '-c:v', 'libx264', '-preset', os.environ.get('X264P', 'veryfast'), '-crf', os.environ.get('X264CRF', '18'), '-pix_fmt', 'yuv420p', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(f0, f1):
        p.stdin.write(frame(warp105.src(f / FPS)).tobytes())   # v105: f is an OUTPUT frame; map to song-source time
        if f % 150 == 0:
            print(out, f, flush=True)
    p.stdin.close(); p.wait()


if __name__ == '__main__':
    if sys.argv[1] == 'still':
        os.makedirs('st4', exist_ok=True)
        for ts in sys.argv[2:]:
            frame(float(ts)).save('st4/%s.png' % ts)
    elif sys.argv[1] == 'range':
        render_range(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
