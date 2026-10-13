"""This run's real numbers, for the chrome's counters and the outro receipt (BRIEF.md: the meta outro).

Reads production/runlog.csv (sessions, hours, tool calls, tokens), production/ledger.csv (spend by
category, Seedance seconds, lip-sync repairs), production/storyboard/mj_manifest.csv (Midjourney images),
and production/storyboard/shots.json (shots planned and thrown away), and writes
production/comp/src/data/receipt.json. A session still running isn't in the run log yet: pass its ID
with --live and its tool calls and tokens so far are counted from its transcript (tools/session_stats.py); add
--since, in UTC, when the transcript also holds earlier sessions (sessions 3 to 5 ran in one Claude Code session).
Shots thrown away are the shots whose footage was thrown away (a dropped clip's shots, reworked or dropped), and
takes thrown away are the Seedance takes made but not used (production/storyboard/sync_report.json).

Usage, with the project's .venv:
  .venv/Scripts/python tools/receipt.py
  .venv/Scripts/python tools/receipt.py --live 6c730a7e-95f0-42a0-9699-11eb6ea0cc7d --since 2026-09-30T14:09
"""
import argparse
import csv
import datetime
import json
from pathlib import Path

import session_stats

ROOT = Path(__file__).resolve().parent.parent
RUNLOG = ROOT / "production" / "runlog.csv"
LEDGER = ROOT / "production" / "ledger.csv"
MANIFEST = ROOT / "production" / "storyboard" / "mj_manifest.csv"
SHOTS = ROOT / "production" / "storyboard" / "shots.json"
REPORT = ROOT / "production" / "storyboard" / "sync_report.json"
OUT = ROOT / "production" / "comp" / "src" / "data" / "receipt.json"


def read_csv(path):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def hours(a, b):
    fmt = "%Y-%m-%dT%H:%M"
    return (datetime.datetime.strptime(b[:16], fmt) - datetime.datetime.strptime(a[:16], fmt)).total_seconds() / 3600


def live_session(session_id, since=None):
    """Tool calls, tokens and hours so far for a session still running, from its transcript (from `since` on, UTC)."""
    main = next((d / f"{session_id}.jsonl" for d in session_stats.DIRS if (d / f"{session_id}.jsonl").exists()), None)
    if not main:
        raise SystemExit(f"no transcript for {session_id}")
    subs = sorted((main.parent / session_id / "subagents").glob("*.jsonl"))
    stats = session_stats.count([main, *subs], since)
    first = since + ":00Z" if since and len(since) == 16 else since
    with main.open(encoding="utf-8") as f:
        for line in f if not first else []:
            try:
                ts = json.loads(line).get("timestamp")
            except ValueError:
                continue
            if ts:
                first = ts
                break
    started = datetime.datetime.fromisoformat(first.replace("Z", "+00:00")) if first else None
    now = datetime.datetime.now(datetime.timezone.utc)
    return {"session": session_id, "started_utc": first,
            "hours": round((now - started).total_seconds() / 3600, 2) if started else 0.0,
            "tool_calls": stats["tool_calls"], "tokens": stats["tokens"]}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--live", help="the ID of a session still running, to count it from its transcript")
    ap.add_argument("--live-number", type=int, help="its number in the run log (default: the next one)")
    ap.add_argument("--since", help="with --live: count its transcript from this UTC time on, such as 2026-09-30T14:09")
    args = ap.parse_args()

    sessions = []
    for r in read_csv(RUNLOG):
        sessions.append({"session": int(r["session"]), "start": r["start"], "end": r["end"],
                         "hours": round(hours(r["start"], r["end"]), 2),
                         "tool_calls": int(r["tool_calls"] or 0), "tokens": int(r["tokens"] or 0)})
    if args.live:
        live = live_session(args.live, args.since)
        n = args.live_number or (max((s["session"] for s in sessions), default=0) + 1)
        sessions.append({"session": n, "start": live["started_utc"], "end": None, "hours": live["hours"],
                         "tool_calls": live["tool_calls"], "tokens": live["tokens"], "running": True})

    ledger = read_csv(LEDGER)
    by_tool = {}
    for r in ledger:
        by_tool[r["tool"]] = round(by_tool.get(r["tool"], 0) + float(r["estimated_usd"] or 0), 3)
    seedance = [r for r in ledger if r["tool"] in ("seedance",)]
    repairs = [r for r in ledger if r["tool"] == "lipsync"]  # the production repairs; the lip-sync test is lipsync_test
    manifest = read_csv(MANIFEST)
    board = json.loads(SHOTS.read_text(encoding="utf-8")) if SHOTS.exists() else {"shots": [], "clips": [], "plates": []}
    report = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else {"clips": {}}
    thrown = {s["id"] for s in board["shots"] if s.get("status") == "dropped"}
    takes_made = takes_used = 0
    for e in report["clips"].values():
        if e.get("result") == "dropped":
            thrown.update(e.get("shots", []))  # its shots' footage went; the shots were reworked or dropped
        made = [t for t in e.get("takes", []) if t.get("file")]
        takes_made += len(made)
        takes_used += 1 if e.get("result") in ("accepted", "repaired") else 0

    out = {
        "as_of": datetime.datetime.now().isoformat(timespec="minutes"),
        "sessions": sessions,
        "hours": round(sum(s["hours"] for s in sessions), 2),
        "tool_calls": sum(s["tool_calls"] for s in sessions),
        "tokens": sum(s["tokens"] for s in sessions),
        "spend_usd": round(sum(float(r["estimated_usd"] or 0) for r in ledger), 2),
        "spend_by_tool": by_tool,
        "paid_calls": len(ledger),
        "seedance_generations": len(seedance),
        "seedance_seconds": round(sum(float(r["seconds"] or 0) for r in seedance), 1),
        "lipsync_repairs": len(repairs),
        "lipsync_test_calls": sum(1 for r in ledger if r["tool"] == "lipsync_test"),
        "midjourney_images": len(manifest),
        "midjourney_prompts": len({r["prompt_id"] for r in manifest}),
        "shots_planned": len(board["shots"]),
        "shots_thrown_away": len(thrown),
        "takes_thrown_away": takes_made - takes_used,
        "clips_planned": len(board.get("clips", [])),
        "plates_planned": len(board.get("plates", [])),
        "sources": ["production/runlog.csv", "production/ledger.csv", "production/storyboard/mj_manifest.csv",
                    "production/storyboard/shots.json"] + (["the running session's transcript"] if args.live else []),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(f"{out['hours']:.1f} h over {len(sessions)} sessions, {out['tool_calls']:,} tool calls, {out['tokens']:,} tokens, "
          f"${out['spend_usd']:.2f} spent, {out['midjourney_images']} Midjourney images, {out['seedance_generations']} "
          f"Seedance generations, {out['shots_thrown_away']} shots thrown away -> {OUT.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
