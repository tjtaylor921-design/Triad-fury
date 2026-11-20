# Video to sprite animation

Turns a fighter video into per-move WebP sprite sheets for `ANIMS` in `index.html`.
Not shipped with the game; run locally. Needs `ffmpeg` and `pip install "rembg[cpu]"`.

1. Extract frames: `ffmpeg -i clip.mp4 WORK/full/f%03d.png`
2. Cut out the background (u2net): `python3 segall.py WORK <first> <last>` (writes `WORK/cut/`)
3. Keep only the fighter (drops the opponent and scraps; trims where they touch): edit `SEGS`
   in `isolate.py` to the frame ranges of each move, then `python3 isolate.py WORK`
   (writes `WORK/iso/` and `meta.json`; check the frames, drop any with leftovers)
4. Pack sheets: edit `PLAN` in `build.py`, then `python3 build.py WORK art/anim`
   and paste the printed JSON into `ANIMS` in `index.html` (add the files to `sw.js` too).

Best source clips: locked camera, side view facing right, full body in frame, plain background.
