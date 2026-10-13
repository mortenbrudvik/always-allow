"""The deliverables (BRIEF.md step 8), from the final render of the full video (production/out/roughcut.mp4).

  master   production/out/always-allow_master_1080p.mp4: the full song, 1920x1080 H.264 + AAC (the final render)
  cut      production/out/always-allow_cut_1080p.mp4: at most 2:20, the song trimmed on bar lines (below)
  check    probe every deliverable in production/out/ and print what it is

The cut keeps the spine (BRIEF.md: the little window, the whispered "Allow?", the click, "Access granted.") and the
outro with the receipt. Each join is a bar line of production/analysis/song.json where a shot changes or runs on and
no word crosses it; the video cuts on the frame nearest the bar line, and the audio is the unedited song cut at the
same frame times, so picture and sound stay in sync, with an 8 ms fade either side of each join so it doesn't click.
Rounding the joins the same way keeps each within 15 ms of the musical grid. 2:20 is X's limit for a post's video, and
X takes files up to 512 MB, so the cut's bitrate is capped at 25 Mbit/s (the print's grain runs CRF 15 to ~46 Mbit/s,
which would make it ~790 MB); the master keeps the full rate.

Usage, with the project's .venv:
  .venv/Scripts/python tools/deliver.py master
  .venv/Scripts/python tools/deliver.py cut
  .venv/Scripts/python tools/deliver.py check
"""
import argparse
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "production" / "out"
RENDER = OUT / "roughcut.mp4"
MASTER = OUT / "always-allow_master_1080p.mp4"
CUT = OUT / "always-allow_cut_1080p.mp4"
SONG = ROOT / "Always Allow.mp3"
FPS = 24
FADE = 0.008

# The cut, in frames of the full video: [from, to). Bars are the board's (bar 0 is the drop).
SEGMENTS = [
    (0, 861),      # bars -8 to 12: the intro, "Give me a goal", and the drop, "Tabs open... Executing."
    (1506, 2451),  # bars 27 to 49: break 1, the first little window ("Allow once? Or..."), and hook 1 to "Next step."
    (4858, 5716),  # bars 105 to 125: the riser and the whispered "Allow?", the click, "Access granted.", hook 3
    (6059, 6662),  # bar 133 to the end: the outro, "Task complete.", the Agent's receipt, the button, black
]


def run(cmd):
    subprocess.run(cmd, check=True)


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration:stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate",
                          "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def master():
    if not RENDER.exists():
        raise SystemExit(f"render the video first: node production/comp/scripts/render.mjs full ({RENDER} is missing)")
    shutil.copyfile(RENDER, MASTER)
    print(f"{MASTER.relative_to(ROOT).as_posix()}: the full render")


def cut():
    src = MASTER if MASTER.exists() else RENDER
    n = len(SEGMENTS)
    parts = [f"[0:v]split={n}" + "".join(f"[s{i}]" for i in range(n)), f"[1:a]asplit={n}" + "".join(f"[r{i}]" for i in range(n))]
    for i, (a, b) in enumerate(SEGMENTS):
        t0, t1 = a / FPS, b / FPS
        if i == n - 1:
            t1 = max(t1, float(probe(SONG)["format"]["duration"]))  # the last one runs to the song's own end
        parts.append(f"[s{i}]trim=start_frame={a}:end_frame={b},setpts=PTS-STARTPTS[v{i}]")
        fades = [] if i == 0 else [f"afade=t=in:d={FADE}"]
        if i < n - 1:
            fades.append(f"afade=t=out:st={t1 - t0 - FADE:.4f}:d={FADE}")
        parts.append(f"[r{i}]atrim=start={t0:.6f}:end={t1:.6f},asetpts=PTS-STARTPTS" + "".join("," + f for f in fades) + f"[a{i}]")
    parts.append("".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[v]")
    parts.append("".join(f"[a{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1[a]")
    run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-i", str(SONG), "-filter_complex", ";".join(parts),
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "15", "-maxrate", "25M", "-bufsize", "50M",
         "-preset", "slow", "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "320k",
         "-movflags", "+faststart", str(CUT)])
    frames = sum(b - a for a, b in SEGMENTS)
    print(f"{CUT.relative_to(ROOT).as_posix()}: {frames} frames, {frames / FPS:.2f} s, {CUT.stat().st_size / 1e6:.0f} MB")


def check():
    for f in sorted(OUT.iterdir()):
        if f.suffix.lower() not in (".mp4", ".png"):
            continue
        p = probe(f)
        streams = ", ".join(f"{s['codec_type']} {s['codec_name']}" + (f" {s.get('width')}x{s.get('height')}" if s["codec_type"] == "video" else "")
                            for s in p.get("streams", []))
        dur = p.get("format", {}).get("duration")
        mb = f"{f.stat().st_size / 1e6:6.0f} MB"
        print(f"{f.name:40s} {float(dur):7.2f} s {mb}  {streams}" if dur and f.suffix == ".mp4" else f"{f.name:40s} {'':9s} {mb}  {streams}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("step", choices=["master", "cut", "check"])
    args = ap.parse_args()
    {"master": master, "cut": cut, "check": check}[args.step]()


if __name__ == "__main__":
    main()
