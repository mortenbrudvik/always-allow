"""The plate pack in Midjourney (BRIEF.md step 4): the prompts, the downloads, the contact sheets and the picks.

The prompts are production/storyboard/mj_prompts.md's (tools/storyboard.py writes it). Each job's four images go from
the Downloads folder into production/assets/mj/inbox/, with a row each in production/storyboard/mj_manifest.csv
(prompt_id and `for` are the plate ID). A pick is copied to production/assets/frames/<plate>.png, which the
compositor and the clip loop look for, and noted in production/storyboard/plate_picks.json.

Usage, with the project's .venv:
  .venv/Scripts/python tools/plates.py prompt A_desk_ws           # print one plate's prompt
  .venv/Scripts/python tools/plates.py list                       # every plate, in the pack's order, and its state
  .venv/Scripts/python tools/plates.py ingest A_desk_ws JOB_ID    # file a finished job's 4 downloads
  .venv/Scripts/python tools/plates.py sheet A_desk_ws B_stage_alone --name canon   # one row per plate
  .venv/Scripts/python tools/plates.py pick A_desk_ws 2 [--note "..."]              # use image 2 of its job
  .venv/Scripts/python tools/plates.py fix B_cu_cobalt --recolour --place left        # redo the frame with fixes
  .venv/Scripts/python tools/plates.py status                     # shots with their plate files present -> plate
"""
import argparse
import csv
import datetime
import json
import re
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT / "production" / "storyboard" / "mj_prompts.md"
MANIFEST = ROOT / "production" / "storyboard" / "mj_manifest.csv"
PICKS = ROOT / "production" / "storyboard" / "plate_picks.json"
INBOX = ROOT / "production" / "assets" / "mj" / "inbox"
FRAMES = ROOT / "production" / "assets" / "frames"
SHEETS = ROOT / "production" / "assets" / "mj" / "sheets"
DOWNLOADS = Path.home() / "Downloads"
TILE = (640, 360)
GAP = 8


def rel(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def pack():
    """The plates in the pack's order: {plate: {"prompt", "note", "set"}}."""
    text = PACK.read_text(encoding="utf-8")
    out, section = {}, None
    for m in re.finditer(r"^## ([^\n]+)$|^\*\*([A-Z]_[A-Za-z0-9_]+)\*\* \(([^)]*)\)\n```\n(.+?)\n```", text, re.M | re.S):
        if m.group(1):
            section = m.group(1)
        else:
            out[m.group(2)] = {"prompt": m.group(4).strip(), "note": m.group(3), "set": section}
    return out


def manifest():
    with MANIFEST.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def picks():
    return json.loads(PICKS.read_text(encoding="utf-8")) if PICKS.exists() else {}


def ingest(plate, job, prompt_id=None):
    """Move a job's downloaded images into the inbox and log them. The files are found by the job ID in their names.
    `prompt_id` names a variant of the plate's prompt (a test, a fix); it defaults to the plate."""
    if plate not in pack():
        raise SystemExit(f"no plate {plate} in the pack")
    rows = manifest()
    if any(r["job_id"] == job for r in rows):
        raise SystemExit(f"job {job} is in the manifest already")
    # from the Downloads folder, or already in the inbox (tools/mj_receive.py writes there straight from the page)
    found = sorted(p for p in DOWNLOADS.glob(f"*{job}_*.png") if re.search(rf"{job}_(\d)\.png$", p.name))
    found = found or sorted(p for p in INBOX.glob(f"*{job}_*.png") if re.search(rf"{job}_(\d)\.png$", p.name))
    if not found:
        raise SystemExit(f"no images of job {job} in {DOWNLOADS} or {INBOX}")
    INBOX.mkdir(parents=True, exist_ok=True)
    new = []
    for p in found:
        dest = INBOX / p.name
        if p != dest:
            shutil.move(str(p), dest)
        index = re.search(rf"{job}_(\d)\.png$", p.name).group(1)
        new.append({"prompt_id": prompt_id or plate, "job_id": job, "index": index, "file": rel(dest), "for": plate})
    with MANIFEST.open("a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=["prompt_id", "job_id", "index", "file", "for"]).writerows(new)
    print(f"{plate}: {len(new)} images of job {job} -> {rel(INBOX)}")
    return new


def sheet(plates, name):
    """One row per plate (or per prompt ID, for a variant), one column per image, each tile labelled with its index."""
    rows = manifest()
    by = {}
    for p in plates:
        own = [r for r in rows if r["prompt_id"] == p] or [r for r in rows if r["for"] == p]
        by[p] = sorted(own, key=lambda r: (r["job_id"], r["index"]))
    cols = max((len(v) for v in by.values()), default=1)
    font = ImageFont.load_default(size=22)
    w = cols * TILE[0] + (cols + 1) * GAP + 260
    h = len(plates) * (TILE[1] + GAP) + GAP
    out = Image.new("RGB", (w, h), (12, 12, 14))
    d = ImageDraw.Draw(out)
    for i, p in enumerate(plates):
        y = GAP + i * (TILE[1] + GAP)
        d.text((GAP, y + 8), p, fill=(230, 230, 230), font=font)
        chosen = picks().get(p)
        for j, r in enumerate(by[p]):
            im = Image.open(ROOT / r["file"]).convert("RGB")
            im.thumbnail(TILE)
            x = 260 + GAP + j * (TILE[0] + GAP)
            out.paste(im, (x, y))
            mark = chosen and chosen["job_id"] == r["job_id"] and chosen["index"] == int(r["index"])
            d.rectangle((x, y, x + 58, y + 34), fill=(201, 100, 66) if mark else (12, 12, 14))
            d.text((x + 8, y + 5), r["index"], fill=(255, 255, 255), font=font)
    SHEETS.mkdir(parents=True, exist_ok=True)
    dest = SHEETS / f"{name}.jpg"
    out.save(dest, quality=88)
    print(rel(dest))
    return dest


def zoom(plates, name, tile=(960, 540)):
    """Each plate's latest job as a 2x2 grid of large tiles, the plates side by side: for making the picks."""
    rows = manifest()
    font = ImageFont.load_default(size=28)
    cell_w, cell_h = 2 * tile[0] + GAP, 2 * tile[1] + GAP + 44
    out = Image.new("RGB", (len(plates) * (cell_w + GAP) + GAP, cell_h + GAP), (12, 12, 14))
    d = ImageDraw.Draw(out)
    for k, p in enumerate(plates):
        own = [r for r in rows if r["prompt_id"] == p] or [r for r in rows if r["for"] == p]
        job = own[-1]["job_id"]
        x0 = GAP + k * (cell_w + GAP)
        d.text((x0, GAP + 6), f"{p}  ({job[:8]})", fill=(230, 230, 230), font=font)
        for r in (r for r in own if r["job_id"] == job):
            i = int(r["index"])
            im = Image.open(ROOT / r["file"]).convert("RGB")
            im.thumbnail(tile)
            x, y = x0 + (i % 2) * (tile[0] + GAP), GAP + 44 + (i // 2) * (tile[1] + GAP)
            out.paste(im, (x, y))
            d.rectangle((x, y, x + 44, y + 40), fill=(12, 12, 14))
            d.text((x + 12, y + 4), str(i), fill=(255, 255, 255), font=font)
    SHEETS.mkdir(parents=True, exist_ok=True)
    dest = SHEETS / f"{name}.jpg"
    out.save(dest, quality=86)
    print(rel(dest))
    return dest


def pick(plate, index, note="", job=None):
    rows = [r for r in manifest() if r["for"] == plate and int(r["index"]) == index and (job is None or r["job_id"] == job)]
    if not rows:
        raise SystemExit(f"no image {index} for {plate}")
    r = rows[-1]  # the latest job's, unless a job is named
    FRAMES.mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / r["file"], FRAMES / f"{plate}.png")
    all_picks = picks()
    all_picks[plate] = {"job_id": r["job_id"], "index": index, "file": r["file"], "frame": rel(FRAMES / f"{plate}.png"),
                        "picked": datetime.datetime.now().isoformat(timespec="seconds"), "note": note}
    PICKS.write_text(json.dumps(all_picks, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{plate}: image {index} of job {r['job_id']} -> {rel(FRAMES / f'{plate}.png')}")


def fix(plate, debar=False, recolour=False, lift=1.0, boxes=(), side=None, flat=None, line=None, sky=None):
    """Redo a pick's frame from its Midjourney image with the fixes asked for (tools/plate_fix.py), and record
    them: every call replaces the plate's earlier fixes, so no fixes at all resets the frame to the image."""
    import plate_fix
    all_picks = picks()
    if plate not in all_picks:
        raise SystemExit(f"{plate} has no pick")
    rec = all_picks[plate]
    fixes, notes = plate_fix.plan(ROOT / rec["file"], debar, recolour, lift, boxes, side, flat, line, sky)
    plate_fix.apply(ROOT / rec["file"], fixes).save(FRAMES / f"{plate}.png")
    rec["fixes"] = fixes
    PICKS.write_text(json.dumps(all_picks, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{plate}: " + ("; ".join(notes) or "no fixes, the image as it came"))


def thumbs(size=(480, 270)):
    """Every picked frame small (production/assets/thumbs/plates/<plate>.jpg, covering 16:9): for the flash-past's
    mosaic tiles, which would otherwise decode 64 full-size plates at once."""
    out = ROOT / "production" / "assets" / "thumbs" / "plates"
    out.mkdir(parents=True, exist_ok=True)
    n = 0
    for plate in picks():
        f = next((FRAMES / f"{plate}{x}" for x in (".png", ".jpg") if (FRAMES / f"{plate}{x}").exists()), None)
        dest = out / f"{plate}.jpg"
        if not f or (dest.exists() and dest.stat().st_mtime >= f.stat().st_mtime):
            continue
        im = Image.open(f).convert("RGB")
        s = max(size[0] / im.width, size[1] / im.height)
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        x, y = (im.width - size[0]) // 2, (im.height - size[1]) // 2
        im.crop((x, y, x + size[0], y + size[1])).save(dest, quality=86)
        n += 1
    print(f"{n} thumbnail(s) made in {rel(out)}")


def status():
    """BRIEF.md step 4's done test, applied: a shot that needs a plate (its own, or its clip's start frame) goes from
    `planned` to `plate` when the plate is in production/assets/frames/ and, for a 2.5D shot, its depth map is in
    production/assets/depth/. Later statuses are the pipeline's and stay. Returns the shots still waiting."""
    board_path = ROOT / "production" / "storyboard" / "shots.json"
    board = json.loads(board_path.read_text(encoding="utf-8"))
    clip_plate = {c["clip"]: c["plate"] for c in board["clips"]}
    frame = lambda p: next((FRAMES / f"{p}{x}" for x in (".png", ".jpg") if (FRAMES / f"{p}{x}").exists()), None)
    waiting, moved = [], 0
    for s in board["shots"]:
        need = [p for p in dict.fromkeys([s.get("plate"), clip_plate.get(s.get("clip"))]) if p]
        if not need:
            continue
        missing = [p for p in need if not frame(p)]
        depth = ROOT / "production" / "assets" / "depth" / f"{s['plate']}.png" if s["motion_tier"] == "2.5d" and s.get("plate") else None
        if depth and not depth.exists():
            missing.append(f"{s['plate']} (depth)")
        if missing:
            waiting.append((s["id"], missing))
            continue
        files = {p: rel(frame(p)) for p in need}
        if depth:
            files["depth"] = rel(depth)
        s.setdefault("files", {}).update(files)
        if s["status"] == "planned":
            s["status"] = "plate"
            moved += 1
    board_path.write_text(json.dumps(board, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    counts = {}
    for s in board["shots"]:
        counts[s["status"]] = counts.get(s["status"], 0) + 1
    print(f"{moved} shot(s) moved to plate; now " + ", ".join(f"{n} {k}" for k, n in sorted(counts.items())))
    for sid, missing in waiting:
        print(f"  {sid} waits for {', '.join(missing)}")
    return waiting


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("prompt")
    s.add_argument("plate")
    sub.add_parser("list")
    sub.add_parser("status", help="move the shots whose plate files are present to `plate` (step 4's done test)")
    sub.add_parser("thumbs", help="small copies of every picked frame, for the flash-past's mosaic tiles")
    s = sub.add_parser("ingest")
    s.add_argument("plate")
    s.add_argument("job")
    s.add_argument("--prompt-id", help="a variant's name, such as A_desk_ws.b (default: the plate)")
    s = sub.add_parser("sheet")
    s.add_argument("plates", nargs="+")
    s.add_argument("--name", required=True)
    s = sub.add_parser("zoom")
    s.add_argument("plates", nargs="+")
    s.add_argument("--name", required=True)
    s = sub.add_parser("pick")
    s.add_argument("plate")
    s.add_argument("index", type=int)
    s.add_argument("--note", default="")
    s.add_argument("--job")
    s = sub.add_parser("fix")
    s.add_argument("plate")
    s.add_argument("--debar", action="store_true", help="crop off letterbox bars")
    s.add_argument("--recolour", action="store_true", help="teal and navy to cobalt")
    s.add_argument("--lift", type=float, default=1.0, help="with --recolour: raise the blues' value by this factor")
    s.add_argument("--inpaint", nargs="+", default=[], metavar="X0,Y0,X1,Y1[,SIGN[,CUT]]",
                   help="boxes to paint out, as fractions; SIGN -1 paints out only what's darker than the box's border, "
                        "1 only what's lighter; CUT is how far from the border's colour counts (default 28 of 255)")
    s.add_argument("--place", choices=["left", "right"], help="crop to put her face left or right of centre")
    s.add_argument("--flatfill", metavar="X0,Y0,X1,Y1", help="a box of flat floor to clear, down to --edge")
    s.add_argument("--edge", metavar="XA,YA,XB,YB", help="with --flatfill: the floor's straight edge, two points")
    s.add_argument("--sky", type=float, metavar="Y", help="lift the sky above this horizon (a fraction of the height) to pale grey")
    args = ap.parse_args()
    if args.cmd == "prompt":
        print(pack()[args.plate]["prompt"])
    elif args.cmd == "list":
        done = {r["for"] for r in manifest()}
        chosen = picks()
        for p, v in pack().items():
            state = "picked" if p in chosen else "made" if p in done else "to make"
            print(f"{p:24s} {state:8s} {v['note']}")
    elif args.cmd == "ingest":
        ingest(args.plate, args.job, args.prompt_id)
    elif args.cmd == "sheet":
        sheet(args.plates, args.name)
    elif args.cmd == "zoom":
        zoom(args.plates, args.name)
    elif args.cmd == "pick":
        pick(args.plate, args.index, args.note, args.job)
    elif args.cmd == "status":
        status()
    elif args.cmd == "thumbs":
        thumbs()
    elif args.cmd == "fix":
        boxes = [tuple(float(v) for v in b.split(",")) for b in args.inpaint]
        nums = lambda v: tuple(float(x) for x in v.split(",")) if v else None
        fix(args.plate, args.debar, args.recolour, args.lift, boxes, args.place, nums(args.flatfill), nums(args.edge), args.sky)


if __name__ == "__main__":
    main()
