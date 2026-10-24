"""v39: choose a per-line screen offset/scale for each caption so it sits in the clear part of the frame.
usage: python3 capfix39.py PART NPARTS   -> /tmp/capfix_PART.json ;  python3 capfix39.py merge NPARTS"""
import sys, json, math
import numpy as np
from PIL import Image
import render4
from render4 import raw, RAW_CAPS
from lyrics import LINES
from core import W, H

SW, SH = 192, 108
SAMPLES = 7


def busy_mask(img, bg):
    a = np.asarray(img.resize((SW, SH), Image.BILINEAR), np.float32)
    d = np.abs(a - np.array(bg[:3], np.float32)).max(axis=2)
    m = d > 38
    # dilate a little so captions keep a margin from objects
    mm = m.copy()
    for dy in (-2, -1, 0, 1, 2):
        for dx in (-2, -1, 0, 1, 2):
            mm |= np.roll(np.roll(m, dy, 0), dx, 1)
    # HUD zones count as busy
    mm[:int(SH * 0.14), int(SW * 0.82):] = True
    mm[:int(SH * 0.08), :] = True
    mm[int(SH * 0.92):, :] = True
    return mm


def xf_mask(al, dx, dy, s, small=None):
    bb = al.getbbox()
    if bb is None:
        return None
    k = SW / W
    cx, cy = (bb[0] + bb[2]) / 2 * k + SW, (bb[1] + bb[3]) / 2 * k + SH
    dx, dy = dx * k, dy * k
    big = Image.new('L', (SW * 3, SH * 3), 0)
    big.paste(small, (SW, SH))
    a = 1.0 / s
    co = (a, 0, cx - a * (cx + dx), 0, a, cy - a * (cy + dy))
    out = big.transform((SW * 3, SH * 3), Image.AFFINE, co, Image.BILINEAR)
    return np.asarray(out) > 50


def samples_for(li):
    t0, t1, _ = LINES[li]
    return [t0 + 0.15 + (t1 + 0.25 - t0 - 0.15) * k / (SAMPLES - 1) for k in range(SAMPLES)]


def analyse(li):
    RAW_CAPS[0] = True
    data = []
    for t in samples_for(li):
        g, st = raw(t)
        ov = g.cap_ovs.get(li)
        if ov is None:
            continue
        ov.d.flush()
        if ov.alpha.getbbox() is None:
            continue
        g.d.flush()
        data.append((busy_mask(g.img, g.bg), ov.alpha.copy(), ov.alpha.resize((SW, SH), Image.BILINEAR)))
    if not data:
        return None
    best = None
    dys = [k * H * 0.05 for k in range(-16, 17)]
    for s in (1.0, 0.88, 0.76, 0.66, 0.58):
        for dx in (0.0, 'c'):
            for dy in dys:
                cost = 0.0
                for bm, al, sm in data:
                    bb = al.getbbox()
                    ddx = 0.0 if dx == 0.0 else (W / 2 - (bb[0] + bb[2]) / 2)
                    m = xf_mask(al, ddx, dy, s, sm)
                    tot = m.sum()
                    if tot == 0:
                        cost += 1; continue
                    inner = m[SH:2 * SH, SW:2 * SW]
                    x0, x1, y0, y1 = int(SW * 0.04), int(SW * 0.96), int(SH * 0.06), int(SH * 0.94)
                    inside = inner[y0:y1, x0:x1].sum()
                    off = 1 - inside / tot
                    ov = (inner & bm).sum() / tot
                    wfrac = ((bb[2] - bb[0]) * s) / W
                    cost += ov + 3 * off + max(0, wfrac - 0.70) * 2
                cost /= len(data)
                cost += 0.10 * (1 - s) + 0.06 * abs(dy) / H + (0.03 if dx == 'c' else 0)
                if best is None or cost < best[0]:
                    best = (cost, dx, dy, s)
    # natural placement cost
    return best


if __name__ == '__main__':
    if sys.argv[1] == 'merge':
        out = {}
        for p in range(int(sys.argv[2])):
            out.update(json.load(open('/tmp/capfix_%d.json' % p)))
        json.dump(out, open('capfix39_raw.json', 'w'), indent=1)
        print(len(out))
    else:
        part, n = int(sys.argv[1]), int(sys.argv[2])
        res = {}
        for li in range(len(LINES)):
            if li % n != part or li in (6, 17, 28, 40):
                continue
            b = analyse(li)
            if b is None:
                continue
            res[li] = [b[0], b[1], b[2], b[3]]
            print(li, res[li], flush=True)
        json.dump(res, open('/tmp/capfix_%d.json' % part, 'w'))
