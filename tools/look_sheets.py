"""Contact sheets for a Midjourney batch (BRIEF.md step 2), plain and through the print grade.

Reads production/storyboard/mj_manifest.csv, takes the rows whose `for` column matches --tag, and for
each style (the prompt ID's letter) writes one sheet with a row per prompt and a column per image,
each tile labelled with its prompt ID and index. Every image is also put through
tools/print_grade.py at 1280x720, as Seedance would see it; the graded files are kept at full size
next to the sheets, because a 5 px screen doesn't survive being shrunk into a thumbnail.

--styles limits the sheets to some style letters, and --ref heads every sheet with a row per
reference image, such as the one a batch is meant to match, named by prompt ID and index.

Usage, with the project's .venv:
  .venv/Scripts/python tools/look_sheets.py --tag "look test" --out production/style/moodboard
  .venv/Scripts/python tools/look_sheets.py --tag casting --styles R --ref t3.3 --out production/style/casting
"""
import argparse
import csv
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import print_grade

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "production/storyboard/mj_manifest.csv"
TILE = (640, 360)
GAP = 8
LABEL_BG = (12, 12, 14)


def font(size):
    for name in ("arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def sheet(rows, dest, title):
    """rows: [(prompt_id, [(index, path), ...]), ...] -> one PNG, a row per prompt."""
    cols = max(len(images) for _, images in rows)
    head = 56
    w = GAP + cols * (TILE[0] + GAP)
    h = head + GAP + len(rows) * (TILE[1] + GAP)
    out = Image.new("RGB", (w, h), LABEL_BG)
    draw = ImageDraw.Draw(out)
    draw.text((GAP * 2, 14), title, fill=(235, 235, 230), font=font(28))
    label = font(22)
    for r, (pid, images) in enumerate(rows):
        y = head + GAP + r * (TILE[1] + GAP)
        for c, (index, path) in enumerate(images):
            x = GAP + c * (TILE[0] + GAP)
            with Image.open(path) as im:
                out.paste(im.convert("RGB").resize(TILE, Image.LANCZOS), (x, y))
            tag = f"{pid} . {index}"
            box = draw.textbbox((0, 0), tag, font=label)
            draw.rectangle((x, y, x + box[2] + 16, y + box[3] + 12), fill=LABEL_BG)
            draw.text((x + 8, y + 5), tag, fill=(201, 100, 66), font=label)
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(dest, optimize=True)
    return dest


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--tag", default="look test", help="the manifest's `for` value to sheet")
    p.add_argument("--out", default="production/style/moodboard", help="folder for the sheets")
    p.add_argument("--styles", default="", help="only sheet these style letters, such as R (default: all)")
    p.add_argument("--ref", default="", help="images to head every sheet, as prompt ID and index: t3.3 or R3.3,t3.3")
    args = p.parse_args()

    out = ROOT / args.out
    wanted = [tuple(r.strip().rsplit(".", 1)) for r in args.ref.split(",") if r.strip()]
    styles = defaultdict(lambda: defaultdict(list))
    refs = {}
    with MANIFEST.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            image = (int(row["index"]), ROOT / row["file"])
            if row["for"] == args.tag:
                styles[row["prompt_id"][0]][row["prompt_id"]].append(image)
            if (row["prompt_id"], row["index"]) in wanted:
                refs[row["prompt_id"], row["index"]] = image
    missing = [".".join(r) for r in wanted if r not in refs]
    if missing:
        p.error(f"not in the manifest: {', '.join(missing)}")

    for style, prompts in sorted(styles.items()):
        if args.styles and style not in args.styles:
            continue
        rows = [(pid, [refs[pid, index]]) for pid, index in wanted]
        rows += [(pid, sorted(prompts[pid])) for pid in sorted(prompts)]
        plain, graded = [], []
        for pid, images in rows:
            plain.append((pid, images))
            g = []
            for index, path in images:
                dest = out / "graded" / f"{pid}_{index}.png"
                if not dest.exists():
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    print_grade.grade(str(path), str(dest))
                g.append((index, dest))
            graded.append((pid, g))
        print(sheet(plain, out / f"sheet_{style}.png", f"Style {style}: {args.tag}"))
        print(sheet(graded, out / f"sheet_{style}_graded.png", f"Style {style}: {args.tag}, through print_grade.py"))


if __name__ == "__main__":
    main()
