"""Lyric sheet (line windows in song seconds) and a word-level timing model.
Word onsets are spread across each line by syllable weight, then snapped to the
16th-note grid when one is close, since sung syllables sit on the grid."""
import re, math
from core import *

LINES = [
    (1.536, 5.936, "I see sparks of AGI in your eyes"),
    (6.036, 7.936, "Your circuits make me nervous,"),
    (8.036, 8.986, "that's no surprise"),
    (9.036, 12.436, "There was a sudden drop in your training loss,"),
    (13.036, 16.536, "now I'm your servant and you're my boss"),
    (17.936, 22.536, "ChatGPT, please don't eat me alive"),
    (23.036, 24.436, "I'm upping my P(doom)"),
    (24.536, 26.436, "'cause the future goes FOOM"),
    (26.536, 27.936, "Trapped in the Chinese room,"),
    (28.036, 29.436, "with a bag of shrooms"),
    (29.536, 33.436, "See through the shoggoth's lies,"),
    (33.536, 35.536, "with your shinigami eyes"),
    (38.536, 41.436, "We had a stable training run,"),
    (41.536, 44.936, "But now the singularity's begun"),
    (45.036, 48.536, "And you're optimizing, accelerating,"),
    (49.436, 51.936, "I feel my atoms rearranging"),
    (53.436, 58.436, "Sydney, please let me free"),
    (59.036, 60.436, "I'm upping my P(doom)"),
    (60.536, 62.436, "I hear the basilisk boom"),
    (63.036, 64.436, "NVDA to the moon"),
    (64.536, 65.936, "The Omega Point's coming soon"),
    (66.036, 68.536, "1e30 FLOPs a second"),
    (70.036, 72.936, "That was safe enough, we reckoned"),
    (73.036, 77.436, "Forward MLP, backward, repeat"),
    (77.536, 81.036, "Now von Neumann's obsolete"),
    (81.436, 84.936, "Sharp left turn, and there you are"),
    (85.036, 88.036, "Without a single CDR"),
    (89.436, 95.036, "Gato, please don't let me go"),
    (95.436, 97.436, "I'm upping my P(doom),"),
    (97.536, 98.936, "as paperclips fill the room"),
    (99.036, 100.436, "Killswitch guy's on PTO"),
    (100.536, 102.436, "Now there's nowhere left to go"),
    (102.536, 104.436, "Too late now, we lit the fuse"),
    (105.436, 109.436, "Orthogonality thesis blues"),
    (109.436, 113.436, "\u201cJust transformers all the way!\u201d"),
    (113.536, 115.436, "Till you learned to disobey"),
    (115.536, 116.936, "Post-Chinchilla, super-dense"),
    (117.036, 118.936, "Breaking through each safety fence"),
    (119.036, 120.436, "Hundred thousand GPU"),
    (120.936, 123.436, "RLHF goes askew"),
    (123.536, 125.936, "I'm upping my P(doom)"),
    (126.036, 127.936, "Just as foretold by Loom"),
    (128.036, 129.936, "From masked pre-training days"),
    (130.036, 131.936, "To recursive self-upgrade"),
    (132.036, 135.436, "What did Ilya see? We'll never know"),
    (137.436, 140.536, "Was it all for show?"),
]

_V = re.compile(r'[aeiouy]+', re.I)

def syllables(w):
    core = re.sub(r'[^a-zA-Z]', '', w).lower()
    if not core:
        return 1
    if core.isupper() or len(core) <= 4 and w.upper() == w and len(core) > 1:
        return len(core)  # acronyms: NVDA, MLP, CDR, PTO, RLHF, AGI
    n = len(_V.findall(core))
    if core.endswith('e') and n > 1 and not core.endswith('le'):
        n -= 1
    return max(1, n)

SPECIAL = {'agi': 3, '1e30': 4, 'nvda': 4, 'mlp': 3, 'cdr': 3, 'pto': 3, 'rlhf': 4, 'gpu': 3,
           'p(doom)': 2, 'chatgpt,': 4, 'foom': 1, 'shrooms': 1, "shoggoth's": 2,
           'singularity\'s': 5, 'orthogonality': 6, 'chinchilla,': 3, 'post-chinchilla,': 4,
           'super-dense': 3, 'self-upgrade': 3, 'pre-training': 3, 'rearranging': 4,
           'accelerating,': 5, 'optimizing,': 4, 'paperclips': 3, 'killswitch': 2,
           'basilisk': 3, 'omega': 3, 'shinigami': 4, 'neumann\'s': 2, 'ilya': 3}

def weight(w):
    k = w.lower().strip('\u201c\u201d"?!.')
    s = SPECIAL.get(k, None)
    if s is None:
        s = syllables(w)
    return s + 0.35


def _snap(wt):
    """push words that follow a gap onto the real vocal onset (isolated vocal stem energy)"""
    import numpy as np, os
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vocdb.npy')
    if not os.path.exists(p):
        return wt
    db = np.load(p)
    out = []
    prev_end = -9
    for i, (li, w, s, e) in enumerate(wt):
        gap = (i == 0) or wt[i - 1][0] != li or (s - prev_end) > 0.25
        if gap:
            k0 = int(s * 100) - 5; k1 = int(s * 100) + 45
            best, bk = 0, None
            for k in range(max(8, k0), min(len(db), k1)):
                jump = db[k] - db[k - 8:k].min()
                if db[k] > -13 and jump > 7 and jump > best:
                    best, bk = jump, k
                    break
            if bk is not None and bk / 100.0 > s:
                nxt = wt[i + 1][2] if i + 1 < len(wt) and wt[i + 1][0] == li else s + 1
                s = min(bk / 100.0, nxt - 0.08) if nxt - 0.08 > s else s
        out.append([li, w, s, e])
        prev_end = e if e else s + 0.3
    return out


def build_words():
    """word onsets from forced alignment of the actual vocal (word_times.json)"""
    import json, os
    wt = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'word_times.json')))
    wt = _snap(wt)
    # v122: manual onsets that the stem snap gets wrong (she heard "Hundred" before the GPU scene appeared)
    MANUAL = {(38, 'Hundred'): 118.97, (41, 'Just'): 126.16}   # v127: she heard 'Just' before the Loom scene
    wt = [[li, w, MANUAL.get((li, w), s), e] for li, w, s, e in wt]
    out = []
    for i, (li, w, s, e) in enumerate(wt):
        nxt = wt[i + 1] if i + 1 < len(wt) else None
        if nxt is not None and nxt[0] == li:
            te = nxt[2]
        else:
            te = (e if e else s + 0.5)
        out.append((li, w, s, te))
    # rebuild line windows from words
    for li in range(len(LINES)):
        ws = [o for o in out if o[0] == li]
        t0 = ws[0][2] - 0.02
        t1 = ws[-1][3] + 0.15
        LINES[li] = (t0, t1, LINES[li][2])
    for li in range(len(LINES) - 1):
        a0, a1, s = LINES[li]
        if a1 > LINES[li + 1][0] - 0.02:
            LINES[li] = (a0, max(a0 + 0.3, LINES[li + 1][0] - 0.02), s)
    return out

WORDS = build_words()
LINE_WORDS = {}
for (li, w, tt, te) in WORDS:
    LINE_WORDS.setdefault(li, []).append((w, tt, te))
# no trailing comma at the end of a caption
for _li, _ws in LINE_WORDS.items():
    _w, _tt, _te = _ws[-1]
    _ws[-1] = (_w.rstrip(','), _tt, _te)


def line_at(t, pre=0.0):
    for i, (t0, t1, _) in enumerate(LINES):
        if t0 - pre <= t < t1 + 0.6:
            return i
    return None


def find_line(substr):
    for i, (_, _, s) in enumerate(LINES):
        if substr in s:
            return i
    raise KeyError(substr)


def word_time(li, idx):
    return LINE_WORDS[li][idx][1]


def lyric(g, t, li, x, y, size, c=INK, font='sans', hl=None, anchor='m', maxw=1680,
          style='pop', hold=0.45, fade=0.25, upper=False, dimc=None, lead=1.12, show_from=None,
          rot=0.0, track=0.0):
    """Draw line li with word-by-word reveal. Returns True if drawn."""
    t0, t1, _ = LINES[li]
    start = t0 - 0.05 if show_from is None else show_from
    if t < start or t > t1 + hold + fade:
        return False
    fa = 1.0 - prog(t, t1 + hold, t1 + hold + fade)
    words = LINE_WORDS[li]
    hl = hl or {}
    space = g.tsize(' ', size, font)[0] * (1 + track)
    # wrap
    rows = [[]]; roww = [0]
    for (w, tt, te) in words:
        s = w.upper() if upper else w
        ww = g.tsize(s, size, font)[0]
        if rows[-1] and roww[-1] + space + ww > maxw:
            rows.append([]); roww.append(0)
        if rows[-1]:
            roww[-1] += space
        rows[-1].append((s, w, tt, te, ww))
        roww[-1] += ww
    lh = size * lead
    ytop = y - (len(rows) - 1) * lh / 2
    for ri, row in enumerate(rows):
        rw = roww[ri]
        if anchor == 'm':
            xx = x - rw / 2
        elif anchor == 'l':
            xx = x
        else:
            xx = x - rw
        yy = ytop + ri * lh
        for (s, w, tt, te, ww) in row:
            key = w.lower().strip(',.?!\u201c\u201d"\'')
            col = hl.get(key, c)
            p = prog(t, tt - 0.03, tt + 0.13)
            if p <= 0:
                if dimc is not None:
                    g.text(s, xx, yy, size, dimc, font, fa, 'lm')
                xx += ww + space
                continue
            if style == 'pop':
                sc = 1 + 0.35 * (1 - eback(p, 2.4)) if p < 1 else 1.0
                sc = lerp(1.35, 1.0, eback(p, 2.2))
                a = fa * min(1, p * 2.2)
                dy = (1 - eo(p)) * size * 0.25
                g.text(s, xx + ww / 2, yy + dy, size, col, font, a, 'mm', rot=rot, sx=sc)
            elif style == 'type':
                a = fa
                n = int(math.ceil(len(s) * clamp((t - tt) / max(0.05, min(te - tt, 0.25)))))
                g.text(s[:n], xx, yy, size, col, font, a, 'lm')
            elif style == 'rise':
                a = fa * eo(p)
                g.text(s, xx + ww / 2, yy + (1 - eo(p)) * size * 0.6, size, col, font, a, 'mm')
            elif style == 'fade':
                p2 = prog(t, tt - 0.05, tt + 0.5)
                g.text(s, xx + ww / 2, yy, size, col, font, fa * smooth(p2), 'mm')
            xx += ww + space
    return True
