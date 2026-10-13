"""Tool calls and tokens for a Claude Code session, for production/runlog.csv and the outro receipt.

Reads a session's transcript (the .jsonl named after its session ID), the transcripts of its
subagents (`<session id>/subagents/*.jsonl`), and any other transcripts you name, such as the
automatic reviews that ran on its commits. A streamed reply appears in a transcript several times
with the same message ID, so usage is counted once per message and tool calls once per call ID.
Tokens are input + output + cache writes + cache reads, as ESCAPE VELOCITY counted them.

Usage, with the project's .venv:
  .venv/Scripts/python tools/session_stats.py SESSION_ID [EXTRA.jsonl ...]
  .venv/Scripts/python tools/session_stats.py c4afc4fc-54c0-44fc-8b1c-70b4d972c68c --since 2026-09-28T20:00

The transcripts are looked for under %USERPROFILE%/.claude-work/projects/C--code-music-videos-always-allow/
and %USERPROFILE%/.claude/projects/C--code-music-videos-always-allow/.
"""
import argparse
import json
from pathlib import Path

DIRS = [Path.home() / d / "projects" / "C--code-music-videos-always-allow" for d in (".claude-work", ".claude")]


def count(paths, since=None):
    messages, calls = {}, set()
    for path in paths:
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                m = d.get("message") or {}
                if d.get("type") != "assistant" or not isinstance(m, dict):
                    continue
                if since and d.get("timestamp", "") < since:
                    continue
                if m.get("id") and m.get("usage"):
                    messages[(path.name, m["id"])] = m["usage"]
                for block in m.get("content") or []:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        calls.add(block.get("id"))
    fields = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
    parts = {k: sum(int(u.get(k) or 0) for u in messages.values()) for k in fields}
    return {"tool_calls": len(calls), "tokens": sum(parts.values()), "api_calls": len(messages), **parts}


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("session")
    p.add_argument("extra", nargs="*", help="more transcripts to include, such as the commit reviews")
    p.add_argument("--since", help="count only what happened from this UTC time on, such as 2026-09-28T20:00")
    args = p.parse_args()
    main_file = next((d / f"{args.session}.jsonl" for d in DIRS if (d / f"{args.session}.jsonl").exists()), None)
    if not main_file:
        raise SystemExit(f"no transcript for {args.session} in {', '.join(map(str, DIRS))}")
    subs = sorted((main_file.parent / args.session / "subagents").glob("*.jsonl"))
    extra = [Path(e) if Path(e).is_absolute() else main_file.parent / e for e in args.extra]
    stats = count([main_file, *subs, *extra], args.since)
    print(json.dumps({"session": args.session, "since": args.since, "transcripts": 1 + len(subs) + len(extra), **stats}, indent=1))


if __name__ == "__main__":
    main()
