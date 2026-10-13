"""Compare lip-sync models on Midjourney test clips (PLAN.md phase 0b).

Put 2-3 Midjourney HD clips of the Agent in production/tests/lipsync/clips/
(mj_test_prompts.md there says how to make them). The script cuts one vocal
line from the song, from the vocal stem if production/stems/ has one, runs each
clip through the chosen fal models, and writes a side-by-side per clip to
production/tests/lipsync/out/. It adds a scoring table for the run to
production/tests/lipsync/results.md and logs every paid call, with its
estimated cost, to production/ledger.csv.

Usage, with the project's .venv (FAL_KEY comes from the repo's .env or the environment):
  .venv/Scripts/python tools/lipsync_test.py                    # bars 88-90, default models
  .venv/Scripts/python tools/lipsync_test.py --start 168.9 --end 174.9 --models sync-2-pro
  .venv/Scripts/python tools/lipsync_test.py --dry-run          # no API calls; checks the plumbing in out/dry-run/
  .venv/Scripts/python tools/lipsync_test.py --clips t2,t3 --reuse   # some clips; keep results in out/

Each call is submitted to fal's queue and polled; its request ID goes to
out/requests.txt. After --timeout seconds a call still waiting in the queue is
cancelled; one already running is left on fal, logged at its estimated cost and
noted in results.md, so it can be collected later.

The endpoints, inputs and prices below are from fal's model pages as of
28 Sep 2026. Check them before a paid run.
"""
import argparse
import csv
import datetime
import filecmp
import json
import math
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SONG = ROOT / "Always Allow.mp3"
ANALYSIS = ROOT / "production" / "analysis" / "song.json"
STEMS = ROOT / "production" / "stems"
TEST = ROOT / "production" / "tests" / "lipsync"
LEDGER = ROOT / "production" / "ledger.csv"
PROMPT = "A calm woman looks straight into the camera and says a short line, deadpan, with minimal head movement."

# name: (endpoint, extra inputs, estimated USD for s seconds of output)
MODELS = {
    "latentsync": ("fal-ai/latentsync", {}, lambda s: 0.20 if s <= 40 else 0.005 * s),
    "sync-2-pro": ("fal-ai/sync-lipsync/v2/pro", {"sync_mode": "cut_off"}, lambda s: 5 / 60 * s),
    "infinitalk": ("fal-ai/infinitalk/video-to-video", {"prompt": PROMPT, "resolution": "720p"}, lambda s: 0.20 * s),
    "veed": ("veed/lipsync/v2", {}, lambda s: 0.07 * s),
}
DEFAULT_MODELS = "latentsync,sync-2-pro,infinitalk"


def ffmpeg():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
    except ImportError:
        sys.exit("ffmpeg not found: install it, or run pip install -r tools/requirements-lipsync.txt")
    return imageio_ffmpeg.get_ffmpeg_exe()


def probe(path):
    """Return (width, height, fps, seconds) of a video."""
    import imageio_ffmpeg
    reader = imageio_ffmpeg.read_frames(str(path))
    meta = next(reader)
    reader.close()
    return (*meta["size"], meta["fps"], meta["duration"])


def line_times(args):
    if args.start is not None:
        return args.start, args.end
    song = json.loads(ANALYSIS.read_text())
    down = song["downbeats_s"]
    bar0 = next(s["start"] for s in song["sections"] if s["bar"] == 0)
    i0 = min(range(len(down)), key=lambda i: abs(down[i] - bar0))
    a, b = (int(x) for x in args.bars.split(":"))
    return down[i0 + a] - args.pad, down[i0 + b] + args.pad


def compare(ff, panels, audio, seconds, out):
    """Tile the panels left to right, top to bottom, over the vocal line. A None panel stays black."""
    cols = 2 if len(panels) <= 4 else 3
    cells = cols * math.ceil(len(panels) / cols)
    w, h = (960, 540) if cols == 2 else (640, 360)
    videos = [p for p in panels if p is not None]
    chains, k = [], 0
    for i in range(cells):
        if i < len(panels) and panels[i] is not None:
            chains.append(f"[{k}:v]scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,"
                          f"setsar=1,fps=24,trim=duration={seconds:.3f},setpts=PTS-STARTPTS[v{i}]")
            k += 1
        else:
            chains.append(f"color=black:s={w}x{h}:r=24:d={seconds:.3f}[v{i}]")
    layout = "|".join(f"{i % cols * w}_{i // cols * h}" for i in range(cells))
    chains.append("".join(f"[v{i}]" for i in range(cells)) + f"xstack=inputs={cells}:layout={layout}[grid]")
    inputs = [x for p in [*videos, audio] for x in ("-i", str(p))]
    subprocess.run([ff, "-y", "-v", "error", *inputs, "-filter_complex", ";".join(chains), "-map", "[grid]",
                    "-map", f"{len(videos)}:a", "-t", f"{seconds:.3f}", "-r", "24", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-crf", "20", "-c:a", "aac", str(out)], check=True)


def log_spend(model, seconds, usd):
    new = not LEDGER.exists()
    with LEDGER.open("a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["time", "tool", "model", "endpoint", "seconds", "estimated_usd"])
        w.writerow([datetime.datetime.now().isoformat(timespec="seconds"), "lipsync_test", model,
                    MODELS[model][0], f"{seconds:.2f}", f"{usd:.3f}"])


class Unfinished(TimeoutError):
    """A call that timed out. billed is False when it was cancelled before a worker picked it up."""
    def __init__(self, message, billed):
        super().__init__(message)
        self.billed = billed


def run_model(fal_client, endpoint, inputs, label, timeout, log):
    """Submit to fal's queue and poll. Return the output video URL, or raise Unfinished.

    On timeout a call that is still queued is cancelled, since it hasn't cost anything yet; one that is
    already running is left to finish on fal, where its request ID can collect the result."""
    handle = fal_client.submit(endpoint, arguments=inputs)
    rid = handle.request_id
    print(f"  {label}: request {rid}")
    with log.open("a") as f:
        f.write(f"{datetime.datetime.now().isoformat(timespec='seconds')} {label} {endpoint} {rid}\n")
    t0, last = time.monotonic(), None
    while time.monotonic() - t0 < timeout:
        status = handle.status()
        if isinstance(status, fal_client.Completed):
            return handle.get()["video"]["url"]
        now = (f"queued, position {status.position}" if isinstance(status, fal_client.Queued) else "running")
        if now != last:
            print(f"  {label}: {now} ({time.monotonic() - t0:.0f} s)")
            last = now
        time.sleep(5)
    if isinstance(handle.status(), fal_client.Queued):
        handle.cancel()
        raise Unfinished(f"still queued after {timeout:.0f} s, so cancelled (request {rid})", billed=False)
    raise Unfinished(f"not done after {timeout:.0f} s ({last}); request {rid} is still on fal", billed=True)


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--bars", default="88:90",
                   help="the vocal window as start:end bars (default 88:90: \"I'm here for your weekends. Your mor-\", "
                        "cut off mid-word; it's the window the first lip-sync test used)")
    p.add_argument("--pad", type=float, default=0.4, help="seconds added before and after --bars (default 0.4)")
    p.add_argument("--start", type=float, help="line start in seconds, instead of --bars")
    p.add_argument("--end", type=float, help="line end in seconds, with --start")
    p.add_argument("--models", default=DEFAULT_MODELS, help=f"comma-separated, from: {', '.join(MODELS)}")
    p.add_argument("--clips", help="comma-separated clip names without extension, e.g. t2,t3 (default: all)")
    p.add_argument("--reuse", action="store_true",
                   help="keep a model result already in out/ from an earlier paid run instead of paying for it again")
    p.add_argument("--timeout", type=float, default=1200,
                   help="seconds to wait for each model call (default 1200); it keeps running on fal after that")
    p.add_argument("--dry-run", action="store_true",
                   help="no API calls; each clip stands in for the model results, all written to out/dry-run/")
    args = p.parse_args()
    models = args.models.split(",")
    if unknown := [m for m in models if m not in MODELS]:
        p.error(f"unknown model(s): {', '.join(unknown)}")
    if (args.start is None) != (args.end is None):
        p.error("--start and --end go together")
    clips = sorted(c for c in (TEST / "clips").glob("*") if c.suffix.lower() in {".mp4", ".mov", ".webm", ".m4v"})
    if args.clips:
        wanted = args.clips.split(",")
        if missing := [w for w in wanted if w not in {c.stem for c in clips}]:
            p.error(f"no such clip(s) in {(TEST / 'clips').relative_to(ROOT)}: {', '.join(missing)}")
        clips = [c for c in clips if c.stem in wanted]
    if not clips:
        sys.exit(f"No clips in {(TEST / 'clips').relative_to(ROOT)}; make them with {(TEST / 'mj_test_prompts.md').relative_to(ROOT)}.")
    if not args.dry_run:
        from envfile import load_env
        load_env()
        if not os.environ.get("FAL_KEY"):
            sys.exit("Set FAL_KEY in .env or the environment (or use --dry-run).")
        import fal_client

    ff = ffmpeg()
    # A dry run gets its own folder: in the shared one, its copies overwrote t1's paid results on 28 Sep.
    out = TEST / "out" / "dry-run" if args.dry_run else TEST / "out"
    out.mkdir(parents=True, exist_ok=True)
    start, end = line_times(args)
    seconds = end - start
    stems = sorted(s for s in STEMS.glob("*") if "vocal" in s.name.lower()) if STEMS.exists() else []
    source = stems[0] if stems else SONG
    if not stems:
        print("No vocal stem in production/stems/; using the full mix, which lip-syncs less cleanly.")
    line = out / "line.wav"
    subprocess.run([ff, "-y", "-v", "error", "-ss", f"{start:.3f}", "-t", f"{seconds:.3f}", "-i", str(source),
                    "-ac", "1", "-ar", "44100", str(line)], check=True)
    audio_url = None if args.dry_run else fal_client.upload_file(line)

    run = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    what = f"bars {args.bars}" if args.start is None else "custom times"
    order = ", ".join(f"{i + 1} {name}" for i, name in enumerate(["original (no lip sync)", *models]))
    report = [f"## Run of {run}{' (dry run)' if args.dry_run else ''}", "",
              f"- Line: {what}, {start:.2f}-{end:.2f} s, from {source.relative_to(ROOT)}",
              f"- Panels in each side-by-side, left to right and top to bottom: {order}",
              "- Score 1-5 (5 is best). A model passes with 4 or more overall on every clip.", ""]
    total = 0.0
    for clip in clips:
        w, h, fps, length = probe(clip)
        print(f"{clip.name}: {w}x{h}, {fps:g} fps, {length:.1f} s")
        if h < 720:
            print(f"  {clip.name} is below 720p; make lip-sync shots in Midjourney HD.")
        if length < seconds:
            print(f"  {clip.name} is shorter than the {seconds:.1f} s line; results may loop or cut off.")
        def reusable(result):  # a dry-run copy is identical to the clip, so it doesn't count
            return args.reuse and result.exists() and not filecmp.cmp(result, clip, shallow=False)
        skip_upload = all(reusable(out / f"{clip.stem}__{m}.mp4") for m in models)
        clip_url = None if args.dry_run or skip_upload else fal_client.upload_file(clip)
        panels, rows = [clip], []
        for model in models:
            result = out / f"{clip.stem}__{model}.mp4"
            endpoint, extra, cost = MODELS[model]
            note = ""
            try:
                if args.dry_run:
                    shutil.copy(clip, result)
                elif reusable(result):
                    print(f"  {model}: reusing {result.relative_to(ROOT)}")
                    note = "reused from an earlier run"
                else:
                    inputs = {"video_url": clip_url, "audio_url": audio_url, **extra}
                    if model == "infinitalk":  # Wan-style frame counts (4n + 1) at 25 fps
                        inputs["num_frames"] = min(721, max(41, 4 * math.ceil(seconds * 25 / 4) + 1))
                    print(f"  {model}: running {endpoint}")
                    try:
                        video = run_model(fal_client, endpoint, inputs, f"{clip.stem}/{model}", args.timeout,
                                          out / "requests.txt")
                    except Unfinished as e:
                        if e.billed:  # still running on fal, so it will probably be billed
                            log_spend(model, seconds, cost(seconds))
                            total += cost(seconds)
                        raise
                    urllib.request.urlretrieve(video, result)
                    made = probe(result)[3]
                    total += cost(made)
                    log_spend(model, made, cost(made))
                panels.append(result)
            except Exception as e:  # keep going: one failing model shouldn't sink the test
                note = f"failed: {e}".replace("|", "/").replace("\n", " ")[:200]
                print(f"  {model} {note}")
                panels.append(None)
            rows.append(f"| {model} | | | | | | {note} |")
        side_by_side = out / f"{clip.stem}__compare.mp4"
        compare(ff, panels, line, seconds, side_by_side)
        report += [f"### {clip.name}: `{side_by_side.relative_to(TEST)}`", "",
                   "| Model | Sync on p, b, m | Teeth and mouth | Keeps the face | No jitter | Overall | Notes |",
                   "|---|---|---|---|---|---|---|", *rows, ""]
    report.insert(4, f"- Estimated cost: ${total:.2f}")

    results = out / "results.md" if args.dry_run else TEST / "results.md"
    if not results.exists():
        results.write_text("# Lip-sync test results\n\nWritten by `tools/lipsync_test.py`. "
                           "Fill in the scores after watching each side-by-side.\n\n")
    with results.open("a") as f:
        f.write("\n".join(report) + "\n")
    print(f"Side-by-sides in {out.relative_to(ROOT)}; score them in {results.relative_to(ROOT)}. "
          f"Estimated cost ${total:.2f}.")


if __name__ == "__main__":
    main()
