import sys, json
import numpy as np
from PIL import Image
D = sys.argv[1]
SEGS = {  # name: (first, last) source frames
    'stance': (0, 35), 'atk': (36, 59), 'cast': (81, 116), 'hit': (123, 151), 'beam': (184, 201)}

def label(m):
    """4-connected components on a small boolean mask (union-find)."""
    h, w = m.shape; lab = np.zeros((h, w), np.int32); par = [0]; nxt = 1
    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]; a = par[a]
        return a
    for y in range(h):
        row = m[y]
        for x in range(w):
            if not row[x]: continue
            up = lab[y-1, x] if y else 0; lf = lab[y, x-1] if x else 0
            if up and lf:
                a, b = find(up), find(lf); lab[y, x] = min(a, b); par[max(a, b)] = min(a, b)
            elif up or lf: lab[y, x] = up or lf
            else: par.append(nxt); lab[y, x] = nxt; nxt += 1
    for i in range(len(par)): par[i] = find(i)
    return np.array(par)[lab]

def isolate(fr):
    im = np.array(Image.open(f'{D}/cut/c{fr:03d}.png').convert('RGBA')).astype(np.float32)
    a = im[..., 3]; rgb = im[..., :3]; lum = rgb @ np.array([.299, .587, .114], np.float32)
    S = 4; small = (a[::S, ::S] > 110)
    lab = label(small); best, bscore = 0, -1
    bright = (lum[::S, ::S] > 150) & small
    for k in np.unique(lab):
        if k == 0: continue
        sc = int((bright & (lab == k)).sum())
        if sc > bscore: best, bscore = k, sc
    keep = lab == best
    # also keep small pieces that sit inside/near her box (staff tip, loose hair)
    ys, xs = np.nonzero(keep); y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max(); pad = 6
    for k in np.unique(lab):
        if k in (0, best): continue
        cy, cx = np.nonzero(lab == k)
        if cy.size < 400 and cy.min() >= y0-pad and cy.max() <= y1+pad and cx.min() >= x0-pad and cx.max() <= x1+pad: keep |= lab == k
    mask = np.kron(keep, np.ones((S, S), bool))[:a.shape[0], :a.shape[1]]
    # robot overlapping her: cut at the first tall dark column beyond her bright body
    dark = (lum < 60) & (a > 110) & mask
    bys, bxs = np.nonzero((lum > 150) & mask)
    H = (ys.max()-ys.min()+1)*S
    if bxs.size:
        dcol = dark.sum(0); cx_b = np.median(bxs)
        dxs = np.nonzero(dark)[1]
        if dxs.size:
            side = 1 if dxs.mean() > cx_b else -1
            start = int(np.percentile(bxs, 80 if side > 0 else 20))
            rng = range(start, a.shape[1]) if side > 0 else range(start, -1, -1)
            for x in rng:
                if dcol[x] > H*.33:
                    if side > 0: mask[:, x-2:] = False
                    else: mask[:, :x+3] = False
                    break
    a2 = np.where(mask, a, 0)
    out = im.copy(); out[..., 3] = a2
    ys, xs = np.nonzero(a2 > 40)
    top, bot = ys.min(), ys.max(); h = bot-top
    band = (ys > top+h*.4) & (ys < top+h*.7)
    cx = float(np.median(xs[band])) if band.any() else float(np.median(xs))
    return Image.fromarray(out.astype(np.uint8)), (int(xs.min()), int(top), int(xs.max()), int(bot)), cx, h

meta = {}
for name, (f0, f1) in SEGS.items():
    rows = []
    for fr in range(f0, f1+1):
        img, box, cx, h = isolate(fr)
        img.save(f'{D}/iso/{name}-{fr:03d}.png'); rows.append({'fr': fr, 'box': box, 'cx': cx, 'h': int(h)})
    meta[name] = rows; print(name, len(rows), 'heights', [r['h'] for r in rows][:8], flush=True)
json.dump(meta, open(f'{D}/iso/meta.json', 'w'))
