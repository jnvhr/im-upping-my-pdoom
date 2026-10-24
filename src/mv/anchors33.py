"""v33: precompute world anchors for every caption -> anchors33.pkl (run: python3 anchors33.py part nparts; then merge)"""
import sys, pickle, math
import render4, cam3d
from cam3d import *
from lyrics import LINES
TL = render4.TL
STEP = 0.25


def capture(fn, st, tt):
    g2 = G(BG); g2.hud = dict(a=1); g2.flash = 0.0; g2.flash_c = GOLD; g2.post = {}
    cam3d._REC[0] = {}
    cam3d._CUR[0], cam3d._CUR[1] = fn, st
    try:
        fn(g2, tt, tt - st)
    except Exception as e:
        pass
    r = cam3d._REC[0]; cam3d._REC[0] = None
    return r


def tbox(li, size, font, upper, maxw):
    return cam3d._text_bbox(li, size, font, upper, maxw)


def screen_box(cam, pl, bb):
    center, right, up, width = pl
    (lw, lh), (x0, y0, x1, y1) = bb
    ht = width * lh / lw
    pts = []
    for px, py in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        w = v_add(center, v_add(v_mul(right, (px / lw - 0.5) * width), v_mul(up, (0.5 - py / lh) * ht)))
        q = cam.p(w)
        if q is None:
            return None
        pts.append(q)
    return pts


def score(cam, pl, bb):
    pts = screen_box(cam, pl, bb)
    if pts is None:
        return 0.0
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    if pts[1][0] <= pts[0][0]:          # mirrored / upside down
        return 0.0
    if min(xs) < 0.02 * W or max(xs) > 0.98 * W or min(ys) < 0.02 * H or max(ys) > 0.98 * H:
        return 0.0
    w = max(xs) - min(xs)
    if w < 0.22 * W:
        return 0.3
    if w > 0.80 * W:
        return 0.4
    if abs((pts[1][1] - pts[0][1])) > 0.5 * w:  # strongly tilted
        return 0.5
    cy = (min(ys) + max(ys)) / 2
    if 0.38 * H < cy < 0.62 * H:        # sitting over the middle of the frame
        return 0.5
    return 1.0


def solve(part, nparts):
    out = {}
    for k in range(part, len(TL), nparts):
        st, fn, bg = TL[k]
        if getattr(fn, '__name__', '') == 'fn':
            continue
        en = TL[k + 1][0] if k + 1 < len(TL) else st + 20
        caps = {}
        tt = st + 0.01
        while tt < en + 0.6:
            for li, a in capture(fn, st, tt).items():
                caps.setdefault(li, []).append((tt, a))
            tt += STEP
        for li, lst in caps.items():
            t0, t1, _ = LINES[li]
            lst = [(t, a) for (t, a) in lst if t0 - 0.15 <= t <= t1 + 0.8]
            if not lst:
                continue
            a0 = lst[0][1]
            bb = tbox(li, a0[5], a0[6], a0[7], a0[8])
            if not bb or not bb[1]:
                continue
            pls = [(t, cam3d._place(li, *a)) for t, a in lst]   # each time's own placement (band-pushed)
            span = max(t1 - t0, 0.3)
            best = None
            for ci, (tc, plc) in enumerate(pls):
                if tc > t0 + 0.7 * span:
                    break
                sc = 0.0; wsum = 0.0
                for (t, a), _ in zip(lst, pls):
                    wgt = 2.0 if t < t1 else 0.6
                    sc += wgt * score(a[0], plc, bb); wsum += wgt
                sc /= wsum
                if best is None or sc > best[0] + 1e-6:
                    best = (sc, tc, plc)
            fixed_design = max(math.dist(a[1], lst[0][1][1]) for _, a in lst) < 1.0   # scene already placed it in world space
            if best and (best[0] >= 0.9 or (fixed_design and (best[0] >= 0.88 or 'jaw' in cam3d.scene_key(fn)))):
                keys = [(best[1],) + tuple(best[2])]
                kind = 'fixed@%.2f' % best[1]
            else:   # camera moves too much for one fixed spot: a slow, heavily smoothed world anchor
                def smooth(sig):
                    ks = []
                    for t, _ in pls:
                        ws = [(math.exp(-((t2 - t) / sig) ** 2) if sig > 0 else (1.0 if t2 == t else 0.0), p) for t2, p in pls]
                        tw = sum(w for w, _ in ws)
                        c = tuple(sum(w * p[0][i] for w, p in ws) / tw for i in range(3))
                        r = v_norm(tuple(sum(w * p[1][i] for w, p in ws) for i in range(3)))
                        u = v_norm(tuple(sum(w * p[2][i] for w, p in ws) for i in range(3)))
                        wd = sum(w * p[3] for w, p in ws) / tw
                        ks.append((t, c, r, u, wd))
                    return ks
                for sig in (1.0, 0.7, 0.5, 0.35, 0.22, 0.12):
                    keys = smooth(sig)
                    m = sum(score(a[0], k[1:], bb) for (t, a), k in zip(lst, keys)) / len(keys)
                    if m >= 0.9:
                        break
                best = (m, sig, None)
                kind = 'drift'
            out[(cam3d.scene_key(fn), li)] = keys
            print('%-28s L%-2d %-11s score=%.2f %s' % (cam3d.scene_key(fn), li, kind, best[0] if best else -1, best[1] if best else ''), flush=True)
    return out


if __name__ == '__main__':
    if sys.argv[1] == 'merge':
        tab = {}
        for f in sys.argv[2:]:
            tab.update(pickle.load(open(f, 'rb')))
        pickle.dump(tab, open('anchors33.pkl', 'wb'))
    else:
        p, n = int(sys.argv[1]), int(sys.argv[2])
        pickle.dump(solve(p, n), open('/tmp/anc_%d.pkl' % p, 'wb'))
