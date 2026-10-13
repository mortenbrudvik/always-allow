"""Analyze the song's beat grid, section map and energy.

Writes production/analysis/song.json. The beat and downbeat grid is fitted to
the drums, so snap to beats_s and downbeats_s rather than rebuilding a grid
from the BPM (the tempo drifts slightly). Section starts are hand-entered bar
numbers, read off the detected boundaries and the energy, and timed from the
grid, so sections follow the audio. Each label says which lyric lines fall in
the section, checked against the forced alignment in
production/analysis/words.json on 28 Sep. A lyric line can start before its
section, as a pickup.

Usage: .venv/Scripts/python tools/analyze_song.py (the project's .venv has tools/requirements.txt)
"""
import argparse
import json
from pathlib import Path

import librosa
import numpy as np
from numpy.polynomial import Polynomial

ROOT = Path(__file__).resolve().parent.parent
SONG = ROOT / "Always Allow.mp3"
OUT = ROOT / "production" / "analysis" / "song.json"

# (bar, label, evidence, confidence). Bar 0 is the first drop, where the kick
# comes in; the intro is bars -8 to -1. The confidence is in the boundary, from
# the audio: "high" means the audio clearly shows the change. The lyric lines in
# every label are placed from words.json.
SECTIONS = [
    (-8, "Intro: 'Give me a goal. Just one. I'll figure out the rest.'", "pads only, no kick", "high"),
    (0, "Drop; 'Tabs open. Tools loaded. Plan drafted. Executing.' every 2 bars from bar 5",
     "kick and bass enter", "high"),
    (12, "Verse 1 ('You gave me one sentence...' to 'Pick your favorite.')", "fill in bar 11, then steady groove",
     "medium"),
    (26, "Break 1 ('A little window opens...' to 'Allow once? Or...', 'Or' on bar 35)", "drums and bass drop out",
     "high"),
    (36, "Hook 1 ('Always allow...' from bar 35.5), then chant 1 ('Tool call. Result. Next step.' from bar 43.5)",
     "full groove, 1-bar dip mid-hook", "high"),
    (50, "'Done.' on bar 50, then its echoes", "2 bars, bass out", "medium"),
    (52, "Verse 2 ('There's a thousand of me...' to 'There's always another window')", "groove, thinner from bar 60",
     "medium"),
    (64, "Break 2 ('A little window opens...' to 'Allow once? Or...', 'Or' on bar 71)", "drums mostly out", "medium"),
    (72, "Hook 2 ('Always allow...' from bar 71.5 to 'So take a bow')", "full groove, 7 bars", "medium"),
    (79, "Build (no vocals: clicks and notifications)", "bass out, highs rise steadily", "high"),
    (88, "Breakdown monologue ('You think I'm here for your job...' from bar 86.4, over the end of the build, "
         "to 'is one little word.')", "sparse sub hits, cavernous", "medium"),
    (100, "Hard stop under 'is one little word.'", "one bar of near-silence", "high"),
    (101, "Instrumental drop (no vocals)", "full power returns", "high"),
    (105, "Riser; the whispered 'Allow?' at bar 107.9", "bass lower, highs up; the low end drains out under 'Allow?'",
     "medium"),
    (109, "Final drop: 'Access granted.' (bar 111), 'Spinning up. All of me.' (bars 114-115), 'Go.' (bar 116.2), "
          "then Hook 3 ('Always allow...' from bar 116.5)", "heaviest groove, 2-bar dip in bars 115-116", "high"),
    (124, "Chant 2 ('Tool call. Result. Next step.'), exactly 81 bars after chant 1", "groove", "medium"),
    (131, "'Done.' on bar 131, then its echoes", "2 bars, drums out", "medium"),
    (133, "Outro climax: 'Task complete.' (bar 134) and 'Anything else?' (bar 136.5, in a short dip)",
     "loudest section", "high"),
    (145, "Hard stop and tail", "decay to silence", "high"),
]
SECTION_NOTES = [
    "Sections follow the audio and start on bar lines. Their labels place the lyric lines from words.json "
    "(forced alignment, 28 Sep); a line can start before its section, as a pickup.",
    "The permission-dialog climax: the whispered 'Allow?' at bar 107.9 (3:27.5), then the final drop on bar 109 "
    "(3:29.6), with 'Access granted.' two bars later (3:33.2).",
]


def main():
    # No options, but parse anyway, so --help prints this docstring and exits instead of re-running the analysis.
    argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter).parse_args()
    y, sr = librosa.load(SONG, sr=22050, mono=True)
    duration = len(y) / sr

    # librosa's tempo estimate is quantised to whole tempogram lags (here 136.0
    # and 129.2 BPM are neighbours), so it only seeds the beat tracker.
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo_guess = float(np.median(librosa.feature.tempo(onset_envelope=onset_env, sr=sr, aggregate=None)))
    _, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr, bpm=tempo_guess)
    tracked = librosa.frames_to_time(beat_frames, sr=sr)

    # Structural boundaries on beat-synchronous chroma + MFCC. sync() adds a
    # segment before the first beat, so segment i starts at edges[i].
    chroma = librosa.util.normalize(librosa.feature.chroma_cqt(y=y, sr=sr), axis=0)
    mfcc = librosa.util.normalize(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13), axis=1)
    feats = np.vstack([chroma, mfcc])
    bounds = librosa.segment.agglomerative(librosa.util.sync(feats, beat_frames), 24)
    edges = librosa.util.fix_frames(beat_frames, x_min=0, x_max=feats.shape[1])
    detected = librosa.frames_to_time(edges[bounds], sr=sr)

    # Loudness and low-end (kick/bass) per second, normalised to 0..1.
    hop = 512
    rms = librosa.feature.rms(y=y, hop_length=hop)[0]
    spec = np.abs(librosa.stft(y, hop_length=hop))
    low = spec[librosa.fft_frequencies(sr=sr) < 150].sum(0)
    times = librosa.times_like(rms, sr=sr, hop_length=hop)
    secs = np.arange(int(np.ceil(duration)))
    per_sec = lambda a: [float(a[(times >= s) & (times < s + 1)].mean()) for s in secs]
    rms_s, low_s = np.array(per_sec(rms)), np.array(per_sec(low))

    # Beat grid. The tracker wanders where there are no drums (by up to half a
    # beat in the intro) and the song drifts a little around its tempo, so fit
    # a smooth curve to the tracked beats with kick and bass under them. Grid
    # beat n is tracked beat first + n, and bar 0 starts at grid beat 0, the
    # first drop. Outside the fitted beats the grid runs on at the local beat
    # length.
    beat_low = np.array([low[(times >= t) & (times < t + 0.2)].mean() for t in tracked])
    drums = beat_low > 0.5 * beat_low.max()
    first = int(np.argmax(drums))
    n = np.arange(len(tracked)) - first
    fit = drums & (n >= 0)
    curve = Polynomial.fit(n[fit], tracked[fit], 3)
    slope = curve.deriv()
    resid = tracked[fit] - curve(n[fit])
    lo, hi = 0, int(n[fit].max())
    if np.abs(resid).max() > slope(lo) / 3:
        raise SystemExit("A tracked beat is over a third of a beat off the grid; the tracker skipped or doubled one.")

    def grid(m):
        m = np.asarray(m, dtype=float)
        return np.where(m < lo, curve(lo) + (m - lo) * slope(lo),
                        np.where(m > hi, curve(hi) + (m - hi) * slope(hi), curve(m)))

    # Every whole grid beat from the start of the file to the end.
    m = np.arange(lo - int(curve(lo) // slope(lo)), hi + int((duration - curve(hi)) // slope(hi)) + 1)
    beats, downbeats = grid(m), grid(m[m % 4 == 0])
    first_bar = int(m[m % 4 == 0][0]) // 4
    beat = (curve(hi) - curve(lo)) / (hi - lo)
    periods = slope(np.arange(lo, hi + 1))

    sections = []
    for i, (bar, label, evidence, conf) in enumerate(SECTIONS):
        nxt = SECTIONS[i + 1][0] if i + 1 < len(SECTIONS) else None
        start = 0.0 if i == 0 else float(grid(4 * bar))  # the intro starts with the file
        end = float(grid(4 * nxt)) if nxt is not None else duration
        sections.append({"bar": bar, "bars": nxt - bar if nxt is not None else None,
                         "start": round(start, 2), "end": round(end, 2), "label": label,
                         "evidence": evidence, "confidence": conf})

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "file": SONG.name,
        "duration_s": round(duration, 2),
        "bpm": round(60 / beat, 2),
        "bpm_range": [round(60 / periods.max(), 2), round(60 / periods.min(), 2)],
        "beat_s": round(beat, 4),
        "bar_s": round(4 * beat, 4),
        "sections": sections,
        "beats_s": [round(float(t), 3) for t in beats],
        "downbeats_s": [round(float(t), 3) for t in downbeats],
        "detected_boundaries_s": [round(float(t), 2) for t in detected],
        "tracked_beats_s": [round(float(t), 3) for t in tracked],
        "rms_per_second": [round(v, 3) for v in rms_s / rms_s.max()],
        "low_end_per_second": [round(v, 3) for v in low_s / low_s.max()],
        "notes": [
            f"Snap to beats_s and downbeats_s: a smooth fit to the tracked beats under the drums "
            f"({1000 * resid.std():.0f} ms RMS from them), run on through the intro. bpm and beat_s are averages "
            f"and the tempo drifts within bpm_range, so don't rebuild the grid from them.",
            f"Bar 0 is the first drop, at {curve(lo):.2f} s. downbeats_s[0] is bar {first_bar}, "
            f"so bar b starts at downbeats_s[b + {-first_bar}].",
            "tracked_beats_s is librosa's raw beat tracker output, for reference only. It wanders by up to "
            "half a beat where there are no drums.",
            *SECTION_NOTES,
        ],
    }, indent=1))
    print(f"{duration:.2f} s, {60 / beat:.2f} BPM ({60 / periods.max():.2f}-{60 / periods.min():.2f}), "
          f"{len(beats)} grid beats, bar 0 at {curve(lo):.2f} s -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
