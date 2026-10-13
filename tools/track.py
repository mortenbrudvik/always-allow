"""Her tracking in every clip she's in (BRIEF.md step 5): face landmarks per frame and body boxes, saved next to the
clip for the graphics layer.

For every select in production/clips/selects/ whose shots have her on screen, production/clips/tracking/<clip>.json
holds, in the animation guide's format (production/comp/ANIMATION_GUIDE.md, "Footage, as it arrives"):
  {"fps": 24, "width": 1920, "height": 1080, "frames": [{"f": 0, "face": {"x", "y", "w", "h"} | null,
   "landmarks": [[x, y], ...], "body": {"x", "y", "w", "h"} | null}, ...]}
in clip frames and 1920x1080 frame pixels (the comp shows a clip full-frame). The face and its twelve landmarks
are MediaPipe's face landmarker's, in the order the tracking layer draws them (eye corners left to right, the
pupils, the brows, the nose tip, the lip corners and the lower lip's centre); the body is Grounding DINO's
"a woman.", found every other frame and interpolated between. A frame without a face has none, never a guess.

Usage, with the project's .venv:
  .venv/Scripts/python tools/track.py              # every select without tracking, or newer than its tracking
  .venv/Scripts/python tools/track.py C12 D1       # these clips
"""
import argparse
import json
import os
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

import plate_fix

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "production" / "storyboard" / "shots.json"
SELECTS = ROOT / "production" / "clips" / "selects"
TRACKING = ROOT / "production" / "clips" / "tracking"
FRAME = (1920, 1080)
KEY = [33, 133, 362, 263, 468, 473, 105, 334, 1, 61, 291, 14]  # the tracking layer's twelve, in its order
DINO = "IDEA-Research/grounding-dino-base"
EVERY = 2  # body boxes on every other frame, interpolated between


def frames_of(video):
    """The select's frames as RGB arrays, and its size."""
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                            "-of", "csv=p=0", str(video)], capture_output=True, text=True, check=True)
    w, h = (int(v) for v in probe.stdout.strip().split(","))
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3), (w, h)


def faces_of(frames, size):
    os.environ.setdefault("GLOG_minloglevel", "2")
    import mediapipe as mp
    from mediapipe.tasks import python as mpp
    from mediapipe.tasks.python import vision
    opts = vision.FaceLandmarkerOptions(base_options=mpp.BaseOptions(model_asset_path=str(plate_fix.MODEL)),
                                        running_mode=vision.RunningMode.VIDEO, num_faces=1)
    sx, sy = FRAME[0] / size[0], FRAME[1] / size[1]
    out = []
    with vision.FaceLandmarker.create_from_options(opts) as lm:
        for i, f in enumerate(frames):
            r = lm.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(f)),
                                    int(round(i * 1000 / 24)))
            if not r.face_landmarks:
                out.append((None, []))
                continue
            p = np.array([(q.x * size[0] * sx, q.y * size[1] * sy) for q in r.face_landmarks[0]])
            x0, y0 = p.min(axis=0)
            x1, y1 = p.max(axis=0)
            box = {"x": round(float(x0), 1), "y": round(float(y0), 1), "w": round(float(x1 - x0), 1), "h": round(float(y1 - y0), 1)}
            out.append((box, [[round(float(p[k, 0]), 1), round(float(p[k, 1]), 1)] for k in KEY]))
    return out


def bodies_of(frames, size, proc, model, dev):
    import torch
    sx, sy = FRAME[0] / size[0], FRAME[1] / size[1]
    found = {}
    for i in list(range(0, len(frames), EVERY)) + [len(frames) - 1]:
        img = Image.fromarray(frames[i])
        inputs = proc(images=img, text="a woman.", return_tensors="pt").to(dev)
        with torch.no_grad():
            out = model(**inputs)
        r = proc.post_process_grounded_object_detection(out, inputs.input_ids, threshold=0.3, text_threshold=0.2,
                                                        target_sizes=[img.size[::-1]])[0]
        if len(r["boxes"]):
            b = r["boxes"][int(r["scores"].argmax())].tolist()
            found[i] = [b[0] * sx, b[1] * sy, b[2] * sx, b[3] * sy]
    keys = sorted(found)
    out = []
    for i in range(len(frames)):
        before = [k for k in keys if k <= i]
        after = [k for k in keys if k >= i]
        if not before or not after:
            out.append(None)
            continue
        a, b = before[-1], after[0]
        t = 0 if a == b else (i - a) / (b - a)
        x0, y0, x1, y1 = [(1 - t) * u + t * v for u, v in zip(found[a], found[b])]
        out.append({"x": round(x0, 1), "y": round(y0, 1), "w": round(x1 - x0, 1), "h": round(y1 - y0, 1)})
    return out


def clips_with_her():
    board = json.loads(SHOTS.read_text(encoding="utf-8"))
    on = {s["id"] for s in board["shots"] if s.get("agent_on_screen")}
    return [c["clip"] for c in board["clips"] if on & set(c["shots"])]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("clips", nargs="*")
    args = ap.parse_args()
    todo = []
    for c in args.clips or clips_with_her():
        sel = SELECTS / f"{c}.mp4"
        dest = TRACKING / f"{c}.json"
        if not sel.exists():
            continue
        if args.clips or not dest.exists() or dest.stat().st_mtime < sel.stat().st_mtime:
            todo.append((c, sel, dest))
    if not todo:
        print("every select with her has its tracking")
        return
    import torch
    from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    proc = AutoProcessor.from_pretrained(DINO)
    model = AutoModelForZeroShotObjectDetection.from_pretrained(DINO).to(dev).eval()
    TRACKING.mkdir(parents=True, exist_ok=True)
    for c, sel, dest in todo:
        frames, size = frames_of(sel)
        faces, bodies = faces_of(frames, size), bodies_of(frames, size, proc, model, dev)
        rows = [{"f": i, "face": fb[0], "landmarks": fb[1], "body": b} for i, (fb, b) in enumerate(zip(faces, bodies))]
        dest.write_text(json.dumps({"fps": 24, "width": FRAME[0], "height": FRAME[1], "clip": c,
                                    "source": sel.relative_to(ROOT).as_posix(), "frames": rows},
                                   separators=(",", ":")) + "\n", encoding="utf-8")
        print(f"{c}: {len(rows)} frames, a face in {sum(r['face'] is not None for r in rows)}, "
              f"a body in {sum(r['body'] is not None for r in rows)}")


if __name__ == "__main__":
    main()
