"""Step 6's done test, applied (BRIEF.md): once production/out/roughcut.mp4 is a full-length render of the board, every
shot that isn't dropped and is in it with its real footage goes to `composited`.

A shot counts as in with its footage when: it's code (it's all code); it's a 2.5D shot whose plate and depth map are
in production/assets/; or it's a Seedance shot whose select is in production/clips/selects/ (a dancer's matte too).
BRIEF.md's order holds: a clip without speech from `clip`, a speaking one from `synced`, a 2.5D shot from `plate`, a
code shot from `planned`; a shot further back than that (a speaking clip not yet synced) stays where it is, and
`approved` is never touched.

Usage, with the project's .venv:
  .venv/Scripts/python tools/roughcut.py            # check the render and move the shots
  .venv/Scripts/python tools/roughcut.py --check    # only say what would move
"""
import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "production" / "storyboard" / "shots.json"
CUT = ROOT / "production" / "out" / "roughcut.mp4"
FRAMES = ROOT / "production" / "assets" / "frames"
DEPTH = ROOT / "production" / "assets" / "depth"
SELECTS = ROOT / "production" / "clips" / "selects"
MATTES = ROOT / "production" / "clips" / "mattes"
READY = {"code": {"planned"}, "2.5d": {"plate"}, "seedance": {"clip", "synced"}}


def probe(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
                          "stream=width,height,r_frame_rate,nb_read_packets", "-of", "json", str(video)],
                         capture_output=True, text=True, check=True).stdout
    s = json.loads(out)["streams"][0]
    n, d = (int(v) for v in s["r_frame_rate"].split("/"))
    return {"width": s["width"], "height": s["height"], "fps": n / d, "frames": int(s["nb_read_packets"])}


def footage_ok(s, clips):
    if s["motion_tier"] == "code":
        return True
    if s["motion_tier"] == "2.5d":
        return (FRAMES / f"{s['plate']}.png").exists() and (DEPTH / f"{s['plate']}.png").exists()
    c = clips.get(s["clip"])
    if not c or not (SELECTS / f"{s['clip']}.mp4").exists():
        return False
    return c["kind"] != "dancer" or (MATTES / f"{s['clip']}.webm").exists()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    board = json.loads(SHOTS.read_text(encoding="utf-8"))
    if not CUT.exists():
        raise SystemExit(f"no rough cut at {CUT.relative_to(ROOT).as_posix()}: render it first (render.mjs full)")
    info = probe(CUT)
    if (info["width"], info["height"], info["fps"], info["frames"]) != (1920, 1080, 24.0, board["frames"]):
        raise SystemExit(f"the rough cut isn't the full board: {info}, the board has {board['frames']} frames")
    clips = {c["clip"]: c for c in board["clips"]}
    moved, waiting = [], []
    for s in board["shots"]:
        if s["status"] in ("dropped", "composited", "approved"):
            continue
        if s["status"] in READY[s["motion_tier"]] and footage_ok(s, clips):
            moved.append(s["id"])
            if not args.check:
                s["status"] = "composited"
        else:
            waiting.append(f"{s['id']} ({s['motion_tier']}, {s['status']})")
    if not args.check:
        SHOTS.write_text(json.dumps(board, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    counts = {}
    for s in board["shots"]:
        counts[s["status"]] = counts.get(s["status"], 0) + 1
    print(f"{'would move' if args.check else 'moved'} {len(moved)} shot(s) to composited; now "
          + ", ".join(f"{n} {k}" for k, n in sorted(counts.items())))
    for w in waiting:
        print(f"  waits: {w}")


if __name__ == "__main__":
    main()
