"""Contact sheets: tile frames into one labelled image (BRIEF.md steps 3 and 7).

For the compositor's QA sheets, production/comp/scripts/sheet.mjs renders the frames and writes a
labels.json next to them ({"f00123.jpg": "s014 · 0:36.04 · first word 'You'", ...}); this tiles them in
that order. It works on any folder of images (Midjourney batches too), labelling each with its file
name when there's no labels.json.

Usage, with the project's .venv:
  .venv/Scripts/python tools/contact_sheet.py DIR --out SHEET.jpg [--cols 4] [--width 480] [--title TEXT]
"""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

LABEL_BG = (12, 12, 14)
LABEL_FG = (216, 228, 220)
ACCENT = (201, 100, 66)
GAP = 6


def font(size):
    for name in ("consola.ttf", "arialbd.ttf", "arial.ttf", "DejaVuSansMono.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def sheet(images, labels, dest, cols=4, width=480, title=None):
    if not images:
        raise SystemExit("no images to tile")
    with Image.open(images[0]) as im:
        aspect = im.height / im.width
    tw, th = width, round(width * aspect)
    lab_h = 22
    rows = (len(images) + cols - 1) // cols
    head = 40 if title else 0
    out = Image.new("RGB", (GAP + cols * (tw + GAP), head + GAP + rows * (th + lab_h + GAP)), LABEL_BG)
    draw = ImageDraw.Draw(out)
    f = font(14)
    if title:
        draw.text((GAP * 2, 10), title, fill=LABEL_FG, font=font(20))
    for i, path in enumerate(images):
        r, c = divmod(i, cols)
        x = GAP + c * (tw + GAP)
        y = head + GAP + r * (th + lab_h + GAP)
        with Image.open(path) as im:
            out.paste(im.convert("RGB").resize((tw, th), Image.LANCZOS), (x, y + lab_h))
        text = labels.get(Path(path).name, Path(path).stem)
        draw.text((x + 4, y + 3), text[:80], fill=ACCENT if "!" in text else LABEL_FG, font=f)
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(dest, quality=88)
    return dest


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("dir")
    p.add_argument("--out", required=True)
    p.add_argument("--cols", type=int, default=4)
    p.add_argument("--width", type=int, default=480)
    p.add_argument("--title")
    args = p.parse_args()
    d = Path(args.dir)
    labels_file = d / "labels.json"
    labels = json.loads(labels_file.read_text(encoding="utf-8")) if labels_file.exists() else {}
    order = list(labels) if labels else sorted(x.name for x in d.iterdir() if x.suffix.lower() in (".jpg", ".jpeg", ".png"))
    images = [d / name for name in order if (d / name).exists()]
    print(sheet(images, labels, args.out, args.cols, args.width, args.title))


if __name__ == "__main__":
    main()
