"""The Seedance sync test (BRIEF.md step 0, PLAN.md phase 0c).

Three clips through OpenRouter, one per lip-sync test plate (the first frames of
production/tests/lipsync/clips/t1-t3.mp4), each given the vocal stem from 168.9 to 174.9 s, which
holds exactly "You think I'm here for your job. I'm here for your weekends." Then a cover: a 4 s
clip that starts from the best clip's frame at the cut (171.089 s, 2.189 s in), with the vocal from
the cut. Every result is checked with tools/avsync.py, for colour, and against its start image.
Request IDs, costs and results go to production/tests/seedance/sync_report.json, and every paid
call to production/ledger.csv. Media goes to production/tests/seedance/out/ (git-ignored).

Steps, with the project's .venv:
  .venv/Scripts/python tools/seedance_test.py prepare          # free: plates, audio, uploads, requests
  .venv/Scripts/python tools/seedance_test.py show [NAME ...]  # print the requests (no keys)
  .venv/Scripts/python tools/seedance_test.py submit t1 t2 t3  # paid: submit, poll, download, check
  .venv/Scripts/python tools/seedance_test.py collect          # wait for jobs already submitted
  .venv/Scripts/python tools/seedance_test.py cover --from t2  # free: build the cover request
  .venv/Scripts/python tools/seedance_test.py submit cover     # paid
  .venv/Scripts/python tools/seedance_test.py review           # the review page: clips over the song, plots
Add --mock to run a step against a fake API and fake uploads, in out/mock/ with its own ledger;
it never touches the real report or ledger.

Covers. Variant a is BRIEF.md's request: frame_images pins the first frame, with the plate and the
audio in input_references. OpenRouter's docs say that when both are sent the frame images take
priority and the references have no effect, which the cover's soundtrack will show. Variant b is
the one revision if a fails: no frame_images; the frame goes in as @Image2, and the prompt starts
"@Image2 as the first frame." (Seedance's own phrasing for its reference mode).

A job is submitted once and never resubmitted; one still running after 40 minutes is left on
OpenRouter, logged at its estimate, and picked up by `collect`.
"""
import argparse
import datetime
import hashlib
import html
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np

import avsync
import ledger
import openrouter_video as orv
import print_grade

ROOT = Path(__file__).resolve().parent.parent
TEST = ROOT / "production" / "tests" / "seedance"
LIPSYNC_CLIPS = ROOT / "production" / "tests" / "lipsync" / "clips"
SONG = ROOT / "Always Allow.mp3"
VOCALS = ROOT / "production" / "stems" / "vocals.mp3"
WORDS_JSON = ROOT / "production" / "analysis" / "words.json"

START, LENGTH = 168.9, 6      # BRIEF.md step 0
WORDS = "You think I'm here for your job. I'm here for your weekends."
CUT, COVER_LENGTH = 171.089, 4  # beat 382, in the silence after "job"
COVER_WORDS = "I'm here for your weekends."
PLATES = ["t1", "t2", "t3"]
CAP_USD = 10.0                # BRIEF.md: keep the whole test under $10
PASS_FRACTION = 0.8
POLL_S, TIMEOUT_S = 30, 40 * 60
ENDPOINT = "openrouter.ai/api/v1/videos"
REPAIR_ENDPOINT = "fal-ai/sync-lipsync/v2/pro"  # inputs checked on fal on 29 Sep 2026
REPAIR_USD_PER_S = 5 / 60                       # $5 a minute (PLAN.md section 6)
FAILED = {"failed", "cancelled", "expired", "rejected"}


def rel(path):
    return avsync.rel(path)


def now():
    return datetime.datetime.now().isoformat(timespec="seconds")


class Paths:
    def __init__(self, mock):
        self.mock = mock
        self.out = TEST / "out" / ("mock" if mock else "")
        self.report = self.out / "sync_report.json" if mock else TEST / "sync_report.json"
        self.ledger = self.out / "ledger.csv" if mock else ledger.LEDGER
        self.uploads = self.out / "uploads.json"
        for sub in ("plates", "audio", "clips", "avsync", "sheets", "review"):
            (self.out / sub).mkdir(parents=True, exist_ok=True)


# ---- media helpers ----------------------------------------------------------------------------

def run(cmd):
    """Run ffmpeg or ffprobe; on failure the error carries the tool's own message, not just its exit status."""
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode:
        raise RuntimeError(f"{Path(cmd[0]).name} failed: {r.stderr.decode(errors='replace').strip()[-400:]}")


def frame(video, index, dest):
    """Save frame `index` (0-based, in decode order) of a video as PNG."""
    run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vf", f"select=eq(n\\,{index})", "-frames:v", "1", str(dest)])
    return dest


def cut_audio(start, length, dest):
    """The vocal stem from `start` for `length` s, mono 16-bit WAV at the stem's 48 kHz. WAV, not MP3,
    so no encoder delay moves the words."""
    import soundfile
    y, sr = soundfile.read(VOCALS, dtype="float32", always_2d=True)
    a = int(round(start * sr))
    soundfile.write(dest, y[a:a + int(round(length * sr))].mean(1), sr, subtype="PCM_16")
    return dest


def probe(path):
    out = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
                                    capture_output=True, text=True, check=True).stdout)
    v = next((s for s in out["streams"] if s["codec_type"] == "video"), {})
    a = next((s for s in out["streams"] if s["codec_type"] == "audio"), {})
    num, den = (int(x) for x in v.get("r_frame_rate", "0/1").split("/"))
    return {"width": v.get("width"), "height": v.get("height"), "fps": num / den if den else None,
            "frames": int(v["nb_frames"]) if v.get("nb_frames") else None,
            "duration_s": float(out["format"].get("duration", 0)), "video_codec": v.get("codec_name"),
            "video_start_s": float(v.get("start_time", 0) or 0),
            "audio": None if not a else {"codec": a.get("codec_name"), "sample_rate": int(a.get("sample_rate", 0)),
                                         "channels": a.get("channels"), "start_s": float(a.get("start_time", 0) or 0)}}


def rgb_frames(path, width=160, height=90, fps=None, first=False):
    vf = (f"fps={fps}," if fps else "") + f"scale={width}:{height}"
    only = ["-frames:v", "1"] if first else []
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vf", vf, *only, "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, height, width, 3).astype(float) / 255


def saturation(frames):
    """Mean HSV saturation over the pixels that aren't near black."""
    hi, lo = frames.max(-1), frames.min(-1)
    lit = hi > 0.1
    return float(((hi - lo) / np.maximum(hi, 1e-6))[lit].mean()) if lit.any() else 0.0


def likeness(image, video):
    """How close the video's first frame is to an image: mean absolute difference (0-255) and PSNR."""
    a = rgb_frames(image, 320, 180, first=True)[0]
    b = rgb_frames(video, 320, 180, first=True)[0]
    mse = float(((a - b) ** 2).mean())
    return {"mean_abs_diff": round(float(np.abs(a - b).mean() * 255), 2),
            "psnr_db": round(10 * math.log10(1 / mse), 2) if mse > 0 else None}


def sheet(video, dest, every=1.0):
    run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vf", f"fps=1/{every},scale=426:240,tile=6x1",
         "-frames:v", "1", str(dest)])


# ---- the words -----------------------------------------------------------------------------

def window_text(start, length):
    """The lyric lines inside a window, joined. Every word of each line must be inside it."""
    lines = json.loads(WORDS_JSON.read_text(encoding="utf-8"))["lines"]
    inside = [ln for ln in lines if any(w["end"] > start and w["start"] < start + length for w in ln["words"])]
    for ln in inside:
        if ln["words"][0]["start"] < start or ln["words"][-1]["end"] > start + length:
            raise SystemExit(f"the window {start}-{start + length} s cuts the line {ln['text']!r}")
    return " ".join(ln["text"] for ln in inside)


def prompt(words, first_frame=None):
    lead = f"{first_frame} as the first frame. " if first_frame else ""
    return (f'{lead}@Image1 sings @Audio1. She lip-syncs to @Audio1 exactly, every word in time: "{words}" '
            "Close-up of the woman from @Image1, face to camera, deadpan. She looks straight into the lens and says "
            "the words calmly. Locked camera, no cuts, no head turns.")


def request(text, duration, images, audio, first_frame=None):
    body = {"model": orv.MODEL, "prompt": text, "duration": duration, "resolution": "720p", "aspect_ratio": "16:9",
            "generate_audio": True,
            "input_references": [*({"type": "image_url", "image_url": {"url": u}} for u in images),
                                 {"type": "audio_url", "audio_url": {"url": audio}}]}
    if first_frame:
        body["frame_images"] = [{"type": "image_url", "image_url": {"url": first_frame}, "frame_type": "first_frame"}]
    return body


# ---- uploads, report -------------------------------------------------------------------------

def upload(paths, file):
    cache = json.loads(paths.uploads.read_text(encoding="utf-8")) if paths.uploads.exists() else {}
    digest = hashlib.sha256(Path(file).read_bytes()).hexdigest()
    if digest not in cache:
        if paths.mock:
            url = f"https://mock.invalid/{digest[:12]}/{Path(file).name}"
        else:
            from envfile import load_env
            load_env()
            import fal_client
            url = fal_client.upload_file(str(file))
        cache[digest] = {"url": url, "file": rel(file), "uploaded": now()}
        paths.uploads.write_text(json.dumps(cache, indent=1), encoding="utf-8")
    return cache[digest]["url"]


def load(paths):
    if paths.report.exists():
        return json.loads(paths.report.read_text(encoding="utf-8"))
    return {"test": "BRIEF.md step 0 (PLAN.md phase 0c): the Seedance sync test",
            "window": {"start": START, "end": START + LENGTH, "words": WORDS, "source": rel(VOCALS)},
            "cover_cut": {"song_s": CUT, "clip_s": round(CUT - START, 3)},
            "pass_rule": "at least 2 of the 3 clips in sync (offset within 42 ms) for at least 80 % of their speaking "
                         "seconds and in colour; the cover accepted with the start frame and the audio together, and "
                         "in sync the same way",
            "clips": {}}


def save(paths, report):
    """Write the report through a temporary file, so a crash mid-write can't lose job IDs."""
    tmp = paths.report.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, paths.report)


def spent(report):
    """The test's spend so far: reported costs, and estimates for jobs not settled yet."""
    total = 0.0
    for entry in report["clips"].values():
        for a in entry["attempts"]:
            if a.get("cost_usd") is not None:
                total += a["cost_usd"]
            elif a["status"] not in FAILED:
                total += orv.estimate(entry["request"]["duration"])
        for rep in entry.get("repairs", []):
            if rep.get("cost_usd") is not None:
                total += rep["cost_usd"]
            elif rep.get("status") in ("submitting", "submitted", "running", "unknown"):
                total += REPAIR_USD_PER_S * entry["request"]["duration"]
    return total


def log_once(paths, report, rec, tool, model, endpoint, seconds, usd):
    """Log a cost to the ledger exactly once, even across a crash: the row's stamp goes into the report before the
    row goes into the ledger, and a rerun that finds the row doesn't write it again."""
    if rec.get("ledger_time"):
        return rec["ledger_time"]
    pending = rec.get("ledger_pending")
    if pending and ledger.has_row(pending, model, paths.ledger):
        rec["ledger_time"] = pending  # written just before a crash
    else:
        rec["ledger_pending"] = stamp = ledger.stamp_now()
        save(paths, report)
        rec["ledger_time"] = ledger.log(tool, model, endpoint, seconds, usd, paths.ledger, stamp=stamp)
    rec.pop("ledger_pending", None)
    save(paths, report)
    return rec["ledger_time"]


def in_flight(report):
    """What jobs that may bill but aren't in the ledger yet would cost, at their estimates. The ledger only
    learns a job's cost when it ends, so the $150 and $400 checks must add this to it."""
    total = 0.0
    for entry in report["clips"].values():
        for a in entry["attempts"]:
            if not a.get("ledger_time") and a["status"] not in orv.TERMINAL | FAILED:
                total += orv.estimate(entry["request"]["duration"])
        for rep in entry.get("repairs", []):
            if not rep.get("ledger_time") and rep.get("status") in ("submitting", "submitted", "running", "unknown"):
                total += REPAIR_USD_PER_S * entry["request"]["duration"]
    return total


# ---- steps ----------------------------------------------------------------------------------

def prepare(paths, args):
    start, length = args.start, args.length
    words = window_text(start, length)
    if (start, length) == (START, LENGTH) and words != WORDS:
        raise SystemExit(f"the words in the window changed: {words!r}")
    report = load(paths)
    audio = cut_audio(start, length, paths.out / "audio" / f"vocal_{start:.3f}-{start + length:.3f}.wav")
    audio_url = upload(paths, audio)
    names = []
    for name in PLATES:
        key = name + (args.suffix if args.suffix is not None else "g" if args.grade else "")
        names.append(key)
        entry = report["clips"].get(key)
        if entry and entry["attempts"]:
            print(f"{key}: already submitted; its request stays as sent")
            continue
        plate = frame(LIPSYNC_CLIPS / f"{name}.mp4", 0, paths.out / "plates" / f"{name}.png")
        source = plate
        if args.grade:  # the print look, so the face goes in stylised (see tools/print_grade.py)
            plate = print_grade.grade(plate, paths.out / "plates" / f"{name}_print_c{args.cell:g}.png", cell=args.cell)
        report["clips"][key] = {"plate": rel(plate), "plate_from": rel(LIPSYNC_CLIPS / f"{name}.mp4") + " frame 0",
                                "grade": {"tool": "tools/print_grade.py", "cell": args.cell, "source": rel(source)}
                                if args.grade else None,
                                "window": {"start": start, "end": round(start + length, 3)}, "words": words,
                                "audio": rel(audio), "request": request(prompt(words), length, [upload(paths, plate)], audio_url),
                                "attempts": []}
    save(paths, report)
    print(f"Requests written to {rel(paths.report)}")
    show(paths, argparse.Namespace(names=names))


def show(paths, args):
    report = load(paths)
    names = args.names or list(report["clips"])
    print(f"POST {orv.API}/videos   (headers: Authorization: Bearer <OPENROUTER_API_KEY from .env>, "
          "Content-Type: application/json)")
    for name in names:
        entry = report["clips"][name]
        print(f"\n--- {name}: {entry['window']['start']:.3f}-{entry['window']['end']:.3f} s, "
              f"about ${orv.estimate(entry['request']['duration']):.2f}")
        print(json.dumps(entry["request"], indent=2, ensure_ascii=False))


def client(paths):
    if paths.mock:
        return orv.Client(key="mock-key", transport=MockApi(paths))
    return orv.Client()


def submit(paths, args):
    report = load(paths)
    api = client(paths)
    try:
        for name in args.names:
            submit_one(paths, report, api, name, args.again)
    finally:  # whatever stopped the loop, every job already posted is polled and logged
        wait(paths, report, api)


def submit_one(paths, report, api, name, again):
    entry = report["clips"].get(name)
    if not entry:
        raise SystemExit(f"no request named {name}; run prepare (or cover) first")
    last = entry["attempts"][-1] if entry["attempts"] else None
    if last and last["status"] == "unknown":
        raise SystemExit(f"{name}: an earlier submission may have created a job ({last.get('error')}); check OpenRouter's "
                         "activity page before anything is resubmitted")
    if last and last["status"] not in FAILED:
        print(f"{name}: already submitted as {last.get('job_id', '(no job ID yet)')}; use collect")
        return
    if last and not again:
        raise SystemExit(f"{name} failed before; resubmitting costs money, so pass --again to do it on purpose")
    cost = orv.estimate(entry["request"]["duration"])
    ledger.check(cost + in_flight(report), paths.ledger)
    if spent(report) + cost > CAP_USD:
        raise SystemExit(f"{name}: the test has spent ${spent(report):.2f}; ${cost:.2f} more passes its ${CAP_USD:.0f} cap")
    attempt = {"submitted": now(), "status": "submitting"}
    entry["attempts"].append(attempt)
    save(paths, report)
    try:
        job = api.submit(entry["request"])
    except orv.ApiError as e:
        if 400 <= e.status < 500:  # refused before it started (a 4xx isn't billed)
            attempt.update(status="rejected", error=str(e))
            save(paths, report)
            print(f"{name}: rejected: {e}")
            return
        attempt.update(status="unknown", error=str(e))  # a 5xx can come after the job was created
        save(paths, report)
        raise SystemExit(f"{name}: submitting failed with {e}; the job may exist, so check OpenRouter before "
                         "anything is resubmitted")
    except Exception as e:  # the job may or may not exist: stop, don't guess
        attempt.update(status="unknown", error=repr(e))
        save(paths, report)
        raise SystemExit(f"{name}: submitting failed with {e!r}; the job may exist, so check OpenRouter before "
                         "anything is resubmitted")
    attempt.update(job_id=job["id"], generation_id=job.get("generation_id"), status=job.get("status", "pending"))
    save(paths, report)
    print(f"{name}: submitted as {job['id']} ({attempt['status']})")


def collect(paths, args):
    wait(paths, load(paths), client(paths))


def open_attempts(report):
    for name, entry in report["clips"].items():
        if entry["attempts"]:
            a = entry["attempts"][-1]
            if a.get("job_id") and a["status"] not in orv.TERMINAL | FAILED | {"unknown"} or (
                    a["status"] == "completed" and not a.get("checked")):
                yield name, entry, a


def wait(paths, report, api):
    """Poll every open job until it ends, settle its cost, and fetch and check it. A job that fails its download or
    checks, or runs past TIMEOUT_S, is set aside for `collect`, and the others carry on."""
    poll = 0.05 if paths.mock else POLL_S
    aside = set()
    while True:
        waiting = [(n, e, a) for n, e, a in open_attempts(report) if n not in aside]
        if not waiting:
            break
        for name, entry, a in waiting:
            if a["status"] != "completed":
                try:
                    st = api.status(a["job_id"])
                except Exception as e:  # a failed poll isn't a failed job
                    print(f"{name}: poll failed ({e}); trying again")
                    continue
                if st.get("status") != a["status"]:
                    print(f"{name}: {st.get('status')} ({now()})")
                a["status"], a["last_poll"] = st.get("status"), now()
                a["response"] = {k: v for k, v in st.items() if k not in ("unsigned_urls",)}
                if a["status"] in orv.TERMINAL:
                    settle(paths, report, entry, a, st)
                save(paths, report)  # the cost is in the ledger now; the report must know before anything else
            if a["status"] == "completed" and not a.get("checked"):
                try:
                    finish(paths, name, entry, a, api)
                    a.pop("finish_error", None)
                except Exception as e:  # the job is done and billed; collect can fetch and check it again
                    a["finish_error"] = repr(e)[:500]
                    aside.add(name)
                    print(f"{name}: download or checks failed ({e!r}); set aside, run collect to try again")
            save(paths, report)
        for name, entry, a in list(open_attempts(report)):
            if name in aside or a["status"] == "completed":
                continue
            if time.time() - datetime.datetime.fromisoformat(a["submitted"]).timestamp() > TIMEOUT_S:
                if not a.get("ledger_time"):  # it can still bill, so the ledger counts it now
                    cost = orv.estimate(entry["request"]["duration"])
                    a.update(cost_usd=cost, cost_source="estimate (still running)")
                    log_once(paths, report, a, "seedance", orv.MODEL, ENDPOINT, entry["request"]["duration"], cost)
                aside.add(name)
                print(f"{name}: still running after {TIMEOUT_S // 60} min; logged at its estimate, run collect later. "
                      "Nothing was resubmitted.")
        save(paths, report)
        if any(n not in aside for n, _, _ in open_attempts(report)):
            time.sleep(poll)


def settle(paths, report, entry, a, st):
    """Log the job's cost once it ends. Completed jobs are billed; failed ones only if they report a cost."""
    cost = (st.get("usage") or {}).get("cost")
    source = "usage.cost"
    if cost is None and a["status"] == "completed":
        cost, source = orv.estimate(entry["request"]["duration"]), "estimate"
    if cost is None:
        cost, source = 0.0, "none reported"
    logged_at = a.get("cost_usd")  # the estimate, if it was logged while it was slow
    a.update(cost_usd=round(cost, 4), cost_source=source, finished=now())
    if a["status"] != "completed":
        a["error"] = st.get("error") or st.get("failure_reason") or a["status"]
    if a.get("ledger_time"):
        if source == "usage.cost" and not ledger.replace(a["ledger_time"], orv.MODEL, cost, logged_at, paths.ledger):
            a["ledger_warning"] = f"couldn't find the estimate row of {a['ledger_time']} to set it to ${cost:.3f}"
            print(f"WARNING: {a['ledger_warning']}; fix production/ledger.csv by hand")
    elif cost > 0:
        log_once(paths, report, a, "seedance", orv.MODEL, ENDPOINT, entry["request"]["duration"], cost)


def finish(paths, name, entry, a, api):
    dest = paths.out / "clips" / f"{name}.mp4"
    if dest.exists():
        try:
            probe(dest)
        except subprocess.CalledProcessError:  # a broken earlier download: fetch it again
            dest.unlink()
    if not dest.exists():  # download beside it, check it's a video, then move it into place
        part = dest.with_name(dest.stem + ".part.mp4")
        api.download(a["job_id"], part)
        probe(part)
        os.replace(part, dest)
    a["file"] = rel(dest)
    a["video"] = info = probe(dest)
    image = ROOT / (entry.get("first_frame") or entry["plate"])
    plate_sat = saturation(rgb_frames(ROOT / entry["plate"]))
    clip_sat = saturation(rgb_frames(dest, fps=2))
    a["colour"] = {"saturation": round(clip_sat, 3), "plate_saturation": round(plate_sat, 3),
                   "in_colour": clip_sat >= 0.5 * plate_sat}
    a["start_frame"] = {"compared_with": rel(image), **likeness(image, dest)}
    sheet(dest, paths.out / "sheets" / f"{name}.png")
    if info["audio"] is None:
        a["avsync"] = None
        a["error"] = "no soundtrack, so the sync can't be measured"
    else:
        w = entry["window"]
        r = avsync.analyze(dest, w["start"], round(w["end"] - w["start"], 3), name=name, out=paths.out / "avsync")
        a["avsync"] = {k: r[k] for k in ("in_sync_fraction", "speaking_s", "in_sync_s", "threshold", "first_loss",
                                         "late_start_s", "cut", "global_offset_ms", "median_offset_ms", "best_slip",
                                         "per_word", "plot")}
        print("  " + avsync.line(r))
    frac = (a["avsync"] or {}).get("in_sync_fraction") or 0
    a["passes"] = bool(frac >= PASS_FRACTION and a["colour"]["in_colour"])
    a["checked"] = now()
    print(f"{name}: {'passes' if a['passes'] else 'fails'} "
          f"({frac:.0%} in sync, saturation {clip_sat:.2f} against the plate's {plate_sat:.2f}, "
          f"${a['cost_usd']:.3f} {a['cost_source']})")


def recheck(paths, args):
    """Run the checks again on clips already downloaded (after avsync.py changes, say). No API calls."""
    report = load(paths)
    if args.max_lag:
        avsync.MAX_LAG_S = args.max_lag
    for name in args.names or list(report["clips"]):
        entry = report["clips"][name]
        a = next((a for a in reversed(entry["attempts"]) if a.get("checked")), None)
        if a:
            finish(paths, name, entry, a, api=None)
            if args.max_lag:
                a["avsync"]["max_lag_s"] = args.max_lag
            save(paths, report)


class StillQueued(TimeoutError):
    """Cancelled while still in fal's queue: not billed."""


class StillRunning(TimeoutError):
    """Left running on fal at the timeout: it may bill, and its request ID can collect it later."""


def fal_run(endpoint, inputs, label, timeout, log, on_submit=None, request_id=None):
    """Submit to fal's queue once, or pick up `request_id`, and poll (the pattern in tools/lipsync_test.py).
    Returns (request id, result). on_submit(rid) runs as soon as the job exists, so its ID is saved before
    anything else can fail."""
    import fal_client
    if request_id:
        rid = request_id
        status_of = lambda: fal_client.status(endpoint, rid)  # noqa: E731
        result_of = lambda: fal_client.result(endpoint, rid)  # noqa: E731
        cancel = lambda: fal_client.cancel(endpoint, rid)  # noqa: E731
    else:
        handle = fal_client.submit(endpoint, arguments=inputs)
        rid = handle.request_id
        status_of, result_of, cancel = handle.status, handle.get, handle.cancel
        with log.open("a", encoding="utf-8") as f:
            f.write(f"{now()} {label} {endpoint} {rid}\n")
        if on_submit:
            on_submit(rid)
    print(f"  {label}: request {rid}")
    t0, last = time.monotonic(), None
    while time.monotonic() - t0 < timeout:
        try:
            status = status_of()
        except Exception as e:  # a failed poll isn't a failed job
            print(f"  {label}: poll failed ({e}); trying again")
            time.sleep(5)
            continue
        if isinstance(status, fal_client.Completed):
            return rid, result_of()
        state = "queued" if isinstance(status, fal_client.Queued) else "running"
        if state != last:
            print(f"  {label}: {state} ({time.monotonic() - t0:.0f} s)")
            last = state
        time.sleep(5)
    try:
        queued = isinstance(status_of(), fal_client.Queued)
    except Exception:
        queued = False
    if queued:
        cancel()
        raise StillQueued(f"{label}: still queued after {timeout:.0f} s, so cancelled (request {rid}, not billed)")
    raise StillRunning(f"{label}: still running after {timeout:.0f} s; request {rid} is left on fal and may bill")


def repair(paths, args):
    """Redraw a clip's mouth to our vocal with Sync lipsync-2-pro on fal (PLAN.md phase 4's repair), then check it
    from the picture with tools/lipcheck.py: the mouth should now follow our vocal."""
    if paths.mock:
        raise SystemExit("repair has no mock; it calls fal")
    from envfile import load_env
    load_env()
    import lipcheck
    report = load(paths)
    out = paths.out / "repair"
    out.mkdir(exist_ok=True)
    for name in args.names:
        entry = report["clips"][name]
        a = checked(entry)
        if not a:
            raise SystemExit(f"{name} has no finished clip to repair")
        reps = entry.setdefault("repairs", [])
        last = reps[-1] if reps else None
        if last and last.get("file"):
            print(f"{name}: already repaired; its result stays")
            continue
        if last and last.get("status") == "unknown":
            raise SystemExit(f"{name}: an earlier repair may have been created ({last.get('error')}); check fal's "
                             "request history before paying for another")
        w = entry["window"]
        length = round(w["end"] - w["start"], 3)
        cost = REPAIR_USD_PER_S * length
        resume = last if last and last.get("request_id") and last.get("status") in ("submitted", "running") else None
        if resume:
            rep, inputs = resume, resume["inputs"]
            print(f"{name}: picking up repair {rep['request_id']}")
        else:
            if last and last.get("status") == "failed" and not args.again:
                raise SystemExit(f"{name}: its last repair failed ({last.get('error')}); pass --again to pay for another")
            ledger.check(cost + in_flight(report), paths.ledger)
            if spent(report) + cost > CAP_USD:
                raise SystemExit(f"{name}: the test has spent ${spent(report):.2f}; ${cost:.2f} more passes its ${CAP_USD:.0f} cap")
            silent = out / f"{name}_video.mp4"  # the model's own audio is dropped before anything else sees it
            run(["ffmpeg", "-v", "error", "-y", "-i", str(ROOT / a["file"]), "-an", "-c:v", "copy", str(silent)])
            inputs = {"video_url": upload(paths, silent), "audio_url": upload(paths, ROOT / entry["audio"]),
                      "sync_mode": "cut_off"}
            rep = {"model": "sync-2-pro", "endpoint": REPAIR_ENDPOINT, "inputs": inputs, "submitted": now(),
                   "status": "submitting"}
            reps.append(rep)
            save(paths, report)

        def submitted(rid):
            rep.update(request_id=rid, status="submitted")
            save(paths, report)
        try:
            rid, result = fal_run(REPAIR_ENDPOINT, inputs, f"{name}/sync-2-pro", args.timeout, out / "requests.txt",
                                  on_submit=submitted, request_id=rep.get("request_id") if resume else None)
        except StillQueued as e:  # cancelled before it started: not billed, so a later run may simply try again
            rep.update(status="cancelled", error=str(e))
            save(paths, report)
            print(e)
            continue
        except StillRunning as e:  # it may bill: count it now, and collect it later by its request ID
            rep["status"] = "running"
            if not rep.get("ledger_time"):
                rep.update(cost_usd=round(cost, 4), cost_source="estimate (still running)")
                log_once(paths, report, rep, "lipsync", "sync-2-pro", REPAIR_ENDPOINT, length, cost)
            save(paths, report)
            print(f"{e}; run repair {name} again later to collect it")
            continue
        except Exception as e:
            if rep.get("request_id"):  # the job exists: keep it resumable
                rep.update(status="running", poll_error=repr(e)[:300])
            else:  # it failed on submission and may or may not exist: don't guess
                rep.update(status="unknown", error=repr(e)[:300])
            save(paths, report)
            raise
        rep["status"] = "completed"
        if not rep.get("ledger_time"):  # done means billed: log it before the download can fail
            rep.update(cost_usd=round(cost, 4), cost_source="estimate from $5/min (PLAN.md section 6)")
            log_once(paths, report, rep, "lipsync", "sync-2-pro", REPAIR_ENDPOINT, length, cost)
        rep["result_url"] = result["video"]["url"]
        save(paths, report)
        dest = out / f"{name}_sync2pro.mp4"
        part = dest.with_name(dest.stem + ".part.mp4")
        with urllib.request.urlopen(rep["result_url"], timeout=300) as r, part.open("wb") as f:
            shutil.copyfileobj(r, f)
        info = probe(part)
        os.replace(part, dest)
        rep.update(file=rel(dest), video=info, finished=now())
        save(paths, report)
        rep["lipcheck"] = lipcheck.check(dest, w["start"], length)
        save(paths, report)
        print(f"{name}: repaired, {info['duration_s']:.2f} s at {info['fps']:g} fps, ${cost:.3f}")
        for row in rep["lipcheck"]["lines"]:
            print(f"  {row['signal']:8s} \"{row['line']}\": sound {row['our_vocal_ms']:+d} ms after the mouth "
                  f"(r={row['our_vocal_r']:.2f}) -> follows {row['follows']}")


def cover(paths, args):
    """Retired after step 0: through OpenRouter a cover can't both start on a given frame and follow the audio, so the
    route repairs the lips with sync-2-pro instead (PLAN.md phase 0c). Kept to reproduce the test. Known limits: it
    uses the test's START and CUT rather than the source clip's own window, and cover_edit places the cover on the
    frame boundary before CUT, up to one frame early."""
    report = load(paths)
    src = report["clips"][args.source]
    done = [a for a in src["attempts"] if a.get("checked")]
    if not done:
        raise SystemExit(f"{args.source} has no finished clip to cut")
    name = ("cover" if args.variant == "a" else "cover_b") + ("_g" if args.grade else "")
    if report["clips"].get(name, {}).get("attempts"):
        raise SystemExit(f"{name} was already submitted")
    fps = done[-1]["video"]["fps"]
    index = int(math.floor((CUT - START) * fps + 1e-6))  # the frame on screen at the cut
    first = frame(ROOT / done[-1]["file"], index, paths.out / "plates" / f"{name}_first_frame_{args.source}_f{index}.png")
    if args.grade:  # Seedance's own frames come back photoreal enough to be refused, so they get the print grade too
        first = print_grade.grade(first, first.with_name(first.stem + f"_print_c{args.cell:g}.png"), cell=args.cell)
    words = window_text(CUT, COVER_LENGTH)
    if words != COVER_WORDS:
        raise SystemExit(f"the words in the cover window changed: {words!r}")
    audio = cut_audio(CUT, COVER_LENGTH, paths.out / "audio" / f"vocal_{CUT:.3f}-{CUT + COVER_LENGTH:.3f}.wav")
    plate_url, first_url, audio_url = (upload(paths, f) for f in (ROOT / src["plate"], first, audio))
    if args.variant == "a":
        body = request(prompt(words), COVER_LENGTH, [plate_url], audio_url, first_frame=first_url)
    else:
        body = request(prompt(words, first_frame="@Image2"), COVER_LENGTH, [plate_url, first_url], audio_url)
    report["clips"][name] = {"from": args.source, "variant": args.variant, "plate": src["plate"],
                             "first_frame": rel(first), "first_frame_index": index,
                             "grade": {"tool": "tools/print_grade.py", "cell": args.cell} if args.grade else None,
                             "window": {"start": CUT, "end": CUT + COVER_LENGTH}, "words": words, "audio": rel(audio),
                             "request": body, "attempts": []}
    save(paths, report)
    show(paths, argparse.Namespace(names=[name]))


# ---- review ---------------------------------------------------------------------------------

def over_song(video, start, seconds, dest, fps):
    vf = [] if abs(fps - 24) < 1e-3 else ["-vf", "fps=24"]  # conform once, as the compositor needs
    run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-ss", f"{start:.3f}", "-t", f"{seconds:.3f}", "-i", str(SONG),
         "-map", "0:v", "-map", "1:a", *vf, "-t", f"{seconds:.3f}", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(dest)])


def cover_edit(original, cover_clip, cut_frame, dest):
    """The original to the cut, then the cover from its first frame, over the song."""
    n = probe(cover_clip)["frames"] or int(round(COVER_LENGTH * 24))
    seconds = (cut_frame + n) / 24
    run(["ffmpeg", "-v", "error", "-y", "-i", str(original), "-i", str(cover_clip), "-ss", f"{START:.3f}", "-t", f"{seconds:.3f}",
         "-i", str(SONG), "-filter_complex",
         f"[0:v]fps=24,trim=end_frame={cut_frame},setpts=PTS-STARTPTS[a];[1:v]fps=24,setpts=PTS-STARTPTS[b];"
         f"[a][b]concat=n=2:v=1:a=0[v]", "-map", "[v]", "-map", "2:a", "-t", f"{seconds:.3f}", "-c:v", "libx264",
         "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(dest)])
    return seconds


def checked(entry):
    return next((a for a in reversed(entry["attempts"]) if a.get("checked")), None)


def row(name, a):
    s = a["avsync"]
    if not s:
        return f"<tr><td>{name}</td><td colspan=8>{html.escape(a.get('error', 'no result'))}</td></tr>"
    loss = s["first_loss"]
    lost = "none" if not loss else "never in sync" if loss["from_start"] else f"{loss['clip_s']:.2f} s"
    verdict = "ok" if a["passes"] else "bad"
    slip = s["best_slip"]
    pct = lambda x: "-" if x is None else f"{x:.0%}"  # noqa: E731
    offset = "-" if s["global_offset_ms"] is None else f"{s['global_offset_ms']:+.0f} ms"
    cells = [name, pct(s["in_sync_fraction"]), f"{pct(slip['in_sync_fraction'])} ({slip['frames_earlier']:+d} fr)",
             f"{s['speaking_s']:.2f} s", offset, lost,
             f"{a['colour']['saturation']:.2f} / {a['colour']['plate_saturation']:.2f}",
             f"{a['start_frame']['mean_abs_diff']:.1f}", f"${a['cost_usd']:.3f}"]
    return ("<tr>" + "".join(f"<td>{c}</td>" for c in cells)
            + f"<td class={verdict}>{'pass' if a['passes'] else 'fail'}</td></tr>")


def card(paths, name, entry, a, video, slipped=None, k=0):
    w = entry["window"]
    title = name + (f" (cover of {entry['from']}, variant {entry['variant']})" if entry.get("from") else "")
    plot = ""
    if a["avsync"]:
        src = (ROOT / a["avsync"]["plot"]).relative_to(paths.out).as_posix()
        plot = f'<img src="../{src}" alt="avsync plot for {name}">'
    return (f"<section><h2>{html.escape(title)}</h2>"
            f"<p class=meta>{w['start']:.3f}&ndash;{w['end']:.3f} s &middot; &ldquo;{html.escape(entry['words'])}&rdquo;"
            f" &middot; job <code>{a['job_id']}</code></p>"
            f"<p class=meta>As placed: the clip starts at {w['start']:.3f} s, where its audio window starts.</p>"
            f"<video src=\"{video.name}\" controls loop preload=metadata></video>"
            + (f"<p class=meta>Moved {k} frames earlier ({k / 24 * 1000:.0f} ms), the slip avsync measured: the clip starts "
               f"at {w['start'] - k / 24:.3f} s.</p><video src=\"{slipped.name}\" controls loop preload=metadata></video>"
               if slipped else "")
            + f"{plot}"
            f"<details><summary>Prompt</summary><p>{html.escape(entry['request']['prompt'])}</p></details></section>")


def review(paths, args):
    report = load(paths)
    out = paths.out / "review"
    rows, cards = [], []
    for name, entry in report["clips"].items():
        a = checked(entry)
        if not a:
            continue
        w = entry["window"]
        video = out / f"{name}.mp4"
        over_song(ROOT / a["file"], w["start"], w["end"] - w["start"], video, a["video"]["fps"])
        k = ((a["avsync"] or {}).get("best_slip") or {}).get("frames_earlier", 0)
        slipped = None
        if k:  # placed k frames earlier, the song under it starts k frames earlier too
            slipped = out / f"{name}_slip{k:+d}.mp4"
            over_song(ROOT / a["file"], w["start"] - k / 24, w["end"] - w["start"], slipped, a["video"]["fps"])
        rows.append(row(name, a))
        cards.append(card(paths, name, entry, a, video, slipped, k))
    for key in ("cover", "cover_b", "cover_g", "cover_b_g"):
        entry = report["clips"].get(key)
        c = entry and checked(entry)
        o = c and checked(report["clips"][entry["from"]])
        if not (c and o):
            continue
        video = out / f"{key}_edit.mp4"
        cover_edit(ROOT / o["file"], ROOT / c["file"], entry["first_frame_index"], video)
        k = entry["first_frame_index"]
        cards.append(f"<section><h2>{key} in the edit</h2><p class=meta>{entry['from']} plays its frames 0&ndash;{k - 1}, "
                     f"to the cut at {CUT - START:.3f} s; then {key} takes over from its first frame, which was made from "
                     f"{entry['from']}&rsquo;s frame {k}. All over the song.</p>"
                     f"<video src=\"{video.name}\" controls loop preload=metadata></video></section>")
    repaired = []
    for name, entry in report["clips"].items():
        for rep in entry.get("repairs", []):
            if not rep.get("file"):
                continue
            w = entry["window"]
            video = out / f"{name}_sync2pro.mp4"
            over_song(ROOT / rep["file"], w["start"], w["end"] - w["start"], video, rep["video"]["fps"])
            checks = "".join(f"<tr><td>{html.escape(r['line'])}</td><td>{r['signal']}</td><td>{r['our_vocal_ms']:+d} ms</td>"
                             f"<td>{r['our_vocal_r']:.2f}</td></tr>" for r in (rep.get("lipcheck") or {}).get("lines", []))
            repaired.append(f"<section><h2>{name}, repaired with sync-2-pro</h2><p class=meta>The mouth redrawn to our vocal "
                            f"on fal ({rep['endpoint']}, request <code>{rep.get('request_id', '')}</code>, "
                            f"${rep['cost_usd']:.3f}). As placed, over the song.</p>"
                            f"<video src=\"{video.name}\" controls loop preload=metadata></video>"
                            + "".join(f'<img src="../repair/{img}" alt="{img}">' for img in
                                      (f"{name}_mouth.png", f"{name}_mouth_frames.png") if (paths.out / "repair" / img).exists())
                            + f"<p class=meta>Lip check: how long after the mouth moves our vocal sounds (0&ndash;100 ms is "
                            f"natural speech; below r&nbsp;&asymp;&nbsp;0.3 it's noise).</p><table><tr><th>Line</th>"
                            f"<th>Mouth signal</th><th>Sound after mouth</th><th>Correlation</th></tr>{checks}</table></section>")
    cards = repaired + cards
    page = out / "index.html"
    found = (report.get("result") or {}).get("findings") or []
    notes = ("<h2>Findings</h2><ul>" + "".join(f"<li>{html.escape(f)}</li>" for f in found) + "</ul>") if found else ""
    page.write_text(PAGE.format(rule=html.escape(report["pass_rule"]), rows="".join(rows), cards="".join(cards),
                                notes=notes), encoding="utf-8")
    print(f"Review page: {rel(page)}")


PAGE = """<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Seedance sync test</title>
<style>
:root{{--bg:#fafaf8;--fg:#1b1b1b;--muted:#666;--line:#ddd;--ok:#0a7d52;--bad:#b3261e}}
@media (prefers-color-scheme:dark){{:root{{--bg:#141414;--fg:#eee;--muted:#9a9a9a;--line:#333;--ok:#4cc38a;--bad:#ff8a80}}}}
body{{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;max-width:1180px;margin:0 auto;padding:24px 16px}}
h1{{font-size:22px;margin:0 0 4px}} h2{{font-size:17px;margin:32px 0 4px}} .meta{{color:var(--muted);margin:0 0 10px}}
table{{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}}
td,th{{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left}}
.ok{{color:var(--ok);font-weight:600}} .bad{{color:var(--bad);font-weight:600}}
video{{width:100%;max-width:960px;display:block;background:#000}} img{{width:100%;margin-top:10px}} code{{font-size:13px}}
</style>
<h1>Seedance sync test (BRIEF.md step 0)</h1>
<p class=meta>Every clip plays over the song itself, <code>Always Allow.mp3</code>; the model's own audio is only used to
measure the sync. Rule: {rule}.</p>
<table><tr><th>Clip</th><th>In sync as placed</th><th>In sync, moved</th><th>Speaking</th><th>Global offset</th><th>Sync lost</th>
<th>Saturation (clip / plate)</th><th>Start-frame diff</th><th>Cost</th><th>Result</th></tr>
{rows}</table>
{notes}
{cards}
"""


# ---- the fake API for --mock ----------------------------------------------------------------

class MockApi:
    """Stands in for OpenRouter: a job goes pending, in_progress, completed, and its content is an
    MP4 of the request's start image (or plate) over its audio reference played 20 ms late, so the
    checks have something real to measure. The cost is what 720p would cost."""

    def __init__(self, paths):
        cache = json.loads(paths.uploads.read_text(encoding="utf-8")) if paths.uploads.exists() else {}
        self.files = {v["url"]: ROOT / v["file"] for v in cache.values()}
        self.jobs, self.tmp = {}, paths.out

    def __call__(self, method, url, headers, data, timeout):
        assert headers.get("Authorization", "").startswith("Bearer "), "the key must go with every call"
        path = urllib.parse.urlparse(url).path
        if method == "POST" and path.endswith("/videos"):
            body = json.loads(data)
            for field in ("model", "prompt", "duration", "input_references"):
                if field not in body:
                    return 400, {}, json.dumps({"error": f"missing {field}"}).encode()
            job = f"mock-{len(self.jobs) + 1}"
            self.jobs[job] = {"body": body, "polls": 0}
            return 202, {}, json.dumps({"id": job, "generation_id": f"gen-{job}", "polling_url": f"/api/v1/videos/{job}",
                                        "status": "pending"}).encode()
        m = re.search(r"/videos/([^/]+)(/content)?$", path)
        job = self.jobs[m.group(1)]
        if m.group(2):
            return 200, {}, self.render(job["body"])
        job["polls"] += 1
        state = ["pending", "in_progress", "completed"][min(job["polls"] - 1, 2)]
        reply = {"id": m.group(1), "status": state}
        if state == "completed":
            reply["usage"] = {"cost": round(orv.USD_PER_S_720P * job["body"]["duration"], 4), "is_byok": False}
        return 200, {}, json.dumps(reply).encode()

    def render(self, body):
        image = (body.get("frame_images") or body["input_references"])[0]["image_url"]["url"]
        audio = next(r["audio_url"]["url"] for r in body["input_references"] if r["type"] == "audio_url")
        dest = self.tmp / "mock_render.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", "24", "-i", str(self.files[image]), "-i",
             str(self.files[audio]), "-af", "adelay=20", "-t", str(body["duration"]), "-vf", "scale=1280:720,format=yuv420p",
             "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", "-ar", "44100", str(dest)])
        return dest.read_bytes()


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--mock", action="store_true", help="fake API and uploads, in out/mock/ with its own ledger")
    sub = p.add_subparsers(dest="step", required=True)
    s = sub.add_parser("prepare")
    s.add_argument("--grade", action="store_true", help="put each plate through the print grade first (names t1g-t3g)")
    s.add_argument("--cell", type=float, default=5.0, help="the print grade's dot spacing in pixels (default 5)")
    s.add_argument("--start", type=float, default=START, help=f"the audio window's start in song seconds (default {START})")
    s.add_argument("--length", type=int, default=LENGTH, help=f"its length in whole seconds, 4-30 (default {LENGTH})")
    s.add_argument("--suffix", help="added to t1-t3 for these entries (default: g with --grade)")
    s = sub.add_parser("show")
    s.add_argument("names", nargs="*")
    s = sub.add_parser("submit")
    s.add_argument("names", nargs="+")
    s.add_argument("--again", action="store_true", help="resubmit a request that failed")
    sub.add_parser("collect")
    s = sub.add_parser("cover")
    s.add_argument("--from", dest="source", required=True, help="the clip to cut, e.g. t2")
    s.add_argument("--variant", choices=["a", "b"], default="a")
    s.add_argument("--grade", action="store_true", help="put the start frame through the print grade (name ends _g)")
    s.add_argument("--cell", type=float, default=5.0, help="the print grade's dot spacing in pixels (default 5)")
    s = sub.add_parser("repair")
    s.add_argument("names", nargs="+")
    s.add_argument("--timeout", type=float, default=1200, help="seconds to wait for fal (default 1200)")
    s.add_argument("--again", action="store_true", help="pay for a new repair of a clip whose last one failed")
    s = sub.add_parser("recheck")
    s.add_argument("names", nargs="*")
    s.add_argument("--max-lag", type=float, help="search offsets this far either way, in s (avsync's default is 0.5)")
    sub.add_parser("review")
    args = p.parse_args()
    paths = Paths(args.mock)
    {"prepare": prepare, "show": show, "submit": submit, "collect": collect, "cover": cover, "recheck": recheck,
     "repair": repair, "review": review}[args.step](paths, args)


if __name__ == "__main__":
    main()
