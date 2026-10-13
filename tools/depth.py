"""Depth maps for the 2.5D plates (BRIEF.md step 4), with Depth Anything V2 Large through transformers on the GPU.

Every plate a 2.5D shot uses gets production/assets/depth/<plate>.png: 8-bit grey at the plate's own size, near
white and far black, which the compositor's print pass reads (scripts/scan-media.mjs finds it). The model's
relative depth is stretched between its 1st and 99th percentiles, grown a few pixels at near edges so a
foreground's rim moves with it rather than with the background, and softened, so parallax bends the plate
instead of tearing it.

Usage, with the project's .venv (the model, about 1.3 GB, downloads to the Hugging Face cache on first use):
  .venv/Scripts/python tools/depth.py            # every 2.5D plate whose depth map is missing or older than its plate
  .venv/Scripts/python tools/depth.py --all      # all of them again
  .venv/Scripts/python tools/depth.py A_desk_ws  # these plates
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "production" / "storyboard" / "shots.json"
FRAMES = ROOT / "production" / "assets" / "frames"
DEPTH = ROOT / "production" / "assets" / "depth"
MODEL = "depth-anything/Depth-Anything-V2-Large-hf"


def plates_2p5d():
    shots = json.loads(SHOTS.read_text(encoding="utf-8"))["shots"]
    return sorted({s["plate"] for s in shots if s["motion_tier"] == "2.5d" and s["plate"]})


def frame_of(plate):
    for ext in (".png", ".jpg"):
        f = FRAMES / f"{plate}{ext}"
        if f.exists():
            return f
    return None


def to_map(pred, size):
    """The model's relative depth (bigger is nearer) as the compositor's 8-bit map at `size` (w, h)."""
    d = cv2.resize(pred.astype(np.float32), size, interpolation=cv2.INTER_CUBIC)
    lo, hi = np.percentile(d, [1, 99])
    d = np.clip((d - lo) / max(hi - lo, 1e-6), 0, 1)
    k = max(3, round(0.002 * size[0]) | 1)
    d = cv2.dilate(d, np.ones((k, k), np.uint8))  # near edges win
    d = cv2.GaussianBlur(d, (0, 0), max(1.0, 0.0015 * size[0]))
    return Image.fromarray((d * 255 + 0.5).astype(np.uint8), mode="L")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("plates", nargs="*")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    todo = []
    for p in args.plates or plates_2p5d():
        f = frame_of(p)
        if not f:
            print(f"{p}: no plate yet")
            continue
        dest = DEPTH / f"{p}.png"
        if args.all or args.plates or not dest.exists() or dest.stat().st_mtime < f.stat().st_mtime:
            todo.append((p, f, dest))
    if not todo:
        print("every depth map is up to date")
        return
    import torch
    from transformers import AutoImageProcessor, AutoModelForDepthEstimation
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    proc = AutoImageProcessor.from_pretrained(MODEL)
    model = AutoModelForDepthEstimation.from_pretrained(MODEL).to(dev).eval()
    DEPTH.mkdir(parents=True, exist_ok=True)
    for p, f, dest in todo:
        img = Image.open(f).convert("RGB")
        with torch.no_grad():
            out = model(**proc(images=img, return_tensors="pt").to(dev))
        to_map(out.predicted_depth[0].float().cpu().numpy(), img.size).save(dest)
        print(f"{p}: {dest.relative_to(ROOT).as_posix()} ({img.width}x{img.height})")


if __name__ == "__main__":
    main()
