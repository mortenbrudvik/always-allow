"""The dancer mattes (BRIEF.md step 5): each dancer clip cut out with SAM 2, for the clone formations the compositor
builds by duplicating her in code, so every clone moves in perfect sync.

For every dancer clip with a select, production/clips/mattes/<clip>.webm is the select with her alone kept, as VP9
with an alpha channel (what `DancerFootage` in production/comp reads). SAM 2.1 (hiera-large, through transformers)
is prompted by her body box on the first, middle and last frames (Grounding DINO's "a woman."), and follows her
through the clip; the mask is softened by a pixel at its edge. production/clips/mattes/<clip>.json says where her
figure stands in the frame (head, feet and centre line, as fractions), for scaling and planting each copy, and a
sheet of frames over a checkerboard goes to production/clips/mattes/<clip>_check.jpg to look at, and <clip>_still.png
is her middle frame cut out, small, for the flash-past mosaic.

Usage, with the project's .venv (the model, about 0.9 GB, downloads to the Hugging Face cache on first use):
  .venv/Scripts/python tools/matte.py            # every dancer select without a matte, or newer than its matte
  .venv/Scripts/python tools/matte.py D1         # these clips
"""
import argparse
import json
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from track import DINO, frames_of

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "production" / "storyboard" / "shots.json"
SELECTS = ROOT / "production" / "clips" / "selects"
MATTES = ROOT / "production" / "clips" / "mattes"
SAM2 = "facebook/sam2.1-hiera-large"


def body_box(img, proc, model, dev):
    import torch
    inputs = proc(images=img, text="a woman.", return_tensors="pt").to(dev)
    with torch.no_grad():
        out = model(**inputs)
    r = proc.post_process_grounded_object_detection(out, inputs.input_ids, threshold=0.3, text_threshold=0.2,
                                                    target_sizes=[img.size[::-1]])[0]
    if not len(r["boxes"]):
        return None
    return [round(v, 1) for v in r["boxes"][int(r["scores"].argmax())].tolist()]


def masks_of(frames, prompts, dev):
    """SAM 2's mask per frame (0..1) for one object, prompted with a box on each of `prompts` {frame: box}."""
    import torch
    from transformers import Sam2VideoModel, Sam2VideoProcessor
    model = Sam2VideoModel.from_pretrained(SAM2).to(dev).eval()
    proc = Sam2VideoProcessor.from_pretrained(SAM2)
    session = proc.init_video_session(video=[Image.fromarray(f) for f in frames], inference_device=dev,
                                      dtype=torch.float32)
    out = {}
    with torch.no_grad():
        for f, box in sorted(prompts.items()):  # each prompt is run once, which also sets where propagation starts
            proc.add_inputs_to_inference_session(inference_session=session, frame_idx=f, obj_ids=1, input_boxes=[[box]])
            model(inference_session=session, frame_idx=f)
        for o in model.propagate_in_video_iterator(session, start_frame_idx=min(prompts)):
            m = proc.post_process_masks([o.pred_masks], original_sizes=[[session.video_height, session.video_width]],
                                        binarize=False)[0]
            out[o.frame_idx] = torch.sigmoid(m[0, 0]).float().cpu().numpy()
    return [out.get(i, np.zeros(frames.shape[1:3], np.float32)) for i in range(len(frames))]


def figure_of(masks):
    """Where her figure stands in the matte's frame, as fractions of it, for the formations to scale and plant each
    copy: the top of her head at her tallest, her feet and her centre line (medians over the clip, so a bow or a
    raised arm doesn't move them)."""
    tops, feet, cxs = [], [], []
    for m in masks:
        ys, xs = np.nonzero(m > 0.5)
        if len(ys):
            tops.append(ys.min() / m.shape[0])
            feet.append(ys.max() / m.shape[0])
            cxs.append((xs.min() + xs.max()) / 2 / m.shape[1])
    if not tops:
        return None
    return {"top": round(float(np.percentile(tops, 5)), 4), "feet": round(float(np.median(feet)), 4),
            "cx": round(float(np.median(cxs)), 4)}


def still_of(frames, masks, dest, width=640):
    """Her middle frame cut out, small, with alpha: for the flash-past's mosaic tiles, which copy it into the
    formation instead of playing the matte."""
    i = len(frames) // 2
    a = cv2.GaussianBlur((masks[i] > 0.5).astype(np.float32), (0, 0), 0.8)
    im = Image.fromarray(np.dstack([frames[i], (a * 255 + 0.5).astype(np.uint8)]), "RGBA")
    im.resize((width, round(width * im.height / im.width)), Image.LANCZOS).save(dest)


def write_webm(frames, masks, dest):
    h, w = frames.shape[1:3]
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{w}x{h}", "-r", "24",
                            "-i", "-", "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "18",
                            "-auto-alt-ref", "0", "-row-mt", "1", str(dest)], stdin=subprocess.PIPE)
    for f, m in zip(frames, masks):
        a = (m > 0.5).astype(np.float32)
        a = cv2.GaussianBlur(a, (0, 0), 0.8)  # a soft edge, a pixel wide
        enc.stdin.write(np.dstack([f, (a * 255 + 0.5).astype(np.uint8)]).tobytes())
    enc.stdin.close()
    if enc.wait():
        raise SystemExit(f"ffmpeg failed writing {dest}")


def check_sheet(frames, masks, dest, n=6):
    h, w = frames.shape[1:3]
    tile = (w // 3, h // 3)
    yy, xx = np.mgrid[0:h, 0:w]
    board = np.where(((yy // 24 + xx // 24) % 2)[..., None] == 0, 200, 120).astype(np.float32)
    out = Image.new("RGB", (n * tile[0], tile[1]))
    for k, i in enumerate(np.linspace(0, len(frames) - 1, n).astype(int)):
        a = (masks[i] > 0.5).astype(np.float32)[..., None]
        comp = frames[i] * a + board * (1 - a)
        out.paste(Image.fromarray(comp.astype(np.uint8)).resize(tile), (k * tile[0], 0))
    out.save(dest, quality=85)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("clips", nargs="*")
    args = ap.parse_args()
    board = json.loads(SHOTS.read_text(encoding="utf-8"))
    dancers = [c["clip"] for c in board["clips"] if c["kind"] == "dancer"]
    todo = []
    for c in args.clips or dancers:
        sel, dest = SELECTS / f"{c}.mp4", MATTES / f"{c}.webm"
        if sel.exists() and (args.clips or not dest.exists() or dest.stat().st_mtime < sel.stat().st_mtime):
            todo.append((c, sel, dest))
    if not todo:
        print("every dancer select has its matte")
        return
    import torch
    from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    dproc = AutoProcessor.from_pretrained(DINO)
    dino = AutoModelForZeroShotObjectDetection.from_pretrained(DINO).to(dev).eval()
    MATTES.mkdir(parents=True, exist_ok=True)
    for c, sel, dest in todo:
        frames, _ = frames_of(sel)
        prompts = {}
        for i in (0, len(frames) // 2, len(frames) - 1):
            box = body_box(Image.fromarray(frames[i]), dproc, dino, dev)
            if box:
                prompts[i] = box
        if not prompts:
            print(f"{c}: no woman found to cut out")
            continue
        masks = masks_of(frames, prompts, dev)
        write_webm(frames, masks, dest)
        check_sheet(frames, masks, MATTES / f"{c}_check.jpg")
        fig = figure_of(masks)
        dest.with_suffix(".json").write_text(json.dumps({"clip": c, "figure": fig}, indent=1) + "\n", encoding="utf-8")
        still_of(frames, masks, MATTES / f"{c}_still.png")
        cover = np.mean([float((m > 0.5).mean()) for m in masks])
        print(f"{c}: {dest.relative_to(ROOT).as_posix()}, prompted on frames {sorted(prompts)}, "
              f"she covers {cover:.1%} of the frame on average")


if __name__ == "__main__":
    main()
