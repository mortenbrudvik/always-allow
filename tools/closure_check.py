"""The closure check (BRIEF.md step 3): do a repaired clip's lips close for every p, b and m it sings?

For every p, b and m in the clip's window (production/analysis/letters.json, from tools/align_lyrics.py --letters),
it looks at the lip gap (tools/lipcheck.py: the inner-lip distance over the eye-corner distance, per frame, from
MediaPipe's face landmarker) in the frames around the letter. A closure is found when one of those frames is at or
under CLOSED. A clip fails when FAIL_MISSES closures miss, or when its only closure misses. A frame without a face
counts as a miss: what can't be seen can't pass.

Calibrated on step 0's two sync-2-pro repairs (`calibrate`, which writes production/analysis/closure_calibration.json):
- t3g_sync2pro.mp4, a pass by eye: its lips close for both /m/s of "I'm" and the /b/ of "job";
- t2r_sync2pro.mp4, borderline by eye: the /m/ closes on its frame, the /b/ of "job" a frame or two late.
BRIEF.md says to look in the three frames ending on the letter, since the lips close before a p or b is heard. The
aligner doesn't time the burst, though: it puts the letter where the closure begins (a sung "job" ends on a held,
unreleased b), and t3g's lips close on the letter's frame or up to two frames after it. Session 4's two test clips
(30 Sep) closed the other way: C13's lips shut fully for the /m/ of "me" one to three frames before its letter
(0.001-0.008) and were open again on it, and C12's /m/ two frames before. So the window is two frames either side
of the letter's frame, about 83 ms, inside what reads as in sync; the user chose it on 30 Sep. CLOSED is taken from
t3g's closed frames: the widest gap at which one of its closures shut (0.021 on the /m/ of the first "I'm"), plus a
tenth. With these, t3g closes 3 of 3 and t2r 1 of 2, still missing the late /b/ (its nearest frame at 0.046,
against 0.001-0.005 with the lips at rest). So one miss is borderline and still passes, and two fail a clip.

Usage, with the project's .venv (tools/requirements-track.txt installed):
  .venv/Scripts/python tools/closure_check.py CLIP.mp4 --start 168.9 --duration 6
  .venv/Scripts/python tools/closure_check.py calibrate
"""
import argparse
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
LETTERS = ROOT / "production" / "analysis" / "letters.json"
CALIBRATION = ROOT / "production" / "analysis" / "closure_calibration.json"
REPAIRS = ROOT / "production" / "tests" / "seedance" / "out" / "repair"
STEP0 = [("t3g", 168.9, 6.0, "pass"), ("t2r", 168.59, 4.0, "borderline")]  # windows from step 0's sync_report.json

CLOSED = 0.023      # lip gap at or under which the lips count as closed (from t3g, see above)
WINDOW = (-2, 2)    # frames to look in, from the letter's frame: two either side of the frame it starts in
FAIL_MISSES = 2     # a clip fails with this many misses, or when its only closure misses
MIN_FACE = 0.8      # and when its face is found in fewer of its frames than this


def rel(path):
    path = Path(path).resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()


def closures(start, duration, letters=LETTERS):
    """The p, b and m whose letters start inside the window, in song seconds."""
    data = json.loads(Path(letters).read_text(encoding="utf-8"))
    return [c for c in data["closures"] if start <= c["start"] < start + duration]


def lip_gap(clip):
    """The lip gap per frame (NaN where no face was found) and the frame rate."""
    import lipcheck
    track, fps = lipcheck.mouth(clip)
    return track[:, 0], fps


def verdict(misses, checked):
    return checked == 0 or not (misses >= FAIL_MISSES or (checked == 1 and misses == 1))


def judge(gap, fps, start, marks, closed=CLOSED, window=WINDOW):
    """Look for each closure in its frames of the gap track. `gap` covers the clip from song time `start`."""
    rows = []
    for c in marks:
        f = int(math.floor((c["start"] - start) * fps + 1e-6))  # the frame on screen when the letter starts
        frames = [i for i in range(f + window[0], f + window[1] + 1) if 0 <= i < len(gap)]
        seen = [float(gap[i]) for i in frames if np.isfinite(gap[i])]
        lowest = min(seen) if seen else None
        rows.append({"word": c["word"], "letter": c["letter"], "line": c["line"], "song_s": c["start"], "frame": f,
                     "frames": frames, "gaps": [None if not np.isfinite(gap[i]) else round(float(gap[i]), 4) for i in frames],
                     "lowest": None if lowest is None else round(lowest, 4), "seen": bool(seen),
                     "closed": lowest is not None and lowest <= closed})
    misses = sum(not r["closed"] for r in rows)
    return rows, misses


def check(clip, start, duration, gap=None, fps=None, letters=LETTERS, shown=None):
    """The closure check of one clip whose first frame is at song time `start`. Returns a dict with `passes`.
    `shown` limits it to the letters the cut shows: (from, to) stretches in the same song seconds as the window; a
    letter after the edit has cut away (a window may end mid-word) is never on screen, so it isn't checked."""
    if gap is None:
        gap, fps = lip_gap(clip)
    marks = closures(start, duration, letters)
    if shown is not None:
        marks = [c for c in marks if any(a <= c["start"] < b for a, b in shown)]
    rows, misses = judge(gap, fps, start, marks)
    face = float(np.isfinite(gap).mean()) if len(gap) else 0.0
    passes = verdict(misses, len(rows)) and face >= MIN_FACE
    return {"clip": rel(clip), "window": {"start": start, "duration": duration},
            "shown": None if shown is None else [[round(a, 3), round(b, 3)] for a, b in shown], "face_found": round(face, 3),
            "closed_at_or_under": CLOSED, "window_frames": list(WINDOW), "checked": len(rows), "misses": misses,
            "passes": passes, "rule": f"fails with {FAIL_MISSES} misses, when its only closure misses, or with a face "
                                      f"in under {MIN_FACE:.0%} of frames", "closures": rows}


def calibrate():
    """Measure step 0's repairs, derive CLOSED from t3g's closures, and write down what the rule makes of both."""
    tracks = {name: lip_gap(REPAIRS / f"{name}_sync2pro.mp4") for name, *_ in STEP0}
    name, start, duration, _ = STEP0[0]
    gap, fps = tracks[name]
    loose, _ = judge(gap, fps, start, closures(start, duration), closed=1.0)  # every frame counts: the minima
    derived = round(max(r["lowest"] for r in loose) * 1.1, 3)
    out = {"derived_closed": derived, "closed_in_use": CLOSED, "window_frames": list(WINDOW), "fail_misses": FAIL_MISSES,
           "clips": {}}
    for name, start, duration, by_eye in STEP0:
        gap, fps = tracks[name]
        r = check(REPAIRS / f"{name}_sync2pro.mp4", start, duration, gap=gap, fps=fps)
        at_rest = gap[np.isfinite(gap)]
        r.update(by_eye=by_eye, gap_percentiles={str(q): round(float(np.percentile(at_rest, q)), 4) for q in (5, 50, 95)})
        out["clips"][name] = r
        print(f"{name} ({by_eye} by eye): {r['checked'] - r['misses']}/{r['checked']} closures, "
              f"{'passes' if r['passes'] else 'fails'}")
        for row in r["closures"]:
            print(f"  {row['word']:6s} /{row['letter']}/ at {row['song_s']:.3f} s, frames {row['frames']}: {row['gaps']} "
                  f"-> {'closed' if row['closed'] else 'MISSED'}")
    if abs(derived - CLOSED) > 1e-9:
        print(f"NOTE: t3g gives CLOSED = {derived}, but {CLOSED} is in use; update the constant if that's intended")
    CALIBRATION.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(f"Wrote {rel(CALIBRATION)}")
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("clip", help="a repaired clip, or `calibrate`")
    p.add_argument("--start", type=float, help="song time of the clip's first frame")
    p.add_argument("--duration", type=float, help="the window's length in seconds")
    args = p.parse_args()
    if args.clip == "calibrate":
        calibrate()
        return
    if args.start is None or args.duration is None:
        p.error("--start and --duration are needed for a clip")
    r = check(Path(args.clip), args.start, args.duration)
    print(f"{r['clip']}: {r['checked'] - r['misses']}/{r['checked']} closures, face in {r['face_found']:.0%} of frames: "
          f"{'passes' if r['passes'] else 'FAILS'}")
    for row in r["closures"]:
        print(f"  {row['word']:10s} /{row['letter']}/ {row['song_s']:.3f} s: lowest gap {row['lowest']} "
              f"-> {'closed' if row['closed'] else 'missed'}")


if __name__ == "__main__":
    main()
