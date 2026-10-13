"""A watch-through of a render (BRIEF.md step 7): the video sampled at 2 frames a second, tiled into contact sheets
with each frame's time, bar and shot under it, to look at against the timeline.

Sheets go to production/qa/watch/<name>_NN.jpg, 48 frames (24 s) each.

Usage, with the project's .venv:
  .venv/Scripts/python tools/watch.py production/out/roughcut.mp4 --name pass1
  .venv/Scripts/python tools/watch.py production/out/roughcut.mp4 --name pass1 --from 60 --to 120 --fps 4
"""
import argparse
import bisect
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "production" / "storyboard" / "shots.json"
SONG = ROOT / "production" / "analysis" / "song.json"
OUT = ROOT / "production" / "qa" / "watch"
TILE = (320, 180)
COLS, ROWS = 8, 6
LABEL = 22


def frames(video, fps, t0, t1, rate=24):
    """Every (rate / fps)-th frame of the video from t0 to t1 seconds, exactly (ffmpeg's fps filter would take the
    frame nearest each step, up to half a step off), as (its time, RGB array at TILE size)."""
    step = max(1, round(rate / fps))
    f0 = int(round(t0 * rate))
    f1 = int(round(t1 * rate)) if t1 is not None else 10 ** 9
    cmd = ["ffmpeg", "-v", "error", "-i", str(video), "-vf",
           f"select='between(n\\,{f0}\\,{f1})*not(mod(n-{f0}\\,{step}))',scale={TILE[0]}:{TILE[1]}",
           "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    size = TILE[0] * TILE[1] * 3
    for i in range(len(raw) // size):
        yield (f0 + i * step) / rate, np.frombuffer(raw[i * size:(i + 1) * size], np.uint8).reshape(TILE[1], TILE[0], 3)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("video")
    ap.add_argument("--name", required=True)
    ap.add_argument("--fps", type=float, default=2.0)
    ap.add_argument("--from", dest="t0", type=float, default=0.0)
    ap.add_argument("--to", dest="t1", type=float)
    args = ap.parse_args()
    shots = json.loads(SHOTS.read_text(encoding="utf-8"))["shots"]
    starts = [s["t0"] for s in shots]
    downbeats = json.loads(SONG.read_text(encoding="utf-8"))["downbeats_s"]
    font = ImageFont.load_default(size=15)
    OUT.mkdir(parents=True, exist_ok=True)
    per = COLS * ROWS
    batch, n = [], 0

    def flush():
        nonlocal batch, n
        if not batch:
            return
        sheet = Image.new("RGB", (COLS * (TILE[0] + 4) + 4, ROWS * (TILE[1] + LABEL + 4) + 4), (12, 12, 14))
        d = ImageDraw.Draw(sheet)
        for k, (t, im) in enumerate(batch):
            x, y = 4 + (k % COLS) * (TILE[0] + 4), 4 + (k // COLS) * (TILE[1] + LABEL + 4)
            sheet.paste(Image.fromarray(im), (x, y))
            s = shots[max(0, bisect.bisect_right(starts, t) - 1)]
            bar = bisect.bisect_right(downbeats, t) - 9  # the board's bars count from the intro's -8
            d.text((x + 2, y + TILE[1] + 3), f"{int(t // 60)}:{t % 60:05.2f}  bar {bar}  {s['id']} {s['framing']} {s['motion_tier']}",
                   fill=(225, 225, 225), font=font)
        n += 1
        dest = OUT / f"{args.name}_{n:02d}.jpg"
        sheet.save(dest, quality=84)
        print(dest.relative_to(ROOT).as_posix(), f"{batch[0][0]:.1f}-{batch[-1][0]:.1f} s")
        batch = []

    for t, im in frames(args.video, args.fps, args.t0, args.t1):
        batch.append((t, im))
        if len(batch) == per:
            flush()
    flush()


if __name__ == "__main__":
    main()
