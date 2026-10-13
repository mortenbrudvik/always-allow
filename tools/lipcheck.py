"""Which audio does a clip's mouth follow? (PLAN.md phase 0c)

avsync.py assumes a Seedance mouth follows Seedance's own soundtrack. This checks it from the
picture: MediaPipe's face landmarker gives the mouth opening per frame (the inner-lip gap,
landmarks 13-14, over the eye-corner distance, 33-263, and the jawOpen blendshape), and each lyric
line's opening is cross-correlated with the loudness of our vocal window and of the clip's own
soundtrack. In speech the sound peaks come 0-100 ms after the mouth opens, so the track whose lag
sits there is the one the mouth is animated to. Lines need a clear face and some mouth movement;
treat a correlation under about 0.3 as noise.

Usage, with the project's .venv (and tools/requirements-track.txt installed):
  .venv/Scripts/python tools/lipcheck.py CLIP.mp4 --start 168.9 --duration 6

The landmarker model is face_landmarker.task (float16) from
https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task
in %USERPROFILE%/.cache/mediapipe/.
"""
import argparse
import functools
import subprocess
from pathlib import Path

import numpy as np

import avsync

MODEL = Path.home() / ".cache" / "mediapipe" / "face_landmarker.task"
RATE = 100  # the envelopes and the upsampled mouth track, per second
NATURAL_S = 0.06  # where the sound usually sits after the mouth


def rgb_frames(path):
    """The video's RGB frames one at a time, its size and its frame rate: a clip is never held in memory whole."""
    info = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
                           "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True).stdout.strip().split(",")
    w, h = int(info[0]), int(info[1])
    num, den = (int(x) for x in info[2].split("/"))

    def frames():
        proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(path), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                stdout=subprocess.PIPE)
        try:
            while len(buf := proc.stdout.read(w * h * 3)) == w * h * 3:
                yield np.frombuffer(buf, np.uint8).reshape(h, w, 3)
        finally:
            proc.stdout.close()
            proc.wait()
    return frames(), (w, h), num / den


@functools.lru_cache(maxsize=4)  # --plot and the check both need the same clip's track: decode it once
def mouth(path):
    """Per frame: (lip gap, jawOpen), NaN where no face was found, and the frame rate."""
    import mediapipe as mp
    from mediapipe.tasks import python as mpp
    from mediapipe.tasks.python import vision
    if not MODEL.exists():
        raise SystemExit(f"Download the face landmarker model to {MODEL} (see the docstring).")
    frames, (w, h), fps = rgb_frames(path)
    opts = vision.FaceLandmarkerOptions(base_options=mpp.BaseOptions(model_asset_path=str(MODEL)),
                                        running_mode=vision.RunningMode.VIDEO, num_faces=1, output_face_blendshapes=True)
    out = []
    with vision.FaceLandmarker.create_from_options(opts) as lm:
        for i, f in enumerate(frames):
            r = lm.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(f)),
                                    int(round(i * 1000 / fps)))
            row = [np.nan, np.nan]
            if r.face_landmarks:
                p = np.array([(q.x * w, q.y * h) for q in r.face_landmarks[0]])
                row[0] = np.linalg.norm(p[13] - p[14]) / np.linalg.norm(p[33] - p[263])
                row[1] = next(b.score for b in r.face_blendshapes[0] if b.category_name == "jawOpen")
            out.append(row)
    return np.array(out, dtype=float).reshape(-1, 2), fps


def envelope(y):
    hop = avsync.SR // RATE
    n = len(y) // hop
    e = 20 * np.log10(np.sqrt(np.mean(y[:n * hop].reshape(n, hop) ** 2, 1)) + 1e-6)
    return np.maximum(e, e.max() - 40)


def lag(m, e, lo, hi, max_lag=0.6):
    """The lag (s) of the sound after the mouth that best lines them up over [lo, hi], and its correlation."""
    t = np.arange(int(lo * RATE), int(hi * RATE))
    t = t[t < len(m)]
    best = (-2.0, 0.0)
    for k in range(-int(max_lag * RATE), int(max_lag * RATE) + 1):
        idx = t + k
        ok = (idx >= 0) & (idx < len(e))
        if ok.sum() >= 20:
            best = max(best, (float(np.corrcoef(m[t[ok]], e[idx[ok]])[0, 1]), k / RATE))
    return best[1], best[0]


def check(clip, start, duration):
    track, fps = mouth(clip)
    t = np.arange(len(track)) / fps
    grid = np.arange(0, t[-1], 1 / RATE)
    ours = envelope(avsync.cut(avsync.stem(), start, duration))
    theirs = envelope(avsync.fit(avsync.decode(clip), duration))
    words, lines = avsync.load_words()
    rows = []
    for line in lines:
        a, b = line["words"][0]["start"] - start, line["words"][-1]["end"] - start
        if a < 0 or b > duration:
            continue
        for k, label in enumerate(("lip gap", "jawOpen")):
            ok = np.isfinite(track[:, k])
            if ok.sum() < 10:
                continue
            m = np.interp(grid, t[ok], track[ok, k])
            lo, hi = max(a - 0.2, 0), min(b + 0.3, duration - 0.1)
            l_ours, r_ours = lag(m, ours, lo, hi)
            l_theirs, r_theirs = lag(m, theirs, lo, hi)
            seen = np.isfinite(track[(t >= lo) & (t < hi), k]).mean() if ((t >= lo) & (t < hi)).any() else 0.0
            if seen < 0.8:
                follows = f"unclear (face found in {seen:.0%} of the line)"
            elif max(r_ours, r_theirs) < 0.3:
                follows = "unclear (r < 0.3)"
            else:
                follows = "its soundtrack" if abs(l_theirs - NATURAL_S) < abs(l_ours - NATURAL_S) else "our vocal"
            rows.append({"line": line["text"], "signal": label, "our_vocal_ms": round(l_ours * 1000),
                         "our_vocal_r": round(r_ours, 2), "soundtrack_ms": round(l_theirs * 1000),
                         "soundtrack_r": round(r_theirs, 2), "follows": follows})
    return {"clip": avsync.rel(clip), "face_found": round(float(np.isfinite(track[:, 0]).mean()), 3), "lines": rows}


def plot(clips, start, duration, dest):
    """Mouth opening over time for each (label, clip), under our vocal's loudness with its words shaded."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    env = envelope(avsync.cut(avsync.stem(), start, duration))
    words = avsync.window_words(avsync.load_words()[0], start, duration)
    fig, ax = plt.subplots(len(clips) + 1, 1, figsize=(13, 2.4 * (len(clips) + 1)), sharex=True, layout="constrained")
    ax[0].plot(np.arange(len(env)) / RATE, env, color="#333")
    ax[0].set_ylabel("our vocal, dB")
    for w in words:
        ax[0].text(w["start"] - start, env.max() + 1, w["word"], fontsize=9, va="bottom")
        for a in ax:
            a.axvspan(w["start"] - start, w["end"] - start, color="#0072B2", alpha=0.08)
    for a, (label, clip) in zip(ax[1:], clips):
        track, fps = mouth(clip)
        t = np.arange(len(track)) / fps
        a.plot(t, track[:, 0], color="#D55E00", label="lip gap")
        a.set_ylabel(label, fontsize=9)
        twin = a.twinx()
        twin.plot(t, track[:, 1], color="#009E73", alpha=0.7, label="jawOpen")
        a.legend(loc="upper left", fontsize=8)
        twin.legend(loc="upper right", fontsize=8)
    ax[-1].set_xlabel(f"clip time, s (song time = clip time + {start:g} s); blue bands are the words")
    ax[0].set_xlim(0, duration)
    fig.savefig(dest, dpi=100)
    plt.close(fig)
    return dest


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("clip")
    p.add_argument("--start", type=float, required=True, help="song time of the clip's first frame")
    p.add_argument("--duration", type=float, required=True, help="the audio window's length in seconds")
    p.add_argument("--plot", help="also save the mouth opening over time to this PNG")
    p.add_argument("--compare", help="another take of the same window to plot under it, e.g. before a repair")
    args = p.parse_args()
    if args.plot:
        takes = [("before", Path(args.compare))] if args.compare else []
        plot([*takes, (Path(args.clip).stem, Path(args.clip))], args.start, args.duration, args.plot)
    r = check(Path(args.clip), args.start, args.duration)
    print(f"{r['clip']}: face found in {r['face_found']:.0%} of frames. Sound after mouth (0-100 ms is natural):")
    for row in r["lines"]:
        print(f"  {row['signal']:8s} \"{row['line']}\": our vocal {row['our_vocal_ms']:+5d} ms (r={row['our_vocal_r']:.2f}), "
              f"its soundtrack {row['soundtrack_ms']:+5d} ms (r={row['soundtrack_r']:.2f}) -> follows {row['follows']}")


if __name__ == "__main__":
    main()
