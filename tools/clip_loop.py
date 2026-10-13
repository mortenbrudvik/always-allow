"""The clip loop (BRIEF.md step 5, built in step 3): every Seedance clip on the board, from its plate to the select
the compositor shows.

For each clip in production/storyboard/shots.json, in board order:
  1. plate    production/assets/frames/<plate>.png|jpg, picked in step 4; a plate with a face goes through
              tools/print_grade.py first (ByteDance's filter refuses photoreal faces)
  2. audio    the clip's window, from the vocal stem for a speaking clip, from the full mix for motion and dancers
  3. take     Seedance through OpenRouter (tools/paid.py: the ledger, the $150 pause, the $400 stop, 3 jobs at once),
              downloaded, and checked: in colour, and for a speaking clip tools/avsync.py (how far Seedance's
              performance is from our vocal; a take that re-reads the line is retaken)
  4. repair   a speaking take: sync-2-pro on fal, from the take with its audio stripped and our vocal window; then
              the closure check (tools/closure_check.py). LatentSync only if sync-2-pro can't process the take,
              padded by a second and trimmed after (it drops about the last half-second).
  5. retake   a failed repair or check means a new take: at most 2 retakes a clip and 1 sync-2-pro repair a take
  6. select   production/clips/selects/<clip>.mp4 (24 fps, the window's frames, no audio), and every shot using
              the clip goes to `clip` (no speech) or `synced` (repaired), or `dropped`
Everything is logged per clip in production/storyboard/sync_report.json. A face refused by the filter, a credit
error (HTTP 402), the pause or the stop, a submission that may have created a job, or 3 Seedance failures in a row
stop new submissions; jobs already running are still collected, and the reason is printed and kept in the report.
The dancer mattes (SAM 2) and her tracking are separate step-5 jobs.

Usage, with the project's .venv:
  .venv/Scripts/python tools/clip_loop.py status              # every clip's state; no calls
  .venv/Scripts/python tools/clip_loop.py run --dry-run       # grade and cut the inputs, print the requests; no calls
  .venv/Scripts/python tools/clip_loop.py run [CLIP ...]      # paid: runs until every clip ends or waits
  .venv/Scripts/python tools/clip_loop.py run --mock          # fake APIs, in production/clips/mock/, own ledger
  .venv/Scripts/python tools/clip_loop.py recheck C13         # after a change to the closure rule: re-judge its repairs
"""
import argparse
import dataclasses
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

import closure_check
import ledger
import openrouter_video as orv
import paid
import print_grade
from seedance_test import likeness, probe, rgb_frames, run, saturation, sheet

ROOT = Path(__file__).resolve().parent.parent
BOARD = ROOT / "production" / "storyboard"
CLIPS = ROOT / "production" / "clips"
FPS = 24
MAX_RETAKES = 2            # BRIEF.md: 2 retakes a clip
REREAD_BELOW = 0.25        # avsync's best-slip in-sync fraction under which a take re-read the line in its own time
COLOUR_RATIO = 0.5         # a take is in colour if its saturation is at least half its plate's (step 0)
SWITCH_AFTER = 3           # BRIEF.md: switch to fal's Seedance after 3 OpenRouter failures in a row
COPYRIGHT = "copyright restrictions"  # ByteDance's output filter: unbilled, and not the provider failing
MAX_REFUSED = 4            # refusals a clip may have before it's dropped (they aren't takes: nothing came back)
PAD_S = 1.0                # LatentSync's padding


@dataclasses.dataclass
class Config:
    shots: Path = BOARD / "shots.json"
    report: Path = BOARD / "sync_report.json"
    ledger: Path = ledger.LEDGER
    work: Path = CLIPS                                 # inputs/, takes/, repairs/, selects/, sheets/, jobs.json
    frames: Path = ROOT / "production" / "assets" / "frames"
    vocals: Path = ROOT / "production" / "stems" / "vocals.mp3"
    song: Path = ROOT / "Always Allow.mp3"
    letters: Path = closure_check.LETTERS
    poll_s: float = 20.0

    @classmethod
    def mock(cls, base=CLIPS / "mock"):
        base.mkdir(parents=True, exist_ok=True)
        shots = base / "shots.json"
        if not shots.exists():  # the loop writes shot statuses: never into the real board from a mock
            shutil.copy(BOARD / "shots.json", shots)
        return cls(shots=shots, report=base / "sync_report.json", ledger=base / "ledger.csv", work=base, poll_s=0.01)


def now():
    return datetime.datetime.now().isoformat(timespec="seconds")


def rel(path):
    path = Path(path).resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()


def save_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for attempt in range(40):  # Windows refuses the swap while any other process has the file open (a reader)
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            if attempt == 39:
                raise
            time.sleep(0.25)


# ---- the lock ---------------------------------------------------------------------------------------------

def pid_alive(pid):
    if os.name == "nt":  # os.kill(pid, 0) would terminate the process on Windows
        import ctypes
        k = ctypes.windll.kernel32
        h = k.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return False
        code = ctypes.c_ulong()
        ok = k.GetExitCodeProcess(h, ctypes.byref(code))
        k.CloseHandle(h)
        return bool(ok) and code.value == 259  # STILL_ACTIVE
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


class Lock:
    """One loop at a time over a work folder: two would each think they own the same jobs."""

    def __init__(self, work):
        self.path = Path(work) / "clip_loop.lock"

    def __enter__(self):
        if self.path.exists():
            held = json.loads(self.path.read_text(encoding="utf-8"))
            if pid_alive(held["pid"]) and held["pid"] != os.getpid():
                raise SystemExit(f"another clip loop is running (pid {held['pid']}, since {held['started']})")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps({"pid": os.getpid(), "started": now()}), encoding="utf-8")
        return self

    def __exit__(self, *exc):
        self.path.unlink(missing_ok=True)


# ---- local media ------------------------------------------------------------------------------------------

def cut_audio(source, start, length, dest):
    """A window of `source` as mono 16-bit WAV at its own rate (WAV, so no encoder delay moves the words)."""
    import soundfile
    y, sr = soundfile.read(source, dtype="float32", always_2d=True)
    a = int(round(start * sr))
    Path(dest).parent.mkdir(parents=True, exist_ok=True)
    soundfile.write(dest, y[a:a + int(round(length * sr))].mean(1), sr, subtype="PCM_16")
    return Path(dest)


def strip_audio(video, dest):
    run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-an", "-c:v", "copy", str(dest)])
    return Path(dest)


def pad_video(video, seconds, dest):
    run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-an", "-vf", f"tpad=stop_mode=clone:stop_duration={seconds}",
         "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", str(dest)])
    return Path(dest)


def conform(video, frames, dest):
    """The select: 24 fps, exactly the window's frames, no audio (the soundtrack is the song). A source a few frames
    short (a repair cut to its audio's length) holds its last frame to the window's end. Returns the frames held."""
    Path(dest).parent.mkdir(parents=True, exist_ok=True)
    part = Path(dest).with_name(Path(dest).stem + ".part.mp4")
    run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-an", "-vf", f"fps={FPS},tpad=stop_mode=clone:stop_duration=1",
         "-frames:v", str(frames), "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(part)])
    os.replace(part, dest)
    src = probe(video)
    have = int(round(src["duration_s"] * FPS)) if not src["frames"] or abs(src["fps"] - FPS) > 1e-3 else src["frames"]
    return max(0, frames - have)


# ---- the checks (a class, so a mock run can stand in for what needs a real face) -----------------------------

class Checks:
    def __init__(self, cfg):
        self.cfg = cfg

    def avsync(self, take, start, seconds, name):
        import avsync
        r = avsync.analyze(take, start, seconds, name=name, out=self.cfg.work / "avsync")
        return {k: r[k] for k in ("in_sync_fraction", "speaking_s", "global_offset_ms", "median_offset_ms", "best_slip",
                                  "first_loss", "plot")}

    def closure(self, repaired, start, seconds, shown=None):
        return closure_check.check(repaired, start, seconds, letters=self.cfg.letters, shown=shown)


class MockChecks(Checks):
    """A mock clip is a still with a tone under it: nothing to measure a mouth on, so these pass."""

    def avsync(self, take, start, seconds, name):
        return {"in_sync_fraction": 1.0, "speaking_s": seconds, "global_offset_ms": 0, "median_offset_ms": 0,
                "best_slip": {"in_sync_fraction": 1.0, "frames_earlier": 0}, "first_loss": None, "plot": None, "mock": True}

    def closure(self, repaired, start, seconds, shown=None):
        return {"clip": rel(repaired), "checked": 0, "misses": 0, "passes": True, "face_found": 1.0, "mock": True,
                "closures": []}


# ---- the loop ---------------------------------------------------------------------------------------------

class Loop:
    def __init__(self, cfg, seedance, fal, checks, names=None, dry_run=False, log=print):
        self.cfg, self.seedance, self.fal, self.checks, self.log = cfg, seedance, fal, checks, log
        self.board = json.loads(cfg.shots.read_text(encoding="utf-8"))
        self.plates = {p["plate"]: p for p in self.board["plates"]}
        self.clips = [c for c in self.board["clips"] if not names or c["clip"] in names]
        if names and len(self.clips) != len(set(names)):
            raise SystemExit(f"unknown clip(s): {', '.join(sorted(set(names) - {c['clip'] for c in self.clips}))}")
        self.report = json.loads(cfg.report.read_text(encoding="utf-8")) if cfg.report.exists() else {
            "about": "BRIEF.md step 5: every Seedance clip's takes, repairs and checks, written by tools/clip_loop.py",
            "clips": {}}
        self.dry_run = dry_run
        self.halt = None  # why nothing more is submitted this run

    # -- bookkeeping --

    def save(self):
        save_json(self.cfg.report, self.report)

    def entry(self, clip):
        cid = clip["clip"]
        if cid not in self.report["clips"]:
            self.report["clips"][cid] = {
                "clip": cid, "kind": clip["kind"], "plate": clip["plate"], "window": clip["window"],
                "seconds": clip["seconds"], "words": clip["words"], "speaks_on_camera": clip["speaks_on_camera"],
                "shots": clip["shots"], "inputs": {}, "takes": [], "result": None, "state": "new"}
        return self.report["clips"][cid]

    def stop(self, why):
        if not self.halt:
            self.halt = why
            self.report["halted"] = {"at": now(), "why": why}
            self.log(f"STOP SUBMITTING: {why}")

    def finish(self, e, result, note, select=None):
        e.update(result=result, state=result, note=note, finished=now())
        if select:
            e["select"] = rel(select)
        status = {"accepted": "clip", "repaired": "synced", "dropped": "dropped"}[result]
        board = json.loads(self.cfg.shots.read_text(encoding="utf-8"))  # re-read: a rebuild may have happened
        for s in board["shots"]:
            if s["id"] in e["shots"]:
                s["status"] = status
                if result == "dropped":
                    s["drop_reason"] = note
                else:
                    s.pop("drop_reason", None)
        save_json(self.cfg.shots, board)
        self.log(f"{e['clip']}: {result} ({note})")

    # -- the steps --

    def plate_file(self, plate):
        for ext in (".png", ".jpg", ".jpeg", ".webp"):
            f = self.cfg.frames / f"{plate}{ext}"
            if f.exists():
                return f
        return None

    def inputs(self, clip, e):
        """The graded plate and the audio window, made once."""
        ins = e["inputs"]
        plate = self.plate_file(clip["plate"])
        if not plate:
            e["state"] = "waiting for its plate"
            return None
        digest = hashlib.sha1(plate.read_bytes()).hexdigest()[:12]  # a plate fixed in place is a new plate
        if not ins.get("plate") or ins.get("plate_source") != rel(plate) or ins.get("plate_sha1") != digest:
            ins["plate_source"], ins["plate_sha1"] = rel(plate), digest
            if self.plates[clip["plate"]]["print_grade"]:
                graded = self.cfg.work / "inputs" / f"{clip['plate']}_print_c5.png"
                graded.parent.mkdir(parents=True, exist_ok=True)
                print_grade.grade(plate, graded)
                ins["plate"], ins["graded"] = rel(graded), True
            else:
                ins["plate"], ins["graded"] = rel(plate), False
            ins.pop("plate_url", None)
        if not ins.get("audio"):
            w = clip["window"]
            src = self.cfg.vocals if clip["speaks_on_camera"] else self.cfg.song
            wav = cut_audio(src, w["start"], clip["seconds"], self.cfg.work / "inputs" / f"{clip['clip']}_{w['start']:.3f}.wav")
            ins.update(audio=rel(wav), audio_source=rel(src))
        return ins

    def request(self, clip, ins):
        # a clip without speech needs no soundtrack of its own (no sync check reads it); after the output filter
        # refused a take's generated music as copyrighted, it's asked for none
        return {"model": orv.MODEL, "prompt": clip["prompt"], "duration": clip["seconds"], "resolution": "720p",
                "aspect_ratio": "16:9", "generate_audio": not ins.get("no_audio", False),
                "input_references": [{"type": "image_url", "image_url": {"url": ins.get("plate_url", "<the plate's URL>")}},
                                     {"type": "audio_url", "audio_url": {"url": ins.get("audio_url", "<the audio's URL>")}}]}

    def new_take(self, clip, e, ins):
        n = len(e["takes"]) + 1
        if not ins.get("plate_url"):
            ins["plate_url"] = self.fal.upload(ROOT / ins["plate"])
        if not ins.get("audio_url"):
            ins["audio_url"] = self.fal.upload(ROOT / ins["audio"])
        self.save()
        key = f"{clip['clip']}/t{n}"
        rec = self.seedance.submit(key, self.request(clip, ins))
        e["takes"].append({"n": n, "job": key, "submitted": now()})
        e["state"] = f"take {n} submitted"
        if rec["status"] == "rejected":
            e["takes"][-1].update(verdict="rejected", reason=rec.get("error", "")[:300])
        self.save()
        self.log(f"{clip['clip']}: take {n} submitted ({rec['status']})")
        return True

    def after_take(self, clip, e, take):
        """The take's job ended: fetch it and check it. Returns True if anything changed."""
        rec = self.seedance.store.jobs[take["job"]]
        if rec["status"] in paid.OPEN:
            return False
        if rec["status"] != "completed":
            take.update(verdict="failed", reason=rec.get("error", rec["status"]), cost_usd=rec.get("cost_usd"))
            if rec.get("refused"):
                self.finish(e, "dropped", "the face filter refused the plate; it needs a stronger print grade or a new "
                                          "plate (a human call)")
            elif COPYRIGHT in (rec.get("error") or ""):
                # the output filter took the take for someone else's music or footage: not a provider failure, so it
                # doesn't count toward a switch; a clip without speech then asks for no generated audio
                if "output audio" in (rec.get("error") or "") and not clip["speaks_on_camera"]:
                    e["inputs"]["no_audio"] = True
                refused = sum(COPYRIGHT in (t.get("reason") or "") for t in e["takes"])
                if refused >= MAX_REFUSED:
                    self.finish(e, "dropped", f"Seedance's output filter refused it {refused} times as copyrighted")
            else:
                self.report["seedance_failures_in_a_row"] = self.report.get("seedance_failures_in_a_row", 0) + 1
                if self.report["seedance_failures_in_a_row"] >= SWITCH_AFTER:
                    self.stop(f"{SWITCH_AFTER} Seedance jobs failed in a row on OpenRouter: BRIEF.md switches to fal's "
                              "bytedance/seedance-2.5/reference-to-video, whose inputs must be checked on fal first")
            self.save()
            return True
        self.report["seedance_failures_in_a_row"] = 0
        dest = self.cfg.work / "takes" / f"{clip['clip']}_t{take['n']}.mp4"
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            self.seedance.download(take["job"], dest)
        info = probe(dest)
        ins = e["inputs"]
        plate = ROOT / ins["plate"]
        take_sat, plate_sat = saturation(rgb_frames(dest, fps=2)), saturation(rgb_frames(plate))
        (self.cfg.work / "sheets").mkdir(parents=True, exist_ok=True)
        sheet(dest, self.cfg.work / "sheets" / f"{clip['clip']}_t{take['n']}.png")
        take.update(file=rel(dest), video=info, cost_usd=rec["cost_usd"], cost_source=rec["cost_source"],
                    colour={"saturation": round(take_sat, 3), "plate_saturation": round(plate_sat, 3),
                            "in_colour": take_sat >= COLOUR_RATIO * plate_sat},
                    start_frame={"compared_with": ins["plate"], **likeness(plate, dest)}, checked=now())
        if not take["colour"]["in_colour"]:
            take.update(verdict="retake", reason="came back grey")
        elif clip["speaks_on_camera"] and info["audio"] is None:
            take.update(avsync=None, verdict="repair", note="no soundtrack, so avsync can't measure the performance")
        elif clip["speaks_on_camera"]:
            take["avsync"] = self.checks.avsync(dest, clip["window"]["start"], clip["seconds"], f"{clip['clip']}_t{take['n']}")
            slip = (take["avsync"].get("best_slip") or {}).get("in_sync_fraction") or 0
            # a take whose speech avsync can't match (a re-read, or the line started later than the lag it searches)
            # is repaired anyway: sync-2-pro re-times the lips to our vocal, and the closure check judges the result.
            # A take repaired this way is marked for a look by eye (QA_NOTES.md, checkpoint 2, item 6)
            take["verdict"] = "repair"
            if slip < REREAD_BELOW:
                take["reread"] = f"in sync {slip:.0%} at best (avsync): repaired all the same, to be judged by eye"
        else:
            take["verdict"] = "accept"
        self.save()
        self.log(f"{clip['clip']}: take {take['n']} {take['verdict']}{' (' + take['reason'] + ')' if take.get('reason') else ''}")
        return True

    @staticmethod
    def next_repair(reps):
        """The model for the take's next repair, or None: sync-2-pro once; again if it was cancelled in the queue
        (never started, never billed); LatentSync only if sync-2-pro couldn't process the take."""
        if not reps:
            return "sync-2-pro"
        last = reps[-1]
        if last.get("verdict") == "cancelled":
            return last["model"]
        if last["model"] == "sync-2-pro" and last.get("verdict") == "could not process":
            return "latentsync"
        return None

    def repair(self, clip, e, take):
        """Start, collect and check the take's repair. Returns True if anything changed."""
        reps = take.setdefault("repairs", [])
        seconds = clip["seconds"]
        model = self.next_repair(reps)
        if model:
            if self.halt or self.dry_run:
                return False
            base = self.cfg.work / "repairs" / f"{clip['clip']}_t{take['n']}"
            base.parent.mkdir(parents=True, exist_ok=True)
            video = strip_audio(ROOT / take["file"], base.with_name(base.name + "_video.mp4"))
            audio = ROOT / e["inputs"]["audio"]
            if model == "latentsync":  # it drops about the last half-second: pad both by a second, trim after
                video = pad_video(video, PAD_S, base.with_name(base.name + "_video_pad.mp4"))
                w = clip["window"]
                audio = cut_audio(self.cfg.vocals, w["start"], seconds + PAD_S, base.with_name(base.name + "_audio_pad.wav"))
            tries = sum(r["model"] == model for r in reps)
            key = f"{take['job']}/{model}" + (f"/{tries + 1}" if tries else "")
            try:
                self.fal.submit(key, model, self.fal.upload(video), self.fal.upload(audio),
                                seconds + (PAD_S if model == "latentsync" else 0))
            except paid.Busy:
                return False
            reps.append({"model": model, "job": key, "submitted": now()})
            e["state"] = f"take {take['n']} repairing ({model})"
            self.save()
            self.log(f"{clip['clip']}: take {take['n']} repair submitted ({model})")
            return True
        last = reps[-1]
        rec = self.fal.store.jobs[last["job"]]
        if rec["status"] in paid.OPEN or last.get("verdict"):
            return False
        if rec["status"] != "completed":
            last.update(verdict={"failed": "could not process"}.get(rec["status"], rec["status"]), reason=rec.get("error"))
            if self.next_repair(reps) is None:
                take.update(verdict="retake", reason=f"the repair didn't finish ({last['model']}: {rec['status']})")
            self.save()
            return True
        dest = self.cfg.work / "repairs" / f"{clip['clip']}_t{take['n']}_{last['model']}.mp4"
        if not dest.exists():
            self.fal.download(last["job"], dest)
        if last["model"] == "latentsync":  # back to the window's length
            trimmed = dest.with_name(dest.stem + "_trim.mp4")
            run(["ffmpeg", "-v", "error", "-y", "-i", str(dest), "-t", f"{seconds:.3f}", "-an", "-c:v", "libx264", "-crf", "14",
                 "-pix_fmt", "yuv420p", str(trimmed)])
            dest = trimmed
        last.update(file=rel(dest), cost_usd=rec["cost_usd"], cost_source=rec["cost_source"])
        last["closure"] = self.checks.closure(dest, clip["window"]["start"], seconds, self.shown(clip))
        last["verdict"] = "passes" if last["closure"]["passes"] else "fails"
        c = last["closure"]
        if last["verdict"] == "passes":
            take["verdict"] = "repaired"
        else:
            take.update(verdict="retake", reason=f"the lips missed {c['misses']} of {c['checked']} closures (p, b, m)"
                                                 f" or the face was lost (found in {c['face_found']:.0%} of frames)")
        self.save()
        self.log(f"{clip['clip']}: take {take['n']} repair {last['verdict']} ({c['checked'] - c['misses']}/{c['checked']} closures)")
        return True

    def advance(self, clip):
        """One step for one clip. Returns True if anything changed."""
        e = self.entry(clip)
        if e["result"]:
            return False
        ins = self.inputs(clip, e)
        if ins is None:
            return False
        take = e["takes"][-1] if e["takes"] else None
        if take and "verdict" not in take:
            return self.after_take(clip, e, take)
        if take and take["verdict"] == "repair":
            return self.repair(clip, e, take)
        if take and take["verdict"] in ("accept", "repaired"):
            src = ROOT / (take["repairs"][-1]["file"] if take["verdict"] == "repaired" else take["file"])
            select = self.cfg.work / "selects" / f"{clip['clip']}.mp4"
            e["select_held_frames"] = conform(src, int(round(clip["seconds"] * FPS)), select)
            self.finish(e, "repaired" if take["verdict"] == "repaired" else "accepted",
                        f"take {take['n']}" + (f", {take['repairs'][-1]['model']}" if take["verdict"] == "repaired" else ""),
                        select)
            self.save()
            return True
        if take and take["verdict"] == "rejected":
            if paid.is_refusal(take.get("reason")):
                self.finish(e, "dropped", "the face filter refused the plate; it needs a stronger print grade or a new plate")
                self.save()
                return True
            self.stop(f"OpenRouter rejected {take['job']} ({take.get('reason', '')[:200]}); if it no longer accepts the request "
                      "format, BRIEF.md switches to fal's Seedance")
            self.save()
            return False
        # a new take: the first, or a retake after a failure or a failed check
        completed = [t for t in e["takes"] if t.get("file")]
        if len(completed) > MAX_RETAKES:
            self.finish(e, "dropped", f"{len(completed)} takes, none passed: {completed[-1].get('reason', '')}")
            self.save()
            return True
        if self.dry_run:
            e["state"] = "ready to submit"
            self.log(f"{clip['clip']}: ready; the request would be:\n{json.dumps(self.request(clip, ins), indent=1)}")
            return False
        if self.halt:
            return False
        try:
            return self.new_take(clip, e, ins)
        except paid.Busy:
            return False
        except (ledger.Paused, ledger.Stopped, paid.Credit, paid.Unknown) as err:
            self.stop(f"{type(err).__name__}: {err}")
            self.save()
            return False

    def shown(self, clip):
        """What of the take the cut shows, in the window's song seconds: each shot plays it from `clip_in_s` for the
        shot's length (a held last frame adds nothing new). The closure check looks only there."""
        w0, end = clip["window"]["start"], clip["window"]["start"] + clip["seconds"]
        shots = {s["id"]: s for s in self.board["shots"]}
        out = []
        for sid in clip["shots"]:
            s = shots.get(sid)
            if not s or "t0" not in s or "t1" not in s:
                return [(w0, end)]  # a shot without its times: check the whole window
            a = w0 + s.get("clip_in_s", 0)
            out.append((a, min(end, a + s["t1"] - s["t0"])))
        return out or [(w0, end)]

    def recheck(self, clip):
        """The closure check again, as it stands now, on every repair the clip already has, in take order; the first
        take whose repair passes becomes the select, even if the clip was dropped. For a change to the check's rule:
        no uploads, no calls. Returns True if the clip's result changed."""
        e = self.entry(clip)
        passing = None
        for take in e["takes"]:
            for r in take.get("repairs", []):
                if r.get("file"):
                    c = self.checks.closure(ROOT / r["file"], clip["window"]["start"], clip["seconds"], self.shown(clip))
                    r.update(closure=c, verdict="passes" if c["passes"] else "fails", rechecked=now())
                    self.log(f"{clip['clip']}: take {take['n']} {r['model']} {r['verdict']} "
                             f"({c['checked'] - c['misses']}/{c['checked']} closures)")
                    if r["verdict"] == "passes" and passing is None:
                        passing = (take, r)
        self.save()
        if passing is None or e.get("result") == "repaired":
            return False
        take, r = passing
        take["verdict"] = "repaired"
        take.pop("reason", None)
        select = self.cfg.work / "selects" / f"{clip['clip']}.mp4"
        e["select_held_frames"] = conform(ROOT / r["file"], int(round(clip["seconds"] * FPS)), select)
        self.finish(e, "repaired", f"take {take['n']}, {r['model']} (rechecked {now()[:10]}: the closure rule changed)", select)
        self.save()
        return True

    def poll_all(self):
        for api in (self.seedance, self.fal):
            for rec in list(api.store.open_jobs()):
                if rec["provider"] != ("openrouter" if api is self.seedance else "fal"):
                    continue
                try:
                    api.poll(rec["key"])
                except Exception as err:  # a failed poll isn't a failed job
                    self.log(f"{rec['key']}: poll failed ({err!r}); trying again")

    def run(self, cycles=None):
        """Until every clip has ended or waits on something outside the loop; `cycles` stops it sooner (the tests use it
        to stop a run halfway, as a crash would)."""
        if self.dry_run:
            for clip in self.clips:
                self.advance(clip)
            self.save()
            return self.report
        while cycles is None or (cycles := cycles - 1) >= 0:
            self.poll_all()
            changed = False
            for clip in self.clips:
                changed |= self.advance(clip)
            self.save()
            waiting = self.seedance.store.open_jobs()
            if not waiting and not changed:
                break
            if waiting and not changed:
                time.sleep(self.cfg.poll_s)
        return self.report


# ---- mocks, for --mock and the tests ------------------------------------------------------------------------

class MockServer:
    """A fake provider's own state, kept in a file, so a mock loop can be stopped and started again like a real one."""

    def __init__(self, path, empty):
        self.state_path = Path(path)
        self.state = json.loads(self.state_path.read_text(encoding="utf-8")) if self.state_path.exists() else empty

    def keep(self):
        save_json(self.state_path, self.state)


class MockOpenRouter(MockServer):
    """A transport for openrouter_video.Client: a job goes pending, in_progress, completed; its content is the request's
    image over its audio, rendered with ffmpeg. `fail` names requests (by prompt text) that fail."""

    def __init__(self, store, tmp, fail=()):
        super().__init__(Path(tmp) / "mock_openrouter.json", {"jobs": {}})
        self.store, self.tmp, self.fail, self.jobs = store, Path(tmp), set(fail), self.state["jobs"]

    def files(self):
        return {v["url"]: Path(v["file"]) for v in self.store.data.get("uploads", {}).values()}

    def __call__(self, method, url, headers, data, timeout):
        assert headers.get("Authorization", "").startswith("Bearer "), "the key goes with every call"
        path = urllib.parse.urlparse(url).path
        if method == "POST" and path.endswith("/videos"):
            body = json.loads(data)
            job = f"mock-{len(self.jobs) + 1}"
            self.jobs[job] = {"body": body, "polls": 0}
            self.keep()
            return 202, {}, json.dumps({"id": job, "status": "pending"}).encode()
        m = re.search(r"/videos/([^/]+)(/content)?$", path)
        job = self.jobs[m.group(1)]
        if m.group(2):
            return 200, {}, self.render(job["body"])
        job["polls"] += 1
        self.keep()
        state = ["pending", "in_progress", "completed"][min(job["polls"] - 1, 2)]
        if state == "completed" and any(f in job["body"]["prompt"] for f in self.fail):
            return 200, {}, json.dumps({"id": m.group(1), "status": "failed", "error": "mock failure"}).encode()
        reply = {"id": m.group(1), "status": state}
        if state == "completed":
            reply["usage"] = {"cost": round(orv.USD_PER_S_720P * job["body"]["duration"], 4)}
        return 200, {}, json.dumps(reply).encode()

    def render(self, body):
        files = self.files()
        image = files[body["input_references"][0]["image_url"]["url"]]
        audio = files[body["input_references"][1]["audio_url"]["url"]]
        dest = self.tmp / "mock_render.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", "24", "-i", str(image), "-i", str(audio),
             "-t", str(body["duration"] + 0.04), "-vf", "scale=1280:720,format=yuv420p", "-c:v", "libx264", "-preset",
             "veryfast", "-c:a", "aac", str(dest)])
        return dest.read_bytes()


class MockFal(MockServer):
    """Stands in for fal_client: uploads get fake URLs, a repair is the video with the audio laid under it."""

    class Queued:
        position = 0

    class InProgress:
        pass

    class Completed:
        pass

    class Handle:
        def __init__(self, rid):
            self.request_id = rid

    def __init__(self, tmp, fail_models=()):
        super().__init__(Path(tmp) / "mock_fal.json", {"requests": {}, "urls": {}})
        self.tmp, self.fail_models = Path(tmp), set(fail_models)
        self.requests, self.urls = self.state["requests"], self.state["urls"]

    def upload_file(self, path):
        digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()[:12]
        url = f"https://mock.invalid/{digest}/{Path(path).name}"
        self.urls[url] = str(path)
        self.keep()
        return url

    def submit(self, endpoint, arguments):
        rid = f"fal-{len(self.requests) + 1}"
        self.requests[rid] = {"endpoint": endpoint, "arguments": arguments, "polls": 0}
        self.keep()
        return self.Handle(rid)

    def status(self, endpoint, rid):
        r = self.requests[rid]
        r["polls"] += 1
        self.keep()
        return [self.Queued(), self.InProgress(), self.Completed()][min(r["polls"] - 1, 2)]

    def result(self, endpoint, rid):
        if any(m in endpoint for m in self.fail_models):
            raise RuntimeError("mock: the model couldn't process the video")
        return {"video": {"url": f"mock://{rid}"}}

    def cancel(self, endpoint, rid):
        self.requests[rid]["cancelled"] = True

    def fetch(self, url, dest):
        args = self.requests[url.removeprefix("mock://")]["arguments"]
        run(["ffmpeg", "-v", "error", "-y", "-i", str(self.urls[args["video_url"]]), "-i", str(self.urls[args["audio_url"]]),
             "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-shortest", str(dest)])


def apis(cfg, mock):
    store = paid.JobStore(cfg.work / "jobs.json")
    if mock:
        fal = MockFal(cfg.work)
        return (paid.Seedance(store, orv.Client(key="mock-key", transport=MockOpenRouter(store, cfg.work)), cfg.ledger),
                paid.Fal(store, fal=fal, ledger_path=cfg.ledger, fetch=fal.fetch), MockChecks(cfg))
    return paid.Seedance(store, orv.Client(), cfg.ledger), paid.Fal(store, ledger_path=cfg.ledger), Checks(cfg)


def status(cfg):
    board = json.loads(cfg.shots.read_text(encoding="utf-8"))
    report = json.loads(cfg.report.read_text(encoding="utf-8")) if cfg.report.exists() else {"clips": {}}
    store = paid.JobStore(cfg.work / "jobs.json")
    spent = sum(j.get("cost_usd") or 0 for j in store.jobs.values())
    print(f"ledger ${ledger.total(cfg.ledger):.2f} (pause ${ledger.PAUSE_USD:.0f}, stop ${ledger.STOP_USD:.0f}); "
          f"this loop's jobs ${spent:.2f}; open {len(store.open_jobs())}")
    if report.get("halted"):
        print(f"halted {report['halted']['at']}: {report['halted']['why']}")
    for c in board["clips"]:
        e = report["clips"].get(c["clip"], {})
        plate = any((cfg.frames / f"{c['plate']}{x}").exists() for x in (".png", ".jpg", ".jpeg", ".webp"))
        state = e.get("result") or e.get("state") or ("ready" if plate else "waiting for its plate")
        print(f"  {c['clip']:4s} {c['kind']:6s} {c['seconds']} s  {state:28s} takes {len(e.get('takes', []))}")


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="step", required=True)
    s = sub.add_parser("status")
    s.add_argument("--mock", action="store_true")
    s = sub.add_parser("recheck", help="the closure check again on the repairs clips already have; no calls")
    s.add_argument("clips", nargs="+")
    s.add_argument("--mock", action="store_true")
    s = sub.add_parser("run")
    s.add_argument("clips", nargs="*", help="only these clips (default: all, in board order)")
    s.add_argument("--dry-run", action="store_true", help="make the inputs and print the requests; no uploads, no calls")
    s.add_argument("--mock", action="store_true", help="fake APIs in production/clips/mock/, with its own ledger and board")
    args = p.parse_args()
    cfg = Config.mock() if args.mock else Config()
    if args.step == "status":
        status(cfg)
        return
    with Lock(cfg.work):
        if args.step == "recheck":
            loop = Loop(cfg, None, None, MockChecks(cfg) if args.mock else Checks(cfg), names=args.clips)
            for c in loop.clips:
                loop.recheck(c)
            return
        if args.dry_run:
            loop = Loop(cfg, None, None, None, names=args.clips, dry_run=True)
        else:
            seedance, fal, checks = apis(cfg, args.mock)
            loop = Loop(cfg, seedance, fal, checks, names=args.clips)
        loop.run()
    if loop.halt:
        print(f"Halted: {loop.halt}")
        sys.exit(3)


if __name__ == "__main__":
    main()
