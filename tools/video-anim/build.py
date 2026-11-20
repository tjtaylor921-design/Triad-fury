"""Pack the cut-out Sylphine frames into one WebP sprite sheet per move, normalised for scale and anchored at the feet."""
import sys, json, math
import numpy as np
from PIL import Image
D, OUT = sys.argv[1], sys.argv[2]
meta = json.load(open(f'{D}/iso/meta.json'))
TH = 410  # target figure height of the guard pose, in sheet pixels
PLAN = {  # anim key: (segment, first, last, scale mode)
    'stance': ('stance', 0, 35, 'perframe'),
    'atk': ('atk', 36, 44, 36),
    'cast': ('cast', 85, 109, 85),
    'hit': ('hit', 129, 149, 'hit'),
}
info = {}
for key, (seg, a, b, mode) in PLAN.items():
    rows = {r['fr']: r for r in meta[seg]}
    if mode == 'hit':
        k_all = TH * 1.1 / rows[151]['h'] if 151 in rows else TH * 1.1 / rows[b]['h']
    frames = []
    for fr in range(a, b + 1):
        r = rows[fr]
        if mode == 'perframe': k = TH / r['h']
        elif mode == 'hit': k = k_all
        else: k = TH / rows[mode]['h']
        im = Image.open(f'{D}/iso/{seg}-{fr:03d}.png').convert('RGBA')
        x0, y0, x1, y1 = r['box']; pad = 6
        im = im.crop((x0 - pad, y0 - pad, x1 + pad + 1, y1 + pad + 1))
        arr = np.array(im).astype(np.float32)
        al = arr[..., 3]; al = np.clip((al - 50) * 1.35, 0, 255); arr[..., 3] = al  # firm up soft, haloed edges
        im = Image.fromarray(arr.astype(np.uint8))
        w, h = im.size; im = im.resize((max(1, round(w * k)), max(1, round(h * k))), Image.LANCZOS)
        ax = (r['cx'] - (x0 - pad)) * k; ay = (y1 - (y0 - pad)) * k
        frames.append((im, ax, ay))
    L = math.ceil(max(f[1] for f in frames)); Rr = math.ceil(max(f[0].width - f[1] for f in frames))
    T = math.ceil(max(f[2] for f in frames)); Bt = math.ceil(max(f[0].height - f[2] for f in frames))
    cw, ch = L + Rr, T + Bt; n = len(frames); cols = min(n, max(1, 4000 // cw)); rws = math.ceil(n / cols)
    sheet = Image.new('RGBA', (cw * cols, ch * rws), (0, 0, 0, 0))
    for i, (im, ax, ay) in enumerate(frames):
        cx, cy = (i % cols) * cw, (i // cols) * ch
        sheet.alpha_composite(im, (round(cx + L - ax), round(cy + T - ay)))
    path = f'{OUT}/sylphine-{key}.webp'; sheet.save(path, 'WEBP', quality=82, method=6)
    info[key] = {'src': f'art/anim/sylphine-{key}.webp', 'n': n, 'cols': cols, 'cw': cw, 'ch': ch, 'ax': L, 'ay': T}
    import os; print(key, n, 'cell', cw, ch, 'sheet', sheet.size, '%.0fKB' % (os.path.getsize(path) / 1024))
print(json.dumps(info))
