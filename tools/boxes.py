"""Her face and body boxes on every plate she's in (BRIEF.md step 4), for the tracking graphics, the type zones and
step 5's SAM 2 prompts.

For each plate whose prompt has her or the Instances in it, production/assets/boxes/<plate>.json holds, as fractions
of the plate's width and height:
  faces   every face MediaPipe's face landmarker finds, largest first, each with its box; the largest also keeps
          its 478 landmarks (the irises are 468 and 473)
  bodies  every woman Grounding DINO finds, best first, each with its box and score ("a woman." on a plate of her,
          "a person." at a lower score on one of the Instances)
  agent   which body is hers: the one holding the largest face, or the largest body, or, for the Instances, the
          biggest near the centre, where the board puts her
Wide plates whose faces are too small for the landmarker have bodies only.

Usage, with the project's .venv (Grounding DINO, about 0.9 GB, downloads to the Hugging Face cache on first use):
  .venv/Scripts/python tools/boxes.py              # every plate with her whose boxes are missing or older than it
  .venv/Scripts/python tools/boxes.py --all
  .venv/Scripts/python tools/boxes.py B_row_ws     # these plates
"""
import argparse
import importlib.util
import json
import math
from pathlib import Path

from PIL import Image

import plate_fix

ROOT = Path(__file__).resolve().parent.parent
BOARD = ROOT / "production" / "storyboard" / "board.py"
FRAMES = ROOT / "production" / "assets" / "frames"
BOXES = ROOT / "production" / "assets" / "boxes"
DINO = "IDEA-Research/grounding-dino-base"
# what to ask Grounding DINO for, and at what box score: "a woman." finds her alone, but in a crowd of the
# Instances it finds a few of dozens, where "a person." at a lower score finds most (session 4's test, 30 Sep)
ASK = {"agent": ("a woman.", 0.35), "instances": ("a person.", 0.25)}
TEXT_T = 0.2
SAME = 0.6  # boxes overlapping more than this (intersection over union) are one woman


def plates_with_her():
    spec = importlib.util.spec_from_file_location("board", BOARD)
    board = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(board)
    return {p: d["who"] for p, d in board.PLATES.items() if d.get("who") in ("agent", "instances")}


def frac(box, w, h):
    x0, y0, x1, y1 = box
    return [round(max(0.0, x0 / w), 5), round(max(0.0, y0 / h), 5), round(min(1.0, x1 / w), 5), round(min(1.0, y1 / h), 5)]


def faces_of(img):
    import mediapipe as mp
    from mediapipe.tasks import python as mpp
    from mediapipe.tasks.python import vision
    opts = vision.FaceLandmarkerOptions(base_options=mpp.BaseOptions(model_asset_path=str(plate_fix.MODEL)),
                                        running_mode=vision.RunningMode.IMAGE, num_faces=40)
    rgb = __import__("numpy").ascontiguousarray(__import__("numpy").asarray(img))
    with vision.FaceLandmarker.create_from_options(opts) as lm:
        r = lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
    out = []
    for f in r.face_landmarks:
        xs, ys = [q.x for q in f], [q.y for q in f]
        out.append({"box": [round(min(xs), 5), round(min(ys), 5), round(max(xs), 5), round(max(ys), 5)],
                    "landmarks": [[round(q.x, 5), round(q.y, 5)] for q in f]})
    out.sort(key=lambda f: -(f["box"][2] - f["box"][0]) * (f["box"][3] - f["box"][1]))
    for f in out[1:]:
        del f["landmarks"]
    return out


def bodies_of(img, proc, model, dev, who):
    import torch
    from torchvision.ops import nms
    text, box_t = ASK.get(who, ASK["agent"])
    inputs = proc(images=img, text=text, return_tensors="pt").to(dev)
    with torch.no_grad():
        out = model(**inputs)
    res = proc.post_process_grounded_object_detection(out, inputs.input_ids, threshold=box_t, text_threshold=TEXT_T,
                                                      target_sizes=[img.size[::-1]])[0]
    keep = nms(res["boxes"].float(), res["scores"].float(), SAME).tolist() if len(res["boxes"]) else []
    w, h = img.size
    found = [{"box": frac(res["boxes"][i].tolist(), w, h), "score": round(float(res["scores"][i]), 3)} for i in keep]
    # drop a box that holds most of the frame and several others: the group, not a woman
    area = lambda b: (b[2] - b[0]) * (b[3] - b[1])
    inside = lambda a, b: a[0] >= b[0] - 0.01 and a[1] >= b[1] - 0.01 and a[2] <= b[2] + 0.01 and a[3] <= b[3] + 0.01
    found = [f for f in found if not (area(f["box"]) > 0.3 and sum(inside(g["box"], f["box"]) for g in found if g is not f) >= 2)]
    return sorted(found, key=lambda f: -f["score"])


def agent_of(who, faces, bodies):
    if not bodies:
        return None
    if who == "instances":  # the board puts her in the middle and nearest: big and central wins
        def weight(b):
            d2 = ((b[0] + b[2]) / 2 - 0.5) ** 2 + ((b[1] + b[3]) / 2 - 0.5) ** 2
            return (b[2] - b[0]) * (b[3] - b[1]) * math.exp(-d2 / (2 * 0.15 ** 2))
        return max(range(len(bodies)), key=lambda i: weight(bodies[i]["box"]))
    if faces:
        fx = (faces[0]["box"][0] + faces[0]["box"][2]) / 2
        fy = (faces[0]["box"][1] + faces[0]["box"][3]) / 2
        holding = [i for i, b in enumerate(bodies) if b["box"][0] <= fx <= b["box"][2] and b["box"][1] <= fy <= b["box"][3]]
        if holding:
            return holding[0]
    return max(range(len(bodies)), key=lambda i: (bodies[i]["box"][2] - bodies[i]["box"][0]) * (bodies[i]["box"][3] - bodies[i]["box"][1]))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("plates", nargs="*")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    who = plates_with_her()
    todo = []
    for p in args.plates or sorted(who):
        f = FRAMES / f"{p}.png"
        if not f.exists():
            print(f"{p}: no plate yet")
            continue
        dest = BOXES / f"{p}.json"
        if args.all or args.plates or not dest.exists() or dest.stat().st_mtime < f.stat().st_mtime:
            todo.append((p, f, dest))
    if not todo:
        print("every plate's boxes are up to date")
        return
    import os
    os.environ.setdefault("GLOG_minloglevel", "2")
    import torch
    from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    proc = AutoProcessor.from_pretrained(DINO)
    model = AutoModelForZeroShotObjectDetection.from_pretrained(DINO).to(dev).eval()
    BOXES.mkdir(parents=True, exist_ok=True)
    for p, f, dest in todo:
        img = Image.open(f).convert("RGB")
        faces, bodies = faces_of(img), bodies_of(img, proc, model, dev, who.get(p))
        rec = {"plate": p, "size": list(img.size), "who": who.get(p), "faces": faces, "bodies": bodies,
               "agent": agent_of(who.get(p), faces, bodies), "models": {"faces": "MediaPipe face_landmarker", "bodies": DINO,
                                                                       "text": ASK.get(who.get(p), ASK["agent"])[0]}}
        dest.write_text(json.dumps(rec, separators=(",", ":")) + "\n", encoding="utf-8")
        print(f"{p}: {len(faces)} face(s), {len(bodies)} body box(es)")


if __name__ == "__main__":
    main()
