"""Does a Seedance clip still speak our vocal? (PLAN.md phase 0c, BRIEF.md step 0)

Seedance copies the audio reference into its own soundtrack, and the mouth follows that
soundtrack, so where the soundtrack drifts from the reference the lip sync drifts with it
(research/escape-velocity.md). This compares the soundtrack a clip came back with against the
vocal window it was given:

- the match over time: the cosine similarity of log-mel patches (40 mel bands by 0.4 s, centred
  on each moment, normalised per band and mean-removed, so it's a correlation), at the best lag;
- the local offset: that best lag, from cross-correlating the patches over +-0.5 s;
- the threshold, from a null comparison: the same soundtrack against other stretches of the
  vocal stem that hold different words. It's the 99th percentile of their best-lag matches over
  their speaking frames, so the data sets it, never the ear.

A moment is in sync when its match clears the threshold and its offset is within one frame at
24 fps (42 ms). Positive offsets mean the clip's soundtrack, and so its mouth, is late. Speaking
time is where the reference vocal is active: the spans of its words in
production/analysis/words.json, with gaps under 0.25 s inside a line bridged (the stem's reverb
tails would fool a level threshold); where the window has no words, the vocal's level decides.

The report gives the fraction of speaking seconds in sync, the first point where sync is lost
(the first out-of-sync run of at least 0.1 s of speech), the last eighth note before it (where
BRIEF.md cuts for a cover), the global offset, the best whole-frame slip, and per-word results.
The plot has four panels: our vocal's spectrogram with the words, the clip's soundtrack under
it, the match against the threshold, and the local offset.

Usage, with the project's .venv:
  .venv/Scripts/python tools/avsync.py CLIP.mp4 --start 168.9 --duration 6
  .venv/Scripts/python tools/avsync.py CLIP.mp4 --start 168.9 --duration 6 --out DIR --name t1
  .venv/Scripts/python tools/avsync.py --self-test     # synthetic checks on the real stem; no API

CLIP is anything ffmpeg reads with an audio track. --start is the song time of the clip's first
frame, which is the start of the audio window it was given. The plot and the report go to --out
(default: next to the clip) as NAME.avsync.png and NAME.avsync.json.
"""
import argparse
import bisect
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
VOCALS = ROOT / "production" / "stems" / "vocals.mp3"
MASTER = ROOT / "Always Allow.mp3"
WORDS = ROOT / "production" / "analysis" / "words.json"
SONG = ROOT / "production" / "analysis" / "song.json"

SR = 16000
HOP = 80                 # 5 ms frames
FRAME_S = HOP / SR
N_FFT = 512
N_MELS = 40
FMIN, FMAX = 80.0, 7600.0
FLOOR_DB = 70.0          # log-mel floor, below each signal's own peak
PATCH_S = 0.4
MAX_LAG_S = 0.5
FPS = 24
TOL_S = 1 / FPS          # in sync: within one frame
NULL_PCT = 99.0
NULL_STRETCHES = 16
BRIDGE_S = 0.25
EDGE_S = 0.05            # the match also sees this much either side of the speech
MIN_LOSS_S = 0.1
LEVEL_DB = 15.0          # fallback speaking test without words: within this of the window's peak


def rel(path):
    path = Path(path).resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()


def norm(token):
    return re.sub(r"[^a-z0-9]", "", token.lower())


# ---- audio ---------------------------------------------------------------------------------

def stream_start(path, kind):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", f"{kind}:0", "-show_entries",
                          "stream=start_time", "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout
    try:
        return float(out.strip().splitlines()[0])
    except (ValueError, IndexError):
        return None


def decode(path):
    """The first audio track as mono float64 at SR, through ffmpeg. For a video, sample 0 is its
    first frame: if the audio track starts before or after the picture, it's shifted to line up."""
    cmd = ["ffmpeg", "-v", "error", "-nostdin", "-i", str(path), "-map", "0:a:0", "-ac", "1", "-ar", str(SR),
           "-f", "f32le", "-"]
    y = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, dtype="<f4").astype(np.float64)
    v0, a0 = stream_start(path, "v"), stream_start(path, "a")
    if v0 is not None and a0 is not None:
        shift = int(round((a0 - v0) * SR))
        y = np.concatenate([np.zeros(shift), y]) if shift > 0 else y[-shift:]
    return y


_stems = {}


def stem(path=VOCALS):
    """The whole stem, decoded once."""
    key = Path(path).resolve()
    if key not in _stems:
        _stems[key] = decode(path)
    return _stems[key]


def cut(y, start, duration):
    a = int(round(start * SR))
    n = int(round(duration * SR))
    out = np.zeros(n)
    part = y[max(a, 0):a + n]
    out[max(-a, 0):max(-a, 0) + len(part)] = part
    return out


def fit(y, duration):
    """Trim or zero-pad to exactly `duration` seconds."""
    n = int(round(duration * SR))
    return y[:n] if len(y) >= n else np.concatenate([y, np.zeros(n - len(y))])


# ---- features and matching ------------------------------------------------------------------

def logmel(y):
    import librosa
    power = np.abs(librosa.stft(y, n_fft=N_FFT, hop_length=HOP, center=True)) ** 2
    mel = librosa.feature.melspectrogram(S=power, sr=SR, n_mels=N_MELS, fmin=FMIN, fmax=FMAX)
    db = 10 * np.log10(np.maximum(mel, 1e-12))
    return np.maximum(db, db.max() - FLOOR_DB)


def standardise(db):
    """Per band, zero mean and unit variance over the window (a floor of 1 dB keeps an empty band
    from turning its noise into signal)."""
    return (db - db.mean(1, keepdims=True)) / np.maximum(db.std(1, keepdims=True), 1.0)


def box(x, h):
    c = np.concatenate([[0.0], np.cumsum(x)])
    i = np.arange(len(x))
    return c[np.clip(i + h + 1, 0, len(x))] - c[np.clip(i - h, 0, len(x))]


def match_curves(R, T, use, patch=PATCH_S, max_lag=MAX_LAG_S):
    """corr[l, t]: the correlation between R's patch centred on frame t and T's patch centred on
    frame t + lags[l], over the patch's frames where `use` is set (the reference speaking, so
    sound around the voice doesn't count) and T exists. NaN where that's under MIN_LOSS_S of
    frames or a patch is flat."""
    bands, n = R.shape
    m = T.shape[1]
    h = int(round(patch / FRAME_S / 2))
    lags = np.arange(-int(round(max_lag / FRAME_S)), int(round(max_lag / FRAME_S)) + 1)
    use = use.astype(float)
    rs, rss = (R * use).sum(0), (R * R * use).sum(0)
    corr = np.full((len(lags), n), np.nan)
    for k, lag in enumerate(lags):
        idx = np.arange(n) + lag
        ok = (idx >= 0) & (idx < m)
        Ts = np.zeros((bands, n))
        Ts[:, ok] = T[:, idx[ok]] * use[ok]
        v = ok * use
        cnt = box(v, h) * bands
        sx, sxx = box(rs * ok, h), box(rss * ok, h)
        sy, syy = box(Ts.sum(0), h), box((Ts * Ts).sum(0), h)
        sxy = box((R * Ts).sum(0), h)
        with np.errstate(invalid="ignore", divide="ignore"):
            var = (sxx - sx * sx / cnt) * (syy - sy * sy / cnt)
            c = (sxy - sx * sy / cnt) / np.sqrt(var)
        c[(cnt < bands * MIN_LOSS_S / FRAME_S) | ~(var > 1e-9)] = np.nan
        corr[k] = c
    return lags, corr


def widen(mask, s=EDGE_S):
    """The mask grown by s on each side, so a word's onset edge is part of its patch."""
    k = int(round(s / FRAME_S))
    return box(mask.astype(float), k) > 0


def best_lag(lags, corr):
    """Per frame: the best match and its lag in seconds, refined between lags by a parabola."""
    filled = np.where(np.isnan(corr), -np.inf, corr)
    k = filled.argmax(0)
    cols = np.arange(corr.shape[1])
    best = corr[k, cols]
    lag = lags[k].astype(float)
    inner = (k > 0) & (k < len(lags) - 1)
    y0 = np.where(inner, filled[np.clip(k - 1, 0, None), cols], np.nan)
    y2 = np.where(inner, filled[np.clip(k + 1, None, len(lags) - 1), cols], np.nan)
    with np.errstate(invalid="ignore", divide="ignore"):
        den = y0 - 2 * best + y2
        step = np.where(np.isfinite(den) & (den < 0), 0.5 * (y0 - y2) / den, 0.0)
    lag += np.clip(np.nan_to_num(step), -0.5, 0.5)
    return best, lag * FRAME_S


# ---- words, speech and the beat grid ----------------------------------------------------------

def load_words():
    data = json.loads(WORDS.read_text(encoding="utf-8"))
    return [w for line in data["lines"] for w in line["words"]], data["lines"]


def window_words(words, start, duration):
    return [w for w in words if w["end"] > start and w["start"] < start + duration]


def spans(words, start, duration):
    """Speaking spans in window time: the words' spans, with short gaps bridged."""
    out = []
    for w in sorted(window_words(words, start, duration), key=lambda w: w["start"]):
        a, b = max(w["start"] - start, 0.0), min(w["end"] - start, duration)
        if out and a - out[-1][1] < BRIDGE_S:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def speaking_mask(n, words, start, duration, ref_db=None):
    t = np.arange(n) * FRAME_S
    mask = np.zeros(n, bool)
    found = spans(words, start, duration)
    for a, b in found:
        mask |= (t >= a) & (t < b)
    if not found and ref_db is not None:  # no words here: use the vocal's level
        level = 10 * np.log10(np.sum(10 ** (ref_db / 10), 0))
        mask = level > level.max() - LEVEL_DB
    return mask


def eighth_notes():
    beats = json.loads(SONG.read_text(encoding="utf-8"))["beats_s"]
    return sorted(beats + [(a + b) / 2 for a, b in zip(beats, beats[1:])])


def last_eighth_before(song_t, not_before):
    grid = eighth_notes()
    i = bisect.bisect_left(grid, song_t - 1e-6) - 1
    return grid[i] if i >= 0 and grid[i] >= not_before - 1e-6 else None


def null_starts(words, lines, start, duration, song_len, count=NULL_STRETCHES):
    """Stretches of the vocal for the null comparison: each starts just before a lyric line, holds
    enough speech, stays clear of the window, and shares no three-word run with it (the hooks and
    breaks repeat lines)."""
    own = [norm(w["word"]) for w in window_words(words, start, duration)]
    grams = {tuple(own[i:i + 3]) for i in range(len(own) - 2)}
    picks = []
    for line in lines:
        s = round(line["start"] - 0.25, 3)
        if s < 0 or s + duration > song_len or (s < start + duration + 0.5 and s + duration > start - 0.5):
            continue
        theirs = [norm(w["word"]) for w in window_words(words, s, duration)]
        if grams & {tuple(theirs[i:i + 3]) for i in range(len(theirs) - 2)}:
            continue
        if sum(b - a for a, b in spans(words, s, duration)) < 0.2 * duration:
            continue
        if picks and s - picks[-1] < duration / 2:
            continue
        picks.append(s)
    if len(picks) > count:
        picks = [picks[i] for i in sorted(set(np.linspace(0, len(picks) - 1, count).round().astype(int)))]
    return picks


# ---- the analysis ---------------------------------------------------------------------------

def compare(test, start, duration, ref_path=VOCALS, words=None, lines=None):
    """Compare a soundtrack (samples at SR, sample 0 = song time `start`) with the reference stem's
    window. Returns everything the report and the plot need."""
    if words is None:
        words, lines = load_words()
    ref = stem(ref_path)
    song_len = len(ref) / SR
    R_db, T_db = logmel(cut(ref, start, duration)), logmel(fit(test, duration))
    n = min(R_db.shape[1], T_db.shape[1])
    R_db, T_db = R_db[:, :n], T_db[:, :n]
    R, T = standardise(R_db), standardise(T_db)
    speaking = speaking_mask(n, words, start, duration, R_db)
    lags, corr = match_curves(R, T, widen(speaking), max_lag=MAX_LAG_S)
    match, offset = best_lag(lags, corr)

    nulls, pooled = null_starts(words, lines, start, duration, song_len), []
    for s in nulls:
        Rn_db = logmel(cut(ref, s, duration))[:, :n]
        sp = speaking_mask(n, words, s, duration, Rn_db)
        m_null, _ = best_lag(*match_curves(standardise(Rn_db), T, widen(sp), max_lag=MAX_LAG_S))
        pooled.append(m_null[sp & np.isfinite(m_null)])
    pooled = np.concatenate(pooled) if pooled else np.array([])
    # A silent or empty soundtrack matches nothing, the null stretches included: report no signal, not an error.
    no_signal = len(pooled) < 100
    threshold = 1.0 if no_signal else float(np.percentile(pooled, NULL_PCT))

    matched = np.isfinite(match) & (match >= threshold)
    in_sync = matched & (np.abs(offset) <= TOL_S)
    with np.errstate(invalid="ignore"):
        profile = np.nanmean(np.where(speaking, corr, np.nan), 1) if speaking.any() else np.full(len(lags), np.nan)
    g = int(np.nanargmax(profile)) if np.isfinite(profile).any() else None
    global_offset = None
    if g is not None:
        global_offset = float(lags[g] * FRAME_S)
        if 0 < g < len(lags) - 1 and np.isfinite(profile[g - 1:g + 2]).all():
            y0, y1, y2 = profile[g - 1:g + 2]
            if y0 - 2 * y1 + y2 < 0:
                global_offset += float(0.5 * (y0 - y2) / (y0 - 2 * y1 + y2) * FRAME_S)
    return dict(n=n, t=np.arange(n) * FRAME_S, R_db=R_db, T_db=T_db, match=match, offset=offset,
                speaking=speaking, matched=matched, in_sync=in_sync, threshold=threshold, no_signal=no_signal,
                null_starts=nulls, null_frames=int(len(pooled)), global_offset=global_offset,
                words=window_words(words, start, duration), start=start, duration=duration)


def runs(res):
    """Runs of speech with one sync state: (start frame, end frame, in sync). A pause in the
    speech ends a run."""
    sp, ok, out = res["speaking"], res["in_sync"], []
    i, n = 0, res["n"]
    while i < n:
        if not sp[i]:
            i += 1
            continue
        j = i
        while j < n and sp[j] and ok[j] == ok[i]:
            j += 1
        out.append((i, j, bool(ok[i])))
        i = j
    return out


def first_loss(res):
    """Where sync is first lost, in window time, and whether it was ever there: (time, from_start,
    late_start_s). Only runs of at least MIN_LOSS_S count. Sync is lost at the first out-of-sync run
    after an in-sync one; a clip that's never in sync is out of sync from the start of its speech.
    late_start_s is how much speech is out of sync before sync first holds."""
    need = int(round(MIN_LOSS_S / FRAME_S))
    t, held, late = res["t"], False, 0
    for i, j, ok in runs(res):
        if ok and j - i >= need:
            held = True
        elif not ok and not held:
            late += j - i
        elif not ok and j - i >= need:
            return float(t[i]), False, late * FRAME_S
    if held:
        return None, False, late * FRAME_S
    first_speech = np.flatnonzero(res["speaking"])
    return (float(t[first_speech[0]]) if len(first_speech) else None), True, late * FRAME_S


def summarise(res, name, clip=None):
    sp, ok = res["speaking"], res["in_sync"]
    speak_s = float(sp.sum() * FRAME_S)
    frac = float(ok[sp].mean()) if sp.any() else None
    loss, from_start, late = first_loss(res)
    cut_song = last_eighth_before(res["start"] + loss, res["start"]) if loss is not None and not from_start else None
    # The whole-frame slip nearest the global offset: placing the clip that many frames earlier
    # takes the constant part of the offset out.
    # An offset at the edge of the search means the real one is further out: no slip is suggested then.
    beyond = res["global_offset"] is not None and abs(res["global_offset"]) >= MAX_LAG_S - 2 * FRAME_S
    slip = int(round(res["global_offset"] * FPS)) if res["global_offset"] is not None and not beyond else 0
    slipped = res["matched"] & (np.abs(res["offset"] - slip / FPS) <= TOL_S)
    slip_frac = float(slipped[sp].mean()) if sp.any() else 0.0
    matched_sp = res["matched"] & sp
    detail = []
    for w in res["words"]:
        a, b = w["start"] - res["start"], w["end"] - res["start"]
        m = (res["t"] >= a) & (res["t"] < b)
        mm = m & res["matched"]
        detail.append({"word": w["word"], "start": w["start"], "end": w["end"],
                       "in_sync": round(float(ok[m].mean()), 3) if m.any() else None,
                       "offset_ms": round(float(np.median(res["offset"][mm]) * 1000), 1) if mm.any() else None,
                       "match": round(float(np.nanmean(res["match"][m])), 3) if m.any() else None})
    return {
        "name": name,
        "clip": rel(clip) if clip else None,
        "reference": {"file": rel(VOCALS), "start": res["start"], "end": round(res["start"] + res["duration"], 3)},
        "words": " ".join(w["word"] for w in res["words"]),
        "speaking_s": round(speak_s, 3),
        "in_sync_s": round(float((ok & sp).sum() * FRAME_S), 3),
        "in_sync_fraction": round(frac, 4) if frac is not None else None,
        "threshold": round(res["threshold"], 4),
        "no_signal": res["no_signal"],
        "null": {"percentile": NULL_PCT, "stretch_starts": res["null_starts"], "frames": res["null_frames"]},
        "first_loss": None if loss is None else {"clip_s": round(loss, 3), "song_s": round(res["start"] + loss, 3),
                                                 "from_start": from_start},
        "late_start_s": round(late, 3),
        "cut": None if cut_song is None else {"song_s": round(cut_song, 3), "clip_s": round(cut_song - res["start"], 3)},
        "global_offset_ms": None if res["global_offset"] is None else round(res["global_offset"] * 1000, 1),
        "offset_beyond_search": beyond,
        "median_offset_ms": round(float(np.median(res["offset"][matched_sp]) * 1000), 1) if matched_sp.any() else None,
        "best_slip": {"frames_earlier": slip, "in_sync_fraction": round(slip_frac, 4)},
        "per_word": detail,
        "params": {"sr": SR, "hop_s": FRAME_S, "n_mels": N_MELS, "fmin": FMIN, "fmax": FMAX, "patch_s": PATCH_S,
                   "max_lag_s": MAX_LAG_S, "tolerance_s": round(TOL_S, 4), "bridge_s": BRIDGE_S,
                   "min_loss_s": MIN_LOSS_S},
    }


# ---- the plot -------------------------------------------------------------------------------

def plot(res, report, path, test_label="the clip's soundtrack"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import librosa

    t, dur, start = res["t"], res["duration"], res["start"]
    sp, matched, ok = res["speaking"], res["matched"], res["in_sync"]
    green, orange, red, blue = "#009E73", "#E69F00", "#D55E00", "#0072B2"
    fig, ax = plt.subplots(4, 1, figsize=(13, 10.5), sharex=True, layout="constrained",
                           gridspec_kw={"height_ratios": [3, 3, 2, 2]})
    freqs = librosa.mel_frequencies(n_mels=N_MELS + 2, fmin=FMIN, fmax=FMAX)[1:-1]
    ticks = [np.argmin(np.abs(freqs - f)) for f in (200, 500, 1000, 2000, 4000)]
    for a, db, label in ((ax[0], res["R_db"], "our vocal (production/stems/vocals.mp3)"), (ax[1], res["T_db"], test_label)):
        a.imshow(db, origin="lower", aspect="auto", cmap="magma", extent=[0, t[-1] + FRAME_S, 0, N_MELS],
                 vmin=db.max() - FLOOR_DB, vmax=db.max(), interpolation="nearest")
        a.set_yticks([k + 0.5 for k in ticks], ["200", "500", "1k", "2k", "4k"])
        a.set_ylabel("Hz")
        a.set_title(label, loc="left", fontsize=10)
    for i, w in enumerate(res["words"]):
        x = w["start"] - start
        if 0 <= x < dur:
            for a in ax[:2]:
                a.axvline(x, color="white", lw=0.6, alpha=0.5)
            ax[0].text(x + 0.012, N_MELS - (2.2 if i % 2 == 0 else 6.2), w["word"], color="white", fontsize=9,
                       va="top", ha="left", fontweight="bold")
    for a in ax[2:]:
        for s, e in spans(res["words"], start, dur) or []:
            a.axvspan(s, e, color="0.93", zorder=0)
    ax[2].plot(t, res["match"], color="0.55", lw=0.8, label="best-lag match")
    for mask, colour, label in ((sp & ok, green, "speaking, in sync"),
                                (sp & matched & ~ok, orange, "speaking, matched but offset > 42 ms"),
                                (sp & ~matched, red, "speaking, no match")):
        if mask.any():
            ax[2].scatter(t[mask], np.nan_to_num(res["match"][mask], nan=-0.2), s=4, color=colour, label=label, zorder=3)
    ax[2].axhline(res["threshold"], color=blue, ls="--", lw=1.2,
                  label=f"threshold {res['threshold']:.2f} (null, {NULL_PCT:g}th pct)")
    ax[2].set_ylim(-0.25, 1.02)
    ax[2].set_ylabel("match")
    ax[2].legend(loc="lower left", bbox_to_anchor=(0, 1.0), fontsize=8, ncol=5, frameon=False, borderaxespad=0.2)
    off_ms = res["offset"] * 1000
    show = matched & sp
    lim = max(125.0, min(MAX_LAG_S * 1000, 1.15 * np.abs(off_ms[show]).max())) if show.any() else 125.0
    ax[3].axhspan(-TOL_S * 1000, TOL_S * 1000, color=green, alpha=0.15, lw=0, label="±1 frame (42 ms)")
    ax[3].axhline(0, color="0.5", lw=0.6)
    faint = matched & ~sp
    ax[3].scatter(t[faint], off_ms[faint], s=3, color="0.75", label="matched, not speaking")
    for mask, colour, label in ((show & ok, green, "in sync"), (show & ~ok, orange, "offset out of tolerance")):
        if mask.any():
            ax[3].scatter(t[mask], np.clip(off_ms[mask], -lim, lim), s=5, color=colour, label=label, zorder=3)
    ax[3].set_ylim(-lim, lim)
    ax[3].set_ylabel("offset, ms\n(+ = clip late)")
    ax[3].set_xlabel(f"clip time, s (song time = clip time + {start:g} s)")
    ax[3].legend(loc="lower left", bbox_to_anchor=(0, 1.0), fontsize=8, ncol=5, frameon=False, borderaxespad=0.2)
    if report["first_loss"]:
        x = report["first_loss"]["clip_s"]
        for a in ax:
            a.axvline(x, color=red, ls="--", lw=1.4)
        ax[2].text(x + 0.02, 0.95, "never in sync" if report["first_loss"]["from_start"] else f"sync lost {x:.2f} s",
                   color=red, fontsize=9, va="top")
    if report["cut"]:
        x = report["cut"]["clip_s"]
        for a in ax:
            a.axvline(x, color=blue, ls=":", lw=1.4)
        ax[2].text(x - 0.02, -0.2, f"cut {x:.3f} s", color=blue, fontsize=9, va="bottom", ha="right")
    top = ax[0].secondary_xaxis("top", functions=(lambda x: x + start, lambda x: x - start))
    top.set_xlabel("song time, s")
    frac = report["in_sync_fraction"]
    go = report["global_offset_ms"]
    fig.suptitle(f"{report['name']}: {'-' if frac is None else f'{frac:.0%}'} of {report['speaking_s']:.2f} speaking s in sync"
                 f"   |   threshold {report['threshold']:.2f} from {len(res['null_starts'])} null stretches"
                 f"   |   global offset {'-' if go is None else f'{go:+.0f} ms'}", fontsize=12, x=0.01, ha="left")
    ax[0].set_xlim(0, dur)
    fig.savefig(path, dpi=110)
    plt.close(fig)


def analyze(clip, start, duration, name=None, out=None, test=None, test_label=None):
    """Compare `clip`'s soundtrack (or the samples `test`) with the vocal window, write the plot and
    the report, and return the report."""
    clip = Path(clip) if clip else None
    name = name or (clip.stem if clip else "test")
    out = Path(out) if out else clip.parent
    out.mkdir(parents=True, exist_ok=True)
    res = compare(decode(clip) if test is None else test, start, duration)
    report = summarise(res, name, clip)
    png = out / f"{name}.avsync.png"
    report["plot"] = rel(png)
    plot(res, report, png, test_label or (f"the clip's soundtrack ({clip.name})" if clip else "test soundtrack"))
    (out / f"{name}.avsync.json").write_text(json.dumps(report, indent=1))
    return report


def line(report):
    """The report in one line."""
    frac, loss, cut_at, slip = report["in_sync_fraction"], report["first_loss"], report["cut"], report["best_slip"]
    offset = report["global_offset_ms"]
    if report.get("no_signal"):
        return f"{report['name']}: no signal: the soundtrack matches nothing, not even the null stretches"
    parts = [f"{report['name']}: " + ("-" if frac is None else f"{frac:.0%}")
             + f" of {report['speaking_s']:.2f} speaking s in sync",
             f"threshold {report['threshold']:.2f}",
             "global offset " + ("-" if offset is None else f"{offset:+.0f} ms")
             + (f" (at the ±{MAX_LAG_S:g} s search limit: further out)" if report.get("offset_beyond_search") else ""),
             "no sync loss" if loss is None else "out of sync from the start" if loss["from_start"]
             else f"sync lost at {loss['clip_s']:.2f} s (song {loss['song_s']:.2f})"]
    if report["late_start_s"]:
        parts.append(f"{report['late_start_s']:.2f} s of speech before sync first holds")
    if cut_at:
        parts.append(f"cut at {cut_at['clip_s']:.3f} s (song {cut_at['song_s']:.3f})")
    parts.append(f"slip {slip['frames_earlier']:+d} frames -> {slip['in_sync_fraction']:.0%}")
    return "; ".join(parts)


# ---- self-test ------------------------------------------------------------------------------

def self_test(out):
    """Synthetic soundtracks with known answers, made from the real stem around the step 0 window."""
    import librosa
    import scipy.signal
    out.mkdir(parents=True, exist_ok=True)
    start, dur = 168.9, 6.0
    ref = stem()
    R = cut(ref, start, dur)

    def delayed(y, s):
        k = int(round(s * SR))
        return np.concatenate([np.zeros(k), y])[:len(y)]

    def spliced(y, at, gap):
        a = int(round(at * SR))
        return np.concatenate([y[:a], np.zeros(int(round(gap * SR))), y[a:]])[:len(y)]

    rng = np.random.default_rng(0)
    b, a = scipy.signal.butter(4, 3500 / (SR / 2))
    lowpassed = scipy.signal.lfilter(b, a, R)
    noisy = 0.5 * lowpassed + rng.normal(0, np.sqrt(np.mean(lowpassed ** 2)) * 0.5 * 10 ** (-15 / 20), len(R))
    with tempfile.TemporaryDirectory() as tmp:
        wav, mp4 = Path(tmp) / "r.wav", Path(tmp) / "r.mp4"
        import soundfile
        soundfile.write(wav, R.astype(np.float32), SR)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=black:s=320x180:r=24", "-i", str(wav),
                        "-shortest", "-c:v", "libx264", "-c:a", "aac", "-b:a", "128k", "-ar", "44100", str(mp4)], check=True)
        round_trip = decode(mp4)

    cases = [
        ("identical", R, lambda r: r["in_sync_fraction"] >= 0.97 and abs(r["global_offset_ms"]) <= 5 and r["first_loss"] is None),
        ("late 25 ms", delayed(R, 0.025), lambda r: r["in_sync_fraction"] >= 0.95 and abs(r["global_offset_ms"] - 25) <= 5),
        ("late 100 ms", delayed(R, 0.100), lambda r: r["in_sync_fraction"] <= 0.05 and abs(r["global_offset_ms"] - 100) <= 6
         and r["first_loss"]["from_start"] and r["cut"] is None
         and r["best_slip"]["frames_earlier"] == 2 and r["best_slip"]["in_sync_fraction"] >= 0.9),
        ("drift 150 ms from 1.0 s", spliced(R, 1.0, 0.15), lambda r: r["first_loss"] is not None
         and 0.85 <= r["first_loss"]["clip_s"] <= 1.25 and r["cut"] is not None and r["cut"]["clip_s"] <= r["first_loss"]["clip_s"]),
        ("stretched 3 %", librosa.effects.time_stretch(R, rate=1 / 1.03)[:len(R)],
         lambda r: r["first_loss"] is not None and 1.0 <= r["first_loss"]["clip_s"] <= 1.9),
        ("other words (verse 1)", cut(ref, 36.0, dur), lambda r: r["in_sync_fraction"] <= 0.1),
        ("full mix", cut(stem(MASTER), start, dur), lambda r: r["in_sync_fraction"] >= 0.9 and r["first_loss"] is None),
        ("lowpass, noise, -6 dB", noisy, lambda r: r["in_sync_fraction"] >= 0.9),
        ("AAC in MP4, decoded", round_trip, lambda r: r["in_sync_fraction"] >= 0.95 and abs(r["global_offset_ms"]) <= 5),
    ]
    failed = 0
    for label, test, expect in cases:
        name = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
        report = analyze(None, start, dur, name=name, out=out, test=test, test_label=f"synthetic: {label}")
        good = expect(report)
        failed += not good
        print(f"{'PASS' if good else 'FAIL'}  {label:26s} {line(report)}")
    print(f"{len(cases) - failed}/{len(cases)} passed; plots in {rel(out)}")
    return failed == 0


def main():
    global MAX_LAG_S
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("clip", nargs="?", help="the clip (or audio) to check")
    p.add_argument("--start", type=float, help="song time of the clip's first frame (the audio window's start)")
    p.add_argument("--duration", type=float, help="the audio window's length in seconds (default: the clip's)")
    p.add_argument("--out", help="folder for the plot and report (default: next to the clip)")
    p.add_argument("--name", help="name for the outputs (default: the clip's file name)")
    p.add_argument("--max-lag", type=float, default=MAX_LAG_S, help=f"offsets searched, in s either way (default {MAX_LAG_S:g})")
    p.add_argument("--self-test", action="store_true", help="run the synthetic checks and exit")
    args = p.parse_args()
    MAX_LAG_S = args.max_lag
    if args.self_test:
        sys.exit(0 if self_test(Path(args.out) if args.out else ROOT / "production" / "tests" / "seedance" / "out" / "selftest") else 1)
    if not args.clip or args.start is None:
        p.error("give a clip and --start, or --self-test")
    clip = Path(args.clip)
    duration = args.duration or len(decode(clip)) / SR
    report = analyze(clip, args.start, duration, args.name, args.out)
    print(line(report))
    print(f"plot: {report['plot']}")


if __name__ == "__main__":
    main()
