"""Build and check the storyboard (BRIEF.md step 3).

Reads the board in production/storyboard/board.py and writes, with every time on the beat grid of
production/analysis/song.json and every Seedance window placed on the word times of
production/analysis/words.json:
  production/storyboard/shots.json      the shots, clips and plates, for the compositor and the pipeline
  production/storyboard/STORYBOARD.md   the same, to read, with the Seedance clip list and its cost
  production/storyboard/mj_prompts.md   the Midjourney plate pack, each plate with the shots it serves

A rebuild keeps every status, drop reason and file already recorded in shots.json, so the pipeline's
progress survives an edit to the board. `check` runs the board's rules and exits non-zero if any fail.

Usage, with the project's .venv:
  .venv/Scripts/python tools/storyboard.py build      # check, then write all three files
  .venv/Scripts/python tools/storyboard.py check      # only the checks
"""
import argparse
import bisect
import datetime
import importlib.util
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SONG = ROOT / "production" / "analysis" / "song.json"
WORDS = ROOT / "production" / "analysis" / "words.json"
BOARD_DIR = ROOT / "production" / "storyboard"
BOARD = BOARD_DIR / "board.py"
SHOTS = BOARD_DIR / "shots.json"
STORYBOARD = BOARD_DIR / "STORYBOARD.md"
MJ_PROMPTS = BOARD_DIR / "mj_prompts.md"

FPS = 24
LEAD_S = 0.5            # a speaking window starts this far ahead of its first word, where the gap allows
GAP_MIN_S = 0.02        # and at least this long after the previous word ends
TAIL_S = 0.3            # it runs at least this far past its last word
MIN_CLIP_S, MAX_CLIP_S = 4, 8
USD_PER_S = 0.233       # Seedance 2.5 at 720p through OpenRouter (PLAN.md section 6)
REPAIR_USD_PER_S = 5 / 60   # sync-2-pro on fal, $5 a minute
RETAKE_SHARE = 1 / 3    # the expected share of clips retaken once (PLAN.md section 6, "Expected")
MAX_RETAKES = 2         # BRIEF.md's cap per clip
MAX_PLATE_SHOTS = 3     # BRIEF.md: no plate in more than 3 shots
MAX_INSERT_BARS = 2     # BRIEF.md: inserts without her last at most 2 bars
MODES = {"masthead", "coverline", "subtitle", "serif", "mass"}
ZONES = {"left", "right", "top", "bottom", "center", "ui"}
TIERS = {"seedance", "2.5d", "code"}
SPEAK_FRAMINGS = {"CU", "MCU"}
DEVICES = {"tab switch", "window wipe", "blink", "session close", "push-through", "shape match", "terminal scroll", "flash"}
MOODBOARD = "--p m7503794824781234213"
PARAMS_AGENT = "--ar 16:9 --v 8.2 --raw --hd"
PARAMS_SET = f"--ar 16:9 --v 8.2 --raw --hd {MOODBOARD}"
FINISH = "fine film grain, cinematic 35mm film still, no text, no letters, no logos"
KEEP = ("status", "drop_reason", "files", "notes_pipeline")  # fields the pipeline owns


def rel(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def load_board(path=BOARD):
    spec = importlib.util.spec_from_file_location("board", path)
    board = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(board)
    return board


class Grid:
    """Bar positions to song seconds on the fitted beat grid (never a grid rebuilt from the BPM)."""

    def __init__(self, song):
        self.beats = song["beats_s"]
        self.down = song["downbeats_s"]
        self.duration = song["duration_s"]
        self.first_bar = -8  # downbeats_s[0] is bar -8 (song.json notes)

    def pos(self, bar):
        if bar is None:
            return 0.0
        b = 4 * (bar - self.first_bar)
        i = math.floor(b + 1e-9)
        frac = b - i
        n = len(self.beats)
        if i >= n - 1:  # past the last beat: extend with the last beat's length
            step = self.beats[-1] - self.beats[-2]
            return self.beats[-1] + (b - (n - 1)) * step
        return self.beats[i] + frac * (self.beats[i + 1] - self.beats[i])

    def bar_of(self, t):
        k = bisect.bisect_right(self.down, t) - 1
        k = max(0, min(k, len(self.down) - 2))
        return k + self.first_bar + (t - self.down[k]) / (self.down[k + 1] - self.down[k])


def frame(t):
    return int(round(t * FPS))


def section_of(song, t):
    for s in song["sections"]:
        if s["start"] - 1e-6 <= t < s["end"] - 1e-6:
            return s["label"].split(":")[0].split(" (")[0].split(";")[0]
    return song["sections"][-1]["label"]


# ---- clips -----------------------------------------------------------------------------------------

def all_words(lines):
    return sorted(((w["start"], w["end"], i, w["word"]) for i, ln in enumerate(lines) for w in ln["words"]))


def speak_window(clip, lines, words, shot_spans):
    """(start s, seconds, problems) for a speaking clip: in the gap before its first word, on a frame, as near
    LEAD_S ahead as the gap allows, long enough for its words and its shots, in whole seconds."""
    problems = []
    first = lines[clip["lines"][0]]["words"][0]
    last = lines[clip["lines"][-1]]["words"][-1]
    w0 = first["start"]
    before = [e for s, e, i, _ in words if e <= w0 + 1e-6 and not (i in clip["lines"])]
    prev_end = max(before) if before else 0.0
    lo = prev_end + GAP_MIN_S
    target = max(w0 - LEAD_S, lo)
    f = int(round(target * FPS))
    if f / FPS < lo - 1e-9:
        f += 1
    start = f / FPS
    if start > w0 - 2 / FPS:
        problems.append(f"the gap before {first['word']!r} is too short for a window")
    need = max([last["end"] + TAIL_S] + [b for _, b in shot_spans]) - start
    seconds = max(MIN_CLIP_S, math.ceil(need - 1e-6))
    if seconds > MAX_CLIP_S:
        problems.append(f"needs {need:.2f} s, over {MAX_CLIP_S} s")
    for a, _ in shot_spans:
        if a < start - 1e-6:
            problems.append(f"a shot starts at {a:.3f} s, before the window's start at {start:.3f} s")
    return start, seconds, problems


def held_words(lines, start, end):
    """The words wholly inside [start, end], as the prompt quotes them: whole lines as written, a line cut by
    the window's end as its whole words."""
    parts = []
    for ln in lines:
        inside = [w for w in ln["words"] if w["start"] >= start - 1e-6 and w["end"] <= end + 1e-6]
        if not inside:
            continue
        if len(inside) == len(ln["words"]):
            parts.append(ln["text"].replace("(always)", "").strip())
        else:
            parts.append(" ".join(w["word"] for w in inside))
    out = ""
    for part in parts:  # lines join as sentences, so a fragment of the next line reads as one
        out = part if not out else out + ("" if out[-1] in ".?!…" or part[:1].islower() else ".") + " " + part
    return out


def seedance_prompt(clip, quote):
    if clip["kind"] == "speak":
        return (f'@Image1 sings @Audio1. She lip-syncs to @Audio1 exactly, every word in time: "{quote}". '
                f"{clip['framing']}, {clip['action']}. Locked camera, no cuts, no head turns.")
    return (f"The scene from @Image1, moving in time with @Audio1. {clip['framing']}. {clip['action']}. "
            f"{clip['camera']}. No cuts. Her mouth stays closed, face expressionless.")


# ---- plates ----------------------------------------------------------------------------------------

def mj_prompt(board, p):
    who = p.get("who")
    far = p.get("canon") == "far"  # wide, full-length, from behind, overhead: the distance canon (board.py)
    agent = board.AGENT_HANDS if p.get("canon") == "hands" else board.AGENT_FAR if far else board.AGENT
    figure = {"agent": agent, "instances": board.INSTANCES_FAR if far else board.INSTANCES,
              "human": board.HUMAN}.get(who) or p.get("subject", "")
    body = f"{p['framing']} {figure}, {p['action']}, {p['place']}, {p['setting']}, {board.PALETTE[p['palette']]}, {FINISH}"
    params = PARAMS_AGENT if who in ("agent", "instances") else PARAMS_SET
    return f"{body} {params}" + (f" --no {p['no']}" if p.get("no") else "")


# ---- build -----------------------------------------------------------------------------------------

def build(board, song, words_json, old=None):
    grid = Grid(song)
    lines = words_json["lines"]
    words = all_words(lines)
    problems = []
    raw = board.SHOTS
    starts = [grid.pos(s["at"]) for s in raw]
    ends = starts[1:] + [song["duration_s"]]
    old_shots = {s["id"]: s for s in (old or {}).get("shots", [])}

    shots = []
    for n, (s, t0, t1) in enumerate(zip(raw, starts, ends), 1):
        sid = f"s{n:03d}"
        entry = {
            "id": sid, "chapter": s["ch"], "t0": round(t0, 4), "t1": round(t1, 4), "f0": frame(t0), "f1": frame(t1),
            "bar0": s["at"] if s["at"] is not None else -8.0, "bar1": raw[n]["at"] if n < len(raw) else None,
            "section": section_of(song, t0), "set": s["set"], "agent_on_screen": s["agent"], "framing": s["framing"],
            "motion_tier": s["tier"], "clip": s.get("clip"), "plate": s.get("plate"), "place": s["place"],
            "shift_bars": s.get("shift", 0), "hold_last_frame": s.get("hold", False), "footage_x": s.get("footage_x", 0),
            "clip_holds": [list(h) for h in s.get("holds", [])],
            "action": s["action"], "camera": s["camera"], "graphic": s["graphic"],
            "transition": s.get("transition", "cut"), "notes": s.get("notes", ""), "face": s.get("face", "shown"),
            "world": s.get("world"),
            "lyrics": [], "status": "planned",
        }
        for spec in s.get("lines", []):
            idx, mode, zone = spec[:3]  # a 4th item, {at, mode, zone}, changes the mode from word `at` on
            ln = lines[idx]
            ly = {"line": idx, "text": ln["text"], "mode": mode, "zone": zone, "t0": ln["start"], "t1": ln["end"],
                  "words": [{"word": w["word"], "t0": w["start"], "t1": w["end"]} for w in ln["words"]]}
            if len(spec) > 3:
                ly["split"] = spec[3]
            entry["lyrics"].append(ly)
        prior = old_shots.get(sid)
        if prior and prior.get("action") == entry["action"]:  # the same shot: keep what the pipeline recorded
            for k in KEEP:
                if k in prior:
                    entry[k] = prior[k]
        shots.append(entry)

    # clips: windows from the word times, and the shots that use them
    clips = []
    for cid, c in board.CLIPS.items():
        users = [s for s in shots if s["clip"] == cid]
        if c["kind"] == "speak":
            spans = [(s["t0"], s["t1"]) for s in users if not s["shift_bars"]]
            start, seconds, probs = speak_window(c, lines, words, spans)
            problems += [f"clip {cid}: {p}" for p in probs]
        else:
            start = math.floor(grid.pos(c["at"]) * FPS + 1e-6) / FPS
            seconds = c["seconds"]
        end = start + seconds
        for s in users:  # every shot must fall inside the window, after any hook shift
            shift_s = s["t0"] - grid.pos(s["bar0"] - s["shift_bars"]) if s["shift_bars"] else 0.0
            a, b = s["t0"] - shift_s, s["t1"] - shift_s
            s["clip_in_s"] = round(a - start, 4)
            if a < start - 1e-6 or (b > end + 1e-6 and not s["hold_last_frame"]):
                problems.append(f"clip {cid}: shot {s['id']} runs {a:.3f}-{b:.3f} s, outside the window {start:.3f}-{end:.3f} s")
        speaks = c["kind"] == "speak"
        quote = held_words(lines, start, end) if speaks else ""  # a motion clip's mouth stays closed
        clips.append({
            "clip": cid, "kind": c["kind"], "plate": c["plate"], "speaks_on_camera": speaks,
            "window": {"start": round(start, 6), "end": round(end, 6), "start_frame": frame(start)},
            "seconds": seconds, "audio": "production/stems/vocals.mp3" if speaks else "Always Allow.mp3",
            "lines": c.get("lines", []), "words": quote, "prompt": seedance_prompt(c, quote),
            "shots": [s["id"] for s in users], "print_grade": True, "status": "planned",
        })

    # plates: the prompt, the shots each serves (directly, or as the start frame of a clip)
    plates = []
    clip_of_plate = {c["plate"]: c["clip"] for c in clips}
    for pid, p in board.PLATES.items():
        direct = [s["id"] for s in shots if s["plate"] == pid]
        via = [s["id"] for c in clips if c["plate"] == pid for s in shots if s["clip"] == c["clip"]]
        dancer = any(c["plate"] == pid and c["kind"] == "dancer" for c in clips)
        serves = sorted(set(direct + ([] if dancer else via)))
        plates.append({
            "plate": pid, "set": p["set"], "who": p.get("who"), "framing": p["framing"].split(" of")[0],
            "for_clip": clip_of_plate.get(pid), "dancer": dancer, "shots": serves if not dancer else sorted(set(via)),
            "print_grade": p.get("who") in ("agent", "instances", "human"),
            "depth_map": any(s["motion_tier"] == "2.5d" for s in shots if s["plate"] == pid),
            "prompt": mj_prompt(board, p), "status": "planned",
        })
    doc = {"version": 1, "song": "Always Allow.mp3", "fps": FPS, "duration_s": song["duration_s"],
           "frames": frame(song["duration_s"]), "built": datetime.datetime.now().isoformat(timespec="seconds"),
           "source": rel(BOARD), "chapters": [], "shots": shots, "clips": clips, "plates": plates}
    for cid, name, at in board.CHAPTERS:
        own = [s for s in shots if s["chapter"] == cid]  # a chapter runs from its first shot to its last
        if not own:
            problems.append(f"chapter {cid} has no shots")
            continue
        if abs(own[0]["bar0"] - at) > 1e-6:
            problems.append(f"chapter {cid} is listed at bar {at:g} but its first shot {own[0]['id']} is at bar {own[0]['bar0']:g}")
        doc["chapters"].append({"chapter": cid, "name": name, "t0": own[0]["t0"], "t1": own[-1]["t1"],
                                "f0": own[0]["f0"], "f1": own[-1]["f1"], "file": f"production/comp/src/chapters/{cid}.tsx",
                                "shots": [s["id"] for s in own]})
    for a, b in zip(doc["chapters"], doc["chapters"][1:]):
        if a["f1"] != b["f0"]:
            problems.append(f"chapter {a['chapter']} ends at frame {a['f1']} but {b['chapter']} starts at {b['f0']}: its shots aren't contiguous")
    problems += check(doc, lines, grid, board)
    doc["totals"] = totals(doc, grid)
    return doc, problems


def check(doc, lines, grid, board):
    """The board's rules. Returns a list of problems (empty when it passes)."""
    out = []
    shots, clips = doc["shots"], {c["clip"]: c for c in doc["clips"]}
    plates = {p["plate"]: p for p in doc["plates"]}
    # tiling
    if shots[0]["f0"] != 0:
        out.append("the first shot must start at frame 0")
    for a, b in zip(shots, shots[1:]):
        if b["f0"] != a["f1"]:
            out.append(f"{a['id']} ends at frame {a['f1']} but {b['id']} starts at {b['f0']}")
    for s in shots:
        if s["f1"] - s["f0"] < 6:
            out.append(f"{s['id']} is only {s['f1'] - s['f0']} frames long")
        if s["chapter"] not in {c[0] for c in board.CHAPTERS}:
            out.append(f"{s['id']}: unknown chapter {s['chapter']}")
    if shots[-1]["f1"] != doc["frames"]:
        out.append(f"the last shot ends at frame {shots[-1]['f1']}, not {doc['frames']}")
    # every lyric line once, on the shot holding its first word
    seen = {}
    for s in shots:
        for ly in s["lyrics"]:
            if ly["line"] in seen:
                out.append(f"line {ly['line']} is listed on {seen[ly['line']]} and {s['id']}")
            seen[ly["line"]] = s["id"]
            if ly["mode"] not in MODES or ly["zone"] not in ZONES:
                out.append(f"{s['id']}: line {ly['line']} has mode {ly['mode']!r} or zone {ly['zone']!r}")
            sp = ly.get("split")
            if sp and (sp.get("mode") not in MODES or sp.get("zone") not in ZONES or not 0 < sp.get("at", 0) < len(ly["words"])):
                out.append(f"{s['id']}: line {ly['line']} has a bad split {sp!r}")
            w0 = ly["words"][0]["t0"]
            if not (s["t0"] - 1e-6 <= w0 < s["t1"]):
                out.append(f"line {ly['line']} ({ly['text']!r}) starts at {w0:.3f} s, outside its shot {s['id']} ({s['t0']:.3f}-{s['t1']:.3f})")
    for i in range(len(lines)):
        if i not in seen:
            out.append(f"line {i} ({lines[i]['text']!r}) isn't on any shot")
    # tiers
    for s in shots:
        if s["motion_tier"] not in TIERS:
            out.append(f"{s['id']}: tier {s['motion_tier']!r}")
        if s["motion_tier"] == "seedance" and s["clip"] not in clips:
            out.append(f"{s['id']}: seedance without a known clip ({s['clip']})")
        if s["motion_tier"] == "2.5d" and s["plate"] not in plates:
            out.append(f"{s['id']}: 2.5d without a known plate ({s['plate']})")
        if s["motion_tier"] == "code" and (s["plate"] or s["clip"]):
            out.append(f"{s['id']}: code-only but has a plate or clip")
        if s["plate"] and s["plate"] not in plates:
            out.append(f"{s['id']}: unknown plate {s['plate']}")
        c = clips.get(s["clip"])
        if c and c["kind"] == "speak" and s["framing"] not in SPEAK_FRAMINGS:
            out.append(f"{s['id']}: speaking clip {c['clip']} in a {s['framing']}, not CU or MCU")
        if s["transition"] not in DEVICES | {"cut", "cold open", "hard stop"} and not s["transition"].startswith(("the Enter", "shape match")):
            out.append(f"{s['id']}: unknown transition {s['transition']!r}")
    # her face on camera in a close shot during a line she doesn't speak (BRIEF.md: when it's on camera, she speaks)
    sung = [(w["t0"], w["t1"]) for s in shots for ly in s["lyrics"] for w in ly["words"]]
    for s in shots:
        c = clips.get(s["clip"])
        if (s["agent_on_screen"] and s["framing"] in ("ECU", "CU", "MCU") and s["face"] == "shown"
                and not (c and c["kind"] == "speak") and any(a < s["t1"] and b > s["t0"] for a, b in sung)):
            out.append(f"{s['id']}: her face is on camera ({s['framing']}) during a line she doesn't speak")
    # clips: one plate each (no two clips from the same frame), a window of 4-8 whole seconds on a frame
    by_plate = {}
    for c in clips.values():
        by_plate.setdefault(c["plate"], []).append(c["clip"])
        if not (MIN_CLIP_S <= c["seconds"] <= MAX_CLIP_S):
            out.append(f"clip {c['clip']}: {c['seconds']} s")
        if abs(c["window"]["start_frame"] / FPS - c["window"]["start"]) > 1e-5:
            out.append(f"clip {c['clip']}: window start {c['window']['start']} isn't on a frame")
        if c["plate"] not in plates:
            out.append(f"clip {c['clip']}: unknown plate {c['plate']}")
        if not c["shots"] and not board.CLIPS.get(c["clip"], {}).get("dropped"):  # a dropped clip is kept as a record
            out.append(f"clip {c['clip']} isn't used by any shot")
    for pid, cs in by_plate.items():
        if len(cs) > 1:
            out.append(f"plate {pid} starts {len(cs)} clips ({', '.join(cs)}): never two clips from one frame")
    # plates in at most 3 shots (a dancer's start frame is cut out of it, so only its stages count)
    for p in plates.values():
        if not p["dancer"] and len(p["shots"]) > MAX_PLATE_SHOTS:
            out.append(f"plate {p['plate']} serves {len(p['shots'])} shots ({', '.join(p['shots'])}), over {MAX_PLATE_SHOTS}")
        if not p["shots"] and p["plate"] not in {c["plate"] for c in board.CLIPS.values() if c.get("dropped")}:
            out.append(f"plate {p['plate']} isn't used")
    # inserts without her: at most 2 bars in a row
    run, run_from = 0.0, None
    for s in shots:
        if s["agent_on_screen"] or s["notes"] == "end card":
            run, run_from = 0.0, None
            continue
        bars = grid.bar_of(s["t1"] - 1e-6) - grid.bar_of(s["t0"])
        run += bars
        run_from = run_from or s["id"]
        if run > MAX_INSERT_BARS + 1e-3:
            out.append(f"shots from {run_from} to {s['id']} have no Agent for {run:.2f} bars, over {MAX_INSERT_BARS}")
    # transitions: never the same device twice in a row
    last = None
    for s in shots:
        dev = next((d for d in DEVICES if s["transition"].startswith(d)), None)
        if dev:
            if dev == last:
                out.append(f"{s['id']}: {dev} twice in a row")
            last = dev
    return out


def totals(doc, grid):
    clips = doc["clips"]
    shots = doc["shots"]
    seconds = sum(c["seconds"] for c in clips)
    speak = [c for c in clips if c["kind"] == "speak"]
    speak_s = sum(c["seconds"] for c in speak)
    retake_s = seconds * RETAKE_SHARE
    retake_speak_s = speak_s * RETAKE_SHARE
    on = sum(s["t1"] - s["t0"] for s in shots if s["agent_on_screen"])
    tiers = {}
    for s in shots:
        tiers[s["motion_tier"]] = tiers.get(s["motion_tier"], 0) + 1
    exp_seed = (seconds + retake_s) * USD_PER_S
    exp_rep = (speak_s + retake_speak_s) * REPAIR_USD_PER_S
    cap_seed = seconds * (1 + MAX_RETAKES) * USD_PER_S
    cap_rep = speak_s * (1 + MAX_RETAKES) * REPAIR_USD_PER_S
    return {
        "shots": len(shots), "shots_by_tier": tiers, "clips": len(clips), "speaking_clips": len(speak),
        "motion_clips": len(clips) - len(speak), "seedance_s": seconds, "speaking_s": speak_s,
        "agent_on_screen_fraction": round(on / doc["duration_s"], 3),
        "plates": len(doc["plates"]), "plates_with_a_face": sum(p["print_grade"] for p in doc["plates"]),
        "cost_usd": {
            "planned": {"seedance": round(seconds * USD_PER_S, 2), "repairs": round(speak_s * REPAIR_USD_PER_S, 2)},
            "expected": {"seedance": round(exp_seed, 2), "repairs": round(exp_rep, 2), "total": round(exp_seed + exp_rep, 2),
                         "assumes": f"a third of the clips retaken once, and every speaking take repaired with sync-2-pro"},
            "at_the_caps": {"seedance": round(cap_seed, 2), "repairs": round(cap_rep, 2), "total": round(cap_seed + cap_rep, 2),
                            "assumes": f"every clip retaken {MAX_RETAKES} times and every speaking take repaired"},
            "prices": {"seedance_usd_per_s": USD_PER_S, "sync2pro_usd_per_s": round(REPAIR_USD_PER_S, 4)},
        },
    }


# ---- the documents -----------------------------------------------------------------------------------

def mmss(t):
    return f"{int(t // 60)}:{t % 60:05.2f}"


def storyboard_md(doc, board):
    t = doc["totals"]
    c = t["cost_usd"]
    out = [
        "# Storyboard: Always Allow",
        "",
        f"Built by `tools/storyboard.py` from `production/storyboard/board.py` on {doc['built'][:10]}; `shots.json` holds the same shots, clips "
        "and plates for the compositor and the pipeline. The idea, the palette, the type and the rules are in "
        "`production/style/STYLE_BIBLE.md`; the Midjourney plates are in `mj_prompts.md`.",
        "",
        f"**{t['shots']} shots** ({', '.join(f'{v} {k}' for k, v in sorted(t['shots_by_tier'].items()))}), "
        f"**{t['clips']} Seedance clips** ({t['speaking_clips']} speaking, {t['motion_clips']} motion and dancer), "
        f"{t['seedance_s']} s of Seedance, {t['plates']} plates. The Agent is on screen {t['agent_on_screen_fraction']:.0%} of the time.",
        "",
        "How to read a shot: its time range is on the beat grid (song seconds, and bars with bar 0 on the first drop); each lyric line "
        "is listed on the shot where its first word falls, with its type mode and text zone, and stays on screen until it ends. "
        "Tiers: **seedance** (a clip; a dancer clip is cut out with a matte and composited on the named stage), **2.5d** (a plate over its "
        "depth map), **code** (drawn entirely in code). Every shot starts `planned`.",
        "",
        "## Chapters",
        "",
        "One file per chapter in `production/comp/src/chapters/`, so animator agents never edit each other's.",
        "",
        "| Chapter | Name | Time | Shots |",
        "|---|---|---|---|",
    ]
    for ch in doc["chapters"]:
        out.append(f"| {ch['chapter']} | {ch['name']} | {mmss(ch['t0'])}–{mmss(ch['t1'])} | {ch['shots'][0]}–{ch['shots'][-1]} ({len(ch['shots'])}) |")
    names = {ch["chapter"]: ch["name"] for ch in doc["chapters"]}
    for ch in doc["chapters"]:
        out += ["", f"## {ch['chapter']}: {ch['name']} ({mmss(ch['t0'])}–{mmss(ch['t1'])})", ""]
        for sid in ch["shots"]:
            s = next(x for x in doc["shots"] if x["id"] == sid)
            foot = s["clip"] or s["plate"] or "code"
            if s["clip"] and s["plate"]:
                foot = f"{s['clip']} on {s['plate']}"
            head = (f"**{s['id']}** · {s['t0']:.2f}–{s['t1']:.2f} s (bar {s['bar0']:g}) · {s['section']} · {s['framing']} · "
                    f"{s['motion_tier']} ({foot}){'' if s['agent_on_screen'] else ' · without her'}")
            out.append(f"- {head}  ")
            out.append(f"  {s['action']} *Camera:* {s['camera']}. *Transition in:* {s['transition']}.  ")
            for ly in s["lyrics"]:
                sp = ly.get("split")
                then = f"; from “{ly['words'][sp['at']]['word']}” on, {sp['mode']}, {sp['zone']}" if sp else ""
                out.append(f"  *Line {ly['line']}:* “{ly['text']}” ({ly['t0']:.2f} s), {ly['mode']}, {ly['zone']}{then}.  ")
            out.append(f"  *Graphic:* {s['graphic']}")
    out += ["", "## The Seedance clip list", "",
            "Each clip's plate goes through `tools/print_grade.py` first. A speaking clip gets the vocal stem's window, starts on a frame "
            f"in the gap before its first word, as close to {LEAD_S} s ahead of it as the gap allows, and quotes the words it holds whole; "
            "motion and dancer clips get the full mix, so the movement lands on the beat. The windows are computed from `words.json`.",
            "", "| Clip | Plate | Window (s) | Length | Speaks on camera | Words | Shots |", "|---|---|---|---|---|---|---|"]
    for cl in doc["clips"]:
        out.append(f"| {cl['clip']} | {cl['plate']} | {cl['window']['start']:.3f}–{cl['window']['end']:.3f} | {cl['seconds']} s | "
                   f"{'yes' if cl['speaks_on_camera'] else 'no, ' + cl['kind']} | {cl['words'] or '(none)'} | {', '.join(cl['shots'])} |")
    out += ["", "**Totals.**",
            f"- {t['clips']} clips, {t['seedance_s']} s of Seedance planned ({t['speaking_s']} s of it speaking), within BRIEF.md's "
            "\"about 30 clips and at most about 200 s\".",
            f"- Planned: ${c['planned']['seedance']:.2f} of Seedance at ${c['prices']['seedance_usd_per_s']}/s, and "
            f"${c['planned']['repairs']:.2f} of sync-2-pro repairs on the speaking clips at $5 a minute.",
            f"- **Expected, retakes and repairs included: ${c['expected']['total']:.2f}** (${c['expected']['seedance']:.2f} Seedance, "
            f"${c['expected']['repairs']:.2f} repairs), assuming {c['expected']['assumes']}.",
            f"- At the caps: ${c['at_the_caps']['total']:.2f}, if {c['at_the_caps']['assumes']}. The ledger's $150 pause comes first.",
            "- Not counted: LatentSync fallbacks ($0.20 a clip), fal image edits for weak plates, and Topaz upscaling of the selects "
            "(about $0.02/s; PLAN.md section 6).",
            "", "## The shots, as data", "", "`shots.json` carries per shot: `t0`/`t1` (s), `f0`/`f1` (24 fps frames), `bar0`, the section, "
            "`agent_on_screen`, `framing`, `motion_tier`, `clip` and `plate`, `place` (where she is in frame), `lyrics` (each line with its "
            "words, mode and zone), `action`, `camera`, `graphic`, `transition` and `status`; and per clip its window, words, prompt and shots."]
    return "\n".join(out) + "\n"


def mj_md(doc, board):
    plates = doc["plates"]
    groups = [("A", "The night shift (style A)"), ("B", "The clean room (style B)"), ("H", "The Human's daylight")]
    out = ["# Midjourney plate pack: Always Allow",
           "",
           f"Built by `tools/storyboard.py` from `production/storyboard/board.py`; it runs in session 4 (BRIEF.md step 4), in batches, "
           "in the user's browser. {n} plates, each in at most {m} shots so the cut doesn't repeat itself (a dancer's start frame is cut "
           "out onto the stages, so only the stages count).".format(n=len(plates), m=MAX_PLATE_SHOTS),
           "",
           "- **Prompt order** (BRIEF.md): framing; her canon with its descriptor (or the Instances', or the Human's); the action; where "
           "she stands and the area left empty for type; the set; the palette with hex values and one warm accent; the grain and "
           "\"cinematic 35mm film still\"; \"no text, no letters, no logos\".",
           f"- **Parameters:** prompts with her or the Instances end `{PARAMS_AGENT}` (no moodboard: it overrides her canon); every other "
           f"prompt ends `{PARAMS_SET}`.",
           "- **First, the canon check the style bible asks for:** run A_desk_ws and B_stage_alone (her in a wide and a full-length shot) "
           "before the rest, and flag an off-model face early.",
           "- **Faces go to Seedance through the print grade:** every plate marked *graded* is put through `tools/print_grade.py` before "
           "upload. Plates for a clip need her face big and clear for the sync-2-pro repair.",
           "- **2.5D plates** get a depth map (Depth Anything V2) in session 4; the dancer plates get a SAM 2 matte in step 5.",
           "- Record every image in `production/storyboard/mj_manifest.csv` with the plate ID in `for`.",
           ""]
    for key, title in groups:
        out += [f"## {title}", ""]
        for p in [x for x in plates if x["set"] == key]:
            tags = [f"serves {', '.join(p['shots'])}"]
            if p["for_clip"]:
                tags.append(f"start frame of {p['for_clip']}")
            if p["dancer"]:
                tags.append("dancer: cut out with a matte")
            if p["depth_map"]:
                tags.append("2.5D: depth map")
            if p["print_grade"]:
                tags.append("graded")
            out += [f"**{p['plate']}** ({'; '.join(tags)})", "```", p["prompt"], "```", ""]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("step", choices=["build", "check"])
    args = ap.parse_args()
    board = load_board()
    song = json.loads(SONG.read_text(encoding="utf-8"))
    words_json = json.loads(WORDS.read_text(encoding="utf-8"))
    old = json.loads(SHOTS.read_text(encoding="utf-8")) if SHOTS.exists() else None
    doc, problems = build(board, song, words_json, old)
    t = doc["totals"]
    print(f"{t['shots']} shots, {t['clips']} clips ({t['seedance_s']} s), {t['plates']} plates; the Agent on screen "
          f"{t['agent_on_screen_fraction']:.0%}; expected ${t['cost_usd']['expected']['total']:.2f}")
    for p in problems:
        print("PROBLEM:", p)
    if args.step == "build":
        if problems:
            sys.exit(f"{len(problems)} problems; nothing written")
        SHOTS.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        STORYBOARD.write_text(storyboard_md(doc, board), encoding="utf-8")
        MJ_PROMPTS.write_text(mj_md(doc, board), encoding="utf-8")
        print(f"Wrote {rel(SHOTS)}, {rel(STORYBOARD)} and {rel(MJ_PROMPTS)}")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
