"""The print grade for Seedance start images (BRIEF.md step 0, PLAN.md phase 0c).

ByteDance's Seedance 2.5, the only provider behind OpenRouter's, refuses photoreal faces at input,
AI-generated ones included (InputImageSensitiveContentDetected.PrivacyInformation); stylised faces
pass. ESCAPE VELOCITY's plates went in "graded in the video's print look", a halftone screen per
chapter, and came back grey because that grade was monochrome. This is the colour version: four CMYK
dot screens at the classic angles over the plate, with film grain, so the clips keep their colour.

What passed in step 0, and gave the texture that was approved, is 5 px cells on a 1280x720 image, so
grade() first scales anything bigger to 1280x720 (Seedance works at 720p; a 5 px screen on a
2944x1648 Midjourney plate would shrink to about 2 px). Two quirks are kept on purpose, because
they're part of that approved texture: the antialiasing ramp is centred on the dot's edge, so even
zero ink prints a faint dot at each cell centre and solid black keeps pinholes; and the grain comes
from a fixed seed unless you pass one (pass the frame number when grading video frames).

Usage, with the project's .venv:
  .venv/Scripts/python tools/print_grade.py IN.png OUT.png            # 1280x720, 5 px cells
  .venv/Scripts/python tools/print_grade.py IN.png OUT.png --size 0   # keep the image's own size
  .venv/Scripts/python tools/print_grade.py IN.png OUT.png --mono     # 1-bit xerox, as ESCAPE VELOCITY's v1
"""
import argparse
import functools

import numpy as np
from PIL import Image

ANGLES = (15.0, 75.0, 0.0, 45.0)  # cyan, magenta, yellow, black
PAPER = np.array([0.965, 0.955, 0.93])
CELL = 5.0                        # the dot spacing that passed in step 0
SIZE = (1280, 720)                # the size it passed at: Seedance's 720p


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def coverage_radius(value):
    """The dot radius, in cells, that inks `value` of the cell: a round dot's area up to where dots
    touch (r = 0.5), then closing the corners by r = 0.707, where the cell is solid."""
    touch = np.pi / 4
    return np.where(value <= touch, np.sqrt(value / np.pi),
                    0.5 + (value - touch) / (1 - touch) * (np.sqrt(0.5) - 0.5))


@functools.lru_cache(maxsize=16)
def grid(h, w, cell, angle):
    """For a screen rotated by `angle`: each pixel's cell centre in the image, and its distance to it in cells.
    The same for every frame, so it's worked out once."""
    th = np.deg2rad(angle)
    cs, sn = np.cos(th), np.sin(th)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    u, v = (xx * cs + yy * sn) / cell, (-xx * sn + yy * cs) / cell
    uc, vc = np.floor(u) + 0.5, np.floor(v) + 0.5
    xc = np.clip((uc * cs - vc * sn) * cell, 0, w - 1).astype(int)
    yc = np.clip((uc * sn + vc * cs) * cell, 0, h - 1).astype(int)
    return yc, xc, np.hypot(u - uc, v - vc)


def screen(value, cell, angle):
    """Ink coverage per pixel for one channel (HxW, 0-1) printed as dots on a grid rotated by `angle`.
    Each dot's area follows the channel's mean over its cell."""
    yc, xc, dist = grid(*value.shape, float(cell), float(angle))
    radius = coverage_radius(value[yc, xc])
    aa = 0.8 / cell
    return 1 - smoothstep(radius - aa, radius + aa, dist)


def blur(channel, sigma):
    from scipy.ndimage import gaussian_filter
    return gaussian_filter(channel.astype(np.float32), sigma, mode="nearest")


def colour_halftone(rgb, cell=CELL, grain=0.03, seed=0, contrast=0.35):
    rgb = rgb + contrast * (rgb - 0.5) * (1 - np.abs(2 * rgb - 1))  # a gentle S-curve: blacks stay deep
    rgb = np.clip(rgb, 0, 1)
    k = 1 - rgb.max(-1)
    cmy = (1 - rgb - k[..., None]) / np.maximum(1 - k[..., None], 1e-6)
    inks = [screen(blur(ch, cell / 2), cell, a) for ch, a in zip([*np.moveaxis(cmy, -1, 0), k], ANGLES)]
    c, m, y, kk = inks
    out = PAPER * np.stack([(1 - c), (1 - m), (1 - y)], -1) * (1 - kk)[..., None]
    rng = np.random.default_rng(seed)
    out += rng.normal(0, grain, out.shape[:2])[..., None]
    return np.clip(out, 0, 1)


def mono_xerox(rgb, cell=2.0, seed=0):
    """1-bit: luminance with crushed contrast, thresholded against noise."""
    lum = rgb @ np.array([0.299, 0.587, 0.114])
    lum = np.clip((lum - 0.12) / 0.7, 0, 1)
    rng = np.random.default_rng(seed)
    noise = blur(rng.random(lum.shape).astype(np.float32), cell / 2)
    noise = (noise - noise.min()) / (noise.max() - noise.min())
    return np.repeat((lum > noise)[..., None], 3, -1).astype(np.float32)


def fit(img, size=SIZE):
    """Scale an image bigger than `size` down to it. Within 1 % of its aspect (a Midjourney 16:9 plate is
    2944x1648) it goes to exactly `size`; otherwise it keeps its own aspect inside it."""
    if not size or (img.width <= size[0] and img.height <= size[1]):
        return img
    if abs(img.width / img.height - size[0] / size[1]) <= 0.01 * size[0] / size[1]:
        return img.resize(size, Image.LANCZOS)
    img = img.copy()
    img.thumbnail(size, Image.LANCZOS)
    return img


def grade(src, dest, cell=CELL, grain=0.03, mono=False, size=SIZE, seed=0):
    rgb = np.asarray(fit(Image.open(src).convert("RGB"), size), dtype=np.float32) / 255
    out = mono_xerox(rgb, cell, seed) if mono else colour_halftone(rgb, cell, grain, seed)
    Image.fromarray((out * 255 + 0.5).astype(np.uint8)).save(dest)
    return dest


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("src")
    p.add_argument("dest")
    p.add_argument("--cell", type=float, default=CELL, help=f"dot spacing in pixels (default {CELL:g})")
    p.add_argument("--grain", type=float, default=0.03, help="grain strength (default 0.03)")
    p.add_argument("--size", default="1280x720", help="scale anything bigger down to WxH first (default 1280x720; 0 keeps the size)")
    p.add_argument("--seed", type=int, default=0, help="the grain's seed; pass the frame number for video frames")
    p.add_argument("--mono", action="store_true", help="1-bit xerox instead of the colour halftone (--cell sets its noise)")
    args = p.parse_args()
    size = None if args.size in ("0", "") else tuple(int(x) for x in args.size.lower().split("x"))
    grade(args.src, args.dest, args.cell, args.grain, args.mono, size, args.seed)


if __name__ == "__main__":
    main()
