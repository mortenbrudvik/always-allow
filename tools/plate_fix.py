"""Local fixes for picked plates (BRIEF.md step 4, "fix weak plates"), run by `tools/plates.py fix`.

Each fix works on the pick's own Midjourney image and is recorded in production/storyboard/plate_picks.json with any
crop it chose, so `apply()` can always remake production/assets/frames/<plate>.png from the inbox file:
  debar      crop off letterbox bars Midjourney painted into the image (a centred crop at the image's own aspect)
  recolour   turn a teal or navy wall to the palette's cobalt #1f4fd6. Only saturated blues and teals move, so her
             skin, the grey uniform and her grey-blue eyes keep their colour, and the wall keeps its shading.
  inpaint    paint out small things inside boxes (fractions of the image), such as stray figures or a word on a
             window: the pixels that differ from the box's border (optionally only the darker or only the lighter
             ones, and by how much) are filled from around them and given grain again. Keep a box off any edge
             the plate needs straight: the fill blurs what it touches.
  flatfill   paint out whatever stands on a flat-coloured floor, down to a straight edge that stays sharp
  sky        lift a sky that came back dark to a pale studio grey above a horizon, keeping its grain
  place      crop so her face sits where the prompt asked, left or right of centre (the other side is for the
             type), found with MediaPipe's face landmarker; the crop keeps at least MIN_SCALE of the image, so a
             plate stays above 2,000 px wide, and keeps the face's height in the frame
"""
import os
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

MODEL = Path.home() / ".cache" / "mediapipe" / "face_landmarker.task"  # as tools/lipcheck.py

COBALT_HUE = 224.5   # #1f4fd6
MIN_SCALE = 0.72     # of the image's width and height: 2,120 px of a 2,944 px plate
TARGET = 0.64        # the face's centre, as a fraction of the width from the side away from the type
BAR = 20             # a row whose 99th percentile is darker than this is letterbox


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def bars(img):
    """The rows of letterbox at the top and bottom, or (0, 0)."""
    a = np.asarray(img.convert("L"), dtype=np.float32)
    lit = np.percentile(a, 99, axis=1) > BAR
    top = int(np.argmax(lit))
    bottom = int(np.argmax(lit[::-1]))
    return top, bottom


def debar_crop(img):
    top, bottom = bars(img)
    if top + bottom < 0.01 * img.height:
        return None
    pad = round(0.004 * img.height)  # the bars' soft edge
    h = img.height - top - bottom - 2 * pad
    w = round(h * img.width / img.height)
    return [(img.width - w) // 2, top + pad, w, h]


def recolour(img, hue=COBALT_HUE, lift=1.0):
    """Move saturated teals and blues to `hue`, raise their saturation a little and their value by `lift`."""
    rgb = np.asarray(img.convert("RGB"), dtype=np.float32) / 255
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)  # H in degrees, S and V in 0..1 for float input
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    w = smoothstep(160, 175, h) * (1 - smoothstep(245, 260, h)) * smoothstep(0.25, 0.4, s)
    hsv[..., 0] = h + w * (hue - h)
    hsv[..., 1] = s + w * np.clip(0.8 - s, 0, None) * 0.5
    hsv[..., 2] = np.clip(v * (1 + w * (lift - 1)), 0, 1)
    out = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    return Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8))


def inpaint(img, boxes, thr=28.0, seed=0):
    a = np.asarray(img.convert("RGB")).copy()
    H, W = a.shape[:2]
    mask = np.zeros((H, W), np.uint8)
    for box in boxes:
        x0, y0, x1, y1 = box[:4]
        sign = box[4] if len(box) > 4 else 0  # -1: only what's darker than the box's border, +1: only what's lighter
        cut = box[5] if len(box) > 5 else thr  # how far from the border's colour a pixel must be, 0..255
        x0, x1, y0, y1 = int(x0 * W), int(x1 * W), int(y0 * H), int(y1 * H)
        region = a[y0:y1, x0:x1].astype(np.float32)
        border = np.concatenate([region[0], region[-1], region[:, 0], region[:, -1]])
        med = np.median(border, axis=0)
        far = np.linalg.norm(region - med, axis=2) > cut
        lum = region @ [0.299, 0.587, 0.114] - med @ [0.299, 0.587, 0.114]
        if sign < 0:
            far &= lum <= 10
        elif sign > 0:
            far &= lum >= -10
        mask[y0:y1, x0:x1] |= far.astype(np.uint8)
    k = max(3, round(0.004 * W))
    mask = cv2.dilate(mask, np.ones((k, k), np.uint8))
    out = cv2.inpaint(a, mask, max(3, round(0.003 * W)), cv2.INPAINT_TELEA)
    # grain again, as strong as the plate's own around the filled pixels
    ring = cv2.dilate(mask, np.ones((4 * k, 4 * k), np.uint8)) & ~mask.astype(bool)
    grain = a.astype(np.float32) - cv2.GaussianBlur(a, (0, 0), 2).astype(np.float32)
    std = grain[ring.astype(bool)].std(axis=0) if ring.any() else np.zeros(3)
    noise = np.random.default_rng(seed).normal(0, 1, a.shape) * std
    filled = mask.astype(bool)
    res = out.astype(np.float32)
    res[filled] += noise[filled]
    return Image.fromarray(np.clip(res + 0.5, 0, 255).astype(np.uint8)), int(filled.sum())


def flatfill(img, box, line, cut=14.0):
    """Paint out whatever stands on a flat-coloured floor inside `box`, down to a straight edge (`line`, two points
    as fractions). A smooth colour model of the floor above the line, fitted robustly so figures and their shadows
    fall out of it, finds what to paint out; the fill takes its tone from the clean floor around it, never from past
    the edge, and its grain from untouched floor nearby. Pixels
    within a few of the line, and all below it, are left alone, so the edge stays sharp."""
    a = np.asarray(img.convert("RGB"), dtype=np.float32)
    H, W = a.shape[:2]
    x0, y0, x1, y1 = int(box[0] * W), int(box[1] * H), int(box[2] * W), int(box[3] * H)
    xa, ya, xb, yb = line[0] * W, line[1] * H, line[2] * W, line[3] * H
    Y, X = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    floor = Y < ya + (X - xa) * (yb - ya) / (xb - xa) - 4
    u, v = (X - x0) / max(1, x1 - x0), (Y - y0) / max(1, y1 - y0)
    basis = np.stack([np.ones_like(u), u, v, u * u, u * v, v * v], axis=-1)
    region = a[y0:y1, x0:x1]
    keep = floor.copy()
    for _ in range(5):  # trimmed least squares: refit on the 60 % of the floor nearest the model
        coef, *_ = np.linalg.lstsq(basis[keep], region[keep], rcond=None)
        model = basis @ coef
        dist = np.linalg.norm(region - model, axis=-1)
        keep = floor & (dist <= np.percentile(dist[floor], 60))
    mask = floor & (dist > max(cut, 4 * np.median(dist[keep])))  # clear of the floor's own grain
    k = max(3, round(0.004 * W))
    mask = cv2.dilate(mask.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool) & floor
    # the tone: the clean floor's local average (a normalised Gaussian), which ignores the hole and the far side
    # of the edge alike
    wgt = (floor & ~mask).astype(np.float32)
    sigma = max(4.0, 0.012 * W)
    num = cv2.GaussianBlur(region * wgt[..., None], (0, 0), sigma)
    den = cv2.GaussianBlur(wgt, (0, 0), sigma)[..., None]
    tone = np.where(den > 1e-3, num / np.maximum(den, 1e-3), model)
    # the grain: the fine detail of untouched floor, taken from the nearest shift that lands on some
    detail = region - cv2.GaussianBlur(region, (0, 0), 1.5)
    grain = np.zeros_like(region)
    todo = mask.copy()
    step = max(8, round(0.06 * W))
    for dy, dx in [(0, -step), (0, step), (-step, 0), (0, -2 * step), (0, 2 * step), (-2 * step, 0), (-step, -step), (-step, step)]:
        ys, xs = np.nonzero(todo)
        sy, sx = ys + dy, xs + dx
        ok = (sy >= 0) & (sy < region.shape[0]) & (sx >= 0) & (sx < region.shape[1])
        ok[ok] &= floor[sy[ok], sx[ok]] & ~mask[sy[ok], sx[ok]]
        grain[ys[ok], xs[ok]] = detail[sy[ok], sx[ok]]
        todo[ys[ok], xs[ok]] = False
    out = a.copy()
    out[y0:y1, x0:x1][mask] = (tone + grain)[mask]
    return Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8)), int(mask.sum())


def sky(img, line, top=(204, 208, 212), low=(226, 228, 230)):
    """Lift everything above a horizon (`line`, a fraction of the height) to a pale studio sky: a soft vertical
    gradient from `top` to `low`, with the plate's own grain kept. Warm pixels (a terracotta prop standing on the
    horizon) are left alone."""
    a = np.asarray(img.convert("RGB"), dtype=np.float32)
    H, W = a.shape[:2]
    yh = int(round(line * H))
    # how warm a pixel is: 0 for the sky, 1 for the prop, in between on the prop's anti-aliased edge, so its edge
    # blends into the new sky instead of keeping a rim of the old one
    warm = np.clip((a[..., 0] - a[..., 2] - 20) / 30, 0, 1)
    rows = np.arange(H, dtype=np.float32)[:, None]
    k = np.clip((yh + 3 - rows) / 6, 0, 1)  # 1 above the horizon, feathered over 6 px at it
    k = np.repeat(k, W, axis=1) * (1 - warm)
    t = np.clip(rows / max(1, yh), 0, 1)[..., None]
    grad = np.array(top, np.float32) * (1 - t) + np.array(low, np.float32) * t
    grain = a - cv2.GaussianBlur(a, (0, 0), 1.5)
    out = a * (1 - k[..., None]) + (grad + grain) * k[..., None]
    return Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8))


def faces(img, most=12):
    """Every face MediaPipe's landmarker finds, as pixel boxes [x0, y0, x1, y1], largest first."""
    os.environ.setdefault("GLOG_minloglevel", "2")  # MediaPipe's own logging, several lines per call
    import mediapipe as mp
    from mediapipe.tasks import python as mpp
    from mediapipe.tasks.python import vision
    if not MODEL.exists():
        raise SystemExit(f"Download the face landmarker model to {MODEL} (see tools/lipcheck.py).")
    rgb = np.ascontiguousarray(np.asarray(img.convert("RGB")))
    opts = vision.FaceLandmarkerOptions(base_options=mpp.BaseOptions(model_asset_path=str(MODEL)),
                                        running_mode=vision.RunningMode.IMAGE, num_faces=most)
    with vision.FaceLandmarker.create_from_options(opts) as lm:
        r = lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
    out = []
    for f in r.face_landmarks:
        p = np.array([(q.x * img.width, q.y * img.height) for q in f])
        out.append([float(p[:, 0].min()), float(p[:, 1].min()), float(p[:, 0].max()), float(p[:, 1].max())])
    return sorted(out, key=lambda b: -(b[2] - b[0]) * (b[3] - b[1]))


def place_crop(img, side):
    """The crop [x, y, w, h] that puts her face's centre TARGET of the width from the side away from the type, or
    None if it's already there. The crop keeps the image's aspect and the face's height in the frame."""
    found = faces(img, most=1)
    if not found:
        raise SystemExit("no face found to place")
    x0, y0, x1, y1 = found[0]
    W, H = img.size
    fx, fy = (x0 + x1) / 2, (y0 + y1) / 2
    t = TARGET if side == "right" else 1 - TARGET
    s = min(1.0, fx / (t * W), (W - fx) / ((1 - t) * W))
    if s > 0.97:
        return None
    s = max(s, MIN_SCALE)
    w, h = round(s * W), round(s * H)
    cx = int(min(max(fx - t * w, 0), W - w))
    cy = int(min(max(fy * (1 - s), 0), H - h))
    return [cx, cy, w, h]


def crop(img, box):
    x, y, w, h = box
    return img.crop((x, y, x + w, y + h))


def apply(src, fixes):
    """The frame from the source image and its recorded fixes, in order."""
    img = Image.open(src).convert("RGB")
    for f in fixes:
        if f["op"] in ("debar", "place"):
            img = crop(img, f["crop"])
        elif f["op"] == "recolour":
            img = recolour(img, f.get("hue", COBALT_HUE), f.get("lift", 1.0))
        elif f["op"] == "inpaint":
            img, _ = inpaint(img, f["boxes"])
        elif f["op"] == "flatfill":
            img, _ = flatfill(img, f["box"], f["line"])
        elif f["op"] == "sky":
            img = sky(img, f["line"])
    return img


def plan(src, debar=False, recolour_=False, lift=1.0, boxes=(), side=None, flat=None, line=None, sky_line=None):
    """Work out each fix on the source (the crops need the image as the fixes before them left it) and return the
    list to record, with notes for the log."""
    img = Image.open(src).convert("RGB")
    fixes, notes = [], []
    if debar:
        box = debar_crop(img)
        if box:
            fixes.append({"op": "debar", "crop": box})
            img = crop(img, box)
            notes.append(f"bars cropped off: {box[2]}x{box[3]}")
        else:
            notes.append("no bars found")
    if recolour_:
        fixes.append({"op": "recolour", "hue": COBALT_HUE, "lift": lift})
        img = recolour(img, COBALT_HUE, lift)
        notes.append(f"blues to cobalt, value x{lift}")
    if boxes:
        fixes.append({"op": "inpaint", "boxes": [list(b) for b in boxes]})
        img, n = inpaint(img, boxes)
        notes.append(f"painted out {n:,} px in {len(boxes)} box(es)")
    if sky_line is not None:
        fixes.append({"op": "sky", "line": sky_line})
        img = sky(img, sky_line)
        notes.append(f"sky above {sky_line:.3f} lifted to pale grey")
    if flat:
        fixes.append({"op": "flatfill", "box": list(flat), "line": list(line)})
        img, n = flatfill(img, flat, line)
        notes.append(f"filled {n:,} px of flat floor")
    if side:
        box = place_crop(img, side)
        if box:
            fixes.append({"op": "place", "side": side, "crop": box})
            notes.append(f"placed {side} of centre: {box[2]}x{box[3]} ({box[2] / img.width:.0%})")
        else:
            notes.append(f"already {side} of centre")
    return fixes, notes
